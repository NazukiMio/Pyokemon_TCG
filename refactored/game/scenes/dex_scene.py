"""
Pokédex 页面 - 高性能优化版本
解决帧率问题，大幅提升渲染性能
"""

import pygame
import math
import os
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum

# 导入数据库管理器
try:
    from game.core.database.database_manager import DatabaseManager
except ImportError:
    # 如果找不到数据库管理器，创建一个模拟版本
    class DatabaseManager:
        def get_user_pokemon_collection(self, user_id): return {}


class PokemonStatus(Enum):
    """Pokemon状态枚举"""
    NOT_CAUGHT = "not_caught"
    CAUGHT = "caught" 
    SHINY = "shiny"


class DexColors:
    """Dex页面配色方案"""
    # 🌌 深空蓝主题
    BACKGROUND = (15, 23, 42)          # #0F172A 深蓝背景
    CARD_BG = (30, 41, 59)             # #1E293B 卡片背景
    CARD_BORDER = (71, 85, 105)        # #475569 卡片边框
    
    # 状态颜色
    PRIMARY = (59, 130, 246)           # #3B82F6 蓝色强调
    SUCCESS = (16, 185, 129)           # #10B981 已捕获绿色
    WARNING = (245, 158, 11)           # #F59E0B Shiny金色
    GRAY = (100, 116, 139)             # #64748B 未捕获灰色
    FAVORITE = (249, 115, 22)          # #F97316 收藏橙色
    
    # 文字颜色
    TEXT_PRIMARY = (248, 250, 252)     # #F8FAFC 主要文字
    TEXT_SECONDARY = (203, 213, 225)   # #CBD5E1 次要文字
    TEXT_MUTED = (148, 163, 184)       # #94A3B8 暗淡文字


