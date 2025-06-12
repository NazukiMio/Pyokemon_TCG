import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIPanel, UILabel, UIWindow, UIScrollingContainer, UIImage
from pygame_gui.core import ObjectID
import os

class TiendaWindow:
    """
    商店窗口 - 弹出式对话框
    包含各种卡包、道具和特殊商品
    """
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager):
        """
        初始化商店窗口
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            ui_manager: pygame_gui UI管理器
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        
        # 窗口尺寸
        self.window_width = min(900, int(screen_width * 0.85))
        self.window_height = min(650, int(screen_height * 0.85))
        
        # 计算居中位置
        window_x = (screen_width - self.window_width) // 2
        window_y = (screen_height - self.window_height) // 2
        
        # 创建主窗口
        self.window = UIWindow(
            rect=pygame.Rect(window_x, window_y, self.window_width, self.window_height),
            manager=ui_manager,
            window_display_title="🛍️ Tienda Pokémon",
            object_id=ObjectID('#tienda_window'),
            resizable=False
        )
        
        # 状态管理
        self.is_visible = True
        self.player_coins = 1000  # 玩家金币（示例）
        self.selected_item = None
        
        # 商店商品数据
        self.shop_items = [
            {
                'name': 'Sobre Básico',
                'description': 'Contiene 5 cartas comunes\ny 1 carta poco común',
                'price': 100,
                'type': 'pack',
                'image': 'packet1.png',
                'stock': 99
            },
            {
                'name': 'Sobre Premium',
                'description': 'Contiene 5 cartas\ny 1 carta rara garantizada',
                'price': 200,
                'type': 'pack',
                'image': 'packet2.png',
                'stock': 50
            },
            {
                'name': 'Sobre Legendario',
                'description': 'Contiene cartas especiales\ny posibilidad de legendarias',
                'price': 500,
                'type': 'pack',
                'image': 'packet3.png',
                'stock': 20
            },
            {
                'name': 'Poción Curativa',
                'description': 'Restaura 50 HP\na cualquier Pokémon',
                'price': 50,
                'type': 'item',
                'image': None,
                'stock': 25
            },
            {
                'name': 'Poción Super',
                'description': 'Restaura 100 HP\na cualquier Pokémon',
                'price': 100,
                'type': 'item',
                'image': None,
                'stock': 15
            },
            {
                'name': 'Revivir',
                'description': 'Revive un Pokémon\nderrotado con 50% HP',
                'price': 150,
                'type': 'item',
                'image': None,
                'stock': 10
            },
            {
                'name': 'Amuleto de Suerte',
                'description': 'Aumenta la probabilidad\nde encontrar cartas raras',
                'price': 300,
                'type': 'special',
                'image': None,
                'stock': 5
            },
            {
                'name': 'Cristal de Energía',
                'description': 'Proporciona energía extra\npara ataques especiales',
                'price': 250,
                'type': 'special',
                'image': None,
                'stock': 8
            }
        ]
        
        # 创建UI元素
        self.create_ui_elements()
        
        # 回调函数
        self.on_close = None
        self.on_purchase = None
        
        print(f"🛍️ 创建商店窗口 - 玩家金币: {self.player_coins}")
    
    def create_ui_elements(self):
        """创建UI元素"""
        # 顶部信息栏
        top_panel_rect = pygame.Rect(10, 10, self.window_width - 20, 60)
        self.top_panel = UIPanel(
            relative_rect=top_panel_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#top_panel')
        )
        
        # 金币显示
        self.coins_label = UILabel(
            relative_rect=pygame.Rect(20, 15, 200, 30),
            text=f"💰 Monedas: {self.player_coins}",
            manager=self.ui_manager,
            container=self.top_panel,
            object_id=ObjectID('#coins_label')
        )
        
        # 购物车信息
        self.cart_label = UILabel(
            relative_rect=pygame.Rect(self.window_width - 250, 15, 200, 30),
            text="🛒 Carrito: Vacío",
            manager=self.ui_manager,
            container=self.top_panel,
            object_id=ObjectID('#cart_label')
        )
        
        # 商品滚动容器
        scroll_rect = pygame.Rect(10, 80, self.window_width - 20, self.window_height - 200)
        self.scroll_container = UIScrollingContainer(
            relative_rect=scroll_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#scroll_container')
        )
        
        # 创建商品网格
        self.create_shop_grid()
        
        # 底部按钮区域
        bottom_y = self.window_height - 110
        
        # 购买按钮
        self.buy_button = UIButton(
            relative_rect=pygame.Rect(20, bottom_y, 150, 40),
            text="💳 Comprar",
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#buy_button')
        )
        self.buy_button.disable()  # 初始禁用
        
        # 刷新商店按钮
        self.refresh_button = UIButton(
            relative_rect=pygame.Rect(180, bottom_y, 150, 40),
            text="🔄 Actualizar",
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#refresh_button')
        )
        
        # 关闭按钮
        self.close_button = UIButton(
            relative_rect=pygame.Rect(self.window_width - 120, bottom_y, 100, 40),
            text="Cerrar",
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#close_button')
        )
        
        # 状态标签
        self.status_label = UILabel(
            relative_rect=pygame.Rect(20, bottom_y + 50, self.window_width - 40, 30),
            text="🛒 Selecciona un artículo para comprarlo",
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#status_label')
        )
    
    def create_shop_grid(self):
        """创建商品网格布局"""
        self.item_buttons = []
        self.item_panels = []
        
        # 网格配置
        items_per_row = 3
        item_width = 250
        item_height = 120
        margin = 15
        
        # 计算网格尺寸
        grid_width = items_per_row * item_width + (items_per_row - 1) * margin
        start_x = (self.scroll_container.get_container().get_rect().width - grid_width) // 2
        
        for i, item in enumerate(self.shop_items):
            row = i // items_per_row
            col = i % items_per_row
            
            x = start_x + col * (item_width + margin)
            y = row * (item_height + margin) + 20
            
            # 创建商品面板
            item_panel = UIPanel(
                relative_rect=pygame.Rect(x, y, item_width, item_height),
                manager=self.ui_manager,
                container=self.scroll_container,
                object_id=ObjectID('#item_panel')
            )
            self.item_panels.append(item_panel)
            
            # 商品图标 (如果有图片的话)
            icon_text = self.get_item_icon(item['type'])
            icon_label = UILabel(
                relative_rect=pygame.Rect(10, 10, 40, 40),
                text=icon_text,
                manager=self.ui_manager,
                container=item_panel,
                object_id=ObjectID('#item_icon')
            )
            
            # 商品名称
            name_label = UILabel(
                relative_rect=pygame.Rect(60, 10, 180, 25),
                text=item['name'],
                manager=self.ui_manager,
                container=item_panel,
                object_id=ObjectID('#item_name')
            )
            
            # 商品描述
            desc_label = UILabel(
                relative_rect=pygame.Rect(10, 35, 230, 50),
                text=item['description'],
                manager=self.ui_manager,
                container=item_panel,
                object_id=ObjectID('#item_description')
            )
            
            # 价格和库存
            price_text = f"💰 {item['price']} monedas"
            stock_text = f"📦 Stock: {item['stock']}"
            info_text = f"{price_text} | {stock_text}"
            
            info_label = UILabel(
                relative_rect=pygame.Rect(10, 85, 150, 25),
                text=info_text,
                manager=self.ui_manager,
                container=item_panel,
                object_id=ObjectID('#item_info')
            )
            
            # 购买按钮
            buy_enabled = item['stock'] > 0 and self.player_coins >= item['price']
            button_text = "Comprar" if buy_enabled else "Agotado" if item['stock'] == 0 else "Sin fondos"
            
            item_button = UIButton(
                relative_rect=pygame.Rect(170, 85, 70, 25),
                text=button_text,
                manager=self.ui_manager,
                container=item_panel,
                object_id=ObjectID(f'#buy_item_{i}')
            )
            
            if not buy_enabled:
                item_button.disable()
            
            self.item_buttons.append(item_button)
    
    def get_item_icon(self, item_type: str) -> str:
        """获取商品图标"""
        icons = {
            'pack': '🎴',
            'item': '🧪',
            'special': '✨'
        }
        return icons.get(item_type, '📦')
    
    def handle_event(self, event):
        """处理事件"""
        if not self.is_visible:
            return None
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # 检查商品购买按钮
            for i, button in enumerate(self.item_buttons):
                if event.ui_element == button:
                    self.purchase_item(i)
                    return f"buy_item_{i}"
            
            if event.ui_element == self.buy_button:
                if self.selected_item is not None:
                    self.purchase_item(self.selected_item)
                    return "purchase"
            
            elif event.ui_element == self.refresh_button:
                self.refresh_shop()
                return "refresh"
            
            elif event.ui_element == self.close_button:
                self.close()
                return "close"
        
        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self.close()
                return "close"
        
        return None
    
    def purchase_item(self, item_index: int):
        """购买商品"""
        if item_index < 0 or item_index >= len(self.shop_items):
            return
        
        item = self.shop_items[item_index]
        
        # 检查是否能够购买
        if item['stock'] <= 0:
            self.status_label.set_text("❌ Artículo agotado")
            return
        
        if self.player_coins < item['price']:
            self.status_label.set_text("❌ Monedas insuficientes")
            return
        
        # 执行购买
        self.player_coins -= item['price']
        item['stock'] -= 1
        
        # 更新UI
        self.coins_label.set_text(f"💰 Monedas: {self.player_coins}")
        self.status_label.set_text(f"✅ ¡{item['name']} comprado con éxito!")
        
        # 重新创建商品网格以更新库存状态
        self.refresh_item_grid()
        
        # 调用回调
        if self.on_purchase:
            self.on_purchase(item_index, item)
        
        print(f"💳 购买商品: {item['name']} - 花费: {item['price']} - 剩余金币: {self.player_coins}")
    
    def refresh_shop(self):
        """刷新商店（重新随机化库存或添加新商品）"""
        import random
        
        # 随机补充一些库存
        for item in self.shop_items:
            if item['stock'] < 5:
                item['stock'] += random.randint(1, 3)
            
            # 偶尔会有折扣
            if random.random() < 0.2:  # 20%概率折扣
                original_price = item.get('original_price', item['price'])
                if 'original_price' not in item:
                    item['original_price'] = item['price']
                item['price'] = int(original_price * 0.8)  # 8折
        
        self.refresh_item_grid()
        self.status_label.set_text("🔄 ¡Tienda actualizada! Algunos artículos pueden tener descuento.")
        print("🔄 商店已刷新")
    
    def refresh_item_grid(self):
        """刷新商品网格显示"""
        # 清除旧的UI元素
        for panel in self.item_panels:
            panel.kill()
        
        self.item_panels.clear()
        self.item_buttons.clear()
        
        # 重新创建网格
        self.create_shop_grid()
    
    def add_coins(self, amount: int):
        """添加金币"""
        self.player_coins += amount
        self.coins_label.set_text(f"💰 Monedas: {self.player_coins}")
        self.refresh_item_grid()  # 更新购买按钮状态
    
    def draw_shop_effects(self, screen: pygame.Surface):
        """绘制商店特效"""
        if not self.is_visible:
            return
        
        # 获取窗口内容区域
        try:
            content_rect = self.window.get_container().get_rect()
        except:
            return
        
        # 简单的金币闪烁效果
        import time
        import math
        current_time = time.time()
        
        # 在顶部画一些装饰性的金币
        for i in range(5):
            coin_x = content_rect.x + 30 + i * 40
            coin_y = content_rect.y + 35
            
            # 金币闪烁
            alpha = int(180 + 75 * abs(math.sin(current_time * 2 + i)))
            alpha = max(0, min(255, alpha))  # 确保alpha在有效范围内
            
            coin_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(coin_surface, (255, 215, 0, alpha), (10, 10), 8)
            pygame.draw.circle(coin_surface, (255, 255, 0, alpha // 2), (10, 10), 5)
            
            screen.blit(coin_surface, (coin_x, coin_y))
    
    def update(self, time_delta: float):
        """更新窗口状态"""
        # 这里可以添加动画更新逻辑
        pass
    
    def close(self):
        """关闭窗口"""
        if self.is_visible:
            self.is_visible = False
            if self.window:
                self.window.kill()
            if self.on_close:
                self.on_close()
            print("🚪 关闭商店窗口")
    
    def cleanup(self):
        """清理资源"""
        if self.window:
            self.window.kill()