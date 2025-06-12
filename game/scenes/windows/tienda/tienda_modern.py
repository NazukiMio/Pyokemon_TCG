"""
重构后的商店窗口 - 使用ThemedUIWindow实现完美主题化
移除复杂的自绘制，使用主题化窗口组件
"""

import pygame
import pygame_gui
import os
from pygame_gui.elements import (
    UIButton, UIPanel, UILabel, UIScrollingContainer, 
    UISelectionList, UIHorizontalSlider
)
from pygame_gui.core import ObjectID
from typing import Dict, List, Optional, Callable

# 导入主题化窗口组件
from game.scenes.windows.tienda.themed_window import ThemedUIWindow, ShopWindow

# 导入管理系统
from game.core.database.database_manager import DatabaseManager
# from game.scenes.styles.theme import Theme
# from game.scenes.styles.fonts import font_manager


class ModernTiendaWindow:
    """
    商店窗口 - 使用ThemedUIWindow实现完美主题化
    保持原有接口兼容性，添加美观的主题样式
    """
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager, 
                 db_manager: DatabaseManager, user_id: int = 1):
        """
        初始化商店窗口
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            ui_manager: pygame_gui UI管理器
            db_manager: 数据库管理器
            user_id: 用户ID，默认为1
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        self.db_manager = db_manager
        self.user_id = user_id
        
        # 🎨 先加载商店主题（在创建窗口前加载）
        self.load_shop_theme()

        # 窗口尺寸
        self.window_width = min(900, int(screen_width * 0.85))
        self.window_height = min(650, int(screen_height * 0.85))
        
        # 计算居中位置
        window_x = (screen_width - self.window_width) // 2
        window_y = (screen_height - self.window_height) // 2
        
        # 窗口状态
        self.is_visible = True
        self.current_tab = "packs"  # "packs", "items", "special"
        self.selected_category = 0
        
        # 获取用户经济状态
        self.user_economy = self._get_user_economy()
        self.user_coins = self.user_economy.get('coins', 1000)
        
        # 商店配置
        self.shop_config = self._load_shop_config()
        
        # UI元素容器
        self.ui_elements = {}
        self.category_buttons = []
        self.item_buttons = []
        
        # 回调函数
        self.on_close: Optional[Callable] = None
        self.on_purchase: Optional[Callable] = None
        
        print("🏗️ 创建主题化商店窗口...")
        
        # ✨ 使用ThemedUIWindow创建主窗口，自动应用主题样式
        self.window = ShopWindow(
            rect=pygame.Rect(window_x, window_y, self.window_width, self.window_height),
            manager=ui_manager,
            window_display_title="💫 Tienda Pokémon",
            resizable=False
        )
        
        # 🎯 调试：查看主题应用情况
        self.window.debug_theme_info()

        # 创建UI元素
        self.create_ui_elements()
        
        # 初始化显示
        self.update_shop_display()
        
        print(f"✅ 主题化商店窗口创建完成 - 用户金币: {self.user_coins}")
    
    def load_shop_theme(self):
        """加载商店主题"""
        try:
            theme_path = os.path.join("game", "scenes", "windows", "tienda", "tienda_theme.json")
            if os.path.exists(theme_path):
                print(f"🎨 加载主题文件: {theme_path}")
                self.ui_manager.get_theme().load_theme(theme_path)
                print("✅ 商店主题加载成功")
                
                # 调试：打印加载的主题数据
                try:
                    theme_dict = self.ui_manager.get_theme().ui_element_fonts_info
                    shop_themes = [key for key in theme_dict.keys() if 'shop' in str(key).lower()]
                    print(f"🔍 商店相关主题样式: {shop_themes}")
                except:
                    print("🔍 主题数据结构不同，跳过详细检查")
                
            else:
                print(f"⚠️ 主题文件不存在: {theme_path}")
                print("🔧 将使用默认样式")
        except Exception as e:
            print(f"❌ 加载商店主题失败: {e}")
            import traceback
            traceback.print_exc()

    def _get_user_economy(self) -> Dict:
        """获取用户经济状态"""
        try:
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
                    'description': 'Contiene 5 cartas con posibilidad de raras',
                    'price': 100,
                    'currency': 'coins',
                    'icon': '🎴',
                    'cards_count': 5
                },
                {
                    'id': 'premium_pack',
                    'name': 'Sobre Premium',
                    'description': 'Contiene 5 cartas con rara garantizada',
                    'price': 200,
                    'currency': 'coins',
                    'icon': '✨',
                    'cards_count': 5
                },
                {
                    'id': 'legendary_pack',
                    'name': 'Sobre Legendario',
                    'description': 'Contiene cartas especiales y legendarias',
                    'price': 15,
                    'currency': 'gems',
                    'icon': '💎',
                    'cards_count': 5
                }
            ],
            'items': [
                {
                    'id': 'potion',
                    'name': 'Poción Curativa',
                    'description': 'Restaura 50 HP a cualquier Pokémon',
                    'price': 50,
                    'currency': 'coins',
                    'icon': '🧪'
                },
                {
                    'id': 'super_potion',
                    'name': 'Súper Poción',
                    'description': 'Restaura 100 HP a cualquier Pokémon',
                    'price': 100,
                    'currency': 'coins',
                    'icon': '💉'
                },
                {
                    'id': 'revive',
                    'name': 'Revivir',
                    'description': 'Revive un Pokémon con 50% HP',
                    'price': 150,
                    'currency': 'coins',
                    'icon': '💫'
                }
            ],
            'special': [
                {
                    'id': 'luck_charm',
                    'name': 'Amuleto de Suerte',
                    'description': 'Aumenta probabilidad de cartas raras por 24h',
                    'price': 10,
                    'currency': 'gems',
                    'icon': '🍀'
                },
                {
                    'id': 'energy_crystal',
                    'name': 'Cristal de Energía',
                    'description': 'Energía extra para ataques especiales',
                    'price': 8,
                    'currency': 'gems',
                    'icon': '🔮'
                }
            ]
        }
    
    def create_ui_elements(self):
        """创建所有UI元素"""
        print("🎨 创建主题化UI元素...")
        
        # 创建主要容器
        container_rect = pygame.Rect(0, 0, self.window_width - 40, self.window_height - 80)
        self.main_container = UIPanel(
            relative_rect=container_rect,
            starting_height=1,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID(class_id="@shop_main_container", object_id="#shop_main_container")
        )
        
        # 创建顶部经济状态显示
        self.create_economy_display()
        
        # 创建分类标签
        self.create_category_tabs()
        
        # 创建商品展示区域
        self.create_items_display()
        
        # 创建底部按钮
        self.create_bottom_buttons()
        
        print("✅ UI元素创建完成")
    
    def create_economy_display(self):
        """创建经济状态显示"""
        # 💰 金币显示 - 使用主题化样式
        self.coins_label = UILabel(
            relative_rect=pygame.Rect(20, 10, 200, 30),
            text=f"💰 {self.user_coins:,} monedas",
            manager=self.ui_manager,
            container=self.main_container,
            object_id=ObjectID(class_id="@coins_label", object_id="#coins_label")
        )
        
        # 💎 宝石显示 - 使用主题化样式
        gems = self.user_economy.get('gems', 0)
        self.gems_label = UILabel(
            relative_rect=pygame.Rect(230, 10, 150, 30),
            text=f"💎 {gems:,} gemas",
            manager=self.ui_manager,
            container=self.main_container,
            object_id=ObjectID(class_id="@gems_label", object_id="#gems_label")
        )
        
        self.ui_elements['coins_label'] = self.coins_label
        self.ui_elements['gems_label'] = self.gems_label
    
    def create_category_tabs(self):
        """创建分类标签"""
        tab_width = 120
        tab_height = 40
        tab_y = 50
        
        categories = [
            ('packs', '🎴 Sobres'),
            ('items', '🌡️ Objetos'),
            ('special', '✨ Especiales')
        ]
        
        for i, (tab_id, tab_text) in enumerate(categories):
            x = 20 + i * (tab_width + 10)
            
            # 🎯 分类标签使用主题化样式
            button = UIButton(
                relative_rect=pygame.Rect(x, tab_y, tab_width, tab_height),
                text=tab_text,
                manager=self.ui_manager,
                container=self.main_container,
                object_id=ObjectID(class_id="@category_tab", object_id=f"#{tab_id}_tab")
            )
            
            self.category_buttons.append(button)
            self.ui_elements[f'{tab_id}_tab'] = button
    
    def create_items_display(self):
        """创建商品展示区域"""
        # 📦 滚动容器 - 使用主题化样式
        container_rect = pygame.Rect(20, 100, self.window_width - 80, self.window_height - 220)
        
        self.items_container = UIScrollingContainer(
            relative_rect=container_rect,
            manager=self.ui_manager,
            container=self.main_container,
            object_id=ObjectID(class_id="@items_container", object_id="#items_container")
        )
        
        self.ui_elements['items_container'] = self.items_container
    
    def create_bottom_buttons(self):
        """创建底部按钮"""
        button_y = self.window_height - 140
        
        # 🔄 刷新按钮 - 使用主题化样式
        self.refresh_button = UIButton(
            relative_rect=pygame.Rect(20, button_y, 100, 35),
            text="🔄 Actualizar",
            manager=self.ui_manager,
            container=self.main_container,
            object_id=ObjectID(class_id="@refresh_button", object_id="#refresh_button")
        )
        
        # ❌ 关闭按钮 - 使用主题化样式
        self.close_button = UIButton(
            relative_rect=pygame.Rect(self.window_width - 140, button_y, 100, 35),
            text="❌ Cerrar",
            manager=self.ui_manager,
            container=self.main_container,
            object_id=ObjectID(class_id="@close_button", object_id="#close_button")
        )
        
        self.ui_elements['refresh_button'] = self.refresh_button
        self.ui_elements['close_button'] = self.close_button
    
    def update_shop_display(self):
        """更新商品显示"""
        # 清除现有的商品按钮
        for button in self.item_buttons:
            button.kill()
        self.item_buttons.clear()
        
        # 获取当前分类的商品
        items = self.shop_config.get(self.current_tab, [])
        
        # 创建商品按钮
        self.create_item_buttons(items)
        
        # 更新分类标签样式
        self.update_tab_styles()
    
    def create_item_buttons(self, items: List[Dict]):
        """创建商品按钮"""
        button_width = 250
        button_height = 120
        buttons_per_row = 3
        margin = 20
        
        for i, item in enumerate(items):
            row = i // buttons_per_row
            col = i % buttons_per_row
            
            x = col * (button_width + margin)
            y = row * (button_height + margin)
            
            # 🎁 创建商品面板 - 使用主题化样式
            item_panel = UIPanel(
                relative_rect=pygame.Rect(x, y, button_width, button_height),
                starting_height=1,
                manager=self.ui_manager,
                container=self.items_container,
                object_id=ObjectID(class_id="@item_panel", object_id=f"#item_panel_{item['id']}")
            )
            
            # 🏷️ 商品图标和名称
            icon_text = f"{item.get('icon', '📦')} {item['name']}"
            name_label = UILabel(
                relative_rect=pygame.Rect(10, 10, button_width - 20, 25),
                text=icon_text,
                manager=self.ui_manager,
                container=item_panel,
                object_id=ObjectID(class_id="@item_name", object_id=f"#item_name_{item['id']}")
            )
            
            # 📝 商品描述
            desc_label = UILabel(
                relative_rect=pygame.Rect(10, 35, button_width - 20, 60),
                text=item['description'],
                manager=self.ui_manager,
                container=item_panel,
                object_id=ObjectID(class_id="@item_description", object_id=f"#item_desc_{item['id']}")
            )
            
            # 🛒 价格和购买按钮
            currency_symbol = "💰" if item['currency'] == 'coins' else "💎"
            price_text = f"{currency_symbol} {item['price']}"
            
            buy_button = UIButton(
                relative_rect=pygame.Rect(10, button_height - 30, button_width - 20, 25),
                text=f"Comprar - {price_text}",
                manager=self.ui_manager,
                container=item_panel,
                object_id=ObjectID(class_id="@buy_button", object_id=f"#buy_{item['id']}")
            )
            
            # 保存引用
            self.item_buttons.extend([item_panel, name_label, desc_label, buy_button])
            self.ui_elements[f"buy_{item['id']}"] = buy_button
    
    def update_tab_styles(self):
        """更新标签样式"""
        # 通过修改button的文本来表示选中状态
        categories = ['packs', 'items', 'special']
        tab_texts = ['🎴 Sobres', '🧪 Objetos', '✨ Especiales']
        
        for i, (tab_id, original_text) in enumerate(zip(categories, tab_texts)):
            button = self.ui_elements.get(f'{tab_id}_tab')
            if button:
                if i == self.selected_category:
                    button.set_text(f"▶ {original_text}")
                else:
                    button.set_text(original_text)
    
    def handle_event(self, event):
        """处理事件"""
        if not self.is_visible:
            return None
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            button_id = event.ui_element.object_ids[-1] if event.ui_element.object_ids else None
            if not button_id:
                return None
            
            # 处理分类标签点击
            if button_id.endswith('_tab'):
                tab_name = button_id.replace('#', '').replace('_tab', '')
                return self.switch_tab(tab_name)
            
            # 处理购买按钮点击
            elif button_id.startswith('#buy_'):
                item_id = button_id.replace('#buy_', '')
                return self.handle_purchase_click(item_id)
            
            # 处理其他按钮
            elif button_id == '#refresh_button':
                self.refresh_shop()
                return "refresh"
            
            elif button_id == '#close_button':
                self.close()
                return "close"
        
        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self.close()
                return "close"
        
        return None
    
    def switch_tab(self, tab_name: str):
        """切换标签页"""
        if tab_name != self.current_tab:
            self.current_tab = tab_name
            
            # 更新选中的分类
            tab_mapping = {'packs': 0, 'items': 1, 'special': 2}
            self.selected_category = tab_mapping.get(tab_name, 0)
            
            # 更新显示
            self.update_shop_display()
            
            print(f"🔄 切换到分类: {tab_name}")
            return f"category_{tab_name}"
        
        return None
    
    def handle_purchase_click(self, item_id: str):
        """处理购买点击"""
        # 在当前分类中查找商品
        items = self.shop_config.get(self.current_tab, [])
        
        for item in items:
            if item['id'] == item_id:
                return self.attempt_purchase(item)
        
        print(f"❌ 未找到商品: {item_id}")
        return "item_not_found"
    
    def attempt_purchase(self, item_data: Dict):
        """尝试购买商品"""
        currency = item_data.get('currency', 'coins')
        price = item_data.get('price', 0)
        
        # 检查货币是否足够
        if self.user_economy.get(currency, 0) < price:
            print(f"❌ 货币不足: 需要 {price} {currency}")
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
                return "update_error"
            
            # 更新显示
            self.update_economy_display()
            
            # 调用回调
            if self.on_purchase:
                self.on_purchase(item_data)
            
            print(f"✅ 购买成功: {item_data['name']} - 花费 {price} {currency}")
            return "purchase_success"
            
        except Exception as e:
            print(f"❌ 购买失败: {e}")
            return "purchase_error"
    
    def update_economy_display(self):
        """更新经济状态显示"""
        self.user_coins = self.user_economy.get('coins', 0)
        gems = self.user_economy.get('gems', 0)
        
        if self.coins_label:
            self.coins_label.set_text(f"💰 {self.user_coins:,} monedas")
        
        if self.gems_label:
            self.gems_label.set_text(f"💎 {gems:,} gemas")
    
    def refresh_shop(self):
        """刷新商店"""
        # 重新加载用户经济状态
        self.user_economy = self._get_user_economy()
        self.update_economy_display()
        
        print("🔄 商店已刷新")
    
    def close(self):
        """关闭窗口"""
        self.is_visible = False
        if self.window:
            try:
                self.window.kill()
            except pygame.error:
                # pygame已经关闭时忽略错误
                pass
        
        on_close_callback = self.on_close
        self.on_close = None

        if on_close_callback:
            on_close_callback()
        
        print("🛍️ 商店窗口已关闭")
    
    def update(self, dt: float):
        """更新窗口状态"""
        if not self.is_visible:
            return
        
        # pygame_gui会自动处理UI更新，这里只需要处理业务逻辑
        pass
    
    def draw(self, screen: pygame.Surface):
        """绘制窗口"""
        if not self.is_visible:
            return
        
        # pygame_gui会自动绘制所有UI元素
        # 这个方法保留是为了兼容性
        pass
    
    # ========== 兼容性方法 ==========
    
    def switch_to_category(self, category_index: int):
        """切换到指定分类 - 兼容性方法"""
        tab_mapping = {0: 'packs', 1: 'items', 2: 'special'}
        tab_name = tab_mapping.get(category_index, 'packs')
        return self.switch_tab(tab_name)
    
    def select_item(self, item):
        """选择商品 - 兼容性方法"""
        print(f"📦 商品信息: {item}")
    
    def purchase_selected_item(self):
        """购买选中的商品 - 兼容性方法"""
        return "no_selection"
    
    def get_shop_status(self) -> Dict:
        """获取商店状态信息"""
        return {
            'is_visible': self.is_visible,
            'current_tab': self.current_tab,
            'selected_category': self.selected_category,
            'user_coins': self.user_coins,
            'user_economy': self.user_economy.copy(),
            'shop_items_count': {
                'packs': len(self.shop_config.get('packs', [])),
                'items': len(self.shop_config.get('items', [])),
                'special': len(self.shop_config.get('special', []))
            },
            'theme_info': self.window.get_theme_info() if hasattr(self.window, 'get_theme_info') else {}
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
        self.update_economy_display()
        print(f"💰 强制刷新经济状态 - 金币: {self.user_coins}")
    
    def add_test_currency(self, currency_type: str, amount: int):
        """添加测试货币（仅用于测试）"""
        if currency_type in self.user_economy:
            self.user_economy[currency_type] += amount
            self.update_economy_display()
            print(f"🧪 测试添加 {amount} {currency_type}")
        else:
            print(f"❌ 未知的货币类型: {currency_type}")
    
    def debug_theme_status(self):
        """调试主题状态"""
        print("🔍 商店窗口主题调试信息:")
        if hasattr(self.window, 'debug_theme_info'):
            self.window.debug_theme_info()
        else:
            print("   窗口不支持主题调试")
            
        print(f"   当前分类: {self.current_tab}")
        print(f"   UI元素数量: {len(self.ui_elements)}")
        print(f"   商品按钮数量: {len(self.item_buttons)}")
    
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


    # 兼容性：保持原有的导入方式
    # 其他文件可以继续使用: from .tienda_modern import ModernTiendaWindow
    if __name__ == "__main__":
        print("🎨 ModernTiendaWindow - 主题化版本")
        print("✅ 使用ThemedUIWindow实现完美的窗口主题化")
        print("🎯 自动应用标题栏、关闭按钮和所有UI元素的主题样式")
        print("🔧 保持完整的向后兼容性和所有原有功能")