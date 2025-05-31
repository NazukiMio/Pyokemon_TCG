"""
现代化图鉴窗口
展示用户已获得和未获得的卡片收藏
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIWindow, UIScrollingContainer, UIDropDownMenu, UITextEntryLine
from pygame_gui.core import ObjectID
from typing import Dict, List, Optional, Callable
from game.scenes.styles.theme import Theme
from game.scenes.styles.fonts import font_manager
from game.scenes.components.button_component import ModernButton
from game.scenes.components.message_component import MessageManager

class ModernDexWindow:
    """
    现代化图鉴窗口
    显示卡片收藏，支持筛选和搜索
    """
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager, 
                 user_data: Dict, card_data_manager, message_manager: MessageManager):
        """
        初始化图鉴窗口
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            ui_manager: pygame_gui UI管理器
            user_data: 用户数据
            card_data_manager: 卡片数据管理器
            message_manager: 消息管理器
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        self.user_data = user_data
        self.card_data_manager = card_data_manager
        self.message_manager = message_manager
        
        # 窗口尺寸
        self.window_width = min(1200, int(screen_width * 0.95))
        self.window_height = min(800, int(screen_height * 0.9))
        
        # 计算居中位置
        window_x = (screen_width - self.window_width) // 2
        window_y = (screen_height - self.window_height) // 2
        
        # 创建主窗口
        self.window = UIWindow(
            rect=pygame.Rect(window_x, window_y, self.window_width, self.window_height),
            manager=ui_manager,
            window_display_title="",
            object_id=ObjectID('#modern_dex_window'),
            resizable=False
        )
        
        # 状态管理
        self.is_visible = True
        self.scale_factor = min(screen_width / 1920, screen_height / 1080)
        self.current_filter = "all"  # all, owned, missing
        self.current_rarity_filter = "all"
        self.current_type_filter = "all"
        self.search_query = ""
        
        # 数据
        self.all_cards = []
        self.owned_cards = {}  # card_id -> count
        self.filtered_cards = []
        self.selected_card = None
        
        # UI元素
        self.modern_buttons = []
        self.card_grid_rects = []
        self.cards_per_row = 8
        self.card_width = 120
        self.card_height = 160
        
        # 回调函数
        self.on_close: Optional[Callable] = None
        
        # 初始化数据
        self._load_card_data()
        
        # 创建UI
        self._create_modern_ui()
        
        print(f"📚 创建图鉴窗口 - 总卡片: {len(self.all_cards)}, 已拥有: {len(self.owned_cards)}")
    
    def _load_card_data(self):
        """加载卡片数据"""
        # 获取所有可用卡片
        self.all_cards = self.card_data_manager.get_card_pool()
        
        # 统计用户拥有的卡片
        user_collection = self.user_data.get('card_collection', [])
        self.owned_cards = {}
        
        for card in user_collection:
            card_id = card.get('id', '')
            self.owned_cards[card_id] = self.owned_cards.get(card_id, 0) + 1
        
        # 初始过滤
        self._apply_filters()
    
    def _create_modern_ui(self):
        """创建现代化UI"""
        # 创建标题栏
        self._create_title_bar()
        
        # 创建统计面板
        self._create_stats_panel()
        
        # 创建筛选面板
        self._create_filter_panel()
        
        # 创建卡片网格
        self._create_card_grid()
        
        # 创建详情面板
        self._create_detail_panel()
    
    def _create_title_bar(self):
        """创建标题栏"""
        title_rect = pygame.Rect(0, 0, self.window_width, 50)
        self.title_panel = UIPanel(
            relative_rect=title_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#dex_title_panel')
        )
        
        # 标题
        self.title_label = UILabel(
            relative_rect=pygame.Rect(20, 10, 300, 30),
            text="Pokédex - Mi Colección",
            manager=self.ui_manager,
            container=self.title_panel,
            object_id=ObjectID('#dex_title')
        )
        
        # 关闭按钮
        close_rect = pygame.Rect(self.window_width - 50, 5, 40, 40)
        self.close_button = ModernButton(
            rect=close_rect,
            text="✕",
            button_type="text",
            font_size="lg"
        )
        self.modern_buttons.append(self.close_button)
    
    def _create_stats_panel(self):
        """创建统计面板"""
        stats_rect = pygame.Rect(10, 60, self.window_width - 20, 40)
        self.stats_panel = UIPanel(
            relative_rect=stats_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#stats_panel')
        )
        
        # 统计信息
        total_unique = len(self.all_cards)
        owned_unique = len(self.owned_cards)
        completion_rate = (owned_unique / total_unique * 100) if total_unique > 0 else 0
        
        stats_text = f"Progreso: {owned_unique}/{total_unique} ({completion_rate:.1f}%) | Total de cartas: {sum(self.owned_cards.values())}"
        
        self.stats_label = UILabel(
            relative_rect=pygame.Rect(15, 5, 600, 30),
            text=stats_text,
            manager=self.ui_manager,
            container=self.stats_panel,
            object_id=ObjectID('#stats_display')
        )
    
    def _create_filter_panel(self):
        """创建筛选面板"""
        filter_rect = pygame.Rect(10, 110, self.window_width - 20, 80)
        self.filter_panel = UIPanel(
            relative_rect=filter_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#filter_panel')
        )
        
        # 搜索框
        self.search_entry = UITextEntryLine(
            relative_rect=pygame.Rect(15, 10, 200, 30),
            manager=self.ui_manager,
            container=self.filter_panel,
            placeholder_text="Buscar cartas..."
        )
        
        # 拥有状态筛选
        ownership_options = ["Todas", "Poseídas", "Faltantes"]
        self.ownership_dropdown = UIDropDownMenu(
            relative_rect=pygame.Rect(230, 10, 120, 30),
            options_list=ownership_options,
            starting_option="Todas",
            manager=self.ui_manager,
            container=self.filter_panel
        )
        
        # 稀有度筛选
        rarity_options = ["Todas", "Común", "Poco Común", "Rara", "Épica", "Legendaria"]
        self.rarity_dropdown = UIDropDownMenu(
            relative_rect=pygame.Rect(365, 10, 120, 30),
            options_list=rarity_options,
            starting_option="Todas",
            manager=self.ui_manager,
            container=self.filter_panel
        )
        
        # 类型筛选
        type_options = ["Todos", "Fuego", "Agua", "Planta", "Eléctrico", "Psíquico", "Lucha", "Normal"]
        self.type_dropdown = UIDropDownMenu(
            relative_rect=pygame.Rect(500, 10, 120, 30),
            options_list=type_options,
            starting_option="Todos",
            manager=self.ui_manager,
            container=self.filter_panel
        )
        
        # 筛选按钮
        filter_button_rect = pygame.Rect(635, 10, 80, 30)
        self.filter_button = ModernButton(
            rect=filter_button_rect,
            text="Filtrar",
            button_type="primary",
            font_size="sm"
        )
        self.modern_buttons.append(self.filter_button)
        
        # 重置按钮
        reset_button_rect = pygame.Rect(725, 10, 80, 30)
        self.reset_button = ModernButton(
            rect=reset_button_rect,
            text="Limpiar",
            button_type="secondary",
            font_size="sm"
        )
        self.modern_buttons.append(self.reset_button)
        
        # 视图切换按钮
        grid_view_rect = pygame.Rect(15, 45, 80, 25)
        self.grid_view_button = ModernButton(
            rect=grid_view_rect,
            text="Cuadrícula",
            button_type="primary",
            font_size="xs"
        )
        self.modern_buttons.append(self.grid_view_button)
        
        list_view_rect = pygame.Rect(105, 45, 80, 25)
        self.list_view_button = ModernButton(
            rect=list_view_rect,
            text="Lista",
            button_type="secondary",
            font_size="xs"
        )
        self.modern_buttons.append(self.list_view_button)
    
    def _create_card_grid(self):
        """创建卡片网格"""
        grid_rect = pygame.Rect(10, 200, int(self.window_width * 0.7), self.window_height - 250)
        
        self.scroll_container = UIScrollingContainer(
            relative_rect=grid_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#card_grid_scroll')
        )
        
        self._update_card_grid()
    
    def _create_detail_panel(self):
        """创建详情面板"""
        detail_rect = pygame.Rect(int(self.window_width * 0.72), 200, 
                                 int(self.window_width * 0.26), self.window_height - 250)
        
        self.detail_panel = UIPanel(
            relative_rect=detail_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#detail_panel')
        )
        
        # 详情标题
        self.detail_title = UILabel(
            relative_rect=pygame.Rect(10, 10, detail_rect.width - 20, 30),
            text="Selecciona una carta",
            manager=self.ui_manager,
            container=self.detail_panel,
            object_id=ObjectID('#detail_title')
        )
        
        # 卡片图片区域 (占位符)
        self.detail_image_rect = pygame.Rect(10, 50, detail_rect.width - 20, 200)
        
        # 详情信息
        self.detail_info = UILabel(
            relative_rect=pygame.Rect(10, 260, detail_rect.width - 20, 200),
            text="",
            manager=self.ui_manager,
            container=self.detail_panel,
            object_id=ObjectID('#detail_info')
        )
        
        # 操作按钮区域
        button_y = detail_rect.height - 100
        
        # 添加到卡组按钮
        add_to_deck_rect = pygame.Rect(10, button_y, detail_rect.width - 20, 35)
        self.add_to_deck_button = ModernButton(
            rect=add_to_deck_rect,
            text="Añadir al Mazo",
            button_type="primary",
            font_size="sm"
        )
        self.modern_buttons.append(self.add_to_deck_button)
        
        # 查看大图按钮
        view_large_rect = pygame.Rect(10, button_y + 45, detail_rect.width - 20, 35)
        self.view_large_button = ModernButton(
            rect=view_large_rect,
            text="Ver Imagen",
            button_type="secondary",
            font_size="sm"
        )
        self.modern_buttons.append(self.view_large_button)
    
    def _update_card_grid(self):
        """更新卡片网格显示"""
        # 清除现有的卡片矩形
        self.card_grid_rects.clear()
        
        # 计算网格布局
        margin = 10
        start_x = margin
        start_y = margin
        
        grid_width = self.scroll_container.get_container().get_rect().width
        cards_per_row = max(1, (grid_width - margin) // (self.card_width + margin))
        
        for i, card in enumerate(self.filtered_cards):
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = start_x + col * (self.card_width + margin)
            y = start_y + row * (self.card_height + margin)
            
            card_rect = pygame.Rect(x, y, self.card_width, self.card_height)
            self.card_grid_rects.append({
                'rect': card_rect,
                'card': card,
                'is_owned': card['id'] in self.owned_cards,
                'count': self.owned_cards.get(card['id'], 0)
            })
    
    def _apply_filters(self):
        """应用筛选条件"""
        filtered = self.all_cards.copy()
        
        # 搜索筛选
        if self.search_query:
            query = self.search_query.lower()
            filtered = [card for card in filtered 
                       if query in card.get('name', '').lower() or 
                          query in card.get('pokemon_type', '').lower()]
        
        # 拥有状态筛选
        if self.current_filter == "owned":
            filtered = [card for card in filtered if card['id'] in self.owned_cards]
        elif self.current_filter == "missing":
            filtered = [card for card in filtered if card['id'] not in self.owned_cards]
        
        # 稀有度筛选
        if self.current_rarity_filter != "all":
            rarity_map = {
                "común": "common",
                "poco común": "uncommon", 
                "rara": "rare",
                "épica": "epic",
                "legendaria": "legendary"
            }
            target_rarity = rarity_map.get(self.current_rarity_filter.lower())
            if target_rarity:
                filtered = [card for card in filtered if card.get('rarity') == target_rarity]
        
        # 类型筛选
        if self.current_type_filter != "all":
            type_map = {
                "fuego": "fire",
                "agua": "water",
                "planta": "grass",
                "eléctrico": "electric",
                "psíquico": "psychic",
                "lucha": "fighting",
                "normal": "normal"
            }
            target_type = type_map.get(self.current_type_filter.lower())
            if target_type:
                filtered = [card for card in filtered if card.get('pokemon_type') == target_type]
        
        self.filtered_cards = filtered
        self._update_card_grid()
        
        # 更新统计显示
        self._update_stats_display()
    
    def _update_stats_display(self):
        """更新统计显示"""
        total_filtered = len(self.filtered_cards)
        owned_filtered = len([card for card in self.filtered_cards if card['id'] in self.owned_cards])
        
        if total_filtered > 0:
            completion = (owned_filtered / total_filtered * 100)
            stats_text = f"Mostrando: {owned_filtered}/{total_filtered} ({completion:.1f}%)"
        else:
            stats_text = "No se encontraron cartas"
        
        self.stats_label.set_text(stats_text)
    
    def handle_event(self, event):
        """处理事件"""
        if not self.is_visible:
            return None
        
        # 更新按钮悬停状态
        mouse_pos = pygame.mouse.get_pos()
        for button in self.modern_buttons:
            window_pos = (
                mouse_pos[0] - self.window.rect.x,
                mouse_pos[1] - self.window.rect.y
            )
            button.update_hover(window_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
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
                    elif button == self.filter_button:
                        self._handle_filter_click()
                        return "filter"
                    elif button == self.reset_button:
                        self._reset_filters()
                        return "reset"
                    elif button == self.grid_view_button:
                        self._switch_to_grid_view()
                        return "grid_view"
                    elif button == self.list_view_button:
                        self._switch_to_list_view()
                        return "list_view"
                    elif button == self.add_to_deck_button and self.selected_card:
                        return f"add_to_deck_{self.selected_card['id']}"
                    elif button == self.view_large_button and self.selected_card:
                        return f"view_large_{self.selected_card['id']}"
            
            # 检查卡片点击
            scroll_pos = window_pos[0] - 10, window_pos[1] - 200  # 调整到滚动容器坐标
            for card_item in self.card_grid_rects:
                if card_item['rect'].collidepoint(scroll_pos):
                    self._select_card(card_item['card'])
                    return f"select_card_{card_item['card']['id']}"
        
        # 处理下拉菜单事件
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.ownership_dropdown:
                option_map = {"Todas": "all", "Poseídas": "owned", "Faltantes": "missing"}
                self.current_filter = option_map.get(event.text, "all")
                self._apply_filters()
            elif event.ui_element == self.rarity_dropdown:
                self.current_rarity_filter = event.text.lower()
                self._apply_filters()
            elif event.ui_element == self.type_dropdown:
                self.current_type_filter = event.text.lower()
                self._apply_filters()
        
        # 处理搜索框事件
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == self.search_entry:
                self.search_query = event.text
                self._apply_filters()
        
        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self.close()
                return "close"
        
        return None
    
    def _handle_filter_click(self):
        """处理筛选按钮点击"""
        # 获取当前搜索文本
        self.search_query = self.search_entry.get_text()
        self._apply_filters()
        
        self.message_manager.show_message(
            f"Filtros aplicados - {len(self.filtered_cards)} cartas encontradas",
            "info"
        )
    
    def _reset_filters(self):
        """重置所有筛选条件"""
        self.search_query = ""
        self.current_filter = "all"
        self.current_rarity_filter = "all"
        self.current_type_filter = "all"
        
        self.search_entry.set_text("")
        self.ownership_dropdown.selected_option = "Todas"
        self.rarity_dropdown.selected_option = "Todas"
        self.type_dropdown.selected_option = "Todos"
        
        self._apply_filters()
        
        self.message_manager.show_message("Filtros restablecidos", "info")
    
    def _switch_to_grid_view(self):
        """切换到网格视图"""
        self.grid_view_button.button_type = "primary"
        self.list_view_button.button_type = "secondary"
        self.cards_per_row = 8
        self.card_width = 120
        self.card_height = 160
        self._update_card_grid()
    
    def _switch_to_list_view(self):
        """切换到列表视图"""
        self.grid_view_button.button_type = "secondary"
        self.list_view_button.button_type = "primary"
        self.cards_per_row = 2
        self.card_width = 250
        self.card_height = 120
        self._update_card_grid()
    
    def _select_card(self, card: Dict):
        """选择卡片并显示详情"""
        self.selected_card = card
        self._update_detail_panel()
    
    def _update_detail_panel(self):
        """更新详情面板"""
        if not self.selected_card:
            return
        
        card = self.selected_card
        
        # 更新标题
        self.detail_title.set_text(card.get('name', 'Unknown'))
        
        # 构建详情信息
        info_lines = []
        info_lines.append(f"Tipo: {card.get('pokemon_type', 'Unknown').title()}")
        info_lines.append(f"Rareza: {card.get('rarity', 'common').title()}")
        info_lines.append(f"HP: {card.get('hp', 0)}")
        
        # 拥有信息
        owned_count = self.owned_cards.get(card['id'], 0)
        if owned_count > 0:
            info_lines.append(f"Poseídas: {owned_count}")
        else:
            info_lines.append("No poseída")
        
        # 攻击信息
        attacks = card.get('attacks', [])
        if attacks:
            info_lines.append("\nAtaques:")
            for attack in attacks[:2]:  # 最多显示2个攻击
                info_lines.append(f"• {attack.get('name', 'Unknown')} ({attack.get('damage', 0)} daño)")
        
        # 弱点和抗性
        weakness = card.get('weakness', {})
        if weakness:
            info_lines.append(f"\nDebilidad: {weakness.get('type', 'None').title()}")
        
        resistance = card.get('resistance', {})
        if resistance:
            info_lines.append(f"Resistencia: {resistance.get('type', 'None').title()}")
        
        detail_text = "\n".join(info_lines)
        self.detail_info.set_text(detail_text)
        
        # 更新按钮状态
        if owned_count > 0:
            self.add_to_deck_button.button_type = "primary"
        else:
            self.add_to_deck_button.button_type = "secondary"
    
    def update(self, time_delta: float):
        """更新窗口状态"""
        # 更新按钮动画
        for button in self.modern_buttons:
            button.update_animation(time_delta)
    
    def draw_custom_content(self, screen: pygame.Surface):
        """绘制自定义内容"""
        if not self.is_visible:
            return
        
        # 绘制卡片网格
        self._draw_card_grid(screen)
        
        # 绘制详情面板内容
        self._draw_detail_panel_content(screen)
        
        # 绘制按钮
        self._draw_modern_buttons(screen)
    
    def _draw_card_grid(self, screen: pygame.Surface):
        """绘制卡片网格"""
        # 获取滚动容器的可见区域
        scroll_rect = self.scroll_container.get_container().get_rect()
        scroll_offset_x = self.scroll_container.get_container().get_relative_rect().x
        scroll_offset_y = self.scroll_container.get_container().get_relative_rect().y
        
        for card_item in self.card_grid_rects:
            card_rect = card_item['rect'].copy()
            card_rect.x += self.window.rect.x + 10 + scroll_offset_x
            card_rect.y += self.window.rect.y + 200 + scroll_offset_y
            
            # 检查是否在可见区域内
            if card_rect.colliderect(screen.get_rect()):
                self._draw_single_card_in_grid(screen, card_item, card_rect)
    
    def _draw_single_card_in_grid(self, screen: pygame.Surface, card_item: Dict, rect: pygame.Rect):
        """在网格中绘制单张卡片"""
        card = card_item['card']
        is_owned = card_item['is_owned']
        count = card_item['count']
        
        # 卡片背景色
        if card == self.selected_card:
            bg_color = (100, 150, 255, 200)  # 选中状态
        elif is_owned:
            bg_color = (240, 240, 240, 220)  # 已拥有
        else:
            bg_color = (180, 180, 180, 150)  # 未拥有
        
        # 绘制卡片背景
        card_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        card_surface.fill(bg_color)
        
        # 绘制边框
        rarity_color = self._get_rarity_color(card.get('rarity', 'common'))
        border_width = 3 if card == self.selected_card else 2
        pygame.draw.rect(card_surface, rarity_color, 
                        (0, 0, rect.width, rect.height), 
                        width=border_width, border_radius=8)
        
        screen.blit(card_surface, rect)
        
        # 绘制卡片名称
        name_font = font_manager.get_font_by_size(12)
        name_color = (50, 50, 50) if is_owned else (120, 120, 120)
        name_surface = name_font.render(card.get('name', 'Unknown'), True, name_color)
        
        # 缩放名称以适应卡片宽度
        if name_surface.get_width() > rect.width - 10:
            scale = (rect.width - 10) / name_surface.get_width()
            name_surface = pygame.transform.scale(name_surface, 
                                                 (int(name_surface.get_width() * scale),
                                                  int(name_surface.get_height() * scale)))
        
        name_rect = name_surface.get_rect(centerx=rect.centerx, y=rect.y + 5)
        screen.blit(name_surface, name_rect)
        
        # 绘制HP
        hp_font = font_manager.get_font_by_size(10)
        hp_text = f"HP: {card.get('hp', 0)}"
        hp_surface = hp_font.render(hp_text, True, name_color)
        hp_rect = hp_surface.get_rect(centerx=rect.centerx, y=rect.y + 25)
        screen.blit(hp_surface, hp_rect)
        
        # 绘制稀有度
        rarity_text = card.get('rarity', 'common').title()
        rarity_surface = hp_font.render(rarity_text, True, rarity_color)
        rarity_rect = rarity_surface.get_rect(centerx=rect.centerx, y=rect.bottom - 25)
        screen.blit(rarity_surface, rarity_rect)
        
        # 如果拥有，绘制数量
        if is_owned and count > 1:
            count_font = font_manager.get_font_by_size(14)
            count_surface = count_font.render(f"x{count}", True, (255, 255, 255))
            count_bg = pygame.Surface((30, 20), pygame.SRCALPHA)
            count_bg.fill((0, 0, 0, 180))
            screen.blit(count_bg, (rect.right - 35, rect.y + 5))
            screen.blit(count_surface, (rect.right - 30, rect.y + 8))
        
        # 如果未拥有，绘制遮罩
        if not is_owned:
            mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 100))
            screen.blit(mask, rect)
            
            # 绘制问号
            question_font = font_manager.get_font_by_size(36)
            question_surface = question_font.render("?", True, (200, 200, 200))
            question_rect = question_surface.get_rect(center=rect.center)
            screen.blit(question_surface, question_rect)
    
    def _draw_detail_panel_content(self, screen: pygame.Surface):
        """绘制详情面板内容"""
        if not self.selected_card:
            return
        
        # 绘制卡片预览图 (占位符)
        detail_image_screen_rect = pygame.Rect(
            self.window.rect.x + int(self.window_width * 0.72) + 10,
            self.window.rect.y + 250,
            self.detail_image_rect.width,
            self.detail_image_rect.height
        )
        
        # 绘制图片占位符
        placeholder_surface = pygame.Surface((detail_image_screen_rect.width, detail_image_screen_rect.height))
        rarity_color = self._get_rarity_color(self.selected_card.get('rarity', 'common'))
        placeholder_surface.fill(rarity_color)
        
        # 添加卡片名称到占位符
        name_font = font_manager.get_font_by_size(16)
        name_surface = name_font.render(self.selected_card.get('name', 'Unknown'), True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=(placeholder_surface.get_width() // 2, 30))
        placeholder_surface.blit(name_surface, name_rect)
        
        # 添加"图片占位符"文本
        placeholder_font = font_manager.get_font_by_size(14)
        placeholder_text = placeholder_font.render("Imagen no disponible", True, (255, 255, 255))
        placeholder_rect = placeholder_text.get_rect(center=(placeholder_surface.get_width() // 2, placeholder_surface.get_height() // 2))
        placeholder_surface.blit(placeholder_text, placeholder_rect)
        
        screen.blit(placeholder_surface, detail_image_screen_rect)
    
    def _draw_modern_buttons(self, screen: pygame.Surface):
        """绘制现代按钮"""
        for button in self.modern_buttons:
            # 转换到屏幕坐标
            screen_rect = pygame.Rect(
                self.window.rect.x + button.rect.x,
                self.window.rect.y + button.rect.y,
                button.rect.width,
                button.rect.height
            )
            
            # 创建临时按钮进行绘制
            temp_button = type(button)(
                screen_rect,
                button.text,
                getattr(button, 'icon', ''),
                button.button_type,
                button.font_size
            )
            temp_button.scale = button.scale
            temp_button.is_hover = button.is_hover
            temp_button.flash = button.flash
            
            temp_button.draw(screen, self.scale_factor)
    
    def _get_rarity_color(self, rarity: str) -> tuple:
        """获取稀有度颜色"""
        colors = {
            'common': (150, 150, 150),
            'uncommon': (100, 200, 100),
            'rare': (100, 150, 255),
            'epic': (200, 100, 255),
            'legendary': (255, 215, 0)
        }
        return colors.get(rarity, (100, 100, 100))
    
    def refresh_data(self):
        """刷新数据"""
        self._load_card_data()
        self._apply_filters()
        self.message_manager.show_message("Datos actualizados", "success")
    
    def close(self):
        """关闭窗口"""
        if self.is_visible:
            self.is_visible = False
            if self.window:
                self.window.kill()
            if self.on_close:
                self.on_close()
            print("🚪 关闭图鉴窗口")
    
    def cleanup(self):
        """清理资源"""
        if self.window:
            self.window.kill()
        self.modern_buttons.clear()
        self.card_grid_rects.clear()