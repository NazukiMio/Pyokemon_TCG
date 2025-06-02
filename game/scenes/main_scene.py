import pygame
import pygame_gui
import sys
import os

# 导入组件
from game.scenes.home_page import HomePage
from game.ui.navigation_bar import PokemonNavigationGUI
from game.core.message_manager import MessageManager
# from game.ui.toast_message import ToastMessage
from game.core.auth.auth_manager import get_auth_manager
# 导入新的数据库管理器
from game.core.database.database_manager import DatabaseManager

auth = get_auth_manager()
print("测试当前用户 ID：", auth.get_current_user_id())

class MainScene:
    """
    主场景 - 集成主页和导航栏
    包含Pokemon风格的主页、导航栏和弹出窗口系统
    """
    
    def __init__(self, screen, callback=None, *args, **kwargs):
        """初始化主场景"""
        print("🏠 初始化主场景...")
        
        self.screen = screen
        self.callback = callback
        self.auth = get_auth_manager()
        self.user = self.auth.get_user_info()

        if not self.user:
            raise Exception("⛔ 未经授权访问：用户未登录")
        
        print(f"✅ 当前用户: {self.user['username']} (ID: {self.user['id']})")
        
        # 获取屏幕尺寸
        self.screen_width, self.screen_height = screen.get_size()
        
        # 缩放因子
        self.scale_factor = min(self.screen_width / 1920, self.screen_height / 1080)
        
        # 组件管理器
        self.message_manager = MessageManager()
        
        # UI管理器
        self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))
        self.ui_manager.set_window_resolution((self.screen_width, self.screen_height))

        # 通用背景色 - 浅蓝灰色渐变
        self.background_colors = {
            'top': (240, 245, 251),     # 浅蓝白色
            'bottom': (229, 231, 235),  # 浅灰色
            'gradient_steps': 100       # 渐变步数
        }
        
        # 创建Pokemon风格导航栏
        self.nav_bar = PokemonNavigationGUI(self.screen_width, self.screen_height)
        
        # 创建主页
        self.home_page = HomePage(
            self.screen_width, 
            self.screen_height, 
            self.ui_manager,  # 传入UI管理器
            self.nav_bar.height  # 使用导航栏的高度
        )

        # 确保数据库管理器已初始化（可选，因为HomePage会处理）
        # 如果需要在MainScene层面访问数据库，可以添加：
        # self.db_manager = DatabaseManager()
        # self.db_manager.initialize_database()
        
        # 当前页面
        self.current_page = 'home'
        
        # Toast消息
        self.toast_message = None
        
        # 设置回调
        self.setup_callbacks()
        
        print("✅ 主场景初始化完成")
        print(f"[调试] UIManager id in MainScene: {id(self.ui_manager)}")
    
    def setup_callbacks(self):
        """设置回调函数"""
        
        # 卡包点击回调
        def on_pack_click(pack_index, pack_type):
            print(f"🎴 打开卡包窗口 {pack_index + 1}: {pack_type}")
            print("   📦 弹出卡包选择界面...")
            # 窗口已经通过 show_package_window 显示
        
        # 商店点击回调
        def on_shop_click():
            print("🛒 打开现代化商店窗口")
            self.home_page.show_tienda_window() 
            print("   🛍️ 显示毛玻璃风格商店界面")
            # 窗口已经通过 show_tienda_window 显示
        
        # 魔法选择点击回调
        def on_magic_click():
            print("✨ 打开魔法选择窗口")
            print("   ⚔️ 显示可用的挑战和战斗")
            # 窗口已经通过 show_emagica_window 显示
        
        # 精灵点击回调
        def on_sprite_click():
            print("🦄 切换精灵")
            print("   🎲 开始动画序列：抖动→淡出→切换→淡入")
        
        # 导航栏点击回调
        def on_navigation_click(nav_id: str):
            self.current_page = nav_id
            print(f"🧭 导航到: {nav_id}")
            
            # 当切换页面时关闭所有弹出窗口
            if nav_id != 'home':
                self.home_page.close_all_windows()
                print("   🚪 关闭所有弹出窗口")
            
            # 根据导航选择，可能需要切换到其他场景
            if nav_id == 'menu':
                # 切换到设置菜单场景
                if self.callback:
                    self.callback("settings")
            elif nav_id == 'battle':
                # 切换到战斗场景
                if self.callback:
                    self.callback("battle")
            # 其他页面暂时保持在当前场景内显示占位符
            
            page_descriptions = {
                'home': '🏠 主页 - 卡包管理和快速操作',
                'pokedex': '📖 图鉴 - 查看收集的卡牌',
                'social': '👥 社交 - 与其他玩家互动',
                'battle': '⚔️ 战斗 - 进行卡牌对战',
                'menu': '☰ 菜单 - 游戏设置和选项'
            }
            
            description = page_descriptions.get(nav_id, '未知页面')
            print(f"   {description}")
        
        # 设置所有回调
        self.home_page.on_pack_click = on_pack_click
        self.home_page.on_shop_click = on_shop_click
        self.home_page.on_magic_click = on_magic_click
        self.home_page.on_sprite_click = on_sprite_click
        self.nav_bar.on_navigation_click = on_navigation_click
        
        # 设置卡包数据
        self.home_page.set_pack_data(0, "basic_pack", "Sobre Básico")
        self.home_page.set_pack_data(1, "advanced_pack", "Sobre Avanzado") 
        self.home_page.set_pack_data(2, "legendary_pack", "Sobre Legendario")
    
    def create_gradient_background(self):
        """创建渐变背景"""
        gradient_surface = pygame.Surface((self.screen_width, self.screen_height))
        
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(self.background_colors['top'][0] * (1 - ratio) + self.background_colors['bottom'][0] * ratio)
            g = int(self.background_colors['top'][1] * (1 - ratio) + self.background_colors['bottom'][1] * ratio)
            b = int(self.background_colors['top'][2] * (1 - ratio) + self.background_colors['bottom'][2] * ratio)
            
            pygame.draw.line(gradient_surface, (r, g, b), (0, y), (self.screen_width, y))
        
        return gradient_surface
    
    def draw_page_placeholder(self, page_name: str):
        """绘制其他页面的占位内容"""
        content_height = self.screen_height - self.nav_bar.height
        
        # 页面标题
        title_font = pygame.font.SysFont("arial", int(48 * self.scale_factor), bold=True)
        title_text = f"Página de {page_name.title()}"
        title_surface = title_font.render(title_text, True, (74, 85, 104))
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, content_height // 2 - 80))
        
        # 标题阴影
        shadow_surface = title_font.render(title_text, True, (200, 200, 220))
        shadow_rect = shadow_surface.get_rect(center=(title_rect.centerx + 2, title_rect.centery + 2))
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(title_surface, title_rect)
        
        # 描述文本
        desc_texts = {
            'pokedex': 'Aquí verás todas las cartas que has coleccionado',
            'social': 'Conecta con amigos e intercambia cartas',
            'battle': 'Desafía a otros entrenadores en combates épicos',
            'menu': 'Configura tu experiencia de juego'
        }
        
        desc_text = desc_texts.get(page_name, 'Esta página será implementada próximamente')
        desc_font = pygame.font.SysFont("arial", int(24 * self.scale_factor))
        desc_surface = desc_font.render(desc_text, True, (113, 128, 150))
        desc_rect = desc_surface.get_rect(center=(self.screen_width // 2, title_rect.bottom + 30))
        self.screen.blit(desc_surface, desc_rect)
        
        # 返回主页提示
        hint_font = pygame.font.SysFont("arial", int(18 * self.scale_factor))
        hint_text = "Haz clic en 'Inicio' para volver a la página principal"
        hint_surface = hint_font.render(hint_text, True, (160, 174, 192))
        hint_rect = hint_surface.get_rect(center=(self.screen_width // 2, desc_rect.bottom + 50))
        self.screen.blit(hint_surface, hint_rect)
    
    def handle_event(self, event):
        """处理事件"""
        # print(f"[事件追踪] 收到事件: {event}")
        # 处理pygame_gui事件
        self.ui_manager.process_events(event)

        if event.type == pygame.QUIT:
            if self.callback:
                self.callback("exit")
            return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # ESC键：先尝试关闭窗口，如果没有窗口则退出
                has_windows = any(window and window.is_visible 
                                for window in self.home_page.active_windows.values())
                if has_windows:
                    self.home_page.close_all_windows()
                    print("🚪 ESC - 关闭所有弹出窗口")
                else:
                    if self.callback:
                        self.callback("exit")
                    print("🚪 ESC - 退出程序")
            
            elif event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
                print("🖥️ 切换全屏模式")
            
            elif event.key == pygame.K_r:
                # R键重新随机选择卡包和精灵
                if self.current_page == 'home':
                    self.home_page.refresh_pack_selection()
                    if self.home_page.sprite_fade_state == "normal":
                        self.home_page.sprite_fade_state = "shaking"
                        self.home_page.sprite_shake_timer = 200
                    print("🎲 重新随机选择卡包和精灵")
            
            elif event.key == pygame.K_w:
                # W键关闭所有弹出窗口
                self.home_page.close_all_windows()
                print("🚪 W - 强制关闭所有弹出窗口")
            
            elif event.key == pygame.K_1:
                # 快捷键切换到主页
                self.nav_bar.set_active('home')
                self.current_page = 'home'
                print("🏠 快捷键切换到主页")
            
            elif event.key == pygame.K_2:
                # 快捷键切换到图鉴
                self.nav_bar.set_active('pokedex')
                self.current_page = 'pokedex'
                self.home_page.close_all_windows()
                print("📖 快捷键切换到图鉴")
            
            elif event.key == pygame.K_t:
                # T键测试商店窗口
                if self.current_page == 'home':
                    self.home_page.show_tienda_window()
                    print("🛍️ T - 测试打开商店窗口")
            
            elif event.key == pygame.K_m:
                # M键测试魔法窗口
                if self.current_page == 'home':
                    self.home_page.show_emagica_window()
                    print("✨ M - 测试打开魔法选择窗口")
            
            elif event.key == pygame.K_p:
                # P键测试卡包窗口
                if self.current_page == 'home':
                    self.home_page.show_package_window(0, "test_pack")
                    print("📦 P - 测试打开卡包窗口")
        
        elif event.type == pygame.VIDEORESIZE:
            # 调整窗口大小
            self.screen_width, self.screen_height = event.size
            
            # 调整组件大小
            self.nav_bar.resize(self.screen_width, self.screen_height)
            self.home_page.resize(self.screen_width, self.screen_height)
            self.ui_manager.set_window_resolution(event.size)
            
            # 更新缩放因子
            self.scale_factor = min(self.screen_width / 1920, self.screen_height / 1080)
            
            print(f"📐 窗口调整: {self.screen_width}x{self.screen_height}")
        
        # 导航栏事件处理
        nav_result = self.nav_bar.handle_event(event)
        
        # 主页事件处理（仅在主页时）
        if self.current_page == 'home':
            # pygame_gui事件处理（包括窗口事件）
            ui_result = self.home_page.handle_ui_event(event)
            
            # 记录窗口操作
            if ui_result:
                if ui_result.startswith("package_"):
                    print(f"📦 卡包窗口操作: {ui_result}")
                elif ui_result.startswith("e_magica_"):
                    print(f"✨ 魔法窗口操作: {ui_result}")
                elif ui_result.startswith("tienda_"):
                    print(f"🛍️ 商店窗口操作: {ui_result}")
            
            # 精灵点击处理
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.home_page.sprite_area['rect'].collidepoint(event.pos):
                    if self.home_page.sprite_fade_state == "normal":
                        self.home_page.sprite_fade_state = "shaking"
                        self.home_page.sprite_shake_timer = 200
                        if self.home_page.on_sprite_click:
                            self.home_page.on_sprite_click()
            
            elif event.type == pygame.MOUSEMOTION:
                self.home_page.handle_mouse_motion(event.pos)
        
        return True
    
    def update(self, dt):
        """更新场景"""
        # 更新UI管理器
        self.ui_manager.update(dt)
        
        # 更新导航栏
        self.nav_bar.update(dt)
        
        # 更新主页（仅在主页时）
        if self.current_page == 'home':
            # 主页有自己的更新逻辑，但我们需要确保兼容性
            pass
        
        # 更新消息管理器
        self.message_manager.update(dt)
        
        # 更新Toast消息
        if self.toast_message and not self.toast_message.update():
            self.toast_message = None
        
        return True
    
    def draw(self):
        """绘制场景"""
        # 计算时间增量（用于动画）
        time_delta = pygame.time.get_ticks() / 1000.0
        
        # 绘制统一的渐变背景
        gradient_bg = self.create_gradient_background()
        self.screen.blit(gradient_bg, (0, 0))
        
        # 根据当前页面绘制内容
        if self.current_page == 'home':
            # 绘制主页内容（传入time_delta）
            self.home_page.draw(self.screen, time_delta)
        else:
            # 绘制其他页面的占位内容
            page_names = {
                'pokedex': 'Pokédex',
                'social': 'Social',
                'battle': 'Batalla', 
                'menu': 'Menú'
            }
            page_name = page_names.get(self.current_page, self.current_page)
            self.draw_page_placeholder(page_name)
        
        # 绘制导航栏（始终在最上层）
        self.nav_bar.draw(self.screen)
        
        # 绘制消息
        self.message_manager.draw(self.screen, self.scale_factor)
        
        # 绘制Toast消息
        if self.toast_message:
            self.toast_message.draw(
                self.screen, 
                self.screen_width // 2, 
                int(self.screen_height * 0.85), 
                self.scale_factor
            )
        
        # 绘制pygame-gui界面
        self.ui_manager.draw_ui(self.screen)
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理主场景资源...")
        
        if hasattr(self.home_page, 'cleanup'):
            self.home_page.cleanup()
        
        if hasattr(self.nav_bar, 'cleanup'):
            self.nav_bar.cleanup()
        
        print("✅ 主场景资源清理完成")