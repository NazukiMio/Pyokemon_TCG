"""
战斗页面 - 卡组构建和对战准备的入口
包含Logo、装饰背景、卡组构建按钮、对战准备按钮
"""

import pygame
import pygame_gui
import os
from typing import Dict, Any, Optional, Callable
from game.ui.battle.battle_interface.battle_cache import BattleCache

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
        
        # 战斗界面相关
        self.battle_interface = None  # 🆕 添加战斗界面
        self.current_battle_id = None  # 🆕 当前战斗ID
        
        # 战斗缓存系统
        try:
            from game.ui.battle.battle_interface.battle_cache import BattleCache
            self.battle_cache = BattleCache(game_manager)
            print("✅ 战斗缓存系统初始化成功")
        except Exception as e:
            print(f"⚠️ 战斗缓存系统初始化失败: {e}")
            self.battle_cache = None

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
            logo_path = os.path.join("assets", "images", "logo", "game_logo.png")
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
            decoration_path = os.path.join("assets", "images", "backgrounds", "battle_deco.jpg")
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
        """处理事件"""
        try:
            # ✅ 首先处理pygame_gui事件（在BattlePage层级）
            if hasattr(self, 'ui_manager') and self.ui_manager:
                self.ui_manager.process_events(event)
            
            # 🆕 如果在战斗界面状态
            if self.current_state == "battle_interface" and self.battle_interface:
                result = self.battle_interface.handle_event(event)
                if result == "back_to_battle_page":
                    print("🔙 [battle_page.py] 从战斗界面返回")
                    self._exit_battle_interface()
                    return None
                return None
            
            # 原有的事件处理逻辑...
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.deck_builder_button:
                    print("🏗️ 卡组构建按钮被点击")
                    self._open_deck_builder()
                    return "deck_builder_clicked"
                    
                elif event.ui_element == self.battle_prep_button:
                    print("⚔️ 对战准备按钮被点击")
                    self._open_battle_prep()
                    return "battle_prep_clicked"
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)

            if event.type == pygame.USEREVENT:
                if hasattr(event, 'user_type'):
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        self._handle_button_event(event)
            
            return None
            
        except Exception as e:
            print(f"❌ [battle_page.py] 事件处理异常: {e}")
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
        """打开对战准备窗口 - 使用同步控制器"""
        print(f"🔍 [battle_page.py] 尝试打开对战准备窗口，当前状态: {self.active_windows.get('battle_prep')}")
        
        # 检查窗口是否存在且活跃
        if self.active_windows['battle_prep'] is not None:
            try:
                if hasattr(self.active_windows['battle_prep'], 'alive') and not self.active_windows['battle_prep'].alive:
                    print(f"🔍 [battle_page.py] 窗口已关闭，重置状态")
                    self.active_windows['battle_prep'] = None
                else:
                    print("⚠️ [battle_page.py] 对战准备窗口已经打开")
                    return
            except:
                print(f"🔍 [battle_page.py] 窗口状态异常，重置")
                self.active_windows['battle_prep'] = None
        
        if self.active_windows['battle_prep'] is None:
            try:
                from game.scenes.windows.battle.battle_prep.battle_prep_window import BattlePrepWindow
                from game.core.battle.synchronized_battle_controller import BattleControllerWithSync
                
                # 使用同步控制器
                print(f"🔍 [battle_page.py] 创建同步战斗控制器")
                if not hasattr(self, 'battle_controller') or self.battle_controller is None:
                    self.battle_controller = BattleControllerWithSync(self.game_manager)
                    print(f"✅ [battle_page.py] 同步BattleController创建成功")
                else:
                    print(f"✅ [battle_page.py] 使用现有BattleController")

                # 验证控制器
                if not hasattr(self.battle_controller, 'start_new_battle_synchronized'):
                    print(f"❌ [battle_page.py] BattleController缺少同步方法，回退到普通控制器")
                    from game.core.battle.battle_controller import BattleController
                    self.battle_controller = BattleController(self.game_manager)
                
                # 创建窗口
                window_width = int(600 * self.scale_factor)
                window_height = int(500 * self.scale_factor)
                window_x = (self.screen_width - window_width) // 2
                window_y = (self.screen_height - window_height) // 2
                
                window_rect = pygame.Rect(window_x, window_y, window_width, window_height)
                
                battle_prep_window = BattlePrepWindow(
                    rect=window_rect,
                    ui_manager=self.ui_manager,
                    game_manager=self.game_manager,
                    battle_controller=self.battle_controller
                )
                
                # 设置同步战斗开始回调
                battle_prep_window.set_battle_start_callback(self._on_battle_started_synchronized)
                
                self.active_windows['battle_prep'] = battle_prep_window
                
                print("⚔️ [battle_page.py] 对战准备窗口已打开（同步版本）")
                self.current_state = "battle_prep"
                
                if self.on_battle_prep_click:
                    self.on_battle_prep_click()
                    
            except Exception as e:
                print(f"❌ [battle_page.py] 打开对战准备窗口失败: {e}")
                import traceback
                traceback.print_exc()
    
