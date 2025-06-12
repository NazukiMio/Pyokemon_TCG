# ==== fixed_battle_interface.py ====
# 保存为: game/ui/battle/battle_interface/battle_interface.py

"""
修复后的Pokemon TCG战斗界面
重点解决数据获取问题，确保获取真实卡牌数据而不是占位符
"""

import pygame
import os
import time
import threading
from typing import Dict, List, Optional, Callable
from pygame_cards.board import GameBoard, GameBoardGraphic
from pygame_cards.hands import AlignedHand, VerticalPileGraphic
from pygame_cards.deck import Deck
from pygame_cards.manager import CardsManager, CardSetRights
from pygame_cards.set import CardsSet
from pygame_cards.events import CARDSSET_CLICKED, CARD_MOVED
from pygame_cards import constants

# 导入我们的适配器
from .pokemon_card_adapter import PokemonCardAdapter, convert_to_pokemon_cardsset

class PokemonCardsManager(CardsManager):
    def populate_from_state(self, battle_state):
        """
        从战斗状态填充CardsManager的区域。
        为每张卡创建PokemonCardAdapter并分配到相应区域。
        """
        print(f"🔍 [调试] PokemonCardsManager.populate_from_state():")
        print(f"   接收参数类型: {type(battle_state)}")
        
        if not hasattr(self, "interface") or not getattr(self, "interface"):
            print("⚠️ PokemonCardsManager: 没有关联到任何BattleInterface")
            return
        
        # ✅ 修复：直接使用传入的字典，不要检查"state"键
        if isinstance(battle_state, dict):
            print(f"🔍 [调试] battle_state是字典，键: {list(battle_state.keys())}")
            # 直接传递字典给setup_from_battle_state
            actual_state = battle_state
        else:
            actual_state = battle_state
            print(f"🔍 [调试] 直接使用状态，类型: {type(actual_state)}")
        
        # 委托给BattleInterface.setup_from_battle_state处理填充逻辑
        try:
            self.interface.setup_from_battle_state(actual_state)
            print("✅ setup_from_battle_state调用成功")
        except Exception as e:
            print(f"❌ 从状态填充失败: {e}")
            import traceback
            traceback.print_exc()
    
    def get_battle_cache(self):
        """获取战斗缓存实例"""
        if hasattr(self, "_battle_cache"):
            return self._battle_cache
        return None
    
    def set_battle_cache(self, cache):
        """设置战斗缓存实例"""
        self._battle_cache = cache
        
        # 同时设置给PokemonCardAdapter
        try:
            from .pokemon_card_adapter import PokemonCardAdapter
            PokemonCardAdapter.battle_cache = cache
            print("✅ 战斗缓存已设置到PokemonCardAdapter")
        except Exception as e:
            print(f"❌ 设置PokemonCardAdapter缓存失败: {e}")
    
    def sync_with_battle_state(self, battle_state):
        """与战斗状态同步（别名方法）"""
        self.populate_from_state(battle_state)
    
    def get_card_count_summary(self):
        """获取卡牌数量统计"""
        if not hasattr(self, "interface") or not self.interface:
            return {}
        
        try:
            game_board = self.interface.game_board
            summary = {}
            
            # 统计各区域卡牌数量
            areas = {
                'player_hand': '玩家手牌',
                'player_active': '玩家前排',
                'player_deck': '玩家卡组',
                'opponent_hand': '对手手牌',
                'opponent_active': '对手前排',
                'opponent_deck': '对手卡组'
            }
            
            for area_name, display_name in areas.items():
                if hasattr(game_board, area_name):
                    cardset = getattr(game_board, area_name)
                    if hasattr(cardset, 'cards'):
                        summary[display_name] = len(cardset.cards)
                    else:
                        summary[display_name] = 0
                else:
                    summary[display_name] = 0
            
            return summary
            
        except Exception as e:
            print(f"❌ 获取卡牌统计失败: {e}")
            return {}
    
    def validate_state(self, battle_state):
        """验证战斗状态的有效性"""
        if not isinstance(battle_state, dict):
            return False, "battle_state不是字典格式"
        
        required_keys = ['player', 'opponent']
        for key in required_keys:
            if key not in battle_state:
                return False, f"缺少必需的键: {key}"
        
        # 验证玩家数据结构
        player_data = battle_state.get('player', {})
        opponent_data = battle_state.get('opponent', {})
        
        for data_name, data in [('player', player_data), ('opponent', opponent_data)]:
            if not isinstance(data, dict):
                return False, f"{data_name}数据不是字典格式"
        
        return True, "战斗状态有效"
    
    def debug_print_state(self, battle_state):
        """调试打印战斗状态信息"""
        print("🔍 [调试] 战斗状态详情:")
        print(f"   类型: {type(battle_state)}")
        
        if isinstance(battle_state, dict):
            print(f"   键: {list(battle_state.keys())}")
            
            if 'player' in battle_state:
                player_data = battle_state['player']
                print(f"   玩家数据: {type(player_data)}")
                if isinstance(player_data, dict):
                    print(f"     键: {list(player_data.keys())}")
                    print(f"     手牌数量: {player_data.get('hand_size', 'N/A')}")
                    print(f"     卡组数量: {player_data.get('deck_size', 'N/A')}")
            
            if 'opponent' in battle_state:
                opponent_data = battle_state['opponent']
                print(f"   对手数据: {type(opponent_data)}")
                if isinstance(opponent_data, dict):
                    print(f"     键: {list(opponent_data.keys())}")
                    print(f"     手牌数量: {opponent_data.get('hand_size', 'N/A')}")
                    print(f"     卡组数量: {opponent_data.get('deck_size', 'N/A')}")
        
        # 验证状态
        is_valid, message = self.validate_state(battle_state)
        print(f"   状态有效性: {is_valid} - {message}")

