# ==== fixed_battle_interface.py ====
# 保存为: game/ui/battle/battle_interface/battle_interface.py

"""
修复后的Pokemon TCG战斗界面
解决时序、显示和交互问题
"""

import pygame
import os
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
        Pobla las zonas de CardsManager a partir del estado de batalla dado.
        Crea adaptadores PokemonCardAdapter para cada carta y los asigna a sus zonas.
        """
        if not hasattr(self, "interface") or not getattr(self, "interface"):
            print("⚠️ PokemonCardsManager: no está vinculada a ninguna BattleInterface")
            return
        # Delegar en BattleInterface.setup_from_battle_state para la lógica de poblado
        try:
            self.interface.setup_from_battle_state(battle_state)
        except Exception as e:
            print(f"❌ Error al poblar desde estado: {e}")

class FixedPokemonFieldGraphic(VerticalPileGraphic):
    """修复的Pokemon场地图形类"""
    
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
            self.title_font = pygame.font.SysFont("arial", 16, bold=True)
            self.button_font = pygame.font.SysFont("arial", 14, bold=True)
            self.info_font = pygame.font.SysFont("arial", 12)
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
        """创建游戏板图形"""
        # 使用游戏区域宽度而不是全屏宽度
        cardsets_abs_pos = {
            # 对手区域（上方）
            self.opponent_hand: (int(0.05 * self.game_area_width), int(0.02 * self.screen_height)),
            self.opponent_deck: (int(0.05 * self.game_area_width), int(0.15 * self.screen_height)),
            self.opponent_bench_1: (int(0.2 * self.game_area_width), int(0.15 * self.screen_height)),
            self.opponent_bench_2: (int(0.32 * self.game_area_width), int(0.15 * self.screen_height)),
            self.opponent_bench_3: (int(0.44 * self.game_area_width), int(0.15 * self.screen_height)),
            self.opponent_discard: (int(0.56 * self.game_area_width), int(0.15 * self.screen_height)),
            self.opponent_active: (int(0.38 * self.game_area_width), int(0.3 * self.screen_height)),
            
            # 我方区域（下方）
            self.player_active: (int(0.38 * self.game_area_width), int(0.5 * self.screen_height)),
            self.player_discard: (int(0.05 * self.game_area_width), int(0.65 * self.screen_height)),
            self.player_bench_1: (int(0.15 * self.game_area_width), int(0.65 * self.screen_height)),
            self.player_bench_2: (int(0.25 * self.game_area_width), int(0.65 * self.screen_height)),
            self.player_bench_3: (int(0.35 * self.game_area_width), int(0.65 * self.screen_height)),
            self.player_deck: (int(0.55 * self.game_area_width), int(0.65 * self.screen_height)),
            self.player_hand: (int(0.05 * self.game_area_width), int(0.82 * self.screen_height))
        }
        
        cardsets_abs_size = {
            # 手牌区域
            self.player_hand: (int(0.6 * self.game_area_width), int(0.15 * self.screen_height)),
            self.opponent_hand: (int(0.6 * self.game_area_width), int(0.1 * self.screen_height)),
            
            # 战斗位
            self.player_active: (int(0.14 * self.game_area_width), int(0.18 * self.screen_height)),
            self.opponent_active: (int(0.14 * self.game_area_width), int(0.18 * self.screen_height)),
            
            # 备战区
            self.player_bench_1: (int(0.08 * self.game_area_width), int(0.12 * self.screen_height)),
            self.player_bench_2: (int(0.08 * self.game_area_width), int(0.12 * self.screen_height)),
            self.player_bench_3: (int(0.08 * self.game_area_width), int(0.12 * self.screen_height)),
            
            self.opponent_bench_1: (int(0.1 * self.game_area_width), int(0.12 * self.screen_height)),
            self.opponent_bench_2: (int(0.1 * self.game_area_width), int(0.12 * self.screen_height)),
            self.opponent_bench_3: (int(0.1 * self.game_area_width), int(0.12 * self.screen_height)),
            
            # 卡组和弃牌堆
            self.player_deck: (int(0.08 * self.game_area_width), int(0.12 * self.screen_height)),
            self.player_discard: (int(0.08 * self.game_area_width), int(0.12 * self.screen_height)),
            self.opponent_deck: (int(0.08 * self.game_area_width), int(0.12 * self.screen_height)),
            self.opponent_discard: (int(0.08 * self.game_area_width), int(0.12 * self.screen_height))
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
            PokemonCardAdapter.set_battle_cache(self.battle_cache)
        
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
        
        # 立即更新初始状态
        self._update_battle_state()
        
        print("✅ 修复版Pokemon TCG战斗界面创建成功")
    
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
            size=(int(self.game_board.game_area_width * 0.6), int(self.screen_height * 0.1))
        )
        
        # 卡组 - 使用修复的卡背
        self.game_board.player_deck.graphics = FixedDeck(
            self.game_board.player_deck,
            visible=False,
            card_back="assets/images/item/card_back.png",
            size=(80, 120)
        )
        
        self.game_board.opponent_deck.graphics = FixedDeck(
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
    
    def _update_battle_state(self):
        """更新战斗状态"""
        try:
            if not self.battle_controller or not self.battle_controller.current_battle:
                return
            
            battle_manager = self.battle_controller.current_battle
            self.battle_state = battle_manager.battle_state
            
            player_state = battle_manager.get_player_state(1)  # 玩家ID=1
            ai_state = battle_manager.get_player_state(999)    # AI玩家ID=999
            
            if player_state:
                # 更新手牌
                self._safe_update_cardset(self.game_board.player_hand, player_state.hand, "Mano Jugador")
                
                # 更新前排Pokemon
                if player_state.active_pokemon:
                    self._safe_update_cardset(self.game_board.player_active, [player_state.active_pokemon], "Activo Jugador")
                else:
                    self.game_board.player_active.clear()
                
                # 更新后备区Pokemon
                bench_pokemon = player_state.bench_pokemon
                bench_areas = [
                    self.game_board.player_bench_1,
                    self.game_board.player_bench_2,
                    self.game_board.player_bench_3
                ]
                
                for i, bench_area in enumerate(bench_areas):
                    bench_area.clear()
                    if i < len(bench_pokemon) and bench_pokemon[i] is not None:
                        self._safe_update_cardset(bench_areas[i], [bench_pokemon[i]], f"Banca Jucador {i+1}")
                
                # 更新卡组显示（显示卡背）
                self._update_deck_display(self.game_board.player_deck, len(player_state.deck))
            
            if ai_state:
                # 更新AI手牌显示（显示卡背）
                self._update_deck_display(self.game_board.opponent_hand, len(ai_state.hand))
                
                # 更新AI前排
                if ai_state.active_pokemon:
                    self._safe_update_cardset(self.game_board.opponent_active, [ai_state.active_pokemon], "Activo Rival")
                else:
                    self.game_board.opponent_active.clear()
                
                # 更新AI后备区
                ai_bench_pokemon = ai_state.bench_pokemon
                ai_bench_areas = [
                    self.game_board.opponent_bench_1,
                    self.game_board.opponent_bench_2,
                    self.game_board.opponent_bench_3
                ]
                
                for i, bench_area in enumerate(ai_bench_areas):
                    bench_area.clear()
                    if i < len(ai_bench_pokemon) and ai_bench_pokemon[i] is not None:
                        self._safe_update_cardset(ai_bench_areas[i], [ai_bench_pokemon[i]], f"Banca Enemiga {i+1}")
                
                # 更新AI卡组显示
                self._update_deck_display(self.game_board.opponent_deck, len(ai_state.deck))
            
            # 更新控制面板
            self.control_panel.update_button_states(self.battle_state, player_state)

            # populate 管理
            self.cards_manager.populate_from_state(self.battle_state)
            
        except Exception as e:
            print(f"❌ 更新战斗状态失败: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_from_battle_state(self, battle_state):
        """
        Configura la interfaz según el estado de batalla proporcionado.
        Agrega las cartas correspondientes a cada zona visual.
        """
        # Obtener el gestor de batalla y estados de jugadores
        if hasattr(battle_state, "get_player_state"):
            battle_manager = battle_state
        elif hasattr(battle_state, "current_battle"):
            battle_manager = battle_state.current_battle
        else:
            print("⚠️ battle_state no contiene información de batalla válida")
            return

        player_state = battle_manager.get_player_state(1)
        opponent_state = battle_manager.get_player_state(999)

        # Limpiar todas las zonas antes de poblar
        # Mano del jugador
        self.game_board.player_hand.clear()
        if player_state and player_state.hand:
            # Convertir las cartas de la mano a adaptadores PokemonCardAdapter
            player_hand_cards = convert_to_pokemon_cardsset(player_state.hand, "Mano Jugador")
            self.game_board.player_hand.extend(player_hand_cards)
            if hasattr(self.game_board.player_hand, "graphics"):
                self.game_board.player_hand.graphics.clear_cache()

        # Zona Activa del jugador
        self.game_board.player_active.clear()
        if player_state and player_state.active_pokemon:
            active_cardset = convert_to_pokemon_cardsset([player_state.active_pokemon], "Activo Jugador")
            self.game_board.player_active.extend(active_cardset)
            if hasattr(self.game_board.player_active, "graphics"):
                self.game_board.player_active.graphics.clear_cache()

        # Zonas de Banca del jugador (hasta 3 Pokémon)
        bench_areas = [
            self.game_board.player_bench_1,
            self.game_board.player_bench_2,
            self.game_board.player_bench_3
        ]
        # Limpiar primero todas las bancas
        for area in bench_areas:
            area.clear()
        if player_state:
            bench_pokemon = player_state.bench_pokemon if hasattr(player_state, "bench_pokemon") else []
            for i, pokemon in enumerate(bench_pokemon[:3]):  # máx. 3 en banca
                if i < len(bench_areas) and pokemon is not None:
                    bench_slot_cardset = convert_to_pokemon_cardsset([pokemon], f"Banca Jucador {i+1}")
                    bench_areas[i].extend(bench_slot_cardset)
                    if hasattr(bench_areas[i], "graphics"):
                        bench_areas[i].graphics.clear_cache()

        # Pila de descarte del jugador
        self.game_board.player_discard.clear()
        if player_state and hasattr(player_state, "discard_pile"):
            discard_cards = player_state.discard_pile
        elif player_state and hasattr(player_state, "discard"):
            discard_cards = player_state.discard  # si la propiedad se llama así
        else:
            discard_cards = []
        if discard_cards:
            discard_cardset = convert_to_pokemon_cardsset(discard_cards, "Descartes Jugador")
            self.game_board.player_discard.extend(discard_cardset)
            if hasattr(self.game_board.player_discard, "graphics"):
                self.game_board.player_discard.graphics.clear_cache()

        # Mano del oponente (mostrar solo dorso)
        self.game_board.opponent_hand.clear()
        if opponent_state and opponent_state.hand and len(opponent_state.hand) > 0:
            # Crear carta dummy de dorso para representar la mano del oponente
            from game.core.cards.card_data import Card
            dummy_card = Card(id="card_back", name="Dorso de carta", rarity="Common", types=[])
            dummy_adapter = PokemonCardAdapter(dummy_card, instance_id="opponent_hand_back")
            self.game_board.opponent_hand.append(dummy_adapter)
            if hasattr(self.game_board.opponent_hand, "graphics"):
                self.game_board.opponent_hand.graphics.clear_cache()

        # Zona Activa del oponente
        self.game_board.opponent_active.clear()
        if opponent_state and opponent_state.active_pokemon:
            opp_active_cardset = convert_to_pokemon_cardsset([opponent_state.active_pokemon], "Activo Rival")
            self.game_board.opponent_active.extend(opp_active_cardset)
            if hasattr(self.game_board.opponent_active, "graphics"):
                self.game_board.opponent_active.graphics.clear_cache()

        # Zonas de Banca del oponente
        opp_bench_areas = [
            self.game_board.opponent_bench_1,
            self.game_board.opponent_bench_2,
            self.game_board.opponent_bench_3
        ]
        for area in opp_bench_areas:
            area.clear()
        if opponent_state:
            opp_bench_pokemon = opponent_state.bench_pokemon if hasattr(opponent_state, "bench_pokemon") else []
            for i, pokemon in enumerate(opp_bench_pokemon[:3]):  # máx. 3 en banca
                if i < len(opp_bench_areas) and pokemon is not None:
                    opp_bench_cardset = convert_to_pokemon_cardsset([pokemon], f"Banca Enemiga {i+1}")
                    opp_bench_areas[i].extend(opp_bench_cardset)
                    if hasattr(opp_bench_areas[i], "graphics"):
                        opp_bench_areas[i].graphics.clear_cache()

        # Pila de descarte del oponente (si se necesita, similar a la del jugador)
        self.game_board.opponent_discard.clear()
        # (Se puede poblar si hay cartas en la pila de descarte del oponente)

        # Mazo del jugador (dorso de carta)
        self.game_board.player_deck.clear()
        if player_state:
            deck_count = len(player_state.deck) if hasattr(player_state, "deck") else 0
        else:
            deck_count = 0
        if deck_count > 0:
            from game.core.cards.card_data import Card
            dummy_card = Card(id="card_back", name="Dorso de carta", rarity="Common", types=[])
            dummy_adapter = PokemonCardAdapter(dummy_card, instance_id="player_deck_back")
            self.game_board.player_deck.append(dummy_adapter)
            if hasattr(self.game_board.player_deck, "graphics"):
                self.game_board.player_deck.graphics.clear_cache()

        # Mazo del oponente (dorso de carta)
        self.game_board.opponent_deck.clear()
        if opponent_state:
            opp_deck_count = len(opponent_state.deck) if hasattr(opponent_state, "deck") else 0
        else:
            opp_deck_count = 0
        if opp_deck_count > 0:
            from game.core.cards.card_data import Card
            dummy_card = Card(id="card_back", name="Dorso de carta", rarity="Common", types=[])
            dummy_adapter = PokemonCardAdapter(dummy_card, instance_id="opponent_deck_back")
            self.game_board.opponent_deck.append(dummy_adapter)
            if hasattr(self.game_board.opponent_deck, "graphics"):
                self.game_board.opponent_deck.graphics.clear_cache()

    def _safe_update_cardset(self, cardset: CardsSet, cards_data, name: str):
        """安全地更新卡牌集合"""
        try:
            if not cards_data:
                cardset.clear()
                return
            
            valid_cards = [card for card in cards_data if card is not None]
            
            if valid_cards:
                new_cardset = convert_to_pokemon_cardsset(valid_cards, name)
                self._update_cardset(cardset, new_cardset)
            else:
                cardset.clear()
                
        except Exception as e:
            print(f"❌ 安全更新卡牌集合失败 {name}: {e}")
            cardset.clear()
    
    def _update_deck_display(self, cardset: CardsSet, card_count: int):
        """更新卡组显示（显示卡背）"""
        try:
            # 清空现有卡组
            cardset.clear()
            
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
        
        # 处理 pygame_gui 按钮事件（💡 必须加这句！）
        if self.cards_manager and self.cards_manager.ui_manager:
            self.cards_manager.ui_manager.process_events(event)

        # 处理控制面板点击
        if event.type == pygame.MOUSEBUTTONDOWN:
            button_clicked = self.control_panel.handle_click(event.pos)
            if button_clicked:
                self._handle_button_click(button_clicked)
                return None
        
        # 处理卡牌管理器事件
        self.cards_manager.process_events(event)
        
        # 处理卡牌事件
        if event.type == CARDSSET_CLICKED:
            self._handle_cardset_clicked(event)
        elif event.type == CARD_MOVED:
            self._handle_card_moved(event)
        
        return None
    
    def _handle_button_click(self, button_key: str):
        """处理按钮点击"""
        print(f"🔘 按钮点击: {button_key}")
        
        if not self.battle_controller:
            return
        
        try:
            if button_key == "draw_card":
                result = self.battle_controller.process_player_action({"type": "draw_card"})
                print(f"抽卡结果: {result}")
            
            elif button_key == "gain_energy":
                result = self.battle_controller.process_player_action({"type": "gain_energy"})
                print(f"获得能量结果: {result}")
            
            elif button_key == "attack":
                result = self.battle_controller.process_player_action({
                    "type": "attack",
                    "parameters": {"attack_index": 0}
                })
                print(f"攻击结果: {result}")
            
            elif button_key == "end_turn":
                result = self.battle_controller.process_player_action({"type": "end_turn"})
                print(f"结束回合结果: {result}")
            
            elif button_key == "surrender":
                print("🏳️ 玩家投降")
                return "back_to_battle_page"
        
        except Exception as e:
            print(f"❌ 处理按钮点击失败: {e}")
    
    def _handle_cardset_clicked(self, event):
        """处理卡牌集合点击事件"""
        cardset_graphic = event.set
        # 如果图形对象有 cardset 属性，则获取对应的 CardsSet，否则直接使用它
        actual_set = getattr(cardset_graphic, 'cardset', cardset_graphic)
        card = event.card
        print(f"🎯 卡牌集合点击: {actual_set.name}")  # 使用 CardsSet 的名称
        if card:
            print(f"   点击卡牌: {card.name}")
    
    def _handle_card_moved(self, event):
        """Maneja el evento de mover una carta de un conjunto a otro."""
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
    
    def update(self, dt):
        """更新界面"""
        # 定期更新战斗状态
        self.last_update_time += dt
        if self.last_update_time > 0.5:  # 每0.5秒更新一次
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
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理修复版Pokemon TCG战斗界面")
        
        if hasattr(self.cards_manager, 'cleanup'):
            self.cards_manager.cleanup()
        
        if hasattr(self.game_board, 'cleanup'):
            self.game_board.cleanup()