"""
重构后的现代化注册场景
使用pygame_gui替代自定义UI组件，复用login主题
"""

import pygame
import pygame_gui
import shutil
import sys
import os

# 导入核心模块
from game.core.auth.auth_manager import AuthManager
from game.scenes.components.message_component import MessageManager, ToastMessage
from game.scenes.styles.theme import Theme
from game.scenes.styles.fonts import font_manager
from game.utils.video_background import VideoBackground

class RegisterScene:
    """现代化注册场景类，使用pygame_gui组件系统"""
    
    def __init__(self, screen, callback=None):
        """
        初始化注册场景
        
        Args:
            screen: pygame屏幕对象
            callback: 注册成功后的回调函数
        """
        self.screen = screen
        self.callback = callback
        self.auth_manager = AuthManager()
        
        # 缩放因子
        self.scale_factor = min(screen.get_width() / 1920, screen.get_height() / 1080)
        
        # 复用login主题
        self.setup_pygame_gui()
        
        # 组件管理器
        self.message_manager = MessageManager()
        
        # UI组件
        self.inputs = {}
        self.buttons = {}
        self.labels = {}
        self.toast_message = None
        
        # 密码强度显示
        self.password_strength_text = ""
        self.password_strength_color = (150, 150, 150)
        
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
        
        # 设置UI元素
        self.setup_ui_elements()
        
        print("✅ 注册场景初始化完成")

    def setup_pygame_gui(self):
        """设置pygame_gui主题"""
        # 总是创建完整的主题，确保样式正确应用
        self.create_basic_theme()
        print("✅ 创建完整注册主题")
        
        # 创建UI管理器
        self.ui_manager = pygame_gui.UIManager(
            self.screen.get_size(), 
            theme_path='register_theme.json'
        )
    
    def create_basic_theme(self):
        """创建完整主题"""
        import json
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
            "#text_button": {
                "colours": {
                    "normal_bg": "#00000000",
                    "hovered_bg": "#F8F9FF",
                    "selected_bg": "#F8F9FF",
                    "active_bg": "#F8F9FF",
                    "normal_border": "#00000000",
                    "hovered_border": "#5865F2",
                    "selected_border": "#5865F2",
                    "active_border": "#5865F2",
                    "normal_text": "#5865F2",
                    "hovered_text": "#3730A3",
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
                    "bold": "1"
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
                    "border_width": "2",
                    "shadow_width": "0"
                }
            },
            "text_entry_line": {
                "colours": {
                    "normal_bg": "#FFFFFF",
                    "focused_bg": "#FFFFFF",
                    "normal_text": "#FFFFFF",
                    "selected_text": "#000000",
                    "selected_bg": "#5865F2",
                    "normal_border": "#E5E7EB",
                    "focused_border": "#5865F2"
                },
                "misc": {
                    "shape": "rounded_rectangle",
                    "shape_corner_radius": "12",
                    "border_width": "2",
                    "shadow_width": "0",
                    "padding": "12,8"
                },
                "font": {
                    "name": "arial",
                    "size": "16",
                    "bold": "0"
                }
            },
            "label": {
                "colours": {
                    "normal_text": "#374151",
                    "normal_bg": "#00000000"
                },
                "font": {
                    "name": "arial",
                    "size": "14",
                    "bold": "0"
                }
            }
        }
        
        with open('register_theme.json', 'w') as f:
            json.dump(theme_data, f, indent=2)
    
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
                logo_width = int(self.screen.get_width() * 0.25)
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
                logo_width = int(self.screen.get_width() * 0.2)
                logo_height = int(logo_width * (self.subtitle_logo.get_height() / self.subtitle_logo.get_width()))
                self.subtitle_logo = pygame.transform.smoothscale(self.subtitle_logo, (logo_width, logo_height))
                print("✅ 副标题Logo加载成功")
        except Exception as e:
            print(f"⚠️ 副标题Logo加载失败: {e}")
    
    def setup_ui_elements(self):
        """设置UI元素"""
        screen_width, screen_height = self.screen.get_size()
        
        # 计算居中位置
        form_width = int(min(450 * self.scale_factor, screen_width * 0.8))
        center_x = screen_width // 2
        start_y = int(screen_height * 0.35)
        
        # 创建标签和输入框
        # 用户名标签
        username_label_rect = pygame.Rect(center_x - form_width // 2, start_y - 25, form_width, 20)
        self.labels['username'] = pygame_gui.elements.UILabel(
            relative_rect=username_label_rect,
            text='Nombre de usuario',
            manager=self.ui_manager
        )
        
        # 用户名输入框
        username_rect = pygame.Rect(center_x - form_width // 2, start_y, form_width, 
                                   Theme.get_scaled_size('input_height', self.scale_factor))
        self.inputs['username'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=username_rect,
            placeholder_text="Nombre de usuario",
            manager=self.ui_manager
        )
        
        # 密码标签
        password_label_rect = pygame.Rect(center_x - form_width // 2, start_y + 80 - 25, form_width, 20)
        self.labels['password'] = pygame_gui.elements.UILabel(
            relative_rect=password_label_rect,
            text='Contraseña',
            manager=self.ui_manager
        )
        
        # 密码输入框
        password_rect = pygame.Rect(center_x - form_width // 2, start_y + 80, form_width,
                                   Theme.get_scaled_size('input_height', self.scale_factor))
        self.inputs['password'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=password_rect,
            placeholder_text="Contraseña",
            manager=self.ui_manager
        )
        self.inputs['password'].set_text_hidden(True)
        
        # 确认密码标签
        confirm_label_rect = pygame.Rect(center_x - form_width // 2, start_y + 160 - 25, form_width, 20)
        self.labels['confirm_password'] = pygame_gui.elements.UILabel(
            relative_rect=confirm_label_rect,
            text='Confirmar contraseña',
            manager=self.ui_manager
        )
        
        # 确认密码输入框
        confirm_rect = pygame.Rect(center_x - form_width // 2, start_y + 160, form_width,
                                  Theme.get_scaled_size('input_height', self.scale_factor))
        self.inputs['confirm_password'] = pygame_gui.elements.UITextEntryLine(
            relative_rect=confirm_rect,
            placeholder_text="Confirmar contraseña",
            manager=self.ui_manager
        )
        self.inputs['confirm_password'].set_text_hidden(True)
        
        # 创建按钮
        button_width = int(form_width * 0.8)
        register_y = start_y + 260
        register_rect = pygame.Rect(center_x - button_width // 2, register_y, button_width, 
                                   Theme.get_scaled_size('button_height_large', self.scale_factor))
        self.buttons['register'] = pygame_gui.elements.UIButton(
            relative_rect=register_rect,
            text="REGISTRARSE",
            manager=self.ui_manager,
            object_id='#main_button'
        )
        
        login_rect = pygame.Rect(center_x - button_width // 2, register_y + 80, button_width, 30)
        self.buttons['login'] = pygame_gui.elements.UIButton(
            relative_rect=login_rect,
            text="¿Ya tienes una cuenta? Iniciar sesión",
            manager=self.ui_manager,
            object_id='#text_button'
        )
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == pygame.VIDEORESIZE:
            self.handle_resize(event.size)
        
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            self.handle_button_click(event.ui_element)
        
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            # 处理密码强度检查
            if event.ui_element == self.inputs['password']:
                self.update_password_strength(event.text)
        
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            # 处理回车键注册
            if event.ui_element == self.inputs['confirm_password']:
                self.handle_register()
        
        # 处理pygame_gui事件
        self.ui_manager.process_events(event)
        
        return True
    
    def update_password_strength(self, password):
        """更新密码强度提示"""
        if len(password) == 0:
            self.password_strength_text = ""
            self.password_strength_color = (150, 150, 150)
        elif len(password) < 6:
            self.password_strength_text = "Muy débil (mínimo 6 caracteres)"
            self.password_strength_color = (220, 50, 50)
        elif len(password) < 8:
            self.password_strength_text = "Débil"
            self.password_strength_color = (255, 165, 0)
        else:
            # 检查复杂性
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
            
            strength_score = sum([has_upper, has_lower, has_digit, has_special])
            
            if strength_score >= 3:
                self.password_strength_text = "Fuerte"
                self.password_strength_color = (50, 180, 50)
            elif strength_score >= 2:
                self.password_strength_text = "Moderada"
                self.password_strength_color = (255, 200, 0)
            else:
                self.password_strength_text = "Débil"
                self.password_strength_color = (255, 165, 0)
    
    def handle_button_click(self, button):
        """处理按钮点击"""
        if button == self.buttons['register']:
            self.handle_register()
        elif button == self.buttons['login']:
            self.handle_login_switch()
    
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
        
        # 重新加载Logo
        if self.logo:
            self.load_logo()
        if self.subtitle_logo:
            self.load_subtitle_logo()
    
    def clear_ui_elements(self):
        for widget in self.buttons.values():
            widget.kill()
        self.buttons.clear()

        for widget in getattr(self, 'inputs', {}).values():
            widget.kill()
        self.inputs.clear()

        for widget in getattr(self, 'labels', {}).values():
            widget.kill()
        self.labels.clear()

    def handle_register(self):
        """处理注册"""
        username = self.inputs['username'].get_text()
        password = self.inputs['password'].get_text()
        confirm_password = self.inputs['confirm_password'].get_text()
        
        # 简单验证
        if not username.strip():
            self.show_error("Por favor ingresa un nombre de usuario")
            self.inputs['username'].focus()
            return
        
        if len(username) < 3:
            self.show_error("El nombre de usuario debe tener al menos 3 caracteres")
            self.inputs['username'].focus()
            return
        
        if not password.strip():
            self.show_error("Por favor ingresa una contraseña")
            self.inputs['password'].focus()
            return
        
        if len(password) < 6:
            self.show_error("La contraseña debe tener al menos 6 caracteres")
            self.inputs['password'].focus()
            return
        
        if password != confirm_password:
            self.show_error("Las contraseñas no coinciden")
            self.inputs['confirm_password'].focus()
            return
        
        # 调用认证管理器
        success, message = self.auth_manager.register(username, password, confirm_password)
        
        if success:
            # 显示成功消息
            self.toast_message = ToastMessage(message, "success", 2000)
            # 切换到登录页面
            if self.callback:
                self.callback("login")
        else:
            # 显示错误消息
            self.show_error(message)
    
    def show_error(self, message):
        """显示错误消息"""
        self.toast_message = ToastMessage(message, "error", 3000)
    
    def handle_login_switch(self):
        """切换到登录页面"""
        print("🔄 切换到登录页面")
        if self.callback:
            self.callback("login")
    
    def update(self, dt):
        """更新场景"""
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
        self.ui_manager.draw_ui(self.screen)
        
        # 绘制密码强度提示
        self.draw_password_strength()
        
        # 绘制消息
        self.message_manager.draw(self.screen, self.scale_factor)
        
        # 绘制Toast消息
        if self.toast_message:
            screen_width, screen_height = self.screen.get_size()
            self.toast_message.draw(self.screen, screen_width // 2, int(screen_height * 0.8), self.scale_factor)
    
    def draw_password_strength(self):
        """绘制密码强度提示"""
        if self.password_strength_text:
            screen_width, screen_height = self.screen.get_size()
            form_width = int(min(450 * self.scale_factor, screen_width * 0.8))
            center_x = screen_width // 2
            start_y = int(screen_height * 0.35)
            
            # 在密码输入框下方显示强度
            text_y = start_y + 80 + Theme.get_scaled_size('input_height', self.scale_factor) + 5
            
            text_surface = font_manager.render_text(
                self.password_strength_text, 'sm', screen_height, self.password_strength_color
            )
            text_rect = text_surface.get_rect(topleft=(center_x - form_width // 2, text_y))
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
            logo_rect = self.logo.get_rect(center=(screen_width // 2, int(screen_height * 0.15)))
            self.screen.blit(self.logo, logo_rect)
        else:
            # 文字标题作为后备
            title_color = Theme.get_color('text_white')
            title_surface = font_manager.render_text(
                "Crear Cuenta", '2xl', screen_height, title_color
            )
            title_rect = title_surface.get_rect(center=(screen_width // 2, int(screen_height * 0.15)))
            self.screen.blit(title_surface, title_rect)
    
    def draw_subtitle(self):
        """绘制副标题"""
        screen_width, screen_height = self.screen.get_size()
        
        if self.subtitle_logo:
            # 使用图片
            logo_rect = self.subtitle_logo.get_rect(center=(screen_width // 2, int(screen_height * 0.26)))
            self.screen.blit(self.subtitle_logo, logo_rect)
        else:
            # 文字后备方案
            subtitle_text = "Juego de Cartas Coleccionables"
            text_color = Theme.get_color('text_white')
            text_surface = font_manager.render_text(subtitle_text, 'md', screen_height, text_color)
            
            # 位置
            text_rect = text_surface.get_rect(center=(screen_width // 2, int(screen_height * 0.26)))
            
            # 简化的背景
            padding = Theme.get_scaled_size('spacing_lg', self.scale_factor)
            bg_rect = text_rect.inflate(padding * 2, Theme.get_scaled_size('spacing_md', self.scale_factor))
            
            # 绘制简单背景
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((220, 50, 50, 150))  # 半透明红色
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
            os.remove('register_theme.json')
        except:
            pass
            
        print("✅ 注册场景资源清理完成")
    
    def run(self):
        """运行场景的主循环（独立运行时使用）"""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            dt = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if not self.handle_event(event):
                    return
            
            if not self.update(dt):
                return
            
            self.draw()
            pygame.display.flip()
        
        self.cleanup()