"""
现代化开包窗口 - 重构版
真实的开包逻辑，卡片数据管理，动画效果
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIPanel, UILabel, UIWindow
from pygame_gui.core import ObjectID
import random
import json
from typing import Dict, List, Optional, Callable
from ..styles.theme import Theme
from ..styles.fonts import font_manager
from ..components.button_component import ModernButton
from ..components.message_component import MessageManager

class ModernPackageWindow:
    """
    现代化开包窗口
    真实的卡片生成和数据存储
    """
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager, pack_type: str,
                 user_data: Dict, message_manager: MessageManager, card_data_manager=None,
                 database_manager=None):
        """
        初始化开包窗口
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            ui_manager: pygame_gui UI管理器
            pack_type: 卡包类型 (basic, premium, legendary)
            user_data: 用户数据
            message_manager: 消息管理器
            card_data_manager: 卡片数据管理器
            database_manager: 数据库管理器
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        self.pack_type = pack_type
        self.user_data = user_data
        self.message_manager = message_manager
        self.card_data_manager = card_data_manager
        self.database_manager = database_manager
        
        # 窗口尺寸
        self.window_width = min(900, int(screen_width * 0.8))
        self.window_height = min(700, int(screen_height * 0.85))
        
        # 计算居中位置
        window_x = (screen_width - self.window_width) // 2
        window_y = (screen_height - self.window_height) // 2
        
        # 创建主窗口
        self.window = UIWindow(
            rect=pygame.Rect(window_x, window_y, self.window_width, self.window_height),
            manager=ui_manager,
            window_display_title="",
            object_id=ObjectID('#modern_package_window'),
            resizable=False
        )
        
        # 状态管理
        self.is_visible = True
        self.animation_state = "idle"  # idle, opening, revealing, completed
        self.animation_timer = 0
        self.scale_factor = min(screen_width / 1920, screen_height / 1080)
        
        # 开包数据
        self.pack_config = self._get_pack_config()
        self.opened_cards = []
        self.new_cards = []  # 新获得的卡片
        
        # UI元素
        self.modern_buttons = []
        self.card_display_rects = []
        
        # 动画相关
        self.pack_scale = 1.0
        self.pack_rotation = 0
        self.card_reveal_index = 0
        self.sparkle_particles = []
        
        # 回调函数
        self.on_close: Optional[Callable] = None
        self.on_cards_obtained: Optional[Callable] = None
        
        # 创建UI
        self._create_modern_ui()
        
        print(f"📦 创建现代化开包窗口: {self.get_pack_name()}")
    
    def _get_pack_config(self) -> Dict:
        """获取卡包配置"""
        configs = {
            'basic': {
                'name': 'Sobre Básico',
                'card_count': 5,
                'rarity_rates': {
                    'common': 0.7,      # 70%
                    'uncommon': 0.25,   # 25%
                    'rare': 0.05        # 5%
                },
                'guaranteed': ['common'],
                'icon_path': 'assets/icons/pack_basic.png'
            },
            'premium': {
                'name': 'Sobre Premium',
                'card_count': 5,
                'rarity_rates': {
                    'common': 0.4,      # 40%
                    'uncommon': 0.35,   # 35%
                    'rare': 0.2,        # 20%
                    'epic': 0.05        # 5%
                },
                'guaranteed': ['rare'],
                'icon_path': 'assets/icons/pack_premium.png'
            },
            'legendary': {
                'name': 'Sobre Legendario',
                'card_count': 6,
                'rarity_rates': {
                    'uncommon': 0.3,    # 30%
                    'rare': 0.4,        # 40%
                    'epic': 0.25,       # 25%
                    'legendary': 0.05   # 5%
                },
                'guaranteed': ['epic'],
                'icon_path': 'assets/icons/pack_legendary.png'
            }
        }
        return configs.get(self.pack_type, configs['basic'])
    
    def get_pack_name(self) -> str:
        """获取卡包名称"""
        return self.pack_config['name']
    
    def _create_modern_ui(self):
        """创建现代化UI"""
        # 创建标题栏
        self._create_title_bar()
        
        # 创建卡包显示区域
        self._create_pack_display_area()
        
        # 创建卡片展示区域
        self._create_card_display_area()
        
        # 创建控制按钮
        self._create_control_buttons()
    
    def _create_title_bar(self):
        """创建标题栏"""
        title_rect = pygame.Rect(0, 0, self.window_width, 60)
        self.title_panel = UIPanel(
            relative_rect=title_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#pack_title_panel')
        )
        
        # 标题文本
        self.title_label = UILabel(
            relative_rect=pygame.Rect(20, 15, 400, 30),
            text=f"Abrir {self.get_pack_name()}",
            manager=self.ui_manager,
            container=self.title_panel,
            object_id=ObjectID('#pack_title')
        )
        
        # 关闭按钮
        close_rect = pygame.Rect(self.window_width - 50, 10, 40, 40)
        self.close_button = ModernButton(
            rect=close_rect,
            text="✕",
            button_type="text",
            font_size="lg"
        )
        self.modern_buttons.append(self.close_button)
    
    def _create_pack_display_area(self):
        """创建卡包显示区域"""
        self.pack_display_rect = pygame.Rect(
            self.window_width // 2 - 100,
            80,
            200,
            200
        )
    
    def _create_card_display_area(self):
        """创建卡片展示区域"""
        # 卡片网格布局
        cards_per_row = 5
        card_width = 120
        card_height = 160
        margin = 15
        
        start_y = 300
        start_x = (self.window_width - (cards_per_row * card_width + (cards_per_row - 1) * margin)) // 2
        
        self.card_display_rects = []
        for i in range(self.pack_config['card_count']):
            row = i // cards_per_row
            col = i % cards_per_row
            
            x = start_x + col * (card_width + margin)
            y = start_y + row * (card_height + margin)
            
            self.card_display_rects.append(pygame.Rect(x, y, card_width, card_height))
    
    def _create_control_buttons(self):
        """创建控制按钮"""
        button_y = self.window_height - 80
        
        # 开包按钮
        open_rect = pygame.Rect(self.window_width // 2 - 100, button_y, 200, 50)
        self.open_button = ModernButton(
            rect=open_rect,
            text="Abrir Sobre",
            button_type="primary",
            font_size="lg"
        )
        self.modern_buttons.append(self.open_button)
        
        # 再开一个按钮（开包后显示）
        again_rect = pygame.Rect(self.window_width // 2 - 150, button_y, 120, 40)
        self.open_again_button = ModernButton(
            rect=again_rect,
            text="Abrir Otro",
            button_type="secondary",
            font_size="md"
        )
        self.modern_buttons.append(self.open_again_button)
        
        # 查看收藏按钮
        collection_rect = pygame.Rect(self.window_width // 2 + 30, button_y, 120, 40)
        self.view_collection_button = ModernButton(
            rect=collection_rect,
            text="Ver Colección",
            button_type="secondary",
            font_size="md"
        )
        self.modern_buttons.append(self.view_collection_button)
        
        # 初始状态只显示开包按钮
        self.open_again_button.rect.y = -1000  # 隐藏
        self.view_collection_button.rect.y = -1000  # 隐藏
    
    def handle_event(self, event):
        """处理事件"""
        if not self.is_visible:
            return None
        
        # 更新按钮悬停状态
        mouse_pos = pygame.mouse.get_pos()
        for button in self.modern_buttons:
            # 转换为窗口相对坐标
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
            
            for button in self.modern_buttons:
                if button.rect.collidepoint(window_pos):
                    button.trigger_flash()
                    
                    if button == self.close_button:
                        self.close()
                        return "close"
                    elif button == self.open_button and self.animation_state == "idle":
                        self._start_opening_animation()
                        return "open_pack"
                    elif button == self.open_again_button:
                        if self._can_open_another():
                            self._reset_for_new_pack()
                            return "open_another"
                        else:
                            self.message_manager.show_message(
                                "No tienes más oportunidades de este tipo",
                                "warning"
                            )
                    elif button == self.view_collection_button:
                        return "view_collection"
        
        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self.close()
                return "close"
        
        return None
    
    def _can_open_another(self) -> bool:
        """检查是否可以再开一个同类型的包"""
        pack_chances = self.user_data.get('pack_chances', {})
        return pack_chances.get(self.pack_type, 0) > 0
    
    def _reset_for_new_pack(self):
        """重置为开新包状态"""
        self.animation_state = "idle"
        self.animation_timer = 0
        self.opened_cards.clear()
        self.new_cards.clear()
        self.card_reveal_index = 0
        self.pack_scale = 1.0
        self.pack_rotation = 0
        self.sparkle_particles.clear()
        
        # 重置按钮显示
        self.open_button.rect.y = self.window_height - 80
        self.open_again_button.rect.y = -1000
        self.view_collection_button.rect.y = -1000
    
    def _start_opening_animation(self):
        """开始开包动画"""
        if not self._consume_pack_chance():
            self.message_manager.show_message(
                "No tienes oportunidades de este tipo de sobre",
                "error"
            )
            return
        
        self.animation_state = "opening"
        self.animation_timer = 0
        
        # 生成卡片
        self.opened_cards = self._generate_cards()
        
        # 隐藏开包按钮
        self.open_button.rect.y = -1000
        
        print(f"🎴 开始开包: {self.get_pack_name()}, 获得 {len(self.opened_cards)} 张卡")
    
    def _consume_pack_chance(self) -> bool:
        """消耗开包次数"""
        pack_chances = self.user_data.get('pack_chances', {})
        current_count = pack_chances.get(self.pack_type, 0)
        
        if current_count <= 0:
            return False
        
        # 扣除次数
        pack_chances[self.pack_type] = current_count - 1
        self.user_data['pack_chances'] = pack_chances
        
        # 保存到数据库
        if self.database_manager:
            self.database_manager.update_user_data(
                self.user_data['user_id'],
                pack_chances=json.dumps(pack_chances)
            )
        
        return True
    
    def _generate_cards(self) -> List[Dict]:
        """生成卡片"""
        cards = []
        
        # 获取可用卡片池
        if self.card_data_manager:
            card_pool = self.card_data_manager.get_card_pool()
        else:
            # 使用默认卡片池
            card_pool = self._get_default_card_pool()
        
        # 生成保证稀有度的卡片
        guaranteed_rarities = self.pack_config.get('guaranteed', [])
        for rarity in guaranteed_rarities:
            card = self._generate_single_card(card_pool, rarity)
            if card:
                cards.append(card)
        
        # 生成剩余卡片
        remaining_count = self.pack_config['card_count'] - len(cards)
        for _ in range(remaining_count):
            card = self._generate_single_card(card_pool)
            if card:
                cards.append(card)
        
        # 保存新获得的卡片到用户收藏
        self._save_cards_to_collection(cards)
        
        return cards
    
    def _generate_single_card(self, card_pool: List[Dict], force_rarity: str = None) -> Optional[Dict]:
        """生成单张卡片"""
        if not card_pool:
            return None
        
        # 确定稀有度
        if force_rarity:
            rarity = force_rarity
        else:
            rarity = self._roll_rarity()
        
        # 从对应稀有度中随机选择
        rarity_cards = [card for card in card_pool if card.get('rarity', 'common') == rarity]
        if not rarity_cards:
            # 如果没有对应稀有度的卡，从所有卡中选择
            rarity_cards = card_pool
        
        if rarity_cards:
            base_card = random.choice(rarity_cards)
            
            # 创建卡片实例
            card_instance = {
                'id': base_card['id'],
                'name': base_card['name'],
                'rarity': base_card.get('rarity', 'common'),
                'type': base_card.get('type', 'pokemon'),
                'image_url': base_card.get('image_url', ''),
                'hp': base_card.get('hp', 0),
                'attacks': base_card.get('attacks', []),
                'obtained_at': pygame.time.get_ticks(),
                'is_new': True
            }
            
            return card_instance
        
        return None
    
    def _roll_rarity(self) -> str:
        """随机生成稀有度"""
        rand = random.random()
        cumulative = 0
        
        for rarity, rate in self.pack_config['rarity_rates'].items():
            cumulative += rate
            if rand <= cumulative:
                return rarity
        
        # 默认返回最常见的稀有度
        return 'common'
    
    def _get_default_card_pool(self) -> List[Dict]:
        """获取默认卡片池（当没有卡片数据管理器时使用）"""
        return [
            {
                'id': f'pokemon_{i}',
                'name': f'Pokemon {i}',
                'rarity': random.choice(['common', 'uncommon', 'rare', 'epic', 'legendary']),
                'type': 'pokemon',
                'hp': random.randint(30, 200),
                'image_url': f'assets/sprites/pokemon_{i}.png'
            }
            for i in range(1, 151)  # 前150个Pokemon
        ]
    
    def _save_cards_to_collection(self, cards: List[Dict]):
        """保存卡片到用户收藏"""
        if 'card_collection' not in self.user_data:
            self.user_data['card_collection'] = []
        
        # 记录新获得的卡片
        for card in cards:
            # 检查是否是新卡片
            existing_card = next(
                (c for c in self.user_data['card_collection'] if c['id'] == card['id']),
                None
            )
            
            if not existing_card:
                self.new_cards.append(card)
            
            # 添加到收藏（允许重复）
            self.user_data['card_collection'].append(card)
        
        # 保存到数据库
        if self.database_manager:
            self.database_manager.save_user_cards(
                self.user_data['user_id'],
                cards
            )
    
    def update(self, time_delta: float):
        """更新动画状态"""
        if not self.is_visible:
            return
        
        # 更新按钮动画
        for button in self.modern_buttons:
            button.update_animation(time_delta)
        
        # 更新开包动画
        if self.animation_state == "opening":
            self.animation_timer += time_delta
            
            # 卡包震动和缩放
            self.pack_scale = 1.0 + 0.1 * abs(pygame.math.sin(self.animation_timer * 10))
            self.pack_rotation += time_delta * 50
            
            if self.animation_timer >= 2.0:  # 2秒开包动画
                self.animation_state = "revealing"
                self.animation_timer = 0
                self.card_reveal_index = 0
        
        elif self.animation_state == "revealing":
            self.animation_timer += time_delta
            
            # 每0.3秒显示一张卡
            if self.animation_timer >= 0.3 and self.card_reveal_index < len(self.opened_cards):
                self.card_reveal_index += 1
                self.animation_timer = 0
                
                # 添加粒子效果
                self._add_sparkle_particles(self.card_reveal_index - 1)
            
            # 所有卡片显示完毕
            if self.card_reveal_index >= len(self.opened_cards):
                self.animation_state = "completed"
                self._show_completion_buttons()
        
        # 更新粒子效果
        self._update_sparkle_particles(time_delta)
    
    def _add_sparkle_particles(self, card_index: int):
        """添加闪光粒子效果"""
        if card_index < len(self.card_display_rects):
            rect = self.card_display_rects[card_index]
            
            for _ in range(10):
                particle = {
                    'x': rect.centerx + random.randint(-20, 20),
                    'y': rect.centery + random.randint(-20, 20),
                    'vx': random.uniform(-50, 50),
                    'vy': random.uniform(-50, 50),
                    'life': 1.0,
                    'color': (255, 255, 100)
                }
                self.sparkle_particles.append(particle)
    
    def _update_sparkle_particles(self, time_delta: float):
        """更新粒子效果"""
        for particle in self.sparkle_particles[:]:
            particle['x'] += particle['vx'] * time_delta
            particle['y'] += particle['vy'] * time_delta
            particle['life'] -= time_delta * 2
            
            if particle['life'] <= 0:
                self.sparkle_particles.remove(particle)
    
    def _show_completion_buttons(self):
        """显示完成后的按钮"""
        button_y = self.window_height - 80
        
        if self._can_open_another():
            self.open_again_button.rect.y = button_y
        
        self.view_collection_button.rect.y = button_y
        
        # 显示获得的新卡片消息
        if self.new_cards:
            new_count = len(self.new_cards)
            self.message_manager.show_message(
                f"¡Obtuviste {new_count} carta(s) nueva(s)!",
                "success",
                duration=4000
            )
    
    def draw_custom_content(self, screen: pygame.Surface):
        """绘制自定义内容"""
        if not self.is_visible:
            return
        
        # 绘制卡包
        self._draw_pack(screen)
        
        # 绘制卡片
        self._draw_cards(screen)
        
        # 绘制粒子效果
        self._draw_sparkle_particles(screen)
        
        # 绘制按钮
        self._draw_modern_buttons(screen)
    
    def _draw_pack(self, screen: pygame.Surface):
        """绘制卡包"""
        if self.animation_state in ["idle", "opening"]:
            # 创建卡包表面
            pack_size = int(200 * self.pack_scale)
            pack_surface = pygame.Surface((pack_size, pack_size), pygame.SRCALPHA)
            
            # 绘制卡包背景
            pack_color = self._get_pack_color()
            pygame.draw.rect(pack_surface, pack_color, (0, 0, pack_size, pack_size), border_radius=20)
            
            # 绘制卡包装饰
            pygame.draw.rect(pack_surface, (255, 255, 255, 100), 
                           (10, 10, pack_size-20, pack_size//3), border_radius=10)
            
            # 应用旋转
            if self.pack_rotation != 0:
                pack_surface = pygame.transform.rotate(pack_surface, self.pack_rotation)
            
            # 绘制到屏幕
            pack_rect = pack_surface.get_rect(center=(
                self.window.rect.x + self.pack_display_rect.centerx,
                self.window.rect.y + self.pack_display_rect.centery
            ))
            screen.blit(pack_surface, pack_rect)
    
    def _get_pack_color(self) -> tuple:
        """获取卡包颜色"""
        colors = {
            'basic': (100, 150, 255),
            'premium': (255, 150, 100),
            'legendary': (255, 215, 0)
        }
        return colors.get(self.pack_type, (150, 150, 150))
    
    def _draw_cards(self, screen: pygame.Surface):
        """绘制卡片"""
        if self.animation_state in ["revealing", "completed"]:
            for i in range(min(self.card_reveal_index, len(self.opened_cards))):
                card = self.opened_cards[i]
                rect = self.card_display_rects[i]
                
                # 转换为屏幕坐标
                screen_rect = pygame.Rect(
                    self.window.rect.x + rect.x,
                    self.window.rect.y + rect.y,
                    rect.width,
                    rect.height
                )
                
                self._draw_single_card(screen, card, screen_rect)
    
    def _draw_single_card(self, screen: pygame.Surface, card: Dict, rect: pygame.Rect):
        """绘制单张卡片"""
        # 卡片背景
        rarity_color = self._get_rarity_color(card['rarity'])
        
        # 绘制卡片边框
        pygame.draw.rect(screen, rarity_color, rect, width=3, border_radius=10)
        
        # 绘制卡片背景
        card_bg = pygame.Surface((rect.width - 6, rect.height - 6), pygame.SRCALPHA)
        card_bg.fill((240, 240, 240, 220))
        screen.blit(card_bg, (rect.x + 3, rect.y + 3))
        
        # 绘制卡片名称
        name_font = font_manager.get_font_by_size(14)
        name_surface = name_font.render(card['name'], True, (50, 50, 50))
        name_rect = name_surface.get_rect(centerx=rect.centerx, y=rect.y + 10)
        
        # 如果名称太长，缩放
        if name_rect.width > rect.width - 10:
            scale = (rect.width - 10) / name_rect.width
            name_surface = pygame.transform.scale(name_surface, 
                                                 (int(name_rect.width * scale), 
                                                  int(name_rect.height * scale)))
            name_rect = name_surface.get_rect(centerx=rect.centerx, y=rect.y + 10)
        
        screen.blit(name_surface, name_rect)
        
        # 绘制稀有度标识
        rarity_font = font_manager.get_font_by_size(12)
        rarity_surface = rarity_font.render(card['rarity'].title(), True, rarity_color)
        rarity_rect = rarity_surface.get_rect(centerx=rect.centerx, y=rect.bottom - 25)
        screen.blit(rarity_surface, rarity_rect)
        
        # 如果是新卡片，添加"NEW"标识
        if card.get('is_new', False):
            new_surface = rarity_font.render("NEW!", True, (255, 0, 0))
            new_rect = new_surface.get_rect(topright=(rect.right - 5, rect.y + 5))
            screen.blit(new_surface, new_rect)
    
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
    
    def _draw_sparkle_particles(self, screen: pygame.Surface):
        """绘制粒子效果"""
        for particle in self.sparkle_particles:
            if particle['life'] > 0:
                alpha = int(255 * particle['life'])
                color = particle['color'] + (alpha,)
                
                particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color, (2, 2), 2)
                
                screen.blit(particle_surface, (
                    self.window.rect.x + int(particle['x']),
                    self.window.rect.y + int(particle['y'])
                ))
    
    def _draw_modern_buttons(self, screen: pygame.Surface):
        """绘制现代按钮"""
        for button in self.modern_buttons:
            if button.rect.y > 0:  # 只绘制可见的按钮
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
    
    def close(self):
        """关闭窗口"""
        if self.is_visible:
            self.is_visible = False
            if self.window:
                self.window.kill()
            if self.on_close:
                self.on_close()
            print("🚪 关闭开包窗口")
    
    def cleanup(self):
        """清理资源"""
        if self.window:
            self.window.kill()
        self.modern_buttons.clear()
        self.opened_cards.clear()
        self.sparkle_particles.clear()