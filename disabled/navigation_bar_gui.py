import pygame
import pygame_gui
import os
from typing import Optional, Callable

class NavigationBarGUI:
    """
    使用pygame_gui实现的现代简约风格导航栏
    需要pygame-ce (Community Edition) 支持
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
        self.height = 80  # 稍微减小高度，更现代
        self.y_position = screen_height - self.height
        
        # 创建UI管理器
        self.ui_manager = pygame_gui.UIManager((screen_width, screen_height), self.load_theme())
        
        # 导航项目配置
        self.nav_items = [
            {'id': 'pokedex', 'text': 'Pokédex', 'icon': '📖'},
            {'id': 'social', 'text': 'Social', 'icon': '👥'},
            {'id': 'home', 'text': 'Inicio', 'icon': '🏠', 'is_main': True},
            {'id': 'battle', 'text': 'Batalla', 'icon': '⚔️'},
            {'id': 'menu', 'text': 'Menú', 'icon': '☰'}
        ]
        
        # 按钮字典
        self.buttons = {}
        self.active_item = 'home'
        
        # 回调函数
        self.on_navigation_click: Optional[Callable] = None
        
        # 创建导航按钮
        self.create_navigation_buttons()
        
        # 设置初始活跃状态
        self.set_active('home')
    
    def load_theme(self) -> str:
        """
        加载UI主题
        
        Returns:
            主题文件路径或默认主题JSON
        """
        # 尝试加载自定义主题文件
        theme_path = os.path.join("assets", "themes", "navigation_theme.json")
        
        if os.path.exists(theme_path):
            return theme_path
        else:
            # 创建内置现代主题
            return self.create_modern_theme()
    
    def create_modern_theme(self) -> dict:
        """
        创建现代简约风格主题
        
        Returns:
            主题配置字典
        """
        theme_data = {
            "button": {
                "colours": {
                    "normal_bg": "#2D2D3A",
                    "hovered_bg": "#3A3A4A", 
                    "selected_bg": "#FFCC00",
                    "active_bg": "#FFCC00",
                    "normal_text": "#FFFFFF",
                    "hovered_text": "#FFFFFF",
                    "selected_text": "#000000",
                    "active_text": "#000000",
                    "normal_border": "#555564",
                    "hovered_border": "#FFCC00",
                    "selected_border": "#FFDD33",
                    "active_border": "#FFDD33"
                },
                "font": {
                    "name": "arial",
                    "size": "14",
                    "bold": "1"
                },
                "misc": {
                    "shape": "rounded_rectangle",
                    "shape_corner_radius": "15",
                    "border_width": "2",
                    "shadow_width": "3",
                    "text_shadow": "1",
                    "text_shadow_colour": "#000000"
                }
            },
            "#home_home_button": {  # 修改主题选择器，移除点号
                "colours": {
                    "normal_bg": "#FFCC00",
                    "hovered_bg": "#FFDD33",
                    "selected_bg": "#FFAA00",
                    "normal_text": "#000000",
                    "hovered_text": "#000000",
                    "selected_text": "#000000"
                },
                "misc": {
                    "shape": "ellipse",
                    "border_width": "3"
                }
            }
        }
        
        return theme_data
    
    def create_navigation_buttons(self):
        """创建导航按钮"""
        button_width = self.screen_width // 5
        button_height = self.height - 20
        
        for i, item in enumerate(self.nav_items):
            x = i * button_width + 10
            y = self.y_position + 10
            
            # 主页按钮特殊处理（圆形）
            if item.get('is_main'):
                # 圆形主页按钮
                button_size = min(button_width - 20, button_height)
                x = i * button_width + (button_width - button_size) // 2
                y = self.y_position + (self.height - button_size) // 2 - 5  # 稍微上移
                
                button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(x, y, button_size, button_size),
                    text=f"{item['icon']} {item['text']}",
                    manager=self.ui_manager,
                    object_id=f"#{item['id']}_home_button"  # 移除点号，使用下划线
                )
            else:
                # 普通矩形按钮
                button = pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect(x, y, button_width - 20, button_height),
                    text=f"{item['icon']} {item['text']}",
                    manager=self.ui_manager,
                    object_id=f"#{item['id']}_button"
                )
            
            self.buttons[item['id']] = button
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        处理事件
        
        Args:
            event: pygame事件
            
        Returns:
            被点击的导航项ID，如果没有点击返回None
        """
        # 让UI管理器处理事件
        self.ui_manager.process_events(event)
        
        # 检查按钮点击事件
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for nav_id, button in self.buttons.items():
                if event.ui_element == button:
                    self.set_active(nav_id)
                    if self.on_navigation_click:
                        self.on_navigation_click(nav_id)
                    return nav_id
        
        return None
    
    def set_active(self, nav_id: str):
        """
        设置活跃的导航项
        
        Args:
            nav_id: 导航项ID
        """
        if nav_id in self.buttons:
            self.active_item = nav_id
            
            # 更新所有按钮状态
            for item_id, button in self.buttons.items():
                if item_id == nav_id:
                    # 设置为选中状态
                    button.select()
                else:
                    # 取消选中状态
                    button.unselect()
    
    def get_active(self) -> str:
        """
        获取当前活跃的导航项
        
        Returns:
            当前活跃的导航项ID
        """
        return self.active_item
    
    def update(self, time_delta: float):
        """
        更新UI
        
        Args:
            time_delta: 时间增量
        """
        self.ui_manager.update(time_delta)
    
    def draw(self, screen: pygame.Surface):
        """
        绘制导航栏
        
        Args:
            screen: pygame屏幕对象
        """
        # 绘制背景
        self.draw_background(screen)
        
        # 绘制UI元素
        self.ui_manager.draw_ui(screen)
    
    def draw_background(self, screen: pygame.Surface):
        """绘制导航栏背景"""
        # 创建背景矩形
        bg_rect = pygame.Rect(0, self.y_position, self.screen_width, self.height)
        
        # 绘制渐变背景
        for y in range(self.height):
            ratio = y / self.height
            # 从深蓝灰色到更深的颜色
            r = int(45 * (1 - ratio * 0.3))
            g = int(45 * (1 - ratio * 0.3))
            b = int(65 * (1 - ratio * 0.2))
            
            line_rect = pygame.Rect(0, self.y_position + y, self.screen_width, 1)
            pygame.draw.rect(screen, (r, g, b), line_rect)
        
        # 绘制顶部边框
        pygame.draw.line(screen, (85, 85, 110), 
                        (0, self.y_position), 
                        (self.screen_width, self.y_position), 2)
        
        # 绘制顶部高光
        pygame.draw.line(screen, (255, 204, 0), 
                        (0, self.y_position + 2), 
                        (self.screen_width, self.y_position + 2), 1)
    
    def resize(self, new_width: int, new_height: int):
        """
        调整导航栏大小
        
        Args:
            new_width: 新的屏幕宽度
            new_height: 新的屏幕高度
        """
        self.screen_width = new_width
        self.screen_height = new_height
        self.y_position = new_height - self.height
        
        # 重新创建UI管理器
        self.ui_manager = pygame_gui.UIManager((new_width, new_height), self.load_theme())
        
        # 重新创建按钮
        self.buttons.clear()
        self.create_navigation_buttons()
        
        # 恢复活跃状态
        self.set_active(self.active_item)
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'ui_manager'):
            # pygame_gui会自动清理资源
            pass
    
    def __del__(self):
        """析构函数"""
        self.cleanup()


# 使用示例
class NavigationBarGUIExample:
    """
    导航栏使用示例
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        """初始化示例"""
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        
        # 创建导航栏
        self.nav_bar = NavigationBarGUI(screen_width, screen_height)
        
        # 设置回调
        self.nav_bar.on_navigation_click = self.on_nav_click
        
        self.running = True
        self.current_page = 'home'
    
    def on_nav_click(self, nav_id: str):
        """导航点击回调"""
        self.current_page = nav_id
        print(f"导航到: {nav_id}")
    
    def run(self):
        """运行示例"""
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # 处理导航栏事件
                nav_result = self.nav_bar.handle_event(event)
                if nav_result:
                    print(f"导航到: {nav_result}")
            
            # 更新
            self.nav_bar.update(time_delta)
            
            # 绘制
            self.screen.fill((25, 25, 40))
            
            # 绘制页面内容指示
            font = pygame.font.SysFont("arial", 36, bold=True)
            text = font.render(f"当前页面: {self.current_page}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, 200))
            self.screen.blit(text, text_rect)
            
            # 绘制导航栏
            self.nav_bar.draw(self.screen)
            
            pygame.display.flip()
        
        pygame.quit()