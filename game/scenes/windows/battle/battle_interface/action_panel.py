# ==== action_panel.py ====
# 保存为: game/ui/battle/battle_interface/action_panel.py

"""
操作面板 - 战斗中的操作按钮
"""

import pygame
from typing import List, Optional, Callable

class ActionButton:
    """操作按钮类"""
    
    def __init__(self, rect: pygame.Rect, text: str, action: str, enabled: bool = True):
        self.rect = rect
        self.text = text
        self.action = action
        self.enabled = enabled
        self.hovered = False
        
        # 颜色
        self.bg_color = (70, 80, 90) if enabled else (50, 50, 50)
        self.text_color = (255, 255, 255) if enabled else (150, 150, 150)
        self.border_color = (120, 140, 160) if enabled else (80, 80, 80)
        self.hover_color = (90, 110, 130)
        
        # 字体
        try:
            self.font = pygame.font.SysFont("arial", 14, bold=True)
        except:
            self.font = pygame.font.Font(None, 14)
    
    def handle_event(self, event) -> Optional[str]:
        """处理事件"""
        if not self.enabled:
            return None
            
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return self.action
        
        return None
    
    def draw(self, screen):
        """绘制按钮"""
        # 背景
        bg_color = self.hover_color if (self.hovered and self.enabled) else self.bg_color
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)
        
        # 文字
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class ActionPanel:
    """操作面板类"""
    
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.buttons: List[ActionButton] = []
        self.on_action: Optional[Callable] = None
        
        # 创建按钮
        self._create_buttons()
    
    def _create_buttons(self):
        """创建操作按钮"""
        button_width = self.rect.width - 20
        button_height = 35
        button_spacing = 10
        
        button_data = [
            ("ataque", "attack"),
            ("Usar carta", "play_card"),
            ("Turno finalizado", "end_turn"),
            ("Abandonar", "surrender")
        ]
        
        for i, (text, action) in enumerate(button_data):
            button_y = self.rect.y + 40 + i * (button_height + button_spacing)
            button_rect = pygame.Rect(
                self.rect.x + 10,
                button_y,
                button_width,
                button_height
            )
            
            button = ActionButton(button_rect, text, action)
            self.buttons.append(button)
    
    def handle_event(self, event) -> Optional[str]:
        """处理事件"""
        for button in self.buttons:
            action = button.handle_event(event)
            if action:
                print(f"🎯 操作按钮点击: {action}")
                if self.on_action:
                    self.on_action(action)
                return action
        return None
    
    def update_button_states(self, battle_state):
        """根据战斗状态更新按钮状态"""
        # 这里可以根据战斗状态启用/禁用按钮
        # 暂时保持简单
        pass
    
    def draw(self, screen):
        """绘制操作面板"""
        # 背景
        pygame.draw.rect(screen, (40, 45, 55), self.rect)
        pygame.draw.rect(screen, (80, 90, 100), self.rect, 2)
        
        # 标题
        try:
            title_font = pygame.font.SysFont("noto sans", 16, bold=True)
        except:
            title_font = pygame.font.Font(None, 16)
        
        title_text = title_font.render("操作", True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=self.rect.centerx, y=self.rect.y + 10)
        screen.blit(title_text, title_rect)
        
        # 按钮
        for button in self.buttons:
            button.draw(screen)


