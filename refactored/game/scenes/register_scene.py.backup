"""
重构后的现代化注册场景
使用组件化设计和统一样式
"""

import pygame
import pygame_gui
import sys
import os

# 导入核心模块
from game.core.auth.auth_manager import AuthManager
from game.scenes.components.button_component import ModernButton
from game.scenes.components.input_component import ModernInput, PasswordStrengthIndicator
from game.scenes.components.message_component import MessageManager, ToastMessage
from game.scenes.animations.transitions import FadeTransition
from game.scenes.styles.theme import Theme
from game.scenes.styles.fonts import font_manager
from game.utils.video_background import VideoBackground

class RegisterScene:
    """现代化注册场景类，使用统一的组件系统"""
    
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
        
        # 初始化pygame-gui
        self.ui_manager = pygame_gui.UIManager(screen.get_size())
        self.setup_ui_theme()
        
        # 组件管理器
        self.message_manager = MessageManager()
        # self.transition_manager = FadeTransition(screen)
        
        # UI组件
        self.inputs = {}
        self.buttons = {}
        self.password_strength = None
        self.toast_message = None
        
        # 背景
        self.background_surface = None
        self.video_background = None
        self.setup_background()
        
        # Logo
        self.logo = None
        self.load_logo()
        
        # 设置UI元素
        self.setup_ui_elements()
        
        # # 开始淡入动画
        # self.transition_manager.start_fade_in()

        # # 使用传入的转换管理器，如果没有就创建自己的
        # if transition_manager:
        #     self.transition_manager = transition_manager
        #     print("🔗 使用共享转换管理器")
        # else:
        #     self.transition_manager = FadeTransition(screen)
        #     print("🆕 创建新的转换管理器")

    def setup_ui_theme(self):
        """设置现代UI主题"""
        self.ui_manager.get_theme().load_theme(Theme.UI_THEME_DATA)
    
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
    
    def setup_ui_elements(self):
        """设置UI元素"""
        screen_width, screen_height = self.screen.get_size()
        
        # 计算居中位置
        form_width = int(min(450 * self.scale_factor, screen_width * 0.8))
        center_x = screen_width // 2
        start_y = int(screen_height * 0.35)
        
        # 创建输入框
        username_rect = pygame.Rect(center_x - form_width // 2, start_y, form_width, 
                                   Theme.get_scaled_size('input_height', self.scale_factor))
        self.inputs['username'] = ModernInput(
            username_rect, 
            placeholder="Nombre de usuario",
            label="Nombre de usuario",
            ui_manager=self.ui_manager
        )
        
        password_rect = pygame.Rect(center_x - form_width // 2, start_y + 80, form_width,
                                   Theme.get_scaled_size('input_height', self.scale_factor))
        self.inputs['password'] = ModernInput(
            password_rect,
            placeholder="Contraseña",
            label="Contraseña", 
            is_password=True,
            ui_manager=self.ui_manager
        )
        
        # 创建密码强度指示器
        self.password_strength = PasswordStrengthIndicator(self.inputs['password'])
        
        # 确认密码输入框（位置会根据密码强度条动态调整）
        confirm_y = start_y + 160  # 基础位置
        confirm_rect = pygame.Rect(center_x - form_width // 2, confirm_y, form_width,
                                  Theme.get_scaled_size('input_height', self.scale_factor))
        self.inputs['confirm_password'] = ModernInput(
            confirm_rect,
            placeholder="Confirmar contraseña",
            label="Confirmar contraseña",
            is_password=True,
            ui_manager=self.ui_manager
        )
        
        # 创建按钮
        button_width = int(form_width * 0.8)
        register_y = confirm_y + 100
        register_rect = pygame.Rect(center_x - button_width // 2, register_y, button_width, 
                                   Theme.get_scaled_size('button_height_large', self.scale_factor))
        self.buttons['register'] = ModernButton(
            register_rect,
            text="REGISTRARSE",
            icon="",
            button_type="primary",
            font_size="lg"
        )
        
        login_rect = pygame.Rect(center_x - button_width // 2, register_y + 80, button_width, 30)
        self.buttons['login'] = ModernButton(
            login_rect,
            text="¿Ya tienes una cuenta? Iniciar sesión",
            button_type="text",
            font_size="md"
        )
    
    def update_layout_for_password_strength(self):
        """根据密码强度条显示状态更新布局"""
        if not self.password_strength.visible:
            return
        
        screen_width, screen_height = self.screen.get_size()
        center_x = screen_width // 2
        form_width = int(min(450 * self.scale_factor, screen_width * 0.8))
        button_width = int(form_width * 0.8)
        
        # 密码强度条高度
        strength_height = self.password_strength.get_height()
        
        # 重新定位确认密码输入框
        new_confirm_y = self.inputs['password'].rect.bottom + strength_height + Theme.get_scaled_size('spacing_md', self.scale_factor)
        
        # 更新确认密码输入框位置
        old_text = self.inputs['confirm_password'].get_text()
        self.inputs['confirm_password'].kill()
        
        confirm_rect = pygame.Rect(center_x - form_width // 2, new_confirm_y, form_width,
                                  Theme.get_scaled_size('input_height', self.scale_factor))
        self.inputs['confirm_password'] = ModernInput(
            confirm_rect,
            placeholder="Confirmar contraseña",
            label="Confirmar contraseña",
            is_password=True,
            ui_manager=self.ui_manager
        )
        self.inputs['confirm_password'].set_text(old_text)
        
        # 更新按钮位置
        new_register_y = new_confirm_y + 100
        self.buttons['register'].set_position(center_x - button_width // 2, new_register_y)
        self.buttons['login'].set_position(center_x - button_width // 2, new_register_y + 80)
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == pygame.VIDEORESIZE:
            self.handle_resize(event.size)
        
        elif event.type == pygame.MOUSEMOTION:
            # 更新按钮悬停状态
            for button in self.buttons.values():
                button.update_hover(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_mouse_click(event.pos)
        
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            # 处理密码输入变化
            if event.ui_element == self.inputs['password'].ui_element:
                password = event.text
                old_visible = self.password_strength.visible
                self.password_strength.update_strength(password)
                
                # 如果密码强度指示器显示状态改变，更新布局
                if old_visible != self.password_strength.visible:
                    self.update_layout_for_password_strength()
        
        # # 处理输入框事件
        # for input_comp in self.inputs.values():
        #     input_comp.handle_event(event)
        
        # 处理pygame-gui事件
        self.ui_manager.process_events(event)
        
        return True
    
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
    
    def handle_mouse_click(self, mouse_pos):
        """处理鼠标点击"""
        # 检查按钮点击
        if self.buttons['register'].is_clicked(mouse_pos, 1):
            self.buttons['register'].trigger_flash()
            self.handle_register()
        elif self.buttons['login'].is_clicked(mouse_pos, 1):
            self.buttons['login'].trigger_flash()
            self.handle_login_switch()
    
    def handle_register(self):
        """处理注册"""
        username = self.inputs['username'].ui_element.get_text()
        password = self.inputs['password'].ui_element.get_text()
        confirm_password = self.inputs['confirm_password'].ui_element.get_text()
        
        # 清除之前的错误
        for input_comp in self.inputs.values():
            input_comp.clear_error()
        
        success, message = self.auth_manager.register(username, password, confirm_password)
        
        if success:
            # 显示成功消息
            self.toast_message = ToastMessage(message, "success", 2000)
            # 开始淡出转换到登录页面
            if self.callback:
                self.callback("login")
        else:
            # 显示错误消息
            self.toast_message = ToastMessage(message, "error", 3000)
            
            # 根据错误类型设置输入框错误状态
            if "usuario" in message.lower():
                self.inputs['username'].set_error("Nombre de usuario inválido")
            elif "contraseña" in message.lower() and "coinciden" in message.lower():
                self.inputs['confirm_password'].set_error("Las contraseñas no coinciden")
            elif "contraseña" in message.lower():
                self.inputs['password'].set_error("Contraseña inválida")
    
    def handle_login_switch(self):
        """切换到登录页面"""
        print("🔄 切换到登录页面")
        if self.callback:
            self.callback("login")
    
    def update(self, dt):
        """更新场景"""
        # 更新pygame-gui
        self.ui_manager.update(dt)
        
        # # 更新转换动画
        # if not self.transition_manager.update(dt):
        #     return False
        
        # 更新按钮动画
        for button in self.buttons.values():
            button.update_animation(dt)
        
        # 更新输入框
        for input_comp in self.inputs.values():
            input_comp.update(dt)
        
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
        
        # 绘制输入框背景
        for input_comp in self.inputs.values():
            input_comp.draw_background(self.screen, self.scale_factor)
        
        # 绘制密码强度指示器
        self.password_strength.draw(self.screen, self.scale_factor)
        
        # 绘制pygame-gui元素（输入框）
        self.ui_manager.draw_ui(self.screen)
        
        # 绘制按钮
        for button in self.buttons.values():
            button.draw(self.screen, self.scale_factor)
        
        # 绘制消息
        self.message_manager.draw(self.screen, self.scale_factor)
        
        # 绘制Toast消息
        if self.toast_message:
            screen_width, screen_height = self.screen.get_size()
            self.toast_message.draw(self.screen, screen_width // 2, int(screen_height * 0.8), self.scale_factor)
        
        # 绘制转换效果
        # self.transition_manager.draw()
    
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
        """绘制现代化副标题"""
        screen_width, screen_height = self.screen.get_size()
        
        # 副标题文字
        subtitle_text = "Juego de Cartas Coleccionables"
        text_color = Theme.get_color('text_white')
        text_surface = font_manager.render_text(subtitle_text, 'md', screen_height, text_color)
        
        # 位置
        text_rect = text_surface.get_rect(center=(screen_width // 2, int(screen_height * 0.26)))
        
        # 现代化背景条
        padding = Theme.get_scaled_size('spacing_lg', self.scale_factor)
        bg_rect = text_rect.inflate(padding * 2, Theme.get_scaled_size('spacing_md', self.scale_factor))
        
        # 绘制毛玻璃背景
        self.draw_glass_background(bg_rect)
        
        # 绘制文字
        shadow_color = (100, 20, 20)
        shadow_surface = font_manager.render_text(subtitle_text, 'md', screen_height, shadow_color)
        self.screen.blit(shadow_surface, text_rect.move(2, 2))
        self.screen.blit(text_surface, text_rect)
    
    def draw_glass_background(self, rect):
        """绘制毛玻璃背景"""
        radius = Theme.get_scaled_size('border_radius_medium', self.scale_factor)
        
        # 阴影
        shadow_rect = rect.move(4, 4)
        self.draw_rounded_rect_alpha(shadow_rect, radius, (0, 0, 0, 40))
        
        # 主背景 - 红色渐变
        bg_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        for y in range(rect.height):
            progress = y / rect.height
            r = int(220 * (1 - progress * 0.2))
            g = int(50 * (1 - progress * 0.1))
            b = int(50 * (1 - progress * 0.1))
            pygame.draw.line(bg_surface, (r, g, b), (0, y), (rect.width, y))
        
        # 应用圆角
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, rect.width, rect.height), border_radius=radius)
        
        final_bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        final_bg.blit(bg_surface, (0, 0))
        final_bg.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        self.screen.blit(final_bg, rect.topleft)
        
        # 顶部高光
        highlight_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height // 2)
        self.draw_rounded_rect_alpha(highlight_rect, radius - 2, (255, 255, 255, 40))
    
    def draw_rounded_rect_alpha(self, rect, radius, color):
        """绘制带透明度的圆角矩形"""
        if len(color) == 4:
            surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(surface, color, (0, 0, rect.width, rect.height), border_radius=radius)
            self.screen.blit(surface, rect.topleft)
        else:
            pygame.draw.rect(self.screen, color, rect, border_radius=radius)
    
    def cleanup(self):
        """清理资源"""
        # 清理输入框
        for input_comp in self.inputs.values():
            input_comp.kill()
        
        # 清理视频背景
        if self.video_background:
            self.video_background.close()
    
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