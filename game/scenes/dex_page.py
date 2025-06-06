"""
TCG卡牌图鉴页面 - 高性能优化版本
作为MainScene的子页面，展示用户的卡牌收集状态
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UITextEntryLine, UIDropDownMenu, UIVerticalScrollBar
from pygame_gui.core import ObjectID
import math
import os
import json
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum

# 导入数据库管理器和卡牌数据
try:
    from game.core.database.database_manager import DatabaseManager
    from game.core.cards.card_data import Card
    from game.core.auth.auth_manager import get_auth_manager
except ImportError:
    # 如果找不到，创建模拟版本
    class DatabaseManager:
        def __init__(self): pass
    class Card:
        def __init__(self): pass
    # def get_auth_manager(): return None
    get_auth_manager = lambda: None  # 添加这一行

class CollectionStatus(Enum):
    """收集状态枚举"""
    ALL = "todos"           # 全部
    OWNED = "tengo"         # 已拥有  
    MISSING = "falta"       # 缺少

class DexColors:
    """图鉴页面配色方案 - 与HomePage统一"""
    # 背景和卡片
    CARD_BG = (255, 255, 255, 250)
    CARD_HOVER = (255, 255, 255, 255)
    CARD_BORDER = (229, 231, 235)
    
    # 状态颜色
    PRIMARY = (88, 101, 242)         # 蓝紫色
    SUCCESS = (16, 185, 129)         # 已收集绿色
    WARNING = (245, 158, 11)         # 稀有金色
    GRAY = (107, 114, 128)           # 未收集灰色
    
    # 文字颜色
    TEXT_PRIMARY = (55, 65, 81)
    TEXT_SECONDARY = (107, 114, 128)
    TEXT_MUTED = (148, 163, 184)
    
    # 毛玻璃效果
    GLASS_BG = (255, 255, 255, 200)
    GLASS_BORDER = (255, 255, 255, 80)

class CardDisplay:
    """卡牌显示组件 - 性能优化版本"""
    
    def __init__(self, card: Card, card_manager, collection_data: Dict[str, Any] = None):
        self.card = card
        self.card_manager = card_manager  # 👈 添加card_manager引用
        self.collection_data = collection_data or {}
        
        # 显示属性
        self.width = 120
        self.height = 165  # 240x330比例
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        
        # 收集状态
        self.quantity = self.collection_data.get('quantity', 0)
        self.is_owned = self.quantity > 0
        self.obtained_at = self.collection_data.get('obtained_at')
        
        # 动画属性
        self.hover_scale = 1.0
        self.target_scale = 1.0
        self.shine_alpha = 0
        self.shine_offset = 0
        
        # 缓存
        self._cached_surface = None
        self._cache_dirty = True
        self._last_scale = 1.0
        
        # 预渲染静态内容
        self._create_static_surfaces()
    
    def _create_static_surfaces(self):
        """预创建静态表面"""
        # 加载卡牌图片 - 使用CardManager的方法
        self.card_image = None
        if hasattr(self.card, 'id') and self.card.id:
            # 👈 关键：需要传入card_manager引用
            image_path = self.card_manager.get_card_image_path(self.card.id)
            if image_path and os.path.exists(image_path):
                try:
                    original_image = pygame.image.load(image_path)
                    # 缩放到显示尺寸，保持宽高比
                    img_width = self.width - 8
                    img_height = int(img_width * 330 / 240)  # 保持240:330比例
                    self.card_image = pygame.transform.smoothscale(original_image, (img_width, img_height))
                    print(f"✅ 成功加载图片: {self.card.name} - {image_path}")
                except Exception as e:
                    print(f"❌ 加载卡牌图片失败 {self.card.id}: {e}")
            else:
                print(f"❌ 图片文件不存在: {image_path}")
        
        # 预渲染稀有度颜色
        self.rarity_color = self._get_rarity_color()
        
        # 预渲染文字
        self._render_text()
    
    def _get_rarity_color(self) -> Tuple[int, int, int]:
        """根据稀有度获取颜色"""
        rarity_colors = {
            'Common': (156, 163, 175),          # 灰色
            'Uncommon': (34, 197, 94),          # 绿色
            'Rare': (59, 130, 246),             # 蓝色
            'Rare Holo': (139, 69, 19),         # 棕色
            'Rare Holo EX': (168, 85, 247),     # 紫色
            'Rare Holo GX': (236, 72, 153),     # 粉红
            'Rare Holo V': (245, 158, 11),      # 橙色
            'Ultra Rare': (251, 191, 36),       # 金色
            'Rare Secret': (244, 63, 94),       # 红色
            'Amazing Rare': (236, 72, 153),     # 彩虹色
            'Rare Shiny': (192, 132, 252),      # 闪亮紫
            'Rare BREAK': (245, 101, 101),      # 断裂红
            'Rare Ultra': (124, 58, 237),       # 超稀有紫
            'Rare Shining': (252, 211, 77),     # 闪光金
            'Promo': (34, 197, 94),             # 促销绿
        }
        return rarity_colors.get(getattr(self.card, 'rarity', 'Common'), DexColors.GRAY)
    
    def _render_text(self):
        """预渲染文字"""
        # 名称（截断长名称）
        name_font = pygame.font.Font(None, 14)
        display_name = self.card.name[:10] + "..." if len(self.card.name) > 10 else self.card.name
        self.name_surface = name_font.render(display_name, True, DexColors.TEXT_PRIMARY)
        
        # 稀有度
        rarity_font = pygame.font.Font(None, 11)
        rarity_text = getattr(self.card, 'rarity', 'Common')
        if len(rarity_text) > 8:
            rarity_text = rarity_text[:8] + "..."
        self.rarity_surface = rarity_font.render(rarity_text, True, DexColors.TEXT_SECONDARY)
        
        # 数量（如果拥有）
        if self.is_owned:
            qty_font = pygame.font.Font(None, 16)
            self.quantity_surface = qty_font.render(f"x{self.quantity}", True, DexColors.SUCCESS)
        else:
            self.quantity_surface = None
    
    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        """更新动画"""
        # 检查悬停
        is_hovered = self.rect.collidepoint(mouse_pos)
        self.target_scale = 1.08 if is_hovered else 1.0
        
        # 平滑缩放
        scale_diff = self.target_scale - self.hover_scale
        self.hover_scale += scale_diff * dt * 12
        
        # 检查缓存
        if abs(self.hover_scale - self._last_scale) > 0.01:
            self._cache_dirty = True
            self._last_scale = self.hover_scale
        
        # 稀有卡闪光效果
        rarity = getattr(self.card, 'rarity', 'Common')
        if rarity in ['Ultra Rare', 'Amazing Rare', 'Rare Secret', 'Rare Shining']:
            self.shine_offset += dt * 2
            if self.shine_offset > math.pi * 2:
                self.shine_offset -= math.pi * 2
            self.shine_alpha = (math.sin(self.shine_offset) + 1) * 0.15 + 0.1
    
    def draw(self, screen: pygame.Surface, x: int, y: int):
        """绘制卡牌"""
        self.rect.x = x
        self.rect.y = y
        
        # 使用缓存的表面
        if self._cache_dirty or self._cached_surface is None:
            self._cached_surface = self._render_card()
            self._cache_dirty = False
        
        # 计算缩放后的位置
        if self.hover_scale != 1.0:
            scaled_width = int(self.width * self.hover_scale)
            scaled_height = int(self.height * self.hover_scale)
            scaled_x = x + (self.width - scaled_width) // 2
            scaled_y = y + (self.height - scaled_height) // 2
            
            # 绘制阴影
            if self.hover_scale > 1.02:
                shadow_size = 6
                shadow_surf = pygame.Surface((scaled_width + shadow_size, scaled_height + shadow_size), pygame.SRCALPHA)
                shadow_surf.fill((0, 0, 0, 40))
                screen.blit(shadow_surf, (scaled_x - shadow_size//2, scaled_y + shadow_size//2))
            
            # 绘制缩放的卡牌
            scaled_card = pygame.transform.scale(self._cached_surface, (scaled_width, scaled_height))
            screen.blit(scaled_card, (scaled_x, scaled_y))
        else:
            screen.blit(self._cached_surface, (x, y))
    
    def _render_card(self):
        """渲染卡牌到缓存表面"""
        card_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # 毛玻璃背景
        if self.is_owned:
            bg_color = DexColors.CARD_BG
            border_color = self.rarity_color
            border_width = 2
        else:
            bg_color = (*DexColors.GRAY, 120)  # 未拥有的半透明
            border_color = DexColors.GRAY
            border_width = 1
        
        # 绘制圆角背景
        pygame.draw.rect(card_surf, bg_color, card_surf.get_rect(), border_radius=8)
        pygame.draw.rect(card_surf, border_color, card_surf.get_rect(), border_width, border_radius=8)
        
        # 绘制卡牌图片
        if self.card_image:
            img_y = 8
            if self.is_owned:
                card_surf.blit(self.card_image, (4, img_y))
            else:
                # 未拥有的半透明显示
                img_copy = self.card_image.copy()
                img_copy.set_alpha(80)
                card_surf.blit(img_copy, (4, img_y))
        else:
            # 占位符
            img_height = int((self.width - 8) * 330 / 240)
            placeholder_rect = pygame.Rect(4, 8, self.width - 8, img_height)
            pygame.draw.rect(card_surf, DexColors.GRAY, placeholder_rect, border_radius=6)
            
            # "无图片"文字
            no_img_font = pygame.font.Font(None, 11)
            no_img_text = no_img_font.render("Sin imagen", True, DexColors.TEXT_MUTED)
            text_rect = no_img_text.get_rect(center=placeholder_rect.center)
            card_surf.blit(no_img_text, text_rect)
        
        # 绘制文字信息
        text_y = self.height - 35
        
        # 卡牌名称
        name_x = (self.width - self.name_surface.get_width()) // 2
        card_surf.blit(self.name_surface, (name_x, text_y))
        
        # 稀有度
        rarity_x = (self.width - self.rarity_surface.get_width()) // 2
        card_surf.blit(self.rarity_surface, (rarity_x, text_y + 15))
        
        # 数量标识
        if self.quantity_surface:
            card_surf.blit(self.quantity_surface, (self.width - 25, 5))
        
        # 状态指示器
        if self.is_owned:
            # 已拥有标识
            pygame.draw.circle(card_surf, DexColors.SUCCESS, (15, 15), 6)
            pygame.draw.circle(card_surf, (255, 255, 255), (15, 15), 3)
        
        # 稀有卡闪光效果
        if self.shine_alpha > 0:
            shine_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            shine_surf.fill((*DexColors.WARNING, int(self.shine_alpha * 255)))
            card_surf.blit(shine_surf, (0, 0), special_flags=pygame.BLEND_ADD)
        
        return card_surf

class DexPage:
    """TCG卡牌图鉴页面 - 高性能版本"""
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager, card_manager, nav_bar_height: int = 90):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        self.card_manager = card_manager
        self.nav_bar_height = nav_bar_height

        # 从card_manager获取db_manager
        self.db_manager = card_manager.card_dao if hasattr(card_manager, 'card_dao') else None
        
        # 内容区域
        self.content_height = screen_height - nav_bar_height
        
        # 认证管理器
        self.auth = get_auth_manager()
        self.current_user = None
        if self.auth:
            self.current_user = self.auth.get_user_info()
        
        # 数据
        self.all_cards: List[Card] = []
        self.filtered_cards: List[Card] = []
        self.user_collection: Dict[str, Dict] = {}
        self.card_displays: List[CardDisplay] = []
        
        # 滚动相关
        self.scroll_y = 0
        self.target_scroll = 0
        self.max_scroll = 0
        self.scroll_bar_alpha = 0.0
        self.scroll_bar_timer = 0.0
        self.scroll_bar_visible = False
        
        # 布局配置
        self.cards_per_row = 6
        self.card_spacing = 15
        self.content_start_y = 180
        self.card_width = 120
        self.card_height = 165
        
        # UI元素
        self.ui_elements = {}
        self.search_text = ""
        
        # 过滤器状态
        self.selected_rarities: Set[str] = set()
        self.selected_types: Set[str] = set()
        self.collection_filter = CollectionStatus.ALL
        self.effect_cards_only = False
        
        # 统计数据
        self.total_cards = 0
        self.owned_cards = 0
        self.completion_rate = 0.0
        
        print("🔍 初始化DexPage...")
        
        # 初始化数据
        self._load_card_data()
        self._load_user_collection()
        self._load_theme()
        self._create_ui_elements()
        self._apply_filters()
        
        # # 添加页面可见性控制
        # self.is_active = False  # 页面是否活跃

        print(f"✅ DexPage初始化完成 - {len(self.all_cards)} 张卡牌")
    
    def _load_card_data(self):
        """加载卡牌数据"""
        try:
            if self.card_manager:
                # 使用CardManager获取卡牌
                self.all_cards = self.card_manager.search_cards(limit=10000)
                print(f"从CardManager加载了 {len(self.all_cards)} 张卡牌")
            else:
                print("⚠️ CardManager不可用")
                self.all_cards = []
        except Exception as e:
            print(f"❌ 加载卡牌数据失败: {e}")
            self.all_cards = []
        
        self.total_cards = len(self.all_cards)
    
    def _load_user_collection(self):
        """加载用户收集数据"""
        try:
            if self.db_manager and self.current_user:
                user_id = self.current_user['id']
                user_cards = self.db_manager.get_user_cards(user_id)
                
                # 转换为字典格式
                self.user_collection = {}
                for card_data in user_cards:
                    self.user_collection[card_data['card_id']] = {
                        'quantity': card_data['quantity'],
                        'obtained_at': card_data['obtained_at']
                    }
                
                self.owned_cards = len(self.user_collection)
                self.completion_rate = (self.owned_cards / self.total_cards * 100) if self.total_cards > 0 else 0
                
                print(f"用户收集: {self.owned_cards}/{self.total_cards} ({self.completion_rate:.1f}%)")
            else:
                self.user_collection = {}
                self.owned_cards = 0
                self.completion_rate = 0.0
        except Exception as e:
            print(f"❌ 加载用户收集数据失败: {e}")
            self.user_collection = {}
    
    def _create_ui_elements(self):
        """创建UI元素"""
        # 清理旧元素
        for element in self.ui_elements.values():
            if element:
                element.kill()
        self.ui_elements = {}
        
        # 搜索框
        self.ui_elements['search'] = UITextEntryLine(
            relative_rect=pygame.Rect(20, 20, 300, 35),
            manager=self.ui_manager,
            object_id=ObjectID('#search_box')
        )
        self.ui_elements['search'].set_text_length_limit(50)
        self.ui_elements['search'].set_text("")
        
        # 稀有度下拉菜单
        rarities = self._get_all_rarities()
        self.ui_elements['rarity_dropdown'] = UIDropDownMenu(
            relative_rect=pygame.Rect(340, 20, 150, 35),
            options_list=['Todas las rarezas'] + rarities,
            starting_option='Todas las rarezas',
            manager=self.ui_manager,
            object_id=ObjectID('#rarity_dropdown')
        )
        
        # 类型下拉菜单  
        types = self._get_all_types()
        self.ui_elements['type_dropdown'] = UIDropDownMenu(
            relative_rect=pygame.Rect(510, 20, 150, 35),
            options_list=['Todos los tipos'] + types,
            starting_option='Todos los tipos',
            manager=self.ui_manager,
            object_id=ObjectID('#type_dropdown')
        )
        
        # 收集状态按钮组
        self.ui_elements['filter_all'] = UIButton(
            relative_rect=pygame.Rect(20, 70, 80, 30),
            text='Todas',
            manager=self.ui_manager,
            object_id=ObjectID('#filter_button_active' if self.collection_filter == CollectionStatus.ALL else '#filter_button')
        )
        
        self.ui_elements['filter_owned'] = UIButton(
            relative_rect=pygame.Rect(110, 70, 80, 30),
            text='Tengo',
            manager=self.ui_manager,
            object_id=ObjectID('#filter_button_active' if self.collection_filter == CollectionStatus.OWNED else '#filter_button')
        )
        
        self.ui_elements['filter_missing'] = UIButton(
            relative_rect=pygame.Rect(200, 70, 80, 30),
            text='Falta',
            manager=self.ui_manager,
            object_id=ObjectID('#filter_button_active' if self.collection_filter == CollectionStatus.MISSING else '#filter_button')
        )
        
        # 效果卡切换按钮
        self.ui_elements['effect_toggle'] = UIButton(
            relative_rect=pygame.Rect(300, 70, 120, 30),
            text='✨ Con efectos' if self.effect_cards_only else 'Con efectos',
            manager=self.ui_manager,
            object_id=ObjectID('#effect_button_active' if self.effect_cards_only else '#effect_button')
        )
        
        # 滚动条
        self._create_scrollbar()
          
    def _create_scrollbar(self):
        """创建滚动条（纯自定义）"""
        # 删除旧的滚动条
        if 'scrollbar' in self.ui_elements and self.ui_elements['scrollbar']:
            self.ui_elements['scrollbar'].kill()
            self.ui_elements['scrollbar'] = None
        
        # 计算滚动参数
        content_height = self._calculate_content_height()
        visible_height = self.screen_height - self.content_start_y - self.nav_bar_height
        
        self.max_scroll = max(0, content_height - visible_height)
    
    def _load_theme(self):
        """加载DexPage专用主题"""
        try:
            theme_path = os.path.join("game", "scenes", "styles", "dex_theme.json")
            if os.path.exists(theme_path):
                self.ui_manager.get_theme().load_theme(theme_path)
                print("✅ DexPage主题加载成功")
            else:
                print(f"⚠️ 主题文件未找到: {theme_path}")
                # 使用内嵌的备用主题
                self._setup_fallback_theme()
        except Exception as e:
            print(f"❌ 加载主题失败: {e}")
            self._setup_fallback_theme()

    def _setup_fallback_theme(self):
        """备用主题（简化版）"""
        theme_data = {
            '#search_box': {
                'colours': {
                    'normal_bg': '#F8FAFC',
                    'focused_bg': '#FFFFFF',
                    'normal_border': '#E5E7EB',
                    'focused_border': '#3B82F6'
                }
            },
            '#filter_button_active': {
                'colours': {
                    'normal_bg': '#3B82F6',
                    'normal_text': '#FFFFFF'
                }
            }
        }
        self.ui_manager.get_theme().load_theme(theme_data)
    
    # def set_active(self, active: bool):
    #     """设置页面是否活跃"""
    #     self.is_active = active

    def _get_all_rarities(self) -> List[str]:
        """获取所有稀有度"""
        try:
            if self.card_manager:
                return self.card_manager.card_dao.get_all_rarities()
            return []
        except Exception as e:
            print(f"获取稀有度失败: {e}")
            return []
        
    def _get_all_types(self) -> List[str]:
        """获取所有类型"""
        try:
            if self.card_manager:
                return self.card_manager.card_dao.get_all_types()
            return []
        except Exception as e:
            print(f"获取类型失败: {e}")
            return []
    
    def _calculate_content_height(self) -> int:
        """计算内容总高度"""
        if not self.filtered_cards:
            return 0
        
        rows = (len(self.filtered_cards) + self.cards_per_row - 1) // self.cards_per_row
        return rows * (self.card_height + self.card_spacing) + 100
    
    def _apply_filters(self):
        """应用过滤器"""
        self.filtered_cards = []
        
        for card in self.all_cards:
            # 搜索过滤
            if self.search_text:
                search_lower = self.search_text.lower()
                if (search_lower not in card.name.lower() and 
                    search_lower not in getattr(card, 'id', '').lower()):
                    continue
            
            # 稀有度过滤
            if self.selected_rarities and getattr(card, 'rarity', '') not in self.selected_rarities:
                continue
            
            # 类型过滤
            if self.selected_types:
                card_types = getattr(card, 'types', [])
                if isinstance(card_types, str):
                    try:
                        card_types = json.loads(card_types)
                    except:
                        card_types = []
                
                if not any(card_type in self.selected_types for card_type in card_types):
                    continue
            
            # 收集状态过滤
            is_owned = getattr(card, 'id', '') in self.user_collection
            if self.collection_filter == CollectionStatus.OWNED and not is_owned:
                continue
            elif self.collection_filter == CollectionStatus.MISSING and is_owned:
                continue
            
            # 效果卡过滤
            if self.effect_cards_only:
                attacks = getattr(card, 'attacks', [])
                if isinstance(attacks, str):
                    try:
                        attacks = json.loads(attacks)
                    except:
                        attacks = []
                
                has_effects = False
                if isinstance(attacks, list):
                    for attack in attacks:
                        if isinstance(attack, dict) and attack.get('text', '').strip():
                            has_effects = True
                            break
                
                if not has_effects:
                    continue
            
            self.filtered_cards.append(card)
        
        # 重新创建卡牌显示组件
        self._create_card_displays()
        
        # 更新滚动条
        self._create_scrollbar()
        
        print(f"过滤结果: {len(self.filtered_cards)}/{len(self.all_cards)} 张卡牌")
    
    def _create_card_displays(self):
        """创建卡牌显示组件"""
        self.card_displays = []
        
        for card in self.filtered_cards:
            collection_data = self.user_collection.get(getattr(card, 'id', ''), {})
            card_display = CardDisplay(card, self.card_manager, collection_data)  # 👈 传入card_manager
            self.card_displays.append(card_display)
    
    # def _show_scrollbar(self):
    #     """显示滚动条"""
    #     if self.ui_elements.get('scrollbar'):
    #         self.scroll_bar_visible = True
    #         self.scroll_bar_alpha = 1.0  # 直接设为1.0
    #         self.scroll_bar_timer = 2.0  # 2秒后开始淡出

    def _show_scrollbar(self):
        """显示滚动条"""
        if self.max_scroll > 0:  # 只有需要滚动时才显示
            self.scroll_bar_visible = True
            self.scroll_bar_alpha = 1.0
            self.scroll_bar_timer = 3.0  # 3秒后开始淡出
            # print(f"显示滚动条: max_scroll={self.max_scroll}")  # 临时调试
    
    def _hide_scrollbar(self):
        """隐藏滚动条"""
        self.scroll_bar_visible = False
    
    def handle_event(self, event) -> Optional[str]:
        """处理事件"""
        # # 🆕 如果页面不活跃，不处理任何事件
        # if not self.is_active:
        #     return None

        # 搜索框事件
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if event.ui_element == self.ui_elements.get('search'):
                self.search_text = event.text
                self._apply_filters()
        
        # 下拉菜单事件
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.ui_elements.get('rarity_dropdown'):
                selected = event.text
                if selected == 'Todas las rarezas':
                    self.selected_rarities.clear()
                else:
                    # 简单切换逻辑
                    if selected in self.selected_rarities:
                        self.selected_rarities.remove(selected)
                    else:
                        self.selected_rarities.add(selected)
                self._apply_filters()
            
            elif event.ui_element == self.ui_elements.get('type_dropdown'):
                selected = event.text
                if selected == 'Todos los tipos':
                    self.selected_types.clear()
                else:
                    # 简单切换逻辑
                    if selected in self.selected_types:
                        self.selected_types.remove(selected)
                    else:
                        self.selected_types.add(selected)
                self._apply_filters()
        
        # 按钮事件
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.ui_elements.get('filter_all'):
                self.collection_filter = CollectionStatus.ALL
                self._update_filter_buttons()
                self._apply_filters()
            
            elif event.ui_element == self.ui_elements.get('filter_owned'):
                self.collection_filter = CollectionStatus.OWNED
                self._update_filter_buttons()
                self._apply_filters()
            
            elif event.ui_element == self.ui_elements.get('filter_missing'):
                self.collection_filter = CollectionStatus.MISSING
                self._update_filter_buttons()
                self._apply_filters()
            
            elif event.ui_element == self.ui_elements.get('effect_toggle'):
                self.effect_cards_only = not self.effect_cards_only
                self._update_effect_button()
                self._apply_filters()
        
        # # 滚动条事件
        # elif hasattr(pygame_gui, 'UI_VERTICAL_SCROLL_BAR_MOVED') and event.type == pygame_gui.UI_VERTICAL_SCROLL_BAR_MOVED:
        #     if event.ui_element == self.ui_elements.get('scrollbar'):
        #         # 计算新的滚动位置
        #         scroll_percentage = self.ui_elements['scrollbar'].scroll_position
        #         self.scroll_y = self.max_scroll * scroll_percentage
        #         self.target_scroll = self.scroll_y
        #         self._show_scrollbar()
        
        # 鼠标滚轮
        elif event.type == pygame.MOUSEWHEEL:
            self.target_scroll -= event.y * 50
            self.target_scroll = max(0, min(self.target_scroll, self.max_scroll))
            self._show_scrollbar()
            
        # 在鼠标滚轮事件后添加
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键
                mouse_x, mouse_y = event.pos
                # 检查是否点击自定义滚动条
                scrollbar_x = self.screen_width - 20
                scrollbar_y = self.content_start_y + 10
                scrollbar_height = self.content_height - 40
                
                if (scrollbar_x <= mouse_x <= scrollbar_x + 8 and 
                    scrollbar_y <= mouse_y <= scrollbar_y + scrollbar_height):
                    # 计算点击位置对应的滚动值
                    click_ratio = (mouse_y - scrollbar_y) / scrollbar_height
                    self.target_scroll = self.max_scroll * click_ratio
                    self.target_scroll = max(0, min(self.target_scroll, self.max_scroll))
                    self._show_scrollbar()
            
            # 更新滚动条位置
            if self.ui_elements.get('scrollbar') and self.max_scroll > 0:
                scroll_percentage = self.target_scroll / self.max_scroll
                self.ui_elements['scrollbar'].set_scroll_from_start_percentage(scroll_percentage)
        
        # 键盘事件
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # 返回时隐藏UI而不是触发cleanup
                self.hide_ui_elements()
                return "back_to_home"
        
        return None
    
    def _update_filter_buttons(self):
        """更新过滤器按钮样式"""
        # 重新创建按钮以更新样式
        filters = [
            ('filter_all', 'Todas', CollectionStatus.ALL, 20),
            ('filter_owned', 'Tengo', CollectionStatus.OWNED, 110), 
            ('filter_missing', 'Falta', CollectionStatus.MISSING, 200)
        ]
        
        for key, text, status, x_pos in filters:
            if key in self.ui_elements:
                self.ui_elements[key].kill()
            
            object_id = '#filter_button_active' if self.collection_filter == status else '#filter_button'
            self.ui_elements[key] = UIButton(
                relative_rect=pygame.Rect(x_pos, 70, 80, 30),
                text=text,
                manager=self.ui_manager,
                object_id=ObjectID(object_id)
            )
    
    def _update_effect_button(self):
        """更新效果按钮样式"""
        if 'effect_toggle' in self.ui_elements:
            self.ui_elements['effect_toggle'].kill()
        
        object_id = '#effect_button_active' if self.effect_cards_only else '#effect_button'
        text = '✨ Con efectos' if self.effect_cards_only else 'Con efectos'
        
        self.ui_elements['effect_toggle'] = UIButton(
            relative_rect=pygame.Rect(300, 70, 120, 30),
            text=text,
            manager=self.ui_manager,
            object_id=ObjectID(object_id)
        )
    
    def update(self, dt: float):
        """更新页面"""
        # # 临时调试代码（测试完删除）
        # if hasattr(self, 'debug_timer'):
        #     self.debug_timer += dt
        #     if self.debug_timer > 1.0:  # 每秒打印一次
        #         print(f"滚动条状态: visible={self.scroll_bar_visible}, alpha={self.scroll_bar_alpha}, max_scroll={self.max_scroll}")
        #         self.debug_timer = 0
        # else:
        #     self.debug_timer = 0

        # 平滑滚动
        scroll_diff = self.target_scroll - self.scroll_y
        self.scroll_y += scroll_diff * dt * 12
        
        # 滚动条显示/隐藏逻辑
        if self.scroll_bar_visible:
            self.scroll_bar_timer -= dt
            if self.scroll_bar_timer <= 0:
                # 开始淡出
                self.scroll_bar_alpha -= dt * 2
                if self.scroll_bar_alpha <= 0:
                    self.scroll_bar_alpha = 0
                    self._hide_scrollbar()
                    if self.ui_elements.get('scrollbar'):
                        self.ui_elements['scrollbar'].visible = False
            else:
                # 淡入
                self.scroll_bar_alpha = min(1.0, self.scroll_bar_alpha + dt * 4)
                if self.ui_elements.get('scrollbar'):
                    self.ui_elements['scrollbar'].visible = True
        
        # # 更新可见区域的卡牌
        # mouse_pos = pygame.mouse.get_pos()
        # adjusted_mouse_y = mouse_pos[1] + self.scroll_y - self.content_start_y
        # adjusted_mouse_pos = (mouse_pos[0], adjusted_mouse_y)
        
        # # 计算可见范围
        # visible_start = max(0, int(self.scroll_y // (self.card_height + self.card_spacing)) * self.cards_per_row - self.cards_per_row)
        # visible_end = min(len(self.card_displays), visible_start + (self.cards_per_row * 8))
        
        # # 只更新可见卡牌
        # for i in range(visible_start, visible_end):
        #     if i < len(self.card_displays):
        #         self.card_displays[i].update(dt, adjusted_mouse_pos)

        # 更新可见区域的卡牌
        mouse_pos = pygame.mouse.get_pos()

        # 计算可见范围
        visible_start = max(0, int(self.scroll_y // (self.card_height + self.card_spacing)) * self.cards_per_row - self.cards_per_row)
        visible_end = min(len(self.card_displays), visible_start + (self.cards_per_row * 8))

        # 只更新可见卡牌
        for i in range(visible_start, visible_end):
            if i < len(self.card_displays):
                card_display = self.card_displays[i]
                
                # 计算卡牌屏幕位置（与draw方法保持一致）
                row = i // self.cards_per_row
                col = i % self.cards_per_row
                
                cards_area_width = self.cards_per_row * self.card_width + (self.cards_per_row - 1) * self.card_spacing
                start_x = (self.screen_width - cards_area_width) // 2
                
                card_x = start_x + col * (self.card_width + self.card_spacing)
                card_y = self.content_start_y + row * (self.card_height + self.card_spacing) - self.scroll_y
                
                # 更新卡牌rect到当前屏幕位置
                card_display.rect.x = card_x
                card_display.rect.y = card_y
                
                # 使用真实屏幕鼠标坐标
                card_display.update(dt, mouse_pos)
    
    def draw(self, screen: pygame.Surface):
        """绘制页面"""

        # # 🆕 如果页面不活跃，直接返回，什么都不绘制
        # if not self.is_active:
        #     return
        
        # 临时强制显示滚动条进行测试
        if self.max_scroll > 0:  # 只要有滚动就显示
            self._draw_custom_scrollbar(screen)

        # 绘制卡牌网格（虚拟滚动）
        self._draw_card_grid(screen)
        
        # 绘制顶部统计信息
        self._draw_header_stats(screen)
        
        # 绘制UI元素
        self.ui_manager.draw_ui(screen)
        
        # 绘制滚动条（如果可见）
        if self.scroll_bar_visible and self.scroll_bar_alpha > 0:
            self._draw_custom_scrollbar(screen)
    
    def _draw_header_stats(self, screen: pygame.Surface):
        """绘制顶部统计信息"""
        # 背景
        header_bg = pygame.Surface((self.screen_width, 150), pygame.SRCALPHA)
        header_bg.fill((*DexColors.GLASS_BG[:3], 180))
        screen.blit(header_bg, (0, 0))
        
        # 标题
        title_font = pygame.font.Font(None, 32)
        title_text = title_font.render("📖 Colección de Cartas", True, DexColors.TEXT_PRIMARY)
        screen.blit(title_text, (20, 120))
        
        # 统计信息
        stats_font = pygame.font.Font(None, 18)
        stats_text = f"Colección: {self.owned_cards}/{self.total_cards} ({self.completion_rate:.1f}%) | Mostrando: {len(self.filtered_cards)} cartas"
        stats_surface = stats_font.render(stats_text, True, DexColors.TEXT_SECONDARY)
        screen.blit(stats_surface, (self.screen_width - stats_surface.get_width() - 20, 125))
        
        # 进度条
        if self.total_cards > 0:
            progress_width = 200
            progress_height = 8
            progress_x = self.screen_width - progress_width - 20
            progress_y = 145
            
            # 背景
            pygame.draw.rect(screen, DexColors.GRAY, (progress_x, progress_y, progress_width, progress_height), border_radius=4)
            
            # 进度
            progress_fill_width = int(progress_width * (self.owned_cards / self.total_cards))
            if progress_fill_width > 0:
                pygame.draw.rect(screen, DexColors.SUCCESS, (progress_x, progress_y, progress_fill_width, progress_height), border_radius=4)
    
    def _draw_card_grid(self, screen: pygame.Surface):
        """绘制卡牌网格（虚拟滚动）"""
        # # 设置裁剪区域，防止卡牌渲染到header区域
        # clip_rect = pygame.Rect(0, self.content_start_y, self.screen_width, 
        #                     self.screen_height - self.content_start_y - self.nav_bar_height)
        # screen.set_clip(clip_rect)
        if not self.card_displays:
            # 空状态
            empty_font = pygame.font.Font(None, 24)
            empty_text = empty_font.render("No se encontraron cartas", True, DexColors.TEXT_MUTED)
            empty_rect = empty_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            screen.blit(empty_text, empty_rect)
            return
        
        # 计算可见范围
        visible_start_row = max(0, int((self.scroll_y - 50) // (self.card_height + self.card_spacing)))
        visible_end_row = min(
            (len(self.card_displays) + self.cards_per_row - 1) // self.cards_per_row,
            int((self.scroll_y + self.content_height) // (self.card_height + self.card_spacing)) + 1
        )
        
        visible_start = visible_start_row * self.cards_per_row
        visible_end = min(len(self.card_displays), (visible_end_row + 1) * self.cards_per_row)
        
        # 绘制可见卡牌
        for i in range(visible_start, visible_end):
            if i >= len(self.card_displays):
                break
            
            card_display = self.card_displays[i]
            
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            
            # 计算位置
            cards_area_width = self.cards_per_row * self.card_width + (self.cards_per_row - 1) * self.card_spacing
            start_x = (self.screen_width - cards_area_width) // 2
            
            card_x = start_x + col * (self.card_width + self.card_spacing)
            card_y = self.content_start_y + row * (self.card_height + self.card_spacing) - self.scroll_y
            
            # 裁剪检查
            if card_y < self.content_height and card_y + self.card_height > self.content_start_y:
                card_display.draw(screen, card_x, card_y)

            screen.set_clip(None)  # 取消裁剪
    
    # def _draw_custom_scrollbar(self, screen: pygame.Surface):
    #     """绘制自定义滚动条指示器"""
    #     # 临时测试 - 绘制一个明显的红色矩形
    #     test_rect = pygame.Rect(self.screen_width - 50, 100, 30, 200)
    #     pygame.draw.rect(screen, (255, 0, 0), test_rect)  # 红色测试矩形
    #     print("绘制滚动条被调用")  # 确认函数被调用
        
    #     if not self.max_scroll > 0:
    #         return

    #     if not self.ui_elements.get('scrollbar') or self.max_scroll <= 0:
    #         return
        
    #     # 半透明滚动条指示器
    #     scrollbar_x = self.screen_width - 20
    #     scrollbar_y = self.content_start_y + 10
    #     scrollbar_height = self.content_height - 40
    #     scrollbar_width = 8
        
    #     # 背景
    #     bg_alpha = int(self.scroll_bar_alpha * 60)
    #     if bg_alpha > 0:
    #         bg_surf = pygame.Surface((scrollbar_width, scrollbar_height), pygame.SRCALPHA)
    #         bg_surf.fill((200, 200, 200, bg_alpha))
    #         screen.blit(bg_surf, (scrollbar_x, scrollbar_y))
        
    #     # 滑块
    #     thumb_alpha = int(self.scroll_bar_alpha * 120)
    #     if thumb_alpha > 0:
    #         visible_content_height = self.content_height - 40
    #         content_height = self._calculate_content_height()
            
    #         if content_height > visible_content_height:
    #             thumb_height = max(20, int(scrollbar_height * visible_content_height / content_height))
    #             thumb_y = scrollbar_y + int(self.scroll_y / self.max_scroll * (scrollbar_height - thumb_height))
                
    #             thumb_surf = pygame.Surface((scrollbar_width, thumb_height), pygame.SRCALPHA)
    #             thumb_surf.fill((100, 100, 100, thumb_alpha))
    #             pygame.draw.rect(thumb_surf, (100, 100, 100, thumb_alpha), 
    #                            (0, 0, scrollbar_width, thumb_height), border_radius=4)
    #             screen.blit(thumb_surf, (scrollbar_x, thumb_y))

    def _draw_custom_scrollbar(self, screen: pygame.Surface):
        """绘制自定义滚动条指示器"""
        if self.max_scroll <= 0:
            return
        
        # 简化的滚动条
        scrollbar_x = self.screen_width - 15
        scrollbar_y = self.content_start_y + 20
        scrollbar_width = 10
        scrollbar_height = self.content_height - 60
        
        # 背景条
        pygame.draw.rect(screen, (200, 200, 200), 
                        (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
        
        # 滑块
        thumb_height = max(20, scrollbar_height // 4)
        thumb_y = scrollbar_y + int(self.scroll_y / self.max_scroll * (scrollbar_height - thumb_height))
        pygame.draw.rect(screen, (100, 100, 100), 
                        (scrollbar_x, thumb_y, scrollbar_width, thumb_height))
    
    def resize(self, new_width: int, new_height: int):
        """调整页面大小"""
        self.screen_width = new_width
        self.screen_height = new_height
        self.content_height = new_height - self.nav_bar_height
        
        # 重新创建UI元素
        self._create_ui_elements()
        
        # 重新应用过滤器
        self._apply_filters()
        
        print(f"📐 DexPage调整尺寸: {new_width}x{new_height}")
    
    def get_page_name(self) -> str:
        """获取页面名称"""
        return "dex"
    
    # def hide_ui_elements(self):
    #     """隐藏所有UI元素"""
    #     for element in self.ui_elements.values():
    #         if element and element.alive():
    #             element.hide()
    #     print("🙈 DexPage UI元素已隐藏")

    # def show_ui_elements(self):
    #     """显示所有UI元素"""
    #     for element in self.ui_elements.values():
    #         if element and element.alive():
    #             element.show()
    #     print("👁️ DexPage UI元素已显示")

    def cleanup(self):
        """清理资源"""
        print("🧹 清理DexPage资源...")
        
        # # 清理UI元素
        # for element in list(self.ui_elements.values()):  # 使用list()避免字典修改错误
        #     if element and element.alive():
        #         element.kill()
        # self.ui_elements.clear()

        # # 🚀 新增：强制刷新UI管理器
        # if hasattr(self, 'ui_manager'):
        #     self.ui_manager.clear_and_reset()  # 如果有这个方法
        #     # 或者使用：
        #     # self.ui_manager.process_events([])  # 强制处理清理事件
        
        # 清理卡牌显示组件
        for card_display in self.card_displays:
            if hasattr(card_display, '_cached_surface') and card_display._cached_surface:
                try:
                    del card_display._cached_surface
                except:
                    pass
        
        self.card_displays = []
        self.filtered_cards = []
        # self.all_cards = []
        
        print("✅ DexPage资源清理完成")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()


# 使用示例和测试代码
if __name__ == "__main__":
    import pygame
    import pygame_gui
    
    # 模拟测试
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("DexPage Test")
    clock = pygame.time.Clock()
    
    ui_manager = pygame_gui.UIManager((1200, 800))
    
    # 模拟数据库管理器
    class MockDatabaseManager:
        def __init__(self):
            self.card_dao = MockCardDAO()
        
        def get_user_cards(self, user_id):
            return [
                {'card_id': 'xy5-1', 'quantity': 2, 'obtained_at': '2024-01-01'},
                {'card_id': 'det1-1', 'quantity': 1, 'obtained_at': '2024-01-02'}
            ]
    
    class MockCardDAO:
        def search_cards(self, limit=10000):
            # 模拟卡牌数据
            cards = []
            for i in range(50):
                card = type('Card', (), {
                    'id': f'test-{i}',
                    'name': f'Test Card {i}',
                    'rarity': ['Common', 'Uncommon', 'Rare'][i % 3],
                    'types': '["Grass"]',
                    'attacks': '[]',
                    'image_path': None
                })()
                cards.append(card)
            return cards
        
        def get_all_rarities(self):
            return ['Common', 'Uncommon', 'Rare', 'Rare Holo']
        
        def get_all_types(self):
            return ['Grass', 'Fire', 'Water', 'Lightning']
    
    # 模拟认证管理器
    class MockAuth:
        def get_user_info(self):
            return {'id': 1, 'username': 'test_user'}
    
    # 替换全局函数
    # global get_auth_manager
    get_auth_manager = lambda: MockAuth()
    
    db_manager = MockDatabaseManager()
    dex_page = DexPage(1200, 800, ui_manager, db_manager, 90)
    
    running = True
    print("🚀 DexPage测试启动")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            ui_manager.process_events(event)
            result = dex_page.handle_event(event)
            if result == "back_to_home":
                print("返回主页")
        
        dex_page.update(dt)
        ui_manager.update(dt)
        
        # 绘制背景
        screen.fill((240, 245, 251))
        
        dex_page.draw(screen)
        pygame.display.flip()
    
    dex_page.cleanup()
    pygame.quit()
    print("✅ DexPage测试完成")