class FixedPokemonFieldGraphic(VerticalPileGraphic):
    """修复的Pokemon场地图形类"""
    
    def __init__(self, cardset: CardsSet, title: str = "", is_enemy: bool = False):
        super().__init__(cardset, size=(90, 126))
        self.title = title
        self.is_enemy = is_enemy
        
        # 字体
        try:
            self.title_font = pygame.font.SysFont("notosansregular", 14, bold=True)
        except:
            self.title_font = pygame.font.Font(None, 14)
    
    @property
    def surface(self) -> pygame.Surface:
        surf = super().surface.copy()  # 复制基础表面
        
        # 添加标题
        if self.title:
            title_color = (255, 100, 100) if self.is_enemy else (100, 255, 100)
            title_surface = self.title_font.render(self.title, True, title_color)
            title_rect = title_surface.get_rect(centerx=surf.get_width()//2, y=5)
            surf.blit(title_surface, title_rect)
        
        return surf
    
    def with_hovered(self, card, radius: float = 20, **kwargs) -> pygame.Surface:
        """实现悬停效果"""
        if card is None:
            return pygame.Surface((0, 0), pygame.SRCALPHA)
        
        try:
            from pygame_cards.effects import outer_halo
            
            # 创建悬停表面
            card.graphics.size = self.card_size
            highlighted_surf = outer_halo(card.graphics.surface, radius=radius, **kwargs)
            
            # 创建输出表面
            out_surf = pygame.Surface(self.size, pygame.SRCALPHA)
            
            # 绘制高光效果
            highlighted_surf = pygame.transform.scale(
                highlighted_surf,
                (self.card_size[0] + 2 * int(radius), self.card_size[1] + 2 * int(radius))
            )
            
            # 计算位置（假设卡牌居中）
            x_pos = (self.size[0] - self.card_size[0]) // 2
            y_pos = (self.size[1] - self.card_size[1]) // 2
            
            out_surf.blit(highlighted_surf, (x_pos - int(radius), y_pos - int(radius)))
            out_surf.blit(card.graphics.surface, (x_pos, y_pos))
            
            return out_surf
        except Exception as e:
            print(f"⚠️ 悬停效果失败: {e}")
            return self.surface

class FixedDeck(Deck):
    """修复的卡组图形，正确显示卡背"""
    
    def __init__(self, *args, **kwargs):
        # 确保显示卡背
        kwargs.setdefault('visible', False)
        kwargs.setdefault('card_back', 'assets/images/item/card_back.png')
        super().__init__(*args, **kwargs)
    
    @property
    def surface(self) -> pygame.Surface:
        """正确显示卡背"""
        surf = pygame.Surface(self.size, pygame.SRCALPHA)
        
        if len(self.cardset) > 0:
            # 显示卡背堆叠效果
            for i in range(min(3, len(self.cardset))):  # 最多显示3层
                offset_x = i * 2
                offset_y = i * 2
                pos = (
                    (self.size[0] - self.card_size[0]) // 2 + offset_x,
                    (self.size[1] - self.card_size[1]) // 2 + offset_y
                )
                surf.blit(self.card_back, pos)
        
        return surf

class BattleControlPanel:
    """战斗控制面板"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 控制面板区域
        panel_width = int(screen_width * 0.18)
        self.panel_rect = pygame.Rect(
            screen_width - panel_width, 
            0, 
            panel_width, 
            screen_height
        )
        
        # 字体
        try:
            self.title_font = pygame.font.SysFont("notosansregular", 16, bold=True)
            self.button_font = pygame.font.SysFont("notosansregular", 14, bold=True)
            self.info_font = pygame.font.SysFont("notosansregular", 12)
        except:
            self.title_font = pygame.font.Font(None, 16)
            self.button_font = pygame.font.Font(None, 14)
            self.info_font = pygame.font.Font(None, 12)
        
        # 按钮
        self.buttons = {}
        self._create_buttons()
        
        # 状态
        self.battle_state = None
        
    def _create_buttons(self):
        """创建控制按钮"""
        button_width = self.panel_rect.width - 20
        button_height = 35
        start_y = 100
        spacing = 10
        
        button_configs = [
            ("draw_card", "Robar carta", (100, 150, 255)),
            ("gain_energy", "Ganar energía", (255, 200, 100)),
            ("attack", "Atacar", (255, 100, 100)),
            ("end_turn", "Terminar turno", (150, 255, 150)),
            ("surrender", "Rendirse", (200, 200, 200))
        ]
        
        for i, (key, text, color) in enumerate(button_configs):
            y = start_y + i * (button_height + spacing)
            button_rect = pygame.Rect(
                self.panel_rect.x + 10,
                y,
                button_width,
                button_height
            )
            
            self.buttons[key] = {
                'rect': button_rect,
                'text': text,
                'color': color,
                'enabled': False,
                'visible': True
            }
    
    def update_button_states(self, battle_state, player_state):
        """更新按钮状态"""
        if not battle_state or not player_state:
            return
        
        current_phase = battle_state.current_phase.value if hasattr(battle_state.current_phase, 'value') else str(battle_state.current_phase)
        current_player = battle_state.current_turn_player
        user_id = 1  # 假设用户ID为1
        
        # 重置所有按钮
        for button in self.buttons.values():
            button['enabled'] = False
        
        # 只在玩家回合启用按钮
        if current_player == user_id:
            if current_phase == "draw":
                self.buttons['draw_card']['enabled'] = True
            elif current_phase == "energy":
                self.buttons['gain_energy']['enabled'] = True
            elif current_phase == "action":
                if player_state.can_attack():
                    self.buttons['attack']['enabled'] = True
                self.buttons['end_turn']['enabled'] = True
        
        # 投降按钮总是可用
        self.buttons['surrender']['enabled'] = True
    
    def handle_click(self, pos) -> Optional[str]:
        """处理点击事件"""
        for key, button in self.buttons.items():
            if button['enabled'] and button['rect'].collidepoint(pos):
                return key
        return None
    
    def draw(self, screen, battle_state=None, player_state=None, opponent_state=None):
        """绘制控制面板"""
        # 背景
        panel_surf = pygame.Surface((self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA)
        panel_surf.fill((40, 40, 60, 200))  # 半透明背景
        screen.blit(panel_surf, self.panel_rect)
        
        # 标题
        title = "Panel de control"
        title_surface = self.title_font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(centerx=self.panel_rect.centerx, y=self.panel_rect.y + 10)
        screen.blit(title_surface, title_rect)
        
        # 状态信息
        if battle_state:
            info_y = self.panel_rect.y + 40
            
            # 当前阶段
            phase = battle_state.current_phase.value if hasattr(battle_state.current_phase, 'value') else str(battle_state.current_phase)
            phase_text = f"Fase: {phase}"
            phase_surface = self.info_font.render(phase_text, True, (200, 200, 200))
            screen.blit(phase_surface, (self.panel_rect.x + 10, info_y))
            
            # 当前玩家
            current_player = "Usted" if battle_state.current_turn_player == 1 else "AI"
            player_text = f"Turno: {current_player}"
            player_surface = self.info_font.render(player_text, True, (200, 200, 200))
            screen.blit(player_surface, (self.panel_rect.x + 10, info_y + 15))
        
        # 玩家状态
        if player_state:
            info_y = self.panel_rect.y + 350
            
            stats = [
                f"Energía: {player_state.energy_points}",
                f"Mano: {len(player_state.hand)}",
                f"Mazo: {len(player_state.deck)}",
                f"Premio: {player_state.prize_cards_taken}/3"
            ]
            
            for i, stat in enumerate(stats):
                stat_surface = self.info_font.render(stat, True, (255, 255, 255))
                screen.blit(stat_surface, (self.panel_rect.x + 10, info_y + i * 15))
        
        # 绘制按钮
        for key, button in self.buttons.items():
            if not button['visible']:
                continue
                
            rect = button['rect']
            color = button['color'] if button['enabled'] else (100, 100, 100)
            
            # 按钮背景
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)
            
            # 按钮文字
            text_color = (255, 255, 255) if button['enabled'] else (150, 150, 150)
            text_surface = self.button_font.render(button['text'], True, text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)

class FixedPokemonBattleBoard(GameBoard):
    """修复的Pokemon战斗游戏板"""
    
    def __init__(self, screen_width: int, screen_height: int):
        super().__init__()
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 为控制面板留出空间
        self.game_area_width = int(screen_width * 0.82)
        
        # 创建各个卡牌区域
        self._setup_card_areas()
        
        # 设置游戏板图形
        self.graphics = self._create_board_graphics()
    
    def _setup_card_areas(self):
        """设置卡牌区域"""
        # 我方区域
        self.player_hand = CardsSet([])
        self.player_hand.name = "Mano Jugador"
        
        self.player_deck = CardsSet([])
        self.player_deck.name = "Mazo Jugador"
        
        self.player_discard = CardsSet([])
        self.player_discard.name = "Descartes Jugador"
        
        self.player_active = CardsSet([])
        self.player_active.name = "Activo Jugador"
        
        # 我方备战区
        self.player_bench_1 = CardsSet([])
        self.player_bench_1.name = "Banca Jucador 1"
        
        self.player_bench_2 = CardsSet([])
        self.player_bench_2.name = "Banca Jucador 2"
        
        self.player_bench_3 = CardsSet([])
        self.player_bench_3.name = "Banca Jucador 3"
        
        # 对手区域
        self.opponent_hand = CardsSet([])
        self.opponent_hand.name = "Mano Rival"
        
        self.opponent_deck = CardsSet([])
        self.opponent_deck.name = "Mazo Rival"
        
        self.opponent_discard = CardsSet([])
        self.opponent_discard.name = "Descartes Rival"
        
        self.opponent_active = CardsSet([])
        self.opponent_active.name = "Activo Rival"
        
        # 对手备战区
        self.opponent_bench_1 = CardsSet([])
        self.opponent_bench_1.name = "Banca Enemiga 1"
        
        self.opponent_bench_2 = CardsSet([])
        self.opponent_bench_2.name = "Banca Enemiga 2"
        
        self.opponent_bench_3 = CardsSet([])
        self.opponent_bench_3.name = "Banca Enemiga 3"
        
        # 添加到游戏板
        self.cardsets = [
            self.player_hand, self.player_deck, self.player_discard, self.player_active,
            self.player_bench_1, self.player_bench_2, self.player_bench_3,
            self.opponent_hand, self.opponent_deck, self.opponent_discard, self.opponent_active,
            self.opponent_bench_1, self.opponent_bench_2, self.opponent_bench_3
        ]
    
    def _create_board_graphics(self):
        """创建游戏板图形 - 根据1280x720实测数据修正百分比"""
        
        # 🎯 根据实测坐标计算的精确百分比（基于1280x720）
        cardsets_abs_pos = {
            # 🔴 对手区域（上方）
            self.opponent_deck: (int(0.052 * self.game_area_width), int(0.145 * self.screen_height)),      # x58 y100
            self.opponent_bench_1: (int(0.235 * self.game_area_width), int(0.055 * self.screen_height)),  # x250 y35
            self.opponent_bench_2: (int(0.403 * self.game_area_width), int(0.055 * self.screen_height)),  # x422 y35
            self.opponent_bench_3: (int(0.565 * self.game_area_width), int(0.055 * self.screen_height)),  # x600 y35
            self.opponent_active: (int(0.403 * self.game_area_width), int(0.251 * self.screen_height)),    # x422 y178
            self.opponent_discard: (int(0.770 * self.game_area_width), int(0.145 * self.screen_height)),  # x814 y100
            
            # 🔵 我方区域（下方）
            self.player_discard: (int(0.052 * self.game_area_width), int(0.671 * self.screen_height)),    # x58 y479
            self.player_bench_1: (int(0.235 * self.game_area_width), int(0.770 * self.screen_height)),    # x250 y550
            self.player_bench_2: (int(0.403 * self.game_area_width), int(0.770 * self.screen_height)),    # x422 y550
            self.player_bench_3: (int(0.565 * self.game_area_width), int(0.770 * self.screen_height)),    # x600 y550
            self.player_active: (int(0.403 * self.game_area_width), int(0.567 * self.screen_height)),      # x422 y407
            self.player_deck: (int(0.770 * self.game_area_width), int(0.671 * self.screen_height)),        # x814 y479
            
            # 🃏 手牌区域（调整位置让部分在窗口外）
            self.opponent_hand: (int(0.1 * self.game_area_width), int(-0.08 * self.screen_height)),        # 上半部分窗口外
            self.player_hand: (int(0.1 * self.game_area_width), int(0.92 * self.screen_height))            # 下半部分窗口外
        }
        
        # 🎯 统一格子大小（86x120像素的百分比）
        cardsets_abs_size = {
            # 所有战斗区域统一使用86x120对应的百分比
            self.opponent_deck: (int(0.067 * self.game_area_width), int(0.170 * self.screen_height)),
            self.opponent_bench_1: (int(0.067 * self.game_area_width), int(0.170 * self.screen_height)),
            self.opponent_bench_2: (int(0.067 * self.game_area_width), int(0.170 * self.screen_height)),
            self.opponent_bench_3: (int(0.067 * self.game_area_width), int(0.170 * self.screen_height)),
            self.opponent_active: (int(0.067 * self.game_area_width), int(0.170 * self.screen_height)),
            self.opponent_discard: (int(0.067 * self.game_area_width), int(0.170 * self.screen_height)),
            
            self.player_deck: (int(0.067 * self.game_area_width), int(0.170 * self.screen_height)),
            self.player_bench_1: (int(0.067 * self.game_area_width), int(0.170 * self.screen_height)),
            self.player_bench_2: (int(0.067 * self.game_area_width), int(0.170 * self.screen_height)),
            self.player_bench_3: (int(0.067 * self.game_area_width), int(0.170 * self.screen_height)),
            self.player_active: (int(0.067 * self.game_area_width), int(0.170 * self.screen_height)),
            self.player_discard: (int(0.067 * self.game_area_width), int(0.170 * self.screen_height)),
            
            # 手牌区域（横向展开容纳多张卡）
            self.opponent_hand: (int(0.8 * self.game_area_width), int(0.170 * self.screen_height)),
            self.player_hand: (int(0.8 * self.game_area_width), int(0.170 * self.screen_height))
        }

        return GameBoardGraphic(
            cardsets_rel_pos=cardsets_abs_pos,
            cardsets_rel_size=cardsets_abs_size,
            size=(self.game_area_width, self.screen_height)
        )

class BattleInterface:
    """修复的Pokemon TCG战斗界面"""
    
    def __init__(self, screen_width: int, screen_height: int, battle_controller, battle_cache=None):
        print(f"🎮 初始化修复版Pokemon TCG战斗界面: {screen_width}x{screen_height}")
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.battle_controller = battle_controller
        self.battle_cache = battle_cache
        if self.battle_cache:
            from game.ui.battle.battle_interface.pokemon_card_adapter import PokemonCardAdapter
            PokemonCardAdapter.battle_cache = self.battle_cache
        
        # 等待战斗控制器准备完成
        self._wait_for_battle_ready()
        
        # 加载背景图片
        self.background_image = None
        self._load_background()
        
        # 如果提供了 battle_cache，则预加载当前战斗的卡牌图片
        if self.battle_cache:
            self.battle_cache.preload_cards_from_battle(self.battle_controller)

        # 创建游戏板
        self.game_board = FixedPokemonBattleBoard(screen_width, screen_height)
        
        # 创建卡牌管理器
        self.cards_manager = PokemonCardsManager(click_time=200)

        # Vincular la instancia de CardsManager con la interfaz para acceso al método de poblado
        self.cards_manager.interface = self
        
        # 创建控制面板
        self.control_panel = BattleControlPanel(screen_width, screen_height)
        
        # 设置卡牌图形
        self._setup_cardset_graphics()
        
        # 添加卡牌区域到管理器
        self._setup_cards_manager()
        
        # 🔧 添加更新锁防止并发冲突
        self._updating_state = False

        # 🔧 添加调试模式
        self.debug_mode = False  # 按 D 键切换
        self.show_ruler = False  # 按 R 键切换标尺
        self.mouse_pos = (0, 0)  # 鼠标位置

        # 状态
        self.battle_state = None
        self.last_update_time = 0

        # 字体
        try:
            self.title_font = pygame.font.SysFont("notosansregular", 24, bold=True)
            self.info_font = pygame.font.SysFont("notosansregular", 16)
            self.small_font = pygame.font.SysFont("notosansregular", 12)
        except:
            self.title_font = pygame.font.Font(None, 24)
            self.info_font = pygame.font.Font(None, 16)
            self.small_font = pygame.font.Font(None, 12)
        
        # 立即更新初始状态
        self._update_battle_state()
        
        print("✅ 修复版Pokemon TCG战斗界面创建成功")
    
    # 调试界面ui布局内容
    def toggle_debug_mode(self):
        """切换调试模式"""
        self.debug_mode = not self.debug_mode
        print(f"🔍 调试模式: {'开启' if self.debug_mode else '关闭'}")

    def toggle_ruler(self):
        """切换标尺显示"""
        self.show_ruler = not self.show_ruler
        print(f"📏 标尺显示: {'开启' if self.show_ruler else '关闭'}")

    def update_mouse_pos(self, pos):
        """更新鼠标位置"""
        self.mouse_pos = pos

    def draw_debug_overlay(self, screen):
        """绘制调试信息覆盖层"""
        if not self.debug_mode:
            return
        
        import pygame
        
        # 创建半透明覆盖层
        overlay = pygame.Surface((screen.get_width(), screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        
        # 字体
        try:
            font = pygame.font.Font(None, 24)
            small_font = pygame.font.Font(None, 18)
        except:
            font = pygame.font.SysFont('Arial', 24)
            small_font = pygame.font.SysFont('Arial', 18)
        
        # 📏 绘制网格标尺
        if self.show_ruler:
            self._draw_ruler_grid(screen, font)
        
        # 🎯 绘制战斗区域边界
        self._draw_battle_areas_bounds(screen, font)
        
        # 🃏 绘制卡牌信息
        self._draw_cards_info(screen, small_font)
        
        # 🖱️ 显示鼠标坐标和区域信息
        self._draw_mouse_info(screen, font)
        
        # 📊 显示总体布局信息
        self._draw_layout_info(screen, font)

    def _draw_ruler_grid(self, screen, font):
        """绘制标尺网格"""
        import pygame
        
        width, height = screen.get_size()
        
        # 绘制垂直线（每100像素）
        for x in range(0, width, 100):
            pygame.draw.line(screen, (0, 255, 0), (x, 0), (x, height), 1)
            # 标注坐标
            text = font.render(str(x), True, (0, 255, 0))
            screen.blit(text, (x + 2, 2))
        
        # 绘制水平线（每100像素）
        for y in range(0, height, 100):
            pygame.draw.line(screen, (0, 255, 0), (0, y), (width, y), 1)
            # 标注坐标
            text = font.render(str(y), True, (0, 255, 0))
            screen.blit(text, (2, y + 2))

    def _draw_battle_areas_bounds(self, screen, font):
        """绘制战斗区域边界框"""
        import pygame
        
        areas = [
            ("玩家手牌", self.game_board.player_hand, (255, 255, 0)),
            ("玩家前排", self.game_board.player_active, (255, 0, 0)),
            ("玩家后备1", self.game_board.player_bench1, (255, 100, 100)),
            ("玩家后备2", self.game_board.player_bench2, (255, 100, 100)),
            ("玩家后备3", self.game_board.player_bench3, (255, 100, 100)),
            ("玩家后备4", self.game_board.player_bench4, (255, 100, 100)),
            ("玩家后备5", self.game_board.player_bench5, (255, 100, 100)),
            ("玩家卡组", self.game_board.player_deck, (0, 255, 255)),
            ("对手手牌", self.game_board.opponent_hand, (255, 255, 0)),
            ("对手前排", self.game_board.opponent_active, (255, 0, 0)),
            ("对手后备1", self.game_board.opponent_bench1, (255, 100, 100)),
            ("对手后备2", self.game_board.opponent_bench2, (255, 100, 100)),
            ("对手后备3", self.game_board.opponent_bench3, (255, 100, 100)),
            ("对手后备4", self.game_board.opponent_bench4, (255, 100, 100)),
            ("对手后备5", self.game_board.opponent_bench5, (255, 100, 100)),
            ("对手卡组", self.game_board.opponent_deck, (0, 255, 255)),
        ]
        
        for name, cardset, color in areas:
            if hasattr(cardset, 'rect'):
                rect = cardset.rect
                # 绘制边界框
                pygame.draw.rect(screen, color, rect, 2)
                # 显示区域信息
                info_text = f"{name}: ({rect.x},{rect.y}) {rect.width}x{rect.height}"
                text_surface = font.render(info_text, True, color)
                screen.blit(text_surface, (rect.x, rect.y - 25))

    def _draw_cards_info(self, screen, font):
        """绘制卡牌详细信息"""
        import pygame
        
        y_offset = 10
        
        # 获取所有区域的卡牌
        all_areas = [
            ("玩家手牌", self.game_board.player_hand),
            ("玩家前排", self.game_board.player_active),
            ("对手前排", self.game_board.opponent_active),
        ]
        
        for area_name, cardset in all_areas:
            if len(cardset) > 0:
                for i, card in enumerate(cardset):
                    if hasattr(card, 'rect'):
                        # 绘制卡牌边界
                        pygame.draw.rect(screen, (255, 255, 255), card.rect, 1)
                        
                        # 显示卡牌信息
                        card_info = f"{area_name}[{i}]: {card.name} ({card.rect.x},{card.rect.y}) {card.rect.width}x{card.rect.height}"
                        text_surface = font.render(card_info, True, (255, 255, 255))
                        screen.blit(text_surface, (10, y_offset))
                        y_offset += 20

    def _draw_mouse_info(self, screen, font):
        """显示鼠标信息"""
        import pygame
        
        mouse_text = f"鼠标: ({self.mouse_pos[0]}, {self.mouse_pos[1]})"
        
        # 检测鼠标在哪个区域
        current_area = "无"
        areas = [
            ("玩家手牌", self.game_board.player_hand),
            ("玩家前排", self.game_board.player_active),
            ("对手前排", self.game_board.opponent_active),
            ("玩家卡组", self.game_board.player_deck),
            ("对手卡组", self.game_board.opponent_deck),
        ]
        
        for name, cardset in areas:
            if hasattr(cardset, 'rect') and cardset.rect.collidepoint(self.mouse_pos):
                current_area = name
                break
        
        area_text = f"当前区域: {current_area}"
        
        # 显示信息
        mouse_surface = font.render(mouse_text, True, (255, 255, 0))
        area_surface = font.render(area_text, True, (255, 255, 0))
        
        screen.blit(mouse_surface, (screen.get_width() - 250, 10))
        screen.blit(area_surface, (screen.get_width() - 250, 35))

    def _draw_layout_info(self, screen, font):
        """显示总体布局信息"""
        import pygame
        
        layout_info = [
            f"屏幕尺寸: {screen.get_width()} x {screen.get_height()}",
            f"战斗界面: {self.screen_width} x {self.screen_height}",
            f"调试模式: {self.debug_mode} (按D切换)",
            f"标尺显示: {self.show_ruler} (按R切换)",
            "",
            "操作说明:",
            "D - 切换调试模式",
            "R - 切换标尺显示",
            "鼠标移动查看区域信息"
        ]
        
        y_start = screen.get_height() - len(layout_info) * 25 - 10
        
        for i, info in enumerate(layout_info):
            text_surface = font.render(info, True, (255, 255, 255))
            screen.blit(text_surface, (10, y_start + i * 25))

    def handle_debug_keys(self, event):
        """处理调试按键"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                self.toggle_debug_mode()
            elif event.key == pygame.K_r:
                self.toggle_ruler()

    def _wait_for_battle_ready(self):
        """等待战斗控制器准备完成"""
        if not self.battle_controller or not self.battle_controller.current_battle:
            print("⚠️ 战斗控制器未准备完成，使用默认设置")
            return
        
        battle_manager = self.battle_controller.current_battle
        
        # 如果战斗已经开始但还在初始阶段，暂停一下让数据稳定
        if hasattr(battle_manager.battle_state, 'turn_count') and battle_manager.battle_state.turn_count <= 1:
            print("🛑 等待战斗状态稳定...")
            import time
            time.sleep(0.1)  # 短暂等待
    
    def _load_background(self):
        """加载背景图片"""
        try:
            bg_path = os.path.join("assets", "images", "backgrounds", "battle_bg.png")
            if os.path.exists(bg_path):
                self.background_image = pygame.image.load(bg_path)
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
            card_spacing=0.02,
            size=(int(self.game_board.game_area_width * 0.6), int(self.screen_height * 0.15))
        )
        
        # 对手手牌 - 显示卡背
        self.game_board.opponent_hand.graphics = FixedDeck(
            self.game_board.opponent_hand,
            visible=False,
            card_back="assets/images/item/card_back.png",
            size=(int(self.game_board.game_area_width * 0.6), int(self.screen_height * 0.15))
        )
        
        # 卡组 - 使用修复的卡背
        self.game_board.player_deck.graphics = FixedDeck(
            self.game_board.player_deck,
            visible=False,
            card_back="assets/images/item/card_back.png",
            size=(90, 126)
        )
        
        self.game_board.opponent_deck.graphics = FixedDeck(
            self.game_board.opponent_deck,
            visible=False,
            card_back="assets/images/item/card_back.png",
            size=(90, 126)
        )
        
        # 弃牌堆
        self.game_board.player_discard.graphics = VerticalPileGraphic(
            self.game_board.player_discard,
            size=(90, 126)
        )
        
        self.game_board.opponent_discard.graphics = VerticalPileGraphic(
            self.game_board.opponent_discard,
            size=(90, 126)
        )
        
        # 战斗位
        self.game_board.player_active.graphics = FixedPokemonFieldGraphic(
            self.game_board.player_active,
            title="Activo",
            is_enemy=False
        )
        
        self.game_board.opponent_active.graphics = FixedPokemonFieldGraphic(
            self.game_board.opponent_active,
            title="Activo Enemigo",
            is_enemy=True
        )
        
        # 我方备战区
        self.game_board.player_bench_1.graphics = FixedPokemonFieldGraphic(
            self.game_board.player_bench_1,
            title="Banca 1",
            is_enemy=False
        )
        
        self.game_board.player_bench_2.graphics = FixedPokemonFieldGraphic(
            self.game_board.player_bench_2,
            title="Banca 2",
            is_enemy=False
        )
        
        self.game_board.player_bench_3.graphics = FixedPokemonFieldGraphic(
            self.game_board.player_bench_3,
            title="Banca 3",
            is_enemy=False
        )
        
        # 对手备战区
        self.game_board.opponent_bench_1.graphics = FixedPokemonFieldGraphic(
            self.game_board.opponent_bench_1,
            title="Banca Enemiga 1",
            is_enemy=True
        )
        
        self.game_board.opponent_bench_2.graphics = FixedPokemonFieldGraphic(
            self.game_board.opponent_bench_2,
            title="Banca Enemiga 2",
            is_enemy=True
        )
        
        self.game_board.opponent_bench_3.graphics = FixedPokemonFieldGraphic(
            self.game_board.opponent_bench_3,
            title="Banca Enemiga 3",
            is_enemy=True
        )
    
    def _setup_cards_manager(self):
        """设置卡牌管理器"""
        board_graphics = self.game_board.graphics
        
        # 我方手牌 - 可拖拽出去，可点击
        self.cards_manager.add_set(
            self.game_board.player_hand.graphics,
            board_graphics.cardsets_rel_pos[self.game_board.player_hand],
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
        
        # 对手区域 - 只能查看
        opponent_areas = [
            self.game_board.opponent_hand,
            self.game_board.opponent_active,
            self.game_board.opponent_bench_1,
            self.game_board.opponent_bench_2,
            self.game_board.opponent_bench_3,
            self.game_board.opponent_deck,
            self.game_board.opponent_discard
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
        
        # 我方卡组和弃牌区 - 只能点击
        utility_areas = [self.game_board.player_deck]
        
        for utility_area in utility_areas:
            self.cards_manager.add_set(
                utility_area.graphics,
                board_graphics.cardsets_rel_pos[utility_area],
                CardSetRights(
                    clickable=True,
                    draggable_out=False,
                    draggable_in=False,
                    highlight_hovered_card=False
                )
            )
    
    # ======================================
    # 🔥 核心修复：数据获取机制
    # ======================================
    
    def _get_real_player_data(self):
        """🔥 获取真实玩家数据，而不是状态字典"""
        try:
            battle_manager = None
            
            # 🔥 修复：支持同步控制器架构
            if (hasattr(self.battle_controller, '_sync_controller') and 
                self.battle_controller._sync_controller and
                hasattr(self.battle_controller._sync_controller, 'current_battle') and
                self.battle_controller._sync_controller.current_battle):
                
                battle_manager = self.battle_controller._sync_controller.current_battle
                print(f"✅ [修复] 通过同步控制器找到战斗管理器: {type(battle_manager)}")
                
            # 回退：检查直接路径
            elif (self.battle_controller and 
                hasattr(self.battle_controller, 'current_battle') and
                self.battle_controller.current_battle):
                
                battle_manager = self.battle_controller.current_battle
                print(f"✅ [修复] 通过直接路径找到战斗管理器: {type(battle_manager)}")
            
            if battle_manager:
                player_state = battle_manager.get_player_state(1)  # 玩家ID=1
                
                if player_state:
                    print(f"✅ [修复] 获取真实玩家数据成功")
                    print(f"   手牌数量: {len(player_state.hand) if hasattr(player_state, 'hand') and player_state.hand else 0}")
                    print(f"   前排Pokemon: {'是' if player_state.active_pokemon else '否'}")
                    print(f"   后备Pokemon数量: {len(player_state.bench_pokemon) if hasattr(player_state, 'bench_pokemon') and player_state.bench_pokemon else 0}")
                    return player_state
                else:
                    print("❌ [修复] 获取玩家状态为空")
            else:
                print("❌ [修复] 未找到战斗管理器")
                print(f"   battle_controller类型: {type(self.battle_controller)}")
                print(f"   有_sync_controller: {hasattr(self.battle_controller, '_sync_controller')}")
                print(f"   有current_battle: {hasattr(self.battle_controller, 'current_battle')}")
                        
        except Exception as e:
            print(f"❌ [修复] 获取真实玩家数据失败: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def _get_real_opponent_data(self):
        """🔥 获取真实对手数据"""
        try:
            battle_manager = None
            
            # 🔥 修复：支持同步控制器架构
            if (hasattr(self.battle_controller, '_sync_controller') and 
                self.battle_controller._sync_controller and
                hasattr(self.battle_controller._sync_controller, 'current_battle') and
                self.battle_controller._sync_controller.current_battle):
                
                battle_manager = self.battle_controller._sync_controller.current_battle
                
            # 回退：检查直接路径
            elif (self.battle_controller and 
                hasattr(self.battle_controller, 'current_battle') and
                self.battle_controller.current_battle):
                
                battle_manager = self.battle_controller.current_battle
            
            if battle_manager:
                opponent_state = battle_manager.get_player_state(999)  # AI玩家ID=999
                
                if opponent_state:
                    print(f"✅ [修复] 获取真实对手数据成功")
                    print(f"   手牌数量: {len(opponent_state.hand) if hasattr(opponent_state, 'hand') and opponent_state.hand else 0}")
                    print(f"   前排Pokemon: {'是' if opponent_state.active_pokemon else '否'}")
                    return opponent_state
                        
        except Exception as e:
            print(f"❌ [修复] 获取真实对手数据失败: {e}")
        
        return None
    
    def _create_real_card_adapter(self, card_instance, area_name="Unknown"):
        """🔥 创建真实卡牌适配器，而不是占位符"""
        try:
            if card_instance is None:
                print(f"⚠️ [修复] card_instance为None，无法创建适配器 ({area_name})")
                return None

            # 检查card_instance的结构
            if hasattr(card_instance, 'card'):
                # 如果是带有.card属性的实例（如CardInstance）
                card_data = card_instance.card
                instance_id = getattr(card_instance, 'instance_id', f'unknown_{area_name}')
            else:
                # 如果直接是Card对象
                card_data = card_instance
                instance_id = f'card_{area_name}'
            
            # 创建适配器
            adapter = PokemonCardAdapter(card_data, instance_id)
            
            print(f"✅ [修复] 创建真实卡牌适配器: {card_data.name} (ID: {instance_id})")
            return adapter
            
        except Exception as e:
            print(f"❌ [修复] 创建真实卡牌适配器失败: {e}")
            # 回退到占位符
            return self._create_fallback_placeholder(card_instance, area_name)
    
    def _create_fallback_placeholder(self, card_instance, area_name):
        """创建回退占位符"""
        try:
            from game.core.cards.card_data import Card
            
            # 尝试提取卡牌名称
            card_name = "Unknown Card"
            if hasattr(card_instance, 'card') and hasattr(card_instance.card, 'name'):
                card_name = card_instance.card.name
            elif hasattr(card_instance, 'name'):
                card_name = card_instance.name
            
            placeholder_card = Card(
                id=f"placeholder_{area_name}",
                name=card_name,
                rarity="Common",
                types=[]
            )
            
            adapter = PokemonCardAdapter(placeholder_card)
            print(f"⚠️ [修复] 创建回退占位符: {card_name}")
            return adapter
            
        except Exception as e:
            print(f"❌ [修复] 创建回退占位符也失败: {e}")
            return None
    
    def _update_battle_state(self):
        """🔥 修复：更新战斗状态 - 使用真实数据"""
        try:
            print(f"🔍 [调试] 开始更新战斗状态，当前线程: {threading.current_thread().name if 'threading' in globals() else 'unknown'}")
            if not self.battle_controller:
                print("⚠️ [修复] 战斗控制器为None")
                return
            
            print("🔄 [修复] 开始更新战斗状态...")
            
            # 🔥 使用新的数据获取方式
            player_state = self._get_real_player_data()
            opponent_state = self._get_real_opponent_data()
            
            if player_state:
                print("🔥 [修复] 处理玩家真实数据...")
                
                # 🔥 更新手牌 - 使用真实卡牌数据
                if hasattr(player_state, 'hand') and player_state.hand:
                    print(f"🃏 [修复] 更新玩家手牌: {len(player_state.hand)} 张真实卡牌")
                    self._update_real_hand_cards(player_state.hand)
                else:
                    print("⚠️ [修复] 玩家手牌数据为空")
                    self.game_board.player_hand.clear()
                
                # 🔥 更新前排Pokemon - 使用真实数据
                if player_state.active_pokemon:
                    print(f"🎯 [修复] 更新玩家前排Pokemon: {player_state.active_pokemon.card.name if hasattr(player_state.active_pokemon, 'card') else '未知'}")
                    self._update_real_pokemon_area(self.game_board.player_active, [player_state.active_pokemon], "player_active")
                else:
                    self.game_board.player_active.clear()
                
                # 🔥 更新后备区Pokemon - 使用真实数据
                if hasattr(player_state, 'bench_pokemon') and player_state.bench_pokemon:
                    print(f"🏟️ [修复] 更新玩家后备区: {len(player_state.bench_pokemon)} 只Pokemon")
                    self._update_real_bench_pokemon(player_state.bench_pokemon)
                else:
                    self._clear_bench_areas()
                
                # 🔧 修复：使用新的卡组显示方法
                if hasattr(player_state, 'deck'):
                    deck_size = len(player_state.deck)
                    print(f"🃏 [修复] 更新玩家卡组显示: {deck_size} 张")
                    self._update_deck_display(self.game_board.player_deck, deck_size)
            
            if opponent_state:
                print("🔥 [修复] 处理对手真实数据...")
                
                # 🔧 修复：使用简化的对手手牌显示
                if hasattr(opponent_state, 'hand') and opponent_state.hand:
                    hand_size = len(opponent_state.hand)
                    print(f"🃏 [修复] 对手手牌: {hand_size} 张 (显示为卡背)")
                    self._update_opponent_hand_backs(hand_size)
                
                # 对手前排Pokemon
                if opponent_state.active_pokemon:
                    print(f"🎯 [修复] 更新对手前排Pokemon: {opponent_state.active_pokemon.card.name if hasattr(opponent_state.active_pokemon, 'card') else '未知'}")
                    self._update_real_pokemon_area(self.game_board.opponent_active, [opponent_state.active_pokemon], "opponent_active")
                else:
                    self.game_board.opponent_active.clear()
                
                # 对手后备区
                if hasattr(opponent_state, 'bench_pokemon') and opponent_state.bench_pokemon:
                    print(f"🏟️ [修复] 更新对手后备区: {len(opponent_state.bench_pokemon)} 只Pokemon")
                    self._update_real_opponent_bench(opponent_state.bench_pokemon)
                else:
                    self._clear_opponent_bench_areas()
                
                # 🔧 修复：使用新的对手卡组显示方法
                if hasattr(opponent_state, 'deck'):
                    deck_size = len(opponent_state.deck)
                    print(f"🃏 [修复] 更新对手卡组显示: {deck_size} 张")
                    self._update_deck_display(self.game_board.opponent_deck, deck_size)
            
            print("✅ [修复] 战斗状态更新完成")
            
        except Exception as e:
            print(f"❌ [修复] 更新战斗状态失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_real_hand_cards(self, hand_cards):
        """🔥 更新真实手牌卡牌"""
        try:
            self.game_board.player_hand.clear()
            
            valid_hand_cards = [card for card in hand_cards if card is not None]

            for i, card_instance in enumerate(valid_hand_cards[:7]):  # 最多显示7张
                adapter = self._create_real_card_adapter(card_instance, f"hand_{i+1}")
                if adapter is not None:
                    self.game_board.player_hand.append(adapter)
                else:
                    print(f"⚠️ [修复] 第{i+1}张手牌适配器创建失败，跳过")
                    
            print(f"✅ [修复] 手牌更新完成: {len(self.game_board.player_hand)} 张")
            
        except Exception as e:
            print(f"❌ [修复] 更新真实手牌失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_real_pokemon_area(self, cardset, pokemon_list, area_name):
        """🔥 更新真实Pokemon区域"""
        try:
            if cardset and hasattr(cardset, 'clear'):
                try:
                    cardset.clear()
                except Exception as e:
                    print(f"⚠️ [修复] 清理卡牌区域时出错: {e}")
            
            valid_pokemon = [pokemon for pokemon in pokemon_list if pokemon is not None]

            for pokemon_instance in valid_pokemon:
                if pokemon_instance:
                    adapter = self._create_real_card_adapter(pokemon_instance, area_name)
                if adapter is not None:
                    cardset.append(adapter)
                else:
                    print(f"⚠️ [修复] {area_name}适配器创建失败，跳过")
                        
            print(f"✅ [修复] {area_name}更新完成: {len(cardset)} 只Pokemon")
            
        except Exception as e:
            print(f"❌ [修复] 更新{area_name}失败: {e}")
    
    def _update_real_bench_pokemon(self, bench_pokemon):
        """🔥 更新真实后备区Pokemon"""
        bench_pokemon = [pokemon for pokemon in bench_pokemon if pokemon is not None]

        bench_areas = [
            self.game_board.player_bench_1,
            self.game_board.player_bench_2,
            self.game_board.player_bench_3
        ]
        
        # 清空所有后备区
        for bench_area in bench_areas:
            bench_area.clear()
        
        # 分配Pokemon到后备区槽位
        for i, pokemon_instance in enumerate(bench_pokemon[:3]):  # 最多3只
            if i < len(bench_areas) and pokemon_instance:
                adapter = self._create_real_card_adapter(pokemon_instance, f"player_bench_{i+1}")
                if adapter:
                    bench_areas[i].append(adapter)
                    print(f"✅ [修复] 后备区{i+1}更新: {pokemon_instance.card.name if hasattr(pokemon_instance, 'card') else '未知Pokemon'}")
    
    def _update_real_opponent_bench(self, bench_pokemon):
        """🔥 更新真实对手后备区"""
        bench_areas = [
            self.game_board.opponent_bench_1,
            self.game_board.opponent_bench_2,
            self.game_board.opponent_bench_3
        ]
        
        # 清空所有对手后备区
        for bench_area in bench_areas:
            bench_area.clear()
        
        # 分配对手Pokemon到后备区槽位
        for i, pokemon_instance in enumerate(bench_pokemon[:3]):  # 最多3只
            if i < len(bench_areas) and pokemon_instance:
                adapter = self._create_real_card_adapter(pokemon_instance, f"opponent_bench_{i+1}")
                if adapter:
                    bench_areas[i].append(adapter)
                    print(f"✅ [修复] 对手后备区{i+1}更新: {pokemon_instance.card.name if hasattr(pokemon_instance, 'card') else '未知Pokemon'}")

    def _update_deck_display(self, cardset: CardsSet, card_count: int):
        """更新卡组显示（显示卡背）"""
        try:
            # 清空现有卡组
            if cardset and hasattr(cardset, 'clear'):
                try:
                    cardset.clear()
                except Exception as e:
                    print(f"⚠️ [修复] 清理卡牌区域时出错: {e}")
            
            # 创建虚拟卡背来表示卡组
            if card_count > 0:
                from game.core.cards.card_data import Card
                dummy_card = Card(
                    id="card_back",
                    name="Card Back",
                    rarity="Common",
                    types=[]
                )
                
                # 只添加一张卡牌来表示整个卡组
                adapter = PokemonCardAdapter(dummy_card, "deck_back")
                cardset.append(adapter)
        except Exception as e:
            print(f"❌ 更新卡组显示失败: {e}")
    
    def _update_opponent_hand_backs(self, hand_count):
        """🔥 更新对手手牌卡背显示 - 使用数量渲染避免ID冲突"""
        try:
            self.game_board.opponent_hand.clear()
            
            if hand_count > 0:
                from game.core.cards.card_data import Card
                # 创建一个卡背对象
                card_back = Card(
                    id="opponent_card_back", 
                    name="Card Back", 
                    rarity="Common", 
                    types=[]
                )
                adapter = PokemonCardAdapter(card_back, "opponent_hand_back")
                
                # 根据数量添加多次（同一个对象，避免ID冲突）
                for _ in range(min(hand_count, 7)):  # 最多显示7张
                    self.game_board.opponent_hand.append(adapter)
                    
                print(f"✅ [修复] 对手手牌卡背更新: {len(self.game_board.opponent_hand)} 张")
                
        except Exception as e:
            print(f"❌ [修复] 更新对手手牌卡背失败: {e}")
    
    def _clear_bench_areas(self):
        """清空玩家后备区"""
        bench_areas = [
            self.game_board.player_bench_1,
            self.game_board.player_bench_2,
            self.game_board.player_bench_3
        ]
        
        for bench_area in bench_areas:
            bench_area.clear()
    
    def _clear_opponent_bench_areas(self):
        """清空对手后备区"""
        bench_areas = [
            self.game_board.opponent_bench_1,
            self.game_board.opponent_bench_2,
            self.game_board.opponent_bench_3
        ]
        
        for bench_area in bench_areas:
            bench_area.clear()
    
    # ======================================
    # 保留原有的setup_from_battle_state方法作为备用
    # ======================================
    
    def setup_from_battle_state(self, battle_state):
        """
        Configura la interfaz según el estado de batalla proporcionado.
        🔥 修复版：优先使用真实数据，备用字典数据
        """
        print(f"🔍 [修复] setup_from_battle_state接收到:")
        print(f"   参数类型: {type(battle_state)}")
        
        # 🔥 优先尝试获取真实数据
        player_state = self._get_real_player_data()
        opponent_state = self._get_real_opponent_data()
        
        if player_state or opponent_state:
            print("✅ [修复] 使用真实数据更新界面")
            # 真实数据已经在_update_battle_state中处理了
            return
        
        # 🔄 回退：如果无法获取真实数据，使用字典数据
        print("⚠️ [修复] 回退到字典数据处理")
        
        if not isinstance(battle_state, dict):
            print("❌ battle_state不是字典格式且无法获取真实数据")
            return
        
        # 从字典中提取玩家状态
        player_data = battle_state.get('player', {})
        opponent_data = battle_state.get('opponent', {})
        
        print(f"🔍 [修复] 字典数据 - 玩家: {player_data}")
        print(f"🔍 [修复] 字典数据 - 对手: {opponent_data}")
        
        # 清理所有卡牌区域
        self._clear_all_cardsets()
        
        try:
            # 根据字典数据填充界面
            self._populate_from_dict_data(player_data, opponent_data)
            print("✅ [修复] 字典数据填充完成")
            
        except Exception as e:
            print(f"❌ [修复] 填充界面数据失败: {e}")
            import traceback
            traceback.print_exc()

    def _clear_all_cardsets(self):
        """清理所有卡牌区域"""
        if not hasattr(self, 'game_board'):
            print("⚠️ game_board 未初始化")
            return
        
        cardsets_to_clear = []
        
        # 安全地获取所有卡牌区域
        cardset_names = [
            'player_hand', 'player_active', 'player_bench_1', 'player_bench_2', 'player_bench_3',
            'player_deck', 'player_discard', 'opponent_hand', 'opponent_active', 
            'opponent_bench_1', 'opponent_bench_2', 'opponent_bench_3', 
            'opponent_deck', 'opponent_discard'
        ]
        
        for name in cardset_names:
            if hasattr(self.game_board, name):
                cardset = getattr(self.game_board, name)
                if cardset and hasattr(cardset, 'clear'):
                    cardsets_to_clear.append(cardset)
        
        # 清理卡牌区域
        for cardset in cardsets_to_clear:
            try:
                if cardset and hasattr(cardset, 'clear'):
                    try:
                        cardset.clear()
                    except Exception as e:
                        print(f"⚠️ [修复] 清理卡牌区域时出错: {e}")
            except Exception as e:
                print(f"❌ 清理卡牌区域失败: {e}")
        
        print("✅ 卡牌区域清理完成")

    def _populate_from_dict_data(self, player_data, opponent_data):
        """根据字典数据填充界面（回退方案）"""
        
        # 处理玩家前排Pokemon
        if player_data.get('active_pokemon'):
            active_info = player_data['active_pokemon']
            print(f"🔍 设置玩家前排: {active_info}")
            if hasattr(self.game_board, 'player_active'):
                self._create_placeholder_card(self.game_board.player_active, active_info)
        
        # 处理对手前排Pokemon
        if opponent_data.get('active_pokemon'):
            active_info = opponent_data['active_pokemon']
            print(f"🔍 设置对手前排: {active_info}")
            if hasattr(self.game_board, 'opponent_active'):
                self._create_placeholder_card(self.game_board.opponent_active, active_info)
        
        # 🔧 修复：恢复手牌显示逻辑
        print(f"🃏 [修复] 处理玩家手牌...")
        player_hand_size = player_data.get('hand_size', 0)
        print(f"🔍 玩家手牌数量: {player_hand_size}")

        if player_hand_size > 0 and hasattr(self.game_board, 'player_hand'):
            # 创建手牌显示
            for i in range(min(player_hand_size, 7)):  # 最多7张
                card_info = {'name': f'Hand Card {i+1}', 'instance_id': f'hand_{i+1}'}
                self._create_placeholder_card(self.game_board.player_hand, card_info)
                print(f"✅ 创建占位手牌 {i+1}")
        
        # 修复：处理对手手牌（显示多张卡背）
        opponent_hand_size = opponent_data.get('hand_size', 0)
        print(f"🔍 对手手牌数量: {opponent_hand_size}")
        if opponent_hand_size > 0 and hasattr(self.game_board, 'opponent_hand'):
            for i in range(min(opponent_hand_size, 7)):  # 最多显示7张
                card_info = {'name': 'Card Back', 'instance_id': f'opponent_hand_{i+1}'}
                self._create_placeholder_card(self.game_board.opponent_hand, card_info)
                print(f"✅ 创建对手手牌卡背 {i+1}")
        
        # 处理卡组显示
        player_deck_size = player_data.get('deck_size', 0)
        if player_deck_size > 0 and hasattr(self.game_board, 'player_deck'):
            self._update_deck_display(self.game_board.player_deck, player_deck_size)
            print(f"✅ 创建玩家卡组显示 (剩余 {player_deck_size} 张)")

        opponent_deck_size = opponent_data.get('deck_size', 0)
        if opponent_deck_size > 0 and hasattr(self.game_board, 'opponent_deck'):
            self._update_deck_display(self.game_board.opponent_deck, opponent_deck_size)
            print(f"✅ 创建对手卡组显示 (剩余 {opponent_deck_size} 张)")
        
        # 统计结果
        stats = []
        if hasattr(self.game_board, 'player_hand'):
            stats.append(f"玩家手牌: {len(self.game_board.player_hand)} 张")
        if hasattr(self.game_board, 'opponent_hand'):
            stats.append(f"对手手牌: {len(self.game_board.opponent_hand)} 张")
        if hasattr(self.game_board, 'player_active'):
            stats.append(f"玩家前排: {len(self.game_board.player_active)} 张")
        if hasattr(self.game_board, 'opponent_active'):
            stats.append(f"对手前排: {len(self.game_board.opponent_active)} 张")
        
        print(f"✅ 界面数据填充完成:")
        for stat in stats:
            print(f"   {stat}")

    def _extract_card_id_from_instance(self, instance_id):
        """从instance_id中提取原始card_id"""
        # instance_id格式: "1_xy4-1_17" -> card_id: "xy4-1"
        if isinstance(instance_id, str) and '_' in instance_id:
            parts = instance_id.split('_')
            if len(parts) >= 3:
                # 移除第一个部分(player_id)和最后一个部分(instance_number)
                card_id = '_'.join(parts[1:-1])
                print(f"🔍 提取card_id: {instance_id} -> {card_id}")
                return card_id
        
        # 如果无法提取，返回原始值
        print(f"⚠️ 无法提取card_id，使用原始值: {instance_id}")
        return instance_id

    def _create_placeholder_card(self, cardset, card_info):
        """创建占位卡牌"""
        try:
            from game.core.cards.card_data import Card
            from .pokemon_card_adapter import PokemonCardAdapter
            
            # 修复：提取正确的card_id
            instance_id = card_info.get('instance_id', 'placeholder')
            if instance_id != 'placeholder':
                card_id = self._extract_card_id_from_instance(instance_id)
            else:
                card_id = 'placeholder'
            
            # 创建简单的占位卡牌
            placeholder_card = Card(
                id=card_id,  # 使用提取的card_id
                name=card_info.get('name', 'Unknown'),
                rarity="Common",
                types=[]
            )
            
            adapter = PokemonCardAdapter(placeholder_card)
            cardset.append(adapter)
            
            print(f"✅ 创建占位卡牌: {card_info.get('name', 'Unknown')} (ID: {card_id})")
            
        except Exception as e:
            print(f"❌ 创建占位卡牌失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _safe_update_cardset(self, cardset: CardsSet, cards_data, name: str):
        """安全地更新卡牌集合"""
        try:
            if not cards_data:
                if cardset and hasattr(cardset, 'clear'):
                    try:
                        cardset.clear()
                    except Exception as e:
                        print(f"⚠️ [修复] 清理卡牌区域时出错: {e}")
                return
            
            valid_cards = [card for card in cards_data if card is not None]
            
            if valid_cards:
                new_cardset = convert_to_pokemon_cardsset(valid_cards, name)
                self._update_cardset(cardset, new_cardset)
            else:
                if cardset and hasattr(cardset, 'clear'):
                    try:
                        cardset.clear()
                    except Exception as e:
                        print(f"⚠️ [修复] 清理卡牌区域时出错: {e}")
                
        except Exception as e:
            print(f"❌ 安全更新卡牌集合失败 {name}: {e}")
            if cardset and hasattr(cardset, 'clear'):
                try:
                    cardset.clear()
                except Exception as e:
                    print(f"⚠️ [修复] 清理卡牌区域时出错: {e}")
    
    def _update_deck_display(self, cardset: CardsSet, card_count: int):
        """更新卡组显示（显示卡背）"""
        try:
            # 清空现有卡组
            if cardset and hasattr(cardset, 'clear'):
                try:
                    cardset.clear()
                except Exception as e:
                    print(f"⚠️ [修复] 清理卡牌区域时出错: {e}")
            
            # 创建虚拟卡背来表示卡组
            if card_count > 0:
                # 创建一个简单的卡背表示
                from game.core.cards.card_data import Card
                dummy_card = Card(
                    id="card_back",
                    name="Card Back",
                    rarity="Common",
                    types=[]
                )
                
                # 只添加一张卡牌来表示整个卡组
                adapter = PokemonCardAdapter(dummy_card, "deck_back")
                cardset.append(adapter)
        except Exception as e:
            print(f"❌ 更新卡组显示失败: {e}")
    
    def _update_cardset(self, old_cardset: CardsSet, new_cardset: CardsSet):
        """更新卡牌集合"""
        old_cardset.clear()
        old_cardset.extend(new_cardset)
        
        if hasattr(old_cardset, 'graphics'):
            old_cardset.graphics.clear_cache()
    
    def handle_event(self, event) -> Optional[str]:
        """处理事件"""
        # ESC键返回
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("🔙 ESC键按下，返回战斗页面")
                return "back_to_battle_page"
        
        # 处理控制面板点击
        if event.type == pygame.MOUSEBUTTONDOWN:
            if hasattr(self, 'control_panel') and self.control_panel:
                button_clicked = self.control_panel.handle_click(event.pos)
                if button_clicked:
                    self._handle_button_click(button_clicked)
                    return None
        
        # 🔍 处理调试按键 - 新增部分
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                self.debug_mode = not self.debug_mode
                print(f"🔍 调试模式: {'开启' if self.debug_mode else '关闭'}")
            elif event.key == pygame.K_r:
                self.show_ruler = not self.show_ruler
                print(f"📏 标尺显示: {'开启' if self.show_ruler else '关闭'}")

        # 只处理卡牌管理器事件
        if hasattr(self, 'cards_manager') and self.cards_manager:
            self.cards_manager.process_events(event)
        
        # 处理卡牌事件
        try:
            # 尝试导入pygame_cards事件常量
            from pygame_cards.events import CARDSSET_CLICKED, CARD_MOVED
            
            if event.type == CARDSSET_CLICKED:
                self._handle_cardset_clicked(event)
            elif event.type == CARD_MOVED:
                self._handle_card_moved(event)
        except ImportError:
            # 如果无法导入事件常量，跳过
            pass
        
        return None
    
    def _handle_button_click(self, button_name):
        """处理按钮点击"""
        print(f"🎮 按钮点击: {button_name}")
        
        try:
            if button_name == "end_turn":
                self._end_turn()
            elif button_name == "forfeit":
                self._forfeit_battle()
            elif button_name == "draw_card":
                self._draw_card()
            elif button_name == "gain_energy":
                self._gain_energy()
            elif button_name == "attack":
                self._attack()
            elif button_name == "surrender":
                self._surrender()

        except Exception as e:
            print(f"❌ 处理按钮点击失败: {e}")
    
    def _handle_cardset_clicked(self, event):
        """处理卡牌集合点击事件"""
        print(f"🃏 卡牌集合点击1: {event}")
        cardset_graphic = event.set
        # 如果图形对象有 cardset 属性，则获取对应的 CardsSet，否则直接使用它
        actual_set = getattr(cardset_graphic, 'cardset', cardset_graphic)
        card = event.card
        print(f"🎯 卡牌集合点击2: {actual_set.name}")  # 使用 CardsSet 的名称
        if card:
            print(f"   点击卡牌: {card.name}")
    
    def _handle_card_moved(self, event):
        """Maneja el evento de mover una carta de un conjunto a otro."""
        print(f"🔄 卡牌移动: {event}")
        card_adapter = event.card       # PokemonCardAdapter movido
        from_set = event.from_set.cardset
        to_set = event.to_set.cardset
        print(f"🚚 Carta movida: {card_adapter.name}")
        print(f"   Desde: {from_set.name} -> Hasta: {to_set.name}")

        # Si no hay controlador de batalla, no hacer nada
        if not self.battle_controller:
            return

        try:
            # Si la carta proviene de la mano del jugador y es un Pokémon que se jugó a la zona activa o banca
            if from_set == self.game_board.player_hand and hasattr(card_adapter, "is_pokemon") and card_adapter.is_pokemon():
                if to_set in [self.game_board.player_active, self.game_board.player_bench_1, self.game_board.player_bench_2, self.game_board.player_bench_3]:
                    # Enviar acción de jugar Pokémon
                    action_data = {"type": "play_pokemon", "source_id": getattr(card_adapter, "instance_id", None)}
                    result = self.battle_controller.process_player_action(action_data)
                    print(f"▶️ Resultado de jugar Pokémon: {result}")
            # Si la carta es un Entrenador y se movió a la pila de descarte (usarla)
            if from_set == self.game_board.player_hand and hasattr(card_adapter, "is_trainer") and card_adapter.is_trainer():
                if to_set == self.game_board.player_discard:
                    # (En una versión completa, aquí se podría procesar la acción de entrenador)
                    print(f"▶️ Carta de Entrenador usada: {card_adapter.name}")
            # Actualizar estado visual después de la acción
            self._update_battle_state()
        except Exception as e:
            print(f"❌ Error al procesar movimiento de carta: {e}")
    
    def _end_turn(self):
        """结束回合"""
        print("⏭️ 结束回合")
        
        try:
            # 获取战斗控制器
            if hasattr(self, 'battle_controller') and self.battle_controller:
                # 发送结束回合动作
                action_data = {
                    "action_type": "end_turn",
                    "player_id": 1,  # 玩家ID
                    "timestamp": time.time()
                }
                
                result = self.battle_controller.process_player_action(action_data)
                
                if result.get("success"):
                    print("✅ 回合结束成功")
                    # 更新界面显示
                    self._refresh_battle_display()
                else:
                    print(f"❌ 结束回合失败: {result.get('error', '未知错误')}")
                    
            else:
                print("❌ 找不到战斗控制器")
                
        except Exception as e:
            print(f"❌ 结束回合异常: {e}")
            import traceback
            traceback.print_exc()

    def _forfeit_battle(self):
        """认输"""
        print("🏳️ 认输")
        
        try:
            # 获取战斗控制器
            if hasattr(self, 'battle_controller') and self.battle_controller:
                # 发送认输动作
                action_data = {
                    "action_type": "forfeit",
                    "player_id": 1,  # 玩家ID
                    "timestamp": time.time()
                }
                
                result = self.battle_controller.process_player_action(action_data)
                
                if result.get("success"):
                    print("✅ 认输成功，战斗结束")
                    # 返回到战斗页面
                    if hasattr(self, '_on_battle_ended'):
                        self._on_battle_ended({"result": "forfeit", "winner": "opponent"})
                    else:
                        # 直接返回
                        return "back_to_battle_page"
                else:
                    print(f"❌ 认输失败: {result.get('error', '未知错误')}")
                    
            else:
                print("❌ 找不到战斗控制器")
                
        except Exception as e:
            print(f"❌ 认输异常: {e}")
            import traceback
            traceback.print_exc()

    def _refresh_battle_display(self):
        """刷新战斗显示"""
        try:
            # 🔥 使用新的数据更新机制
            self._update_battle_state()
            print("✅ 界面刷新完成")
                    
        except Exception as e:
            print(f"❌ 刷新界面异常: {e}")

    def update(self, dt):
        """更新界面"""
        # 定期更新战斗状态
        self.last_update_time += dt
        if self.last_update_time > 1.0:  # 每0.5秒更新一次
            if not self._updating_state:  # 只在没有正在更新时才更新
                self._update_battle_state()
            self.last_update_time = 0
        
        # 更新卡牌管理器
        self.cards_manager.update(dt * 1000)  # 转换为毫秒
    
    def draw(self, screen):
        """绘制界面"""
        # 绘制背景
        if self.background_image:
            screen.blit(self.background_image, (0, 0))
        else:
            screen.fill((76, 175, 80))
        
        # 绘制标题
        title = "Batalla Pokémon TCG"
        title_surface = self.title_font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(centerx=self.game_board.game_area_width//2, y=10)
        screen.blit(title_surface, title_rect)
        
        # 绘制分隔线
        center_y = self.screen_height // 2
        pygame.draw.line(screen, (100, 100, 100), 
                        (50, center_y), (self.game_board.game_area_width-50, center_y), 2)
        
        # 标记玩家和对手区域
        player_label = self.info_font.render("JUGADOR", True, (100, 255, 100))
        screen.blit(player_label, (10, center_y + 10))
        
        opponent_label = self.info_font.render("OPONENTE", True, (255, 100, 100))
        screen.blit(opponent_label, (10, center_y - 30))
        
        # 绘制卡牌管理器
        self.cards_manager.draw(screen)
        
        # 绘制控制面板
        battle_manager = self.battle_controller.current_battle if self.battle_controller else None
        player_state = battle_manager.get_player_state(1) if battle_manager else None
        opponent_state = battle_manager.get_player_state(999) if battle_manager else None
        
        self.control_panel.draw(screen, self.battle_state, player_state, opponent_state)
        
        # 操作提示
        hint = "Arrastra las cartas para jugar | Haz clic en los botones para actuar | ESC para salir"
        hint_surface = self.small_font.render(hint, True, (150, 150, 150))
        hint_rect = hint_surface.get_rect(centerx=self.game_board.game_area_width//2, y=self.screen_height-20)
        screen.blit(hint_surface, hint_rect)

        if self.debug_mode:
            self.draw_debug_overlay(screen)
    
        pygame.display.flip()
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理修复版Pokemon TCG战斗界面")
        
        if hasattr(self.cards_manager, 'cleanup'):
            self.cards_manager.cleanup()
        
        if hasattr(self.game_board, 'cleanup'):
            self.game_board.cleanup()