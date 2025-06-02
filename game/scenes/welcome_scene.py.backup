"""
引导欢迎场景
包含登录、注册、退出三个选项的主入口页面
"""

import pygame
import pygame_gui
import math
import sys
import os

# 导入组件和样式
from game.scenes.components.button_component import ModernButton
from game.scenes.components.message_component import MessageManager, ToastMessage
# from game.scenes.animations.transitions import FadeTransition
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
        
        # 组件管理器
        self.message_manager = MessageManager()
        # self.transition_manager = FadeTransition(screen)
        
        # UI组件
        self.buttons = {}
        self.toast_message = None

        # 确认退出对话框状态
        self.show_exit_dialog = False
        self.exit_dialog_buttons = {}  # 👈 添加这行
        
        # 背景
        self.background_surface = None
        self.video_background = None
        self.setup_background()
        
        # Logo
        self.logo = None
        self.load_logo()
        
        # 引导层状态
        self.show_intro = True
        self.intro_alpha = 255
        self.intro_time = 0
        self.transition_intro = False
        self.get_to_daze_text = "Presiona cualquier tecla para comenzar"

        # 按钮动画状态
        self.buttons_animation_started = False
        self.buttons_animation_progress = 0.0
        self.button_offsets = {}  # 存储每个按钮的偏移量

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
        
        print("✅ 欢迎场景初始化完成")
    
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
        self.buttons['login'] = ModernButton(
            login_rect,
            text="INICIAR SESIÓN",
            icon="",
            button_type="primary",
            font_size="lg"
        )
        
        register_rect = pygame.Rect(center_x - button_width // 2, start_y + button_spacing, button_width, button_height)
        self.buttons['register'] = ModernButton(
            register_rect,
            text="CREAR CUENTA",
            icon="",
            button_type="secondary",
            font_size="lg"
        )
        
        exit_rect = pygame.Rect(center_x - button_width // 2, start_y + button_spacing * 2, button_width, button_height)
        self.buttons['exit'] = ModernButton(
            exit_rect,
            text="SALIR",
            icon="",
            button_type="secondary",
            font_size="lg"
        )
        
        # 设置按钮初始偏移（从下方飞入）
        screen_height = self.screen.get_height()
        self.button_offsets = {
            'login': screen_height,      # 登录按钮从最下方
            'register': screen_height + 50,  # 注册按钮稍微延迟
            'exit': screen_height + 100      # 退出按钮最后出现
        }

        # 退出确认对话框按钮（初始化但不显示）
        self.setup_exit_dialog_buttons()
    
    def setup_exit_dialog_buttons(self):
        """设置退出确认对话框按钮"""
        screen_width, screen_height = self.screen.get_size()
        
        dialog_width = int(min(500 * self.scale_factor, screen_width * 0.8))
        dialog_height = int(min(250 * self.scale_factor, screen_height * 0.45))
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2
        
        button_width = int(dialog_width * 0.35)
        button_height = Theme.get_scaled_size('button_height_medium', self.scale_factor)
        button_y = dialog_y + dialog_height - button_height - 20
        
        # 确认退出按钮
        yes_rect = pygame.Rect(dialog_x + 20, button_y, button_width, button_height)
        self.exit_dialog_buttons['yes'] = ModernButton(
            yes_rect,
            text="SÍ, SALIR",
            button_type="primary",
            font_size="md"
        )
        
        # 取消按钮
        no_rect = pygame.Rect(dialog_x + dialog_width - button_width - 20, button_y, button_width, button_height)
        self.exit_dialog_buttons['no'] = ModernButton(
            no_rect,
            text="CANCELAR",
            button_type="secondary",
            font_size="md"
        )
    
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
                return True
            else:
                return False
        
        elif event.type == pygame.VIDEORESIZE:
            self.handle_resize(event.size)
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.show_exit_dialog:
                    self.show_exit_dialog = False
                else:
                    self.show_exit_dialog = True
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            # 更新按钮悬停状态
            if self.show_exit_dialog:
                for button in self.exit_dialog_buttons.values():
                    button.update_hover(event.pos)
            else:
                for button in self.buttons.values():
                    button.update_hover(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_mouse_click(event.pos)
        
        return True
    
    def handle_resize(self, new_size):
        """处理窗口大小变化"""
        self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
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
        if self.show_exit_dialog:
            # 处理退出对话框按钮点击
            if self.exit_dialog_buttons['yes'].is_clicked(mouse_pos, 1):
                self.exit_dialog_buttons['yes'].trigger_flash()
                self.handle_exit_confirm()
            elif self.exit_dialog_buttons['no'].is_clicked(mouse_pos, 1):
                self.exit_dialog_buttons['no'].trigger_flash()
                self.handle_exit_cancel()
        elif not self.show_intro and self.buttons_animation_progress > 0.8:  # 动画基本完成后才能点击
            # 调整鼠标位置以匹配按钮动画偏移
            adjusted_mouse_pos = list(mouse_pos)
            
            for button_name, button in self.buttons.items():
                if button_name in self.button_offsets:
                    offset_y = self.button_offsets[button_name]
                    adjusted_rect = button.rect.copy()
                    adjusted_rect.y += int(offset_y)
                    
                    if adjusted_rect.collidepoint(mouse_pos):
                        if button_name == 'login':
                            button.trigger_flash()
                            self.handle_login_click()
                        elif button_name == 'register':
                            button.trigger_flash()
                            self.handle_register_click()
                        elif button_name == 'exit':
                            button.trigger_flash()
                            self.handle_exit_click()
                        break
    
    def handle_login_click(self):
        """处理登录按钮点击"""
        print("🔐 用户点击登录按钮")
        # 直接调用回调，不需要复杂的转换逻辑
        if self.callback:
            self.callback("login")

    def handle_register_click(self):
        """处理注册按钮点击"""
        print("✨ 用户点击注册按钮")
        # 直接调用回调
        if self.callback:
            self.callback("register")
    
    def handle_exit_click(self):
        """处理退出按钮点击"""
        print("🚪 用户点击退出按钮")
        self.show_exit_dialog = True
    
    def handle_exit_confirm(self):
        """处理确认退出"""
        print("✅ 用户确认退出游戏")
        # 直接执行退出，不要Toast延迟
        if self.callback:
            self.callback("exit")
    
    def handle_exit_cancel(self):
        """处理取消退出"""
        print("❌ 用户取消退出")
        self.show_exit_dialog = False
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
                    self.buttons_animation_started = True  # 开始按钮动画
            
            return True
        
        # 更新按钮飞入动画
        if self.buttons_animation_started and self.buttons_animation_progress < 1.0:
            # 使用easeOutBack缓动函数
            animation_speed = 2.5  # 动画速度
            self.buttons_animation_progress = min(1.0, self.buttons_animation_progress + dt * animation_speed)
            
            # 计算每个按钮的当前偏移
            for button_name in self.button_offsets:
                # 添加延迟效果
                delay_factor = {'login': 0.0, 'register': 0.1, 'exit': 0.2}[button_name]
                progress = max(0, self.buttons_animation_progress - delay_factor)
                progress = min(1.0, progress / (1.0 - delay_factor)) if delay_factor < 1.0 else progress
                
                # easeOutBack缓动
                if progress > 0:
                    c1 = 1.70158
                    c3 = c1 + 1
                    eased = 1 + c3 * pow(progress - 1, 3) + c1 * pow(progress - 1, 2)
                    self.button_offsets[button_name] = self.screen.get_height() * (1 - eased)
                else:
                    self.button_offsets[button_name] = self.screen.get_height()
        
        # 原有的其他更新逻辑...
        if self.show_exit_dialog:
            for button in self.exit_dialog_buttons.values():
                button.update_animation(dt)
        else:
            for button in self.buttons.values():
                button.update_animation(dt)
    

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
        
        # 绘制按钮（带飞入动画）
        if not self.show_exit_dialog and not self.show_intro:
            self.draw_animated_buttons()
        
        # 绘制引导层文字
        if self.show_intro:
            self.draw_intro_text()
        
        # 绘制退出确认对话框
        if self.show_exit_dialog:
            self.draw_exit_dialog()
        
        # 绘制消息
        self.message_manager.draw(self.screen, self.scale_factor)
        
        # 绘制Toast消息
        if self.toast_message:
            screen_width, screen_height = self.screen.get_size()
            self.toast_message.draw(self.screen, screen_width // 2, int(screen_height * 0.85), self.scale_factor)

    def draw_animated_buttons(self):
        """绘制带动画的按钮"""
        for button_name, button in self.buttons.items():
            if button_name in self.button_offsets:
                # 计算按钮当前位置
                offset_y = self.button_offsets[button_name]
                
                # 如果按钮还在屏幕外，不绘制
                if offset_y >= self.screen.get_height():
                    continue
                
                # 临时修改按钮位置
                original_y = button.rect.y
                button.rect.y += int(offset_y)
                
                # 绘制按钮
                button.draw(self.screen, self.scale_factor)
                
                # 恢复原始位置（用于事件处理）
                button.rect.y = original_y

    def draw_intro_text(self):
        """绘制引导文字（不要覆盖层）"""
        screen_width, screen_height = self.screen.get_size()
        
        # 在按钮位置显示引导文字
        start_y = int(screen_height * 0.55)
        text_y = start_y + 60
        
        text_color = (255, 255, 255)
        text_surface = font_manager.render_text(
            self.get_to_daze_text, 'xl', screen_height, text_color
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
        """绘制现代化副标题"""
        screen_width, screen_height = self.screen.get_size()
        
        # 副标题文字
        subtitle_text = "JUEGO DE CARTAS COLECCIONABLES"
        text_color = Theme.get_color('text_white')
        text_surface = font_manager.render_text(subtitle_text, 'lg', screen_height, text_color)
        
        # 位置
        text_rect = text_surface.get_rect(center=(screen_width // 2, int(screen_height * 0.4)))
        
        # 现代化背景条
        padding = Theme.get_scaled_size('spacing_xl', self.scale_factor)
        bg_rect = text_rect.inflate(padding * 2, Theme.get_scaled_size('spacing_lg', self.scale_factor))
        
        # 绘制毛玻璃背景
        self.draw_glass_background(bg_rect)
        
        # 绘制文字
        shadow_color = (0, 0, 0, 120)
        shadow_surface = font_manager.render_text(subtitle_text, 'lg', screen_height, shadow_color[:3])
        self.screen.blit(shadow_surface, text_rect.move(2, 2))
        self.screen.blit(text_surface, text_rect)
    
    def draw_exit_dialog(self):
        """绘制退出确认对话框"""
        screen_width, screen_height = self.screen.get_size()
        
        # 对话框尺寸
        dialog_width = int(min(400 * self.scale_factor, screen_width * 0.7))
        dialog_height = int(min(200 * self.scale_factor, screen_height * 0.4))
        dialog_x = (screen_width - dialog_width) // 2
        dialog_y = (screen_height - dialog_height) // 2
        dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
        
        # 半透明覆盖层
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # 对话框背景
        self.draw_glass_background(dialog_rect, opacity=240)
        
        # 对话框边框
        pygame.draw.rect(self.screen, Theme.get_color('border'), dialog_rect, 2, 
                        border_radius=Theme.get_scaled_size('border_radius_large', self.scale_factor))
        
        # 标题
        title_text = "Confirmar salida"
        title_color = Theme.get_color('text')
        title_surface = font_manager.render_text(title_text, 'xl', screen_height, title_color)
        title_rect = title_surface.get_rect(center=(dialog_rect.centerx, dialog_y + 40))
        self.screen.blit(title_surface, title_rect)
        
        # 消息文本
        message_text = "¿Estás seguro de que quieres salir del juego?"
        message_color = Theme.get_color('text_secondary')
        message_surface = font_manager.render_text(message_text, 'md', screen_height, message_color)
        message_rect = message_surface.get_rect(center=(dialog_rect.centerx, dialog_y + 90))
        self.screen.blit(message_surface, message_rect)
        
        # 绘制对话框按钮
        for button in self.exit_dialog_buttons.values():
            button.draw(self.screen, self.scale_factor)
    
    def draw_glass_background(self, rect, opacity=200):
        """绘制毛玻璃背景"""
        radius = Theme.get_scaled_size('border_radius_large', self.scale_factor)
        
        # 阴影
        shadow_rect = rect.move(6, 6)
        self.draw_rounded_rect_alpha(shadow_rect, radius, (0, 0, 0, 60))
        
        # 主背景 - 渐变效果
        bg_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        for y in range(rect.height):
            progress = y / rect.height
            alpha = int(opacity * (1 - progress * 0.3))
            r = int(255 * (1 - progress * 0.1))
            g = int(255 * (1 - progress * 0.05))
            b = int(255 * (1 - progress * 0.05))
            pygame.draw.line(bg_surface, (r, g, b, alpha), (0, y), (rect.width, y))
        
        # 应用圆角
        mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, rect.width, rect.height), border_radius=radius)
        
        final_bg = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        final_bg.blit(bg_surface, (0, 0))
        final_bg.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        self.screen.blit(final_bg, rect.topleft)
        
        # 顶部高光
        highlight_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height // 3)
        self.draw_rounded_rect_alpha(highlight_rect, radius - 2, (255, 255, 255, 50))
    
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
        # 清理视频背景
        if self.video_background:
            self.video_background.close()
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