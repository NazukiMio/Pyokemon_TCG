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
    
    def setup_exit_dialog(self):
        """设置退出确认对话框"""
        screen_width, screen_height = self.screen.get_size()
        
        dialog_width = int(min(500 * self.scale_factor, screen_width * 0.8))
        dialog_height = int(min(250 * self.scale_factor, screen_height * 0.45))
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2
        
        # 创建对话框面板
        self.exit_dialog_elements['panel'] = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height),
            manager=self.ui_manager
        )
        
        # 标题标签
        self.exit_dialog_elements['title'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 20, dialog_width - 40, 40),
            text='Confirmar salida',
            container=self.exit_dialog_elements['panel'],
            manager=self.ui_manager
        )
        
        # 消息标签
        self.exit_dialog_elements['message'] = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 70, dialog_width - 40, 60),
            text='¿Estás seguro de que quieres salir del juego?',
            container=self.exit_dialog_elements['panel'],
            manager=self.ui_manager
        )
        
        # 按钮
        button_width = int(dialog_width * 0.35)
        button_height = Theme.get_scaled_size('button_height_medium', self.scale_factor)
        button_y = dialog_height - button_height - 20
        
        self.exit_dialog_elements['yes'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20, button_y, button_width, button_height),
            text='SÍ, SALIR',
            container=self.exit_dialog_elements['panel'],
            manager=self.ui_manager,
            object_id='#main_button'
        )
        
        self.exit_dialog_elements['no'] = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(dialog_width - button_width - 20, button_y, button_width, button_height),
            text='CANCELAR',
            container=self.exit_dialog_elements['panel'],
            manager=self.ui_manager,
            object_id='#secondary_button'
        )
        
        # 初始隐藏对话框
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
        self.setup_ui_elements()
        
        # 重新加载Logo
        if self.logo:
            self.load_logo()
    
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
                # 呼吸效果
                self.intro_time += dt
                breath = (math.sin(self.intro_time * 3) + 1) / 2
                self.intro_alpha = int(100 + breath * 155)
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

    def draw_intro_text(self):
        """绘制引导文字"""
        screen_width, screen_height = self.screen.get_size()
        
        # 在按钮位置显示引导文字
        start_y = int(screen_height * 0.55)
        text_y = start_y + 60
        
        text_color = (255, 255, 255)
        text_surface = font_manager.render_text(
            self.intro_text, 'xl', screen_height, text_color
        )
        text_surface.set_alpha(int(self.intro_alpha))
        text_rect = text_surface.get_rect(center=(screen_width // 2, text_y))
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