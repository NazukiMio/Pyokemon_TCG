import pygame
import pygame_gui
import sys
import os

# 导入组件
from game.scenes.home_page import HomePage
from game.scenes.dex_page import DexPage
from game.ui.navigation_bar import PokemonNavigationGUI
from game.core.message_manager import MessageManager
# from game.ui.toast_message import ToastMessage
from game.core.auth.auth_manager import get_auth_manager
# 导入新的数据库管理器
from game.core.database.database_manager import DatabaseManager
from game.core.game_manager import GameManager

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

        # 游戏管理器
        self.game_manager = GameManager()

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
            self.game_manager, # 游戏管理器
            self.nav_bar.height  # 使用导航栏的高度
        )

        self.dex_page = None

        self.battle_page = None

        # 确保数据库管理器已初始化（可选，因为HomePage会处理）
        # 如果需要在MainScene层面访问数据库，可以添加：
        self.db_manager = DatabaseManager()
        # self.db_manager.initialize_database()

    #     from game.core.cards.collection_manager import CardManager
    #     self.card_manager = CardManager(
    #         self.db_manager.connection,
    #         cards_json_path=os.path.join("data", "card.json")
    # )
        
        # 当前页面
        self.current_page = 'home'
        
        # Toast消息
        self.toast_message = None
        
        # 设置回调
        self.setup_callbacks()

        # 缓存渐变背景
        self.gradient_background = None
        
        print("✅ 主场景初始化完成")
        print(f"[调试] UIManager id in MainScene: {id(self.ui_manager)}")

        # 初始化数据库
        self.db_manager = DatabaseManager()

        # 带验证的卡牌管理器初始化
        self._initialize_card_manager_with_validation()
        
    #     # 简单的卡牌数据初始化
    #     self._initialize_card_database()
    
    # def _initialize_card_database(self):
    #     """初始化卡牌数据库（仅在为空时导入）"""
    #     try:
    #         # 检查数据库是否为空
    #         existing_cards = self.db_manager.card_dao.search_cards(limit=1)
            
    #         if existing_cards:
    #             print(f"✅ 数据库已有卡牌数据，跳过初始化")
    #             return
            
    #         # 数据库为空，开始导入
    #         import json
    #         import os
            
    #         card_file = os.path.join("card_assets", "cards.json")
    #         if os.path.exists(card_file):
    #             with open(card_file, 'r', encoding='utf-8') as f:
    #                 cards_data = json.load(f)
                
    #             print(f"📥 数据库为空，正在导入 {len(cards_data)} 张卡牌...")
                
    #             for card_data in cards_data:
    #                 self.db_manager.card_dao.create_card(card_data)
                
    #             print(f"✅ 成功导入 {len(cards_data)} 张卡牌到数据库")
    #         else:
    #             print(f"❌ 找不到卡牌数据文件: {card_file}")
                
    #     except Exception as e:
    #         print(f"❌ 初始化卡牌数据库失败: {e}")

    def _initialize_card_manager_with_validation(self):
        """带验证的卡牌管理器初始化"""
        print("🔍 开始初始化卡牌管理器...")
        
        try:
            # 1. 验证数据库连接
            if not self.db_manager or not self.db_manager.connection:
                print("❌ 数据库连接失败")
                return False
            print("✅ 数据库连接正常")
            
            # 2. 验证card.json文件
            card_json_path = os.path.join("card_assets", "cards.json")
            if not os.path.exists(card_json_path):
                print(f"❌ 找不到卡牌数据文件: {card_json_path}")
                return False
            print(f"✅ 找到卡牌数据文件: {card_json_path}")
            
            # 3. 检查文件大小
            file_size = os.path.getsize(card_json_path)
            print(f"📄 卡牌文件大小: {file_size / 1024:.1f} KB")
            
            if file_size < 1000:  # 小于1KB可能有问题
                print("⚠️ 警告：卡牌文件很小，可能数据不完整")
            
            # 4. 初始化CardManager
            print("🔄 正在初始化CardManager...")
            from game.core.cards.collection_manager import CardManager
            
            self.card_manager = CardManager(
                self.db_manager.connection,
                cards_json_path=card_json_path
            )
            print("✅ CardManager初始化完成")
            
            # 5. 验证数据导入结果
            card_count = self.card_manager.card_dao.get_card_count()
            print(f"📊 数据库中卡牌数量: {card_count}")
            
            if card_count == 0:
                print("⚠️ 警告：数据库中没有卡牌数据")
                return False
            
            # 6. 验证卡牌数据完整性
            rarities = self.card_manager.card_dao.get_all_rarities()
            types = self.card_manager.card_dao.get_all_types()
            
            print(f"🎯 可用稀有度: {len(rarities)} 种")
            print(f"🏷️ 可用类型: {len(types)} 种")
            
            if len(rarities) < 3:
                print("⚠️ 警告：稀有度种类过少")
            
            if len(types) < 5:
                print("⚠️ 警告：卡牌类型种类过少")
            
            # 7. 测试随机获取卡牌
            test_card = self.card_manager.card_dao.get_random_cards(1)
            if test_card:
                print(f"🎲 测试卡牌: {test_card[0].name} ({test_card[0].rarity})")
            else:
                print("❌ 无法获取测试卡牌")
                return False
            
            print("🎉 卡牌管理器初始化验证完成！")
            return True
            
        except Exception as e:
            print(f"❌ 卡牌管理器初始化失败: {e}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            return False

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
            
            # # 控制DexPage的活跃状态
            # if self.dex_page:
            #     self.dex_page.set_active(nav_id == 'pokedex')
        
            # 当切换页面时关闭所有弹出窗口
            if nav_id != 'home':
                self.home_page.close_all_windows()
                print("   🚪 关闭所有弹出窗口")
            
            # 根据导航选择，可能需要切换到其他场景
            if nav_id == 'menu':
                # 切换到设置菜单场景
                if self.callback:
                    self.callback("settings")

            elif nav_id == 'pokedex':
                # 切换到图鉴页面
                self.current_page = nav_id
                if not self.dex_page:
                    self.dex_page = DexPage(
                        self.screen_width, 
                        self.screen_height, 
                        self.ui_manager, 
                        self.game_manager.card_manager,
                        self.game_manager,
                        self.nav_bar.height
                    )
                # else:
                #     # 显示已存在的DexPage UI
                #     self.dex_page.show_ui_elements()

            elif nav_id == 'battle':
                # 切换到战斗页面
                self.current_page = nav_id
                if not self.battle_page:
                    success = self._create_battle_page()
                    if not success:
                        print("❌ 创建战斗页面失败，返回主页")
                        self.nav_bar.set_active('home')
                        self.current_page = 'home'
                        return
                
                # 关闭主页的所有窗口
                self.home_page.close_all_windows()
                print("   ⚔️ 战斗页面 - 卡组构建和对战准备")
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
        if self.gradient_background is None:
            gradient_surface = pygame.Surface((self.screen_width, self.screen_height))
            
            for y in range(self.screen_height):
                ratio = y / self.screen_height
                r = int(self.background_colors['top'][0] * (1 - ratio) + self.background_colors['bottom'][0] * ratio)
                g = int(self.background_colors['top'][1] * (1 - ratio) + self.background_colors['bottom'][1] * ratio)
                b = int(self.background_colors['top'][2] * (1 - ratio) + self.background_colors['bottom'][2] * ratio)
                
                pygame.draw.line(gradient_surface, (r, g, b), (0, y), (self.screen_width, y))
            
            self.gradient_background = gradient_surface
        
        return self.gradient_background
    
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
                # ESC键处理：优先让当前页面处理
                esc_handled = False
                
                if self.current_page == 'battle' and self.battle_page:
                    # 如果在战斗页面，让战斗页面先处理ESC
                    print("🎮 战斗页面处理ESC键")
                    # 不在这里处理，让后面的页面事件处理逻辑来处理
                    esc_handled = False  # 标记为未处理，让后面的逻辑处理
                elif self.current_page == 'home':
                    # 在主页时检查是否有弹出窗口
                    has_windows = any(window and window.is_visible 
                                    for window in self.home_page.active_windows.values())
                    if has_windows:
                        self.home_page.close_all_windows()
                        print("🚪 ESC - 关闭所有弹出窗口")
                        esc_handled = True
                
                # 如果没有被处理，且不在特殊页面，则退出游戏
                if not esc_handled and self.current_page == 'home':
                    if self.callback:
                        self.callback("exit")
                    print("🚪 ESC - 退出程序")
                    return True  # 添加return防止继续处理
            
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

            # 调整DexPage大小
            if self.dex_page:
                self.dex_page.resize(self.screen_width, self.screen_height)

            # 调整BattlePage大小
            if self.battle_page:
                self.battle_page.resize(self.screen_width, self.screen_height)
            
            # 更新缩放因子
            self.scale_factor = min(self.screen_width / 1920, self.screen_height / 1080)

            # 清空渐变背景缓存（因为尺寸变了）
            self.gradient_background = None
            
            print(f"📐 窗口调整: {self.screen_width}x{self.screen_height}")
        
        # 导航栏事件处理
        nav_result = None
        if not self._should_hide_navbar():
            nav_result = self.nav_bar.handle_event(event)
        else:
            print("🎮 战斗场景中，忽略导航栏事件")
        
        # 初始化UI结果
        ui_result = None

        # 主页事件处理（仅在主页时）
        if self.current_page == 'home':
            # 如果开包窗口显示，优先处理其事件
            if (self.home_page.active_windows.get('pack_opening') and 
                self.home_page.active_windows['pack_opening'].is_visible):
                pack_result = self.home_page.active_windows['pack_opening'].handle_event(event)
                if pack_result:
                    return True  # 阻止进一步的事件处理
                
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

            # 处理导航栏事件
        elif self.current_page == 'pokedex':  # 添加这里
            if self.dex_page:
                result = self.dex_page.handle_event(event)
                if result == "back_to_home":
                    self.nav_bar.set_active('home')
                    self.current_page = 'home'

        elif self.current_page == 'battle':
            if self.battle_page:
                try:
                    result = self.battle_page.handle_event(event)
                    
                    # 检查是否从战斗场景返回到战斗页面
                    if result == "back_to_battle_page":
                        print("🔙 从战斗场景返回战斗页面")
                        # 这时应该重新显示navbar
                        return True
                        
                    # 处理从战斗页面返回主页
                    elif result == "back_to_home":
                        self.nav_bar.set_active('home')
                        self.current_page = 'home'
                        print("🏠 从战斗页面返回主页")
                        return True
                        
                    elif result:
                        print(f"🎮 战斗页面事件结果: {result}")
                        return True
                        
                except Exception as e:
                    print(f"❌ 战斗页面事件处理异常: {e}")
                    self.nav_bar.set_active('home')
                    self.current_page = 'home'
                    return True

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
        # 更新图鉴页面（如果存在）
        elif self.current_page == 'pokedex':
            if self.dex_page:
                self.dex_page.update(dt)

        # 更新战斗页面（如果存在）
        elif self.current_page == 'battle':
            if self.battle_page:
                try:
                    self.battle_page.update(dt)
                except Exception as e:
                    print(f"❌ 战斗页面更新异常: {e}")

        # 更新消息管理器
        self.message_manager.update(dt)
        
        # 更新Toast消息
        if self.toast_message and not self.toast_message.update():
            self.toast_message = None
        
        return True
    
    def draw(self):
        """绘制场景"""
        # 调试信息
        if self.battle_page and hasattr(self.battle_page, 'current_state'):
            battle_state = self.battle_page.current_state
            if battle_state != "lobby":
                print(f"🎮 [调试] 战斗页面状态: {battle_state}")
        # 获取实际的时间增量
        current_time = pygame.time.get_ticks() / 1000.0
        if not hasattr(self, 'last_time'):
            self.last_time = current_time
        time_delta = current_time - self.last_time
        self.last_time = current_time
        
        # 限制最大时间增量，避免卡顿时动画跳跃
        time_delta = min(time_delta, 0.05) 
        
        # 绘制统一的渐变背景
        gradient_bg = self.create_gradient_background()
        self.screen.blit(gradient_bg, (0, 0))

        # 绘制统一的渐变背景
        gradient_bg = self.create_gradient_background()
        self.screen.blit(gradient_bg, (0, 0))
        
        # 检查是否有开包窗口显示
        pack_window_visible = (self.current_page == 'home' and 
                            self.home_page.active_windows.get('pack_opening') and 
                            self.home_page.active_windows['pack_opening'].is_visible)
        
        # 根据当前页面绘制内容
        if self.current_page == 'home':
            # 绘制主页内容（传入time_delta）
            self.home_page.draw(self.screen, time_delta)
        elif self.current_page == 'pokedex':
            # 绘制图鉴页面
            if self.dex_page:
                self.dex_page.draw(self.screen)
        elif self.current_page == 'battle':
            # 绘制战斗页面
            if self.battle_page:
                try:
                    self.battle_page.draw(self.screen)
                except Exception as e:
                    print(f"❌ 战斗页面绘制异常: {e}")
                    # 绘制错误信息
                    font = pygame.font.Font(None, 36)
                    error_text = f"战斗页面错误: {str(e)[:30]}..."
                    text_surface = font.render(error_text, True, (255, 100, 100))
                    self.screen.blit(text_surface, (50, 50))
        else:
            # 绘制其他页面的占位内容
            page_names = {
                'social': 'Social',
                # 'battle': 'Batalla', 
                'menu': 'Menú'
            }
            page_name = page_names.get(self.current_page, self.current_page)
            self.draw_page_placeholder(page_name)
        
        # # 绘制导航栏（始终在最上层）
        # self.nav_bar.draw(self.screen)
        # 绘制导航栏（根据条件判断）
        should_hide_navbar = self._should_hide_navbar()
        if not pack_window_visible and not should_hide_navbar:
            self.nav_bar.draw(self.screen)
        elif should_hide_navbar:
            print("🎮 战斗场景中，隐藏导航栏")
        
        
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
        
        # 根据当前页面控制UI可见性
        if self.dex_page:
            if self.current_page == 'pokedex':
                # 显示DexPage UI
                for element in self.dex_page.ui_elements.values():
                    if element and element.alive():
                        element.show()
            else:
                # 隐藏DexPage UI
                for element in self.dex_page.ui_elements.values():
                    if element and element.alive():
                        element.hide()

        # 控制BattlePage UI可见性
        if self.battle_page:
            if self.current_page == 'battle':
                # 显示BattlePage UI元素
                if hasattr(self.battle_page, 'deck_builder_button') and self.battle_page.deck_builder_button:
                    self.battle_page.deck_builder_button.show()
                if hasattr(self.battle_page, 'battle_prep_button') and self.battle_page.battle_prep_button:
                    self.battle_page.battle_prep_button.show()
            else:
                # 隐藏BattlePage UI元素
                if hasattr(self.battle_page, 'deck_builder_button') and self.battle_page.deck_builder_button:
                    self.battle_page.deck_builder_button.hide()
                if hasattr(self.battle_page, 'battle_prep_button') and self.battle_page.battle_prep_button:
                    self.battle_page.battle_prep_button.hide()

        # 绘制pygame-gui界面
        # self.ui_manager.draw_ui(self.screen)
        # 绘制pygame-gui界面（根据条件判断）
        should_hide_navbar = self._should_hide_navbar()
        if not pack_window_visible and not should_hide_navbar:
            self.ui_manager.draw_ui(self.screen)
        elif should_hide_navbar:
            # 在战斗场景中，可能需要不同的UI渲染逻辑
            # BattleInterface有自己的UI渲染
            pass

    def _create_battle_page(self):
        """创建战斗页面（懒加载）"""
        print("⚔️ 正在创建战斗页面...")
        
        try:
            from game.scenes.battle_page import BattlePage
            
            self.battle_page = BattlePage(
                screen_width=self.screen_width,
                screen_height=self.screen_height,
                ui_manager=self.ui_manager,
                game_manager=self.game_manager,
                nav_height=self.nav_bar.height
            )
            
            # 设置战斗页面回调
            self._setup_battle_page_callbacks()

            if self.current_page != 'battle':
                self._hide_battle_page_ui()
            
            print("✅ 战斗页面创建成功")
            return True
            
        except ImportError as e:
            print(f"❌ 导入战斗页面失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 创建战斗页面异常: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    def _hide_battle_page_ui(self):
        """隐藏战斗页面UI元素"""
        if not self.battle_page:
            return
            
        ui_elements = ['deck_builder_button', 'battle_prep_button']
        for element_name in ui_elements:
            if hasattr(self.battle_page, element_name):
                element = getattr(self.battle_page, element_name)
                if element and hasattr(element, 'hide'):
                    element.hide()

    def _setup_battle_page_callbacks(self):
        """设置战斗页面回调"""
        if not self.battle_page:
            return
        
        # 设置返回主页回调
        def on_battle_page_back():
            print("🏠 战斗页面请求返回主页")
            self.nav_bar.set_active('home')
            self.current_page = 'home'
        
        # 战斗开始回调
        def on_battle_started(battle_id):
            print(f"🎮 战斗开始: {battle_id}")
            # 可以在这里添加额外的战斗开始逻辑
        
        # 战斗结束回调
        def on_battle_ended(battle_result):
            print(f"🏁 战斗结束: {battle_result}")
            # 可以在这里处理战斗结果
        
        # 设置回调（如果BattlePage支持的话）
        if hasattr(self.battle_page, 'on_battle_started'):
            self.battle_page.on_battle_started = on_battle_started
        
        # 注意：BattlePage可能没有直接的返回主页回调
        # 这需要通过其他方式实现，比如在handle_event中检查特定返回值
    
    def _is_in_battle_scene(self):
        """检查是否在实际战斗场景中（不是战斗页面）"""
        if not self.battle_page:
            return False
        
        # 检查BattlePage是否处于战斗界面状态
        if hasattr(self.battle_page, 'current_state'):
            return self.battle_page.current_state == "battle_interface"
        
        # 或者检查是否有活跃的战斗界面
        if hasattr(self.battle_page, 'battle_interface'):
            return self.battle_page.battle_interface is not None
        
        return False

    def _should_hide_navbar(self):
        """判断是否应该隐藏导航栏"""
        # 在实际战斗场景中隐藏导航栏
        return self._is_in_battle_scene()

    def cleanup(self):
        """清理资源"""
        print("🧹 清理主场景资源...")
        
        if hasattr(self.home_page, 'cleanup'):
            self.home_page.cleanup()

        # if hasattr(self.dex_page, 'cleanup'):
        #     self.dex_page.cleanup()
            
        # if self.dex_page:
        #     self.dex_page.hide_ui_elements()

        # 清理战斗页面
        if self.battle_page and hasattr(self.battle_page, 'cleanup'):
            self.battle_page.cleanup()
            self.battle_page = None
        
        if hasattr(self.nav_bar, 'cleanup'):
            self.nav_bar.cleanup()
        
        print("✅ 主场景资源清理完成")