class PokemonCard:
    """Pokemon卡片组件 - 性能优化版本"""
    
    def __init__(self, pokemon_id: int, name: str, status: PokemonStatus = PokemonStatus.NOT_CAUGHT):
        self.pokemon_id = pokemon_id
        self.name = name
        self.status = status
        self.is_favorite = False
        
        # 动画属性
        self.hover_scale = 1.0
        self.target_scale = 1.0
        self.glow_alpha = 0
        self.shimmer_offset = 0
        
        # 卡片尺寸
        self.width = 120
        self.height = 140
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        
        # 🚀 性能优化：预渲染静态内容
        self._create_static_surfaces()
        
        # 缓存变量
        self._last_scale = 1.0
        self._cached_surface = None
        self._cache_dirty = True
    
    def _create_static_surfaces(self):
        """预创建静态表面以提高性能"""
        # 创建基础Pokemon图像
        self.base_image = pygame.Surface((60, 60))
        if self.status == PokemonStatus.NOT_CAUGHT:
            self.base_image.fill(DexColors.GRAY)
        else:
            # 根据Pokemon ID生成颜色
            hue = (self.pokemon_id * 137) % 360
            color = self._hsv_to_rgb(hue, 0.7, 0.9)
            self.base_image.fill(color)
        
        # 预渲染文字
        font = pygame.font.Font(None, 20)
        name_font = pygame.font.Font(None, 16)
        
        self.number_text = font.render(f"#{self.pokemon_id:03d}", True, DexColors.TEXT_SECONDARY)
        display_name = self.name[:8] + "..." if len(self.name) > 8 else self.name
        self.name_text = name_font.render(display_name, True, DexColors.TEXT_PRIMARY)
    
    def _hsv_to_rgb(self, h, s, v):
        """HSV转RGB颜色"""
        h = h / 360.0
        c = v * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = v - c
        
        if h < 1/6:
            r, g, b = c, x, 0
        elif h < 2/6:
            r, g, b = x, c, 0
        elif h < 3/6:
            r, g, b = 0, c, x
        elif h < 4/6:
            r, g, b = 0, x, c
        elif h < 5/6:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))
    
    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        """更新卡片动画"""
        # 检查鼠标悬停
        is_hovered = self.rect.collidepoint(mouse_pos)
        self.target_scale = 1.08 if is_hovered else 1.0
        
        # 平滑缩放动画
        scale_diff = self.target_scale - self.hover_scale
        self.hover_scale += scale_diff * dt * 10
        
        # 检查缓存是否需要更新
        if abs(self.hover_scale - self._last_scale) > 0.01:
            self._cache_dirty = True
            self._last_scale = self.hover_scale
        
        # Shiny闪烁效果（减少计算频率）
        if self.status == PokemonStatus.SHINY:
            self.shimmer_offset += dt * 2
            if self.shimmer_offset > math.pi * 2:
                self.shimmer_offset -= math.pi * 2
            self.glow_alpha = (math.sin(self.shimmer_offset) + 1) * 0.2 + 0.3
    
    def draw(self, screen: pygame.Surface, x: int, y: int):
        """绘制Pokemon卡片 - 优化版本"""
        self.rect.x = x
        self.rect.y = y
        
        # 🚀 性能优化：只有在需要时才重新渲染
        if self._cache_dirty or self._cached_surface is None:
            self._cached_surface = self._render_card()
            self._cache_dirty = False
        
        # 计算绘制位置
        scaled_width = int(self.width * self.hover_scale)
        scaled_height = int(self.height * self.hover_scale)
        scaled_x = x + (self.width - scaled_width) // 2
        scaled_y = y + (self.height - scaled_height) // 2
        
        # 绘制阴影（只在悬停时）
        if self.hover_scale > 1.02:
            shadow_size = 8
            shadow_surf = pygame.Surface((scaled_width + shadow_size, scaled_height + shadow_size))
            shadow_surf.set_alpha(30)
            shadow_surf.fill((0, 0, 0))
            screen.blit(shadow_surf, (scaled_x - shadow_size//2, scaled_y + shadow_size//2))
        
        # 缩放并绘制缓存的卡片
        if self.hover_scale != 1.0:
            scaled_card = pygame.transform.scale(self._cached_surface, (scaled_width, scaled_height))
            screen.blit(scaled_card, (scaled_x, scaled_y))
        else:
            screen.blit(self._cached_surface, (x, y))
    
    def _render_card(self):
        """渲染卡片到缓存表面"""
        card_surf = pygame.Surface((self.width, self.height))
        
        # 绘制卡片背景
        if self.status == PokemonStatus.SHINY:
            # 简化的Shiny背景效果
            card_surf.fill(DexColors.CARD_BG)
            overlay = pygame.Surface((self.width, self.height))
            overlay.fill(DexColors.WARNING)
            overlay.set_alpha(int(self.glow_alpha * 80))
            card_surf.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
        else:
            card_surf.fill(DexColors.CARD_BG)
        
        # 绘制边框
        border_color = (DexColors.SUCCESS if self.status == PokemonStatus.CAUGHT else 
                       DexColors.WARNING if self.status == PokemonStatus.SHINY else 
                       DexColors.GRAY)
        pygame.draw.rect(card_surf, border_color, card_surf.get_rect(), 2)
        
        # 绘制Pokemon图像
        img_x = (self.width - 60) // 2
        img_y = 10
        
        if self.status == PokemonStatus.NOT_CAUGHT:
            # 未捕获：半透明灰色图像
            silhouette = self.base_image.copy()
            silhouette.set_alpha(100)
            card_surf.blit(silhouette, (img_x, img_y))
        else:
            # 已捕获：显示彩色图像
            card_surf.blit(self.base_image, (img_x, img_y))
        
        # 绘制预渲染的文字
        text_x = (self.width - self.number_text.get_width()) // 2
        card_surf.blit(self.number_text, (text_x, img_y + 65))
        
        name_x = (self.width - self.name_text.get_width()) // 2
        card_surf.blit(self.name_text, (name_x, img_y + 85))
        
        # 绘制状态图标
        self._draw_status_icons(card_surf)
        
        return card_surf
    
    def _draw_status_icons(self, surface: pygame.Surface):
        """绘制状态图标"""
        # Shiny图标
        if self.status == PokemonStatus.SHINY:
            pygame.draw.circle(surface, DexColors.WARNING, (self.width - 20, 15), 6)
        
        # 收藏图标
        if self.is_favorite:
            pygame.draw.circle(surface, DexColors.FAVORITE, (15, 15), 6)
            
        # 已捕获状态指示器
        if self.status in [PokemonStatus.CAUGHT, PokemonStatus.SHINY]:
            pygame.draw.circle(surface, DexColors.SUCCESS, (self.width - 15, self.height - 15), 4)


class SearchBar:
    """搜索栏组件 - 优化版本"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.is_focused = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
        # 🚀 预渲染静态元素
        self._create_static_surfaces()
    
    def _create_static_surfaces(self):
        """预创建静态表面"""
        # 搜索图标
        self.search_icon = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(self.search_icon, DexColors.TEXT_MUTED, (10, 10), 6, 2)
        pygame.draw.line(self.search_icon, DexColors.TEXT_MUTED, (14, 14), (18, 18), 2)
        
        # 占位符文字
        font = pygame.font.Font(None, 24)
        self.placeholder_text = font.render("Buscar Pokémon...", True, DexColors.TEXT_MUTED)
    
    def handle_event(self, event):
        """处理搜索栏事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.is_focused = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.is_focused:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isprintable():
                self.text += event.unicode
    
    def update(self, dt: float):
        """更新搜索栏"""
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen: pygame.Surface):
        """绘制搜索栏"""
        # 背景
        color = DexColors.PRIMARY if self.is_focused else DexColors.CARD_BG
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, DexColors.CARD_BORDER, self.rect, 2, border_radius=8)
        
        # 搜索图标
        screen.blit(self.search_icon, (self.rect.x + 5, self.rect.y + 10))
        
        # 文本
        text_x = self.rect.x + 30
        text_y = self.rect.y + 10
        
        if self.text:
            font = pygame.font.Font(None, 24)
            text_surf = font.render(self.text, True, DexColors.TEXT_PRIMARY)
            screen.blit(text_surf, (text_x, text_y))
            
            # 光标
            if self.is_focused and self.cursor_visible:
                cursor_x = text_x + text_surf.get_width() + 2
                pygame.draw.line(screen, DexColors.TEXT_PRIMARY, 
                               (cursor_x, text_y), (cursor_x, text_y + 20), 2)
        else:
            screen.blit(self.placeholder_text, (text_x, text_y))


