import pygame
import pygame_gui
import sys
import os

# 导入组件
from game.scenes.home_page import HomePage
from game.ui.navigation_bar import PokemonNavigationGUI
from game.core.message_manager import MessageManager
from game.core.auth.auth_manager import get_auth_manager
from data.card_data_manager import CardDataManager
from data.database_extensions import DatabaseManagerExtensions

# 导入窗口组件
try:
    from game.scenes.windows.modern_battle_window import ModernBattleWindow, create_battle_window, start_ai_battle
    from game.scenes.windows.modern.modern_dex_window import ModernDexWindow
    from game.scenes.windows.modern.modern_settings_window import ModernSettingsWindow
    from game.scenes.windows.tienda import ModernTiendaWindow
    from game.scenes.windows.package import ModernPackageWindow
    MODERN_WINDOWS_AVAILABLE = True
    print("✅ 现代化窗口模块导入成功")
except ImportError as e:
    print(f"⚠️ 现代化窗口模块导入失败: {e}")
    MODERN_WINDOWS_AVAILABLE = False

auth = get_auth_manager()

class MainScene:
    """
    重构后的主场景 - 集成主页和导航栏
    包含Pokemon风格的主页、导航栏和现代化窗口系统
    """
    
    def __init__(self, screen, callback=None, *args, **kwargs):
        """初始化主场景"""
        print("🏠 初始化主场景...")
        
        self.screen = screen
        self.callback = callback
        self.auth = auth
        self.user = self.auth.get_user_info()

        if not self.user:
            raise Exception("⛔ 未经授权访问：用户未登录")
        
        print(f"✅ 当前用户: {self.user['username']} (ID: {self.user['id']})")
        
        # 获取屏幕尺寸
        self.screen_width, self.screen_height = screen.get_size()
        
        # 缩放因子
        self.scale_factor = min(self.screen_width / 1920, self.screen_height / 1080)
        
        # 初始化数据管理器
        self._init_data_managers()
        
        # 组件管理器
        self.message_manager = MessageManager()
        
        # UI管理器
        self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))
        
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
            self.nav_bar.height  # 使用导航栏的高度
        )
        
        # 窗口管理系统
        self.active_windows = {
            'battle': None,
            'dex': None,
            'settings': None,
            'shop': None,  # 原有的商店窗口
            'package': None,  # 原有的卡包窗口
            'e_magica': None  # 原有的魔法窗口
        }
        
        # 当前页面
        self.current_page = 'home'
        
        # 场景状态
        self.scene_state = 'active'  # active, paused, transitioning
        
        # 设置回调
        self.setup_callbacks()
        
        print("✅ 主场景初始化完成")
    
    def _init_data_managers(self):
        """初始化数据管理器"""
        try:
            # 初始化卡片数据管理器
            self.card_data_manager = CardDataManager()
            
            # 初始化数据库扩展
            if hasattr(self.auth, 'database_manager'):
                self.database_extensions = DatabaseManagerExtensions(self.auth.database_manager)
            else:
                self.database_extensions = None
                print("⚠️ 数据库管理器不可用")
            
            print("✅ 数据管理器初始化完成")
            
        except Exception as e:
            print(f"❌ 数据管理器初始化失败: {e}")
            self.card_data_manager = None
            self.database_extensions = None
    
    def setup_callbacks(self):
        """设置回调函数"""
        
        # def _handle_window_request(self, action: str, data: dict) -> bool:
        #     """
        #     处理来自 HomePage 的窗口请求
        #     返回 True 表示已处理，False 表示忽略（将回退使用 legacy 版本）
        #     """
        #     print(f"[窗口管理器] 请求 {action}，数据: {data}")
        #     return False  # 暂不拦截，让 home_page 使用 legacy 弹窗逻辑

        # 卡包点击回调
        def on_pack_click(pack_index, pack_type):
            print(f"🎴 打开卡包窗口 {pack_index + 1}: {pack_type}")
            self.show_package_window(pack_type)
            # 原有的卡包窗口逻辑保持不变
        
        # 商店点击回调
        def on_shop_click():
            print("🛒 打开商店窗口")
            self.show_shop_window()
            # 原有的商店窗口逻辑保持不变
        
        # 魔法选择点击回调
        def on_magic_click():
            print("✨ 打开魔法选择窗口")
            # 原有的魔法窗口逻辑保持不变
        
        # 精灵点击回调
        def on_sprite_click():
            print("🦄 切换精灵")
            print("   🎲 开始动画序列：抖动→淡出→切换→淡入")
        
        # 导航栏点击回调
        def on_navigation_click(nav_id: str):
            result = self.handle_navigation_change(nav_id)
            if result:
                print(f"🧭 导航切换完成: {nav_id}")
        
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
    
    def handle_navigation_change(self, nav_id: str) -> bool:
        """
        处理导航切换
        
        Args:
            nav_id: 导航ID
            
        Returns:
            bool: 是否成功处理
        """
        old_page = self.current_page
        self.current_page = nav_id
        
        print(f"🧭 导航从 {old_page} 切换到 {nav_id}")
        
        # 关闭所有弹出窗口
        self.close_all_windows()
        
        # 根据导航选择处理
        if nav_id == 'home':
            # 主页不需要特殊处理
            pass
            
        elif nav_id == 'pokedex':
            # 打开图鉴窗口
            self.show_dex_window()
            
        elif nav_id == 'battle':
            # 打开对战选择或直接开始AI对战
            self.show_battle_options()
            
        elif nav_id == 'social':
            # 显示社交页面占位符
            self.message_manager.add_success("社交功能即将推出", 3.0)
            
        elif nav_id == 'menu':
            # 打开设置窗口
            self.show_settings_window()
        
        # 更新页面描述
        page_descriptions = {
            'home': '🏠 主页 - 卡包管理和快速操作',
            'pokedex': '📖 图鉴 - 查看收集的卡牌',
            'social': '👥 社交 - 与其他玩家互动',
            'battle': '⚔️ 战斗 - 进行卡牌对战',
            'menu': '⚙️ 设置 - 游戏配置和账户管理'
        }
        
        description = page_descriptions.get(nav_id, '未知页面')
        print(f"   {description}")
        
        return True
    
    def show_package_window(self, pack_type: str = "basic"):
        """显示开包窗口"""
        if not MODERN_WINDOWS_AVAILABLE:
            self.message_manager.add_warning("开包功能暂时不可用", 3.0)
            return

        if self.active_windows['package']:
            self.active_windows['package'].close()

        try:
            self.active_windows['package'] = ModernPackageWindow(
                self.screen_width,
                self.screen_height,
                self.ui_manager,
                pack_type=pack_type,
                user_data=self._get_enhanced_user_data(),
                message_manager=self.message_manager,
                card_data_manager=self.card_data_manager,
                database_manager=getattr(self.auth, 'database_manager', None)
            )
            self.active_windows['package'].on_close = lambda: self._close_window('package')

            print(f"📦 {pack_type} 卡包窗口已打开")
            self.message_manager.add_info("开包窗口已打开", 2.0)

        except Exception as e:
            print(f"❌ 打开开包窗口失败: {e}")
            self.message_manager.add_error("无法打开卡包窗口", 3.0)

    def show_shop_window(self):
        """显示商店窗口"""
        if not MODERN_WINDOWS_AVAILABLE:
            self.message_manager.add_warning("商店功能暂时不可用", 3.0)
            return

        if self.active_windows['shop']:
            self.active_windows['shop'].close()

        try:
            self.active_windows['shop'] = ModernTiendaWindow(
                self.screen_width,
                self.screen_height,
                self.ui_manager,
                user_data=self._get_enhanced_user_data(),
                message_manager=self.message_manager,
                database_manager=getattr(self.auth, 'database_manager', None)
            )
            self.active_windows['shop'].on_close = lambda: self._close_window('shop')

            print("🛍️ 商店窗口已打开")
            self.message_manager.add_info("商店已打开", 2.0)

        except Exception as e:
            print(f"❌ 打开商店窗口失败: {e}")
            self.message_manager.add_error("无法打开商店", 3.0)


    def show_dex_window(self):
        """显示图鉴窗口"""
        if not MODERN_WINDOWS_AVAILABLE:
            self.message_manager.add_warning("图鉴功能暂时不可用", 3.0)
            return
        
        if self.active_windows['dex']:
            self.active_windows['dex'].close()
        
        try:
            # 获取用户数据（包含卡片收藏）
            user_data = self._get_enhanced_user_data()
            
            self.active_windows['dex'] = ModernDexWindow(
                self.screen_width,
                self.screen_height,
                self.ui_manager,
                user_data,
                self.card_data_manager,
                self.message_manager
            )
            
            self.active_windows['dex'].on_close = lambda: self._close_window('dex')
            
            print("📚 图鉴窗口已打开")
            self.message_manager.add_info("图鉴已打开", 2.0)
            
        except Exception as e:
            print(f"❌ 打开图鉴窗口失败: {e}")
            self.message_manager.add_error("无法打开图鉴", 3.0)
    
    def show_battle_options(self):
        """显示对战选项"""
        if not MODERN_WINDOWS_AVAILABLE:
            self.message_manager.add_warning("对战功能暂时不可用", 3.0)
            return
        
        # 简化：直接开始AI对战
        self.start_ai_battle()
    
    def start_ai_battle(self, difficulty: str = "normal"):
        """开始AI对战"""
        if self.active_windows['battle']:
            self.active_windows['battle'].close()
        
        try:
            # 创建用户卡组（简化版）
            from game.cards.deck_manager import Deck
            user_deck = Deck("我的卡组")
            
            # TODO: 从用户收藏中构建卡组
            # 目前使用空卡组作为占位符
            
            # 获取用户数据
            user_data = {
                'user_id': self.user['id'],
                'username': self.user['username']
            }
            
            self.active_windows['battle'] = start_ai_battle(
                self.screen_width,
                self.screen_height,
                self.ui_manager,
                user_deck,
                user_data,
                self.message_manager,
                difficulty
            )
            
            self.active_windows['battle'].on_close = lambda: self._close_window('battle')
            self.active_windows['battle'].on_battle_end = self._on_battle_end
            
            print(f"⚔️ AI对战已开始 (难度: {difficulty})")
            self.message_manager.add_success("对战开始！", 2.0)
            
        except Exception as e:
            print(f"❌ 开始AI对战失败: {e}")
            self.message_manager.add_error("无法开始对战", 3.0)
    
    def show_settings_window(self):
        """显示设置窗口"""
        if not MODERN_WINDOWS_AVAILABLE:
            self.message_manager.add_warning("设置功能暂时不可用", 3.0)
            return
        
        if self.active_windows['settings']:
            self.active_windows['settings'].close()
        
        try:
            # 获取用户数据
            user_data = self._get_enhanced_user_data()
            
            self.active_windows['settings'] = ModernSettingsWindow(
                self.screen_width,
                self.screen_height,
                self.ui_manager,
                user_data,
                self.message_manager,
                self.auth.database_manager if hasattr(self.auth, 'database_manager') else None,
                self.auth
            )
            
            self.active_windows['settings'].on_close = lambda: self._close_window('settings')
            self.active_windows['settings'].on_logout = self._handle_logout
            self.active_windows['settings'].on_exit_game = self._handle_exit_game
            
            print("⚙️ 设置窗口已打开")
            self.message_manager.add_info("设置已打开", 2.0)
            
        except Exception as e:
            print(f"❌ 打开设置窗口失败: {e}")
            self.message_manager.add_error("无法打开设置", 3.0)
    
    def _get_enhanced_user_data(self) -> dict:
        """获取增强的用户数据"""
        enhanced_data = self.user.copy()
        
        # 添加卡片收藏信息
        if self.database_extensions:
            try:
                user_cards = self.database_extensions.get_user_cards(self.user['id'])
                enhanced_data['card_collection'] = user_cards
                
                collection_summary = self.database_extensions.get_user_card_collection_summary(self.user['id'])
                enhanced_data.update(collection_summary)
                
            except Exception as e:
                print(f"⚠️ 获取用户卡片数据失败: {e}")
                enhanced_data['card_collection'] = []
        
        # 添加默认值
        enhanced_data.setdefault('coins', 1000)
        enhanced_data.setdefault('pack_chances', {'basic': 0, 'premium': 0, 'legendary': 0})
        
        return enhanced_data
    
    def _close_window(self, window_name: str):
        """关闭指定窗口"""
        if window_name in self.active_windows:
            self.active_windows[window_name] = None
            print(f"🚪 已关闭窗口: {window_name}")
    
    def _on_battle_end(self, winner):
        """对战结束回调"""
        print(f"🏆 对战结束，获胜者: {winner.name}")
        
        # 更新用户数据
        if self.database_extensions:
            try:
                # 这里可以添加对战结果记录逻辑
                pass
            except Exception as e:
                print(f"⚠️ 保存对战结果失败: {e}")
        
        self.message_manager.add_success(f"对战结束！获胜者: {winner.name}", 5.0)
    
    def _handle_logout(self):
        """处理登出"""
        print("🚪 用户请求登出")
        self.close_all_windows()
        
        # 执行登出
        if self.auth.logout():
            if self.callback:
                self.callback("logout")
        else:
            self.message_manager.add_error("登出失败", 3.0)
    
    def _handle_exit_game(self):
        """处理退出游戏"""
        print("👋 用户请求退出游戏")
        if self.callback:
            self.callback("exit")
    
    def close_all_windows(self):
        """关闭所有窗口"""
        # 关闭现代化窗口
        for window_name, window in self.active_windows.items():
            if window and hasattr(window, 'close'):
                try:
                    window.close()
                except Exception as e:
                    print(f"⚠️ 关闭窗口 {window_name} 时出错: {e}")
        
        # 重置窗口字典
        for key in self.active_windows.keys():
            self.active_windows[key] = None
        
        # 关闭主页的原有窗口
        if hasattr(self.home_page, 'close_all_windows'):
            self.home_page.close_all_windows()
        
        print("🚪 所有窗口已关闭")
    
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
            'pokedex': 'Usa la barra de navegación para abrir el Pokédex',
            'social': 'Funciones sociales en desarrollo',
            'battle': 'Usa la barra de navegación para iniciar combates',
            'menu': 'Usa la barra de navegación para abrir configuración'
        }
        
        desc_text = desc_texts.get(page_name, 'Esta página será implementada próximamente')
        desc_font = pygame.font.SysFont("arial", int(24 * self.scale_factor))
        desc_surface = desc_font.render(desc_text, True, (113, 128, 150))
        desc_rect = desc_surface.get_rect(center=(self.screen_width // 2, title_rect.bottom + 30))
        self.screen.blit(desc_surface, desc_rect)
    
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.QUIT:
            if self.callback:
                self.callback("exit")
            return True
        
        elif event.type == pygame.KEYDOWN:
            return self._handle_keydown(event)
        
        elif event.type == pygame.VIDEORESIZE:
            return self._handle_resize(event)
        
        # 处理现代化窗口事件
        window_result = self._handle_window_events(event)
        if window_result:
            return True
        
        # 导航栏事件处理
        nav_result = self.nav_bar.handle_event(event)
        
        # 主页事件处理（仅在主页时）
        if self.current_page == 'home':
            self._handle_home_page_events(event)
        
        # 处理pygame_gui事件
        self.ui_manager.process_events(event)
        
        return True
    
    def _handle_keydown(self, event):
        """处理按键事件"""
        if event.key == pygame.K_ESCAPE:
            # ESC键：先尝试关闭窗口，如果没有窗口则退出
            has_windows = any(window is not None for window in self.active_windows.values())
            if has_windows:
                self.close_all_windows()
                print("🚪 ESC - 关闭所有窗口")
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
        
        # 数字键快捷导航
        elif event.key == pygame.K_1:
            self.nav_bar.set_active('home')
            self.handle_navigation_change('home')
        elif event.key == pygame.K_2:
            self.nav_bar.set_active('pokedex')
            self.handle_navigation_change('pokedex')
        elif event.key == pygame.K_3:
            self.nav_bar.set_active('social')
            self.handle_navigation_change('social')
        elif event.key == pygame.K_4:
            self.nav_bar.set_active('battle')
            self.handle_navigation_change('battle')
        elif event.key == pygame.K_5:
            self.nav_bar.set_active('menu')
            self.handle_navigation_change('menu')
        
        # 测试快捷键
        elif event.key == pygame.K_b and MODERN_WINDOWS_AVAILABLE:
            # B键快速开始AI对战
            self.start_ai_battle()
            print("⚔️ B - 快速开始AI对战")
        
        elif event.key == pygame.K_d and MODERN_WINDOWS_AVAILABLE:
            # D键打开图鉴
            self.show_dex_window()
            print("📚 D - 打开图鉴")
        
        elif event.key == pygame.K_s and MODERN_WINDOWS_AVAILABLE:
            # S键打开设置
            self.show_settings_window()
            print("⚙️ S - 打开设置")
        
        return True
    
    def _handle_resize(self, event):
        """处理窗口大小调整"""
        self.screen_width, self.screen_height = event.size
        
        # 调整组件大小
        self.nav_bar.resize(self.screen_width, self.screen_height)
        self.home_page.resize(self.screen_width, self.screen_height)
        self.ui_manager.set_window_resolution(event.size)
        
        # 更新缩放因子
        self.scale_factor = min(self.screen_width / 1920, self.screen_height / 1080)
        
        # 关闭所有窗口（它们需要重新创建以适应新尺寸）
        self.close_all_windows()
        
        print(f"📐 窗口调整: {self.screen_width}x{self.screen_height}")
        return True
    
    def _handle_window_events(self, event):
        """处理现代化窗口事件"""
        for window_name, window in self.active_windows.items():
            if window and hasattr(window, 'handle_event'):
                try:
                    result = window.handle_event(event)
                    if result:
                        print(f"🪟 窗口 {window_name} 事件: {result}")
                        return True
                except Exception as e:
                    print(f"⚠️ 处理窗口 {window_name} 事件时出错: {e}")
        
        return False
    
    def _handle_home_page_events(self, event):
        """处理主页事件"""
        # pygame_gui事件处理（包括原有窗口事件）
        ui_result = self.home_page.handle_ui_event(event)
        
        # 记录原有窗口操作
        if ui_result:
            if ui_result.startswith("package_"):
                print(f"📦 卡包窗口操作: {ui_result}")
            elif ui_result.startswith("e_magica_"):
                print(f"✨ 魔法窗口操作: {ui_result}")
            elif ui_result.startswith("tienda_"):
                print(f"🛍️ 商店窗口操作: {ui_result}")
        
        # 精灵点击处理
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(self.home_page, 'sprite_area') and self.home_page.sprite_area['rect'].collidepoint(event.pos):
                if self.home_page.sprite_fade_state == "normal":
                    self.home_page.sprite_fade_state = "shaking"
                    self.home_page.sprite_shake_timer = 200
                    if self.home_page.on_sprite_click:
                        self.home_page.on_sprite_click()
        
        elif event.type == pygame.MOUSEMOTION:
            self.home_page.handle_mouse_motion(event.pos)
    
    def update(self, dt):
        """更新场景"""
        # 更新UI管理器
        self.ui_manager.update(dt)
        
        # 更新导航栏
        self.nav_bar.update(dt)
        
        # 更新消息管理器
        self.message_manager.update(dt)
        
        # 更新现代化窗口
        for window_name, window in self.active_windows.items():
            if window and hasattr(window, 'update'):
                try:
                    window.update(dt)
                except Exception as e:
                    print(f"⚠️ 更新窗口 {window_name} 时出错: {e}")
        
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
                'menu': 'Configuración'
            }
            page_name = page_names.get(self.current_page, self.current_page)
            self.draw_page_placeholder(page_name)
        
        # 绘制导航栏（始终在最上层）
        self.nav_bar.draw(self.screen)
        
        # 绘制现代化窗口自定义内容
        for window_name, window in self.active_windows.items():
            if window and hasattr(window, 'draw_custom_content'):
                try:
                    window.draw_custom_content(self.screen)
                except Exception as e:
                    print(f"⚠️ 绘制窗口 {window_name} 自定义内容时出错: {e}")
        
        # 绘制消息
        self.message_manager.draw(self.screen, self.scale_factor)
        
        # 绘制pygame-gui界面（包括窗口UI元素）
        self.ui_manager.draw_ui(self.screen)
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理主场景资源...")
        
        # 关闭所有窗口
        self.close_all_windows()
        
        # 清理主页
        if hasattr(self.home_page, 'cleanup'):
            self.home_page.cleanup()
        
        # 清理导航栏
        if hasattr(self.nav_bar, 'cleanup'):
            self.nav_bar.cleanup()
        
        # 清理数据管理器
        if self.card_data_manager:
            # CardDataManager 的清理方法（如果有的话）
            pass
        
        print("✅ 主场景资源清理完成")
    
    def pause_scene(self):
        """暂停场景（用于场景切换）"""
        self.scene_state = 'paused'
        print("⏸️ 主场景已暂停")
    
    def resume_scene(self):
        """恢复场景"""
        self.scene_state = 'active'
        print("▶️ 主场景已恢复")
    
    def get_scene_state(self) -> str:
        """获取场景状态"""
        return self.scene_state
    
    def get_active_window_count(self) -> int:
        """获取活跃窗口数量"""
        return sum(1 for window in self.active_windows.values() if window is not None)
    
    def has_active_windows(self) -> bool:
        """检查是否有活跃窗口"""
        return self.get_active_window_count() > 0
    
    def get_user_data(self) -> dict:
        """获取用户数据（供外部调用）"""
        return self._get_enhanced_user_data()
    
    def refresh_user_data(self):
        """刷新用户数据"""
        try:
            self.user = self.auth.get_user_info()
            if not self.user:
                print("⚠️ 用户数据丢失，需要重新登录")
                if self.callback:
                    self.callback("logout")
                return False
            
            print("🔄 用户数据已刷新")
            return True
            
        except Exception as e:
            print(f"❌ 刷新用户数据失败: {e}")
            return False
    
    def show_message(self, message: str, message_type: str = "info", duration: float = 3.0):
        """显示消息（供外部调用）"""
        if message_type == "info":
            self.message_manager.add_info(message, duration)
        elif message_type == "success":
            self.message_manager.add_success(message, duration)
        elif message_type == "warning":
            self.message_manager.add_warning(message, duration)
        elif message_type == "error":
            self.message_manager.add_error(message, duration)
        else:
            self.message_manager.add_info(message, duration)
    
    def force_navigation_to(self, nav_id: str):
        """强制导航到指定页面（供外部调用）"""
        self.nav_bar.set_active(nav_id)
        return self.handle_navigation_change(nav_id)
    
    def is_window_open(self, window_name: str) -> bool:
        """检查指定窗口是否打开"""
        return (window_name in self.active_windows and 
                self.active_windows[window_name] is not None)
    
    def get_window(self, window_name: str):
        """获取指定窗口对象"""
        return self.active_windows.get(window_name)
    
    def close_window(self, window_name: str) -> bool:
        """关闭指定窗口（供外部调用）"""
        if window_name in self.active_windows and self.active_windows[window_name]:
            try:
                self.active_windows[window_name].close()
                self.active_windows[window_name] = None
                print(f"🚪 已关闭窗口: {window_name}")
                return True
            except Exception as e:
                print(f"❌ 关闭窗口 {window_name} 失败: {e}")
                return False
        return False
    
    def __del__(self):
        """析构函数"""
        try:
            self.cleanup()
        except:
            pass