# 在 _on_battle_started_synchronized 方法中修复

    def _on_battle_started_synchronized(self, battle_data):
        """同步战斗开始回调处理"""
        print(f"🎮 [battle_page.py] 同步战斗开始回调: {battle_data}")
        
        try:
            self._create_battle_interface()
            
            battle_id = battle_data.get('battle_id')
            if battle_id:
                print(f"🎮 [battle_page.py] 开始显示同步战斗界面: {battle_id}")
                self._show_battle_interface_synchronized(battle_id)
                
                # ✅ 重要：等待界面完全初始化
                self._wait_for_interface_ready()
                
            else:
                print("❌ [battle_page.py] 未找到battle_id")
                
        except Exception as e:
            print(f"❌ [battle_page.py] 同步战斗开始回调异常: {e}")
            import traceback
            traceback.print_exc()

    def _create_battle_interface(self):
        """创建战斗界面"""
        print("🎮 [battle_page.py] 创建战斗界面...")
        
        try:
            # 检查必要的依赖
            if not self.battle_controller:
                print("❌ [battle_page.py] 战斗控制器未初始化")
                return False
                
            # 清理之前的界面
            if self.battle_interface:
                if hasattr(self.battle_interface, 'cleanup'):
                    self.battle_interface.cleanup()
                self.battle_interface = None
                print("🧹 [battle_page.py] 清理之前的战斗界面")
            
            # 导入BattleInterface类
            from game.ui.battle.battle_interface.battle_interface import BattleInterface
            
            # 创建新的战斗界面实例
            self.battle_interface = BattleInterface(
                screen_width=self.screen_width,
                screen_height=self.screen_height,
                battle_controller=self.battle_controller
            )
            
            # 初始化战斗缓存
            if hasattr(self, 'game_manager') and self.game_manager:
                from game.ui.battle.battle_interface.battle_cache import BattleCache
                battle_cache = BattleCache(self.game_manager)
                
                # 预加载战斗资源
                battle_cache.preload_battle_assets()
                
                # 设置缓存到界面
                if hasattr(self.battle_interface, 'cards_manager'):
                    self.battle_interface.cards_manager.set_battle_cache(battle_cache)
                    print("✅ [battle_page.py] 战斗缓存已设置")
            
            # 验证界面创建成功
            if not self.battle_interface:
                print("❌ [battle_page.py] 战斗界面创建失败")
                return False
                
            print("✅ [battle_page.py] 战斗界面创建成功")
            return True
            
        except ImportError as e:
            print(f"❌ [battle_page.py] 导入BattleInterface失败: {e}")
            return False
        except Exception as e:
            print(f"❌ [battle_page.py] 创建战斗界面异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _wait_for_interface_ready(self):
        """等待界面准备完成"""
        print("🎮 [battle_page.py] 等待界面初始化完成...")
        
        if not self.battle_interface or not hasattr(self.battle_interface, 'cards_manager'):
            print("❌ [battle_page.py] 界面初始化失败")
            return
        
        try:
            # 🧩 填充 cards_manager 卡组内容
            battle_state_result = self.battle_controller.get_current_state()
            print(f"🔍 [调试] 调用get_current_state()结果:")
            print(f"   结果类型: {type(battle_state_result)}")
            
            if battle_state_result.get("success"):
                actual_battle_state = battle_state_result["state"]
                print(f"🔍 [调试] 提取实际状态: {type(actual_battle_state)}")
                self.battle_interface.cards_manager.populate_from_state(actual_battle_state)
                print("✅ 已将战斗状态同步到 cards_manager")
            else:
                print(f"⚠️ 获取战斗状态失败: {battle_state_result.get('error')}")
            
            # ✅ 给界面一点时间完成渲染
            print("📡 [battle_page.py] 界面数据填充完成，等待渲染...")
            pygame.time.wait(200)  # 等待200ms让界面完成渲染
            
            # ✅ 强制渲染一帧确保界面就绪
            if hasattr(self, 'screen'):
                self.battle_interface.draw(self.screen)
                pygame.display.flip()
                print("🎨 [battle_page.py] 强制渲染一帧")
            
            # 📡 现在通知战斗控制器界面准备完成
            print("📡 [battle_page.py] 通知战斗控制器界面准备完成...")
            
            if hasattr(self.battle_controller, 'notify_interface_ready'):
                result = self.battle_controller.notify_interface_ready()
                if result.get("success"):
                    print("✅ [battle_page.py] 界面同步通知成功")
                else:
                    print(f"❌ [battle_page.py] 界面同步通知失败: {result.get('error')}")
            else:
                print("⚠️ [battle_page.py] 控制器没有notify_interface_ready方法")
            
            print("✅ [battle_page.py] 同步战斗界面显示完成")
            
        except Exception as e:
            print(f"❌ [battle_page.py] 界面准备过程异常: {e}")
            import traceback
            traceback.print_exc()


    def _show_battle_interface_synchronized(self, battle_id):
        """显示同步战斗界面"""
        print(f"🎮 [battle_page.py] 开始显示同步战斗界面: {battle_id}")
        
        try:
            # 预加载战斗缓存
            if self.battle_cache:
                print("📦 预加载战斗缓存...")
                self.battle_cache.preload_battle_assets()
            
            # 导入修复的战斗界面
            BattleInterface = None
            
            try:
                # 首先尝试导入修复版本
                print(f"🔄 尝试导入修复的战斗界面...")
                from game.ui.battle.battle_interface.battle_interface import BattleInterface
                print(f"✅ 成功导入修复版BattleInterface")
            except Exception as e:
                print(f"❌ 导入修复版失败，尝试原版: {e}")
                try:
                    from game.ui.battle.battle_interface.new_battle_interface import BattleInterface
                    print(f"✅ 使用原版BattleInterface")
                except Exception as e2:
                    print(f"❌ 导入原版也失败: {e2}")
                    BattleInterface = self._create_fallback_battle_interface()
            
            # 创建战斗界面实例
            print(f"🎮 创建BattleInterface实例...")
            
            # 确保控制器准备完成
            if hasattr(self.battle_controller, 'get_initial_battle_state'):
                initial_state = self.battle_controller.get_initial_battle_state()
                print(f"📊 获取初始战斗状态: {initial_state}")
            
            try:
                # 使用4参数构造函数
                self.battle_interface = BattleInterface(
                    self.screen_width, 
                    self.screen_height,
                    self.battle_controller,
                    self.battle_cache
                )
                print("✅ 使用4参数构造函数成功")
            except Exception as e:
                print(f"❌ 4参数构造函数失败: {e}")
                try:
                    # 使用3参数构造函数
                    self.battle_interface = BattleInterface(
                        self.screen_width, 
                        self.screen_height,
                        self.battle_controller
                    )
                    print("✅ 使用3参数构造函数成功")
                    # 手动设置缓存
                    if hasattr(self.battle_interface, 'battle_cache'):
                        self.battle_interface.battle_cache = self.battle_cache
                except Exception as e2:
                    print(f"❌ 3参数构造函数也失败: {e2}")
                    raise e2
            
            # 设置状态
            self.current_state = "battle_interface"
            print(f"🔄 [battle_page.py] 状态切换到: {self.current_state}")
            self.current_battle_id = battle_id
            
            print(f"✅ [battle_page.py] 同步战斗界面创建成功")
            print(f"   当前状态: {self.current_state}")
            print(f"   战斗ID: {self.current_battle_id}")
            print(f"   界面对象: {type(self.battle_interface)}")
            
        except Exception as e:
            print(f"❌ [battle_page.py] 创建同步战斗界面失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 创建应急界面
            print("🚨 创建应急战斗界面...")
            self.battle_interface = self._create_emergency_interface(battle_id)
            self.current_state = "battle_interface"
            self.current_battle_id = battle_id

    def _on_battle_started(self, battle_id):
        """原有的战斗开始回调 - 保持兼容性"""
        print(f"🎮 [battle_page.py] 原有战斗开始回调触发: {battle_id}")
        
        # 如果是同步控制器，使用同步方法
        if hasattr(self.battle_controller, 'is_battle_synchronized'):
            battle_info = {"battle_id": battle_id}
            self._on_battle_started_synchronized(battle_info)
        else:
            # 否则使用原有方法
            try:
                self._show_battle_interface(battle_id)
                self.current_state = "battle_interface"
                self._close_prep_windows()
                
                if hasattr(self, 'on_battle_started') and self.on_battle_started:
                    self.on_battle_started(battle_id)
            except Exception as e:
                print(f"❌ [battle_page.py] 原有战斗开始处理失败: {e}")
    
    def get_battle_controller(self):
        """获取战斗控制器 - 支持同步版本"""
        if not self.battle_controller:
            try:
                # 优先使用同步控制器
                from game.core.battle.synchronized_battle_controller import BattleControllerWithSync
                self.battle_controller = BattleControllerWithSync(self.game_manager)
                print("✅ 创建同步战斗控制器")
            except Exception as e:
                print(f"⚠️ 创建同步控制器失败，使用普通控制器: {e}")
                from game.core.battle.battle_controller import BattleController
                self.battle_controller = BattleController(self.game_manager)
        
        return self.battle_controller
    
    def is_battle_synchronized(self) -> bool:
        """检查战斗是否使用同步模式"""
        return (hasattr(self.battle_controller, 'is_battle_synchronized') and 
                self.battle_controller.is_battle_synchronized())
    
    def is_battle_active(self) -> bool:
        """检查是否有活跃的战斗"""
        return (self.battle_controller and 
                self.battle_controller.is_battle_active())
    
    def get_current_battle_state(self):
        """获取当前战斗状态"""
        if self.battle_controller:
            return self.battle_controller.get_current_state()
        return None
    
    def _start_battle_handler(self, battle_id):
        """战斗开始回调处理"""
        print(f"🎮 战斗开始回调触发: {battle_id}")
        
        # 只关闭准备相关的窗口，不关闭所有窗口
        self._close_prep_windows()
        
        # 显示战斗界面
        self._show_battle_interface(battle_id)

    def _close_prep_windows(self):
        """只关闭战斗准备相关的窗口"""
        print("🚪 关闭战斗准备窗口...")
        
        # 定义需要关闭的准备窗口
        prep_windows = ['battle_prep', 'deck_selection', 'ai_selection']
        
        for window_name in prep_windows:
            if window_name in self.active_windows and self.active_windows[window_name]:
                window = self.active_windows[window_name]
                if hasattr(window, 'kill'):
                    window.kill()
                    self.active_windows[window_name] = None
                    print(f"   ✅ 关闭 {window_name} 窗口")

    def _show_battle_interface(self, battle_id):
        """显示战斗界面"""
        print(f"🎮 [battle_page.py] 开始显示战斗界面: {battle_id}")
        
        try:
            # 🆕 预加载战斗缓存
            if self.battle_cache:
                print("📦 预加载战斗缓存...")
                self.battle_cache.preload_battle_assets()
            
            # 🆕 多重导入尝试
            BattleInterface = None
            
            import_attempts = [
                "game.ui.battle.battle_interface.new_battle_interface",
                "game.ui.battle.battle_interface.battle_ui",
                "ui.battle.battle_interface.battle_ui", 
                "battle_interface.battle_ui",
                "battle_ui"
            ]
            
            for import_path in import_attempts:
                try:
                    # from game.scenes.windows.battle.battle_interface.battle_ui import BattleInterface
                    print(f"🔄 尝试导入: {import_path}")
                    module = __import__(f"{import_path}", fromlist=['BattleInterface'])
                    BattleInterface = getattr(module, 'BattleInterface', None)
                    if BattleInterface:
                        print(f"✅ 成功导入 BattleInterface from {import_path}")
                        print("✅ 战斗界面创建成功，没有异常")
                        break
                except Exception as e:
                    print(f"❌ 导入失败 {import_path}: {e}")
                    print(f"❌ 战斗界面创建时发生异常: {e}")
                    continue
            
            # 🆕 如果导入失败，使用内置简化版本
            if not BattleInterface:
                print("🔧 使用内置简化BattleInterface")
                BattleInterface = self._create_fallback_battle_interface()
            
            # 🆕 创建战斗界面实例
            print(f"🎮 创建BattleInterface实例...")
            
            # 尝试不同的构造函数参数
            try:
                # 尝试4参数构造函数
                self.battle_interface = BattleInterface(
                    self.screen_width, 
                    self.screen_height,
                    self.battle_controller,
                    self.battle_cache
                )
                print("✅ 使用4参数构造函数成功")
            except Exception as e:
                print(f"❌ 4参数构造函数失败: {e}")
                try:
                    # 尝试3参数构造函数
                    self.battle_interface = BattleInterface(
                        self.screen_width, 
                        self.screen_height,
                        self.battle_controller
                    )
                    print("✅ 使用3参数构造函数成功")
                    # 手动设置缓存
                    if hasattr(self.battle_interface, 'battle_cache'):
                        self.battle_interface.battle_cache = self.battle_cache
                except Exception as e2:
                    print(f"❌ 3参数构造函数也失败: {e2}")
                    raise e2
            
            # 在成功创建 self.battle_interface 实例后添加
            if self.battle_cache:
                self.battle_cache.preload_cards_from_battle(self.battle_controller)

            # 设置状态
            self.current_state = "battle_interface"
            self.current_battle_id = battle_id
            
            print(f"✅ [battle_page.py] 战斗界面创建成功")
            print(f"   当前状态: {self.current_state}")
            print(f"   战斗ID: {self.current_battle_id}")
            print(f"   界面对象: {type(self.battle_interface)}")
            
        except Exception as e:
            print(f"❌ [battle_page.py] 创建战斗界面失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 🆕 创建应急界面
            print("🚨 创建应急战斗界面...")
            self.battle_interface = self._create_emergency_interface(battle_id)
            self.current_state = "battle_interface"
            self.current_battle_id = battle_id

    # 4. 创建后备战斗界面
    def _create_fallback_battle_interface(self):
        """创建后备战斗界面类"""
        print("🔧 创建后备战斗界面类...")
        
        class FallbackBattleInterface:
            """后备战斗界面"""
            
            def __init__(self, screen_width, screen_height, battle_controller, battle_cache=None):
                self.screen_width = screen_width
                self.screen_height = screen_height
                self.battle_controller = battle_controller
                self.battle_cache = battle_cache
                
                # 字体
                try:
                    self.font = pygame.font.SysFont("arial", 24, bold=True)
                    self.small_font = pygame.font.SysFont("arial", 16)
                except:
                    self.font = pygame.font.Font(None, 24)
                    self.small_font = pygame.font.Font(None, 16)
                
                print(f"✅ 后备战斗界面创建: {screen_width}x{screen_height}")
            
            def handle_event(self, event):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("🔙 后备界面 - ESC键返回")
                        return "back_to_battle_page"
                    elif event.key == pygame.K_SPACE:
                        print("🎮 后备界面 - 空格键结束回合")
                        if self.battle_controller:
                            try:
                                self.battle_controller.end_turn()
                            except Exception as e:
                                print(f"❌ 结束回合失败: {e}")
                return None
            
            def update(self, dt):
                pass
            
            def draw(self, screen):
                # 填充背景
                screen.fill((30, 30, 50))
                
                # 标题
                title = "Pokemon TCG - 战斗界面"
                title_surface = self.font.render(title, True, (255, 255, 255))
                title_rect = title_surface.get_rect(center=(self.screen_width//2, 100))
                screen.blit(title_surface, title_rect)
                
                # 说明文字
                instructions = [
                    "战斗界面载入中...",
                    "",
                    "操作说明:",
                    "ESC - 返回战斗页面",
                    "SPACE - 结束回合",
                    "",
                    "如果界面无法正常显示，",
                    "请检查控制台错误信息"
                ]
                
                y_offset = 200
                for instruction in instructions:
                    if instruction:
                        text_surface = self.small_font.render(instruction, True, (200, 200, 200))
                        text_rect = text_surface.get_rect(center=(self.screen_width//2, y_offset))
                        screen.blit(text_surface, text_rect)
                    y_offset += 30
                
                # 战斗信息
                if self.battle_controller and self.battle_controller.current_battle:
                    try:
                        battle_state = self.battle_controller.get_current_state()
                        if battle_state:
                            info_y = self.screen_height - 150
                            
                            current_player = f"当前玩家: {battle_state.current_player_id}"
                            player_surface = self.small_font.render(current_player, True, (255, 255, 0))
                            player_rect = player_surface.get_rect(center=(self.screen_width//2, info_y))
                            screen.blit(player_surface, player_rect)
                            
                            phase = getattr(battle_state, 'current_phase', 'unknown')
                            phase_text = f"当前阶段: {phase}"
                            phase_surface = self.small_font.render(phase_text, True, (255, 255, 0))
                            phase_rect = phase_surface.get_rect(center=(self.screen_width//2, info_y + 25))
                            screen.blit(phase_surface, phase_rect)
                            
                    except Exception as e:
                        error_text = f"获取战斗状态失败: {e}"
                        error_surface = self.small_font.render(error_text, True, (255, 100, 100))
                        error_rect = error_surface.get_rect(center=(self.screen_width//2, self.screen_height - 100))
                        screen.blit(error_surface, error_rect)
            
            def cleanup(self):
                print("🧹 后备战斗界面清理")
        
        return FallbackBattleInterface

    # 5. 创建应急界面
    def _create_emergency_interface(self, battle_id):
        """创建应急界面"""
        print("🚨 创建应急界面...")
        
        class EmergencyInterface:
            def __init__(self):
                try:
                    self.font = pygame.font.SysFont("arial", 18)
                except:
                    self.font = pygame.font.Font(None, 18)
            
            def handle_event(self, event):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "back_to_battle_page"
                return None
            
            def update(self, dt):
                pass
            
            def draw(self, screen):
                screen.fill((50, 20, 20))
                error_text = "战斗界面加载失败 - 按ESC返回"
                text_surface = self.font.render(error_text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
                screen.blit(text_surface, text_rect)
            
            def cleanup(self):
                pass
        
        return EmergencyInterface()


# 7. 退出战斗界面的方法
    def _exit_battle_interface(self):
        """退出战斗界面"""
        print("🚪 [battle_page.py] 退出战斗界面")
        
        try:
            if self.battle_interface:
                # 清理界面资源
                if hasattr(self.battle_interface, 'cleanup'):
                    self.battle_interface.cleanup()
                self.battle_interface = None
            
            # 返回战斗准备状态
            self.current_state = "battle_prep"
            print("✅ [battle_page.py] 已返回战斗准备状态")

        except Exception as e:
            print(f"❌ [battle_page.py] 退出战斗界面失败: {e}")

    def close_all_windows(self):
        """关闭所有非必要窗口（保留战斗界面）"""
        print("🚪 关闭所有非战斗窗口...")
        
        # 定义不应该关闭的窗口（如果有战斗界面窗口的话）
        protected_windows = ['battle_interface']  # 根据实际情况调整
        
        for window_name, window in self.active_windows.items():
            if window_name not in protected_windows and window and hasattr(window, 'kill'):
                window.kill()
                self.active_windows[window_name] = None
                print(f"   ✅ 关闭 {window_name} 窗口")
        
        # 不要自动设置为lobby状态，让战斗管理器来控制状态
        # self.current_state = "lobby"  # 移除这行
    
    def update(self, dt):
        """更新页面状态"""
        try:
            # 🆕 如果在战斗界面状态，只更新战斗界面
            if self.current_state == "battle_interface" and self.battle_interface:
                self.battle_interface.update(dt)
                return
            
            # 原有的更新逻辑
            for window_name, window in self.active_windows.items():
                if window and hasattr(window, 'update'):
                    window.update(dt)
                    
        except Exception as e:
            print(f"❌ [battle_page.py] 更新异常: {e}")
    
    def draw(self, screen):
        """绘制页面内容"""
        try:
            # 如果在战斗界面状态，只渲染战斗界面
            if self.current_state == "battle_interface" and self.battle_interface:
                self.battle_interface.draw(screen)
                return
            
            # 否则渲染原有的battle_page界面
            screen.fill((50, 50, 50))
            
            # 只在非战斗界面状态下渲染UI管理器
            if hasattr(self, 'ui_manager') and self.ui_manager:
                self.ui_manager.draw_ui(screen)
            
            # 原有的绘制逻辑
            # 绘制装饰背景
            self._draw_decoration_background(screen)
            
            # 绘制Logo
            self._draw_logo(screen)
            
            # 绘制按钮装饰效果
            self._draw_button_effects(screen)
            
            # 绘制状态信息
            self._draw_status_info(screen)
                    
        except Exception as e:
            print(f"❌ [battle_page.py] 绘制异常: {e}")
            # 绘制错误信息
            try:
                font = pygame.font.Font(None, 24)
                error_text = f"绘制错误: {str(e)[:50]}"
                text_surface = font.render(error_text, True, (255, 100, 100))
                screen.blit(text_surface, (10, 10))
            except:
                pass
    
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
            title_text = "POKEMON BATALLA"
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
        print("🧹 [battle_page.py] 清理战斗页面资源...")
        
        # 🆕 清理战斗界面
        if self.battle_interface and hasattr(self.battle_interface, 'cleanup'):
            self.battle_interface.cleanup()
        self.battle_interface = None
        
        # 关闭所有窗口
        self.close_all_windows()
        
        # 清理UI元素
        if self.deck_builder_button:
            self.deck_builder_button.kill()
            self.deck_builder_button = None
            
        if self.battle_prep_button:
            self.battle_prep_button.kill()
            self.battle_prep_button = None
        
        # 🆕 清理缓存
        if hasattr(self, 'battle_cache') and self.battle_cache:
            self.battle_cache.cleanup()
        
        print("✅ [battle_page.py] 战斗页面清理完成")

    """
    # 添加到 battle_page.py 的末尾来应用修复
    BattlePage._open_battle_prep = _open_battle_prep
    BattlePage._on_battle_started_synchronized = _on_battle_started_synchronized
    BattlePage._show_battle_interface_synchronized = _show_battle_interface_synchronized
    BattlePage._on_battle_started = _on_battle_started
    BattlePage.get_battle_controller = get_battle_controller
    BattlePage.is_battle_synchronized = is_battle_synchronized
    """