"""
战斗界面 - 基础实现
"""

import pygame
from typing import Dict, Any, Optional, List

class Button:
    """简单按钮组件"""
    
    def __init__(self, rect: pygame.Rect, text: str, callback=None):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.enabled = True
        self.hovered = False
        self.font = pygame.font.SysFont("arial", 16, bold=True)
    
    def handle_event(self, event) -> bool:
        """处理事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.enabled:
                if self.callback:
                    self.callback()
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        
        return False
    
    def draw(self, screen):
        """绘制按钮"""
        # 按钮颜色
        if not self.enabled:
            color = (60, 60, 60)
            text_color = (120, 120, 120)
        elif self.hovered:
            color = (80, 120, 160)
            text_color = (255, 255, 255)
        else:
            color = (60, 100, 140)
            text_color = (220, 220, 220)
        
        # 绘制按钮背景
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
        
        # 绘制文字
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class BattleInterface:
    """战斗界面主类"""
    
    def __init__(self, screen_width: int, screen_height: int, battle_controller):
        """
        初始化战斗界面
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度  
            battle_controller: 战斗控制器
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.battle_controller = battle_controller
        
        # 字体
        self.title_font = pygame.font.SysFont("arial", 32, bold=True)
        self.info_font = pygame.font.SysFont("arial", 18)
        self.small_font = pygame.font.SysFont("arial", 14)
        
        # 布局
        self.layout = self._calculate_layout()
        
        # 按钮
        self.buttons = self._create_buttons()
        
        # 状态
        self.battle_state = None
        self.player_hand = []
        self.selected_card_index = None
        
        print("🎮 战斗界面初始化完成")
        self._update_battle_state()
    
    def _calculate_layout(self) -> Dict[str, pygame.Rect]:
        """计算布局区域"""
        # 战场区域 (70%)
        field_height = int(self.screen_height * 0.7)
        # 操作区域 (30%) 
        action_height = self.screen_height - field_height
        
        return {
            "field": pygame.Rect(0, 0, self.screen_width, field_height),
            "action": pygame.Rect(0, field_height, self.screen_width, action_height),
            
            # 战场子区域
            "opponent_area": pygame.Rect(0, 0, self.screen_width, field_height // 2),
            "player_area": pygame.Rect(0, field_height // 2, self.screen_width, field_height // 2),
            
            # 操作子区域
            "hand_area": pygame.Rect(0, field_height, int(self.screen_width * 0.7), action_height),
            "button_area": pygame.Rect(int(self.screen_width * 0.7), field_height, 
                                     int(self.screen_width * 0.3), action_height)
        }
    
    def _create_buttons(self) -> List[Button]:
        """创建操作按钮"""
        buttons = []
        button_area = self.layout["button_area"]
        
        button_width = button_area.width - 20
        button_height = 40
        button_spacing = 10
        
        # 攻击按钮
        y = button_area.y + 20
        attack_rect = pygame.Rect(button_area.x + 10, y, button_width, button_height)
        buttons.append(Button(attack_rect, "攻击", self._attack_action))
        
        # 使用卡牌按钮
        y += button_height + button_spacing
        play_rect = pygame.Rect(button_area.x + 10, y, button_width, button_height)
        buttons.append(Button(play_rect, "使用卡牌", self._play_card_action))
        
        # 结束回合按钮
        y += button_height + button_spacing
        end_turn_rect = pygame.Rect(button_area.x + 10, y, button_width, button_height)
        buttons.append(Button(end_turn_rect, "结束回合", self._end_turn_action))
        
        # 返回按钮
        y += button_height + button_spacing * 2
        back_rect = pygame.Rect(button_area.x + 10, y, button_width, button_height)
        buttons.append(Button(back_rect, "返回(ESC)", self._back_action))
        
        return buttons
    
    def _update_battle_state(self):
        """更新战斗状态"""
        try:
            if self.battle_controller and self.battle_controller.current_battle:
                self.battle_state = self.battle_controller.current_battle.battle_state
                # 获取玩家手牌
                player_id = self.battle_controller.current_battle.player_id
                if player_id in self.battle_controller.current_battle.player_states:
                    player_state = self.battle_controller.current_battle.player_states[player_id]
                    self.player_hand = player_state.hand
        except Exception as e:
            print(f"⚠️ 更新战斗状态失败: {e}")
    
    def handle_event(self, event) -> Optional[str]:
        """处理事件"""
        # ESC键返回
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back_to_battle_page"
        
        # 按钮事件
        for button in self.buttons:
            if button.handle_event(event):
                break
        
        # 手牌点击
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_hand_click(event.pos)
        
        return None
    
    def _handle_hand_click(self, pos):
        """处理手牌点击"""
        hand_area = self.layout["hand_area"]
        if not hand_area.collidepoint(pos):
            return
        
        if not self.player_hand:
            return
        
        # 计算点击的卡牌
        card_width = 80
        card_spacing = 10
        total_width = len(self.player_hand) * (card_width + card_spacing) - card_spacing
        start_x = hand_area.centerx - total_width // 2
        
        for i in range(len(self.player_hand)):
            card_x = start_x + i * (card_width + card_spacing)
            card_rect = pygame.Rect(card_x, hand_area.y + 10, card_width, 100)
            
            if card_rect.collidepoint(pos):
                self.selected_card_index = i if self.selected_card_index != i else None
                print(f"🃏 选择手牌: {i} ({self.player_hand[i].card.name if self.selected_card_index is not None else '取消选择'})")
                break
    
    def update(self, dt):
        """更新界面"""
        self._update_battle_state()
    
    def draw(self, screen):
        """绘制界面"""
        # 背景
        screen.fill((25, 35, 50))
        
        # 绘制各个区域
        self._draw_field_area(screen)
        self._draw_action_area(screen)
        
        # 绘制按钮
        for button in self.buttons:
            button.draw(screen)
        
        # 绘制调试信息
        self._draw_debug_info(screen)
    
    def _draw_field_area(self, screen):
        """绘制战场区域"""
        field_rect = self.layout["field"]
        opponent_area = self.layout["opponent_area"]
        player_area = self.layout["player_area"]
        
        # 战场背景
        pygame.draw.rect(screen, (40, 60, 80), field_rect)
        
        # 分割线
        mid_y = field_rect.y + field_rect.height // 2
        pygame.draw.line(screen, (100, 120, 140), 
                        (field_rect.x, mid_y), (field_rect.right, mid_y), 3)
        
        # 对手区域
        pygame.draw.rect(screen, (50, 40, 40), opponent_area, 2)
        opponent_text = self.info_font.render("对手区域", True, (200, 150, 150))
        screen.blit(opponent_text, (opponent_area.x + 10, opponent_area.y + 10))
        
        # 玩家区域  
        pygame.draw.rect(screen, (40, 50, 40), player_area, 2)
        player_text = self.info_font.render("玩家区域", True, (150, 200, 150))
        screen.blit(player_text, (player_area.x + 10, player_area.y + 10))
        
        # 绘制Pokemon槽位（占位符）
        self._draw_pokemon_slots(screen, opponent_area, "对手")
        self._draw_pokemon_slots(screen, player_area, "玩家")
    
    def _draw_pokemon_slots(self, screen, area_rect, area_name):
        """绘制Pokemon槽位"""
        # 前排Pokemon槽位 (中央)
        active_size = (120, 160)
        active_x = area_rect.centerx - active_size[0] // 2
        active_y = area_rect.centery - active_size[1] // 2
        active_rect = pygame.Rect(active_x, active_y, active_size[0], active_size[1])
        
        pygame.draw.rect(screen, (80, 100, 120), active_rect, 2)
        active_text = self.small_font.render("前排", True, (180, 180, 180))
        screen.blit(active_text, (active_rect.centerx - 15, active_rect.bottom + 5))
        
        # 后备Pokemon槽位 (底部)
        bench_size = (60, 80)
        bench_spacing = 70
        bench_count = 5
        total_bench_width = bench_count * bench_spacing - (bench_spacing - bench_size[0])
        bench_start_x = area_rect.centerx - total_bench_width // 2
        bench_y = area_rect.bottom - bench_size[1] - 20
        
        for i in range(bench_count):
            bench_x = bench_start_x + i * bench_spacing
            bench_rect = pygame.Rect(bench_x, bench_y, bench_size[0], bench_size[1])
            pygame.draw.rect(screen, (60, 80, 100), bench_rect, 1)
    
    def _draw_action_area(self, screen):
        """绘制操作区域"""
        action_rect = self.layout["action"]
        hand_area = self.layout["hand_area"]
        button_area = self.layout["button_area"]
        
        # 操作区域背景
        pygame.draw.rect(screen, (30, 40, 50), action_rect)
        
        # 分割线
        pygame.draw.line(screen, (80, 100, 120), 
                        (hand_area.right, action_rect.y),
                        (hand_area.right, action_rect.bottom), 2)
        
        # 手牌区域
        pygame.draw.rect(screen, (35, 45, 55), hand_area, 1)
        hand_title = self.info_font.render("手牌", True, (200, 200, 200))
        screen.blit(hand_title, (hand_area.x + 10, hand_area.y + 5))
        
        # 绘制手牌
        self._draw_hand_cards(screen)
        
        # 按钮区域
        pygame.draw.rect(screen, (25, 35, 45), button_area, 1)
        button_title = self.info_font.render("操作", True, (200, 200, 200))
        screen.blit(button_title, (button_area.x + 10, button_area.y + 5))
    
    def _draw_hand_cards(self, screen):
        """绘制手牌"""
        if not self.player_hand:
            no_cards_text = self.small_font.render("没有手牌", True, (150, 150, 150))
            hand_area = self.layout["hand_area"]
            screen.blit(no_cards_text, (hand_area.centerx - 40, hand_area.centery))
            return
        
        hand_area = self.layout["hand_area"]
        card_width = 80
        card_height = 100
        card_spacing = 10
        
        # 计算起始位置
        total_width = len(self.player_hand) * (card_width + card_spacing) - card_spacing
        start_x = hand_area.centerx - total_width // 2
        card_y = hand_area.y + 30
        
        for i, card in enumerate(self.player_hand):
            card_x = start_x + i * (card_width + card_spacing)
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            
            # 选中效果
            if i == self.selected_card_index:
                pygame.draw.rect(screen, (255, 215, 0), card_rect, 3)
                # 向上偏移显示选中
                card_rect.y -= 10
            else:
                pygame.draw.rect(screen, (150, 150, 150), card_rect, 2)
            
            # 卡牌背景
            pygame.draw.rect(screen, (200, 200, 200), card_rect)
            
            # 卡牌名称
            name_text = self.small_font.render(card.card.name[:8], True, (50, 50, 50))
            name_rect = name_text.get_rect(centerx=card_rect.centerx, y=card_rect.y + 5)
            screen.blit(name_text, name_rect)
            
            # 卡牌类型
            if hasattr(card.card, 'hp') and card.card.hp:
                type_text = self.small_font.render(f"HP:{card.card.hp}", True, (50, 50, 50))
            else:
                type_text = self.small_font.render("训练师", True, (50, 50, 50))
            
            type_rect = type_text.get_rect(centerx=card_rect.centerx, y=card_rect.bottom - 20)
            screen.blit(type_text, type_rect)
    
    def _draw_debug_info(self, screen):
        """绘制调试信息"""
        debug_y = 10
        debug_texts = [
            f"战斗界面 - 开发中",
            f"手牌数量: {len(self.player_hand)}",
            f"选中卡牌: {self.selected_card_index}",
            f"按ESC返回"
        ]
        
        for text in debug_texts:
            debug_surface = self.small_font.render(text, True, (180, 180, 180))
            screen.blit(debug_surface, (10, debug_y))
            debug_y += 20
    
    # 按钮回调函数
    def _attack_action(self):
        """攻击动作"""
        print("🗡️ 执行攻击动作")
        # TODO: 实现攻击逻辑
    
    def _play_card_action(self):
        """使用卡牌动作"""
        if self.selected_card_index is not None:
            card = self.player_hand[self.selected_card_index]
            print(f"🃏 使用卡牌: {card.card.name}")
            # TODO: 实现卡牌使用逻辑
        else:
            print("⚠️ 请先选择一张卡牌")
    
    def _end_turn_action(self):
        """结束回合动作"""
        print("⏭️ 结束回合")
        # TODO: 实现结束回合逻辑
    
    def _back_action(self):
        """返回动作"""
        print("🔙 返回战斗页面")
    
    def cleanup(self):
        """清理资源"""
        print("🧹 战斗界面清理")
        self.buttons.clear()
        self.player_hand.clear()