"""
对战准备窗口
提供PVP/PVE模式选择、预置卡组和用户卡组选择功能
"""

import pygame
import pygame_gui
from typing import Dict, List, Optional, Any, Callable
import os

class BattlePrepWindow(pygame_gui.elements.UIWindow):
    """对战准备窗口类"""
    # AI 对手选项
    AI_OPPONENT_OPTIONS = [
        ('rookie_trainer', 'Entrenador Novato', 'Ideal para principiantes'),
        ('gym_leader', 'Líder de Gimnasio', 'Desafío intermedio'),
        ('elite_four', 'Alto Mando', 'Estrategia avanzada'),
        ('champion', 'Campeón', 'Máximo desafío')
    ]
    
    # 预置卡组配置
    PRESET_DECKS = {
        "starter_fire": {
            "name": "fire_starter_deck",
            "description": "Fire Starter Deck - Suited for beginners",
            "theme": "Fire",
            "difficulty": "Easy",
            "card_ids": [
                "xy5-1", "det1-1", "xy2-1", "sm9-2", "xy11-1",
                "bw1-1", "sm115-1", "sm3-1", "bw10-1", "xy7-1",
                "sm1-1", "sm12-2", "bw1-2", "swsh35-2", "det1-3",
                "sm9-3", "sm2-1", "xy4-1", "bw11-1", "bw9-1"
            ]
        },
        # 未来可以添加更多预置卡组
        # "starter_water": {...},
        # "starter_grass": {...},
    }
    
    def __init__(self, rect: pygame.Rect, ui_manager, game_manager, battle_controller, 
                 window_title: str = "对战准备"):
        """
        初始化对战准备窗口
        
        Args:
            rect: 窗口位置和大小
            ui_manager: pygame_gui UI管理器
            game_manager: 游戏管理器
            battle_controller: 战斗控制器
            window_title: 窗口标题
        """
        super().__init__(rect, ui_manager, window_title, object_id='#battle_prep_window')
        
        self.game_manager = game_manager
        self.ui_manager = ui_manager
        self.battle_controller = battle_controller

        print(f"🔍 [battle_prep_window.py] 初始化开始")
        print(f"   ui_manager: {ui_manager is not None}")
        print(f"   game_manager: {game_manager is not None}")
        print(f"   battle_controller: {battle_controller is not None}")
        print(f"   battle_controller类型: {type(battle_controller)}")

        self.battle_start_callback = None
        
        # 检查控制器能力
        capabilities = self.check_controller_capability()
        if capabilities.get("sync"):
            print("✅ [battle_prep_window.py] 检测到同步战斗控制器")
        else:
            print("⚠️ [battle_prep_window.py] 使用普通战斗控制器")

        # 如果battle_controller为None，尝试创建
        if self.battle_controller is None:
            print("⚠️ [battle_prep_window.py] battle_controller为None，尝试创建")
            try:
                from game.core.battle.battle_controller import BattleController
                self.battle_controller = BattleController(self.game_manager)
                print("✅ [battle_prep_window.py] 成功创建battle_controller")
            except Exception as e:
                print(f"❌ [battle_prep_window.py] 创建battle_controller失败: {e}")
        
        # 验证battle_controller的方法
        if self.battle_controller and hasattr(self.battle_controller, 'start_new_battle'):
            print("✅ [battle_prep_window.py] battle_controller验证通过")
        else:
            print("❌ [battle_prep_window.py] battle_controller验证失败")
        
        # 选择状态
        self.selected_mode = None      # "PVP" 或 "PVE"
        self.selected_deck_type = None # "preset" 或 "user"
        self.selected_deck_id = None   # 卡组ID或预置卡组key
        self.selected_ai_difficulty = 1  # AI难度 (1-3)
        
        # UI元素
        self.mode_buttons = {}         # 模式选择按钮
        self.deck_type_buttons = {}    # 卡组类型按钮
        self.deck_list = None          # 卡组列表
        self.difficulty_dropdown = None # AI难度选择
        self.start_battle_button = None
        self.close_button = None
        
        # 回调函数
        self.on_battle_start: Optional[Callable] = None
        
        # 数据
        self.user_decks = []
        self.preset_decks = []
        
        # 加载数据并创建UI
        self._load_deck_data()
        self._create_ui_elements()
        
        self.deck_mapping = {}  # 用于存储显示文本到卡组数据的映射
        self.selected_deck_cards = []  # 存储选中卡组的真实卡牌数据
    
        print(f"🔍 [battle_prep_window.py] 对战准备窗口初始化完成")
    
    def _load_deck_data(self):
        """加载卡组数据"""
        try:
            # 加载用户卡组
            user_decks_raw = self.game_manager.get_user_decks()
            self.user_decks = []
            
            for deck in user_decks_raw:
                deck_cards = self.game_manager.get_deck_cards(deck['id'])
                card_count = sum(card['quantity'] for card in deck_cards) if deck_cards else 0
                
                # 只显示有卡牌的卡组
                if card_count > 0:
                    self.user_decks.append({
                        'id': deck['id'],
                        'name': deck['name'],
                        'description': deck['description'] or '',
                        'card_count': card_count,
                        'type': 'user'
                    })
            
            # 加载预置卡组
            self.preset_decks = []
            for key, preset in self.PRESET_DECKS.items():
                self.preset_decks.append({
                    'id': key,
                    'name': preset['name'],
                    'description': preset['description'],
                    'card_count': len(preset['card_ids']),
                    'theme': preset['theme'],
                    'difficulty': preset['difficulty'],
                    'type': 'preset'
                })
            
            print(f"📚 加载卡组数据: {len(self.user_decks)} 个用户卡组, {len(self.preset_decks)} 个预置卡组")
            
        except Exception as e:
            print(f"❌ 加载卡组数据失败: {e}")
            self.user_decks = []
            self.preset_decks = []
    
    def _create_ui_elements(self):
        """创建UI元素"""
        print("🎯 创建对战准备UI元素...")
        
        window_width = self.get_container().get_size()[0]
        window_height = self.get_container().get_size()[1]
        
        # 第一行：模式选择
        mode_y = 30
        mode_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, mode_y, 100, 30),
            text='Modo de Batalla:',
            manager=self.ui_manager,
            container=self
        )
        
        # PVP按钮
        self.mode_buttons['PVP'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(130, mode_y, 100, 35),
            text='Batalla PVP',
            manager=self.ui_manager,
            container=self,
            object_id='#pvp_mode_button'
        )
        
        # PVE按钮
        self.mode_buttons['PVE'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(240, mode_y, 100, 35),
            text='Batalla PVE',
            manager=self.ui_manager,
            container=self,
            object_id='#pve_mode_button'
        )
        
        # 第二行：卡组类型选择
        deck_type_y = mode_y + 50
        deck_type_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, deck_type_y, 100, 30),
            text='Tipo de Mazo:',
            manager=self.ui_manager,
            container=self
        )
        
        # 预置卡组按钮
        self.deck_type_buttons['preset'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(130, deck_type_y, 100, 35),
            text='Mazos Predefinidos',
            manager=self.ui_manager,
            container=self,
            object_id='#preset_deck_button'
        )
        
        # 用户卡组按钮
        self.deck_type_buttons['user'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(240, deck_type_y, 100, 35),
            text='Mis Mazos',
            manager=self.ui_manager,
            container=self,
            object_id='#user_deck_button'
        )
        
        # 第三行：AI难度选择（仅PVE模式显示）
        difficulty_y = deck_type_y + 50
        self.difficulty_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, difficulty_y, 100, 30),
            text='Oponente IA:',
            manager=self.ui_manager,
            container=self
        )
        
        difficulty_options = [option[1] for option in self.AI_OPPONENT_OPTIONS]
        self.difficulty_dropdown = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(130, difficulty_y, 180, 35),
            options_list=difficulty_options,
            starting_option=difficulty_options[0],
            manager=self.ui_manager,
            container=self,
            object_id='#ai_difficulty_dropdown'
        )
        
        # 初始隐藏AI难度选择
        self.difficulty_label.hide()
        self.difficulty_dropdown.hide()
        
        # 第四行：卡组列表
        deck_list_y = difficulty_y + 60
        deck_list_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, deck_list_y, 100, 30),
            text='Seleccionar Mazo:',
            manager=self.ui_manager,
            container=self
        )
        
        # 卡组选择列表
        self.deck_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(20, deck_list_y + 35, window_width - 40, 200),
            item_list=[],
            manager=self.ui_manager,
            container=self,
            object_id='#deck_selection_list'
        )
        
        # 底部按钮
        button_y = window_height - 60
        
        self.start_battle_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, button_y, 120, 40),
            text='Iniciar Batalla',
            manager=self.ui_manager,
            container=self,
            object_id='#start_battle_button'
        )
        self.start_battle_button.disable()  # 初始禁用
        
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(160, button_y, 80, 40),
            text='Cerrar',
            manager=self.ui_manager,
            container=self,
            object_id='#close_battle_prep'
        )
        
        print("✅ 对战准备UI元素创建完成")
    
    def _select_mode(self, mode: str):
        """选择对战模式"""
        self.selected_mode = mode
        print(f"🎮 选择对战模式: {mode}")
        
        # 更新按钮外观
        for mode_name, button in self.mode_buttons.items():
            if mode_name == mode:
                button.background_colour = pygame.Color(100, 150, 255)
            else:
                button.background_colour = pygame.Color(255, 255, 255)
            button.rebuild()
        
        # 显示/隐藏AI难度选择
        if mode == "PVE":
            self.difficulty_label.show()
            self.difficulty_dropdown.show()
        else:
            self.difficulty_label.hide()
            self.difficulty_dropdown.hide()
        
        self._check_ready_to_battle()
    
    def _select_deck_type(self, deck_type: str):
        """选择卡组类型"""
        self.selected_deck_type = deck_type
        print(f"📚 选择卡组类型: {deck_type}")
        
        # 更新按钮外观
        for type_name, button in self.deck_type_buttons.items():
            if type_name == deck_type:
                button.background_colour = pygame.Color(100, 150, 255)
            else:
                button.background_colour = pygame.Color(255, 255, 255)
            button.rebuild()
        
        # 重置卡组选择状态
        self.selected_deck_id = None
        if hasattr(self.deck_list, 'clear_selection'):
            self.deck_list.clear_selection()  # 清除之前的选择

        # 更新卡组列表
        self._update_deck_list()
        self._check_ready_to_battle()
    
    # def _update_deck_list(self):
    #     """更新卡组列表"""
    #     print(f"🔍 更新卡组列表: selected_deck_type={self.selected_deck_type}")
    #     if not self.selected_deck_type:
    #         return
        
    #     deck_items = []
        
    #     if self.selected_deck_type == "preset":
    #         print(f"🔍 加载预置卡组: {len(self.preset_decks)}个")
    #         for i, deck in enumerate(self.preset_decks):  # 注意这里添加了enumerate
    #             deck_text = f"{deck['name']} ({deck['theme']}) - {deck['card_count']}张卡"
    #             deck_items.append(deck_text)
    #             print(f"   {i}: {deck_text}")
        
    #     elif self.selected_deck_type == "user":
    #         print(f"🔍 加载用户卡组: {len(self.user_decks)}个")
    #         if not self.user_decks:
    #             deck_items.append("暂无可用的用户卡组")
    #             print("   暂无用户卡组")
    #         else:
    #             for i, deck in enumerate(self.user_decks):  # 同样添加enumerate
    #                 deck_text = f"{deck['name']} - {deck['card_count']}张卡"
    #                 deck_items.append(deck_text)
    #                 print(f"   {i}: {deck_text}")
        
    #     self.deck_list.set_item_list(deck_items)
    #     print(f"📋 列表更新完成: {len(deck_items)} 个选项")
    
    def _update_deck_list(self):
        """更新卡组列表"""
        print(f"🔍 [battle_prep_window.py] 更新卡组列表: selected_deck_type={self.selected_deck_type}")
        
        if not self.selected_deck_type:
            return
        
        deck_items = []
        self.deck_mapping = {}  # 添加一个映射表，文本->卡组数据
        
        if self.selected_deck_type == "preset":
            print(f"🔍 [battle_prep_window.py] 加载预置卡组: {len(self.preset_decks)}个")
            for i, (deck_id, deck) in enumerate(self.preset_decks.items()):  # 注意这里改了
                deck_text = f"{deck['name']} ({deck['theme']}) - {len(deck['card_ids'])}张卡"
                deck_items.append(deck_text)
                # 存储映射关系：显示文本 -> (类型, 索引, 卡组ID, 卡组数据)
                self.deck_mapping[deck_text] = ("preset", i, deck_id, deck)
                print(f"   {i}: {deck_text}")
        
        elif self.selected_deck_type == "user":
            print(f"🔍 加载用户卡组: {len(self.user_decks)}个")
            if not self.user_decks:
                deck_items.append("暂无可用的用户卡组")
            else:
                for i, deck in enumerate(self.user_decks):
                    deck_text = f"{deck['name']} - {deck['card_count']}张卡"
                    deck_items.append(deck_text)
                    # 存储映射关系
                    self.deck_mapping[deck_text] = ("user", i, deck['id'], deck)
                    print(f"   {i}: {deck_text}")
        
        self.deck_list.set_item_list(deck_items)
        print(f"📋 列表更新完成: {len(deck_items)} 个选项")
        print(f"📋 映射表: {list(self.deck_mapping.keys())}")

    def _select_deck(self, deck_index: int):
        """选择卡组"""
        print(f"🔍 _select_deck调用: deck_index={deck_index}, type={type(deck_index)}")
        print(f"🔍 当前卡组类型: {self.selected_deck_type}")
        print(f"🔍 可用卡组数量: preset={len(self.preset_decks)}, user={len(self.user_decks)}")

        # 检查deck_index是否为整数
        if not isinstance(deck_index, int):
            print(f"❌ 卡组索引无效: {deck_index} (类型: {type(deck_index)})")  # 保持中文
            return

        if not self.selected_deck_type:
            return
        
        if self.selected_deck_type == "preset":
            if 0 <= deck_index < len(self.preset_decks):
                selected_deck = self.preset_decks[deck_index]
                self.selected_deck_id = selected_deck['id']
                print(f"🎯 选择预置卡组: {selected_deck['name']}")
            else:
                print(f"❌ 预设卡组索引超出范围: {deck_index}")  # 保持中文
                return
                    
        elif self.selected_deck_type == "user":
            if not self.user_decks:
                print("❌ 没有可用的用户卡组")  # 保持中文
                return

            if 0 <= deck_index < len(self.user_decks):
                selected_deck = self.user_decks[deck_index]
                self.selected_deck_id = selected_deck['id']
                print(f"🎯 选择用户卡组: {selected_deck['name']}")
            else:
                print(f"❌ 用户卡组索引超出范围: {deck_index}")  # 保持中文
                return
        
        self._check_ready_to_battle()
    
    def _check_ready_to_battle(self):
        """检查是否准备好开始对战"""
        print(f"🔍 检查战斗准备状态:")
        print(f"   selected_mode: {self.selected_mode}")
        print(f"   selected_deck_type: {self.selected_deck_type}")
        print(f"   selected_deck_id: {self.selected_deck_id}")
        
        ready = (
            self.selected_mode is not None and
            self.selected_deck_type is not None and
            self.selected_deck_id is not None
        )
        
        print(f"   ready: {ready}")
        
        if ready:
            self.start_battle_button.enable()
            print("✅ 准备就绪，可以开始对战")
        else:
            self.start_battle_button.disable()
            print("❌ 尚未准备就绪")
    
    def _start_battle(self):
        """开始对战"""
        if self.selected_mode == "PVP":
            # PVP模式暂未实现
            self._show_under_construction_message()
            return
        
        if self.selected_mode == "PVE":
            self._start_pve_battle()
    
    def _show_under_construction_message(self):
        """显示"正在开发中"消息"""
        # 创建消息窗口
        message_rect = pygame.Rect(0, 0, 300, 150)
        message_rect.center = self.get_abs_rect().center
        
        message_window = pygame_gui.windows.UIMessageWindow(
            rect=message_rect,
            html_message="<p>PVP对战功能正在开发中...</p><p>敬请期待！</p>",
            manager=self.ui_manager,
            window_title="开发中"
        )
        
        print("🚧 显示PVP开发中消息")

    def _validate_deck_cards(self, deck_cards):
        """验证卡组卡牌数据（参考测试文件）"""
        print(f"🔍 [battle_prep_window.py] 验证卡组卡牌")
        
        if not deck_cards:
            print(f"❌ [battle_prep_window.py] 卡牌列表为空")
            return False
        
        valid_count = 0
        for i, card in enumerate(deck_cards):
            if hasattr(card, 'id') and hasattr(card, 'name'):
                valid_count += 1
                if i < 3:  # 只打印前3张卡牌的详情
                    print(f"✅ [battle_prep_window.py] 卡牌 {i+1}: {card.name} (ID: {card.id})")
            else:
                print(f"⚠️ [battle_prep_window.py] 无效卡牌 {i+1}: {type(card)}")
        
        print(f"📊 [battle_prep_window.py] 卡牌验证结果: {valid_count}/{len(deck_cards)} 有效")
        return valid_count >= 20
    
    def _get_preset_deck_cards(self, deck_key):
        """获取预置卡组的卡牌数据"""
        print(f"🔍 [battle_prep_window.py] 获取预置卡组卡牌: {deck_key}")
        
        try:
            if deck_key not in self.preset_decks:
                print(f"❌ [battle_prep_window.py] 预置卡组不存在: {deck_key}")
                return []
            
            deck_data = self.preset_decks[deck_key]
            card_ids = deck_data.get('card_ids', [])
            deck_cards = []
            
            for card_id in card_ids:
                card = self.game_manager.get_card_by_id(card_id)
                if card:
                    deck_cards.append(card)
                    print(f"✅ [battle_prep_window.py] 预置卡牌: {card_id} -> {card.name}")
                else:
                    print(f"⚠️ [battle_prep_window.py] 预置卡牌不存在: {card_id}")
            
            print(f"📦 [battle_prep_window.py] 预置卡组获取完成: {len(deck_cards)} 张卡牌")
            return deck_cards
            
        except Exception as e:
            print(f"❌ [battle_prep_window.py] 获取预置卡组卡牌失败: {e}")
            return []
        
    def _start_pve_battle(self):
        """启动PVE对战 - 同步版本"""
        print("🚀 [battle_prep_window.py] 开始PVE对战准备（同步版本）")
        
        try:
            # 验证battle_controller
            if not self.battle_controller:
                print("❌ [battle_prep_window.py] battle_controller为空")
                self._show_error("战斗控制器未初始化")
                return
            
            print(f"✅ [battle_prep_window.py] battle_controller验证: {type(self.battle_controller)}")
            
            # 获取AI对手
            # ai_difficulty_index = self.AI_OPPONENT_OPTIONS
            # ai_difficulties = ["rookie_trainer", "gym_leader", "elite_four", "champion"]
            
            # if 0 <= ai_difficulty_index < len(ai_difficulties):
            #     opponent_difficulty = ai_difficulties[ai_difficulty_index]
            # else:
            #     opponent_difficulty = "rookie_trainer"

            # 获取AI对手
            opponent_difficulty = self.selected_ai_difficulty or "rookie_trainer"
            
            print(f"🤖 [battle_prep_window.py] 选择AI对手: {opponent_difficulty}")
            
            # 获取卡组
            deck_id = None
            
            if hasattr(self, 'use_user_deck') and self.use_user_deck:
                print(f"🔍 [battle_prep_window.py] 使用用户卡组")
                user_decks = self.game_manager.get_user_decks()
                if user_decks:
                    deck_id = user_decks[0]['id']
                    
                    # 验证卡组
                    deck_cards = self.game_manager.get_deck_cards(deck_id)
                    print(f"📦 [battle_prep_window.py] 用户卡组验证:")
                    print(f"   卡组ID: {deck_id}")
                    print(f"   已获取卡牌数量: {len(deck_cards) if deck_cards else 0}")
                    
                    if not deck_cards or len(deck_cards) < 20:
                        self._show_error(f"卡组卡牌数量不足（需要20张，当前{len(deck_cards) if deck_cards else 0}张）")
                        return
                else:
                    self._show_error("没有可用的用户卡组")
                    return
            else:
                # 使用随机卡组（如果实现了这个功能）
                print(f"🎲 [battle_prep_window.py] 使用随机卡组")
                self._show_error("随机卡组功能尚未实现，请创建自定义卡组")
                return
            
            # 准备战斗参数
            print(f"🚀 [battle_prep_window.py] 启动PVE对战参数:")
            print(f"   player_deck_id: {deck_id} (类型: {type(deck_id)})")
            print(f"   opponent_type: AI")
            print(f"   opponent_difficulty: {opponent_difficulty}")
            
            # 根据控制器类型选择启动方法
            if hasattr(self.battle_controller, 'start_new_battle_synchronized'):
                # 使用同步启动
                print(f"🔄 [battle_prep_window.py] 使用同步战斗启动")
                result = self.battle_controller.start_new_battle_synchronized(
                    player_deck_id=deck_id,
                    opponent_type="AI",
                    opponent_difficulty=opponent_difficulty
                )
            else:
                # 使用普通启动
                print(f"🔄 [battle_prep_window.py] 使用普通战斗启动")
                result = self.battle_controller.start_new_battle(
                    player_deck_id=deck_id,
                    opponent_type="AI",
                    opponent_difficulty=opponent_difficulty
                )
            
            print(f"🔍 [battle_prep_window.py] 战斗启动结果: {result}")
            
            if result.get("success"):
                battle_id = result.get("battle_id")
                status = result.get("status", "started")
                
                print(f"✅ [battle_prep_window.py] 战斗启动成功")
                print(f"   battle_id: {battle_id}")
                print(f"   status: {status}")
                print(f"   message: {result.get('message', '')}")
                
                # 触发战斗开始回调
                if self.battle_start_callback:
                    if status == "prepared":
                        # 同步模式：传递完整信息
                        print(f"📡 [battle_prep_window.py] 触发同步战斗开始回调")
                        self.battle_start_callback({
                            "battle_id": battle_id,
                            "status": status,
                            "message": result.get("message", "")
                        })
                    else:
                        # 普通模式：只传递battle_id
                        print(f"📡 [battle_prep_window.py] 触发普通战斗开始回调")
                        self.battle_start_callback(battle_id)
                
                # 关闭窗口
                self.kill()
                
            else:
                error_msg = result.get("error", "未知错误")
                print(f"❌ [battle_prep_window.py] 战斗启动失败: {error_msg}")
                self._show_error(f"启动战斗失败: {error_msg}")
                
        except Exception as e:
            error_msg = f"启动PVE对战时发生异常: {str(e)}"
            print(f"❌ [battle_prep_window.py] {error_msg}")
            import traceback
            traceback.print_exc()
            self._show_error(error_msg)

    def _show_error(self, message: str):
        """显示错误消息 - 改进版本"""
        print(f"❌ [battle_prep_window.py] 错误: {message}")
        
        try:
            # 如果有状态标签，更新它
            if hasattr(self, 'status_label'):
                self.status_label.set_text(f"错误: {message}")
            
            # 也可以显示系统消息框（如果需要）
            # 这里暂时只打印到控制台
            
        except Exception as e:
            print(f"❌ [battle_prep_window.py] 显示错误消息失败: {e}")
    
    def _create_preset_deck(self) -> Optional[int]:
        """创建预置卡组的临时副本"""
        try:
            if self.selected_deck_id not in self.PRESET_DECKS:
                return None
            
            preset = self.PRESET_DECKS[self.selected_deck_id]
            
            # 创建临时卡组
            deck_name = f"临时-{preset['name']}"
            success, deck_id = self.game_manager.create_deck(deck_name, preset['description'])
            
            if not success:
                print(f"❌ 创建临时卡组失败: {deck_id}")
                return None
            
            # 添加预置卡牌
            for card_id in preset['card_ids']:
                # 每张卡添加1份（可以根据需要调整数量）
                self.game_manager.add_card_to_deck(deck_id, card_id, 1)
            
            print(f"✅ 创建预置卡组副本: {deck_name} (ID: {deck_id})")
            return deck_id
            
        except Exception as e:
            print(f"❌ 创建预置卡组失败: {e}")
            return None
    
    def process_event(self, event):
        """处理窗口事件"""
        handled = super().process_event(event)
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # 处理模式选择
            for mode, button in self.mode_buttons.items():
                if event.ui_element == button:
                    self._select_mode(mode)
                    return True
            
            # 处理卡组类型选择
            for deck_type, button in self.deck_type_buttons.items():
                if event.ui_element == button:
                    self._select_deck_type(deck_type)
                    return True
            
            # 处理开始对战按钮
            if event.ui_element == self.start_battle_button:
                self._start_battle()
                return True
            
            # 处理关闭按钮
            if event.ui_element == self.close_button:
                self.kill()
                return True
        
        elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            # 处理卡组选择
            if event.ui_element == self.deck_list:
                try:
                    selected_text = event.text
                    print(f"🔍 [battle_prep_window.py] 选择的文本: '{selected_text}'")
                    print(f"🔍 [battle_prep_window.py] 可用的映射: {list(self.deck_mapping.keys())}")
                    
                    if selected_text in self.deck_mapping:
                        deck_type, deck_index, deck_id, deck_data = self.deck_mapping[selected_text]
                        print(f"🎯 [battle_prep_window.py] 找到卡组映射: {deck_type}, {deck_id}")
                        self._select_deck_with_data(deck_type, deck_id, deck_data)
                    else:
                        print(f"❌ [battle_prep_window.py] 无法找到选择项: {selected_text}")
                except Exception as e:
                    print(f"❌ [battle_prep_window.py] 处理卡组选择时出错: {e}")
                return True
        
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.difficulty_dropdown:
                selected_name = event.text
                # 根据显示名称找到对应的AI key
                for ai_key, ai_name, ai_desc in self.AI_OPPONENT_OPTIONS:
                    if ai_name == selected_name:
                        self.selected_ai_difficulty = ai_key  # 存储AI key而不是数字
                        print(f"🤖 选择AI对手: {ai_name} ({ai_key})")
                        break
                return True
        
        return handled
    
    def check_controller_capability(self):
        """检查控制器能力"""
        if not self.battle_controller:
            return {"sync": False, "error": "控制器不存在"}
        
        capabilities = {
            "sync": hasattr(self.battle_controller, 'start_new_battle_synchronized'),
            "notify": hasattr(self.battle_controller, 'notify_interface_ready'),
            "state": hasattr(self.battle_controller, 'get_initial_battle_state')
        }
        
        print(f"🔍 [battle_prep_window.py] 控制器能力: {capabilities}")
        return capabilities
    
    def debug_controller_state(self):
        """调试控制器状态"""
        print(f"🔍 [battle_prep_window.py] 控制器调试信息:")
        print(f"   控制器对象: {self.battle_controller}")
        print(f"   控制器类型: {type(self.battle_controller)}")
        
        if self.battle_controller:
            print(f"   方法列表: {[m for m in dir(self.battle_controller) if not m.startswith('_')]}")
            
            if hasattr(self.battle_controller, 'current_battle'):
                print(f"   当前战斗: {self.battle_controller.current_battle}")
            
            if hasattr(self.battle_controller, 'is_battle_synchronized'):
                print(f"   同步状态: {self.battle_controller.is_battle_synchronized()}")

    def _select_deck_with_data(self, deck_type: str, deck_id: str, deck_data: dict):
        """选择卡组并获取真实卡牌数据"""
        print(f"🔍 [battle_prep_window.py] _select_deck_with_data: {deck_type}, {deck_id}")
        
        try:
            deck_cards = []
            
            if deck_type == "preset":
                # 预置卡组：直接从card_ids获取
                card_ids = deck_data.get('card_ids', [])
                print(f"🔍 [battle_prep_window.py] 预置卡组卡牌ID: {card_ids}")
                
                for card_id in card_ids:
                    card = self.game_manager.get_card_by_id(card_id)
                    if card:
                        deck_cards.append(card)
                        print(f"✅ [battle_prep_window.py] 预置卡牌获取成功: {card_id} -> {card.name}")
                    else:
                        print(f"⚠️ [battle_prep_window.py] 预置卡牌不存在: {card_id}")
            
            elif deck_type == "user":
                # 用户卡组：使用现有的get_deck_cards方法
                user_deck_id = deck_data.get('id')
                if user_deck_id:
                    print(f"🔍 [battle_prep_window.py] 获取用户卡组: {user_deck_id}")
                    # 使用现有的数据库方法
                    deck_card_data = self.game_manager.get_deck_cards(user_deck_id)
                    print(f"🔍 [battle_prep_window.py] 卡组数据: {deck_card_data}")
                    
                    for card_data in deck_card_data:
                        card_id = card_data['card_id']
                        quantity = card_data['quantity']
                        
                        print(f"🔍 [battle_prep_window.py] 处理卡牌: {card_id}, 数量: {quantity}")
                        
                        # 根据数量添加卡牌
                        for i in range(quantity):
                            card = self.game_manager.get_card_by_id(card_id)
                            if card:
                                deck_cards.append(card)
                                print(f"✅ [battle_prep_window.py] 用户卡牌获取成功 {i+1}/{quantity}: {card_id} -> {card.name}")
                            else:
                                print(f"⚠️ [battle_prep_window.py] 用户卡牌不存在: {card_id}")
            
            print(f"📦 [battle_prep_window.py] 最终获取卡牌统计:")
            print(f"   总数量: {len(deck_cards)}")
            if deck_cards:
                print(f"   第一张卡牌: {deck_cards[0].name} (ID: {deck_cards[0].id})")
                print(f"   卡牌类型: {type(deck_cards[0])}")
            
            if len(deck_cards) >= 20:  # 检查卡组是否有效
                self.selected_deck_id = deck_id
                self.selected_deck_cards = deck_cards  # 保存真实卡牌数据
                self.use_user_deck = True  # ✅ 让AI使用当前用户选中的卡组
                print(f"✅ [battle_prep_window.py] 成功选择卡组: {deck_id}, 包含 {len(deck_cards)} 张卡牌")
                self._check_ready_to_battle()
            else:
                print(f"❌ [battle_prep_window.py] 卡组无效: 只有 {len(deck_cards)} 张卡牌，需要至少20张")
                
        except Exception as e:
            print(f"❌ [battle_prep_window.py] 获取卡组数据时出错: {e}")
            import traceback
            traceback.print_exc()

    def set_battle_start_callback(self, callback):
        """设置战斗开始回调 - 支持同步模式"""
        self.battle_start_callback = callback
        print(f"📞 [battle_prep_window.py] 设置战斗开始回调: {type(callback)}")
    
    def refresh_data(self):
        """刷新数据"""
        self._load_deck_data()
        if self.selected_deck_type:
            self._update_deck_list()

    """
    # 添加到 battle_prep_window.py 的末尾来应用修复
    BattlePrepWindow._start_pve_battle = _start_pve_battle
    BattlePrepWindow._show_error = _show_error
    BattlePrepWindow.set_battle_start_callback = set_battle_start_callback
    BattlePrepWindow.check_controller_capability = check_controller_capability
    BattlePrepWindow.debug_controller_state = debug_controller_state
    """