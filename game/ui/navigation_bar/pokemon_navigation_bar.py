import pygame
import pygame_gui
import os
import math
from typing import Optional, Callable

class PokemonNavigationGUI:
    """
    Pokemon风格现代毛玻璃导航栏
    使用PNG图标和浮动动效
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        """
        初始化导航栏
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 导航栏尺寸
        self.height = 90
        self.y_position = screen_height - self.height
        
        # 导航项目配置
        self.nav_items = [
            {'id': 'pokedex', 'text': 'Pokédex', 'icon': 'dex'},
            {'id': 'social', 'text': 'Social', 'icon': 'friends'},
            {'id': 'home', 'text': 'Inicio', 'icon': 'home'},
            {'id': 'battle', 'text': 'Batalla', 'icon': 'combat'},
            {'id': 'menu', 'text': 'Menú', 'icon': 'menu'}
        ]
        
        # 加载图标
        self.icons = self.load_icons()
        
        # 导航状态
        self.active_item = 'home'
        self.hover_item = None
        
        # 动画参数
        self.animation_timer = 0
        self.float_offsets = {item['id']: 0 for item in self.nav_items}
        self.hover_scales = {item['id']: 1.0 for item in self.nav_items}
        
        # 计算按钮区域
        self.button_areas = self.calculate_button_areas()
        
        # 回调函数
        self.on_navigation_click: Optional[Callable] = None
        
        # 字体
        self.font = pygame.font.SysFont("arial", 11, bold=True)
    
    def load_icons(self) -> dict:
        """
        加载PNG图标文件
        
        Returns:
            图标字典 {icon_name: {'normal': surface, 'dark': surface}}
        """
        icons = {}
        
        for item in self.nav_items:
            icon_name = item['icon']
            icons[icon_name] = {}
            
            # 加载普通图标
            normal_path = os.path.join("assets", "icons", f"{icon_name}.png")
            if os.path.exists(normal_path):
                try:
                    icon_surface = pygame.image.load(normal_path)
                    icon_surface = pygame.transform.smoothscale(icon_surface, (24, 24))
                    icons[icon_name]['normal'] = icon_surface
                    print(f"✅ 普通图标加载: {icon_name}.png")
                except Exception as e:
                    print(f"❌ 普通图标加载失败 {icon_name}: {e}")
                    icons[icon_name]['normal'] = None
            else:
                print(f"⚠️ 普通图标文件不存在: {normal_path}")
                icons[icon_name]['normal'] = None
            
            # 加载dark图标
            dark_path = os.path.join("assets", "icons", f"{icon_name}_dark.png")
            if os.path.exists(dark_path):
                try:
                    dark_surface = pygame.image.load(dark_path)
                    dark_surface = pygame.transform.smoothscale(dark_surface, (24, 24))
                    icons[icon_name]['dark'] = dark_surface
                    print(f"✅ Dark图标加载: {icon_name}_dark.png")
                except Exception as e:
                    print(f"❌ Dark图标加载失败 {icon_name}: {e}")
                    icons[icon_name]['dark'] = None
            else:
                print(f"⚠️ Dark图标文件不存在: {dark_path}")
                icons[icon_name]['dark'] = None
        
        return icons
    
    def calculate_button_areas(self):
        """计算按钮区域"""
        areas = {}
        button_width = (self.screen_width - 60) // 5
        start_x = 30
        
        for i, item in enumerate(self.nav_items):
            x = start_x + i * (button_width + 6)
            y = self.y_position + 15
            
            areas[item['id']] = pygame.Rect(x, y, button_width, 60)
        
        return areas
    
    def update_animations(self):
        """更新动画效果"""
        self.animation_timer += 1
        
        for item in self.nav_items:
            item_id = item['id']
            
            # 浮动动效
            if item_id == self.active_item:
                # 活跃项目有更明显的浮动
                phase = (self.animation_timer + hash(item_id) % 60) * 0.08
                self.float_offsets[item_id] = math.sin(phase) * 4
            elif item_id == self.hover_item:
                # 悬停项目有轻微浮动
                phase = (self.animation_timer + hash(item_id) % 60) * 0.12
                self.float_offsets[item_id] = math.sin(phase) * 2
            else:
                # 非活跃项目缓慢回到原位
                current_offset = self.float_offsets[item_id]
                self.float_offsets[item_id] = current_offset * 0.9
            
            # 缩放动效
            target_scale = 1.1 if item_id == self.hover_item else 1.0
            current_scale = self.hover_scales[item_id]
            self.hover_scales[item_id] = current_scale + (target_scale - current_scale) * 0.15
    
    def handle_mouse_motion(self, pos: tuple):
        """处理鼠标移动"""
        self.hover_item = None
        
        for item_id, rect in self.button_areas.items():
            if rect.collidepoint(pos):
                self.hover_item = item_id
                break
    
    def handle_mouse_click(self, pos: tuple) -> Optional[str]:
        """处理鼠标点击"""
        for item_id, rect in self.button_areas.items():
            if rect.collidepoint(pos):
                self.set_active(item_id)
                if self.on_navigation_click:
                    self.on_navigation_click(item_id)
                return item_id
        return None
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        处理事件
        
        Args:
            event: pygame事件
            
        Returns:
            被点击的导航项ID，如果没有点击返回None
        """
        if event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                return self.handle_mouse_click(event.pos)
        
        return None
    
    def set_active(self, nav_id: str):
        """设置活跃的导航项"""
        if nav_id in [item['id'] for item in self.nav_items]:
            self.active_item = nav_id
    
    def get_active(self) -> str:
        """获取当前活跃的导航项"""
        return self.active_item
    
    def update(self, time_delta: float):
        """更新导航栏"""
        self.update_animations()
    
    def draw_glass_background(self, screen: pygame.Surface):
        """绘制毛玻璃背景效果"""
        # 创建半透明背景
        bg_surface = pygame.Surface((self.screen_width, self.height), pygame.SRCALPHA)
        
        # 毛玻璃效果背景色
        bg_color = (255, 255, 255, 217)  # 85% 透明度
        bg_surface.fill(bg_color)
        
        # 绘制顶部边框
        pygame.draw.line(bg_surface, (255, 255, 255, 77), 
                        (0, 0), (self.screen_width, 0), 1)
        
        # 绘制到主屏幕
        screen.blit(bg_surface, (0, self.y_position))
    
    def draw_separators(self, screen: pygame.Surface):
        """绘制分隔符"""
        button_width = (self.screen_width - 60) // 5
        start_x = 30
        
        # 绘制垂直分隔符（在按钮之间）
        for i in range(len(self.nav_items) - 1):  # 4条分隔符
            sep_x = start_x + (i + 1) * (button_width + 6) - 3
            sep_y1 = self.y_position + 25  # 不顶格，留出边距
            sep_y2 = self.y_position + self.height - 25
            
            # 绘制半透明的分隔线
            pygame.draw.line(screen, (74, 85, 104, 60), 
                           (sep_x, sep_y1), (sep_x, sep_y2), 1)
    
    def draw_navigation_items(self, screen: pygame.Surface):
        """绘制导航项目"""
        for item in self.nav_items:
            item_id = item['id']
            icon_name = item['icon']
            
            # 获取按钮区域
            rect = self.button_areas[item_id]
            
            # 应用浮动和缩放动效
            float_offset = self.float_offsets[item_id]
            scale = self.hover_scales[item_id]
            
            # 计算动效后的位置
            animated_rect = rect.copy()
            animated_rect.y += int(float_offset)
            
            if scale != 1.0:
                # 应用缩放
                scaled_width = int(rect.width * scale)
                scaled_height = int(rect.height * scale)
                animated_rect = pygame.Rect(
                    rect.centerx - scaled_width // 2,
                    rect.centery - scaled_height // 2 + int(float_offset),
                    scaled_width,
                    scaled_height
                )
            
            # 选择图标类型（活跃状态用dark图标）
            icon_type = 'dark' if item_id == self.active_item else 'normal'
            icon_surface = self.icons.get(icon_name, {}).get(icon_type)
            
            if icon_surface:
                # 绘制图标
                icon_x = animated_rect.centerx - 12
                icon_y = animated_rect.y + 8
                
                # 如果有缩放效果，也缩放图标
                if scale != 1.0:
                    scaled_size = int(24 * scale)
                    scaled_icon = pygame.transform.smoothscale(icon_surface, (scaled_size, scaled_size))
                    icon_x = animated_rect.centerx - scaled_size // 2
                    screen.blit(scaled_icon, (icon_x, icon_y))
                else:
                    screen.blit(icon_surface, (icon_x, icon_y))
            
            # 绘制文字
            text_color = (45, 55, 72) if item_id == self.active_item else (113, 128, 150)
            text_surface = self.font.render(item['text'], True, text_color)
            text_rect = text_surface.get_rect(center=(animated_rect.centerx, animated_rect.bottom - 15))
            screen.blit(text_surface, text_rect)
            
            # 活跃状态的底部指示器
            if item_id == self.active_item:
                indicator_y = self.y_position + self.height - 8
                indicator_x1 = animated_rect.centerx - 15
                indicator_x2 = animated_rect.centerx + 15
                
                # 绘制底部指示线
                pygame.draw.line(screen, (102, 126, 234), 
                               (indicator_x1, indicator_y), (indicator_x2, indicator_y), 3)
    
    def draw(self, screen: pygame.Surface):
        """
        绘制导航栏
        
        Args:
            screen: pygame屏幕对象
        """
        # 绘制毛玻璃背景
        self.draw_glass_background(screen)
        
        # 绘制分隔符
        self.draw_separators(screen)
        
        # 绘制导航项目
        self.draw_navigation_items(screen)
    
    def resize(self, new_width: int, new_height: int):
        """调整导航栏大小"""
        self.screen_width = new_width
        self.screen_height = new_height
        self.y_position = new_height - self.height
        
        # 重新计算按钮区域
        self.button_areas = self.calculate_button_areas()
    
    def cleanup(self):
        """清理资源"""
        pass
    
    def __del__(self):
        """析构函数"""
        self.cleanup()