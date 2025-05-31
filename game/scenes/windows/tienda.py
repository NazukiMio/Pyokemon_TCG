"""
现代化商店窗口 - 重构版
统一主题风格，移除emoji，添加开包逻辑
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIPanel, UILabel, UIWindow, UIScrollingContainer
from pygame_gui.core import ObjectID
import os
import json
from typing import Dict, List, Optional, Callable
from ..styles.theme import Theme
from ..styles.fonts import font_manager
from ..components.button_component import ModernButton
from ..components.message_component import MessageManager

class ModernTiendaWindow:
    """
    现代化商店窗口
    与用户数据库关联，支持购买开包次数
    """
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager, user_data: Dict, 
                 message_manager: MessageManager, database_manager=None):
        """
        初始化商店窗口
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            ui_manager: pygame_gui UI管理器
            user_data: 用户数据字典
            message_manager: 消息管理器
            database_manager: 数据库管理器
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        self.user_data = user_data
        self.message_manager = message_manager
        self.database_manager = database_manager
        
        # 窗口尺寸 - 更大更现代
        self.window_width = min(1000, int(screen_width * 0.9))
        self.window_height = min(700, int(screen_height * 0.85))
        
        # 计算居中位置
        window_x = (screen_width - self.window_width) // 2
        window_y = (screen_height - self.window_height) // 2
        
        # 创建主窗口 - 无标题栏，自定义样式
        self.window = UIWindow(
            rect=pygame.Rect(window_x, window_y, self.window_width, self.window_height),
            manager=ui_manager,
            window_display_title="",
            object_id=ObjectID('#modern_shop_window'),
            resizable=False
        )
        
        # 状态管理
        self.is_visible = True
        self.selected_item = None
        self.scale_factor = min(screen_width / 1920, screen_height / 1080)
        
        # 商店数据
        self.shop_items = self._initialize_shop_items()
        
        # UI元素
        self.modern_buttons = []
        self.item_panels = []
        
        # 回调函数
        self.on_close: Optional[Callable] = None
        self.on_purchase: Optional[Callable] = None
        
        # 创建UI
        self._create_modern_ui()
        
        print(f"🏪 创建现代化商店窗口 - 用户金币: {self.get_user_coins()}")
    
    def _initialize_shop_items(self) -> List[Dict]:
        """初始化商店商品数据"""
        return [
            {
                'id': 'basic_pack_chance',
                'name': 'Oportunidad de Sobre Básico',
                'description': 'Una oportunidad para abrir\nun sobre básico con 5 cartas',
                'price': 100,
                'type': 'pack_chance',
                'pack_type': 'basic',
                'icon_path': 'assets/icons/pack_basic.png',
                'rarity': 'common',
                'stock': 999  # 无限库存
            },
            {
                'id': 'premium_pack_chance',
                'name': 'Oportunidad de Sobre Premium',
                'description': 'Una oportunidad para abrir un\nsobre premium con carta rara garantizada',
                'price': 200,
                'type': 'pack_chance',
                'pack_type': 'premium',
                'icon_path': 'assets/icons/pack_premium.png',
                'rarity': 'rare',
                'stock': 999
            },
            {
                'id': 'legendary_pack_chance',
                'name': 'Oportunidad de Sobre Legendario',
                'description': 'Una oportunidad para abrir un sobre\nlegendario con cartas especiales',
                'price': 500,
                'type': 'pack_chance',
                'pack_type': 'legendary',
                'icon_path': 'assets/icons/pack_legendary.png',
                'rarity': 'legendary',
                'stock': 999
            },
            {
                'id': 'booster_box',
                'name': 'Caja de Refuerzo',
                'description': '5 oportunidades de sobre básico\ncon descuento especial',
                'price': 400,  # 20% descuento
                'type': 'bundle',
                'contains': [{'pack_type': 'basic', 'count': 5}],
                'icon_path': 'assets/icons/booster_box.png',
                'rarity': 'special',
                'stock': 50
            },
            {
                'id': 'starter_bundle',
                'name': 'Paquete de Iniciación',
                'description': '2 sobres básicos + 1 premium\npara nuevos entrenadores',
                'price': 300,
                'type': 'bundle',
                'contains': [
                    {'pack_type': 'basic', 'count': 2},
                    {'pack_type': 'premium', 'count': 1}
                ],
                'icon_path': 'assets/icons/starter_bundle.png',
                'rarity': 'special',
                'stock': 20
            },
            {
                'id': 'daily_coins',
                'name': 'Monedas Diarias',
                'description': 'Bonificación diaria de monedas\npara entrenadores activos',
                'price': 0,  # Gratis
                'type': 'daily_bonus',
                'reward': 50,
                'icon_path': 'assets/icons/daily_coins.png',
                'rarity': 'common',
                'cooldown': 24 * 60 * 60  # 24 horas en segundos
            }
        ]
    
    def get_user_coins(self) -> int:
        """获取用户金币数量"""
        return self.user_data.get('coins', 0)
    
    def get_user_pack_chances(self) -> Dict[str, int]:
        """获取用户的开包次数"""
        return self.user_data.get('pack_chances', {
            'basic': 0,
            'premium': 0,
            'legendary': 0
        })
    
    def _create_modern_ui(self):
        """创建现代化UI界面"""
        # 创建自定义标题栏
        self._create_title_bar()
        
        # 创建货币显示区域
        self._create_currency_display()
        
        # 创建商品网格
        self._create_shop_grid()
        
        # 创建底部按钮区域
        self._create_bottom_buttons()
    
    def _create_title_bar(self):
        """创建自定义标题栏"""
        title_height = 60
        title_rect = pygame.Rect(0, 0, self.window_width, title_height)
        
        self.title_panel = UIPanel(
            relative_rect=title_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#shop_title_panel')
        )
        
        # 商店标题
        self.title_label = UILabel(
            relative_rect=pygame.Rect(20, 15, 300, 30),
            text="Tienda Pokémon",
            manager=self.ui_manager,
            container=self.title_panel,
            object_id=ObjectID('#shop_title')
        )
        
        # 关闭按钮（现代化样式）
        close_button_rect = pygame.Rect(self.window_width - 50, 10, 40, 40)
        self.close_button = ModernButton(
            rect=close_button_rect,
            text="✕",
            button_type="text",
            font_size="lg"
        )
        self.modern_buttons.append(self.close_button)
    
    def _create_currency_display(self):
        """创建货币显示区域"""
        currency_rect = pygame.Rect(10, 70, self.window_width - 20, 50)
        self.currency_panel = UIPanel(
            relative_rect=currency_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#currency_panel')
        )
        
        # 金币显示
        self.coins_label = UILabel(
            relative_rect=pygame.Rect(20, 10, 200, 30),
            text=f"Monedas: {self.get_user_coins()}",
            manager=self.ui_manager,
            container=self.currency_panel,
            object_id=ObjectID('#coins_display')
        )
        
        # 开包次数显示
        pack_chances = self.get_user_pack_chances()
        chances_text = f"Básicos: {pack_chances.get('basic', 0)} | Premium: {pack_chances.get('premium', 0)} | Legendarios: {pack_chances.get('legendary', 0)}"
        
        self.chances_label = UILabel(
            relative_rect=pygame.Rect(250, 10, 500, 30),
            text=chances_text,
            manager=self.ui_manager,
            container=self.currency_panel,
            object_id=ObjectID('#chances_display')
        )
    
    def _create_shop_grid(self):
        """创建商品网格"""
        grid_rect = pygame.Rect(20, 140, self.window_width - 40, self.window_height - 220)
        
        self.scroll_container = UIScrollingContainer(
            relative_rect=grid_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#shop_scroll')
        )
        
        # 网格配置
        items_per_row = 3
        item_width = 280
        item_height = 160
        margin = 20
        
        # 计算网格布局
        grid_width = items_per_row * item_width + (items_per_row - 1) * margin
        start_x = max(10, (grid_rect.width - grid_width) // 2)
        
        for i, item in enumerate(self.shop_items):
            row = i // items_per_row
            col = i % items_per_row
            
            x = start_x + col * (item_width + margin)
            y = row * (item_height + margin) + 20
            
            self._create_shop_item_panel(item, x, y, item_width, item_height, i)
    
    def _create_shop_item_panel(self, item: Dict, x: int, y: int, width: int, height: int, index: int):
        """创建单个商品面板"""
        # 主面板
        item_panel = UIPanel(
            relative_rect=pygame.Rect(x, y, width, height),
            manager=self.ui_manager,
            container=self.scroll_container,
            object_id=ObjectID('#shop_item_panel')
        )
        self.item_panels.append(item_panel)
        
        # 商品名称
        name_label = UILabel(
            relative_rect=pygame.Rect(15, 10, width - 30, 25),
            text=item['name'],
            manager=self.ui_manager,
            container=item_panel,
            object_id=ObjectID('#item_name')
        )
        
        # 商品描述
        desc_label = UILabel(
            relative_rect=pygame.Rect(15, 35, width - 30, 60),
            text=item['description'],
            manager=self.ui_manager,
            container=item_panel,
            object_id=ObjectID('#item_description')
        )
        
        # 价格显示
        price_text = "GRATIS" if item['price'] == 0 else f"{item['price']} Monedas"
        price_label = UILabel(
            relative_rect=pygame.Rect(15, 100, 150, 25),
            text=price_text,
            manager=self.ui_manager,
            container=item_panel,
            object_id=ObjectID('#item_price')
        )
        
        # 购买按钮
        can_afford = self.get_user_coins() >= item['price']
        is_available = self._is_item_available(item)
        
        if item['type'] == 'daily_bonus' and not is_available:
            button_text = "Ya Reclamado"
            button_enabled = False
        elif not can_afford and item['price'] > 0:
            button_text = "Sin Fondos"
            button_enabled = False
        elif item['stock'] <= 0:
            button_text = "Agotado"
            button_enabled = False
        else:
            button_text = "Gratis" if item['price'] == 0 else "Comprar"
            button_enabled = True
        
        buy_button_rect = pygame.Rect(width - 100, height - 40, 85, 30)
        buy_button = ModernButton(
            rect=buy_button_rect,
            text=button_text,
            button_type="primary" if button_enabled else "secondary",
            font_size="sm"
        )
        
        if not button_enabled:
            buy_button.target_scale = 1.0  # 禁用动画
        
        # 存储按钮和商品索引的关联
        buy_button.item_index = index
        self.modern_buttons.append(buy_button)
    
    def _is_item_available(self, item: Dict) -> bool:
        """检查商品是否可用"""
        if item['type'] == 'daily_bonus':
            # 检查每日奖励是否已领取
            last_claim = self.user_data.get('last_daily_claim', 0)
            import time
            current_time = time.time()
            return (current_time - last_claim) >= item.get('cooldown', 86400)
        return True
    
    def _create_bottom_buttons(self):
        """创建底部按钮区域"""
        bottom_y = self.window_height - 60
        
        # 刷新按钮
        refresh_rect = pygame.Rect(20, bottom_y, 120, 40)
        self.refresh_button = ModernButton(
            rect=refresh_rect,
            text="Actualizar",
            button_type="secondary",
            font_size="md"
        )
        self.modern_buttons.append(self.refresh_button)
        
        # 我的卡包按钮
        packs_rect = pygame.Rect(160, bottom_y, 150, 40)
        self.my_packs_button = ModernButton(
            rect=packs_rect,
            text="Mis Oportunidades",
            button_type="primary",
            font_size="md"
        )
        self.modern_buttons.append(self.my_packs_button)
    
    def handle_event(self, event):
        """处理事件"""
        if not self.is_visible:
            return None
        
        # 处理现代按钮事件
        for button in self.modern_buttons:
            if button.rect.collidepoint(pygame.mouse.get_pos()):
                button.update_hover(pygame.mouse.get_pos())
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                mouse_pos = pygame.mouse.get_pos()
                
                # 转换为窗口相对坐标
                window_pos = (
                    mouse_pos[0] - self.window.rect.x,
                    mouse_pos[1] - self.window.rect.y
                )
                
                # 检查按钮点击
                for button in self.modern_buttons:
                    if button.rect.collidepoint(window_pos):
                        button.trigger_flash()
                        
                        if button == self.close_button:
                            self.close()
                            return "close"
                        elif button == self.refresh_button:
                            self._refresh_shop()
                            return "refresh"
                        elif button == self.my_packs_button:
                            return "show_my_packs"
                        elif hasattr(button, 'item_index'):
                            self._purchase_item(button.item_index)
                            return f"purchase_{button.item_index}"
        
        # 处理pygame_gui事件
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self.close()
                return "close"
        
        return None
    
    def _purchase_item(self, item_index: int):
        """购买商品"""
        if item_index < 0 or item_index >= len(self.shop_items):
            return
        
        item = self.shop_items[item_index]
        
        # 检查是否可以购买
        if not self._can_purchase_item(item):
            return
        
        # 执行购买逻辑
        success = self._process_purchase(item)
        
        if success:
            # 更新UI
            self._update_currency_display()
            self._refresh_item_availability()
            
            # 显示成功消息
            self.message_manager.show_message(
                f"{item['name']} comprado con éxito!",
                "success"
            )
            
            # 调用回调
            if self.on_purchase:
                self.on_purchase(item)
        
        print(f"💳 购买商品: {item['name']} - 结果: {'成功' if success else '失败'}")
    
    def _can_purchase_item(self, item: Dict) -> bool:
        """检查是否可以购买商品"""
        # 检查金币
        if self.get_user_coins() < item['price']:
            self.message_manager.show_message("Monedas insuficientes", "error")
            return False
        
        # 检查库存
        if item['stock'] <= 0:
            self.message_manager.show_message("Artículo agotado", "error")
            return False
        
        # 检查每日奖励
        if item['type'] == 'daily_bonus' and not self._is_item_available(item):
            self.message_manager.show_message("Ya reclamaste tu recompensa diaria", "warning")
            return False
        
        return True
    
    def _process_purchase(self, item: Dict) -> bool:
        """处理购买逻辑"""
        try:
            # 扣除金币
            if item['price'] > 0:
                self.user_data['coins'] = self.get_user_coins() - item['price']
            
            # 根据商品类型处理
            if item['type'] == 'pack_chance':
                self._add_pack_chance(item['pack_type'], 1)
            elif item['type'] == 'bundle':
                for content in item['contains']:
                    self._add_pack_chance(content['pack_type'], content['count'])
            elif item['type'] == 'daily_bonus':
                self.user_data['coins'] = self.get_user_coins() + item['reward']
                import time
                self.user_data['last_daily_claim'] = time.time()
            
            # 更新库存
            if item['stock'] < 999:  # 不是无限库存
                item['stock'] -= 1
            
            # 保存到数据库
            if self.database_manager:
                self.database_manager.update_user_data(
                    self.user_data['user_id'],
                    coins=self.user_data['coins'],
                    pack_chances=json.dumps(self.user_data.get('pack_chances', {})),
                    last_daily_claim=self.user_data.get('last_daily_claim', 0)
                )
            
            return True
            
        except Exception as e:
            print(f"❌ 购买失败: {e}")
            self.message_manager.show_message("Error en la compra", "error")
            return False
    
    def _add_pack_chance(self, pack_type: str, count: int):
        """添加开包次数"""
        if 'pack_chances' not in self.user_data:
            self.user_data['pack_chances'] = {}
        
        current_count = self.user_data['pack_chances'].get(pack_type, 0)
        self.user_data['pack_chances'][pack_type] = current_count + count
    
    def _update_currency_display(self):
        """更新货币显示"""
        self.coins_label.set_text(f"Monedas: {self.get_user_coins()}")
        
        pack_chances = self.get_user_pack_chances()
        chances_text = f"Básicos: {pack_chances.get('basic', 0)} | Premium: {pack_chances.get('premium', 0)} | Legendarios: {pack_chances.get('legendary', 0)}"
        self.chances_label.set_text(chances_text)
    
    def _refresh_shop(self):
        """刷新商店"""
        # 重新检查可用性
        self._refresh_item_availability()
        
        # 显示刷新消息
        self.message_manager.show_message("Tienda actualizada", "info")
        
        print("🔄 商店已刷新")
    
    def _refresh_item_availability(self):
        """刷新商品可用性"""
        # 重新创建商品网格以更新按钮状态
        # 清除旧的面板和按钮
        for panel in self.item_panels:
            panel.kill()
        
        # 清除商品相关的按钮
        self.modern_buttons = [btn for btn in self.modern_buttons if not hasattr(btn, 'item_index')]
        self.modern_buttons.extend([self.close_button, self.refresh_button, self.my_packs_button])
        
        self.item_panels.clear()
        
        # 重新创建网格
        self._create_shop_grid()
    
    def update(self, time_delta: float):
        """更新窗口状态"""
        # 更新按钮动画
        for button in self.modern_buttons:
            button.update_animation(time_delta)
    
    def draw_custom_content(self, screen: pygame.Surface):
        """绘制自定义内容"""
        if not self.is_visible:
            return
        
        # 绘制现代按钮
        for button in self.modern_buttons:
            # 转换按钮位置到屏幕坐标
            button_screen_rect = button.rect.copy()
            button_screen_rect.x += self.window.rect.x
            button_screen_rect.y += self.window.rect.y
            
            # 临时创建一个有正确位置的按钮来绘制
            temp_button = type(button)(
                button_screen_rect,
                button.text,
                getattr(button, 'icon', ''),
                button.button_type,
                button.font_size
            )
            temp_button.scale = button.scale
            temp_button.is_hover = button.is_hover
            temp_button.flash = button.flash
            
            temp_button.draw(screen, self.scale_factor)
    
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
        self.modern_buttons.clear()
        self.item_panels.clear()