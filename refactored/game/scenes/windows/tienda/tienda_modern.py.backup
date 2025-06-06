"""
现代化商店窗口 - 第1部分
集成数据库管理、样式系统和动画效果
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIPanel, UILabel, UIWindow, UIScrollingContainer
from pygame_gui.core import ObjectID
import math
import time
from typing import Dict, List, Optional, Callable

# 导入管理系统
from game.core.database.database_manager import DatabaseManager
from game.core.cards.collection_manager import CardManager
from game.scenes.styles.theme import Theme
from game.scenes.styles.fonts import font_manager
from game.scenes.animations.animation_manager import AnimationManager
from game.scenes.components.button_component import ModernButton
from .tienda_draw import TiendaDrawMixin

class ModernTiendaWindow(TiendaDrawMixin):
    """
    现代化商店窗口
    采用毛玻璃风格设计，集成数据库和动画系统
    """
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager, db_manager: DatabaseManager, user_id: int = 1):
        """
        初始化现代化商店窗口
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            ui_manager: pygame_gui UI管理器（不再使用，保持兼容性）
            db_manager: 数据库管理器
            user_id: 用户ID，默认为1
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        self.db_manager = db_manager
        self.user_id = user_id  # 添加缺失的user_id属性
        
        # 动画管理器
        self.animation_manager = AnimationManager()
        
        # 窗口尺寸
        self.window_width = min(1000, int(screen_width * 0.9))
        self.window_height = min(700, int(screen_height * 0.9))
        
        # 计算居中位置
        window_x = (screen_width - self.window_width) // 2
        window_y = (screen_height - self.window_height) // 2
        
        # 窗口状态
        self.is_visible = True
        self.selected_item = None
        self.cart_items = []
        self.current_tab = "packs"  # "packs", "items", "special"
        
        # 获取用户经济状态
        self.user_economy = self._get_user_economy()
        
        # 商店配置
        self.shop_config = self._load_shop_config()
        
        # 创建主背景表面
        self.background_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
        # 不创建pygame_gui窗口，完全使用自定义绘制
        self.window = None
        self.window_rect = pygame.Rect(window_x, window_y, self.window_width, self.window_height)
        
        # 创建现代化UI元素
        self.create_modern_ui()
        
        # 回调函数
        self.on_close: Optional[Callable] = None
        self.on_purchase: Optional[Callable] = None
        
        # 开始入场动画
        self.animation_manager.start_fade_in("window_fade")
        
        print(f"🛍️ 创建现代化商店窗口 - 用户金币: {self.user_economy.get('coins', 0)}")
    
    def _get_user_economy(self) -> Dict:
        """获取用户经济状态"""
        try:
            # 使用正确的方法调用
            economy = self.db_manager.get_user_economy(self.user_id)
            
            if not economy:
                # 为新用户创建经济记录
                economy = {
                    'coins': 1000,
                    'gems': 50,
                    'pack_points': 0,
                    'dust': 0
                }
                self.db_manager.update_user_economy(self.user_id, **economy)
                return economy
            
            return economy
        except Exception as e:
            print(f"获取用户经济状态失败: {e}")
            return {'coins': 1000, 'gems': 50, 'pack_points': 0, 'dust': 0}
    
    def _load_shop_config(self) -> Dict:
        """加载商店配置"""
        return {
            'packs': [
                {
                    'id': 'basic_pack',
                    'name': 'Sobre Básico',
                    'description': 'Contiene 5 cartas\ncon posibilidad de raras',
                    'price': 100,
                    'currency': 'coins',
                    'icon': '🎴',
                    'rarity_chances': {'common': 0.7, 'uncommon': 0.25, 'rare': 0.05},
                    'cards_count': 5,
                    'featured': False
                },
                {
                    'id': 'premium_pack',
                    'name': 'Sobre Premium',
                    'description': 'Contiene 5 cartas\ncon rara garantizada',
                    'price': 200,
                    'currency': 'coins',
                    'icon': '✨',
                    'rarity_chances': {'common': 0.5, 'uncommon': 0.35, 'rare': 0.15},
                    'cards_count': 5,
                    'featured': True
                },
                {
                    'id': 'legendary_pack',
                    'name': 'Sobre Legendario',
                    'description': 'Contiene cartas especiales\ny legendarias',
                    'price': 15,
                    'currency': 'gems',
                    'icon': '💎',
                    'rarity_chances': {'rare': 0.6, 'ultra_rare': 0.3, 'legendary': 0.1},
                    'cards_count': 5,
                    'featured': True
                }
            ],
            'items': [
                {
                    'id': 'potion',
                    'name': 'Poción Curativa',
                    'description': 'Restaura 50 HP\na cualquier Pokémon',
                    'price': 50,
                    'currency': 'coins',
                    'icon': '🧪',
                    'effect': 'heal_50'
                },
                {
                    'id': 'super_potion',
                    'name': 'Súper Poción',
                    'description': 'Restaura 100 HP\na cualquier Pokémon',
                    'price': 100,
                    'currency': 'coins',
                    'icon': '💉',
                    'effect': 'heal_100'
                },
                {
                    'id': 'revive',
                    'name': 'Revivir',
                    'description': 'Revive un Pokémon\ncon 50% HP',
                    'price': 150,
                    'currency': 'coins',
                    'icon': '💫',
                    'effect': 'revive_50'
                }
            ],
            'special': [
                {
                    'id': 'luck_charm',
                    'name': 'Amuleto de Suerte',
                    'description': 'Aumenta probabilidad\nde cartas raras por 24h',
                    'price': 10,
                    'currency': 'gems',
                    'icon': '🍀',
                    'effect': 'luck_boost_24h'
                },
                {
                    'id': 'energy_crystal',
                    'name': 'Cristal de Energía',
                    'description': 'Energía extra para\nataques especiales',
                    'price': 8,
                    'currency': 'gems',
                    'icon': '🔮',
                    'effect': 'energy_boost'
                }
            ]
        }
    
    def create_modern_ui(self):
        """创建现代化UI元素 - 完全自定义版本"""
        # 设置基本属性供TiendaDrawMixin使用
        self.setup_tienda_properties()
        
        print("🎨 现代化UI元素已创建（完全自定义）")
    
    def setup_tienda_properties(self):
        """设置商店所需的属性以兼容TiendaDrawMixin"""
        # 设置窗口矩形（相对于屏幕）
        # self.window_rect 已在 __init__ 中设置
        
        # 设置缩放因子
        self.scale_factor = self.screen_height / 1080
        
        # 设置动画时间
        self.animation_time = 0
        
        # 设置用户金币
        self.user_coins = self.user_economy.get('coins', 1000)
        
        # 设置分类数据
        self.categories = [
            {'name': 'Sobres', 'icon': '🎴'},
            {'name': 'Objetos', 'icon': '🧪'},
            {'name': 'Especiales', 'icon': '✨'}
        ]
        
        # 设置当前选中的分类
        tab_mapping = {'packs': 0, 'items': 1, 'special': 2}
        self.selected_category = tab_mapping.get(self.current_tab, 0)
        
        # 设置商品数据
        self.setup_shop_data()
        
        # 计算布局矩形
        self.calculate_layout_rects()
        
        # 初始化动画状态
        self.show_success_animation = False
        self.show_error_animation = False
        self.success_animation_timer = 0
        self.error_animation_timer = 0
        self.error_message = ""
        
        # 初始化粒子系统
        self.particles = []
        
        print(f"📐 布局计算完成 - 窗口: {self.window_rect}")
        print(f"🏪 商品数据 - 卡包: {len(self.card_packs)}, 道具: {len(self.items)}, 特殊: {len(self.special_items)}")
    
    def setup_shop_data(self):
        """设置商品数据"""
        # 卡包数据
        self.card_packs = self.shop_config.get('packs', [])
        
        # 道具数据
        self.items = self.shop_config.get('items', [])
        
        # 特殊商品数据
        self.special_items = self.shop_config.get('special', [])
        
        # 为每个商品添加图片占位符（如果没有的话）
        for pack in self.card_packs:
            if 'image' not in pack:
                pack['image'] = None  # TiendaDrawMixin会处理占位符
        
        for item in self.items:
            if 'rarity' not in item:
                item['rarity'] = 'common'  # 默认稀有度
        
        for special in self.special_items:
            if 'original_price' not in special:
                special['original_price'] = special.get('price', 100) + 50  # 模拟折扣
    
    def calculate_layout_rects(self):
        """计算所有布局矩形"""
        # 头部区域
        self.header_rect = pygame.Rect(
            self.window_rect.x + 20, 
            self.window_rect.y + 20, 
            self.window_rect.width - 40, 
            80
        )
        
        # 关闭按钮
        close_size = 40
        self.close_button_rect = pygame.Rect(
            self.window_rect.right - close_size - 20,
            self.window_rect.y + 20,
            close_size, close_size
        )
        
        # 侧边栏（分类）
        sidebar_width = 180
        self.sidebar_rect = pygame.Rect(
            self.window_rect.x + 20,
            self.header_rect.bottom + 20,
            sidebar_width,
            self.window_rect.height - self.header_rect.height - 120
        )
        
        # 计算分类按钮
        self.category_buttons = []
        button_height = 60
        button_spacing = 15
        
        for i in range(len(self.categories)):
            button_y = self.sidebar_rect.y + 60 + i * (button_height + button_spacing)
            button_rect = pygame.Rect(
                self.sidebar_rect.x + 10,
                button_y,
                self.sidebar_rect.width - 20,
                button_height
            )
            self.category_buttons.append(button_rect)
        
        # 主内容区域
        content_x = self.sidebar_rect.right + 20
        self.content_rect = pygame.Rect(
            content_x,
            self.sidebar_rect.y,
            self.window_rect.right - content_x - 20,
            self.sidebar_rect.height - 80
        )
        
        # 状态栏
        self.status_bar_rect = pygame.Rect(
            self.sidebar_rect.x,
            self.window_rect.bottom - 80,
            self.window_rect.width - 40,
            60
        )
        
        # 计算商品网格
        self.calculate_shop_grids()
    
    def calculate_shop_grids(self):
        """计算商品网格布局"""
        item_width = 180
        item_height = 220
        spacing = 15
        
        # 使用 TiendaDrawMixin 的布局计算方法
        
        # 卡包网格
        self.pack_grid_rects = self.calculate_grid_layout(
            self.content_rect, len(self.card_packs), 
            item_width, item_height, spacing
        )
        
        # 道具网格
        self.item_grid_rects = self.calculate_grid_layout(
            self.content_rect, len(self.items),
            item_width, item_height, spacing
        )
        
        # 特殊商品网格
        self.special_grid_rects = self.calculate_grid_layout(
            self.content_rect, len(self.special_items),
            item_width, item_height, spacing
        )
    
    def update_mouse_interactions(self, mouse_pos):
        """更新鼠标交互状态"""
        # 更新关闭按钮悬停
        self.close_button_hovered = self.close_button_rect.collidepoint(mouse_pos)
        
        # 更新分类悬停
        self.hovered_category = None
        for i, button_rect in enumerate(self.category_buttons):
            if button_rect.collidepoint(mouse_pos):
                self.hovered_category = i
                break
        
        # 更新商品悬停
        self.hovered_pack = None
        self.hovered_item = None
        self.hovered_special = None
        
        if self.selected_category == 0:  # 卡包
            for i, rect in enumerate(self.pack_grid_rects):
                if rect.collidepoint(mouse_pos):
                    self.hovered_pack = i
                    break
        elif self.selected_category == 1:  # 道具
            for i, rect in enumerate(self.item_grid_rects):
                if rect.collidepoint(mouse_pos):
                    self.hovered_item = i
                    break
        elif self.selected_category == 2:  # 特殊
            for i, rect in enumerate(self.special_grid_rects):
                if rect.collidepoint(mouse_pos):
                    self.hovered_special = i
                    break
    
    # 占位符方法（保持兼容性）
    def create_header(self):
        """创建顶部标题区域 - 占位符方法"""
        pass
    
    def create_economy_display(self):
        """创建经济状态显示 - 占位符方法"""
        pass
    
    def create_tabs(self):
        """创建标签页 - 占位符方法"""
        pass
    
    def create_shop_grid(self):
        """创建商品展示网格 - 占位符方法"""
        pass
    
    def create_footer(self):
        """创建底部操作区 - 占位符方法"""
        pass
    
    def create_modern_buttons(self):
        """创建现代化按钮 - 占位符方法"""
        pass
    
    def update_visible_items(self):
        """更新可见商品列表 - 占位符方法"""
        pass

    def handle_event(self, event):
        """处理事件 - 与TiendaDrawMixin兼容"""
        if not self.is_visible:
            return None
        
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 检查关闭按钮点击
            if hasattr(self, 'close_button_rect') and self.close_button_rect.collidepoint(mouse_pos):
                self.close()
                return "close"
            
            # 检查分类点击
            if hasattr(self, 'category_buttons'):
                for i, button_rect in enumerate(self.category_buttons):
                    if button_rect.collidepoint(mouse_pos):
                        self.switch_to_category(i)
                        return f"category_{i}"
            
            # 检查商品点击
            if self.selected_category == 0:  # 卡包
                if hasattr(self, 'pack_grid_rects'):
                    for i, rect in enumerate(self.pack_grid_rects):
                        if i < len(self.card_packs) and rect.collidepoint(mouse_pos):
                            return self.handle_pack_click(i)
            
            elif self.selected_category == 1:  # 道具
                if hasattr(self, 'item_grid_rects'):
                    for i, rect in enumerate(self.item_grid_rects):
                        if i < len(self.items) and rect.collidepoint(mouse_pos):
                            return self.handle_item_click(i)
            
            elif self.selected_category == 2:  # 特殊商品
                if hasattr(self, 'special_grid_rects'):
                    for i, rect in enumerate(self.special_grid_rects):
                        if i < len(self.special_items) and rect.collidepoint(mouse_pos):
                            return self.handle_special_click(i)
            
            # 检查刷新按钮
            if hasattr(self, 'status_bar_rect'):
                refresh_button_size = 35
                refresh_button_rect = pygame.Rect(
                    self.status_bar_rect.right - refresh_button_size - 15,
                    self.status_bar_rect.centery - refresh_button_size // 2,
                    refresh_button_size,
                    refresh_button_size
                )
                if refresh_button_rect.collidepoint(mouse_pos):
                    self.refresh_shop()
                    return "refresh"
        
        return None
    
    def switch_to_category(self, category_index: int):
        """切换到指定分类"""
        if category_index != self.selected_category:
            self.selected_category = category_index
            
            # 更新当前标签
            tab_mapping = {0: 'packs', 1: 'items', 2: 'special'}
            self.current_tab = tab_mapping.get(category_index, 'packs')
            
            print(f"🔄 切换到分类: {category_index} ({self.current_tab})")
    
    def handle_pack_click(self, pack_index: int):
        """处理卡包点击"""
        if pack_index < len(self.card_packs):
            pack_data = self.card_packs[pack_index]
            return self.attempt_purchase(pack_data, 'pack', pack_index)
        return None
    
    def handle_item_click(self, item_index: int):
        """处理道具点击"""
        if item_index < len(self.items):
            item_data = self.items[item_index]
            return self.attempt_purchase(item_data, 'item', item_index)
        return None
    
    def handle_special_click(self, special_index: int):
        """处理特殊商品点击"""
        if special_index < len(self.special_items):
            special_data = self.special_items[special_index]
            return self.attempt_purchase(special_data, 'special', special_index)
        return None
    
    def attempt_purchase(self, item_data: Dict, item_type: str, item_index: int):
        """尝试购买商品"""
        currency = item_data.get('currency', 'coins')
        price = item_data.get('price', 0)
        
        # 检查货币是否足够
        if self.user_economy.get(currency, 0) < price:
            print(f"❌ 货币不足: 需要 {price} {currency}")
            self.show_error_message("Monedas insuficientes")
            return "insufficient_funds"
        
        # 执行购买
        try:
            # 扣除货币
            self.user_economy[currency] -= price
            success = self.db_manager.update_user_economy(self.user_id, **{currency: self.user_economy[currency]})
            
            if not success:
                # 如果更新失败，回滚本地状态
                self.user_economy[currency] += price
                print("❌ 更新用户经济状态失败")
                self.show_error_message("Error al procesar la compra")
                return "update_error"
            
            # 处理购买的物品
            if item_type == 'pack':
                self._handle_pack_purchase(item_data)
            else:
                self._handle_item_purchase(item_data)
            
            # 更新用户金币显示
            self.user_coins = self.user_economy.get('coins', 0)
            
            # 显示成功消息
            self.show_success_message(f"¡{item_data['name']} comprado!")
            
            # 调用回调
            if self.on_purchase:
                self.on_purchase(item_data)
            
            print(f"✅ 购买成功: {item_data['name']} - 花费 {price} {currency}")
            return "purchase_success"
            
        except Exception as e:
            print(f"❌ 购买失败: {e}")
            self.show_error_message("Error en la compra")
            return "purchase_error"
    
    def show_success_message(self, message: str):
        """显示成功消息"""
        self.show_success_animation = True
        self.success_animation_timer = 3.0  # 3秒
        print(f"✅ {message}")
    
    def show_error_message(self, message: str):
        """显示错误消息"""
        self.show_error_animation = True
        self.error_animation_timer = 3.0  # 3秒
        self.error_message = message
        print(f"❌ {message}")
    
    # 兼容性方法
    def switch_tab(self, tab_id: str):
        """切换标签页 - 保持兼容性"""
        tab_mapping = {'packs': 0, 'items': 1, 'special': 2}
        category_index = tab_mapping.get(tab_id, 0)
        self.switch_to_category(category_index)
    
    def select_item(self, item):
        """选择商品 - 保持兼容性"""
        # 这个方法保留用于兼容性，但实际购买通过点击处理
        print(f"📦 商品信息: {item}")
    
    def purchase_selected_item(self):
        """购买选中的商品 - 保持兼容性"""
        # 在新系统中，购买直接通过点击处理
        return "no_selection"
    
    def _handle_pack_purchase(self, pack_data):
        """处理卡包购买"""
        try:
            # 使用正确的方法获取CardManager
            card_manager = self.db_manager.card_dao  # 或者使用其他正确的获取方式
            if not card_manager:
                print("❌ 无法获取卡牌管理器")
                return
            
            # 简单的卡包开启逻辑
            rarity_chances = pack_data['rarity_chances']
            cards_count = pack_data['cards_count']
            
            # 这里应该实现实际的卡包开启逻辑
            print(f"🎴 开启卡包: {pack_data['name']}")
            print(f"   包含 {cards_count} 张卡牌")
            
        except Exception as e:
            print(f"❌ 处理卡包购买失败: {e}")
    
    def _handle_item_purchase(self, item_data):
        """处理道具购买"""
        try:
            # 这里可以添加道具到用户背包的逻辑
            print(f"🧪 获得道具: {item_data['name']}")
            
        except Exception as e:
            print(f"❌ 处理道具购买失败: {e}")
    
    def close(self):
        """关闭窗口"""
        self.is_visible = False
        # 不需要kill pygame_gui窗口，因为我们没有创建
        if self.on_close:
            self.on_close()
    
    def refresh_shop(self):
        """刷新商店"""
        # 重新加载用户经济状态
        self.user_economy = self._get_user_economy()
        self.user_coins = self.user_economy.get('coins', 0)
        
        # 可以在这里添加其他刷新逻辑，比如随机折扣等
        
        print("🔄 商店已刷新")
    
    def _update_economy_display(self):
        """更新经济状态显示 - 保持兼容性"""
        # 更新用户金币
        self.user_coins = self.user_economy.get('coins', 0)
        print(f"💰 用户金币更新: {self.user_coins}")
    
    def update(self, dt: float):
        """更新窗口状态"""
        if not self.is_visible:
            return
        
        # 更新动画时间
        if hasattr(self, 'animation_time'):
            self.animation_time += dt
        else:
            self.animation_time = 0
        
        # 更新动画管理器
        if hasattr(self, 'animation_manager'):
            callbacks = self.animation_manager.update(dt)
            
            # 执行完成的动画回调
            for callback in callbacks:
                if callback:
                    callback()
        
        # 更新成功动画计时器
        if hasattr(self, 'success_animation_timer') and self.success_animation_timer > 0:
            self.success_animation_timer -= dt
            if self.success_animation_timer <= 0:
                self.show_success_animation = False
        
        # 更新错误动画计时器
        if hasattr(self, 'error_animation_timer') and self.error_animation_timer > 0:
            self.error_animation_timer -= dt
            if self.error_animation_timer <= 0:
                self.show_error_animation = False

        # 更新粒子系统
        if hasattr(self, 'particles') and self.particles:
            for particle in self.particles[:]:
                particle['life'] -= dt * 60  # 假设60FPS
                if particle['life'] <= 0:
                    self.particles.remove(particle)
    
    def draw(self, screen: pygame.Surface) -> None:
        """绘制窗口 - 使用TiendaDrawMixin的方法"""
        if not self.is_visible:
            return
        
        try:
            # 确保属性是最新的
            self.user_coins = self.user_economy.get('coins', 1000)
            
            # 更新动画时间
            current_time = pygame.time.get_ticks() / 1000.0
            self.animation_time = current_time
            
            # 更新鼠标交互（如果需要）
            mouse_pos = pygame.mouse.get_pos()
            self.update_mouse_interactions(mouse_pos)
            
            # 使用TiendaDrawMixin的主绘制方法
            self.draw_shop_effects(screen)
            
            # 绘制调试信息（可选）
            if hasattr(self, '_debug_mode') and self._debug_mode:
                self.draw_debug_info(screen)
            
        except Exception as e:
            print(f"绘制商店窗口时出错: {e}")
            import traceback
            traceback.print_exc()
            # 绘制错误信息
            self.draw_error_fallback(screen, str(e))
    
    def draw_error_fallback(self, screen: pygame.Surface, error_msg: str):
        """绘制错误回退界面"""
        # 绘制半透明背景
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        
        # 绘制错误窗口
        error_rect = pygame.Rect(
            self.window_rect.x, self.window_rect.y,
            self.window_rect.width, self.window_rect.height
        )
        
        pygame.draw.rect(screen, (50, 50, 50), error_rect, border_radius=20)
        pygame.draw.rect(screen, (200, 100, 100), error_rect, 3, border_radius=20)
        
        # 错误文字
        font = pygame.font.Font(None, 36)
        title = font.render("Error en la Tienda", True, (255, 100, 100))
        title_rect = title.get_rect(center=(error_rect.centerx, error_rect.y + 60))
        screen.blit(title, title_rect)
        
        # 错误详情
        small_font = pygame.font.Font(None, 24)
        error_lines = [
            "Ha ocurrido un error al cargar la tienda.",
            f"Detalles: {error_msg[:50]}...",
            "",
            "Presiona ESC para cerrar"
        ]
        
        y_offset = title_rect.bottom + 30
        for line in error_lines:
            if line:
                text = small_font.render(line, True, (255, 255, 255))
                text_rect = text.get_rect(center=(error_rect.centerx, y_offset))
                screen.blit(text, text_rect)
            y_offset += 30
    
    def draw_debug_info(self, screen: pygame.Surface):
        """绘制调试信息"""
        debug_font = pygame.font.Font(None, 20)
        debug_info = [
            f"FPS: {pygame.time.Clock().get_fps():.1f}",
            f"分类: {self.selected_category} ({self.current_tab})",
            f"金币: {self.user_coins}",
            f"卡包: {len(self.card_packs)}",
            f"道具: {len(self.items)}",
            f"特殊: {len(self.special_items)}",
            f"窗口: {self.window_rect}",
        ]
        
        y_offset = 10
        for info in debug_info:
            text = debug_font.render(info, True, (255, 255, 0))
            screen.blit(text, (10, y_offset))
            y_offset += 25
    
    def enable_debug_mode(self):
        """启用调试模式"""
        self._debug_mode = True
        print("🐛 调试模式已启用")
    
    def disable_debug_mode(self):
        """禁用调试模式"""
        self._debug_mode = False
        print("🐛 调试模式已禁用")
    
    def get_shop_status(self) -> Dict:
        """获取商店状态信息"""
        return {
            'is_visible': self.is_visible,
            'current_tab': self.current_tab,
            'selected_category': self.selected_category,
            'user_coins': self.user_coins,
            'user_economy': self.user_economy.copy(),
            'shop_items_count': {
                'packs': len(self.card_packs),
                'items': len(self.items),
                'special': len(self.special_items)
            }
        }
    
    def set_callback(self, callback_type: str, callback_func: Callable):
        """设置回调函数"""
        if callback_type == 'close':
            self.on_close = callback_func
        elif callback_type == 'purchase':
            self.on_purchase = callback_func
        else:
            print(f"⚠️ 未知的回调类型: {callback_type}")
    
    def force_refresh_economy(self):
        """强制刷新经济状态"""
        self.user_economy = self._get_user_economy()
        self.user_coins = self.user_economy.get('coins', 0)
        print(f"💰 强制刷新经济状态 - 金币: {self.user_coins}")
    
    def add_test_currency(self, currency_type: str, amount: int):
        """添加测试货币（仅用于测试）"""
        if currency_type in self.user_economy:
            self.user_economy[currency_type] += amount
            if currency_type == 'coins':
                self.user_coins = self.user_economy['coins']
            print(f"🧪 测试添加 {amount} {currency_type}")
        else:
            print(f"❌ 未知的货币类型: {currency_type}")
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"ModernTiendaWindow(visible={self.is_visible}, tab={self.current_tab}, coins={self.user_coins})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"ModernTiendaWindow("
                f"screen={self.screen_width}x{self.screen_height}, "
                f"user_id={self.user_id}, "
                f"visible={self.is_visible}, "
                f"tab={self.current_tab}, "
                f"economy={self.user_economy})")


# 文件结束标记
if __name__ == "__main__":
    print("ModernTiendaWindow 类定义完成")
    print("使用方法:")
    print("shop = ModernTiendaWindow(screen_width, screen_height, ui_manager, db_manager, user_id)")
    print("在游戏循环中调用: shop.update(dt), shop.draw(screen), shop.handle_event(event)")