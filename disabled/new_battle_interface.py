# ==== new_battle_interface.py ====
# 保存为: game/ui/battle/battle_interface/new_battle_interface.py

"""
使用pygamecards重构的Pokemon TCG战斗界面
提供完整的拖拽交互、视觉效果和权限控制
"""

import pygame
from typing import Dict, List, Optional, Callable
from pygame_cards.board import GameBoard, GameBoardGraphic
from pygame_cards.hands import AlignedHand, RoundedHand, VerticalPileGraphic
from pygame_cards.deck import Deck
from pygame_cards.manager import CardsManager, CardSetRights
from pygame_cards.set import CardsSet
from pygame_cards.events import CARDSSET_CLICKED, CARD_MOVED
from pygame_cards import constants

# 导入我们的适配器
from .pokemon_card_adapter import PokemonCardAdapter, convert_to_pokemon_cardsset

class PokemonFieldGraphic(VerticalPileGraphic):
    """Pokemon场地图形类"""
    
    def __init__(self, cardset: CardsSet, title: str = "", is_enemy: bool = False):
        super().__init__(cardset, size=(150, 200))
        self.title = title
        self.is_enemy = is_enemy
        
        # 字体
        try:
            self.title_font = pygame.font.SysFont("arial", 14, bold=True)
        except:
            self.title_font = pygame.font.Font(None, 14)
    
    @property
    def surface(self) -> pygame.Surface:
        surf = super().surface
        
        # 添加标题
        if self.title:
            title_color = (255, 100, 100) if self.is_enemy else (100, 255, 100)
            title_surface = self.title_font.render(self.title, True, title_color)
            title_rect = title_surface.get_rect(centerx=surf.get_width()//2, y=5)
            surf.blit(title_surface, title_rect)
        
        return surf

class PokemonBattleBoard(GameBoard):
    """Pokemon战斗游戏板"""
    
    def __init__(self, screen_width: int, screen_height: int):
        super().__init__()
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 创建各个卡牌区域
        self._setup_card_areas()
        
        # 设置游戏板图形
        self.graphics = self._create_board_graphics()
    
    def _setup_card_areas(self):
        """设置卡牌区域 - 根据用户精确设计"""
        # 我方区域
        self.player_hand = CardsSet([])
        self.player_hand.name = "Player Hand"
        
        self.player_deck = CardsSet([])
        self.player_deck.name = "Player Deck"
        
        self.player_discard = CardsSet([])
        self.player_discard.name = "Player Discard"
        
        self.player_active = CardsSet([])
        self.player_active.name = "Player Active"
        
        # 我方备战区 - 3张
        self.player_bench_1 = CardsSet([])
        self.player_bench_1.name = "Player Bench 1"
        
        self.player_bench_2 = CardsSet([])
        self.player_bench_2.name = "Player Bench 2"
        
        self.player_bench_3 = CardsSet([])
        self.player_bench_3.name = "Player Bench 3"
        
        # 对手区域
        self.opponent_hand = CardsSet([])
        self.opponent_hand.name = "Opponent Hand"
        
        self.opponent_deck = CardsSet([])
        self.opponent_deck.name = "Opponent Deck"
        
        self.opponent_discard = CardsSet([])
        self.opponent_discard.name = "Opponent Discard"
        
        self.opponent_active = CardsSet([])
        self.opponent_active.name = "Opponent Active"
        
        # 对手备战区 - 3张
        self.opponent_bench_1 = CardsSet([])
        self.opponent_bench_1.name = "Opponent Bench 1"
        
        self.opponent_bench_2 = CardsSet([])
        self.opponent_bench_2.name = "Opponent Bench 2"
        
        self.opponent_bench_3 = CardsSet([])
        self.opponent_bench_3.name = "Opponent Bench 3"
        
        # 添加到游戏板
        self.cardsets = [
            # 我方区域
            self.player_hand, self.player_deck, self.player_discard, self.player_active,
            self.player_bench_1, self.player_bench_2, self.player_bench_3,
            # 对手区域
            self.opponent_hand, self.opponent_deck, self.opponent_discard, self.opponent_active,
            self.opponent_bench_1, self.opponent_bench_2, self.opponent_bench_3
        ]
    
    def _create_board_graphics(self):
        """创建游戏板图形 - 使用绝对坐标修复位置问题"""
        # 转换相对位置为绝对位置
        cardsets_abs_pos = {
            # 对手区域（上方）
            self.opponent_hand: (int(0.05 * self.screen_width), int(0.02 * self.screen_height)),
            self.opponent_deck: (int(0.05 * self.screen_width), int(0.15 * self.screen_height)),
            self.opponent_bench_1: (int(0.2 * self.screen_width), int(0.15 * self.screen_height)),
            self.opponent_bench_2: (int(0.32 * self.screen_width), int(0.15 * self.screen_height)),
            self.opponent_bench_3: (int(0.44 * self.screen_width), int(0.15 * self.screen_height)),
            self.opponent_discard: (int(0.56 * self.screen_width), int(0.15 * self.screen_height)),
            self.opponent_active: (int(0.4 * self.screen_width), int(0.3 * self.screen_height)),
            
            # 我方区域（下方）
            self.player_active: (int(0.4 * self.screen_width), int(0.5 * self.screen_height)),
            self.player_discard: (int(0.05 * self.screen_width), int(0.65 * self.screen_height)),
            self.player_bench_1: (int(0.15 * self.screen_width), int(0.65 * self.screen_height)),
            self.player_bench_2: (int(0.25 * self.screen_width), int(0.65 * self.screen_height)),
            self.player_bench_3: (int(0.35 * self.screen_width), int(0.65 * self.screen_height)),
            self.player_deck: (int(0.55 * self.screen_width), int(0.65 * self.screen_height)),
            self.player_hand: (int(0.05 * self.screen_width), int(0.82 * self.screen_height))
        }
        
        # 转换相对大小为绝对大小
        cardsets_abs_size = {
            # 手牌区域 - 水平展开
            self.player_hand: (int(0.7 * self.screen_width), int(0.15 * self.screen_height)),
            self.opponent_hand: (int(0.7 * self.screen_width), int(0.1 * self.screen_height)),
            
            # 战斗位 - 较大
            self.player_active: (int(0.14 * self.screen_width), int(0.18 * self.screen_height)),
            self.opponent_active: (int(0.14 * self.screen_width), int(0.18 * self.screen_height)),
            
            # 备战区 - 标准大小
            self.player_bench_1: (int(0.08 * self.screen_width), int(0.12 * self.screen_height)),
            self.player_bench_2: (int(0.08 * self.screen_width), int(0.12 * self.screen_height)),
            self.player_bench_3: (int(0.08 * self.screen_width), int(0.12 * self.screen_height)),
            
            self.opponent_bench_1: (int(0.1 * self.screen_width), int(0.12 * self.screen_height)),
            self.opponent_bench_2: (int(0.1 * self.screen_width), int(0.12 * self.screen_height)),
            self.opponent_bench_3: (int(0.1 * self.screen_width), int(0.12 * self.screen_height)),
            
            # 卡组和弃牌堆
            self.player_deck: (int(0.08 * self.screen_width), int(0.12 * self.screen_height)),
            self.player_discard: (int(0.08 * self.screen_width), int(0.12 * self.screen_height)),
            self.opponent_deck: (int(0.08 * self.screen_width), int(0.12 * self.screen_height)),
            self.opponent_discard: (int(0.08 * self.screen_width), int(0.12 * self.screen_height))
        }
        
        print(f"🔍 绝对坐标调试信息:")
        print(f"   手牌绝对位置: {cardsets_abs_pos[self.player_hand]}")
        print(f"   手牌绝对大小: {cardsets_abs_size[self.player_hand]}")
        print(f"   战斗位绝对位置: {cardsets_abs_pos[self.player_active]}")

        return GameBoardGraphic(
            cardsets_rel_pos=cardsets_abs_pos,  # 现在传入绝对位置
            cardsets_rel_size=cardsets_abs_size,  # 现在传入绝对大小
            size=(self.screen_width, self.screen_height)
        )

class PokemonBattleInterface:
    """Pokemon TCG战斗界面（pygamecards版本）"""
    
    def __init__(self, screen_width: int, screen_height: int, battle_controller, battle_cache=None):
        """
        初始化战斗界面
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            battle_controller: 战斗控制器
            battle_cache: 战斗缓存（可选）
        """
        print(f"🎮 初始化新版Pokemon TCG战斗界面: {screen_width}x{screen_height}")
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.battle_controller = battle_controller
        self.battle_cache = battle_cache
        
        # 加载背景图片
        self.background_image = None
        self._load_background()
        
        # 创建游戏板
        self.game_board = PokemonBattleBoard(screen_width, screen_height)
        
        # 创建卡牌管理器
        self.cards_manager = CardsManager(click_time=200)
        
        # 设置卡牌图形
        self._setup_cardset_graphics()
        print(f"🔍 游戏板调试:")
        print(f"   游戏板图形: {self.game_board.graphics}")
        print(f"   手牌位置: {self.game_board.graphics.cardsets_rel_pos.get(self.game_board.player_hand, 'NOT_FOUND')}")
        print(f"   手牌图形: {self.game_board.player_hand.graphics}")
        
        # 添加卡牌区域到管理器
        self._setup_cards_manager()
        
        # 状态
        self.battle_state = None
        self.last_update_time = 0
        
        # 字体
        try:
            self.title_font = pygame.font.SysFont("arial", 24, bold=True)
            self.info_font = pygame.font.SysFont("arial", 16)
            self.small_font = pygame.font.SysFont("arial", 12)
        except:
            self.title_font = pygame.font.Font(None, 24)
            self.info_font = pygame.font.Font(None, 16)
            self.small_font = pygame.font.Font(None, 12)
        
        # 回调
        self.on_card_action: Optional[Callable] = None
        self.on_battle_action: Optional[Callable] = None
        
        # 更新初始状态
        self._update_battle_state()
        
        print("✅ 新版Pokemon TCG战斗界面创建成功")
    
    def _load_background(self):
        """加载背景图片"""
        try:
            import os
            bg_path = os.path.join("assets", "images", "backgrounds", "battle_bg.png")
            if os.path.exists(bg_path):
                self.background_image = pygame.image.load(bg_path)
                # 缩放到屏幕大小
                self.background_image = pygame.transform.scale(
                    self.background_image, 
                    (self.screen_width, self.screen_height)
                )
                print(f"✅ 战斗背景加载成功: {bg_path}")
            else:
                print(f"⚠️ 战斗背景文件不存在: {bg_path}")
                self.background_image = None
        except Exception as e:
            print(f"❌ 加载战斗背景失败: {e}")
            self.background_image = None
    
    def _setup_cardset_graphics(self):
        """设置卡牌集合图形"""
        # 我方手牌 - 直线排列
        self.game_board.player_hand.graphics = AlignedHand(
            self.game_board.player_hand,
            card_spacing=0.02,  # 紧密排列
            size=(int(self.screen_width * 0.7), int(self.screen_height * 0.15))
        )
        
        # 对手手牌 - 显示卡背
        self.game_board.opponent_hand.graphics = Deck(
            self.game_board.opponent_hand,
            visible=False,  # 显示卡背
            card_back="assets/images/item/card_back.png",
            size=(int(self.screen_width * 0.7), int(self.screen_height * 0.1))
        )
        
        # 卡组 - 使用卡背图片
        self.game_board.player_deck.graphics = Deck(
            self.game_board.player_deck,
            visible=False,
            card_back="assets/images/item/card_back.png",
            size=(80, 120)
        )
        
        self.game_board.opponent_deck.graphics = Deck(
            self.game_board.opponent_deck,
            visible=False,
            card_back="assets/images/item/card_back.png",
            size=(80, 120)
        )
        
        # 弃牌堆
        self.game_board.player_discard.graphics = VerticalPileGraphic(
            self.game_board.player_discard,
            size=(80, 120)
        )
        
        self.game_board.opponent_discard.graphics = VerticalPileGraphic(
            self.game_board.opponent_discard,
            size=(80, 120)
        )
        
        # 战斗位
        self.game_board.player_active.graphics = PokemonFieldGraphic(
            self.game_board.player_active,
            title="Active",
            is_enemy=False
        )
        
        self.game_board.opponent_active.graphics = PokemonFieldGraphic(
            self.game_board.opponent_active,
            title="Enemy Active",
            is_enemy=True
        )
        
        # 我方备战区 - 3张
        self.game_board.player_bench_1.graphics = PokemonFieldGraphic(
            self.game_board.player_bench_1,
            title="Bench 1",
            is_enemy=False
        )
        
        self.game_board.player_bench_2.graphics = PokemonFieldGraphic(
            self.game_board.player_bench_2,
            title="Bench 2",
            is_enemy=False
        )
        
        self.game_board.player_bench_3.graphics = PokemonFieldGraphic(
            self.game_board.player_bench_3,
            title="Bench 3",
            is_enemy=False
        )
              
        # 对手备战区 - 3张
        self.game_board.opponent_bench_1.graphics = PokemonFieldGraphic(
            self.game_board.opponent_bench_1,
            title="Enemy Bench 1",
            is_enemy=True
        )
        
        self.game_board.opponent_bench_2.graphics = PokemonFieldGraphic(
            self.game_board.opponent_bench_2,
            title="Enemy Bench 2",
            is_enemy=True
        )
        
        self.game_board.opponent_bench_3.graphics = PokemonFieldGraphic(
            self.game_board.opponent_bench_3,
            title="Enemy Bench 3",
            is_enemy=True
        )
    
    def _setup_cards_manager(self):
        """设置卡牌管理器 - 使用绝对坐标"""
        board_graphics = self.game_board.graphics
        print(f"🔍 卡牌管理器调试:")
        print(f"   board_graphics: {board_graphics}")
        print(f"   cardsets_rel_pos keys: {list(board_graphics.cardsets_rel_pos.keys())[:3]}")

        # 我方手牌 - 可拖拽出去，可点击
        self.cards_manager.add_set(
            self.game_board.player_hand.graphics,
            board_graphics.cardsets_rel_pos[self.game_board.player_hand],  # 现在是绝对坐标
            CardSetRights(
                clickable=True,
                draggable_out=True,
                draggable_in=False,
                highlight_hovered_card=True
            )
        )
        
        # 我方Pokemon区域 - 可拖拽进出，可点击
        pokemon_areas = [
            self.game_board.player_active,
            self.game_board.player_bench_1,
            self.game_board.player_bench_2,
            self.game_board.player_bench_3
        ]
        
        for pokemon_area in pokemon_areas:
            self.cards_manager.add_set(
                pokemon_area.graphics,
                board_graphics.cardsets_rel_pos[pokemon_area],
                CardSetRights(
                    clickable=True,
                    draggable_out=True,
                    draggable_in=lambda card: hasattr(card, 'is_pokemon') and card.is_pokemon(),
                    highlight_hovered_card=True
                )
            )
        
        # 弃牌堆 - 只能拖拽进入，可查看
        self.cards_manager.add_set(
            self.game_board.player_discard.graphics,
            board_graphics.cardsets_rel_pos[self.game_board.player_discard],
            CardSetRights(
                clickable=True,
                draggable_out=False,
                draggable_in=True,
                highlight_hovered_card=True
            )
        )
        
        # 对手手牌区 - 只能查看
        self.cards_manager.add_set(
            self.game_board.opponent_hand.graphics,
            board_graphics.cardsets_rel_pos[self.game_board.opponent_hand],
            CardSetRights(
                clickable=True,
                draggable_out=False,
                draggable_in=False,
                highlight_hovered_card=False
            )
        )
        
        # 对手Pokemon区域 - 只能查看，不能操作
        opponent_areas = [
            self.game_board.opponent_active,
            self.game_board.opponent_bench_1,
            self.game_board.opponent_bench_2,
            self.game_board.opponent_bench_3
        ]
        
        for opponent_area in opponent_areas:
            self.cards_manager.add_set(
                opponent_area.graphics,
                board_graphics.cardsets_rel_pos[opponent_area],
                CardSetRights(
                    clickable=True,
                    draggable_out=False,
                    draggable_in=False,
                    highlight_hovered_card=True
                )
            )
        
        # 卡组和弃牌区 - 只能点击
        deck_areas = [
            self.game_board.player_deck,
            self.game_board.opponent_deck,
            self.game_board.opponent_discard
        ]
        
        for deck_area in deck_areas:
            self.cards_manager.add_set(
                deck_area.graphics,
                board_graphics.cardsets_rel_pos[deck_area],
                CardSetRights(
                    clickable=True,
                    draggable_out=False,
                    draggable_in=False,
                    highlight_hovered_card=False
                )
            )
    
    def _update_battle_state(self):
        """更新战斗状态 - 直接从battle_manager获取"""
        try:
            if self.battle_controller and self.battle_controller.current_battle:
                # 直接从battle_manager获取player_state
                battle_manager = self.battle_controller.current_battle
                player_state = battle_manager.get_player_state(1)  # 玩家ID=1
                ai_state = battle_manager.get_player_state(999)    # AI玩家ID=999
                
                print(f"🔍 直接获取玩家状态:")
                if player_state:
                    print(f"   手牌数量: {len(player_state.hand)}")
                    if player_state.hand:
                        print(f"   手牌类型: {type(player_state.hand[0])}")
                    
                    # 更新手牌 - 确保清空后再添加
                    self._safe_update_cardset(self.game_board.player_hand, player_state.hand, "Player Hand")
                    
                    # 更新前排Pokemon
                    if player_state.active_pokemon:
                        self._safe_update_cardset(self.game_board.player_active, [player_state.active_pokemon], "Player Active")
                    else:
                        self.game_board.player_active.clear()
                    
                    # 更新后备区Pokemon（分配到3个槽位）
                    bench_pokemon = player_state.bench_pokemon
                    bench_areas = [
                        self.game_board.player_bench_1,
                        self.game_board.player_bench_2,
                        self.game_board.player_bench_3
                    ]
                    
                    # 清空所有后备区
                    for bench_area in bench_areas:
                        bench_area.clear()
                    
                    # 分配Pokemon到后备区槽位
                    for i, pokemon in enumerate(bench_pokemon[:3]):  # 最多3只
                        if i < len(bench_areas) and pokemon is not None:
                            self._safe_update_cardset(bench_areas[i], [pokemon], f"Player Bench {i+1}")
                
                # 更新AI状态
                if ai_state:
                    # 显示AI手牌数量（但不显示具体卡牌）
                    # 创建空卡牌来表示AI手牌数量
                    ai_hand_count = len(ai_state.hand) if ai_state.hand else 0
                    self.game_board.opponent_hand.clear()
                    # 这里应该显示卡背，实际的Deck graphics会处理这个
                    
                    # 更新AI前排
                    if ai_state.active_pokemon:
                        self._safe_update_cardset(self.game_board.opponent_active, [ai_state.active_pokemon], "Opponent Active")
                    else:
                        self.game_board.opponent_active.clear()
                    
                    # 更新AI后备区
                    ai_bench_pokemon = ai_state.bench_pokemon
                    ai_bench_areas = [
                        self.game_board.opponent_bench_1,
                        self.game_board.opponent_bench_2,
                        self.game_board.opponent_bench_3
                    ]
                    
                    # 清空AI后备区
                    for bench_area in ai_bench_areas:
                        bench_area.clear()
                    
                    # 分配AI Pokemon到后备区槽位
                    for i, pokemon in enumerate(ai_bench_pokemon[:3]):  # 最多3只
                        if i < len(ai_bench_areas) and pokemon is not None:
                            self._safe_update_cardset(ai_bench_areas[i], [pokemon], f"Opponent Bench {i+1}")
                            
        except Exception as e:
            print(f"❌ 更新战斗状态失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _safe_update_cardset(self, cardset: CardsSet, cards_data, name: str):
        """安全地更新卡牌集合，避免None错误"""
        try:
            if not cards_data:
                cardset.clear()
                return
            
            # 过滤掉None值
            valid_cards = [card for card in cards_data if card is not None]
            
            if valid_cards:
                new_cardset = convert_to_pokemon_cardsset(valid_cards, name)
                self._update_cardset(cardset, new_cardset)
            else:
                cardset.clear()
                
        except Exception as e:
            print(f"❌ 安全更新卡牌集合失败 {name}: {e}")
            cardset.clear()
    
    def _sync_cardsets_with_battle_state(self):
        """同步卡牌集合与战斗状态"""
        if not self.battle_state:
            return
        
        try:
            # 获取玩家状态
            current_player_id = self.battle_state.get('current_player')
            player_states = self.battle_state.get('player_states', {})
            
            if current_player_id in player_states:
                player_state = player_states[current_player_id]
                
                # 更新手牌
                hand_cards = player_state.get('hand', [])
                if hand_cards:
                    new_hand = convert_to_pokemon_cardsset(hand_cards, "Player Hand")
                    self._update_cardset(self.game_board.player_hand, new_hand)
                
                # 更新场上Pokemon
                active_pokemon = player_state.get('active_pokemon')
                if active_pokemon:
                    active_cards = [active_pokemon]
                    new_active = convert_to_pokemon_cardsset(active_cards, "Player Active")
                    self._update_cardset(self.game_board.player_active, new_active)
                
                bench_pokemon = player_state.get('bench_pokemon', [])
                if bench_pokemon:
                    new_bench = convert_to_pokemon_cardsset(bench_pokemon, "Player Bench")
                    self._update_cardset(self.game_board.player_bench, new_bench)
            
            # 更新对手状态（类似）
            opponent_id = None
            for pid in player_states.keys():
                if pid != current_player_id:
                    opponent_id = pid
                    break
            
            if opponent_id and opponent_id in player_states:
                opponent_state = player_states[opponent_id]
                
                # 更新对手前排
                opponent_active = opponent_state.get('active_pokemon')
                if opponent_active:
                    opponent_active_cards = [opponent_active]
                    new_opponent_active = convert_to_pokemon_cardsset(opponent_active_cards, "Opponent Active")
                    self._update_cardset(self.game_board.opponent_active, new_opponent_active)
                
                # 更新对手后备区
                opponent_bench = opponent_state.get('bench_pokemon', [])
                if opponent_bench:
                    new_opponent_bench = convert_to_pokemon_cardsset(opponent_bench, "Opponent Bench")
                    self._update_cardset(self.game_board.opponent_bench, new_opponent_bench)
                    
        except Exception as e:
            print(f"❌ 同步卡牌集合失败: {e}")
    
    def _update_cardset(self, old_cardset: CardsSet, new_cardset: CardsSet):
        """更新卡牌集合"""
        # 清空旧集合
        old_cardset.clear()
        
        # 添加新卡牌
        old_cardset.extend(new_cardset)
        
        # 清除图形缓存
        if hasattr(old_cardset, 'graphics'):
            old_cardset.graphics.clear_cache()
    
    def handle_event(self, event) -> Optional[str]:
        """处理事件"""
        # ESC键返回
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("🔙 ESC键按下，返回战斗页面")
                return "back_to_battle_page"
            elif event.key == pygame.K_SPACE:
                print("⏭️ 空格键结束回合")
                self._end_turn()
        
        # 处理卡牌管理器事件
        self.cards_manager.process_events(event)
        
        # 处理卡牌事件
        if event.type == CARDSSET_CLICKED:
            self._handle_cardset_clicked(event)
        elif event.type == CARD_MOVED:
            self._handle_card_moved(event)
        
        return None
    
    def _handle_cardset_clicked(self, event):
        """处理卡牌集合点击事件"""
        cardset = event.set
        card = event.card
        
        print(f"🎯 卡牌集合点击: {cardset.name}")
        if card:
            print(f"   点击卡牌: {card.name}")
        
        # 根据不同区域执行不同操作
        if cardset == self.game_board.player_deck:
            print("📚 点击卡组 - 抽卡")
            self._draw_card()
        elif cardset == self.game_board.player_prizes:
            print("🏆 点击奖励卡")
        elif card and hasattr(card, 'is_pokemon') and card.is_pokemon():
            print(f"⚔️ 点击Pokemon: {card.name}")
            self._select_pokemon_for_action(card)
    
    def _handle_card_moved(self, event):
        """处理卡牌移动事件"""
        card = event.card
        from_set = event.from_set
        to_set = event.to_set
        
        print(f"🚚 卡牌移动: {card.name}")
        print(f"   从: {from_set.cardset.name}")
        print(f"   到: {to_set.cardset.name}")
        
        # 验证移动是否合法
        if self._validate_card_move(card, from_set.cardset, to_set.cardset):
            print("✅ 卡牌移动合法")
            self._execute_card_action(card, from_set.cardset, to_set.cardset)
        else:
            print("❌ 卡牌移动不合法，回退")
            # 回退移动
            to_set.cardset.remove(card)
            from_set.cardset.append(card)
    
    def _validate_card_move(self, card, from_set: CardsSet, to_set: CardsSet) -> bool:
        """验证卡牌移动是否合法"""
        # Pokemon只能放在Pokemon区域
        if hasattr(card, 'is_pokemon') and card.is_pokemon():
            pokemon_areas = [
                self.game_board.player_active,
                self.game_board.player_bench_1,
                self.game_board.player_bench_2,
                self.game_board.player_bench_3,
                self.game_board.player_discard
            ]
            return to_set in pokemon_areas
        
        # 训练师卡可以直接使用（放入弃牌堆）
        if hasattr(card, 'is_trainer') and card.is_trainer():
            return to_set == self.game_board.player_discard
        
        return True
    
    def _execute_card_action(self, card, from_set: CardsSet, to_set: CardsSet):
        """执行卡牌行动"""
        try:
            if self.battle_controller:
                # 根据移动类型创建相应的行动
                if to_set == self.game_board.player_active:
                    print(f"🎯 放置Pokemon到前排: {card.name}")
                    # 调用battle_controller的相应方法
                    
                elif to_set == self.game_board.player_bench:
                    print(f"🎯 放置Pokemon到后备区: {card.name}")
                    
                elif to_set == self.game_board.player_discard:
                    if hasattr(card, 'is_trainer') and card.is_trainer():
                        print(f"🎯 使用训练师卡: {card.name}")
                        # 执行训练师卡效果
                
                # 通知回调
                if self.on_card_action:
                    self.on_card_action(card, from_set.name, to_set.name)
                    
        except Exception as e:
            print(f"❌ 执行卡牌行动失败: {e}")
    
    def _draw_card(self):
        """抽卡"""
        try:
            if self.battle_controller:
                # 调用战斗控制器的抽卡方法
                result = self.battle_controller.process_player_action({
                    "type": "draw_card"
                })
                print(f"抽卡结果: {result}")
        except Exception as e:
            print(f"❌ 抽卡失败: {e}")
    
    def _end_turn(self):
        """结束回合"""
        try:
            if self.battle_controller:
                result = self.battle_controller.process_player_action({
                    "type": "end_turn"
                })
                print(f"结束回合结果: {result}")
        except Exception as e:
            print(f"❌ 结束回合失败: {e}")
    
    def _select_pokemon_for_action(self, pokemon_card):
        """选择Pokemon进行行动"""
        print(f"🎯 选择Pokemon进行行动: {pokemon_card.name}")
        
        # 这里可以显示Pokemon的行动菜单
        # 比如：攻击、撤退、使用道具等
        
        if self.on_battle_action:
            self.on_battle_action("select_pokemon", pokemon_card)
    
    def update(self, dt):
        """更新界面"""
        # 定期更新战斗状态
        self.last_update_time += dt
        if self.last_update_time > 1.0:  # 每秒更新一次
            self._update_battle_state()
            self.last_update_time = 0
        
        # 更新卡牌管理器
        self.cards_manager.update(dt * 1000)  # 转换为毫秒
    
    def draw(self, screen):
        """绘制界面"""
        # 1. 绘制背景（不要再用fill覆盖！）
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
            print("🎨 背景已绘制")
        else:
            screen.fill((76, 175, 80))  # 只有没有背景图时才填充
            print("🎨 使用默认背景色")
        
        # 2. 绘制标题和状态信息
        self._draw_title_and_status(screen)
        
        # 3. 绘制游戏板背景线条（保留分隔线但去掉色块）
        self._draw_board_background(screen)
        
        # 4. 绘制卡牌管理器
        self.cards_manager.draw(screen)
        print("🎨 卡牌管理器已绘制")
        
        # 5. 绘制UI覆盖层
        self._draw_ui_overlay(screen)
        print("🎨 UI覆盖层已绘制")
    
    def _draw_title_and_status(self, screen):
        """绘制标题和状态信息"""
        # 标题
        title = "Pokemon TCG Battle"
        title_surface = self.title_font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(centerx=self.screen_width//2, y=10)
        screen.blit(title_surface, title_rect)
        
        # 状态信息
        if self.battle_state:
            info_y = 40
            
            # 当前玩家
            current_player = self.battle_state.get('current_player', 'Unknown')
            player_text = f"Current Player: {current_player}"
            player_surface = self.info_font.render(player_text, True, (200, 200, 200))
            screen.blit(player_surface, (10, info_y))
            
            # 当前阶段
            phase = self.battle_state.get('phase', 'unknown')
            phase_text = f"Phase: {phase}"
            phase_surface = self.info_font.render(phase_text, True, (200, 200, 200))
            screen.blit(phase_surface, (250, info_y))
            
            # 回合数
            turn = self.battle_state.get('turn', 1)
            turn_text = f"Turn: {turn}"
            turn_surface = self.info_font.render(turn_text, True, (200, 200, 200))
            screen.blit(turn_surface, (400, info_y))
        
        # 操作提示
        hint = "Drag cards to play | Click Pokemon to select | ESC to exit | Space to end turn"
        hint_surface = self.small_font.render(hint, True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(centerx=self.screen_width//2, y=self.screen_height-20)
        screen.blit(hint_surface, hint_rect)
    
    def _draw_board_background(self, screen):
        """绘制游戏板背景 - 只保留分隔线，去掉红绿色块"""
        # 绘制分隔线
        center_y = self.screen_height // 2
        pygame.draw.line(screen, (100, 100, 100), 
                        (50, center_y), (self.screen_width-50, center_y), 2)
        
        # 标记玩家和对手区域
        player_label = self.info_font.render("PLAYER", True, (100, 255, 100))
        screen.blit(player_label, (10, center_y + 10))
        
        opponent_label = self.info_font.render("OPPONENT", True, (255, 100, 100))
        screen.blit(opponent_label, (10, center_y - 30))
    
    def _draw_ui_overlay(self, screen):
        """绘制UI覆盖层 - 信息区域"""
        info_x = int(self.screen_width * 0.81)
        info_y = 30
        line_height = 20
        
        # 绘制游戏状态信息
        if self.battle_controller and self.battle_controller.current_battle:
            try:
                battle_manager = self.battle_controller.current_battle
                player_state = battle_manager.get_player_state(1)
                
                if player_state:
                    # 能量信息
                    energy_text = f"Energy: {player_state.energy_points}"
                    energy_surface = self.info_font.render(energy_text, True, (255, 255, 0))
                    screen.blit(energy_surface, (info_x, info_y))
                    info_y += line_height
                    
                    # 奖励卡信息
                    prizes_text = f"Prizes: {player_state.prize_cards_taken}/3"
                    prizes_surface = self.info_font.render(prizes_text, True, (255, 215, 0))
                    screen.blit(prizes_surface, (info_x, info_y))
                    info_y += line_height
                    
                    # 卡组数量
                    deck_text = f"Deck: {len(player_state.deck)}"
                    deck_surface = self.info_font.render(deck_text, True, (200, 200, 200))
                    screen.blit(deck_surface, (info_x, info_y))
                    info_y += line_height * 2
            except Exception as e:
                print(f"❌ 绘制状态信息失败: {e}")
        
        # 绘制调试信息
        debug_title = self.small_font.render("DEBUG INFO:", True, (180, 180, 180))
        screen.blit(debug_title, (info_x, info_y))
        info_y += 15
        
        debug_info = [
            f"Hand: {len(self.game_board.player_hand)}",
            f"Active: {len(self.game_board.player_active)}",
            f"Bench1: {len(self.game_board.player_bench_1)}",
            f"Bench2: {len(self.game_board.player_bench_2)}",
            f"Bench3: {len(self.game_board.player_bench_3)}",
            f"Discard: {len(self.game_board.player_discard)}",
        ]
        
        for info in debug_info:
            debug_surface = self.small_font.render(info, True, (150, 150, 150))
            screen.blit(debug_surface, (info_x, info_y))
            info_y += 12
        
        # 绘制操作提示
        button_area_y = int(self.screen_height * 0.7)
        button_title = self.small_font.render("CONTROLS:", True, (180, 180, 180))
        screen.blit(button_title, (info_x, button_area_y))
        button_area_y += 20
        
        # 操作提示
        controls = [
            "SPACE - End Turn",
            "ESC - Forfeit", 
            "Drag cards to play",
            "Click to inspect"
        ]
        
        for control in controls:
            control_surface = self.small_font.render(control, True, (120, 120, 120))
            screen.blit(control_surface, (info_x, button_area_y))
            button_area_y += 14
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理新版Pokemon TCG战斗界面")
        
        # 清理卡牌管理器
        if hasattr(self.cards_manager, 'cleanup'):
            self.cards_manager.cleanup()
        
        # 清理游戏板
        if hasattr(self.game_board, 'cleanup'):
            self.game_board.cleanup()


# 兼容性别名
BattleInterface = PokemonBattleInterface

# 创建函数，用于替换现有的battle_ui.py
def create_battle_interface(screen_width: int, screen_height: int, battle_controller, battle_cache=None):
    """创建战斗界面的工厂函数"""
    return PokemonBattleInterface(screen_width, screen_height, battle_controller, battle_cache)