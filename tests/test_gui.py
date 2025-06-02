"""
pygame_gui按钮样式测试
基于当前主题风格，去掉半透明效果
"""

import pygame
import pygame_gui
import sys
import os
import json

# 初始化pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pokemon TCG - pygame_gui Button Test")

# 主题数据 - 边框放大 + 伪立体 + hover文字变粗变醒目
UI_THEME_DATA = {
    "#main_button": {
        "colours": {
            "normal_bg": "#5865F2",          # 蓝色按钮
            "hovered_bg": "#4338D8",         # hover变深蓝
            "normal_border": "#7C84FF",      # 比背景稍亮的边框
            "hovered_border": "#3730A3",     # hover时深色边框，形成对比
            "normal_text": "#FFFFFF",
            "hovered_text": "#FFFFFF"
        },
        "font:hovered": {
            "bold": "1"
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "16", 
            "border_width": "3",             # 常规粗细
            "shadow_width": "0"
        }
    },
    "#secondary_button": {
        "colours": {
            "normal_bg": "#FFFFFF",          # 白色按钮
            "hovered_bg": "#F1F5F9",         # hover变浅灰，更明显
            "normal_border": "#E5E7EB",      # 浅灰边框
            "hovered_border": "#94A3B8",     # hover时中灰边框，更明显
            "normal_text": "#5865F2",
            "hovered_text": "#3730A3"
        },
        "font:hovered": {
            "bold": "1"
        },
        "misc": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "12",
            "border_width": "3",             # 常规粗细
            "shadow_width": "0"
        }
    },
    "#text_button": {
        "colours": {
            "normal_bg": "#00000000",
            "hovered_bg": "#F8F9FF",
            "selected_bg": "#F8F9FF", 
            "active_bg": "#F1F5F9",
            "normal_border": "#00000000",
            "hovered_border": "#5865F2",  # hover时显示边框
            "selected_border": "#5865F2",
            "active_border": "#4338D8",
            "normal_text": "#5865F2",
            "hovered_text": "#3730A3",   # 更深更醒目
            "selected_text": "#3730A3",
            "active_text": "#3730A3"
        },
        "font": {
            "name": "arial",
            "size": "16",
            "bold": "0"
        },
        "font:hovered": {
            "name": "arial",
            "size": "16",
            "bold": "1"  # hover粗体
        },
        "misc": {
            "shape": "rounded_rectangle", 
            "shape_corner_radius": "8",
            "border_width": "0",
            "shadow_width": "0"
        },
        "misc:hovered": {
            "shape": "rounded_rectangle",
            "shape_corner_radius": "8",
            "border_width": "2",      # hover时出现边框
            "shadow_width": "0"
        }
    }
}

with open('test_theme.json', 'w') as f:
    json.dump(UI_THEME_DATA, f, indent=2)

# 创建UI管理器
ui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), theme_path='test_theme.json')

# 创建按钮
primary_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(300, 200, 200, 56),
    text='Primary Button',
    manager=ui_manager,
    object_id='#main_button'
)

secondary_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(300, 280, 200, 50),
    text='Secondary Button', 
    manager=ui_manager,
    object_id='#secondary_button'
)

text_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(300, 350, 200, 40),
    text='Text Button',
    manager=ui_manager,
    object_id='#text_button'
)

# 时钟
clock = pygame.time.Clock()

# 主循环
running = True
while running:
    time_delta = clock.tick(60) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == primary_button:
                    print("Primary Button Clicked!")
                elif event.ui_element == secondary_button:
                    print("Secondary Button Clicked!")
                elif event.ui_element == text_button:
                    print("Text Button Clicked!")
        
        ui_manager.process_events(event)
    
    ui_manager.update(time_delta)
    
    # 绘制背景 - 使用你的主题背景色
    screen.fill((230, 235, 245))  # Theme.COLORS['background']
    
    # 绘制UI
    ui_manager.draw_ui(screen)
    
    # 更新显示
    pygame.display.flip()

pygame.quit()
sys.exit()