import pygame
import math
import os

class NavigationBar:
    """
    Pokemon TCG风格的导航栏组件
    位于屏幕底部，包含5个主要功能按钮
    """
    
    def __init__(self, screen_width, screen_height):
        """
        初始化导航栏
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 导航栏尺寸
        self.height = 100
        self.y_position = screen_height - self.height
        
        # 颜色主题 - Pokemon TCG风格
        self.colors = {
            'bg_primary': (45, 45, 65),           # 深蓝灰色背景
            'bg_secondary': (60, 60, 85),         # 次要背景色
            'accent': (255, 204, 0),              # Pokemon金黄色
            'accent_hover': (255, 221, 51),       # 悬停时的金黄色
            'text': (255, 255, 255),              # 白色文字
            'text_inactive': (180, 180, 200),     # 非活跃文字
            'border': (85, 85, 110),              # 边框颜色
            'shadow': (25, 25, 35),               # 阴影颜色
            'active_bg': (70, 130, 200),          # 活跃按钮背景
            'gradient_top': (65, 65, 90),         # 渐变顶部
            'gradient_bottom': (35, 35, 55)       # 渐变底部
        }
        
        # 导航项目配置
        self.nav_items = [
            {
                'id': 'pokedex',
                'name': 'Pokédex',
                'icon': '📖',  # 可以替换为实际图标
                'position': 0
            },
            {
                'id': 'social',
                'name': 'Social',
                'icon': '👥',
                'position': 1
            },
            {
                'id': 'home',
                'name': 'Inicio',
                'icon': '🏠',
                'position': 2,
                'is_main': True  # 主要按钮，样式特殊
            },
            {
                'id': 'battle',
                'name': 'Batalla',
                'icon': '⚔️',
                'position': 3
            },
            {
                'id': 'menu',
                'name': 'Menú',
                'icon': '☰',
                'position': 4
            }
        ]
        
        # 按钮状态
        self.active_item = 'home'  # 默认活跃项
        self.hover_item = None
        self.button_rects = {}
        
        # 动画参数
        self.animation_offset = 0
        self.animation_speed = 0.1
        self.pulse_timer = 0
        
        # 加载字体
        self.fonts = self.load_fonts()
        
        # 加载图标（如果有）
        self.icons = self.load_icons()
        
        # 创建按钮
        self.create_buttons()
    
    def load_fonts(self):
        """加载字体"""
        fonts = {}
        try:
            font_path = os.path.join("assets", "fonts", "power-clear.ttf")
            if os.path.exists(font_path):
                fonts['nav'] = pygame.font.Font(font_path, 16)
                fonts['nav_small'] = pygame.font.Font(font_path, 14)
            else:
                fonts['nav'] = pygame.font.SysFont("arial", 16, bold=True)
                fonts['nav_small'] = pygame.font.SysFont("arial", 14)
        except Exception as e:
            print(f"Error al cargar fuentes: {e}")
            fonts['nav'] = pygame.font.SysFont("arial", 16, bold=True)
            fonts['nav_small'] = pygame.font.SysFont("arial", 14)
        
        return fonts
    
    def load_icons(self):
        """加载导航图标"""
        icons = {}
        icon_names = ['pokedex', 'social', 'home', 'battle', 'menu']
        
        for icon_name in icon_names:
            try:
                icon_path = os.path.join("assets", "images", "icons", f"{icon_name}.png")
                if os.path.exists(icon_path):
                    icon = pygame.image.load(icon_path).convert_alpha()
                    # 调整图标大小
                    icon = pygame.transform.scale(icon, (32, 32))
                    icons[icon_name] = icon
            except Exception as e:
                print(f"Error al cargar icono {icon_name}: {e}")
        
        return icons
    
    def create_buttons(self):
        """创建导航按钮"""
        button_width = self.screen_width // 5
        
        for item in self.nav_items:
            x = item['position'] * button_width
            y = self.y_position
            
            # 主页按钮稍大一些
            if item.get('is_main'):
                # 主页按钮做成圆形并稍微向上突出
                button_rect = pygame.Rect(
                    x + (button_width - 70) // 2,
                    y - 10,
                    70,
                    70
                )
            else:
                button_rect = pygame.Rect(
                    x + 10,
                    y + 10,
                    button_width - 20,
                    self.height - 20
                )
            
            self.button_rects[item['id']] = button_rect
    
    def create_gradient_surface(self, width, height, color_top, color_bottom):
        """创建渐变表面"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        for y in range(height):
            # 计算当前行的颜色
            ratio = y / height
            r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
            g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
            b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
        return surface
    
    def draw_nav_background(self, screen):
        """绘制导航栏背景"""
        # 创建渐变背景
        gradient = self.create_gradient_surface(
            self.screen_width, 
            self.height, 
            self.colors['gradient_top'], 
            self.colors['gradient_bottom']
        )
        
        # 绘制主背景
        nav_rect = pygame.Rect(0, self.y_position, self.screen_width, self.height)
        screen.blit(gradient, (0, self.y_position))
        
        # 绘制顶部边框线
        pygame.draw.line(
            screen, 
            self.colors['border'], 
            (0, self.y_position), 
            (self.screen_width, self.y_position), 
            2
        )
        
        # 绘制顶部高光线
        pygame.draw.line(
            screen, 
            self.colors['accent'], 
            (0, self.y_position + 2), 
            (self.screen_width, self.y_position + 2), 
            1
        )
    
    def draw_button(self, screen, item):
        """绘制单个导航按钮"""
        button_rect = self.button_rects[item['id']]
        is_active = self.active_item == item['id']
        is_hover = self.hover_item == item['id']
        is_main = item.get('is_main', False)
        
        # 动画效果计算
        scale = 1.0
        if is_hover:
            scale = 1.05
        elif is_active:
            scale = 1.02
        
        # 脉冲动画（仅对主页按钮）
        if is_main:
            pulse = math.sin(self.pulse_timer * 0.1) * 0.03 + 1.0
            scale *= pulse
        
        # 计算缩放后的矩形
        if scale != 1.0:
            scaled_width = int(button_rect.width * scale)
            scaled_height = int(button_rect.height * scale)
            scaled_rect = pygame.Rect(
                button_rect.centerx - scaled_width // 2,
                button_rect.centery - scaled_height // 2,
                scaled_width,
                scaled_height
            )
        else:
            scaled_rect = button_rect
        
        # 绘制按钮阴影
        if is_main:
            shadow_rect = scaled_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.circle(
                screen, 
                self.colors['shadow'], 
                shadow_rect.center, 
                shadow_rect.width // 2
            )
        else:
            shadow_rect = scaled_rect.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            pygame.draw.rect(screen, self.colors['shadow'], shadow_rect, border_radius=15)
        
        # 选择按钮颜色
        if is_active:
            if is_main:
                bg_color = self.colors['accent']
            else:
                bg_color = self.colors['active_bg']
        elif is_hover:
            bg_color = self.colors['accent_hover']
        else:
            bg_color = self.colors['bg_secondary']
        
        # 绘制按钮背景
        if is_main:
            # 主页按钮绘制为圆形
            pygame.draw.circle(screen, bg_color, scaled_rect.center, scaled_rect.width // 2)
            pygame.draw.circle(
                screen, 
                self.colors['border'], 
                scaled_rect.center, 
                scaled_rect.width // 2, 
                2
            )
            
            # 主页按钮的内圈高光
            if is_active or is_hover:
                inner_radius = scaled_rect.width // 2 - 8
                pygame.draw.circle(
                    screen, 
                    (255, 255, 255, 100), 
                    scaled_rect.center, 
                    inner_radius, 
                    2
                )
        else:
            # 普通按钮绘制为圆角矩形
            pygame.draw.rect(screen, bg_color, scaled_rect, border_radius=15)
            pygame.draw.rect(screen, self.colors['border'], scaled_rect, 2, border_radius=15)
            
            # 活跃/悬停状态的内部高光
            if is_active or is_hover:
                highlight_rect = scaled_rect.inflate(-6, -6)
                pygame.draw.rect(
                    screen, 
                    (255, 255, 255, 60), 
                    highlight_rect, 
                    2, 
                    border_radius=13
                )
        
        # 绘制图标
        if item['id'] in self.icons:
            icon = self.icons[item['id']]
            icon_rect = icon.get_rect(center=(scaled_rect.centerx, scaled_rect.centery - 8))
            screen.blit(icon, icon_rect)
        else:
            # 使用emoji作为临时图标
            icon_font = pygame.font.SysFont("arial", 24)
            icon_surface = icon_font.render(item['icon'], True, self.colors['text'])
            icon_rect = icon_surface.get_rect(center=(scaled_rect.centerx, scaled_rect.centery - 8))
            screen.blit(icon_surface, icon_rect)
        
        # 绘制文字标签
        text_color = self.colors['text'] if (is_active or is_hover) else self.colors['text_inactive']
        font = self.fonts['nav_small'] if is_main else self.fonts['nav']
        text_surface = font.render(item['name'], True, text_color)
        
        # 主页按钮的文字位置稍微下移
        text_y_offset = 15 if is_main else 12
        text_rect = text_surface.get_rect(center=(scaled_rect.centerx, scaled_rect.centery + text_y_offset))
        screen.blit(text_surface, text_rect)
        
        # 活跃状态指示器（小圆点）
        if is_active and not is_main:
            indicator_y = scaled_rect.bottom + 5
            pygame.draw.circle(
                screen, 
                self.colors['accent'], 
                (scaled_rect.centerx, indicator_y), 
                3
            )
    
    def handle_click(self, pos):
        """
        处理点击事件
        
        Args:
            pos: 点击位置 (x, y)
        
        Returns:
            被点击的导航项ID，如果没有点击到按钮则返回None
        """
        for item in self.nav_items:
            if self.button_rects[item['id']].collidepoint(pos):
                self.active_item = item['id']
                return item['id']
        return None
    
    def handle_hover(self, pos):
        """
        处理鼠标悬停
        
        Args:
            pos: 鼠标位置 (x, y)
        """
        self.hover_item = None
        for item in self.nav_items:
            if self.button_rects[item['id']].collidepoint(pos):
                self.hover_item = item['id']
                break
    
    def update(self):
        """更新动画和状态"""
        self.pulse_timer += 1
        if self.pulse_timer >= 628:  # 2π * 100 的近似值
            self.pulse_timer = 0
    
    def draw(self, screen):
        """
        绘制导航栏
        
        Args:
            screen: pygame屏幕对象
        """
        # 更新动画
        self.update()
        
        # 绘制背景
        self.draw_nav_background(screen)
        
        # 绘制所有按钮
        for item in self.nav_items:
            self.draw_button(screen, item)
    
    def resize(self, new_width, new_height):
        """
        当屏幕尺寸改变时调整导航栏
        
        Args:
            new_width: 新的屏幕宽度
            new_height: 新的屏幕高度
        """
        self.screen_width = new_width
        self.screen_height = new_height
        self.y_position = new_height - self.height
        self.create_buttons()
    
    def set_active(self, item_id):
        """
        设置活跃的导航项
        
        Args:
            item_id: 导航项ID
        """
        if any(item['id'] == item_id for item in self.nav_items):
            self.active_item = item_id
    
    def get_active(self):
        """
        获取当前活跃的导航项
        
        Returns:
            当前活跃的导航项ID
        """
        return self.active_item