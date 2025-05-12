import pygame
import pygame.freetype
import sys
import os

# 导入核心模块
from game.core.auth_manager import AuthManager

class LoginScene:
    """
    登录场景类，处理用户登录界面和逻辑
    """
    
    def __init__(self, screen, callback=None):
        """
        初始化登录场景
        
        Args:
            screen: pygame屏幕对象
            callback: 登录成功后的回调函数
        """
        self.screen = screen
        self.callback = callback
        self.auth_manager = AuthManager()
        
        # 颜色定义
        self.colors = {
            'background': (30, 30, 60),
            'button': (86, 62, 139),
            'button_hover': (106, 82, 159),
            'button_text': (255, 255, 255),
            'input_bg': (255, 255, 255, 220),
            'input_text': (20, 20, 20),
            'error': (255, 80, 80),
            'success': (80, 255, 80),
            'title': (255, 255, 255),
            'link': (150, 150, 255),
            'link_hover': (200, 200, 255)
        }
        
        # 加载字体
        self.fonts = self.load_fonts()
        
        # 输入框和按钮状态
        self.input_boxes = {
            'username': pygame.Rect(0, 0, 300, 50),
            'password': pygame.Rect(0, 0, 300, 50)
        }
        self.buttons = {
            'login': pygame.Rect(0, 0, 200, 60),
            'register_link': pygame.Rect(0, 0, 200, 40)
        }
        
        # 动态调整UI元素位置
        self.adjust_ui_positions()
        
        # 输入框状态
        self.active_input = None
        self.username = ""
        self.password = ""
        self.show_password = False
        
        # 按钮悬停状态
        self.button_hover = None
        
        # 消息状态
        self.message = None
        self.message_type = None  # 'error' 或 'success'
        
        # 注册链接状态
        self.register_link_hover = False
        
        # 创建返回键盘事件的字典
        self.key_handlers = {
            pygame.K_RETURN: self.handle_return,
            pygame.K_BACKSPACE: self.handle_backspace,
            pygame.K_TAB: self.handle_tab
        }
        
        # 加载背景图（如果有）
        self.background = None
        try:
            bg_path = os.path.join("assets", "images", "backgrounds", "login_bg.jpg")
            self.background = pygame.image.load(bg_path)
            self.background = pygame.transform.scale(self.background, screen.get_size())
        except Exception as e:
            print(f"无法加载背景图: {e}")
            
        # 加载Logo（如果有）
        self.logo = None
        try:
            logo_path = os.path.join("assets", "images", "logo", "game_logo.png")
            self.logo = pygame.image.load(logo_path)
            logo_width = self.screen.get_width() * 0.4
            logo_height = logo_width * (self.logo.get_height() / self.logo.get_width())
            self.logo = pygame.transform.scale(self.logo, (int(logo_width), int(logo_height)))
            self.logo_rect = self.logo.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() * 0.2))
        except Exception as e:
            print(f"无法加载Logo: {e}")
    
    def load_fonts(self):
        """加载字体"""
        fonts = {}
        try:
            font_path = os.path.join("assets", "fonts", "power-clear.ttf")
            # 如果字体文件存在，使用它
            if os.path.exists(font_path):
                fonts['title'] = pygame.font.Font(font_path, 40)
                fonts['input'] = pygame.font.Font(font_path, 24)
                fonts['button'] = pygame.font.Font(font_path, 28)
                fonts['message'] = pygame.font.Font(font_path, 22)
                fonts['link'] = pygame.font.Font(font_path, 20)
            else:
                # 否则使用系统字体
                fonts['title'] = pygame.font.SysFont("arial", 40, bold=True)
                fonts['input'] = pygame.font.SysFont("arial", 24)
                fonts['button'] = pygame.font.SysFont("arial", 28, bold=True)
                fonts['message'] = pygame.font.SysFont("arial", 22)
                fonts['link'] = pygame.font.SysFont("arial", 20)
        except Exception as e:
            print(f"加载字体出错: {e}")
            # 使用系统字体作为后备
            fonts['title'] = pygame.font.SysFont("arial", 40, bold=True)
            fonts['input'] = pygame.font.SysFont("arial", 24)
            fonts['button'] = pygame.font.SysFont("arial", 28, bold=True)
            fonts['message'] = pygame.font.SysFont("arial", 22)
            fonts['link'] = pygame.font.SysFont("arial", 20)
        
        return fonts
    
    def adjust_ui_positions(self):
        """根据屏幕尺寸调整UI元素位置"""
        w, h = self.screen.get_size()
        
        # 居中输入框
        center_x = w // 2
        username_y = int(h * 0.4)
        password_y = username_y + 80
        
        # 输入框位置和大小
        input_width = min(400, int(w * 0.8))
        self.input_boxes['username'].width = input_width
        self.input_boxes['username'].height = 50
        self.input_boxes['username'].center = (center_x, username_y)
        
        self.input_boxes['password'].width = input_width
        self.input_boxes['password'].height = 50
        self.input_boxes['password'].center = (center_x, password_y)
        
        # 登录按钮位置和大小
        button_width = min(300, int(w * 0.6))
        self.buttons['login'].width = button_width
        self.buttons['login'].height = 60
        self.buttons['login'].center = (center_x, password_y + 100)
        
        # 注册链接位置
        self.buttons['register_link'].width = 200
        self.buttons['register_link'].height = 40
        self.buttons['register_link'].center = (center_x, password_y + 170)
    
    def handle_event(self, event):
        """
        处理pygame事件
        
        Args:
            event: pygame事件对象
        
        Returns:
            布尔值表示是否继续运行场景
        """
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        elif event.type == pygame.VIDEORESIZE:
            # 窗口大小改变时调整UI
            self.adjust_ui_positions()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # 检查点击的位置
            return self.handle_mouse_click(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            # 更新悬停状态
            self.update_hover_states(event.pos)
        
        elif event.type == pygame.KEYDOWN:
            # 处理键盘输入
            if event.key in self.key_handlers:
                self.key_handlers[event.key]()
            elif self.active_input:
                self.handle_text_input(event)
        
        return True
    
    def handle_mouse_click(self, pos):
        """处理鼠标点击事件"""
        # 检查输入框点击
        for input_name, input_rect in self.input_boxes.items():
            if input_rect.collidepoint(pos):
                self.active_input = input_name
                return True
        
        # 点击其他地方时取消输入框焦点
        self.active_input = None
        
        # 检查登录按钮点击
        if self.buttons['login'].collidepoint(pos):
            success, message = self.auth_manager.login(self.username, self.password)
            self.message = message
            self.message_type = 'success' if success else 'error'
            
            if success and self.callback:
                # 登录成功，调用回调函数
                self.callback(self.auth_manager.get_current_user_id())
                return False  # 不再继续此场景
            
            return True
        
        # 检查注册链接点击
        if self.buttons['register_link'].collidepoint(pos):
            # 切换到注册场景（通过回调函数）
            if self.callback:
                self.callback("register")
                return False  # 不再继续此场景
        
        return True
    
    def update_hover_states(self, pos):
        """更新按钮和链接的悬停状态"""
        # 检查登录按钮悬停
        self.button_hover = self.buttons['login'].collidepoint(pos)
        
        # 检查注册链接悬停
        self.register_link_hover = self.buttons['register_link'].collidepoint(pos)
    
    def handle_text_input(self, event):
        """处理文本输入"""
        # 忽略不可打印的字符
        if event.unicode.isprintable():
            if self.active_input == 'username':
                self.username += event.unicode
            elif self.active_input == 'password':
                self.password += event.unicode
    
    def handle_return(self):
        """处理回车键"""
        if self.active_input == 'username':
            # 从用户名移动到密码输入框
            self.active_input = 'password'
        elif self.active_input == 'password':
            # 触发登录操作
            success, message = self.auth_manager.login(self.username, self.password)
            self.message = message
            self.message_type = 'success' if success else 'error'
            
            if success and self.callback:
                # 登录成功，调用回调函数
                self.callback(self.auth_manager.get_current_user_id())
                return False  # 不再继续此场景
    
    def handle_backspace(self):
        """处理退格键"""
        if self.active_input == 'username':
            self.username = self.username[:-1]
        elif self.active_input == 'password':
            self.password = self.password[:-1]
    
    def handle_tab(self):
        """处理Tab键切换输入框"""
        if self.active_input == 'username':
            self.active_input = 'password'
        elif self.active_input == 'password':
            self.active_input = 'username'
        else:
            self.active_input = 'username'
    
    def draw_text_input(self, rect, text, active, is_password=False):
        """绘制文本输入框"""
        # 绘制输入框背景
        pygame.draw.rect(self.screen, self.colors['input_bg'], rect, border_radius=10)
        
        # 如果输入框处于活动状态，绘制高亮边框
        border_color = self.colors['button'] if active else (100, 100, 100)
        pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=10)
        
        # 处理密码遮蔽
        display_text = text
        if is_password and not self.show_password:
            display_text = '*' * len(text)
        
        # 渲染文本
        if text:
            text_surface = self.fonts['input'].render(display_text, True, self.colors['input_text'])
            # 将文本放置在输入框内，保持一定的内边距
            text_rect = text_surface.get_rect(midleft=(rect.x + 15, rect.centery))
            self.screen.blit(text_surface, text_rect)
    
    def draw_button(self, rect, text, hover=False):
        """绘制按钮"""
        # 绘制按钮背景
        color = self.colors['button_hover'] if hover else self.colors['button']
        pygame.draw.rect(self.screen, color, rect, border_radius=15)
        
        # 绘制按钮文本
        text_surface = self.fonts['button'].render(text, True, self.colors['button_text'])
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def draw_link(self, rect, text, hover=False):
        """绘制链接文本"""
        color = self.colors['link_hover'] if hover else self.colors['link']
        text_surface = self.fonts['link'].render(text, True, color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
        # 绘制下划线
        start_pos = (text_rect.left, text_rect.bottom)
        end_pos = (text_rect.right, text_rect.bottom)
        pygame.draw.line(self.screen, color, start_pos, end_pos, 1)
    
    def draw(self):
        """绘制场景"""
        # 绘制背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.colors['background'])
        
        # 绘制Logo
        if self.logo:
            self.screen.blit(self.logo, self.logo_rect)
        
        # 绘制标题
        if not self.logo:
            title_surface = self.fonts['title'].render("Inicio de Sesión", True, self.colors['title'])
            title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() * 0.2))
            self.screen.blit(title_surface, title_rect)
        
        # 绘制用户名标签
        username_label = self.fonts['input'].render("Nombre de usuario:", True, self.colors['title'])
        username_label_rect = username_label.get_rect(bottomleft=(self.input_boxes['username'].left, self.input_boxes['username'].top - 10))
        self.screen.blit(username_label, username_label_rect)
        
        # 绘制密码标签
        password_label = self.fonts['input'].render("Contraseña:", True, self.colors['title'])
        password_label_rect = password_label.get_rect(bottomleft=(self.input_boxes['password'].left, self.input_boxes['password'].top - 10))
        self.screen.blit(password_label, password_label_rect)
        
        # 绘制输入框
        self.draw_text_input(self.input_boxes['username'], self.username, self.active_input == 'username')
        self.draw_text_input(self.input_boxes['password'], self.password, self.active_input == 'password', is_password=True)
        
        # 绘制登录按钮
        self.draw_button(self.buttons['login'], "Iniciar Sesión", self.button_hover)
        
        # 绘制注册链接
        self.draw_link(self.buttons['register_link'], "Crear nueva cuenta", self.register_link_hover)
        
        # 绘制消息（如果有）
        if self.message:
            color = self.colors['success'] if self.message_type == 'success' else self.colors['error']
            message_surface = self.fonts['message'].render(self.message, True, color)
            message_rect = message_surface.get_rect(center=(self.screen.get_width() // 2, self.buttons['login'].bottom + 40))
            self.screen.blit(message_surface, message_rect)
    
    def run(self):
        """运行场景的主循环"""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if not self.handle_event(event):
                    return  # 场景结束，返回
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)