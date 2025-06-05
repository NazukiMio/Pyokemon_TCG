import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIPanel, UILabel
from pygame_gui.core import ObjectID
import math
import os
import sys
import random
from typing import Optional, Callable
from game.core.database.database_manager import DatabaseManager

# 导入PIL处理GIF动画
try:
    from PIL import Image, ImageSequence
    PIL_AVAILABLE = True
except ImportError:
    print("警告: PIL/Pillow未安装，GIF动画将不可用")
    PIL_AVAILABLE = False

# 导入窗口类
try:
    # from game.scenes.windows.package import PackageWindow
    from game.scenes.windows.e_magica import EMagicaWindow
    from game.scenes.windows.tienda.tienda_modern import ModernTiendaWindow
    from game.scenes.windows.package.pack_opening_window import PackOpeningWindow

    WINDOWS_AVAILABLE = True
    print("✅ 窗口模块导入成功")
except ImportError as e:
    print(f"⚠️ 窗口模块导入失败: {e}")
    print("将使用占位符功能")
    WINDOWS_AVAILABLE = False

class HomePage:
    """
    游戏主页面
    包含抽卡包入口、商店和魔法选择等功能区域
    横屏布局版本 - 使用pygame_gui重构 + 弹出窗口支持
    """
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager, game_manager, nav_bar_height: int = 100):
        """
        初始化主页
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            nav_bar_height: 导航栏高度
        """
        self.game_manager = game_manager

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.nav_bar_height = nav_bar_height
        
        # 计算内容区域（排除导航栏）
        self.content_height = screen_height - nav_bar_height
        self.content_rect = pygame.Rect(0, 0, screen_width, self.content_height)

        self.ui_manager = ui_manager

        # 初始化db管理器
        self.db_manager = DatabaseManager()
        if hasattr(self.db_manager, "card_dao"):
            self.db_manager.card_dao.create_card_tables()
        if hasattr(self.db_manager, "user_dao"):
            self.db_manager.user_dao.create_user_table()
        
        # 基准尺寸（1344x756）
        self.base_width = 1344
        self.base_height = 756
        self.scale_factor = min(screen_width / self.base_width, (screen_height - nav_bar_height) / (self.base_height - nav_bar_height))
        
        # 颜色主题
        self.colors = {
            'card_bg': (255, 255, 255, 250), 
            'card_hover': (255, 255, 255, 255),
            'accent': (88, 101, 242),  # 紫蓝色
            'accent_hover': (67, 78, 216),
            'text': (55, 65, 81),
            'text_secondary': (107, 114, 128), 
            'border': (209, 213, 219),
            'shadow': (0, 0, 0, 0.15 * 255),  # 阴影
            'glass_bg': (255, 255, 255, 0.9 * 255),  # 玻璃态效果
            'glass_border': (255, 255, 255, 0.3 * 255),
            'emboss_light': (255, 255, 255, 120),  # 浮雕高光
            'emboss_shadow': (0, 0, 0, 60),  # 浮雕阴影
            'glass_bg_modern': (255, 255, 255, 0.85 * 255),  # 现代毛玻璃背景
            'glass_border_modern': (255, 255, 255, 0.3 * 255),  # 毛玻璃边框
            'button_shadow_light': (255, 255, 255, 0.6 * 255),  # 按钮内部高光
            'button_gradient_start': (248, 249, 255),  # 渐变开始色
            'button_gradient_end': (240, 242, 247),    # 渐变结束色
            'button_hover_bg': (248, 249, 255),        # hover背景色
            'modern_border': (229, 231, 235)        # 现代边框色
        }
        
        # 加载字体
        self.fonts = self.load_fonts()
        
        # 创建pygame_gui管理器
        # self.ui_manager = pygame_gui.UIManager((screen_width, self.content_height))
        
        # 加载现代主题
        self.setup_ui_theme()
        
        # Logo相关
        self.logo = None
        # self.subtitle_logo = None

        # 图标相关
        self.shop_icon = None
        self.magic_icon = None

        # UI元素
        self.ui_elements = {
            'magic_button': None,
            'shop_button': None,
            'pack_buttons': []
        }
        
        # 弹出窗口管理
        self.active_windows = {
            'pack_opening': None,
            'e_magica': None,
            'tienda': None
        }
        
        # 组件状态
        self.hover_pack = None
        self.hover_shop = False
        self.hover_magic = False
        self.hover_sprite = False
        
        # 动画参数
        self.pack_hover_scale = [1.0, 1.0, 1.0]  # 三个卡包的缩放
        self.target_pack_scale = [1.0, 1.0, 1.0]  # 目标缩放
        self.sprite_hover_scale = 1.0
        self.target_sprite_scale = 1.0
        self.sprite_shake_offset = [0, 0]  # 抖动偏移
        self.sprite_shake_timer = 0
        self.sprite_fade_alpha = 255  # 精灵透明度
        self.sprite_fade_state = "normal"  # normal, shaking, fading, switching
        self.sprite_fade_timer = 0
        
        # 功能按钮动画参数
        self.magic_hover_scale = 1.0
        self.target_magic_scale = 1.0
        self.shop_hover_scale = 1.0
        self.target_shop_scale = 1.0
        
        # 组件区域
        self.pack_areas = []
        self.shop_area = None
        self.magic_area = None
        self.sprite_area = None
        
        # 回调函数
        self.on_pack_click: Optional[Callable] = None
        self.on_shop_click: Optional[Callable] = None
        self.on_magic_click: Optional[Callable] = None
        self.on_sprite_click: Optional[Callable] = None
        
        # 卡包图片
        self.pack_images = []
        self.selected_pack_images = []
        self.load_pack_images()
        
        # 精灵动图
        self.sprite_gif = None
        self.sprite_frames = []
        self.sprite_frame_index = 0
        self.sprite_animation_timer = 0
        self.sprite_frame_duration = 100  # 毫秒
        self.load_random_sprite()
        
        # 创建布局
        self.create_layout()

        # 加载Logo和副标题Logo
        self.load_logo()
        # self.load_subtitle_logo()

        self.load_icons()

        # print(f"[注册检查] 所有 UI 元素: {[str(s) for s in self.ui_manager.get_sprite_group().sprites()]}")
        # print(f"[注册检查] shop_button 是否存在: {self.ui_elements['shop_button'] in self.ui_manager.get_sprite_group().sprites()}")
        # print(f"[按钮位置] shop_button.rect = {self.ui_elements['shop_button'].relative_rect}")
        # print(f"[调试] UIManager id in HomePage: {id(self.ui_manager)}")


    
    def load_fonts(self):
        """加载字体"""
        fonts = {}
        try:
            font_path = os.path.join("assets", "fonts", "power-clear.ttf")
            pokemon_font_path = os.path.join("assets", "fonts", "Pokemon-Solid-Normal.ttf")
            
            if os.path.exists(pokemon_font_path):
                fonts['title'] = pygame.font.Font(pokemon_font_path, int(24 * self.scale_factor))
                fonts['pack_title'] = pygame.font.Font(pokemon_font_path, int(14 * self.scale_factor))
            else:
                fonts['title'] = pygame.font.SysFont("arial", int(24 * self.scale_factor), bold=True)
                fonts['pack_title'] = pygame.font.SysFont("arial", int(14 * self.scale_factor), bold=True)
            
            if os.path.exists(font_path):
                fonts['subtitle'] = pygame.font.Font(font_path, int(18 * self.scale_factor))
                fonts['button'] = pygame.font.Font(font_path, int(16 * self.scale_factor))
                fonts['text'] = pygame.font.Font(font_path, int(14 * self.scale_factor))
                fonts['small'] = pygame.font.Font(font_path, int(12 * self.scale_factor))
            else:
                fonts['subtitle'] = pygame.font.SysFont("arial", int(18 * self.scale_factor), bold=True)
                fonts['button'] = pygame.font.SysFont("arial", int(16 * self.scale_factor), bold=True)
                fonts['text'] = pygame.font.SysFont("arial", int(14 * self.scale_factor))
                fonts['small'] = pygame.font.SysFont("arial", int(12 * self.scale_factor))
                
        except Exception as e:
            print(f"Error al cargar fuentes: {e}")
            fonts['title'] = pygame.font.SysFont("arial", int(24 * self.scale_factor), bold=True)
            fonts['pack_title'] = pygame.font.SysFont("arial", int(14 * self.scale_factor), bold=True)
            fonts['subtitle'] = pygame.font.SysFont("arial", int(18 * self.scale_factor), bold=True)
            fonts['button'] = pygame.font.SysFont("arial", int(16 * self.scale_factor), bold=True)
            fonts['text'] = pygame.font.SysFont("arial", int(14 * self.scale_factor))
            fonts['small'] = pygame.font.SysFont("arial", int(12 * self.scale_factor))
        
        return fonts
    
    def load_icons(self):
        """加载功能图标"""
        try:
            # 加载商店图标
            shop_icon_path = os.path.join("assets", "icons", "store.png")
            if os.path.exists(shop_icon_path):
                self.shop_icon = pygame.image.load(shop_icon_path)
                # 调整图标大小 - 适应垂直布局，占据按钮上部分空间
                icon_size = int(120 * self.scale_factor)  # 增大图标
                self.shop_icon = pygame.transform.smoothscale(self.shop_icon, (icon_size, icon_size))
                print("✅ 商店图标加载成功")
            else:
                self.shop_icon = None
                
            # 加载魔法图标  
            magic_icon_path = os.path.join("assets", "icons", "magic.png")
            if os.path.exists(magic_icon_path):
                self.magic_icon = pygame.image.load(magic_icon_path)
                # 调整图标大小 - 适应垂直布局，占据按钮上部分空间
                icon_size = int(120 * self.scale_factor)  # 增大图标
                self.magic_icon = pygame.transform.smoothscale(self.magic_icon, (icon_size, icon_size))
                print("✅ 魔法图标加载成功")
            else:
                self.magic_icon = None
                
        except Exception as e:
            print(f"⚠️ 图标加载失败: {e}")
            self.shop_icon = None
            self.magic_icon = None

    def setup_ui_theme(self):
        """设置现代UI主题"""
        theme_data = {
            '#magic_button': {
                'colours': {
                    'normal_bg': '#00000000',
                    'hovered_bg': '#00000000',
                    'selected_bg': '#00000000',
                    'pressed_bg': '#00000000',
                    'active_bg': '#00000000',
                    'disabled_bg': '#00000000',
                    'normal_border': '#00000000',
                    'hovered_border': '#00000000',
                    'selected_border': '#00000000',
                    'pressed_border': '#00000000',
                    'active_border': '#00000000',
                    'disabled_border': '#00000000',
                    'normal_text': '#00000000',
                    'hovered_text': '#00000000',
                    'selected_text': '#00000000',
                    'pressed_text': '#00000000',
                    'active_text': '#00000000',
                    'disabled_text': '#00000000'
                },
                'misc': {
                    'border_width': '0',
                    'border_radius': '0',
                    'shadow_width': '0',
                    'shape': 'rectangle',
                    'tool_tip_delay': '1.0',
                    'text_shadow': '0',
                    'text_shadow_colour': '#00000000'
                }
            },
            '#shop_button': {
                'colours': {
                    'normal_bg': '#00000000',
                    'hovered_bg': '#00000000',
                    'selected_bg': '#00000000',
                    'pressed_bg': '#00000000',
                    'active_bg': '#00000000',
                    'disabled_bg': '#00000000',
                    'normal_border': '#00000000',
                    'hovered_border': '#00000000',
                    'selected_border': '#00000000',
                    'pressed_border': '#00000000',
                    'active_border': '#00000000',
                    'disabled_border': '#00000000',
                    'normal_text': '#00000000',
                    'hovered_text': '#00000000',
                    'selected_text': '#00000000',
                    'pressed_text': '#00000000',
                    'active_text': '#00000000',
                    'disabled_text': '#00000000'
                },
                'misc': {
                    'border_width': '0',
                    'border_radius': '0',
                    'shadow_width': '0',
                    'shape': 'rectangle',
                    'tool_tip_delay': '1.0',
                    'text_shadow': '0',
                    'text_shadow_colour': '#00000000'
                }
            },
            '#pack_button': {
                'colours': {
                    'normal_bg': '#00000000',
                    'hovered_bg': '#00000000',
                    'selected_bg': '#00000000',
                    'pressed_bg': '#00000000',
                    'active_bg': '#00000000',
                    'disabled_bg': '#00000000',
                    'normal_border': '#00000000',
                    'hovered_border': '#00000000',
                    'selected_border': '#00000000',
                    'pressed_border': '#00000000',
                    'active_border': '#00000000',
                    'disabled_border': '#00000000'
                },
                'misc': {
                    'border_width': '0',
                    'border_radius': '0',
                    'shadow_width': '0',
                    'shape': 'rectangle'
                }
            }
        }
        
        self.ui_manager.get_theme().load_theme(theme_data)
    
    def load_pack_images(self):
        """加载卡包图片并随机选择3张"""
        pack_dir = os.path.join("assets", "images", "packets")
        
        # 加载所有可用的卡包图片
        available_packs = []
        for i in range(1, 11):  # packet1.png 到 packet10.png
            pack_path = os.path.join(pack_dir, f"packet{i}.png")
            if os.path.exists(pack_path):
                try:
                    pack_image = pygame.image.load(pack_path)
                    available_packs.append((pack_image, f"packet{i}"))
                    print(f"已加载卡包图片: packet{i}.png")
                except Exception as e:
                    print(f"加载卡包图片失败 packet{i}.png: {e}")
        
        # 随机选择3张卡包
        if len(available_packs) >= 3:
            self.selected_pack_images = random.sample(available_packs, 3)
        else:
            print(f"警告: 只找到 {len(available_packs)} 张卡包图片，需要至少3张")
            while len(available_packs) < 3:
                if available_packs:
                    available_packs.append(available_packs[0])
                else:
                    available_packs.append((None, "placeholder"))
            self.selected_pack_images = available_packs[:3]
        
        print(f"已选择卡包: {[pack[1] for pack in self.selected_pack_images]}")
    
    def load_random_sprite(self):
        """随机加载精灵动图"""
        if not PIL_AVAILABLE:
            print("PIL不可用，无法加载GIF动画")
            return
        
        sprite_dirs = [
            os.path.join("assets", "images", "sprites", "animated"),
            os.path.join("assets", "images", "sprites", "animated", "female"),
            os.path.join("assets", "images", "sprites", "animated", "shiny"),
            os.path.join("assets", "images", "sprites", "animated", "shiny", "female")
        ]
        
        # 收集所有可用的gif文件
        available_sprites = []
        for sprite_dir in sprite_dirs:
            if os.path.exists(sprite_dir):
                for filename in os.listdir(sprite_dir):
                    if filename.lower().endswith('.gif'):
                        sprite_path = os.path.join(sprite_dir, filename)
                        available_sprites.append(sprite_path)
        
        if available_sprites:
            # 随机选择一个精灵
            selected_sprite = random.choice(available_sprites)
            try:
                # 加载GIF动画帧
                self.load_gif_frames(selected_sprite)
                print(f"已加载精灵: {selected_sprite}")
            except Exception as e:
                print(f"加载精灵失败 {selected_sprite}: {e}")
                self.sprite_frames = []
        else:
            print("未找到精灵动图文件")
            self.sprite_frames = []
    
    def load_gif_frames(self, gif_path):
        """加载GIF的所有帧"""
        self.sprite_frames = []
        try:
            gif = Image.open(gif_path)
            for frame in ImageSequence.Iterator(gif):
                # 转换为RGBA模式
                frame = frame.convert('RGBA')
                # 转换为pygame surface
                frame_surface = pygame.image.fromstring(
                    frame.tobytes(), frame.size, 'RGBA'
                )
                self.sprite_frames.append(frame_surface)
            
            self.sprite_frame_index = 0
            print(f"GIF加载成功，共 {len(self.sprite_frames)} 帧")
        except Exception as e:
            print(f"加载GIF帧失败: {e}")
            self.sprite_frames = []
    
    def create_layout(self):
        """创建页面布局 - 弹性盒子模式"""
        # 基于比例的尺寸计算
        def scaled(value):
            return int(value * self.scale_factor)
        
        margin = scaled(40)
        
        # 左侧卡包区域 - 使用弹性布局
        pack_area_width = int(self.screen_width * 0.65)
        pack_width = scaled(216)  # 再次放大卡包
        pack_height = scaled(360)  # 再次放大卡包
        
        # 减小卡包间距到30像素（比例化）
        pack_spacing = scaled(45)
        total_pack_width = pack_width * 3 + pack_spacing * 2
        pack_margin_y = scaled(5)  
        pack_start_x = (pack_area_width - total_pack_width) // 2
        pack_y = (self.content_height - pack_height) // 2 - pack_margin_y
        
        self.pack_areas = []
        pack_names = ["FESTIVAL BRILLANTE", "GUARDIANES CELESTIALES", "GUARDIANES CELESTIALES"]
        
        for i in range(3):
            x = pack_start_x + i * (pack_width + pack_spacing)
            pack_rect = pygame.Rect(x, pack_y, pack_width, pack_height)
            self.pack_areas.append({
                'rect': pack_rect,
                'type': f'pack_{i+1}',
                'name': pack_names[i] if i < len(pack_names) else f'Sobre {i+1}',
                'hover': False,
                'image': self.selected_pack_images[i][0] if i < len(self.selected_pack_images) else None
            })
        
        # 右侧区域布局 - 弹性布局
        right_area_x = pack_area_width + margin // 2
        right_area_width = self.screen_width - right_area_x - margin
        
        # 功能按钮 - 更高更华丽
        function_width = int(right_area_width * 0.4)
        function_height = scaled(200)  # 增加高度
        function_y = scaled(80)
        function_spacing = (right_area_width - function_width * 2) // 3
        
        # 魔法选择区域
        magic_x = right_area_x + function_spacing
        self.magic_area = {
            'rect': pygame.Rect(magic_x, function_y, function_width, function_height),
            'title': 'Elecciones mágicas',
            'icon': 'magic', # 使用图标名称
            'hover': False
        }
        
        # 商店区域
        shop_x = magic_x + function_width + function_spacing
        self.shop_area = {
            'rect': pygame.Rect(shop_x, function_y, function_width, function_height),
            'title': 'Tienda',
            'icon': 'shop', # 使用图标名称
            'hover': False
        }
        
        # 精灵区域 - 加大一倍，向左移动
        sprite_size = scaled(280)  # 放大一倍
        sprite_margin_x = scaled(100)  # 向左移动一些
        sprite_margin_y = scaled(90)
        sprite_x = self.screen_width - sprite_size - sprite_margin_x
        sprite_y = self.content_height - sprite_size - sprite_margin_y
        
        self.sprite_area = {
            'rect': pygame.Rect(sprite_x, sprite_y, sprite_size, sprite_size),
            'hover': False
        }
        
        # 创建pygame_gui元素
        self.create_ui_elements()
    
    def load_logo(self):
        """加载Logo"""
        try:
            logo_path = os.path.join("assets", "images", "logo", "game_logo.png")
            if os.path.exists(logo_path):
                self.logo = pygame.image.load(logo_path)
                # 调整Logo大小 - 左上角小logo
                logo_width = int(self.screen_width * 0.16)  # 改为8%宽度
                logo_height = int(logo_width * (self.logo.get_height() / self.logo.get_width()))
                self.logo = pygame.transform.smoothscale(self.logo, (logo_width, logo_height))
                print("✅ Logo加载成功")
        except Exception as e:
            print(f"⚠️ Logo加载失败: {e}")

    # def load_subtitle_logo(self):
    #     """加载副标题Logo"""
    #     try:
    #         logo_path = os.path.join("assets", "images", "logo", "secondLogo.png")
    #         if os.path.exists(logo_path):
    #             self.subtitle_logo = pygame.image.load(logo_path)
    #             # 调整副标题Logo大小 - 左上角小logo
    #             logo_width = int(self.screen_width * 0.10)  # 改为12%宽度
    #             logo_height = int(logo_width * (self.subtitle_logo.get_height() / self.subtitle_logo.get_width()))
    #             self.subtitle_logo = pygame.transform.smoothscale(self.subtitle_logo, (logo_width, logo_height))
    #             print("✅ 副标题Logo加载成功")
    #     except Exception as e:
    #         print(f"⚠️ 副标题Logo加载失败: {e}")

    def create_ui_elements(self):
        """创建pygame_gui UI元素"""
        # 清理旧元素
        for element_list in self.ui_elements.values():
            if isinstance(element_list, list):
                for element in element_list:
                    if element:
                        element.kill()
            elif element_list:
                element_list.kill()
        
        # 重置UI元素字典
        self.ui_elements = {
            'magic_button': None,
            'shop_button': None,
            'pack_buttons': []
        }
        
        # 创建魔法选择按钮
        magic_rect = self.magic_area['rect']
        self.ui_elements['magic_button'] = UIButton(
            relative_rect=pygame.Rect(magic_rect.x, magic_rect.y, magic_rect.width, magic_rect.height),
            text='✨ Elecciones mágicas',
            manager=self.ui_manager,
            object_id=ObjectID('#magic_button')
        )
        
        # 创建商店按钮
        shop_rect = self.shop_area['rect']
        self.ui_elements['shop_button'] = UIButton(
            relative_rect=pygame.Rect(shop_rect.x, shop_rect.y, shop_rect.width, shop_rect.height),
            text='🛍️ Tienda',
            manager=self.ui_manager,
            object_id=ObjectID('#shop_button')
        )
        # self.ui_elements['shop_button'].visible = True
        
        # 创建卡包按钮（透明，仅用于边框效果）
        for i, pack in enumerate(self.pack_areas):
            pack_rect = pack['rect']
            pack_button = UIButton(
                relative_rect=pygame.Rect(pack_rect.x, pack_rect.y, pack_rect.width, pack_rect.height),
                text='',
                manager=self.ui_manager,
                object_id=ObjectID('#pack_button')
            )
            self.ui_elements['pack_buttons'].append(pack_button)

        print(f"[调试] shop_button.rect = {self.ui_elements['shop_button'].rect}")
        print(f"[检查] shop_button enabled: {self.ui_elements['shop_button'].is_enabled}")
        print(f"[检查] shop_button visible: {self.ui_elements['shop_button'].visible}")
        print(f"[检查] UIManager window size: {self.ui_manager.window_resolution}")
        print(f"[检查] shop_button absolute rect: {self.ui_elements['shop_button'].rect}")
        print(f"[检查] mouse pos在UI区域内: {self.ui_elements['shop_button'].rect.collidepoint(pygame.mouse.get_pos())}")


    def handle_ui_event(self, event):
        """处理pygame_gui事件"""
        # print(f"[事件] 收到事件: {event}")
        result = None
        
        # 优先处理开包界面事件
        if self.active_windows['pack_opening'] and self.active_windows['pack_opening'].is_visible:
            pack_result = self.active_windows['pack_opening'].handle_event(event)
            if pack_result:
                return f"pack_opening_{pack_result}"

        # 处理窗口事件
        for window_name, window in self.active_windows.items():
            if window and window.is_visible:
                window_result = window.handle_event(event)
                if window_result:
                    result = f"{window_name}_{window_result}"

        # 处理UI事件
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            print(f"[UI事件] 按下了按钮: {event.ui_element}")
            if event.ui_element == self.ui_elements['magic_button']:
                print("[UI事件] 是 magic_button")
                # self.show_emagica_window()
                if self.on_magic_click:
                    self.on_magic_click()
                result = "magic"
            
            elif event.ui_element == self.ui_elements['shop_button']:
                print("[UI事件] 是 shop_button")
                # self.show_tienda_window()
                if self.on_shop_click:
                    self.on_shop_click()
                result = "shop"
            
            # 检查卡包按钮
            for i, pack_button in enumerate(self.ui_elements['pack_buttons']):
                if event.ui_element == pack_button:
                    self.show_package_window(i, self.pack_areas[i]['type'])
                    if self.on_pack_click:
                        self.on_pack_click(i, self.pack_areas[i]['type'])
                    result = f"pack_{i}"
                    break
        
        return result
    
    # def show_package_window(self, pack_index: int, pack_type: str):
    #     """显示卡包窗口"""
    #     if not WINDOWS_AVAILABLE:
    #         print("📦 [占位符] 显示卡包窗口")
    #         return
        
    #     # 关闭现有的卡包窗口
    #     if self.active_windows['package']:
    #         self.active_windows['package'].close()
        
    #     # 创建新的卡包窗口
    #     try:
    #         self.active_windows['package'] = PackageWindow(
    #             self.screen_width, 
    #             self.screen_height, 
    #             self.ui_manager, 
    #             pack_index, 
    #             pack_type
    #         )
    #         self.active_windows['package'].on_close = lambda: self.close_window('package')
    #         print(f"📦 显示卡包窗口: 索引{pack_index}, 类型{pack_type}")
    #     except Exception as e:
    #         print(f"❌ 创建卡包窗口失败: {e}")

    def show_package_window(self, pack_index: int, pack_type: str):
        """显示开包界面"""
        if not WINDOWS_AVAILABLE:
            print("📦 [占位符] 显示开包界面")
            return
        
        # 关闭现有的开包窗口
        if self.active_windows['pack_opening']:
            self.active_windows['pack_opening'].close()
        
        # 创建新的开包窗口
        try:
            self.active_windows['pack_opening'] = PackOpeningWindow(
                self.screen_width, 
                self.screen_height, 
                self.game_manager  # 传入game_manager而不是其他参数
            )
            self.active_windows['pack_opening'].show()
            print(f"📦 显示开包界面: 索引{pack_index}, 类型{pack_type}")
        except Exception as e:
            print(f"❌ 创建开包界面失败: {e}")
    
    def show_emagica_window(self):
        """显示魔法选择窗口"""
        if not WINDOWS_AVAILABLE:
            print("✨ [占位符] 显示魔法选择窗口")
            return
        
        # 关闭现有的魔法窗口
        if self.active_windows['e_magica']:
            self.active_windows['e_magica'].close()
        
        # 创建新的魔法窗口
        try:
            self.active_windows['e_magica'] = EMagicaWindow(
                self.screen_width, 
                self.screen_height, 
                self.ui_manager
            )
            self.active_windows['e_magica'].on_close = lambda: self.close_window('e_magica')
            print("✨ 显示魔法选择窗口")
        except Exception as e:
            print(f"❌ 创建魔法选择窗口失败: {e}")
    
    # def show_tienda_window(self):
    #     """显示商店窗口"""
    #     if not WINDOWS_AVAILABLE:
    #         print("🛍️ [占位符] 显示商店窗口")
    #         return
        
    #     # 关闭现有的商店窗口
    #     if self.active_windows['tienda']:
    #         self.active_windows['tienda'].close()
        
    #     # 创建新的商店窗口
    #     try:
    #         self.active_windows['tienda'] = TiendaWindow(
    #             self.screen_width, 
    #             self.screen_height, 
    #             self.ui_manager
    #         )
    #         self.active_windows['tienda'].on_close = lambda: self.close_window('tienda')
    #         print("🛍️ 显示商店窗口")
    #     except Exception as e:
    #         print(f"❌ 创建商店窗口失败: {e}")

    # 新的现代化商店窗口方法
    def show_tienda_window(self):
        """显示现代化商店窗口"""
        # 关闭现有的商店窗口
        if self.active_windows['tienda']:
            self.active_windows['tienda'].close()
        
        # 创建新的现代化商店窗口
        try:
            self.active_windows['tienda'] = ModernTiendaWindow(
                self.screen_width, 
                self.screen_height, 
                self.ui_manager,
                self.db_manager  # 新增的参数
            )
            self.active_windows['tienda'].is_visible = True
            self.active_windows['tienda'].on_close = lambda: self.close_window('tienda')
            print("🛍️ 显示现代化商店窗口")
        except Exception as e:
            print(f"❌ 创建现代化商店窗口失败: {e}")
    
    # def close_window(self, window_name: str):
    #     """关闭指定窗口"""
    #     if window_name in self.active_windows:
    #         self.active_windows[window_name] = None
    #         print(f"🚪 关闭窗口: {window_name}")
    
    def close_window(self, window_name: str):
        """关闭指定窗口"""
        if window_name in self.active_windows and self.active_windows[window_name]:
            if hasattr(self.active_windows[window_name], 'close'):
                self.active_windows[window_name].close()
            self.active_windows[window_name] = None
            print(f"🚪 关闭窗口: {window_name}")

    def close_all_windows(self):
        """关闭所有弹出窗口"""
        for window_name, window in self.active_windows.items():
            if window and window.is_visible:
                window.close()
        self.active_windows = {key: None for key in self.active_windows.keys()}
        print("🚪 关闭所有弹出窗口")
    
    def update_sprite_animation(self):
        """更新精灵动画 - 包含淡出淡入效果"""
        if not self.sprite_frames:
            return
        
        # 正常播放动画
        if self.sprite_fade_state == "normal":
            self.sprite_animation_timer += 16
            if self.sprite_animation_timer >= self.sprite_frame_duration:
                self.sprite_frame_index = (self.sprite_frame_index + 1) % len(self.sprite_frames)
                self.sprite_animation_timer = 0
        
        # 抖动状态
        elif self.sprite_fade_state == "shaking":
            self.sprite_shake_timer -= 16
            if self.sprite_shake_timer <= 0:
                # 抖动完成，开始淡出
                self.sprite_fade_state = "fading"
                self.sprite_fade_timer = 300  # 300ms淡出时间
            else:
                # 继续抖动
                shake_intensity = self.sprite_shake_timer / 200.0
                self.sprite_shake_offset[0] = random.uniform(-4, 4) * shake_intensity
                self.sprite_shake_offset[1] = random.uniform(-4, 4) * shake_intensity
        
        # 淡出状态
        elif self.sprite_fade_state == "fading":
            self.sprite_fade_timer -= 16
            self.sprite_fade_alpha = int(255 * (self.sprite_fade_timer / 300.0))
            
            if self.sprite_fade_timer <= 0:
                # 淡出完成，切换精灵
                self.sprite_fade_state = "switching"
                self.load_random_sprite()
                self.sprite_fade_timer = 300  # 300ms淡入时间
                self.sprite_fade_alpha = 0
        
        # 切换并淡入状态
        elif self.sprite_fade_state == "switching":
            self.sprite_fade_timer -= 16
            self.sprite_fade_alpha = int(255 * (1.0 - self.sprite_fade_timer / 300.0))
            
            if self.sprite_fade_timer <= 0:
                # 淡入完成，回到正常状态
                self.sprite_fade_state = "normal"
                self.sprite_fade_alpha = 255
                self.sprite_shake_offset = [0, 0]
            
            # 正常播放新精灵的动画
            self.sprite_animation_timer += 16
            if self.sprite_animation_timer >= self.sprite_frame_duration:
                self.sprite_frame_index = (self.sprite_frame_index + 1) % len(self.sprite_frames)
                self.sprite_animation_timer = 0
    
    def update_button_animations(self):
        """更新按钮动画"""
        # 更新魔法按钮动画
        if self.ui_elements['magic_button'] and self.ui_elements['magic_button'].hovered:
            self.target_magic_scale = 1.05
        else:
            self.target_magic_scale = 1.0
        
        self.magic_hover_scale += (self.target_magic_scale - self.magic_hover_scale) * 0.12
        
        # 更新商店按钮动画
        if self.ui_elements['shop_button'] and self.ui_elements['shop_button'].hovered:
            self.target_shop_scale = 1.05
        else:
            self.target_shop_scale = 1.0
        
        self.shop_hover_scale += (self.target_shop_scale - self.shop_hover_scale) * 0.12
    
    def draw_luxury_button(self, screen: pygame.Surface, area_data: dict, scale: float):
        """绘制现代毛玻璃风格按钮"""
        rect = area_data['rect']
        is_hover = scale > 1.0
        
        # 应用缩放
        if scale != 1.0:
            scaled_width = int(rect.width * scale)
            scaled_height = int(rect.height * scale)
            animated_rect = pygame.Rect(
                rect.centerx - scaled_width // 2,
                rect.centery - scaled_height // 2,
                scaled_width,
                scaled_height
            )
        else:
            animated_rect = rect
        
        # 现代圆角矩形阴影效果 - 更柔和
        shadow_offset = 8 if is_hover else 4
        shadow_blur_layers = 3 if is_hover else 2
        shadow_radius = int(20 * self.scale_factor)  # 阴影圆角半径

        for i in range(shadow_blur_layers):
            shadow_alpha = (20 - i * 6) if is_hover else (15 - i * 5)
            if shadow_alpha > 0:
                shadow_rect = animated_rect.copy()
                shadow_rect.x += shadow_offset + i
                shadow_rect.y += shadow_offset + i
                shadow_rect.width += i * 2
                shadow_rect.height += i * 2
                
                # 创建圆角矩形阴影
                shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surface, (0, 0, 0, shadow_alpha), 
                                (0, 0, shadow_rect.width, shadow_rect.height), 
                                border_radius=shadow_radius + i)
                
                screen.blit(shadow_surface, (shadow_rect.x - i, shadow_rect.y - i))
        
        # 毛玻璃背景效果
        radius = int(20 * self.scale_factor)
        bg_surface = pygame.Surface((animated_rect.width, animated_rect.height), pygame.SRCALPHA)
        
        # 主背景 - 毛玻璃效果
        if is_hover:
            bg_color = (*self.colors['button_hover_bg'], 220)
        else:
            bg_color = (*self.colors['glass_bg_modern'][:3], 200)
        
        bg_surface.fill(bg_color)
        
        # 应用圆角蒙版
        mask = pygame.Surface((animated_rect.width, animated_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, animated_rect.width, animated_rect.height), border_radius=radius)
        
        final_surface = pygame.Surface((animated_rect.width, animated_rect.height), pygame.SRCALPHA)
        final_surface.blit(bg_surface, (0, 0))
        final_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # 添加顶部高光效果（完全圆角毛玻璃反光）
        highlight_height = animated_rect.height // 3
        highlight_surface = pygame.Surface((animated_rect.width, highlight_height), pygame.SRCALPHA)

        # 创建完全圆角矩形高光
        pygame.draw.rect(highlight_surface, (*self.colors['button_shadow_light'][:3], 40),
                        (0, 0, animated_rect.width, highlight_height),
                        border_radius=radius)

        final_surface.blit(highlight_surface, (0, 0))
        
        screen.blit(final_surface, animated_rect.topleft)
        
        # 轻微立体感 - 减半宽度版本
        # 顶部内侧高光 - 高度减半
        inner_highlight = pygame.Rect(animated_rect.x + 0.5, animated_rect.y + 0.5, 
                                    animated_rect.width - 2, 1)
        highlight_surface = pygame.Surface((inner_highlight.width, inner_highlight.height), pygame.SRCALPHA)
        highlight_surface.fill((255, 255, 255, 30))
        screen.blit(highlight_surface, inner_highlight)

        # 底部内侧阴影 - 高度减半
        inner_shadow = pygame.Rect(animated_rect.x + 0.5, animated_rect.bottom - 1, 
                                animated_rect.width - 2, 1)
        shadow_surface = pygame.Surface((inner_shadow.width, inner_shadow.height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 20))
        screen.blit(shadow_surface, inner_shadow)

        # hover时稍微加强效果
        if is_hover:
            # 额外的顶部高光 - 也减半
            top_glow = pygame.Rect(animated_rect.x + 1, animated_rect.y + 1, 
                                animated_rect.width - 4, 1)
            glow_surface = pygame.Surface((top_glow.width, top_glow.height), pygame.SRCALPHA)
            glow_surface.fill((255, 255, 255, 40))
            screen.blit(glow_surface, top_glow)

        # 图标和文字 - 使用PNG图标的垂直布局
        # 绘制PNG图标（在按钮上方70%区域）
        icon_to_use = None
        if area_data['icon'] == 'magic' and self.magic_icon:
            icon_to_use = self.magic_icon
        elif area_data['icon'] == 'shop' and self.shop_icon:
            icon_to_use = self.shop_icon

        if icon_to_use:
            # 图标放在按钮上方70%的区域居中
            icon_area_height = int(animated_rect.height * 0.85)
            icon_x = animated_rect.centerx - icon_to_use.get_width() // 2
            icon_y = animated_rect.y + (icon_area_height - icon_to_use.get_height()) // 2
            screen.blit(icon_to_use, (icon_x, icon_y))
        else:
            # 如果图标加载失败，显示文字占位符
            icon_font = pygame.font.SysFont("arial", int(32 * self.scale_factor))
            fallback_text = "✨" if area_data['icon'] == 'magic' else "🛍️"
            icon_surface = icon_font.render(fallback_text, True, self.colors['accent'])
            icon_area_height = int(animated_rect.height * 0.85)
            icon_rect = icon_surface.get_rect(center=(animated_rect.centerx, animated_rect.y + icon_area_height // 2))
            screen.blit(icon_surface, icon_rect)

        # 绘制文字（在按钮底部）
        title_color = self.colors['accent'] if is_hover else self.colors['text']
        title_surface = self.fonts['subtitle'].render(area_data['title'], True, title_color)
        title_rect = title_surface.get_rect(center=(animated_rect.centerx, animated_rect.bottom - int(30 * self.scale_factor)))
        screen.blit(title_surface, title_rect)
    
    def draw_pack_image_only(self, screen: pygame.Surface, pack_data: dict, index: int):
        """只绘制卡包图片（边框由UI按钮处理）"""
        rect = pack_data['rect']
        ui_button = self.ui_elements['pack_buttons'][index]
        is_hover = ui_button.hovered
        
        # 平滑缩放动画
        if is_hover:
            self.target_pack_scale[index] = 1.15
        else:
            self.target_pack_scale[index] = 1.0
        
        self.pack_hover_scale[index] += (self.target_pack_scale[index] - self.pack_hover_scale[index]) * 0.12
        
        # 应用缩放
        scale = self.pack_hover_scale[index]
        if scale != 1.0:
            scaled_width = int(rect.width * scale)
            scaled_height = int(rect.height * scale)
            animated_rect = pygame.Rect(
                rect.centerx - scaled_width // 2,
                rect.centery - scaled_height // 2,
                scaled_width,
                scaled_height
            )
        else:
            animated_rect = rect
        
        # # 高质量阴影
        # shadow_offset = 10 if is_hover else 8
        # shadow_rect = animated_rect.copy()
        # shadow_rect.x += shadow_offset
        # shadow_rect.y += shadow_offset
        
        # # 创建模糊阴影效果
        # shadow_surface = pygame.Surface((shadow_rect.width + 15, shadow_rect.height + 15), pygame.SRCALPHA)
        # for i in range(6):
        #     alpha = (80 - i * 12) if is_hover else (50 - i * 8)
        #     if alpha > 0:
        #         pygame.draw.rect(shadow_surface, (0, 0, 0, alpha), 
        #                        (i, i, shadow_rect.width - i*2, shadow_rect.height - i*2), 
        #                        border_radius=15)
        
        # screen.blit(shadow_surface, (shadow_rect.x - 7, shadow_rect.y - 7))
        
        # 绘制椭圆羽化阴影
        shadow_offset_y = int(25 * self.scale_factor)  # 阴影垂直偏移
        shadow_width = int(animated_rect.width * 0.8)  # 阴影宽度（比卡包稍窄）
        shadow_height = int(shadow_width * 0.3)        # 阴影高度（椭圆扁平）

        # 阴影中心位置
        shadow_center_x = animated_rect.centerx
        shadow_center_y = animated_rect.bottom + shadow_offset_y

        # 创建羽化效果 - 多层椭圆
        feather_layers = 16  # 羽化层数
        for i in range(feather_layers):
            # 计算当前层的参数
            layer_scale = 1.0 + (i * 0.075)  # 每层递增15%
            layer_alpha = max(0, 30 - i * 1.875)  # 透明度递减
            
            # 当前层椭圆尺寸
            layer_width = int(shadow_width * layer_scale)
            layer_height = int(shadow_height * layer_scale)
            
            # 创建椭圆表面
            if layer_alpha > 0:
                ellipse_surface = pygame.Surface((layer_width, layer_height), pygame.SRCALPHA)
                
                # 绘制椭圆
                pygame.draw.ellipse(
                    ellipse_surface, 
                    (0, 0, 0, layer_alpha),  # 黑色半透明
                    (0, 0, layer_width, layer_height)
                )
                
                # 绘制到屏幕
                ellipse_rect = ellipse_surface.get_rect(center=(shadow_center_x, shadow_center_y))
                screen.blit(ellipse_surface, ellipse_rect)

        # 绘制卡包图片
        if pack_data['image']:
            scaled_image = pygame.transform.scale(pack_data['image'], (animated_rect.width, animated_rect.height))
            screen.blit(scaled_image, animated_rect)
        else:
            # 占位符
            pygame.draw.rect(screen, (200, 200, 200), animated_rect, border_radius=15)
            placeholder_text = self.fonts['pack_title'].render("No Image", True, self.colors['text_secondary'])
            text_rect = placeholder_text.get_rect(center=animated_rect.center)
            screen.blit(placeholder_text, text_rect)
    
    def draw_sprite_area(self, screen: pygame.Surface):
        """绘制精灵装饰区域"""
        if not self.sprite_frames:
            return
        
        rect = self.sprite_area['rect']
        is_hover = self.sprite_area['hover']
        
        # 平滑缩放动画
        if is_hover:
            self.target_sprite_scale = 1.1
        else:
            self.target_sprite_scale = 1.0
        
        # 平滑过渡
        self.sprite_hover_scale += (self.target_sprite_scale - self.sprite_hover_scale) * 0.1
        
        # 应用缩放和抖动
        scale = self.sprite_hover_scale
        shake_x, shake_y = self.sprite_shake_offset
        
        if scale != 1.0:
            scaled_width = int(rect.width * scale)
            scaled_height = int(rect.height * scale)
            animated_rect = pygame.Rect(
                rect.centerx - scaled_width // 2 + shake_x,
                rect.centery - scaled_height // 2 + shake_y,
                scaled_width,
                scaled_height
            )
        else:
            animated_rect = pygame.Rect(
                rect.x + shake_x,
                rect.y + shake_y,
                rect.width,
                rect.height
            )
        
        # 绘制当前帧（带透明度）
        current_frame = self.sprite_frames[self.sprite_frame_index].copy()

        # 应用透明度
        if self.sprite_fade_alpha < 255:
            alpha_surface = pygame.Surface(current_frame.get_size(), pygame.SRCALPHA)
            alpha_surface.fill((255, 255, 255, self.sprite_fade_alpha))
            current_frame.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        scaled_sprite = pygame.transform.scale(current_frame, (animated_rect.width, animated_rect.height))
        screen.blit(scaled_sprite, animated_rect)
    
    def handle_mouse_motion(self, pos: tuple):
        """处理鼠标移动事件"""
        # 检查精灵悬停
        self.sprite_area['hover'] = self.sprite_area['rect'].collidepoint(pos)
    
    def handle_mouse_click(self, pos: tuple) -> Optional[str]:
        """处理鼠标点击事件"""
        # 检查精灵区域点击
        if self.sprite_area['rect'].collidepoint(pos):
            # 只有在正常状态下才能触发新的动画
            if self.sprite_fade_state == "normal":
                self.sprite_fade_state = "shaking"
                self.sprite_shake_timer = 200  # 200ms抖动
                if self.on_sprite_click:
                    self.on_sprite_click()
            return "sprite"
        
        return None
    
    def set_pack_data(self, pack_index: int, pack_type: str, pack_name: str):
        """设置卡包数据"""
        if 0 <= pack_index < len(self.pack_areas):
            self.pack_areas[pack_index]['type'] = pack_type
            self.pack_areas[pack_index]['name'] = pack_name
    
    def refresh_pack_selection(self):
        """重新随机选择卡包"""
        self.load_pack_images()
        for i, pack in enumerate(self.pack_areas):
            if i < len(self.selected_pack_images):
                pack['image'] = self.selected_pack_images[i][0]
    
    def resize(self, new_width: int, new_height: int):
        """调整页面大小"""
        self.screen_width = new_width
        self.screen_height = new_height
        self.content_height = new_height - self.nav_bar_height
        self.content_rect = pygame.Rect(0, 0, new_width, self.content_height)
        
        # 重新计算缩放因子
        self.scale_factor = min(new_width / self.base_width, (new_height - self.nav_bar_height) / (self.base_height - self.nav_bar_height))
        
        # 重新设置UI管理器大小
        self.ui_manager.set_window_resolution((new_width, self.content_height))
        
        # 重新加载字体（因为缩放因子改变了）
        self.fonts = self.load_fonts()

        # 重新加载图标以适应新尺寸
        self.load_icons()
        
        # 关闭所有弹出窗口（它们需要重新创建以适应新尺寸）
        self.close_all_windows()
        
        self.create_layout()

        # 重新加载logo和副标题logo
        self.load_logo()
        # self.load_subtitle_logo()
    
    # def update_windows(self, time_delta: float):
    #     """更新所有活跃窗口"""
    #     for window_name, window in self.active_windows.items():
    #         if window and window.is_visible:
    #             try:
    #                 window.update(time_delta)
    #             except Exception as e:
    #                 print(f"⚠️ 更新窗口 {window_name} 时出错: {e}")

    def update_windows(self, time_delta: float):
        """更新所有活跃窗口"""
        # 特殊处理开包窗口的更新
        if self.active_windows['pack_opening'] and self.active_windows['pack_opening'].is_visible:
            try:
                self.active_windows['pack_opening'].update(time_delta)
            except Exception as e:
                print(f"⚠️ 更新开包窗口时出错: {e}")
        
        # 其他窗口更新
        for window_name, window in self.active_windows.items():
            if window_name != 'pack_opening' and window and window.is_visible:
                try:
                    window.update(time_delta)
                except Exception as e:
                    print(f"⚠️ 更新窗口 {window_name} 时出错: {e}")
    
    def draw_windows(self, screen: pygame.Surface):
        """绘制所有活跃窗口的自定义内容"""
        for window_name, window in self.active_windows.items():
            if window and window.is_visible:
                try:
                    # 绘制窗口特定的自定义内容
                    # if hasattr(window, 'draw_custom_content'):
                    #     window.draw_custom_content(screen)
                    # elif hasattr(window, 'draw_magical_effects'):
                    #     window.draw_magical_effects(screen)
                    # elif hasattr(window, 'draw_shop_effects'):
                    #     window.draw_shop_effects(screen)
                    window.draw(screen)
                except Exception as e:
                    print(f"⚠️ 绘制窗口 {window_name} 自定义内容时出错: {e}")
    
    def draw_logo(self, screen: pygame.Surface):
        """绘制左上角Logo"""
        logo_margin = int(28 * self.scale_factor) # logo边距
        
        # if self.logo:
        #     # 主logo位置
        logo_x = logo_margin + int(10 * self.scale_factor)  # 向右偏移一些
        logo_y = logo_margin
        screen.blit(self.logo, (logo_x, logo_y))
            
        #     # 如果有副标题logo，放在主logo下方
        #     if self.subtitle_logo:
        #         subtitle_y = logo_y + self.logo.get_height() + int(10 * self.scale_factor)
        #         screen.blit(self.subtitle_logo, (logo_x, subtitle_y))
        # elif self.subtitle_logo:
        #     # 如果只有副标题logo
        #     logo_x = logo_margin + int(10 * self.scale_factor)  # 向右偏移一些
        #     logo_y = logo_margin
        #     screen.blit(self.subtitle_logo, (logo_x, logo_y))

    def draw(self, screen: pygame.Surface, time_delta: float):
        """绘制主页"""
        # 更新UI管理器
        self.ui_manager.update(time_delta)
        
        # 更新精灵动画
        self.update_sprite_animation()
        
        # 更新按钮动画
        self.update_button_animations()
        
        # 更新窗口
        self.update_windows(time_delta)
        
        # 绘制左上角logo
        self.draw_logo(screen)

        # 绘制精灵（背景层）
        self.draw_sprite_area(screen)
        
        # 绘制卡包区域（现在只绘制图片，边框由UI按钮处理）
        for i, pack in enumerate(self.pack_areas):
            self.draw_pack_image_only(screen, pack, i)
        
        # 绘制UI元素（透明按钮用于事件处理）
        self.ui_manager.draw_ui(screen)

        # 绘制华丽的功能按钮（在UI按钮下方作为装饰层）
        self.draw_luxury_button(screen, self.magic_area, self.magic_hover_scale)
        self.draw_luxury_button(screen, self.shop_area, self.shop_hover_scale)
        
        # 绘制窗口自定义内容（在UI之上）
        self.draw_windows(screen)

        # 添加开包窗口的特殊处理（因为它是全屏覆盖）
        if self.active_windows['pack_opening'] and self.active_windows['pack_opening'].is_visible:
            self.active_windows['pack_opening'].draw(screen)

        if self.ui_elements['shop_button']:
            real_rect = self.ui_elements['shop_button'].rect.move(
                self.ui_elements['shop_button'].relative_rect.topleft
            )
            # print(f"[验证] 鼠标位置: {pygame.mouse.get_pos()}")
            # print(f"[验证] 按钮区域: {real_rect}")
            # print(f"[验证] 命中按钮: {real_rect.collidepoint(pygame.mouse.get_pos())}")

        
    def cleanup(self):
        """清理资源"""
        # 关闭所有弹出窗口
        self.close_all_windows()
        
        # 清理UI元素
        for element_list in self.ui_elements.values():
            if isinstance(element_list, list):
                for element in element_list:
                    if element:
                        element.kill()
            elif element_list:
                element_list.kill()
        
        # 清理加载的图片
        for image_data in self.selected_pack_images:
            if image_data[0]:
                try:
                    del image_data[0]
                except:
                    pass
        
        # 添加数据库清理
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        
        # 清理精灵帧
        for frame in self.sprite_frames:
            try:
                del frame
            except:
                pass
        
        print("🧹 主页资源清理完成")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()