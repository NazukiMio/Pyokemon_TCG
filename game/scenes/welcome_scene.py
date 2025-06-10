"""
重构后的引导欢迎场景
使用pygame_gui替代自定义UI组件
"""

import pygame
import pygame_gui
import json
import sys
import os

# 导入核心模块
from game.scenes.components.message_component import MessageManager, ToastMessage
from game.scenes.styles.theme import Theme
from game.scenes.styles.fonts import font_manager
from game.utils.video_background import VideoBackground

class WelcomeScene:
    """引导欢迎场景类，游戏的主入口页面"""
    
    def __init__(self, screen, callback=None, *args, **kwargs):
        """
        初始化欢迎场景
        
        Args:
            screen: pygame屏幕对象
            callback: 场景切换回调函数
        """
        self.screen = screen
        self.callback = callback
        
        # 缩放因子
        self.scale_factor = min(screen.get_width() / 1920, screen.get_height() / 1080)
        
        # 创建pygame_gui主题并初始化UI管理器
        self.setup_pygame_gui()
        
        # 组件管理器
        self.message_manager = MessageManager()
        
        # UI组件
        self.buttons = {}
        self.toast_message = None

        # 确认退出对话框状态
        self.show_exit_dialog = False
        self.exit_dialog_elements = {}
        
        # 背景
        self.background_surface = None
        self.video_background = None
        self.setup_background()
        
        # Logo
        self.logo = None
        self.load_logo()

        # 副标题Logo
        self.subtitle_logo = None
        self.load_subtitle_logo()
        
        # 引导层状态
        self.show_intro = True
        self.intro_alpha = 255
        self.intro_time = 0
        self.transition_intro = False
        self.intro_text = "Presiona cualquier tecla para comenzar"

        # 加载引导图片
        self.press_start_image = None
        self.load_press_start_image()

        # 设置UI元素
        self.setup_ui_elements()
        
        print("✅ 欢迎场景初始化完成")
    
    def setup_pygame_gui(self):
        """设置pygame_gui主题和管理器"""
        # 创建主题数据
        theme_data = {
            "#main_button": {
                "colours": {
                    "normal_bg": "#5865F2",
                    "hovered_bg": "#4338D8",
                    "selected_bg": "#4338D8",
                    "active_bg": "#4338D8",
                    "normal_border": "#7C84FF",
                    "hovered_border": "#3730A3",
                    "selected_border": "#3730A3",
                    "active_border": "#3730A3",
                    "normal_text": "#FFFFFF",
                    "hovered_text": "#FFFFFF",
                    "selected_text": "#FFFFFF",
                    "active_text": "#FFFFFF"
                },
                "font": {
                    "name": "arial",
                    "size": "20",
                    "bold": "0"
                },
                "font:hovered": {
                    "name": "arial",
                    "size": "20",
                    "bold": "1"
                },
                "misc": {
                    "shape": "rounded_rectangle",
                    "shape_corner_radius": "16",
                    "border_width": "3",
                    "shadow_width": "0"
                }
            },
            "#secondary_button": {
                "colours": {
                    "normal_bg": "#FFFFFF",
                    "hovered_bg": "#F1F5F9",
                    "selected_bg": "#F1F5F9",
                    "active_bg": "#F1F5F9",
                    "normal_border": "#E5E7EB",
                    "hovered_border": "#94A3B8",
                    "selected_border": "#94A3B8",
                    "active_border": "#94A3B8",
                    "normal_text": "#5865F2",
                    "hovered_text": "#3730A3",
                    "selected_text": "#3730A3",
                    "active_text": "#3730A3"
                },
                "font": {
                    "name": "arial",
                    "size": "18",
                    "bold": "0"
                },
                "font:hovered": {
                    "name": "arial",
                    "size": "18",
                    "bold": "1"
                },
                "misc": {
                    "shape": "rounded_rectangle",
                    "shape_corner_radius": "12",
                    "border_width": "3",
                    "shadow_width": "0"
                }
            },
            "#exit_dialog": {
                "colours": {
                    "normal_bg": "#FAFBFC",           # 非常浅的灰白色
                    "normal_border": "#E1E5E9",       # 浅边框
                    "dark_bg": "#F5F7FA"              # 稍深一点的背景
                },
                "misc": {
                    "shape": "rounded_rectangle",
                    "shape_corner_radius": "16",      # 稍小的圆角更现代
                    "border_width": "1",              # 更细的边框
                    "shadow_width": "12",             # 更大的阴影更有层次
                    "shadow_colour": "#00000015"      # 更淡的阴影
                }
            },
            # 添加对话框标题样式
            "#dialog_title": {
                "colours": {
                    "normal_text": "#1F2937",         # 深灰色文字
                    "normal_bg": "transparent"
                },
                "font": {
                    "name": "arial",
                    "size": "24",
                    "bold": "1"
                }
            },
            # 添加对话框消息样式
            "#dialog_message": {
                "colours": {
                    "normal_text": "#6B7280",         # 中等灰色文字
                    "normal_bg": "transparent"
                },
                "font": {
                    "name": "arial",
                    "size": "16",
                    "bold": "0"
                }
            }
        }
        
        # 保存主题文件
        with open('welcome_theme.json', 'w') as f:
            json.dump(theme_data, f, indent=2)
        
        # 创建UI管理器
        self.ui_manager = pygame_gui.UIManager(
            self.screen.get_size(), 
            theme_path='welcome_theme.json'
        )
    
    def setup_background(self):
        """设置背景效果"""
        try:
            # 尝试加载视频背景
            video_path = "assets/videos/bg.mp4"
            if os.path.exists(video_path):
                self.video_background = VideoBackground(video_path, self.screen.get_size())
                print("✅ 视频背景加载成功")
            else:
                print("⚠️ 视频背景文件不存在，使用渐变背景")
                self.create_gradient_background()
        except Exception as e:
            print(f"⚠️ 视频背景加载失败: {e}")
            self.create_gradient_background()
    
    def create_gradient_background(self):
        """创建渐变背景"""
        width, height = self.screen.get_size()
        self.background_surface = pygame.Surface((width, height))
        
        # 创建垂直渐变
        start_color = Theme.get_color('background_gradient_start')
        end_color = Theme.get_color('background_gradient_end')
        
        for y in range(height):
            progress = y / height
            r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
            pygame.draw.line(self.background_surface, (r, g, b), (0, y), (width, y))
    
    def load_logo(self):
        """加载Logo"""
        try:
            logo_path = os.path.join("assets", "images", "logo", "game_logo.png")
            if os.path.exists(logo_path):
                self.logo = pygame.image.load(logo_path)
                # 调整Logo大小
                logo_width = int(self.screen.get_width() * 0.3)
                logo_height = int(logo_width * (self.logo.get_height() / self.logo.get_width()))
                self.logo = pygame.transform.smoothscale(self.logo, (logo_width, logo_height))
                print("✅ Logo加载成功")
        except Exception as e:
            print(f"⚠️ Logo加载失败: {e}")

    def load_subtitle_logo(self):
        """加载副标题Logo"""
        try:
            logo_path = os.path.join("assets", "images", "logo", "secondLogo.png")
            if os.path.exists(logo_path):
                self.subtitle_logo = pygame.image.load(logo_path)
                # 调整副标题Logo大小
                logo_width = int(self.screen.get_width() * 0.25)
                logo_height = int(logo_width * (self.subtitle_logo.get_height() / self.subtitle_logo.get_width()))
                self.subtitle_logo = pygame.transform.smoothscale(self.subtitle_logo, (logo_width, logo_height))
                print("✅ 副标题Logo加载成功")
        except Exception as e:
            print(f"⚠️ 副标题Logo加载失败: {e}")
    
    def load_press_start_image(self):
        """加载Press Start图片"""
        try:
            press_path = os.path.join("assets", "icons", "ui", "press.png")
            if os.path.exists(press_path):
                self.press_start_image = pygame.image.load(press_path)
                # 根据屏幕大小调整图片尺寸
                screen_width, screen_height = self.screen.get_size()
                # 基础宽度为屏幕宽度的20%，但不超过400px
                target_width = int(min(screen_width * 0.2, 400))
                # 保持宽高比
                original_width, original_height = self.press_start_image.get_size()
                target_height = int(target_width * (original_height / original_width))
                
                self.press_start_image = pygame.transform.smoothscale(
                    self.press_start_image, 
                    (target_width, target_height)
                )
                print("✅ Press Start图片加载成功")
            else:
                print(f"⚠️ Press Start图片文件不存在: {press_path}")
        except Exception as e:
            print(f"⚠️ Press Start图片加载失败: {e}")

    def setup_ui_elements(self):
        """设置UI元素"""
        screen_width, screen_height = self.screen.get_size()
        
        # 计算按钮尺寸和位置
        button_width = int(min(400 * self.scale_factor, screen_width * 0.6))
        button_height = Theme.get_scaled_size('button_height_large', self.scale_factor)
        center_x = screen_width // 2
        start_y = int(screen_height * 0.55)
        button_spacing = int(80 * self.scale_factor)
        
        # 创建主要按钮
        login_rect = pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height)
        self.buttons['login'] = pygame_gui.elements.UIButton(
            relative_rect=login_rect,
            text='INICIAR SESIÓN',
            manager=self.ui_manager,
            object_id='#main_button'
        )
        
        register_rect = pygame.Rect(center_x - button_width // 2, start_y + button_spacing, button_width, button_height)
        self.buttons['register'] = pygame_gui.elements.UIButton(
            relative_rect=register_rect,
            text='CREAR CUENTA',
            manager=self.ui_manager,
            object_id='#secondary_button'
        )
        
        exit_rect = pygame.Rect(center_x - button_width // 2, start_y + button_spacing * 2, button_width, button_height)
        self.buttons['exit'] = pygame_gui.elements.UIButton(
            relative_rect=exit_rect,
            text='SALIR',
            manager=self.ui_manager,
            object_id='#secondary_button'
        )
        
        # 初始隐藏按钮（引导层期间）
        if self.show_intro:
            for button in self.buttons.values():
                button.hide()

        # 设置退出确认对话框
        self.setup_exit_dialog()
    
    # def setup_exit_dialog(self):
    #     """设置退出确认对话框"""
    #     screen_width, screen_height = self.screen.get_size()
        
    #     # 增加对话框尺寸
    #     dialog_width = int(min(500 * self.scale_factor, screen_width * 0.85))
    #     dialog_height = int(min(320 * self.scale_factor, screen_height * 0.55))  # 再增加高度
    #     dialog_x = (screen_width - dialog_width) // 2
    #     dialog_y = (screen_height - dialog_height) // 2
        
    #     # 创建对话框面板（应用新样式）
    #     self.exit_dialog_elements['panel'] = pygame_gui.elements.UIPanel(
    #         relative_rect=pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height),
    #         manager=self.ui_manager,
    #         object_id='#exit_dialog'
    #     )
        
    #     # 标题标签
    #     self.exit_dialog_elements['title'] = pygame_gui.elements.UILabel(
    #         relative_rect=pygame.Rect(30, 30, dialog_width - 60, 40),
    #         text='Confirmar salida',
    #         container=self.exit_dialog_elements['panel'],
    #         manager=self.ui_manager,
    #         object_id='#dialog_title'
    #     )
        
    #     # 消息标签
    #     self.exit_dialog_elements['message'] = pygame_gui.elements.UILabel(
    #         relative_rect=pygame.Rect(30, 80, dialog_width - 60, 80),
    #         text='¿Estás seguro de que quieres salir del juego?',
    #         container=self.exit_dialog_elements['panel'],
    #         manager=self.ui_manager,
    #         object_id='#dialog_message'
    #     )
        
    #     # 按钮（更大的边距）
    #     button_width = int(dialog_width * 0.3)       # 再缩小按钮宽度
    #     button_height = Theme.get_scaled_size('button_height_medium', self.scale_factor)
    #     button_margin = 40                           # 增加边距到40
    #     bottom_margin = 50                           # 底部边距设为50
    #     button_spacing = 20  # 按钮之间的间距
    #     total_buttons_width = button_width * 2 + button_spacing
    #     start_x = (dialog_width - total_buttons_width) // 2
        
    #     # 计算按钮位置
    #     button_y = dialog_height - button_height - bottom_margin
        
    #     # 左侧按钮（SÍ, SALIR）
    #     self.exit_dialog_elements['yes'] = pygame_gui.elements.UIButton(
    #         relative_rect=pygame.Rect(start_x, button_y, button_width, button_height),
    #         text='SÍ, SALIR',
    #         container=self.exit_dialog_elements['panel'],
    #         manager=self.ui_manager,
    #         object_id='#main_button'
    #     )
        
    #     # 右侧按钮（CANCELAR）- 确保右边距足够
    #     right_button_x = dialog_width - button_width - button_margin
    #     self.exit_dialog_elements['no'] = pygame_gui.elements.UIButton(
    #         relative_rect=pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height),
    #         text='CANCELAR',
    #         container=self.exit_dialog_elements['panel'],
    #         manager=self.ui_manager,
    #         object_id='#secondary_button'
    #     )
        
    #     # 初始隐藏对话框
    #     self.exit_dialog_elements['panel'].hide()
        
    def setup_exit_dialog(self):
        """设置退出确认对话框，带内容位置偏移修正"""
        dialog_width = 380
        dialog_height = 280
        screen_width, screen_height = self.screen.get_size()
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2

        self.exit_dialog_elements['panel'] = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height),
            manager=self.ui_manager,
            object_id='#exit_dialog'
        )

        # 偏移修正值
        x_offset = -13  # 实测偏右的像素数，微调可用 -14 ~ -20
        label_width = 360
        padding_top = 30
        title_height = 40
        message_height = 60
        button_height = 50
        button_width = 140
        button_spacing = 20

        # 居中标题 + 偏移
        self.exit_dialog_elements['title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                (dialog_width - label_width) // 2 + x_offset,
                padding_top,
                label_width,
                title_height
            ),
            text='Confirmar salida',
            container=self.exit_dialog_elements['panel'],
            manager=self.ui_manager,
            object_id='#dialog_title'
        )

        # 信息文字 + 偏移
        self.exit_dialog_elements['message'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                (dialog_width - label_width) // 2 + x_offset,
                padding_top + title_height + 10,
                label_width,
                message_height
            ),
            text='¿Estás seguro de que quieres salir del juego?',
            container=self.exit_dialog_elements['panel'],
            manager=self.ui_manager,
            object_id='#dialog_message'
        )

        # 按钮起始位置 + 偏移
        total_button_width = button_width * 2 + button_spacing
        start_x = (dialog_width - total_button_width) // 2 + x_offset
        button_y = dialog_height - button_height - 40

        self.exit_dialog_elements['yes'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x, button_y, button_width, button_height),
            text='SÍ, SALIR',
            container=self.exit_dialog_elements['panel'],
            manager=self.ui_manager,
            object_id='#main_button'
        )

        self.exit_dialog_elements['no'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height),
            text='CANCELAR',
            container=self.exit_dialog_elements['panel'],
            manager=self.ui_manager,
            object_id='#secondary_button'
        )

        self.exit_dialog_elements['panel'].hide()



    
    def handle_event(self, event):
        """处理事件"""
        # 处理引导层
        if self.show_intro and not self.transition_intro:
            if event.type == pygame.KEYDOWN or (event.type == pygame.MOUSEBUTTONDOWN):
                print("🎬 开始引导层转换")
                self.transition_intro = True
                return True
            elif event.type == pygame.QUIT:
                return False
            return True
        
        # 如果正在转换引导层，不处理其他事件
        if self.transition_intro and self.show_intro:
            return True

        if event.type == pygame.QUIT:
            if not self.show_exit_dialog:
                self.show_exit_dialog = True
                self.exit_dialog_elements['panel'].show()
                return True
            else:
                return False
        
        elif event.type == pygame.VIDEORESIZE:
            self.handle_resize(event.size)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.show_exit_dialog:
                    self.show_exit_dialog = False
                    self.exit_dialog_elements['panel'].hide()
                else:
                    self.show_exit_dialog = True
                    self.exit_dialog_elements['panel'].show()
                return True
        
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            self.handle_button_click(event.ui_element)
        
        # 处理pygame_gui事件
        self.ui_manager.process_events(event)
        
        return True
    
    def handle_button_click(self, button):
        """处理按钮点击"""
        if self.show_exit_dialog:
            if button == self.exit_dialog_elements['yes']:
                self.handle_exit_confirm()
            elif button == self.exit_dialog_elements['no']:
                self.handle_exit_cancel()
        else:
            if button == self.buttons['login']:
                self.handle_login_click()
            elif button == self.buttons['register']:
                self.handle_register_click()
            elif button == self.buttons['exit']:
                self.handle_exit_click()
    
    def handle_resize(self, new_size):
        """处理窗口大小变化"""
        self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
        self.ui_manager.set_window_resolution(new_size)
        self.scale_factor = min(new_size[0] / 1920, new_size[1] / 1080)
        
        # 重新创建背景
        if not self.video_background:
            self.create_gradient_background()
        else:
            self.video_background.update_size(new_size)
        
        # 重新设置UI元素
        self.clear_ui_elements()
        self.setup_ui_elements()
        self.setup_exit_dialog()

        # 如果原本正在显示退出对话框，resize 后需要重新 show 出来
        if self.show_exit_dialog and 'panel' in self.exit_dialog_elements:
            self.exit_dialog_elements['panel'].show()
        
        # 重新加载Logo
        if self.logo:
            self.load_logo()

        # 重新加载Press Start图片
        if self.press_start_image:
            self.load_press_start_image()

    def clear_ui_elements(self):
        for widget in self.buttons.values():
            widget.kill()
        self.buttons.clear()

        for widget in getattr(self, 'exit_dialog_elements', {}).values():
            widget.kill()
        self.exit_dialog_elements.clear()
    
    def handle_login_click(self):
        """处理登录按钮点击"""
        print("🔐 用户点击登录按钮")
        if self.callback:
            self.callback("login")

    def handle_register_click(self):
        """处理注册按钮点击"""
        print("✨ 用户点击注册按钮")
        if self.callback:
            self.callback("register")
    
    def handle_exit_click(self):
        """处理退出按钮点击"""
        print("🚪 用户点击退出按钮")
        self.show_exit_dialog = True
        self.exit_dialog_elements['panel'].show()
    
    def handle_exit_confirm(self):
        """处理确认退出"""
        print("✅ 用户确认退出游戏")
        if self.callback:
            self.callback("exit")
    
    def handle_exit_cancel(self):
        """处理取消退出"""
        print("❌ 用户取消退出")
        self.show_exit_dialog = False
        self.exit_dialog_elements['panel'].hide()
        self.toast_message = ToastMessage("Operación cancelada", "info", 1000)
    
    def update(self, dt):
        """更新场景"""
        import math
        
        # 更新引导层
        if self.show_intro:
            if not self.transition_intro:
                # 呼吸效果（图片版本）
                self.intro_time += dt
                breath = (math.sin(self.intro_time * 2.5) + 1) / 2  # 稍微慢一点
                if self.press_start_image:
                    # 图片的透明度变化范围可以更大
                    self.intro_alpha = int(0 + breath * 255)  # 120-255
                else:
                    # 文字保持原来的范围
                    self.intro_alpha = int(100 + breath * 155)  # 100-255
            else:
                # 引导层淡出
                fade_speed = 400
                self.intro_alpha -= dt * fade_speed
                
                if self.intro_alpha <= 0:
                    self.intro_alpha = 0
                    self.show_intro = False
                    self.transition_intro = False
                    # 显示按钮
                    for button in self.buttons.values():
                        button.show()
            
            return True
        
        # 更新pygame_gui
        self.ui_manager.update(dt)
        
        # 更新消息管理器
        self.message_manager.update(dt)
        
        # 更新Toast消息
        if self.toast_message and not self.toast_message.update():
            self.toast_message = None
        
        # 更新视频背景
        if self.video_background:
            self.video_background.update()
        
        return True
    
    def draw(self):
        """绘制场景"""
        # 绘制背景
        self.draw_background()
        
        # 绘制Logo和标题
        self.draw_logo_and_title()
        
        # 绘制副标题
        self.draw_subtitle()
        
        # 绘制pygame_gui UI
        if not self.show_intro:
            self.ui_manager.draw_ui(self.screen)
        
        # 绘制引导层文字
        if self.show_intro:
            self.draw_intro_text()
        
        # 绘制消息
        self.message_manager.draw(self.screen, self.scale_factor)
        
        # 绘制Toast消息
        if self.toast_message:
            screen_width, screen_height = self.screen.get_size()
            self.toast_message.draw(self.screen, screen_width // 2, int(screen_height * 0.85), self.scale_factor)

        # # 临时绘制对话框 panel 的可视边界和中心线
        # panel = self.exit_dialog_elements.get('panel')
        # if panel and self.show_exit_dialog:
        #     panel_rect = panel.get_relative_rect()
        #     abs_panel_x, abs_panel_y = panel.get_abs_rect().topleft

        #     # 绘制 panel 边框线（红）
        #     pygame.draw.rect(self.screen, (255, 0, 0), panel.get_abs_rect(), 2)

        #     # 绘制 panel 的垂直中轴线（绿）
        #     center_x = abs_panel_x + panel_rect.width // 2
        #     pygame.draw.line(self.screen, (0, 255, 0), (center_x, abs_panel_y), (center_x, abs_panel_y + panel_rect.height), 2)

        #     # 绘制 “SÍ, SALIR” 按钮中心（蓝）
        #     yes_button = self.exit_dialog_elements.get('yes')
        #     if yes_button:
        #         btn_rect = yes_button.get_abs_rect()
        #         btn_center_x = btn_rect.centerx
        #         pygame.draw.line(self.screen, (0, 0, 255), (btn_center_x, btn_rect.top), (btn_center_x, btn_rect.bottom), 2)

    def draw_intro_text(self):
        """绘制引导图片/文字"""
        screen_width, screen_height = self.screen.get_size()
        
        # 在按钮位置显示引导内容
        start_y = int(screen_height * 0.75)
        content_y = start_y + 60
        
        if self.press_start_image:
            # 使用图片
            # 创建带透明度的图片副本
            image_with_alpha = self.press_start_image.copy()
            image_with_alpha.set_alpha(int(self.intro_alpha))
            
            # 居中显示
            image_rect = image_with_alpha.get_rect(center=(screen_width // 2, content_y))
            self.screen.blit(image_with_alpha, image_rect)
        else:
            # 后备文字方案
            text_color = (255, 255, 255)
            
            # 计算合适的字体大小
            scale_factor = screen_height / 900
            font_size = int(24 * scale_factor)  # 24px基础大小
            
            # 使用智能渲染
            text_surface = font_manager.render_text_smart(
                self.intro_text, font_size, text_color, 'body'
            )
            
            text_surface.set_alpha(int(self.intro_alpha))
            text_rect = text_surface.get_rect(center=(screen_width // 2, content_y))
            self.screen.blit(text_surface, text_rect)

    def draw_background(self):
        """绘制背景"""
        if self.video_background:
            bg_surface = self.video_background.get_surface()
            if bg_surface:
                self.screen.blit(bg_surface, (0, 0))
            else:
                # 视频不可用时的后备背景
                if self.background_surface:
                    self.screen.blit(self.background_surface, (0, 0))
                else:
                    self.screen.fill(Theme.get_color('background'))
        else:
            if self.background_surface:
                self.screen.blit(self.background_surface, (0, 0))
            else:
                self.screen.fill(Theme.get_color('background'))
    
    def draw_logo_and_title(self):
        """绘制Logo和标题"""
        screen_width, screen_height = self.screen.get_size()
        
        if self.logo:
            logo_rect = self.logo.get_rect(center=(screen_width // 2, int(screen_height * 0.25)))
            self.screen.blit(self.logo, logo_rect)
        else:
            # 文字标题作为后备
            title_color = Theme.get_color('text_white')
            title_surface = font_manager.render_text(
                "Juego de Cartas", '2xl', screen_height, title_color
            )
            title_rect = title_surface.get_rect(center=(screen_width // 2, int(screen_height * 0.25)))
            self.screen.blit(title_surface, title_rect)
    
    def draw_subtitle(self):
        """绘制副标题"""
        screen_width, screen_height = self.screen.get_size()
        
        if self.subtitle_logo:
            # 使用图片
            logo_rect = self.subtitle_logo.get_rect(center=(screen_width // 2, int(screen_height * 0.4)))
            self.screen.blit(self.subtitle_logo, logo_rect)
        else:
            # 副标题文字
            subtitle_text = "JUEGO DE CARTAS COLECCIONABLES"
            text_color = Theme.get_color('text_white')
            text_surface = font_manager.render_text(subtitle_text, 'lg', screen_height, text_color)
            
            # 位置
            text_rect = text_surface.get_rect(center=(screen_width // 2, int(screen_height * 0.4)))
            
            # 简化的背景（不要毛玻璃效果）
            padding = Theme.get_scaled_size('spacing_xl', self.scale_factor)
            bg_rect = text_rect.inflate(padding * 2, Theme.get_scaled_size('spacing_lg', self.scale_factor))
            
            # 绘制简单背景
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 100))  # 半透明黑色
            self.screen.blit(bg_surface, bg_rect.topleft)
            
            # 绘制文字
            self.screen.blit(text_surface, text_rect)
    
    def cleanup(self):
        """清理资源"""
        # 清理视频背景
        if self.video_background:
            self.video_background.close()
        
        # 清理主题文件
        try:
            os.remove('welcome_theme.json')
        except:
            pass
            
        print("✅ 欢迎场景资源清理完成")
    
    def run(self):
        """运行场景的主循环（独立运行时使用）"""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            dt = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if not self.handle_event(event):
                    return "exit"
            
            if not self.update(dt):
                return "exit"
            
            self.draw()
            pygame.display.flip()
        
        self.cleanup()
        return "exit"