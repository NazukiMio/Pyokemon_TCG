"""
现代化对战窗口 - 第一部分
导入声明和类初始化
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIWindow, UIButton, UIProgressBar
from pygame_gui.core import ObjectID
from typing import Dict, List, Optional, Callable, Any
from ..styles.theme import Theme
from ..styles.fonts import font_manager
from ..components.button_component import ModernButton
from ..components.message_component import MessageManager
from game.battle.battle_engine import BattleEngine, Player, AIPlayer, GamePhase, BattleState
from game.cards.card_types import PokemonCard, TrainerCard, EnergyCard, CardType

class ModernBattleWindow:
    """
    现代化对战窗口
    完整的Pokemon TCG对战界面
    """
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager,
                 battle_engine: BattleEngine, message_manager: MessageManager,
                 user_data: Dict):
        """
        初始化对战窗口
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            ui_manager: pygame_gui UI管理器
            battle_engine: 对战引擎
            message_manager: 消息管理器
            user_data: 用户数据
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        self.battle_engine = battle_engine
        self.message_manager = message_manager
        self.user_data = user_data
        
        # 窗口尺寸（全屏对战）
        self.window_width = screen_width
        self.window_height = screen_height
        
        # 创建主窗口
        self.window = UIWindow(
            rect=pygame.Rect(0, 0, self.window_width, self.window_height),
            manager=ui_manager,
            window_display_title="",
            object_id=ObjectID('#modern_battle_window'),
            resizable=False
        )
        
        # 状态管理
        self.is_visible = True
        self.scale_factor = min(screen_width / 1920, screen_height / 1080)
        self.selected_card = None
        self.selected_pokemon = None
        self.current_action = None
        
        # UI布局区域
        self._calculate_layout_areas()
        
        # UI元素
        self.modern_buttons = []
        self.card_rects = []  # 手牌卡片矩形
        self.pokemon_rects = []  # Pokemon区域矩形
        
        # 动画状态
        self.animation_timer = 0
        self.card_animations = []
        self.battle_effects = []
        
        # 回调函数
        self.on_close: Optional[Callable] = None
        self.on_battle_end: Optional[Callable] = None
        
        # 设置对战引擎回调
        self._setup_battle_callbacks()
        
        # 创建UI
        self._create_battle_ui()
        
        print(f"⚔️ 创建对战窗口: {battle_engine.player1.name} vs {battle_engine.player2.name}")
    
    def _calculate_layout_areas(self):
        """计算布局区域"""
        # 对手区域（上方）
        self.opponent_area = pygame.Rect(0, 0, self.window_width, self.window_height // 3)
        
        # 战斗场区域（中间）
        self.battle_area = pygame.Rect(0, self.window_height // 3, 
                                      self.window_width, self.window_height // 3)
        
        # 玩家区域（下方）
        self.player_area = pygame.Rect(0, (self.window_height * 2) // 3, 
                                      self.window_width, self.window_height // 3)
        
        # 手牌区域
        self.hand_area = pygame.Rect(50, self.player_area.y + 50, 
                                    self.window_width - 100, 100)
        
        # 控制面板区域
        self.control_area = pygame.Rect(self.window_width - 250, self.battle_area.y + 20,
                                       230, self.battle_area.height - 40)
    
    def _setup_battle_callbacks(self):
        """设置对战引擎回调"""
        self.battle_engine.on_turn_start = self._on_turn_start
        self.battle_engine.on_turn_end = self._on_turn_end
        self.battle_engine.on_pokemon_knocked_out = self._on_pokemon_knocked_out
        self.battle_engine.on_battle_end = self._on_battle_end

    def _create_battle_ui(self):
        """创建对战UI"""
        # 创建顶部信息栏
        self._create_top_info_bar()
        
        # 创建控制面板
        self._create_control_panel()
        
        # 创建战斗场标识
        self._create_battle_field_labels()
        
        # 创建底部按钮
        self._create_bottom_buttons()
    
    def _create_top_info_bar(self):
        """创建顶部信息栏"""
        info_height = 50
        info_rect = pygame.Rect(0, 0, self.window_width, info_height)
        
        self.info_panel = UIPanel(
            relative_rect=info_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#battle_info_panel')
        )
        
        # 回合信息
        self.turn_label = UILabel(
            relative_rect=pygame.Rect(20, 10, 200, 30),
            text=f"回合 {self.battle_engine.turn_number}",
            manager=self.ui_manager,
            container=self.info_panel,
            object_id=ObjectID('#turn_info')
        )
        
        # 当前阶段
        self.phase_label = UILabel(
            relative_rect=pygame.Rect(240, 10, 200, 30),
            text=f"阶段: {self.battle_engine.current_phase.value}",
            manager=self.ui_manager,
            container=self.info_panel,
            object_id=ObjectID('#phase_info')
        )
        
        # 当前玩家
        self.current_player_label = UILabel(
            relative_rect=pygame.Rect(460, 10, 300, 30),
            text=f"当前玩家: {self.battle_engine.current_player.name}",
            manager=self.ui_manager,
            container=self.info_panel,
            object_id=ObjectID('#current_player_info')
        )
        
        # 对战时间
        self.time_label = UILabel(
            relative_rect=pygame.Rect(self.window_width - 150, 10, 130, 30),
            text="时间: 00:00",
            manager=self.ui_manager,
            container=self.info_panel,
            object_id=ObjectID('#battle_time')
        )
    
    def _create_control_panel(self):
        """创建控制面板"""
        self.control_panel = UIPanel(
            relative_rect=self.control_area,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#control_panel')
        )
        
        # 阶段控制按钮
        button_width = 200
        button_height = 35
        button_x = 15
        current_y = 20
        
        # 结束回合按钮
        end_turn_rect = pygame.Rect(button_x, current_y, button_width, button_height)
        self.end_turn_button = ModernButton(
            rect=end_turn_rect,
            text="结束回合",
            button_type="primary",
            font_size="md"
        )
        self.modern_buttons.append(self.end_turn_button)
        current_y += button_height + 10
        
        # 撤退按钮
        retreat_rect = pygame.Rect(button_x, current_y, button_width, button_height)
        self.retreat_button = ModernButton(
            rect=retreat_rect,
            text="Pokemon撤退",
            button_type="secondary",
            font_size="md"
        )
        self.modern_buttons.append(self.retreat_button)
        current_y += button_height + 10
        
        # 查看弃牌堆按钮
        discard_rect = pygame.Rect(button_x, current_y, button_width, button_height)
        self.view_discard_button = ModernButton(
            rect=discard_rect,
            text="查看弃牌堆",
            button_type="secondary",
            font_size="md"
        )
        self.modern_buttons.append(self.view_discard_button)
        current_y += button_height + 10
        
        # 投降按钮
        surrender_rect = pygame.Rect(button_x, current_y, button_width, button_height)
        self.surrender_button = ModernButton(
            rect=surrender_rect,
            text="投降",
            button_type="secondary",
            font_size="md"
        )
        self.modern_buttons.append(self.surrender_button)
        current_y += button_height + 20
        
        # 状态显示区域
        status_rect = pygame.Rect(button_x, current_y, button_width, 100)
        self.status_label = UILabel(
            relative_rect=status_rect,
            text="等待玩家行动...",
            manager=self.ui_manager,
            container=self.control_panel,
            object_id=ObjectID('#battle_status')
        )
    
    def _create_battle_field_labels(self):
        """创建战斗场区域标识"""
        # 对手战斗场标签
        opponent_label_rect = pygame.Rect(50, self.opponent_area.bottom - 30, 200, 25)
        self.opponent_field_label = UILabel(
            relative_rect=opponent_label_rect,
            text=f"{self.battle_engine.player2.name}的战斗场",
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#opponent_field_label')
        )
        
        # 玩家战斗场标签
        player_label_rect = pygame.Rect(50, self.battle_area.bottom - 30, 200, 25)
        self.player_field_label = UILabel(
            relative_rect=player_label_rect,
            text=f"{self.battle_engine.player1.name}的战斗场",
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#player_field_label')
        )
    
    def _create_bottom_buttons(self):
        """创建底部按钮"""
        # 暂停/菜单按钮
        menu_rect = pygame.Rect(20, self.window_height - 60, 100, 40)
        self.menu_button = ModernButton(
            rect=menu_rect,
            text="菜单",
            button_type="secondary",
            font_size="md"
        )
        self.modern_buttons.append(self.menu_button)
        
        # 关闭对战按钮
        close_rect = pygame.Rect(self.window_width - 120, self.window_height - 60, 100, 40)
        self.close_button = ModernButton(
            rect=close_rect,
            text="退出",
            button_type="text",
            font_size="md"
        )
        self.modern_buttons.append(self.close_button)

    def handle_event(self, event):
        """处理事件"""
        if not self.is_visible:
            return None
        
        # 更新按钮悬停状态
        mouse_pos = pygame.mouse.get_pos()
        for button in self.modern_buttons:
            window_pos = (
                mouse_pos[0] - self.window.rect.x,
                mouse_pos[1] - self.window.rect.y
            )
            button.update_hover(window_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            window_pos = (
                mouse_pos[0] - self.window.rect.x,
                mouse_pos[1] - self.window.rect.y
            )
            
            # 检查按钮点击
            for button in self.modern_buttons:
                if button.rect.collidepoint(window_pos):
                    button.trigger_flash()
                    return self._handle_button_click(button)
            
            # 检查卡片点击
            card_click_result = self._handle_card_click(window_pos)
            if card_click_result:
                return card_click_result
            
            # 检查Pokemon点击
            pokemon_click_result = self._handle_pokemon_click(window_pos)
            if pokemon_click_result:
                return pokemon_click_result
        
        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self.close()
                return "close"
        
        return None
    
    def _handle_button_click(self, button):
        """处理按钮点击"""
        if button == self.close_button:
            self.close()
            return "close"
        
        elif button == self.menu_button:
            return "show_menu"
        
        elif button == self.end_turn_button:
            if self._can_end_turn():
                self.battle_engine.end_turn()
                self._update_ui_state()
                return "end_turn"
            else:
                self.message_manager.show_message("现在不能结束回合", "warning")
        
        elif button == self.retreat_button:
            return self._handle_retreat_action()
        
        elif button == self.view_discard_button:
            return "view_discard"
        
        elif button == self.surrender_button:
            return "surrender_confirm"
        
        return None
    
    def _handle_card_click(self, pos: tuple) -> Optional[str]:
        """处理手牌卡片点击"""
        # 计算手牌区域的卡片位置
        current_player = self._get_current_user_player()
        if not current_player or current_player != self.battle_engine.current_player:
            return None
        
        hand_cards = current_player.hand
        if not hand_cards:
            return None
        
        card_width = 80
        card_height = 120
        card_spacing = 10
        total_width = len(hand_cards) * card_width + (len(hand_cards) - 1) * card_spacing
        start_x = self.hand_area.x + (self.hand_area.width - total_width) // 2
        
        for i, card in enumerate(hand_cards):
            card_x = start_x + i * (card_width + card_spacing)
            card_y = self.hand_area.y
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            
            if card_rect.collidepoint(pos):
                self.selected_card = card
                self._update_action_options()
                return f"select_card_{i}"
        
        return None
    
    def _handle_pokemon_click(self, pos: tuple) -> Optional[str]:
        """处理Pokemon点击"""
        # 检查战斗场和后备区Pokemon
        current_player = self._get_current_user_player()
        if not current_player:
            return None
        
        # 战斗场Pokemon区域
        if current_player.active_pokemon:
            active_rect = self._get_active_pokemon_rect(is_player=True)
            if active_rect.collidepoint(pos):
                self.selected_pokemon = current_player.active_pokemon
                return "select_active_pokemon"
        
        # 后备区Pokemon
        for i, bench_pokemon in enumerate(current_player.bench):
            if bench_pokemon:
                bench_rect = self._get_bench_pokemon_rect(i, is_player=True)
                if bench_rect.collidepoint(pos):
                    self.selected_pokemon = bench_pokemon
                    return f"select_bench_pokemon_{i}"
        
        return None
    
    def _handle_retreat_action(self) -> str:
        """处理撤退行动"""
        current_player = self._get_current_user_player()
        if not current_player or not current_player.active_pokemon:
            self.message_manager.show_message("没有可撤退的Pokemon", "warning")
            return "retreat_failed"
        
        if not current_player.active_pokemon.can_retreat():
            self.message_manager.show_message("能量不足，无法撤退", "warning")
            return "retreat_failed"
        
        available_pokemon = current_player.get_available_pokemon_for_active()
        if not available_pokemon:
            self.message_manager.show_message("没有可替换的Pokemon", "warning")
            return "retreat_failed"
        
        # 简化：自动选择第一个可用Pokemon
        success = current_player.retreat_pokemon(available_pokemon[0])
        if success:
            self.message_manager.show_message("Pokemon成功撤退", "success")
            self._update_ui_state()
            return "retreat_success"
        else:
            self.message_manager.show_message("撤退失败", "error")
            return "retreat_failed"
    
    def _can_end_turn(self) -> bool:
        """检查是否可以结束回合"""
        current_player = self._get_current_user_player()
        return (current_player and 
                current_player == self.battle_engine.current_player and
                self.battle_engine.current_phase == GamePhase.MAIN)
    
    def _get_current_user_player(self) -> Optional[Player]:
        """获取当前用户控制的玩家"""
        # 假设player1是用户，player2是AI或其他玩家
        user_id = self.user_data.get('user_id')
        if self.battle_engine.player1.player_id == user_id:
            return self.battle_engine.player1
        elif self.battle_engine.player2.player_id == user_id:
            return self.battle_engine.player2
        return None
    
    def _update_action_options(self):
        """更新可用行动选项"""
        if not self.selected_card:
            return
        
        current_player = self._get_current_user_player()
        if not current_player or current_player != self.battle_engine.current_player:
            return
        
        card = self.selected_card
        
        if card.card_type == CardType.POKEMON:
            self._show_pokemon_play_options(card)
        elif card.card_type == CardType.ENERGY:
            self._show_energy_play_options(card)
        elif card.card_type == CardType.TRAINER:
            self._show_trainer_play_options(card)
    
    def _show_pokemon_play_options(self, pokemon: PokemonCard):
        """显示Pokemon使用选项"""
        current_player = self._get_current_user_player()
        
        if pokemon.evolution_stage == "basic":
            if not current_player.active_pokemon:
                self.status_label.set_text(f"点击战斗场放置{pokemon.name}")
            elif len(current_player.bench) < 5:
                self.status_label.set_text(f"点击后备区放置{pokemon.name}")
            else:
                self.status_label.set_text("战斗场和后备区已满")
        else:
            self.status_label.set_text(f"选择要进化的{pokemon.evolves_from}")
    
    def _show_energy_play_options(self, energy: EnergyCard):
        """显示能量使用选项"""
        if self.battle_engine.current_player.energy_played_this_turn:
            self.status_label.set_text("本回合已使用过能量")
        else:
            self.status_label.set_text(f"选择Pokemon附加{energy.name}")
    
    def _show_trainer_play_options(self, trainer: TrainerCard):
        """显示训练师卡使用选项"""
        self.status_label.set_text(f"使用{trainer.name}")
    
    def _get_active_pokemon_rect(self, is_player: bool) -> pygame.Rect:
        """获取战斗场Pokemon矩形区域"""
        pokemon_width = 150
        pokemon_height = 200
        
        if is_player:
            # 玩家战斗场（下方）
            x = self.battle_area.centerx - pokemon_width // 2
            y = self.battle_area.bottom - pokemon_height - 20
        else:
            # 对手战斗场（上方）
            x = self.battle_area.centerx - pokemon_width // 2
            y = self.battle_area.y + 20
        
        return pygame.Rect(x, y, pokemon_width, pokemon_height)
    
    def _get_bench_pokemon_rect(self, index: int, is_player: bool) -> pygame.Rect:
        """获取后备区Pokemon矩形区域"""
        pokemon_width = 100
        pokemon_height = 140
        spacing = 110
        
        base_x = 50 + index * spacing
        
        if is_player:
            # 玩家后备区
            y = self.battle_area.bottom - pokemon_height - 20
        else:
            # 对手后备区
            y = self.battle_area.y + 20
        
        return pygame.Rect(base_x, y, pokemon_width, pokemon_height)
    
    def _on_turn_start(self, player: Player):
        """回合开始回调"""
        self.message_manager.show_message(f"{player.name}的回合开始", "info")
        self._update_ui_state()
    
    def _on_turn_end(self, player: Player):
        """回合结束回调"""
        self.message_manager.show_message(f"{player.name}结束回合", "info")
        self._update_ui_state()
    
    def _on_pokemon_knocked_out(self, pokemon: PokemonCard, owner: Player):
        """Pokemon被击倒回调"""
        self.message_manager.show_message(f"{pokemon.name}被击倒了！", "warning")
        self._add_knockout_effect(pokemon)
    
    def _on_battle_end(self, winner: Player):
        """对战结束回调"""
        winner_text = f"{winner.name}获胜！"
        self.message_manager.show_message(winner_text, "success", duration=5000)
        
        if self.on_battle_end:
            self.on_battle_end(winner)
    
    def _add_knockout_effect(self, pokemon: PokemonCard):
        """添加击倒特效"""
        effect = {
            'type': 'knockout',
            'pokemon': pokemon,
            'timer': 2.0,  # 2秒特效
            'alpha': 255
        }
        self.battle_effects.append(effect)
    
    def _update_ui_state(self):
        """更新UI状态"""
        # 更新回合信息
        self.turn_label.set_text(f"回合 {self.battle_engine.turn_number}")
        self.phase_label.set_text(f"阶段: {self.battle_engine.current_phase.value}")
        self.current_player_label.set_text(f"当前玩家: {self.battle_engine.current_player.name}")
        
        # 更新按钮状态
        current_user_player = self._get_current_user_player()
        is_user_turn = (current_user_player and 
                       current_user_player == self.battle_engine.current_player)
        
        # 只有在用户回合时才能操作
        for button in self.modern_buttons:
            if button in [self.end_turn_button, self.retreat_button]:
                if is_user_turn:
                    button.button_type = "primary" if button == self.end_turn_button else "secondary"
                else:
                    button.button_type = "secondary"

    def update(self, time_delta: float):
        """更新窗口状态"""
        self.animation_timer += time_delta
        
        # 更新按钮动画
        for button in self.modern_buttons:
            button.update_animation(time_delta)
        
        # 更新战斗特效
        self._update_battle_effects(time_delta)
        
        # 更新对战时间显示
        self._update_battle_time()
        
        # 处理AI回合
        if isinstance(self.battle_engine.current_player, AIPlayer):
            self._process_ai_turn()
    
    def _update_battle_effects(self, time_delta: float):
        """更新战斗特效"""
        for effect in self.battle_effects[:]:
            effect['timer'] -= time_delta
            
            if effect['type'] == 'knockout':
                # 击倒特效淡出
                effect['alpha'] = max(0, effect['alpha'] - time_delta * 127)
            
            if effect['timer'] <= 0:
                self.battle_effects.remove(effect)
    
    def _update_battle_time(self):
        """更新对战时间显示"""
        duration = self.battle_engine.get_battle_duration()
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        time_text = f"时间: {minutes:02d}:{seconds:02d}"
        self.time_label.set_text(time_text)
    
    def _process_ai_turn(self, time_delta: float):
        """处理AI回合"""
        if (isinstance(self.battle_engine.current_player, AIPlayer) and 
            self.battle_engine.current_phase == GamePhase.MAIN):
            
            ai_player = self.battle_engine.current_player
            
            # 简单的AI逻辑：延迟后执行行动
            if not hasattr(ai_player, '_ai_action_timer'):
                ai_player._ai_action_timer = ai_player.thinking_time
            
            ai_player._ai_action_timer -= time_delta
            
            if ai_player._ai_action_timer <= 0:
                self._execute_ai_actions(ai_player)
                del ai_player._ai_action_timer
    
    def _execute_ai_actions(self, ai_player: AIPlayer):
        """执行AI行动"""
        actions = ai_player.make_turn_decisions(self.battle_engine)
        
        for action in actions:
            if action['action'] == 'play_energy':
                self.battle_engine.play_card(action['card'], action['target'])
            elif action['action'] == 'play_trainer':
                self.battle_engine.play_card(action['card'], action.get('target'))
            elif action['action'] == 'play_pokemon':
                self.battle_engine.play_card(action['card'], action['target'])
            elif action['action'] == 'attack':
                self.battle_engine.attack(action['attack_index'], action.get('target'))
        
        # AI自动结束回合
        if self.battle_engine.current_phase == GamePhase.MAIN:
            self.battle_engine.end_turn()

    def draw_custom_content(self, screen: pygame.Surface):
        """绘制自定义内容"""
        if not self.is_visible:
            return
        
        # 绘制战斗场背景
        self._draw_battle_field(screen)
        
        # 绘制Pokemon
        self._draw_pokemon(screen)
        
        # 绘制手牌
        self._draw_hand_cards(screen)
        
        # 绘制奖励卡和牌库
        self._draw_deck_areas(screen)
        
        # 绘制战斗特效
        self._draw_battle_effects(screen)
        
        # 绘制现代按钮
        self._draw_modern_buttons(screen)
    
    def _draw_battle_field(self, screen: pygame.Surface):
        """绘制战斗场背景"""
        # 绘制分割线
        line_y = self.battle_area.centery
        pygame.draw.line(screen, Theme.get_color('modern_border'), 
                        (0, line_y), (self.window_width, line_y), 2)
        
        # 绘制区域标识
        field_color = (*Theme.get_color('glass_bg_modern')[:3], 100)
        
        # 玩家区域背景
        player_bg = pygame.Surface((self.battle_area.width, self.battle_area.height // 2), pygame.SRCALPHA)
        player_bg.fill(field_color)
        screen.blit(player_bg, (self.battle_area.x, line_y))
        
        # 对手区域背景
        opponent_bg = pygame.Surface((self.battle_area.width, self.battle_area.height // 2), pygame.SRCALPHA)
        opponent_bg.fill(field_color)
        screen.blit(opponent_bg, (self.battle_area.x, self.battle_area.y))
    
    def _draw_pokemon(self, screen: pygame.Surface):
        """绘制Pokemon"""
        # 绘制玩家Pokemon
        self._draw_player_pokemon(screen, self.battle_engine.player1, is_player=True)
        
        # 绘制对手Pokemon
        self._draw_player_pokemon(screen, self.battle_engine.player2, is_player=False)
    
    def _draw_player_pokemon(self, screen: pygame.Surface, player: Player, is_player: bool):
        """绘制玩家的Pokemon"""
        # 绘制战斗场Pokemon
        if player.active_pokemon:
            active_rect = self._get_active_pokemon_rect(is_player)
            self._draw_single_pokemon(screen, player.active_pokemon, active_rect, is_active=True)
        
        # 绘制后备区Pokemon
        for i, bench_pokemon in enumerate(player.bench):
            if bench_pokemon:
                bench_rect = self._get_bench_pokemon_rect(i, is_player)
                self._draw_single_pokemon(screen, bench_pokemon, bench_rect, is_active=False)
    
    def _draw_single_pokemon(self, screen: pygame.Surface, pokemon: PokemonCard, 
                           rect: pygame.Rect, is_active: bool):
        """绘制单个Pokemon"""
        # Pokemon卡片背景
        bg_color = Theme.get_color('glass_bg_modern')[:3] + (200,)
        border_color = Theme.get_color('accent') if is_active else Theme.get_color('modern_border')
        
        # 绘制背景
        pokemon_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pokemon_surface.fill(bg_color)
        
        # 绘制边框
        border_width = 3 if is_active else 2
        pygame.draw.rect(pokemon_surface, border_color, 
                        (0, 0, rect.width, rect.height), 
                        width=border_width, border_radius=10)
        
        screen.blit(pokemon_surface, rect)
        
        # 绘制Pokemon名称
        name_font = font_manager.get_font_by_size(14)
        name_surface = name_font.render(pokemon.name, True, Theme.get_color('text'))
        name_rect = name_surface.get_rect(centerx=rect.centerx, y=rect.y + 5)
        screen.blit(name_surface, name_rect)
        
        # 绘制HP条
        self._draw_hp_bar(screen, pokemon, rect)
        
        # 绘制能量指示
        self._draw_energy_indicators(screen, pokemon, rect)
        
        # 绘制状态异常
        self._draw_status_conditions(screen, pokemon, rect)
    
    def _draw_hp_bar(self, screen: pygame.Surface, pokemon: PokemonCard, rect: pygame.Rect):
        """绘制HP条"""
        hp_bar_width = rect.width - 20
        hp_bar_height = 8
        hp_bar_x = rect.x + 10
        hp_bar_y = rect.bottom - 30
        
        # HP条背景
        hp_bg_rect = pygame.Rect(hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height)
        pygame.draw.rect(screen, (200, 200, 200), hp_bg_rect, border_radius=4)
        
        # HP条填充
        hp_ratio = pokemon.current_hp / pokemon.hp if pokemon.hp > 0 else 0
        hp_fill_width = int(hp_bar_width * hp_ratio)
        
        if hp_fill_width > 0:
            hp_color = (100, 255, 100) if hp_ratio > 0.5 else (255, 255, 100) if hp_ratio > 0.25 else (255, 100, 100)
            hp_fill_rect = pygame.Rect(hp_bar_x, hp_bar_y, hp_fill_width, hp_bar_height)
            pygame.draw.rect(screen, hp_color, hp_fill_rect, border_radius=4)
        
        # HP文字
        hp_font = font_manager.get_font_by_size(12)
        hp_text = f"{pokemon.current_hp}/{pokemon.hp}"
        hp_surface = hp_font.render(hp_text, True, Theme.get_color('text'))
        hp_text_rect = hp_surface.get_rect(centerx=rect.centerx, y=hp_bar_y + hp_bar_height + 2)
        screen.blit(hp_surface, hp_text_rect)

    def _draw_energy_indicators(self, screen: pygame.Surface, pokemon: PokemonCard, rect: pygame.Rect):
        """绘制能量指示器"""
        if not pokemon.attached_energies:
            return
        
        energy_size = 15
        energy_spacing = 18
        start_x = rect.x + 5
        start_y = rect.y + 25
        
        # 统计能量数量
        energy_counts = {}
        for energy_type in pokemon.attached_energies:
            energy_counts[energy_type] = energy_counts.get(energy_type, 0) + 1
        
        # 绘制能量图标
        current_x = start_x
        current_y = start_y
        
        for energy_type, count in energy_counts.items():
            # 能量颜色映射
            energy_colors = {
                'fire': (255, 100, 100),
                'water': (100, 150, 255),
                'grass': (100, 255, 100),
                'electric': (255, 255, 100),
                'psychic': (200, 100, 255),
                'fighting': (200, 150, 100),
                'darkness': (100, 100, 100),
                'metal': (150, 150, 150),
                'fairy': (255, 150, 200),
                'colorless': (200, 200, 200)
            }
            
            energy_color = energy_colors.get(energy_type.value, (150, 150, 150))
            
            # 绘制能量球
            pygame.draw.circle(screen, energy_color, 
                             (current_x + energy_size // 2, current_y + energy_size // 2), 
                             energy_size // 2)
            
            # 绘制数量
            if count > 1:
                count_font = font_manager.get_font_by_size(10)
                count_surface = count_font.render(str(count), True, (255, 255, 255))
                count_rect = count_surface.get_rect(center=(current_x + energy_size // 2, current_y + energy_size // 2))
                screen.blit(count_surface, count_rect)
            
            current_x += energy_spacing
            if current_x + energy_size > rect.right - 5:
                current_x = start_x
                current_y += energy_spacing
    
    def _draw_status_conditions(self, screen: pygame.Surface, pokemon: PokemonCard, rect: pygame.Rect):
        """绘制状态异常指示器"""
        if not pokemon.status_conditions:
            return
        
        status_size = 20
        status_spacing = 22
        start_x = rect.right - status_size - 5
        start_y = rect.y + 5
        
        status_colors = {
            'burn': (255, 150, 0),
            'poison': (150, 0, 255),
            'paralysis': (255, 255, 0),
            'sleep': (100, 100, 255),
            'confusion': (255, 100, 255),
            'freeze': (150, 200, 255)
        }
        
        for i, condition in enumerate(pokemon.status_conditions):
            condition_color = status_colors.get(condition.value, (200, 200, 200))
            
            # 绘制状态图标（简单的圆形）
            status_center = (start_x + status_size // 2, start_y + i * status_spacing + status_size // 2)
            pygame.draw.circle(screen, condition_color, status_center, status_size // 2)
            
            # 绘制状态首字母
            status_font = font_manager.get_font_by_size(10)
            status_letter = condition.value[0].upper()
            letter_surface = status_font.render(status_letter, True, (255, 255, 255))
            letter_rect = letter_surface.get_rect(center=status_center)
            screen.blit(letter_surface, letter_rect)
    
    def _draw_hand_cards(self, screen: pygame.Surface):
        """绘制手牌"""
        current_player = self._get_current_user_player()
        if not current_player:
            return
        
        hand_cards = current_player.hand
        if not hand_cards:
            return
        
        card_width = 80
        card_height = 120
        card_spacing = 10
        total_width = len(hand_cards) * card_width + (len(hand_cards) - 1) * card_spacing
        start_x = self.hand_area.x + (self.hand_area.width - total_width) // 2
        
        for i, card in enumerate(hand_cards):
            card_x = start_x + i * (card_width + card_spacing)
            card_y = self.hand_area.y
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            
            # 高亮选中的卡片
            is_selected = (card == self.selected_card)
            self._draw_hand_card(screen, card, card_rect, is_selected)
    
    def _draw_hand_card(self, screen: pygame.Surface, card: Any, rect: pygame.Rect, is_selected: bool):
        """绘制单张手牌"""
        # 卡片背景
        bg_color = Theme.get_color('glass_bg_modern')[:3] + (220,)
        border_color = Theme.get_color('accent') if is_selected else Theme.get_color('modern_border')
        
        # 绘制卡片背景
        card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        card_surface.fill(bg_color)
        
        # 绘制边框
        border_width = 3 if is_selected else 2
        pygame.draw.rect(card_surface, border_color, 
                        (0, 0, rect.width, rect.height), 
                        width=border_width, border_radius=8)
        
        screen.blit(card_surface, rect)
        
        # 绘制卡片类型图标
        type_color = self._get_card_type_color(card)
        type_rect = pygame.Rect(rect.x + 5, rect.y + 5, 15, 15)
        pygame.draw.rect(screen, type_color, type_rect, border_radius=3)
        
        # 绘制卡片名称
        name_font = font_manager.get_font_by_size(10)
        name_surface = name_font.render(card.name, True, Theme.get_color('text'))
        
        # 如果名称太长，缩放文字
        if name_surface.get_width() > rect.width - 10:
            scale = (rect.width - 10) / name_surface.get_width()
            name_surface = pygame.transform.scale(name_surface, 
                                                 (int(name_surface.get_width() * scale),
                                                  int(name_surface.get_height() * scale)))
        
        name_rect = name_surface.get_rect(centerx=rect.centerx, y=rect.y + 25)
        screen.blit(name_surface, name_rect)
        
        # 绘制卡片特定信息
        if card.card_type == CardType.POKEMON:
            self._draw_pokemon_card_info(screen, card, rect)
        elif card.card_type == CardType.ENERGY:
            self._draw_energy_card_info(screen, card, rect)
        elif card.card_type == CardType.TRAINER:
            self._draw_trainer_card_info(screen, card, rect)
    
    def _get_card_type_color(self, card: Any) -> tuple:
        """获取卡片类型颜色"""
        if card.card_type == CardType.POKEMON:
            return (255, 200, 100)  # 橙色
        elif card.card_type == CardType.ENERGY:
            return (100, 255, 100)  # 绿色
        elif card.card_type == CardType.TRAINER:
            return (100, 150, 255)  # 蓝色
        return (150, 150, 150)
    
    def _draw_pokemon_card_info(self, screen: pygame.Surface, pokemon: PokemonCard, rect: pygame.Rect):
        """绘制Pokemon卡片信息"""
        info_font = font_manager.get_font_by_size(9)
        
        # HP
        hp_text = f"HP: {pokemon.hp}"
        hp_surface = info_font.render(hp_text, True, Theme.get_color('text'))
        hp_rect = hp_surface.get_rect(centerx=rect.centerx, y=rect.y + 45)
        screen.blit(hp_surface, hp_rect)
        
        # 属性
        type_text = pokemon.pokemon_type.value.title()
        type_surface = info_font.render(type_text, True, Theme.get_color('text'))
        type_rect = type_surface.get_rect(centerx=rect.centerx, y=rect.y + 60)
        screen.blit(type_surface, type_rect)
        
        # 攻击数量
        if pokemon.attacks:
            attack_text = f"{len(pokemon.attacks)} 攻击"
            attack_surface = info_font.render(attack_text, True, Theme.get_color('text'))
            attack_rect = attack_surface.get_rect(centerx=rect.centerx, y=rect.y + 75)
            screen.blit(attack_surface, attack_rect)
    
    def _draw_energy_card_info(self, screen: pygame.Surface, energy: EnergyCard, rect: pygame.Rect):
        """绘制能量卡片信息"""
        info_font = font_manager.get_font_by_size(9)
        
        # 能量类型
        type_text = energy.energy_type.value.title()
        type_surface = info_font.render(type_text, True, Theme.get_color('text'))
        type_rect = type_surface.get_rect(centerx=rect.centerx, y=rect.y + 45)
        screen.blit(type_surface, type_rect)
        
        # 是否为基础能量
        basic_text = "基础" if energy.is_basic else "特殊"
        basic_surface = info_font.render(basic_text, True, Theme.get_color('text'))
        basic_rect = basic_surface.get_rect(centerx=rect.centerx, y=rect.y + 60)
        screen.blit(basic_surface, basic_rect)
    
    def _draw_trainer_card_info(self, screen: pygame.Surface, trainer: TrainerCard, rect: pygame.Rect):
        """绘制训练师卡片信息"""
        info_font = font_manager.get_font_by_size(9)
        
        # 训练师类型
        type_text = trainer.trainer_type.value.title()
        type_surface = info_font.render(type_text, True, Theme.get_color('text'))
        type_rect = type_surface.get_rect(centerx=rect.centerx, y=rect.y + 45)
        screen.blit(type_surface, type_rect)

    def _draw_deck_areas(self, screen: pygame.Surface):
        """绘制牌库和奖励卡区域"""
        # 玩家牌库和奖励卡
        self._draw_player_deck_area(screen, self.battle_engine.player1, is_player=True)
        
        # 对手牌库和奖励卡
        self._draw_player_deck_area(screen, self.battle_engine.player2, is_player=False)
    
    def _draw_player_deck_area(self, screen: pygame.Surface, player: Player, is_player: bool):
        """绘制玩家的牌库区域"""
        card_width = 60
        card_height = 80
        
        if is_player:
            # 玩家区域（右下角）
            deck_x = self.window_width - 200
            deck_y = self.window_height - 100
            prize_x = self.window_width - 130
            prize_y = self.window_height - 100
        else:
            # 对手区域（右上角）
            deck_x = self.window_width - 200
            deck_y = 20
            prize_x = self.window_width - 130
            prize_y = 20
        
        # 绘制牌库
        if player.deck.cards:
            deck_rect = pygame.Rect(deck_x, deck_y, card_width, card_height)
            self._draw_deck_pile(screen, len(player.deck.cards), deck_rect, "牌库")
        
        # 绘制奖励卡
        if player.prize_cards:
            prize_rect = pygame.Rect(prize_x, prize_y, card_width, card_height)
            self._draw_deck_pile(screen, len(player.prize_cards), prize_rect, "奖励")
    
    def _draw_deck_pile(self, screen: pygame.Surface, count: int, rect: pygame.Rect, label: str):
        """绘制卡牌堆"""
        # 卡牌背面
        pile_color = Theme.get_color('glass_bg_modern')[:3] + (200,)
        pile_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pile_surface.fill(pile_color)
        
        # 绘制边框
        pygame.draw.rect(pile_surface, Theme.get_color('modern_border'), 
                        (0, 0, rect.width, rect.height), 
                        width=2, border_radius=6)
        
        screen.blit(pile_surface, rect)
        
        # 绘制数量
        count_font = font_manager.get_font_by_size(14)
        count_surface = count_font.render(str(count), True, Theme.get_color('text'))
        count_rect = count_surface.get_rect(center=rect.center)
        screen.blit(count_surface, count_rect)
        
        # 绘制标签
        label_font = font_manager.get_font_by_size(10)
        label_surface = label_font.render(label, True, Theme.get_color('text'))
        label_rect = label_surface.get_rect(centerx=rect.centerx, y=rect.bottom + 2)
        screen.blit(label_surface, label_rect)
    
    def _draw_battle_effects(self, screen: pygame.Surface):
        """绘制战斗特效"""
        for effect in self.battle_effects:
            if effect['type'] == 'knockout':
                self._draw_knockout_effect(screen, effect)
    
    def _draw_knockout_effect(self, screen: pygame.Surface, effect: Dict):
        """绘制击倒特效"""
        # 简单的闪光效果
        flash_alpha = int(effect['alpha'])
        if flash_alpha > 0:
            flash_surface = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, flash_alpha // 4))
            screen.blit(flash_surface, (0, 0))
    
    def _draw_modern_buttons(self, screen: pygame.Surface):
        """绘制现代按钮"""
        for button in self.modern_buttons:
            # 转换到屏幕坐标
            screen_rect = pygame.Rect(
                self.window.rect.x + button.rect.x,
                self.window.rect.y + button.rect.y,
                button.rect.width,
                button.rect.height
            )
            
            # 创建临时按钮进行绘制
            temp_button = type(button)(
                screen_rect,
                button.text,
                getattr(button, 'icon', ''),
                button.button_type,
                button.font_size
            )
            temp_button.scale = button.scale
            temp_button.is_hover = button.is_hover
            temp_button.flash = button.flash
            
            temp_button.draw(screen, self.scale_factor)
    
    def close(self):
        """关闭窗口"""
        if self.is_visible:
            self.is_visible = False
            if self.window:
                self.window.kill()
            if self.on_close:
                self.on_close()
            print("🚪 关闭对战窗口")
    
    def cleanup(self):
        """清理资源"""
        if self.window:
            self.window.kill()
        self.modern_buttons.clear()
        self.battle_effects.clear()

# 对战窗口工厂函数
def create_battle_window(screen_width: int, screen_height: int, ui_manager,
                        player1_data: Dict, player2_data: Dict, 
                        message_manager: MessageManager, user_data: Dict,
                        is_ai_battle: bool = True) -> ModernBattleWindow:
    """
    创建对战窗口
    
    Args:
        screen_width: 屏幕宽度
        screen_height: 屏幕高度
        ui_manager: UI管理器
        player1_data: 玩家1数据
        player2_data: 玩家2数据
        message_manager: 消息管理器
        user_data: 用户数据
        is_ai_battle: 是否为AI对战
        
    Returns:
        对战窗口实例
    """
    from game.battle.battle_engine import create_battle
    
    # 创建对战引擎
    battle_engine = create_battle(player1_data, player2_data, is_ai_battle)
    
    # 设置游戏
    battle_engine.setup_game()
    battle_engine.start_turn()
    
    # 创建对战窗口
    battle_window = ModernBattleWindow(
        screen_width, screen_height, ui_manager,
        battle_engine, message_manager, user_data
    )
    
    return battle_window

# 简单的AI对战启动函数
def start_ai_battle(screen_width: int, screen_height: int, ui_manager,
                   user_deck, user_data: Dict, message_manager: MessageManager,
                   ai_difficulty: str = "normal") -> ModernBattleWindow:
    """
    启动AI对战
    
    Args:
        screen_width: 屏幕宽度
        screen_height: 屏幕高度
        ui_manager: UI管理器
        user_deck: 用户卡组
        user_data: 用户数据
        message_manager: 消息管理器
        ai_difficulty: AI难度
        
    Returns:
        对战窗口实例
    """
    from game.cards.deck_manager import Deck
    
    # 创建AI卡组（简化版）
    ai_deck = Deck("AI对手卡组")
    # TODO: 这里应该根据难度生成合适的AI卡组
    
    player1_data = {
        'id': user_data['user_id'],
        'name': user_data['username'],
        'deck': user_deck
    }
    
    player2_data = {
        'id': -1,  # AI玩家ID
        'name': f"AI对手({ai_difficulty})",
        'deck': ai_deck,
        'difficulty': ai_difficulty
    }
    
    return create_battle_window(
        screen_width, screen_height, ui_manager,
        player1_data, player2_data, message_manager, user_data,
        is_ai_battle=True
    )

# 快速测试对战功能
def test_battle_system():
    """测试对战系统功能"""
    print("🧪 对战系统测试")
    
    from game.cards.card_types import PokemonCard, PokemonType, Rarity, Attack
    from game.cards.deck_manager import Deck
    
    # 创建测试卡片
    pikachu = PokemonCard(
        card_id="test_pikachu",
        name="Pikachu",
        pokemon_type=PokemonType.ELECTRIC,
        hp=60,
        rarity=Rarity.COMMON,
        attacks=[
            Attack(
                name="Thunder Shock",
                cost=[PokemonType.ELECTRIC],
                damage=20,
                description="May cause paralysis"
            )
        ]
    )
    
    # 创建测试卡组
    test_deck = Deck("测试卡组")
    for _ in range(20):
        test_deck.add_card(pikachu)
    
    print("测试数据创建完成")
    return test_deck

if __name__ == "__main__":
    test_battle_system()