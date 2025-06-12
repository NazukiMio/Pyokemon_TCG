# ==== battle_ui.py ====
# 保存为: game/ui/battle/battle_interface/battle_ui.py

"""
完整的战斗界面 - 可直接使用
"""

import pygame
import os
from typing import Optional, Dict, Any, List

# 导入组件（如果不存在就创建简化版本）
try:
    from game.scenes.windows.battle.battle_interface.action_panel import ActionPanel
except:
    print("⚠️ action_panel.py 未找到，使用内置版本")
    ActionPanel = None

try:
    from game.scenes.windows.battle.battle_interface.field_display import FieldDisplay
except:
    print("⚠️ field_display.py 未找到，使用内置版本")
    FieldDisplay = None

class SimpleBattleInterface:
    """简化的战斗界面 - 确保能显示"""
    
    def __init__(self, screen_width: int, screen_height: int, battle_controller, battle_cache=None):
        """初始化战斗界面"""
        print(f"🎮 创建简化战斗界面: {screen_width}x{screen_height}")
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.battle_controller = battle_controller
        self.battle_cache = battle_cache
        
        # 字体初始化
        try:
            self.font = pygame.font.SysFont("arial", 16)
            self.small_font = pygame.font.SysFont("arial", 12)
            self.large_font = pygame.font.SysFont("arial", 24, bold=True)
        except:
            self.font = pygame.font.Font(None, 16)
            self.small_font = pygame.font.Font(None, 12)
            self.large_font = pygame.font.Font(None, 24)
        
        # 布局
        self.layout = self._setup_layout()
        
        # 状态
        self.battle_state = None
        self.player_hand = []
        self.selected_card_index = None
        self.hovered_card_index = None
        self.hover_timer = 0.0
        
        # 简单按钮
        self.buttons = self._create_simple_buttons()
        
        # 更新战斗状态
        self._update_battle_state()
        
        print(f"✅ 简化战斗界面创建成功")
        print(f"   - 手牌数量: {len(self.player_hand)}")
        print(f"   - 战斗状态: {self.battle_state is not None}")
    
    def _setup_layout(self):
        """设置界面布局"""
        return {
            "field_area": pygame.Rect(0, 0, self.screen_width, int(self.screen_height * 0.7)),
            "hand_area": pygame.Rect(0, int(self.screen_height * 0.7), 
                                   int(self.screen_width * 0.7), int(self.screen_height * 0.3)),
            "action_area": pygame.Rect(int(self.screen_width * 0.7), int(self.screen_height * 0.7),
                                     int(self.screen_width * 0.3), int(self.screen_height * 0.3))
        }
    
    def _create_simple_buttons(self):
        """创建简单按钮"""
        buttons = []
        action_area = self.layout["action_area"]
        
        button_data = [
            ("Ataque", "attack"),
            ("Utilizar carta", "play_card"), 
            ("Terminar turno", "end_turn"),
            ("Abandonar", "surrender"),
            ("Volver", "back")
        ]
        
        button_width = action_area.width - 20
        button_height = 30
        button_spacing = 8
        
        for i, (text, action) in enumerate(button_data):
            button_y = action_area.y + 30 + i * (button_height + button_spacing)
            button_rect = pygame.Rect(
                action_area.x + 10,
                button_y,
                button_width,
                button_height
            )
            buttons.append({
                'rect': button_rect,
                'text': text,
                'action': action,
                'hovered': False
            })
        
        return buttons
    
    def _update_battle_state(self):
        """更新战斗状态 - 修复版"""
        try:
            if self.battle_controller and self.battle_controller.current_battle:
                self.battle_state = self.battle_controller.get_current_state()
                
                if self.battle_state:
                    # 🔧 兼容字典和对象两种格式
                    current_player_id = None
                    if isinstance(self.battle_state, dict):
                        current_player_id = self.battle_state.get('current_player_id')
                        player_states = self.battle_state.get('player_states', {})
                    else:
                        current_player_id = getattr(self.battle_state, 'current_player_id', None)
                        player_states = getattr(self.battle_state, 'player_states', {})
                    
                    if current_player_id and player_states:
                        player_state = player_states.get(current_player_id)
                        if player_state:
                            # 🔧 兼容字典和对象格式的player_state
                            if isinstance(player_state, dict):
                                self.player_hand = player_state.get('hand', [])
                            else:
                                self.player_hand = getattr(player_state, 'hand', [])
                            
                            # print(f"🔄 更新手牌: {len(self.player_hand)} 张")
                        else:
                            self.player_hand = []
                    else:
                        self.player_hand = []
                else:
                    self.player_hand = []
            else:
                self.battle_state = None
                self.player_hand = []
        except Exception as e:
            print(f"❌ 更新战斗状态失败: {e}")
            self.battle_state = None
            self.player_hand = []
    
    def handle_event(self, event) -> Optional[str]:
        """处理事件"""
        # ESC键返回
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("🔙 ESC键按下，返回战斗页面")
                return "back_to_battle_page"
        
        # 鼠标移动
        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
        
        # 鼠标点击
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 检查按钮点击
            action = self._handle_button_click(event.pos)
            if action:
                return action
            
            # 检查手牌点击
            self._handle_hand_click(event.pos)
        
        return None
    
    def _handle_mouse_motion(self, pos):
        """处理鼠标移动"""
        # 更新按钮hover状态
        for button in self.buttons:
            button['hovered'] = button['rect'].collidepoint(pos)
        
        # 更新手牌hover状态
        prev_hover = self.hovered_card_index
        self.hovered_card_index = self._get_hovered_card_index(pos)
        
        if prev_hover != self.hovered_card_index:
            self.hover_timer = 0.0
    
    def _handle_button_click(self, pos) -> Optional[str]:
        """处理按钮点击 - 增强版"""
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                action = button['action']
                print(f"🎯 按钮点击: {button['text']} ({action})")
                
                if action == "back":
                    return "back_to_battle_page"
                elif action == "end_turn":
                    # 结束回合逻辑
                    if self.battle_controller:
                        try:
                            print("🔄 尝试结束回合...")
                            self.battle_controller.end_turn()
                            print("✅ 回合结束成功")
                        except Exception as e:
                            print(f"❌ 结束回合失败: {e}")
                elif action == "attack":
                    # 攻击逻辑
                    if self.selected_card_index is not None and self.player_hand:
                        selected_card = self.player_hand[self.selected_card_index]
                        print(f"🗡️ 尝试攻击，选中卡牌: {selected_card.card.name}")
                        # TODO: 实现实际攻击逻辑
                    else:
                        print("⚠️ 请先选择一张卡牌")
                elif action == "play_card":
                    # 使用卡牌逻辑
                    if self.selected_card_index is not None and self.player_hand:
                        selected_card = self.player_hand[self.selected_card_index]
                        print(f"🃏 尝试使用卡牌: {selected_card.card.name}")
                        # TODO: 实现实际使用卡牌逻辑
                    else:
                        print("⚠️ 请先选择一张卡牌")
                elif action == "surrender":
                    # 投降逻辑
                    print("🏳️ 投降")
                    # TODO: 实现投降逻辑
                    return "back_to_battle_page"
                else:
                    print(f"🎯 执行操作: {action}")
                
                return None
        
        return None
    
    def debug_battle_state(self):
        """调试战斗状态结构"""
        if not self.battle_state:
            print("🔍 battle_state 为 None")
            return
        
        print(f"🔍 battle_state 类型: {type(self.battle_state)}")
        
        if isinstance(self.battle_state, dict):
            print("🔍 battle_state 是字典，包含以下键:")
            for key, value in self.battle_state.items():
                print(f"   {key}: {type(value)} = {str(value)[:50]}...")
        else:
            print("🔍 battle_state 是对象，包含以下属性:")
            for attr in dir(self.battle_state):
                if not attr.startswith('_'):
                    try:
                        value = getattr(self.battle_state, attr)
                        print(f"   {attr}: {type(value)} = {str(value)[:50]}...")
                    except:
                        print(f"   {attr}: <无法访问>")

    def _get_hovered_card_index(self, pos) -> Optional[int]:
        """获取鼠标悬停的卡牌索引"""
        hand_area = self.layout["hand_area"]
        if not hand_area.collidepoint(pos) or not self.player_hand:
            return None
        
        card_width = 80
        card_spacing = 10
        total_width = len(self.player_hand) * (card_width + card_spacing) - card_spacing
        start_x = hand_area.centerx - total_width // 2
        
        for i in range(len(self.player_hand)):
            card_x = start_x + i * (card_width + card_spacing)
            card_rect = pygame.Rect(card_x, hand_area.y + 20, card_width, 100)
            
            if card_rect.collidepoint(pos):
                return i
        
        return None
    
    def _handle_hand_click(self, pos):
        """处理手牌点击"""
        hand_area = self.layout["hand_area"]
        if not hand_area.collidepoint(pos) or not self.player_hand:
            return
        
        card_width = 80
        card_spacing = 10
        total_width = len(self.player_hand) * (card_width + card_spacing) - card_spacing
        start_x = hand_area.centerx - total_width // 2
        
        for i in range(len(self.player_hand)):
            card_x = start_x + i * (card_width + card_spacing)
            card_rect = pygame.Rect(card_x, hand_area.y + 20, card_width, 100)
            
            if card_rect.collidepoint(pos):
                self.selected_card_index = i if self.selected_card_index != i else None
                card_name = self.player_hand[i].card.name if i < len(self.player_hand) else "未知"
                print(f"🃏 选择手牌 {i}: {card_name} ({'已选中' if self.selected_card_index == i else '取消选择'})")
                break
    
    def update(self, dt):
        """更新界面"""
        self._update_battle_state()
        
        # 更新hover计时器
        if self.hovered_card_index is not None:
            self.hover_timer += dt
    
    def draw(self, screen):
        """绘制界面 - 带调试信息"""
        # 清空屏幕
        screen.fill((25, 30, 40))
        
        # 绘制标题
        self._draw_title(screen)
        
        # 绘制各个区域
        self._draw_field_area(screen)
        self._draw_hand_area(screen)
        self._draw_action_area(screen)
        
        # 绘制手牌
        self._draw_hand_cards(screen)
        
        # 绘制战斗信息
        self._draw_battle_info(screen)
        
        # 🔧 绘制调试信息（左下角）
        self._draw_debug_info(screen)

    def _draw_debug_info(self, screen):
        """绘制调试信息"""
        try:
            debug_x = 10
            debug_y = self.screen_height - 150
            
            # 背景
            debug_rect = pygame.Rect(debug_x, debug_y, 250, 140)
            pygame.draw.rect(screen, (20, 20, 30, 200), debug_rect)
            pygame.draw.rect(screen, (60, 60, 80), debug_rect, 1)
            
            # 调试信息
            debug_info = [
                f"接口状态: 正常",
                f"战斗控制器: {'有' if self.battle_controller else '无'}",
                f"当前战斗: {'有' if self.battle_controller and self.battle_controller.current_battle else '无'}",
                f"战斗状态: {type(self.battle_state).__name__ if self.battle_state else '无'}",
                f"手牌数量: {len(self.player_hand)}",
                f"选中卡牌: {self.selected_card_index if self.selected_card_index is not None else '无'}",
                f"悬停卡牌: {self.hovered_card_index if self.hovered_card_index is not None else '无'}"
            ]
            
            for i, info in enumerate(debug_info):
                text_surface = self.small_font.render(info, True, (180, 180, 180))
                screen.blit(text_surface, (debug_x + 5, debug_y + 5 + i * 18))
                
        except Exception as e:
            print(f"❌ 绘制调试信息失败: {e}")

    def _draw_title(self, screen):
        """绘制标题"""
        title = "Pokemon TCG - batalla"
        title_surface = self.large_font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(centerx=self.screen_width//2, y=10)
        screen.blit(title_surface, title_rect)
        
        # 提示文字
        hint = "Presiona ESC para volver | Haz clic en las cartas para seleccionar | Haz clic en los botones para operar"
        hint_surface = self.small_font.render(hint, True, (200, 200, 200))
        hint_rect = hint_surface.get_rect(centerx=self.screen_width//2, y=35)
        screen.blit(hint_surface, hint_rect)
    
    def _draw_field_area(self, screen):
        """绘制战场区域"""
        field_area = self.layout["field_area"]
        
        # 战场背景
        pygame.draw.rect(screen, (40, 50, 60), field_area)
        pygame.draw.rect(screen, (80, 100, 120), field_area, 3)
        
        # 标题
        title = "Área de batalla"
        title_surface = self.font.render(title, True, (255, 255, 255))
        screen.blit(title_surface, (field_area.x + 10, field_area.y + 60))
        
        # 简单的战场布局
        center_x = field_area.centerx
        center_y = field_area.centery
        
        # 敌方区域（红色）
        enemy_rect = pygame.Rect(center_x - 100, center_y - 120, 200, 80)
        pygame.draw.rect(screen, (120, 60, 60), enemy_rect)
        pygame.draw.rect(screen, (200, 100, 100), enemy_rect, 2)
        
        enemy_text = self.font.render("Área enemiga", True, (255, 255, 255))
        enemy_text_rect = enemy_text.get_rect(center=enemy_rect.center)
        screen.blit(enemy_text, enemy_text_rect)
        
        # 玩家区域（绿色）
        player_rect = pygame.Rect(center_x - 100, center_y + 40, 200, 80)
        pygame.draw.rect(screen, (60, 120, 60), player_rect)
        pygame.draw.rect(screen, (100, 200, 100), player_rect, 2)
        
        player_text = self.font.render("Área del jugador", True, (255, 255, 255))
        player_text_rect = player_text.get_rect(center=player_rect.center)
        screen.blit(player_text, player_text_rect)
        
        # 中央分隔线
        pygame.draw.line(screen, (150, 150, 150), 
                        (field_area.x + 50, center_y), 
                        (field_area.right - 50, center_y), 2)
    
    def _draw_hand_area(self, screen):
        """绘制手牌区域"""
        hand_area = self.layout["hand_area"]
        
        # 手牌区域背景
        pygame.draw.rect(screen, (50, 60, 40), hand_area)
        pygame.draw.rect(screen, (100, 120, 80), hand_area, 3)
        
        # 标题
        title = f"({len(self.player_hand)} Cartas) Área de mano"
        title_surface = self.font.render(title, True, (255, 255, 255))
        screen.blit(title_surface, (hand_area.x + 10, hand_area.y + 5))
    
    def _draw_action_area(self, screen):
        """绘制操作区域"""
        action_area = self.layout["action_area"]
        
        # 操作区域背景
        pygame.draw.rect(screen, (60, 40, 50), action_area)
        pygame.draw.rect(screen, (120, 80, 100), action_area, 3)
        
        # 标题
        title = "Área de acción"
        title_surface = self.font.render(title, True, (255, 255, 255))
        screen.blit(title_surface, (action_area.x + 10, action_area.y + 5))
        
        # 绘制按钮
        for button in self.buttons:
            # 按钮背景
            bg_color = (80, 100, 120) if button['hovered'] else (60, 70, 80)
            pygame.draw.rect(screen, bg_color, button['rect'])
            pygame.draw.rect(screen, (150, 150, 150), button['rect'], 2)
            
            # 按钮文字
            text_surface = self.small_font.render(button['text'], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button['rect'].center)
            screen.blit(text_surface, text_rect)
    
    def _draw_hand_cards(self, screen):
        """绘制手牌"""
        if not self.player_hand:
            hand_area = self.layout["hand_area"]
            no_cards_text = self.font.render("No hay cartas", True, (150, 150, 150))
            no_cards_rect = no_cards_text.get_rect(center=(hand_area.centerx, hand_area.centery))
            screen.blit(no_cards_text, no_cards_rect)
            return
        
        hand_area = self.layout["hand_area"]
        card_width = 80
        card_height = 100
        card_spacing = 10
        
        # 计算起始位置
        total_width = len(self.player_hand) * (card_width + card_spacing) - card_spacing
        start_x = hand_area.centerx - total_width // 2
        card_y = hand_area.y + 20
        
        # 绘制hover放大卡牌（最后绘制，在最上层）
        hover_card_info = None
        
        for i, card in enumerate(self.player_hand):
            card_x = start_x + i * (card_width + card_spacing)
            
            is_hovered = (i == self.hovered_card_index and self.hover_timer > 0.3)
            is_selected = (i == self.selected_card_index)
            
            if is_hovered:
                # 记录hover卡牌信息，稍后绘制放大版
                hover_card_info = {
                    'card': card,
                    'x': card_x,
                    'y': card_y,
                    'selected': is_selected
                }
                # 普通卡牌半透明
                self._draw_single_card(screen, card, card_x, card_y, card_width, card_height, is_selected, alpha=150)
            else:
                # 普通卡牌
                self._draw_single_card(screen, card, card_x, card_y, card_width, card_height, is_selected)
        
        # 绘制hover放大卡牌
        if hover_card_info:
            self._draw_hover_card(screen, hover_card_info)
    
    def _draw_single_card(self, screen, card, x, y, width, height, selected=False, alpha=255):
        """绘制单张卡牌"""
        # 使用缓存系统（如果可用）
        if self.battle_cache:
            try:
                card_surface = self.battle_cache.render_card(card, 'hand', selected)
                if card_surface:
                    if alpha < 255:
                        card_surface = card_surface.copy()
                        card_surface.set_alpha(alpha)
                    
                    # 缩放到目标大小
                    scaled_surface = pygame.transform.scale(card_surface, (width, height))
                    screen.blit(scaled_surface, (x, y))
                    return
            except Exception as e:
                print(f"❌ 缓存渲染失败: {e}")
        
        # 降级到简单渲染
        card_rect = pygame.Rect(x, y, width, height)
        
        # 卡牌背景
        bg_color = (200, 200, 200)
        border_color = (255, 215, 0) if selected else (150, 150, 150)
        border_width = 3 if selected else 2
        
        # 创建卡牌表面
        card_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(card_surface, bg_color, card_surface.get_rect())
        pygame.draw.rect(card_surface, border_color, card_surface.get_rect(), border_width)
        
        # 卡牌名称
        name = card.card.name
        if len(name) > 8:
            name = name[:6] + ".."
        
        name_text = self.small_font.render(name, True, (50, 50, 50))
        name_rect = name_text.get_rect(centerx=width//2, y=5)
        card_surface.blit(name_text, name_rect)
        
        # 卡牌类型
        if hasattr(card.card, 'hp') and card.card.hp:
            type_text = self.small_font.render(f"HP:{card.card.hp}", True, (50, 50, 50))
        else:
            type_text = self.small_font.render("Entrenador", True, (50, 50, 50))
        
        type_rect = type_text.get_rect(centerx=width//2, y=height-20)
        card_surface.blit(type_text, type_rect)
        
        # 设置透明度
        if alpha < 255:
            card_surface.set_alpha(alpha)
        
        screen.blit(card_surface, card_rect)
    
    def _draw_hover_card(self, screen, hover_info):
        """绘制hover放大卡牌"""
        card = hover_info['card']
        original_x = hover_info['x']
        original_y = hover_info['y']
        selected = hover_info['selected']
        
        # 放大尺寸
        hover_width = 160
        hover_height = 220
        
        # 位置（向上偏移，居中）
        hover_x = original_x + (80 - hover_width) // 2
        hover_y = original_y - 80  # 向上偏移
        
        # 确保不超出屏幕
        if hover_x < 0:
            hover_x = 0
        elif hover_x + hover_width > self.screen_width:
            hover_x = self.screen_width - hover_width
        
        if hover_y < 0:
            hover_y = 0
        
        # 绘制阴影
        shadow_surface = pygame.Surface((hover_width + 8, hover_height + 8), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 80))
        screen.blit(shadow_surface, (hover_x - 4, hover_y + 4))
        
        # 使用缓存系统绘制放大卡牌
        if self.battle_cache:
            try:
                hover_surface = self.battle_cache.render_card(card, 'hover', selected)
                if hover_surface:
                    screen.blit(hover_surface, (hover_x, hover_y))
                    return
            except Exception as e:
                print(f"❌ hover缓存渲染失败: {e}")
        
        # 降级到简单放大渲染
        self._draw_single_card(screen, card, hover_x, hover_y, hover_width, hover_height, selected)
    
    def _draw_battle_info(self, screen):
        """绘制战斗信息 - 修复版"""
        if not self.battle_state:
            return
        
        try:
            # 在右上角显示战斗信息
            info_x = self.screen_width - 200
            info_y = 60
            
            # 背景
            info_rect = pygame.Rect(info_x, info_y, 190, 120)
            pygame.draw.rect(screen, (30, 30, 30, 180), info_rect)
            pygame.draw.rect(screen, (100, 100, 100), info_rect, 2)
            
            # 🔧 兼容字典和对象两种格式
            if isinstance(self.battle_state, dict):
                # 字典格式
                current_player = self.battle_state.get('current_player_id', 'Unknown')
                turn = self.battle_state.get('turn_number', 1)
                phase = self.battle_state.get('current_phase', 'unknown')
            else:
                # 对象格式
                current_player = getattr(self.battle_state, 'current_player_id', 'Unknown')
                turn = getattr(self.battle_state, 'turn_number', 1)
                phase = getattr(self.battle_state, 'current_phase', 'unknown')
            
            # 标题
            title_text = self.small_font.render("Info de Batalla", True, (255, 255, 255))
            screen.blit(title_text, (info_x + 5, info_y + 5))
            
            # 当前玩家
            player_text = self.small_font.render(f"Jugador actual: {current_player}", True, (255, 255, 255))
            screen.blit(player_text, (info_x + 5, info_y + 25))
            
            # 回合数
            turn_text = self.small_font.render(f"Turno: {turn}", True, (255, 255, 255))
            screen.blit(turn_text, (info_x + 5, info_y + 45))
            
            # 阶段
            phase_text = self.small_font.render(f"Fase: {phase}", True, (255, 255, 255))
            screen.blit(phase_text, (info_x + 5, info_y + 65))
            
            # 手牌数
            hand_count = len(self.player_hand)
            hand_text = self.small_font.render(f"Carta en mano: {hand_count}", True, (255, 255, 255))
            screen.blit(hand_text, (info_x + 5, info_y + 85))
            
        except Exception as e:
            print(f"❌ 绘制战斗信息失败: {e}")
            # 显示错误信息
            try:
                error_text = f"信息获取失败: {str(e)[:20]}"
                error_surface = self.small_font.render(error_text, True, (255, 100, 100))
                screen.blit(error_surface, (info_x + 5, info_y + 25))
            except:
                pass
    
    def cleanup(self):
        """清理资源"""
        print("🧹 简化战斗界面清理")
        self.player_hand.clear()
        self.selected_card_index = None
        self.hovered_card_index = None
        self.hover_timer = 0.0


# 兼容性别名
BattleInterface = SimpleBattleInterface