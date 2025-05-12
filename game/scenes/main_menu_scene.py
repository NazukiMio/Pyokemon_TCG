import pygame
import sys
import os

# 导入核心模块
from game.core.auth_manager import AuthManager
from game.core.database_manager import DatabaseManager

class MainMenuScene:
    """
    主菜单场景类，显示登录成功后的主菜单
    """
    
    def __init__(self, screen, callback=None, user_id=None):
        """
        初始化主菜单场景
        
        Args:
            screen: pygame屏幕对象
            callback: 场景切换回调函数
            user_id: 当前登录的用户ID
        """
        self.screen = screen
        self.callback = callback
        self.user_id = user_id
        
        # 初始化数据库和认证管理器
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthManager(self.db_manager)
        
        # 如果提供了用户ID，获取用户信息
        self.user_info = None
        self.user_decks = []
        self.user_cards = []
        if user_id:
            self.user_info = self.db_manager.get_user_info(user_id)
            self.user_decks = self.db_manager.get_user_decks(user_id)
            self.user_cards = self.db_manager.get_user_cards(user_id)
        
        # 颜色定义
        self.colors = {
            'background': (30, 30, 60),
            'button': (86, 62, 139),
            'button_hover': (106, 82, 159),
            'button_text': (255, 255, 255),
            'panel_bg': (40, 40, 70, 220),
            'panel_border': (86, 62, 139),
            'title': (255, 255, 255),
            'text': (230, 230, 230),
            'highlight': (150, 150, 255)
        }
        
        # 加载字体
        self.fonts = self.load_fonts()
        
        # 主菜单选项
        self.menu_options = [
            "Jugar",              # 开始游戏
            "Colección",          # 查看收藏
            "Mazos",              # 管理卡组
            "Tienda",             # 商店
            "Opciones",           # 选项
            "Cerrar Sesión"       # 登出
        ]
        
        # 主菜单按钮
        self.buttons = []
        self.active_button = -1
        
        # 按钮动画效果参数
        self.button_scale = 1.0
        self.button_scale_direction = -0.001
        self.button_min_scale = 0.98
        self.button_max_scale = 1.02
        
        # 创建主菜单按钮
        self.create_menu_buttons()
        
        # 加载背景图（如果有）
        self.background = None
        try:
            bg_path = os.path.join("assets", "images", "backgrounds", "main_menu_bg.jpg")
            self.background = pygame.image.load(bg_path)
            self.background = pygame.transform.scale(self.background, screen.get_size())
        except Exception as e:
            print(f"无法加载背景图: {e}")
            
        # 加载装饰元素
        self.decorations = []
        self.load_decorations()
    
    def load_fonts(self):
        """加载字体"""
        fonts = {}
        try:
            font_path = os.path.join("assets", "fonts", "power-clear.ttf")
            title_font_path = os.path.join("assets", "fonts", "Pokemon-Solid-Normal.ttf")
            
            # 加载标题字体
            if os.path.exists(title_font_path):
                fonts['main_title'] = pygame.font.Font(title_font_path, 60)
            else:
                fonts['main_title'] = pygame.font.SysFont("arial", 60, bold=True)
            
            # 加载常规字体
            if os.path.exists(font_path):
                fonts['title'] = pygame.font.Font(font_path, 40)
                fonts['button'] = pygame.font.Font(font_path, 32)
                fonts['info'] = pygame.font.Font(font_path, 24)
                fonts['small'] = pygame.font.Font(font_path, 18)
            else:
                # 否则使用系统字体
                fonts['title'] = pygame.font.SysFont("arial", 40, bold=True)
                fonts['button'] = pygame.font.SysFont("arial", 32, bold=True)
                fonts['info'] = pygame.font.SysFont("arial", 24)
                fonts['small'] = pygame.font.SysFont("arial", 18)
        except Exception as e:
            print(f"加载字体出错: {e}")
            # 使用系统字体作为后备
            fonts['main_title'] = pygame.font.SysFont("arial", 60, bold=True)
            fonts['title'] = pygame.font.SysFont("arial", 40, bold=True)
            fonts['button'] = pygame.font.SysFont("arial", 32, bold=True)
            fonts['info'] = pygame.font.SysFont("arial", 24)
            fonts['small'] = pygame.font.SysFont("arial", 18)
        
        return fonts
    
    def create_menu_buttons(self):
        """创建主菜单按钮"""
        w, h = self.screen.get_size()
        button_width = 300
        button_height = 70
        
        # 计算起始y坐标，使按钮垂直居中
        total_buttons_height = len(self.menu_options) * button_height + (len(self.menu_options) - 1) * 20
        start_y = (h - total_buttons_height) // 2
        
        # 创建每个菜单选项的按钮
        for i, option in enumerate(self.menu_options):
            button_rect = pygame.Rect(
                w // 2 - button_width // 2,
                start_y + i * (button_height + 20),
                button_width,
                button_height
            )
            self.buttons.append({
                'rect': button_rect,
                'text': option,
                'hover': False
            })
    
    def load_decorations(self):
        """加载装饰元素"""
        # 尝试加载装饰图片，例如宝可梦图标或卡牌图案
        try:
            decoration_path = os.path.join("assets", "images", "decorations")
            for i in range(1, 4):  # 尝试加载3个装饰图片
                file_path = os.path.join(decoration_path, f"decoration_{i}.png")
                if os.path.exists(file_path):
                    decoration = pygame.image.load(file_path).convert_alpha()
                    self.decorations.append(decoration)
        except Exception as e:
            print(f"加载装饰元素出错: {e}")
    
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
            # 窗口大小改变时重新调整UI
            self.create_menu_buttons()
            
            # 重新缩放背景
            if self.background:
                self.background = pygame.transform.scale(self.background, self.screen.get_size())
        
        elif event.type == pygame.MOUSEMOTION:
            # 更新按钮悬停状态
            self.update_hover_states(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 处理按钮点击
            return self.handle_button_click(event.pos)
        
        return True
    
    def update_hover_states(self, pos):
        """
        更新按钮的悬停状态
        
        Args:
            pos: 鼠标位置（x, y）
        """
        # 重置所有按钮的悬停状态
        self.active_button = -1
        
        # 检查每个按钮
        for i, button in enumerate(self.buttons):
            button['hover'] = button['rect'].collidepoint(pos)
            if button['hover']:
                self.active_button = i
    
    def handle_button_click(self, pos):
        """
        处理按钮点击
        
        Args:
            pos: 点击位置（x, y）
        
        Returns:
            布尔值表示是否继续运行场景
        """
        for i, button in enumerate(self.buttons):
            if button['rect'].collidepoint(pos):
                # 根据点击的按钮执行对应操作
                if i == 0:  # "Jugar"
                    print("开始游戏")
                    # TODO: 跳转到游戏场景
                    return True
                
                elif i == 1:  # "Colección"
                    print("查看收藏")
                    # TODO: 跳转到收藏场景
                    return True
                
                elif i == 2:  # "Mazos"
                    print("管理卡组")
                    # TODO: 跳转到卡组管理场景
                    return True
                
                elif i == 3:  # "Tienda"
                    print("进入商店")
                    # TODO: 跳转到商店场景
                    return True
                
                elif i == 4:  # "Opciones"
                    print("打开选项")
                    # TODO: 跳转到选项场景
                    return True
                
                elif i == 5:  # "Cerrar Sesión"
                    print("退出登录")
                    # 退出登录并返回登录场景
                    if self.callback:
                        self.callback("login")
                        return False
        
        return True
    
    def draw_button(self, button, index):
        """
        绘制菜单按钮
        
        Args:
            button: 按钮信息字典
            index: 按钮索引
        """
        rect = button['rect']
        text = button['text']
        hover = button['hover']
        
        # 对活动按钮应用缩放效果
        if index == self.active_button:
            # 计算缩放后的尺寸
            scaled_width = int(rect.width * self.button_scale)
            scaled_height = int(rect.height * self.button_scale)
            
            # 保持居中
            scaled_rect = pygame.Rect(
                rect.centerx - scaled_width // 2,
                rect.centery - scaled_height // 2,
                scaled_width,
                scaled_height
            )
            
            # 使用缩放后的矩形
            draw_rect = scaled_rect
        else:
            draw_rect = rect
        
        # 绘制按钮阴影
        shadow_rect = draw_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=15)
        
        # 绘制按钮背景
        color = self.colors['button_hover'] if hover else self.colors['button']
        pygame.draw.rect(self.screen, color, draw_rect, border_radius=15)
        
        # 绘制内边缘高光
        if hover:
            highlight_rect = draw_rect.inflate(-6, -6)
            pygame.draw.rect(self.screen, (150, 150, 255, 80), highlight_rect, width=2, border_radius=13)
        
        # 绘制按钮边框
        pygame.draw.rect(self.screen, (46, 32, 99), draw_rect, width=2, border_radius=15)
        
        # 绘制按钮文本
        font = self.fonts['button']
        text_surface = font.render(text, True, self.colors['button_text'])
        text_rect = text_surface.get_rect(center=draw_rect.center)
        
        # 添加文本阴影
        shadow_surface = font.render(text, True, (30, 30, 30))
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 2, text_rect.centery + 2))
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(text_surface, text_rect)
    
    def draw_user_info_panel(self):
        """绘制用户信息面板"""
        if not self.user_info:
            return
            
        w, h = self.screen.get_size()
        panel_width = 300
        panel_height = 100
        panel_x = 20
        panel_y = 20
        
        # 创建面板矩形
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # 绘制半透明背景
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.colors['panel_bg'])
        self.screen.blit(panel_surface, panel_rect)
        
        # 绘制边框
        pygame.draw.rect(self.screen, self.colors['panel_border'], panel_rect, width=2, border_radius=10)
        
        # 绘制用户名
        username_text = f"Usuario: {self.user_info['username']}"
        username_surface = self.fonts['info'].render(username_text, True, self.colors['text'])
        username_rect = username_surface.get_rect(topleft=(panel_x + 15, panel_y + 15))
        self.screen.blit(username_surface, username_rect)
        
        # 绘制卡牌和卡组信息
        cards_text = f"Cartas: {sum(card['quantity'] for card in self.user_cards)}"
        cards_surface = self.fonts['info'].render(cards_text, True, self.colors['text'])
        cards_rect = cards_surface.get_rect(topleft=(panel_x + 15, panel_y + 45))
        self.screen.blit(cards_surface, cards_rect)
        
        decks_text = f"Mazos: {len(self.user_decks)}"
        decks_surface = self.fonts['info'].render(decks_text, True, self.colors['text'])
        decks_rect = decks_surface.get_rect(topleft=(panel_x + 15, panel_y + 75))
        self.screen.blit(decks_surface, decks_rect)
    
    def draw_decorations(self):
        """绘制装饰元素"""
        w, h = self.screen.get_size()
        
        # 如果有装饰图片，绘制它们
        if self.decorations:
            for i, decoration in enumerate(self.decorations):
                # 可以根据需要调整装饰的位置
                if i == 0:
                    # 左上角装饰
                    pos = (50, 150)
                elif i == 1:
                    # 右上角装饰
                    pos = (w - decoration.get_width() - 50, 150)
                else:
                    # 底部中央装饰
                    pos = (w // 2 - decoration.get_width() // 2, h - decoration.get_height() - 50)
                
                self.screen.blit(decoration, pos)
    
    def draw(self):
        """绘制场景"""
        # 绘制背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.colors['background'])
        
        # 绘制装饰
        self.draw_decorations()
        
        # 绘制标题
        title_text = "Menú Principal"
        title_surface = self.fonts['main_title'].render(title_text, True, self.colors['title'])
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 80))
        
        # 绘制标题阴影
        shadow_surface = self.fonts['main_title'].render(title_text, True, (30, 30, 30))
        shadow_rect = shadow_surface.get_rect(center=(title_rect.centerx + 4, title_rect.centery + 4))
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(title_surface, title_rect)
        
        # 绘制用户信息面板
        self.draw_user_info_panel()
        
        # 更新按钮动画
        self.button_scale += self.button_scale_direction
        if self.button_scale <= self.button_min_scale or self.button_scale >= self.button_max_scale:
            self.button_scale_direction *= -1
        
        # 绘制所有菜单按钮
        for i, button in enumerate(self.buttons):
            self.draw_button(button, i)
    
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