"""
战斗页面 - 卡组构建和对战准备的入口
包含Logo、装饰背景、卡组构建按钮、对战准备按钮
"""

import pygame
import pygame_gui
import os
from typing import Dict, Any, Optional, Callable

class BattlePage:
    """战斗页面类"""
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager, game_manager, nav_height: int = 0):
        """
        初始化战斗页面
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            ui_manager: pygame_gui UI管理器
            game_manager: 游戏管理器
            nav_height: 导航栏高度
        """
        print("⚔️ 初始化战斗页面...")
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        self.game_manager = game_manager
        self.nav_height = nav_height
        
        # 缩放因子
        self.scale_factor = min(screen_width / 1920, screen_height / 1080)
        
        # 可用内容区域
        self.content_height = screen_height - nav_height
        
        # 窗口管理
        self.active_windows = {
            'deck_builder': None,
            'battle_prep': None,
            'battle_interface': None
        }
        
        # 页面状态
        self.current_state = "lobby"  # lobby, deck_building, battle_prep, in_battle
        
        # UI元素
        self.logo_image = None
        self.decoration_image = None
        self.deck_builder_button = None
        self.battle_prep_button = None
        
        # 按钮状态
        self.button_hover_states = {
            'deck_builder': False,
            'battle_prep': False
        }
        
        # 回调函数
        self.on_deck_builder_click: Optional[Callable] = None
        self.on_battle_prep_click: Optional[Callable] = None
        self.on_battle_started: Optional[Callable] = None  # 战斗开始回调
        
        # 战斗控制器
        self.battle_controller = None
        
        # 初始化UI
        self._setup_ui_layout()
        self._load_assets()
        self._create_ui_elements()
        
        print("✅ 战斗页面初始化完成")
    
    def _setup_ui_layout(self):
        """设置UI布局"""
        print("📐 设置战斗页面布局...")
        
        # Logo区域 (左上角)
        logo_size = int(200 * self.scale_factor)
        self.logo_rect = pygame.Rect(
            int(20 * self.scale_factor), 
            self.nav_height + int(20 * self.scale_factor), 
            logo_size, 
            int(logo_size * 0.5)  # 2:1 比例
        )
        
        # 装饰图片区域 (上方背景，占内容区域的40%)
        decoration_height = int(self.content_height * 0.4)
        self.decoration_rect = pygame.Rect(
            0, 
            self.nav_height, 
            self.screen_width, 
            decoration_height
        )
        
        # 功能按钮区域 (装饰图片下方)
        button_width = int(320 * self.scale_factor)
        button_height = int(120 * self.scale_factor)
        button_spacing = int(80 * self.scale_factor)
        
        # 垂直位置：装饰图片下方留一些间距
        button_y = self.decoration_rect.bottom + int(60 * self.scale_factor)
        
        # 水平居中，两个按钮分左右
        total_width = button_width * 2 + button_spacing
        start_x = (self.screen_width - total_width) // 2
        
        # 左侧：卡组构建按钮
        self.deck_builder_button_rect = pygame.Rect(
            start_x, 
            button_y, 
            button_width, 
            button_height
        )
        
        # 右侧：对战准备按钮
        self.battle_prep_button_rect = pygame.Rect(
            start_x + button_width + button_spacing, 
            button_y, 
            button_width, 
            button_height
        )
        
        print(f"   Logo区域: {self.logo_rect}")
        print(f"   装饰区域: {self.decoration_rect}")
        print(f"   卡组构建按钮: {self.deck_builder_button_rect}")
        print(f"   对战准备按钮: {self.battle_prep_button_rect}")
    
    def _load_assets(self):
        """加载资源文件"""
        print("🎨 加载战斗页面资源...")
        
        try:
            # 加载Logo (可以是Pokemon风格的Logo)
            logo_path = os.path.join("assets", "images", "battle_logo.png")
            if os.path.exists(logo_path):
                self.logo_image = pygame.image.load(logo_path)
                self.logo_image = pygame.transform.scale(
                    self.logo_image, 
                    (self.logo_rect.width, self.logo_rect.height)
                )
                print("✅ Logo加载成功")
            else:
                print(f"⚠️ Logo文件不存在: {logo_path}")
                self.logo_image = None
            
            # 加载装饰背景图片
            decoration_path = os.path.join("assets", "images", "battle_decoration.png")
            if os.path.exists(decoration_path):
                self.decoration_image = pygame.image.load(decoration_path)
                self.decoration_image = pygame.transform.scale(
                    self.decoration_image, 
                    (self.decoration_rect.width, self.decoration_rect.height)
                )
                print("✅ 装饰图片加载成功")
            else:
                print(f"⚠️ 装饰图片不存在: {decoration_path}")
                self.decoration_image = None
                
        except Exception as e:
            print(f"❌ 加载资源时出错: {e}")
            self.logo_image = None
            self.decoration_image = None
    
    def _create_ui_elements(self):
        """创建UI元素"""
        print("🎯 创建战斗页面UI元素...")
        
        try:
            # 创建卡组构建按钮
            self.deck_builder_button = pygame_gui.elements.UIButton(
                relative_rect=self.deck_builder_button_rect,
                text='Constructor de Mazos',
                manager=self.ui_manager,
                object_id='#deck_builder_button'
            )
            
            # 创建对战准备按钮
            self.battle_prep_button = pygame_gui.elements.UIButton(
                relative_rect=self.battle_prep_button_rect,
                text='Preparar Batalla',
                manager=self.ui_manager,
                object_id='#battle_prep_button'
            )
            
            print("✅ UI元素创建完成")
            
        except Exception as e:
            print(f"❌ 创建UI元素时出错: {e}")
    
    def handle_event(self, event) -> Optional[str]:
        """
        处理事件
        
        Args:
            event: pygame事件
            
        Returns:
            事件处理结果
        """
        # 处理按钮点击事件
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.deck_builder_button:
                print("🏗️ 卡组构建按钮被点击")
                self._open_deck_builder()
                return "deck_builder_clicked"
                
            elif event.ui_element == self.battle_prep_button:
                print("⚔️ 对战准备按钮被点击")
                self._open_battle_prep()
                return "battle_prep_clicked"
        
        # 处理鼠标悬停效果
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
        
        return None
    
    def _handle_mouse_motion(self, mouse_pos):
        """处理鼠标移动事件"""
        # 检查卡组构建按钮悬停
        prev_hover = self.button_hover_states['deck_builder']
        self.button_hover_states['deck_builder'] = self.deck_builder_button_rect.collidepoint(mouse_pos)
        if prev_hover != self.button_hover_states['deck_builder']:
            print(f"🎯 卡组构建按钮悬停: {self.button_hover_states['deck_builder']}")
        
        # 检查对战准备按钮悬停
        prev_hover = self.button_hover_states['battle_prep']
        self.button_hover_states['battle_prep'] = self.battle_prep_button_rect.collidepoint(mouse_pos)
        if prev_hover != self.button_hover_states['battle_prep']:
            print(f"🎯 对战准备按钮悬停: {self.button_hover_states['battle_prep']}")
    
    def _open_deck_builder(self):
        """打开卡组构建窗口"""
        if self.active_windows['deck_builder'] is None:
            try:
                from game.scenes.windows.battle.deck_builder.deck_builder_window import DeckBuilderWindow
                
                # 创建窗口位置和大小
                window_width = int(800 * self.scale_factor)
                window_height = int(600 * self.scale_factor)
                window_x = (self.screen_width - window_width) // 2
                window_y = (self.screen_height - window_height) // 2
                
                window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
                
                # 创建卡组构建窗口
                self.active_windows['deck_builder'] = DeckBuilderWindow(
                    rect=window_rect,
                    ui_manager=self.ui_manager,
                    game_manager=self.game_manager
                )
                
                print("🏗️ 卡组构建窗口已打开")
                self.current_state = "deck_building"
                
                if self.on_deck_builder_click:
                    self.on_deck_builder_click()
                    
            except Exception as e:
                print(f"❌ 打开卡组构建窗口失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️ 卡组构建窗口已经打开")
    
    def _open_battle_prep(self):
        """打开对战准备窗口"""
        if self.active_windows['battle_prep'] is None:
            try:
                from game.scenes.windows.battle.battle_prep.battle_prep_window import BattlePrepWindow
                from game.core.battle.battle_controller import BattleController
                
                # 创建战斗控制器（如果还没有）
                if not hasattr(self, 'battle_controller'):
                    self.battle_controller = BattleController(self.game_manager)
                
                # 创建窗口位置和大小
                window_width = int(600 * self.scale_factor)
                window_height = int(500 * self.scale_factor)
                window_x = (self.screen_width - window_width) // 2
                window_y = (self.screen_height - window_height) // 2
                
                window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
                
                # 创建对战准备窗口
                battle_prep_window = BattlePrepWindow(
                    rect=window_rect,
                    ui_manager=self.ui_manager,
                    game_manager=self.game_manager,
                    battle_controller=self.battle_controller
                )
                
                # 设置战斗开始回调
                battle_prep_window.set_battle_start_callback(self._on_battle_started)
                
                self.active_windows['battle_prep'] = battle_prep_window
                
                print("⚔️ 对战准备窗口已打开")
                self.current_state = "battle_prep"
                
                if self.on_battle_prep_click:
                    self.on_battle_prep_click()
                    
            except Exception as e:
                print(f"❌ 打开对战准备窗口失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("⚠️ 对战准备窗口已经打开")
    
    def _on_battle_started(self, battle_id: int):
        """处理战斗开始回调"""
        print(f"🎮 战斗已开始，ID: {battle_id}")
        self.current_state = "in_battle"
        
        # 关闭所有窗口
        self.close_all_windows()
        
        # 通知父组件战斗已开始
        if self.on_battle_started:
            self.on_battle_started(battle_id)
    
    def get_battle_controller(self):
        """获取战斗控制器"""
        if not self.battle_controller:
            from game.core.battle.battle_controller import BattleController
            self.battle_controller = BattleController(self.game_manager)
        return self.battle_controller
    
    def is_battle_active(self) -> bool:
        """检查是否有活跃的战斗"""
        return (self.battle_controller and 
                self.battle_controller.is_battle_active())
    
    def get_current_battle_state(self):
        """获取当前战斗状态"""
        if self.battle_controller:
            return self.battle_controller.get_current_state()
        return None
    
    def close_all_windows(self):
        """关闭所有弹出窗口"""
        print("🚪 关闭所有战斗页面窗口...")
        
        for window_name, window in self.active_windows.items():
            if window and hasattr(window, 'kill'):
                window.kill()
                self.active_windows[window_name] = None
                print(f"   ✅ 关闭 {window_name} 窗口")
        
        self.current_state = "lobby"
    
    def update(self, dt):
        """更新页面状态"""
        # 更新窗口状态
        for window_name, window in self.active_windows.items():
            if window and hasattr(window, 'update'):
                window.update(dt)
    
    def draw(self, screen):
        """绘制页面内容"""
        # 绘制装饰背景
        self._draw_decoration_background(screen)
        
        # 绘制Logo
        self._draw_logo(screen)
        
        # 绘制按钮装饰效果
        self._draw_button_effects(screen)
        
        # 绘制状态信息
        self._draw_status_info(screen)
    
    def _draw_decoration_background(self, screen):
        """绘制装饰背景"""
        if self.decoration_image:
            screen.blit(self.decoration_image, self.decoration_rect)
        else:
            # 如果没有装饰图片，绘制渐变背景
            decoration_surface = pygame.Surface((self.decoration_rect.width, self.decoration_rect.height))
            
            # 战斗主题渐变：深蓝到紫色
            top_color = (25, 35, 70)      # 深蓝
            bottom_color = (60, 25, 85)   # 深紫
            
            for y in range(self.decoration_rect.height):
                ratio = y / self.decoration_rect.height
                r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
                g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
                b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
                
                pygame.draw.line(decoration_surface, (r, g, b), (0, y), (self.decoration_rect.width, y))
            
            screen.blit(decoration_surface, self.decoration_rect)
            
            # 添加一些装饰元素
            self._draw_decoration_effects(screen)
    
    def _draw_decoration_effects(self, screen):
        """绘制装饰效果"""
        # 绘制一些简单的装饰图案
        center_x = self.decoration_rect.centerx
        center_y = self.decoration_rect.centery
        
        # 战斗图标（剑交叉）
        sword_color = (200, 180, 120)  # 金色
        sword_width = int(8 * self.scale_factor)
        sword_length = int(100 * self.scale_factor)
        
        # 左剑（倾斜45度）
        start_1 = (center_x - sword_length // 2, center_y - sword_length // 2)
        end_1 = (center_x + sword_length // 2, center_y + sword_length // 2)
        
        # 右剑（倾斜-45度）
        start_2 = (center_x + sword_length // 2, center_y - sword_length // 2)
        end_2 = (center_x - sword_length // 2, center_y + sword_length // 2)
        
        pygame.draw.line(screen, sword_color, start_1, end_1, sword_width)
        pygame.draw.line(screen, sword_color, start_2, end_2, sword_width)
        
        # 中心圆环
        pygame.draw.circle(screen, sword_color, (center_x, center_y), int(20 * self.scale_factor), int(4 * self.scale_factor))
    
    def _draw_logo(self, screen):
        """绘制Logo"""
        if self.logo_image:
            screen.blit(self.logo_image, self.logo_rect)
        else:
            # 如果没有Logo图片，绘制文字Logo
            font_size = int(36 * self.scale_factor)
            font = pygame.font.SysFont("arial", font_size, bold=True)
            
            # 主标题
            title_text = "POKEMON BATTLE"
            title_surface = font.render(title_text, True, (255, 255, 255))
            
            # 副标题
            subtitle_font = pygame.font.SysFont("arial", int(18 * self.scale_factor))
            subtitle_text = "TCG Arena"
            subtitle_surface = subtitle_font.render(subtitle_text, True, (200, 200, 200))
            
            # 绘制阴影
            shadow_offset = int(2 * self.scale_factor)
            shadow_surface = font.render(title_text, True, (50, 50, 50))
            screen.blit(shadow_surface, (self.logo_rect.x + shadow_offset, self.logo_rect.y + shadow_offset))
            
            # 绘制主文字
            screen.blit(title_surface, self.logo_rect)
            
            # 绘制副标题
            subtitle_y = self.logo_rect.bottom - subtitle_surface.get_height()
            screen.blit(subtitle_surface, (self.logo_rect.x, subtitle_y))
    
    def _draw_button_effects(self, screen):
        """绘制按钮装饰效果"""
        # 为悬停的按钮绘制发光效果
        glow_color = (100, 150, 255, 50)  # 半透明蓝色发光
        
        if self.button_hover_states['deck_builder']:
            self._draw_glow_effect(screen, self.deck_builder_button_rect, glow_color)
        
        if self.button_hover_states['battle_prep']:
            self._draw_glow_effect(screen, self.battle_prep_button_rect, glow_color)
    
    def _draw_glow_effect(self, screen, rect, color):
        """绘制发光效果"""
        glow_surface = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        glow_rect = pygame.Rect(0, 0, rect.width + 20, rect.height + 20)
        
        # 绘制多层发光
        for i in range(3):
            alpha = color[3] // (i + 1)
            glow_color = (*color[:3], alpha)
            
            inflated_rect = glow_rect.inflate(-i * 4, -i * 4)
            pygame.draw.rect(glow_surface, glow_color, inflated_rect, border_radius=10)
        
        screen.blit(glow_surface, (rect.x - 10, rect.y - 10))
    
    def _draw_status_info(self, screen):
        """绘制状态信息"""
        if self.current_state != "lobby":
            font = pygame.font.SysFont("arial", int(24 * self.scale_factor))
            
            status_texts = {
                "deck_building": "Construyendo mazo...",
                "battle_prep": "Preparando batalla...",
                "in_battle": "Batalla en curso..."
            }
            
            status_text = status_texts.get(self.current_state, "")
            if status_text:
                text_surface = font.render(status_text, True, (255, 255, 255))
                
                # 在屏幕底部居中显示
                text_x = (self.screen_width - text_surface.get_width()) // 2
                text_y = self.screen_height - int(100 * self.scale_factor)
                
                # 绘制背景
                bg_rect = pygame.Rect(text_x - 20, text_y - 10, text_surface.get_width() + 40, text_surface.get_height() + 20)
                pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect, border_radius=10)
                
                screen.blit(text_surface, (text_x, text_y))
    
    def resize(self, screen_width: int, screen_height: int):
        """调整页面大小"""
        print(f"📐 调整战斗页面大小: {screen_width}x{screen_height}")
        
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.content_height = screen_height - self.nav_height
        self.scale_factor = min(screen_width / 1920, screen_height / 1080)
        
        # 重新设置布局
        self._setup_ui_layout()
        
        # 重新加载和缩放资源
        self._load_assets()
        
        # 重新创建UI元素
        if self.deck_builder_button:
            self.deck_builder_button.kill()
        if self.battle_prep_button:
            self.battle_prep_button.kill()
            
        self._create_ui_elements()
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理战斗页面资源...")
        
        # 关闭所有窗口
        self.close_all_windows()
        
        # 清理UI元素
        if self.deck_builder_button:
            self.deck_builder_button.kill()
            self.deck_builder_button = None
            
        if self.battle_prep_button:
            self.battle_prep_button.kill()
            self.battle_prep_button = None
        
        print("✅ 战斗页面清理完成")