class FilterChip:
    """过滤标签组件 - 优化版本"""
    
    def __init__(self, text: str, icon: str, filter_type: str):
        self.text = text
        self.icon = icon
        self.filter_type = filter_type
        self.is_active = False
        self.rect = pygame.Rect(0, 0, 0, 30)
        
        # 🚀 预渲染文字
        font = pygame.font.Font(None, 20)
        self.text_surface = font.render(f"{icon} {text}", True, DexColors.TEXT_PRIMARY)
        self.rect.width = self.text_surface.get_width() + 20
        
    def draw(self, screen: pygame.Surface, x: int, y: int):
        """绘制过滤标签"""
        self.rect.x = x
        self.rect.y = y
        
        # 绘制背景
        color = DexColors.PRIMARY if self.is_active else DexColors.CARD_BG
        pygame.draw.rect(screen, color, self.rect, border_radius=15)
        
        # 绘制预渲染的文本
        text_x = x + 10
        text_y = y + (self.rect.height - self.text_surface.get_height()) // 2
        screen.blit(self.text_surface, (text_x, text_y))


class DexScene:
    """Pokédex主场景 - 高性能版本"""
    
    def __init__(self, screen_width: int, screen_height: int, db_manager: DatabaseManager = None):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.db_manager = db_manager or DatabaseManager()
        
        # 滚动相关
        self.scroll_y = 0
        self.target_scroll = 0
        self.max_scroll = 0
        
        # 数据
        self.pokemon_cards: List[PokemonCard] = []
        self.filtered_cards: List[PokemonCard] = []
        self.user_collection = {}
        
        # UI组件
        self.search_bar = SearchBar(50, 120, 300, 40)
        self.filter_chips = [
            FilterChip("Capturados", "🟢", "caught"),
            FilterChip("Faltantes", "⚫", "missing"),
            FilterChip("Shiny", "💎", "shiny"),
            FilterChip("Favoritos", "⭐", "favorite"),
        ]
        self.active_filters: Set[str] = set()
        
        # 统计数据
        self.total_pokemon = 1010
        self.caught_count = 0
        self.shiny_count = 0
        self.favorite_count = 0
        
        # 布局配置
        self.cards_per_row = 6
        self.card_spacing = 20
        self.content_start_y = 200
        
        # 🚀 性能优化：预渲染静态内容
        self._create_static_surfaces()
        
        # 初始化数据
        self._initialize_pokemon_data()
        self._update_statistics()
        self._filter_pokemon()
        
        print(f"🔍 Pokédex场景初始化完成 - {len(self.pokemon_cards)} Pokémon")
    
    def _create_static_surfaces(self):
        """预创建静态表面以提高性能"""
        # 🚀 预渲染背景（性能关键优化！）
        self.background_surface = pygame.Surface((self.screen_width, self.screen_height))
        
        # 创建简单的渐变背景，避免每帧重绘
        for y in range(self.screen_height):
            alpha = y / self.screen_height * 0.3
            color = tuple(max(0, int(DexColors.BACKGROUND[i] * (1 - alpha))) for i in range(3))
            pygame.draw.line(self.background_surface, color, (0, y), (self.screen_width, y))
        
        # 预渲染头部背景
        self.header_surface = pygame.Surface((self.screen_width, 80), pygame.SRCALPHA)
        self.header_surface.set_alpha(220)
        self.header_surface.fill(DexColors.CARD_BG)
        
        # 预渲染静态文字
        self._prerender_static_texts()
    
    def _prerender_static_texts(self):
        """预渲染静态文字"""
        # 标题
        title_font = pygame.font.Font(None, 36)
        self.title_text = title_font.render("🔍 Pokédex Nacional", True, DexColors.TEXT_PRIMARY)
        
        # 返回按钮
        back_font = pygame.font.Font(None, 24)
        self.back_text = back_font.render("🔙 Volver", True, DexColors.TEXT_PRIMARY)
        
        # 清空过滤器
        clear_font = pygame.font.Font(None, 20)
        self.clear_text = clear_font.render("✖ Limpiar", True, DexColors.TEXT_MUTED)
    
    def _initialize_pokemon_data(self):
        """初始化Pokemon数据"""
        # 模拟Pokemon数据
        pokemon_names = [
            "Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard",
            "Squirtle", "Wartortle", "Blastoise", "Caterpie", "Metapod", "Butterfree",
            "Weedle", "Kakuna", "Beedrill", "Pidgey", "Pidgeotto", "Pidgeot",
            "Rattata", "Raticate", "Spearow", "Fearow", "Ekans", "Arbok",
            "Pikachu", "Raichu", "Sandshrew", "Sandslash", "Nidoran♀", "Nidorina",
            "Nidoqueen", "Nidoran♂", "Nidorino", "Nidoking", "Clefairy", "Clefable",
            "Vulpix", "Ninetales", "Jigglypuff", "Wigglytuff", "Zubat", "Golbat",
            "Oddish", "Gloom", "Vileplume", "Paras", "Parasect", "Venonat",
            "Venomoth", "Diglett", "Dugtrio", "Meowth", "Persian", "Psyduck"
        ]
        
        # 加载用户收集数据
        try:
            self.user_collection = self.db_manager.get_user_pokemon_collection(1) or {}
        except:
            self.user_collection = {}
        
        # 创建Pokemon卡片
        for i, name in enumerate(pokemon_names, 1):
            if i in self.user_collection:
                status = PokemonStatus.SHINY if self.user_collection[i].get('is_shiny') else PokemonStatus.CAUGHT
            else:
                # 模拟一些已捕获的Pokemon
                if i <= 20 and i % 3 == 0:
                    status = PokemonStatus.CAUGHT
                elif i <= 10 and i % 5 == 0:
                    status = PokemonStatus.SHINY
                else:
                    status = PokemonStatus.NOT_CAUGHT
            
            card = PokemonCard(i, name, status)
            if i % 7 == 0 and status != PokemonStatus.NOT_CAUGHT:
                card.is_favorite = True
            
            self.pokemon_cards.append(card)
        
        # 填充到1010个Pokemon（使用占位符）
        for i in range(len(pokemon_names) + 1, self.total_pokemon + 1):
            card = PokemonCard(i, f"Pokemon{i}", PokemonStatus.NOT_CAUGHT)
            self.pokemon_cards.append(card)
    
    def _update_statistics(self):
        """更新统计数据"""
        self.caught_count = sum(1 for card in self.pokemon_cards 
                               if card.status in [PokemonStatus.CAUGHT, PokemonStatus.SHINY])
        self.shiny_count = sum(1 for card in self.pokemon_cards 
                              if card.status == PokemonStatus.SHINY)
        self.favorite_count = sum(1 for card in self.pokemon_cards if card.is_favorite)
    
    def _filter_pokemon(self):
        """根据搜索和过滤条件筛选Pokemon"""
        self.filtered_cards = []
        
        for card in self.pokemon_cards:
            # 搜索过滤
            if self.search_bar.text:
                search_text = self.search_bar.text.lower()
                if (search_text not in card.name.lower() and 
                    search_text not in f"{card.pokemon_id:03d}"):
                    continue
            
            # 状态过滤
            if self.active_filters:
                if "caught" in self.active_filters and card.status == PokemonStatus.NOT_CAUGHT:
                    continue
                if "missing" in self.active_filters and card.status != PokemonStatus.NOT_CAUGHT:
                    continue
                if "shiny" in self.active_filters and card.status != PokemonStatus.SHINY:
                    continue
                if "favorite" in self.active_filters and not card.is_favorite:
                    continue
            
            self.filtered_cards.append(card)
        
        # 更新最大滚动距离
        rows = (len(self.filtered_cards) + self.cards_per_row - 1) // self.cards_per_row
        content_height = rows * (140 + self.card_spacing) + 100
        self.max_scroll = max(0, content_height - (self.screen_height - self.content_start_y))
    
    def handle_event(self, event) -> Optional[str]:
        """处理事件"""
        # 搜索栏事件
        old_text = self.search_bar.text
        self.search_bar.handle_event(event)
        if self.search_bar.text != old_text:
            self._filter_pokemon()
        
        # 鼠标滚轮事件
        if event.type == pygame.MOUSEWHEEL:
            self.target_scroll -= event.y * 60
            self.target_scroll = max(0, min(self.target_scroll, self.max_scroll))
        
        # 过滤标签点击
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            
            # 检查过滤标签点击
            chip_x = 400
            for chip in self.filter_chips:
                chip_rect = pygame.Rect(chip_x, 130, chip.rect.width, chip.rect.height)
                if chip_rect.collidepoint(mouse_x, mouse_y):
                    if chip.filter_type in self.active_filters:
                        self.active_filters.remove(chip.filter_type)
                        chip.is_active = False
                    else:
                        self.active_filters.add(chip.filter_type)
                        chip.is_active = True
                    self._filter_pokemon()
                    break
                chip_x += chip.rect.width + 10
            
            # 返回按钮点击检测
            if pygame.Rect(20, 20, 100, 40).collidepoint(mouse_x, mouse_y):
                return "back_to_home"
        
        # 键盘事件
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back_to_home"
        
        return None
    
    def update(self, dt: float):
        """更新场景"""
        # 更新搜索栏
        self.search_bar.update(dt)
        
        # 平滑滚动
        scroll_diff = self.target_scroll - self.scroll_y
        self.scroll_y += scroll_diff * dt * 12
        
        # 🚀 只更新可见区域的卡片
        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_y = mouse_pos[1] + self.scroll_y - self.content_start_y
        adjusted_mouse_pos = (mouse_pos[0], adjusted_mouse_y)
        
        # 计算可见范围
        visible_start = max(0, int(self.scroll_y // (140 + self.card_spacing)) * self.cards_per_row - self.cards_per_row)
        visible_end = min(len(self.filtered_cards), visible_start + (self.cards_per_row * 10))
        
        # 只更新可见卡片
        for i in range(visible_start, visible_end):
            if i < len(self.filtered_cards):
                self.filtered_cards[i].update(dt, adjusted_mouse_pos)
    
    def draw(self, screen: pygame.Surface):
        """绘制场景 - 高性能版本"""
        # 🚀 绘制预渲染的背景
        screen.blit(self.background_surface, (0, 0))
        
        # 绘制固定头部
        self._draw_header(screen)
        
        # 绘制搜索栏和过滤器
        self._draw_search_and_filters(screen)
        
        # 绘制统计信息（缓存渲染）
        self._draw_statistics(screen)
        
        # 绘制Pokemon卡片（虚拟滚动）
        self._draw_pokemon_grid(screen)
        
        # 绘制滚动条
        if self.max_scroll > 0:
            self._draw_scrollbar(screen)
    
    def _draw_header(self, screen: pygame.Surface):
        """绘制固定头部"""
        # 绘制预渲染的头部背景
        screen.blit(self.header_surface, (0, 0))
        
        # 返回按钮
        back_button = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(screen, DexColors.PRIMARY, back_button, border_radius=8)
        text_x = back_button.x + (back_button.width - self.back_text.get_width()) // 2
        text_y = back_button.y + (back_button.height - self.back_text.get_height()) // 2
        screen.blit(self.back_text, (text_x, text_y))
        
        # 标题
        title_x = (self.screen_width - self.title_text.get_width()) // 2
        screen.blit(self.title_text, (title_x, 25))
        
        # 总体进度（动态渲染，因为会变化）
        progress_text = f"📊 {self.caught_count}/{self.total_pokemon} ({self.caught_count/self.total_pokemon*100:.1f}%)"
        progress_font = pygame.font.Font(None, 24)
        progress_surf = progress_font.render(progress_text, True, DexColors.TEXT_SECONDARY)
        progress_x = self.screen_width - progress_surf.get_width() - 20
        screen.blit(progress_surf, (progress_x, 30))
    
    def _draw_search_and_filters(self, screen: pygame.Surface):
        """绘制搜索栏和过滤器"""
        # 搜索栏
        self.search_bar.draw(screen)
        
        # 过滤标签
        chip_x = 400
        for chip in self.filter_chips:
            chip.draw(screen, chip_x, 130)
            chip_x += chip.rect.width + 10
        
        # 清空过滤器按钮
        if self.active_filters:
            clear_x = chip_x + 20
            clear_rect = pygame.Rect(clear_x, 130, self.clear_text.get_width() + 10, 30)
            
            mouse_pos = pygame.mouse.get_pos()
            if clear_rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, DexColors.GRAY, clear_rect, border_radius=15)
                if pygame.mouse.get_pressed()[0]:
                    self.active_filters.clear()
                    for chip in self.filter_chips:
                        chip.is_active = False
                    self._filter_pokemon()
            
            screen.blit(self.clear_text, (clear_x + 5, 135))
    
    def _draw_statistics(self, screen: pygame.Surface):
        """绘制统计信息"""
        stats_y = 175
        font = pygame.font.Font(None, 20)
        
        stats = [
            f"💎 {self.shiny_count} Shiny",
            f"🏆 {self.caught_count} Capturados", 
            f"⭐ {self.favorite_count} Favoritos",
            f"📋 {len(self.filtered_cards)} Mostrados"
        ]
        
        stat_x = 50
        for stat in stats:
            stat_surf = font.render(stat, True, DexColors.TEXT_SECONDARY)
            screen.blit(stat_surf, (stat_x, stats_y))
            stat_x += stat_surf.get_width() + 40
    
    def _draw_pokemon_grid(self, screen: pygame.Surface):
        """绘制Pokemon卡片网格 - 优化版虚拟滚动"""
        # 🚀 计算精确的可见范围
        visible_start_row = max(0, int((self.scroll_y - 100) // (140 + self.card_spacing)))
        visible_end_row = min(
            (len(self.filtered_cards) + self.cards_per_row - 1) // self.cards_per_row,
            int((self.scroll_y + self.screen_height) // (140 + self.card_spacing)) + 1
        )
        
        visible_start = visible_start_row * self.cards_per_row
        visible_end = min(len(self.filtered_cards), (visible_end_row + 1) * self.cards_per_row)
        
        # 🚀 只绘制可见的Pokemon卡片
        for i in range(visible_start, visible_end):
            if i >= len(self.filtered_cards):
                break
                
            card = self.filtered_cards[i]
            
            row = i // self.cards_per_row
            col = i % self.cards_per_row
            
            # 计算卡片位置
            card_x = 50 + col * (card.width + self.card_spacing)
            card_y = self.content_start_y + row * (card.height + self.card_spacing) - self.scroll_y
            
            # 剪切检查
            if card_y < self.screen_height and card_y + card.height > self.content_start_y:
                card.draw(screen, card_x, card_y)
    
    def _draw_scrollbar(self, screen: pygame.Surface):
        """绘制滚动条"""
        scrollbar_x = self.screen_width - 15
        scrollbar_y = self.content_start_y
        scrollbar_height = self.screen_height - self.content_start_y
        
        # 滚动条背景
        pygame.draw.rect(screen, DexColors.CARD_BG, 
                       (scrollbar_x, scrollbar_y, 10, scrollbar_height))
        
        # 滚动条滑块
        thumb_height = max(20, int(scrollbar_height * scrollbar_height / (scrollbar_height + self.max_scroll)))
        thumb_y = scrollbar_y + int(self.scroll_y / self.max_scroll * (scrollbar_height - thumb_height))
        
        pygame.draw.rect(screen, DexColors.PRIMARY, 
                       (scrollbar_x, thumb_y, 10, thumb_height), border_radius=5)
    
    def get_scene_name(self) -> str:
        """获取场景名称"""
        return "dex"
    
    def cleanup(self):
        """清理资源"""
        print("🔍 Pokédex场景清理完成")


# 使用示例
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Pokédex Demo - Optimized")
    clock = pygame.time.Clock()
    
    dex_scene = DexScene(1200, 800)
    running = True
    
    print("🚀 高性能版本启动 - 预期60FPS")
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            result = dex_scene.handle_event(event)
            if result == "back_to_home":
                print("返回主页")
        
        dex_scene.update(dt)
        dex_scene.draw(screen)
        pygame.display.flip()
    
    pygame.quit()