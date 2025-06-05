import pygame
import math
import random
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
# from game.core.game_manager import GameManager

# 假设Theme在相对路径导入，你需要根据实际路径调整
try:
    from game.scenes.styles.theme import Theme
    from game.scenes.components.button_component import ModernButton
    print("✅ Theme导入成功")
except ImportError:
    # 备用Theme（测试用）
    class Theme:
        COLORS = {
            'glass_bg': (255, 255, 255, 217),
            'glass_bg_hover': (255, 255, 255, 235),
            'glass_border': (255, 255, 255, 76),
            'glass_border_hover': (255, 255, 255, 102),
            'accent': (88, 101, 242),
            'accent_hover': (67, 78, 216),
            'text': (55, 65, 81),
            'text_white': (255, 255, 255),
            'shadow': (0, 0, 0, 38),
            'shadow_light': (0, 0, 0, 25),
            'highlight': (255, 255, 255, 80),
            'highlight_strong': (255, 255, 255, 120),
        }
        SIZES = {
            'border_radius_large': 16,
            'border_radius_xl': 20,
            'shadow_blur': 4,
            'shadow_offset': 2,
            'spacing_lg': 24,
            'spacing_xl': 32,
        }
        @classmethod
        def get_color(cls, name): return cls.COLORS.get(name, (255,255,255))
        @classmethod
        def get_size(cls, name): return cls.SIZES.get(name, 0)
    
    class ModernButton:
        def __init__(self, rect, text, **kwargs): 
            self.rect = rect
            self.text = text
        def update_hover(self, pos): return False
        def update_animation(self, dt): pass
        def draw(self, screen, **kwargs): 
            pygame.draw.rect(screen, (100,100,100), self.rect)
        def is_clicked(self, pos, btn): return self.rect.collidepoint(pos)
    
    print("⚠️ 使用备用Theme，请检查导入路径")

class PackQuality(Enum):
    BASIC = "basic"
    PREMIUM = "premium" 
    LEGENDARY = "legendary"

class AnimationState(Enum):
    SELECTION = "selection"
    IDLE = "idle"
    OPENING = "opening"
    REVEALING = "revealing"
    COMPLETED = "completed"

@dataclass
class CardResult:
    id: str
    name: str
    rarity: str
    image_path: str
    hp: Optional[int] = None
    types: Optional[List[str]] = None

class GlassEffect:
    """高性能特效管理器"""
    
    @staticmethod
    def draw_dark_overlay(screen: pygame.Surface, alpha: int = 150):
        """绘制深色半透明遮罩（高性能版本）"""
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
    
    @staticmethod
    def draw_glass_rect(screen: pygame.Surface, rect: pygame.Rect, 
                       alpha: int = 217, border_alpha: int = 76, radius: int = 16):
        """绘制毛玻璃矩形"""
        # 主体毛玻璃背景
        glass_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glass_surface, (255, 255, 255, alpha),
                        (0, 0, rect.width, rect.height), border_radius=radius)
        screen.blit(glass_surface, rect.topleft)
        
        # 毛玻璃边框
        border_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, (255, 255, 255, border_alpha),
                        (0, 0, rect.width, rect.height), width=2, border_radius=radius)
        screen.blit(border_surface, rect.topleft)

class PackOpeningWindow:
    def __init__(self, screen_width: int, screen_height: int, game_manager):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.game_manager = game_manager
        
        # 窗口状态
        self.is_visible = False
        self.animation_state = AnimationState.SELECTION
        self.current_pack_quality = PackQuality.BASIC
        self.selected_pack_index = 0
        
        # 可用的卡包品质
        self.available_packs = [PackQuality.BASIC, PackQuality.PREMIUM, PackQuality.LEGENDARY]
        
        # 动画时间控制
        self.animation_timer = 0.0
        self.selection_bounce_timer = 0.0
        self.glass_animation_timer = 0.0
        
        # 资源管理
        self.textures = {}
        self.pack_images = {}
        self.packet_images = []  # 存储所有packet图片
        self.current_packet_image = None 
        self.obtained_cards = []
        
        # 动画效果参数
        self.circle_rotation = 0.0
        self.circle_breath_scale = 1.0
        self.pack_bounce_offset = 0.0

        # 窗口出现动画参数
        self.entrance_animation_timer = 0.0
        self.entrance_duration = 0.8  # 入场动画持续时间
        self.overlay_alpha = 0.0      # 遮罩透明度
        self.ui_alpha = 0.0          # UI按钮透明度
        self.content_offset_y = 100   # 内容向上偏移量
        
        # 现代UI组件 - 全屏布局
        self._create_ui_components()
        
        # 交互区域
        self.pack_click_rect = pygame.Rect(0, 0, 300, 300)
        
        # 状态控制
        self.can_close = True
        self.can_interact = True
        
        self._load_assets()
        self._setup_quality_configs()

    def _create_ui_components(self):
        """创建全屏布局的UI组件"""
        # 关闭按钮 - 右上角
        close_size = 50
        self.close_button = ModernButton(
            pygame.Rect(self.screen_width - close_size - 30, 30, close_size, close_size),
            "✕",
            button_type="secondary"
        )
        
        # 左右切换按钮 - 屏幕边缘
        arrow_size = 70
        arrow_y = self.screen_height // 2 - arrow_size // 2
        
        self.left_arrow_button = ModernButton(
            pygame.Rect(50, arrow_y, arrow_size, arrow_size),
            "‹",
            button_type="secondary"
        )
        
        self.right_arrow_button = ModernButton(
            pygame.Rect(self.screen_width - arrow_size - 50, arrow_y, arrow_size, arrow_size),
            "›", 
            button_type="secondary"
        )

    def _load_assets(self):
        """加载UI资源"""
        try:
            # UI图标
            ui_icons = ["close", "gem", "gold_coin"]
            for icon in ui_icons:
                path = f"assets/icons/ui/{icon}.png"
                self.textures[icon] = pygame.image.load(path).convert_alpha()
            
            # Circle特效
            circle_effects = ["blue_circle", "purple_circle", "golden_circle"]
            for effect in circle_effects:
                path = f"assets/icons/effects/{effect}.png"
                self.textures[effect] = pygame.image.load(path).convert_alpha()
            
            # # 卡包图片
            # for quality in self.available_packs:
            #     try:
            #         pack_path = f"assets/packs/{quality.value}_pack.png"
            #         self.pack_images[quality] = pygame.image.load(pack_path).convert_alpha()
            #     except:
            #         self.pack_images[quality] = self._create_modern_pack_placeholder(quality)

            # 加载随机卡包图片
            self.packet_images = []
            for i in range(1, 11):  # packet1 到 packet10
                try:
                    packet_path = f"assets/images/packets/packet{i}.png"
                    packet_img = pygame.image.load(packet_path).convert_alpha()
                    self.packet_images.append(packet_img)
                except:
                    print(f"⚠️ 无法加载 packet{i}.png")

            self._select_random_packet()
                
            print("✅ 开包界面资源加载完成")
            
        except Exception as e:
            print(f"❌ 资源加载失败: {e}")
            self._create_fallback_textures()

    def _select_random_packet(self):
        """随机选择一个卡包图片"""
        if self.packet_images:
            self.current_packet_image = random.choice(self.packet_images)
        else:
            # 备用：创建占位符
            self.current_packet_image = self._create_modern_pack_placeholder(self.current_pack_quality)

    def _create_modern_pack_placeholder(self, quality: PackQuality) -> pygame.Surface:
        """创建现代风格卡包占位符"""
        size = 300
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 品质对应的颜色
        colors = {
            PackQuality.BASIC: Theme.get_color('accent'),
            PackQuality.PREMIUM: (138, 43, 226),  # 紫色
            PackQuality.LEGENDARY: (255, 215, 0)  # 金色
        }
        
        color = colors.get(quality, Theme.get_color('accent'))
        
        # 绘制现代风格卡包
        # 主体渐变背景
        for i in range(size):
            alpha = int(200 * (1 - i / size * 0.3))
            line_color = color + (alpha,)
            pygame.draw.line(surface, line_color, (i, 0), (i, size))
        
        # 圆角遮罩
        mask = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255),
                        (0, 0, size, size), border_radius=Theme.get_size('border_radius_xl'))
        
        final_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        final_surface.blit(surface, (0, 0))
        final_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        # 高光效果
        highlight = pygame.Surface((size, size // 3), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 60))
        final_surface.blit(highlight, (0, 0))
        
        # 品质文字
        font = pygame.font.Font(None, 36)
        text = font.render(quality.value.upper(), True, (255, 255, 255))
        text_rect = text.get_rect(center=(size // 2, size // 2))
        final_surface.blit(text, text_rect)
        
        return final_surface

    def _create_fallback_textures(self):
        """创建备用特效纹理"""
        for name, color in [
            ("blue_circle", (100, 150, 255)),
            ("purple_circle", (180, 100, 255)),
            ("golden_circle", (255, 215, 0))
        ]:
            surface = pygame.Surface((300, 300), pygame.SRCALPHA)
            # 现代风格圆形
            pygame.draw.circle(surface, color + (120,), (150, 150), 140)
            pygame.draw.circle(surface, (255, 255, 255, 60), (150, 150), 140, 4)
            self.textures[name] = surface

    def _setup_quality_configs(self):
        """配置不同品质的视觉效果"""
        self.quality_configs = {
            PackQuality.BASIC: {
                "circle_texture": "blue_circle",
                "circle_color": Theme.get_color('accent'),
                "rotation_speed": 15,
                "breath_speed": 1.2,
                "breath_amplitude": 0.08,
                "bounce_height": 8,
                "glow_color": (100, 150, 255, 100)
            },
            PackQuality.PREMIUM: {
                "circle_texture": "purple_circle", 
                "circle_color": (138, 43, 226),
                "rotation_speed": 25,
                "breath_speed": 1.8,
                "breath_amplitude": 0.12,
                "bounce_height": 12,
                "glow_color": (180, 100, 255, 120)
            },
            PackQuality.LEGENDARY: {
                "circle_texture": "golden_circle",
                "circle_color": (255, 215, 0),
                "rotation_speed": 35,
                "breath_speed": 2.2,
                "breath_amplitude": 0.16,
                "bounce_height": 16,
                "glow_color": (255, 215, 0, 140)
            }
        }

    def show(self):
        """显示全屏开包界面"""
        print("📦 显示全屏开包界面")
        self.is_visible = True
        self.animation_state = AnimationState.SELECTION
        self.animation_timer = 0.0
        self.glass_animation_timer = 0.0
        self.selection_bounce_timer = 0.0
        self.can_interact = True
        self.can_close = True

        # 重置入场动画
        self.entrance_animation_timer = 0.0
        self.overlay_alpha = 0.0
        self.ui_alpha = 0.0
        self.content_offset_y = 100

        # 随机选择一个卡包图片
        self._select_random_packet()

    def start_pack_opening(self):
        """开始开包流程"""
        if not self.can_interact:
            return False
            
        current_quality = self.available_packs[self.selected_pack_index]
        print(f"🎴 开始开包: {current_quality.value}")
        
        # 调用后端开包逻辑
        result = self.game_manager.open_pack_complete_flow(current_quality.value)
        
        if not result.get("success", False):
            error_msg = result.get("error", "unknown_error")
            print(f"❌ 开包失败: {error_msg}")
            self._show_error_message(error_msg)
            return False
        
        # 转换卡牌数据格式
        raw_cards = result.get("cards", [])
        self.obtained_cards = []
        for card_data in raw_cards:
            self.obtained_cards.append(CardResult(
                id=card_data.get("id", ""),
                name=card_data.get("name", "Unknown"),
                rarity=card_data.get("rarity", "Common"),
                image_path=card_data.get("image", ""),
                hp=card_data.get("hp"),
                types=card_data.get("types", [])
            ))
        
        print(f"🎊 获得 {len(self.obtained_cards)} 张卡牌")
        
        # 开始开包动画
        self.animation_state = AnimationState.IDLE
        self.animation_timer = 0.0
        self.can_interact = False
        self.can_close = False
        
        return True

    def _show_error_message(self, error_type: str):
        """显示错误信息（西班牙语）"""
        error_messages = {
            "insufficient_packs": "Paquetes insuficientes",
            "deduct_pack_failed": "Error al descontar paquete", 
            "transaction_failed": "Transacción fallida, intenta de nuevo"
        }
        message = error_messages.get(error_type, "Error desconocido")
        print(f"💢 Error: {message}")

    def switch_pack_left(self):
        """切换到左边的卡包"""
        if not self.can_interact or self.animation_state != AnimationState.SELECTION:
            return
            
        self.selected_pack_index = (self.selected_pack_index - 1) % len(self.available_packs)
        self.current_pack_quality = self.available_packs[self.selected_pack_index]
        self.selection_bounce_timer = 0.0
        self._select_random_packet() 
        print(f"🔄 切换到: {self.current_pack_quality.value}")

    def switch_pack_right(self):
        """切换到右边的卡包"""
        if not self.can_interact or self.animation_state != AnimationState.SELECTION:
            return
            
        self.selected_pack_index = (self.selected_pack_index + 1) % len(self.available_packs)
        self.current_pack_quality = self.available_packs[self.selected_pack_index]
        self.selection_bounce_timer = 0.0
        self._select_random_packet() 
        print(f"🔄 切换到: {self.current_pack_quality.value}")

    def update(self, dt: float):
        """更新动画和逻辑"""
        # 处理入场动画
        if self.entrance_animation_timer < self.entrance_duration:
            progress = self.entrance_animation_timer / self.entrance_duration
            # 缓动函数
            eased_progress = 1 - (1 - progress) ** 3
            
            self.overlay_alpha = eased_progress * 160
            self.ui_alpha = eased_progress
            self.content_offset_y = (1 - eased_progress) * 100

            self.entrance_animation_timer += dt 

        if not self.is_visible:
            return
        
        # 更新计时器
        self.animation_timer += dt
        self.selection_bounce_timer += dt
        self.glass_animation_timer += dt
        
        # 更新UI组件动画
        mouse_pos = pygame.mouse.get_pos()
        self.close_button.update_hover(mouse_pos)
        self.close_button.update_animation(dt)
        self.left_arrow_button.update_hover(mouse_pos)
        self.left_arrow_button.update_animation(dt)
        self.right_arrow_button.update_hover(mouse_pos)
        self.right_arrow_button.update_animation(dt)
        
        # 更新circle特效
        config = self.quality_configs[self.current_pack_quality]
        self.circle_rotation += config["rotation_speed"] * dt
        if self.circle_rotation >= 360:
            self.circle_rotation -= 360
        
        # 更新circle呼吸效果
        breath_cycle = math.sin(self.glass_animation_timer * config["breath_speed"])
        self.circle_breath_scale = 1.0 + breath_cycle * config["breath_amplitude"]
        
        # 更新卡包弹跳效果
        if self.animation_state == AnimationState.SELECTION:
            bounce_cycle = math.sin(self.selection_bounce_timer * 2.5)
            self.pack_bounce_offset = bounce_cycle * config["bounce_height"]
        
        # 状态机更新
        if self.animation_state == AnimationState.IDLE:
            if self.animation_timer >= 0.8:
                self.animation_state = AnimationState.OPENING
        elif self.animation_state == AnimationState.OPENING:
            if self.animation_timer >= 3.0:
                self.animation_state = AnimationState.REVEALING
        elif self.animation_state == AnimationState.REVEALING:
            if self.animation_timer >= 4.5:
                self.animation_state = AnimationState.COMPLETED
                self.can_close = True
        
        # 更新卡包点击区域 - 居中
        pack_display_height = 500
        pack_display_width = int(pack_display_height * (256 / 492))
        pack_x = self.screen_width // 2 - pack_display_width // 2
        pack_y = self.screen_height // 2 - pack_display_height // 2 - 30 + self.pack_bounce_offset + self.content_offset_y
        self.pack_click_rect = pygame.Rect(pack_x, pack_y, pack_display_width, pack_display_height)

    def handle_event(self, event):
        """处理输入事件"""
        if not self.is_visible:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                
                # 检查UI按钮
                if self.close_button.is_clicked(mouse_pos, 1) and self.can_close:
                    self.close()
                    return True
                
                if self.animation_state == AnimationState.SELECTION:
                    if self.left_arrow_button.is_clicked(mouse_pos, 1):
                        self.switch_pack_left()
                        return True
                    elif self.right_arrow_button.is_clicked(mouse_pos, 1):
                        self.switch_pack_right()
                        return True
                
                # 卡包点击 - 直接开包
                if self.pack_click_rect.collidepoint(mouse_pos):
                    if self.animation_state == AnimationState.SELECTION:
                        self.start_pack_opening()
                    elif self.animation_state == AnimationState.OPENING:
                        self.animation_timer = 3.0  # 加速
                    return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.can_close:
                self.close()
                return True
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.switch_pack_left()
                return True
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.switch_pack_right()
                return True
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                if self.animation_state == AnimationState.SELECTION:
                    self.start_pack_opening()
                return True
        
        return True

    def close(self):
        """关闭开包界面"""
        print("📦 关闭开包界面")
        self.is_visible = False

    def draw(self, screen):
        """绘制全屏沉浸式开包界面"""
        if not self.is_visible:
            return
        
        # 绘制深色半透明背景遮罩
        GlassEffect.draw_dark_overlay(screen, alpha=int(self.overlay_alpha))
        
        # 绘制内容 - 无窗口边框
        self._draw_background_circle(screen)
        self._draw_pack(screen)
        
        if self.animation_state == AnimationState.SELECTION:
            self._draw_selection_ui(screen)
        elif self.animation_state == AnimationState.COMPLETED:
            self._draw_cards(screen)
        
        self._draw_ui_elements(screen)

    def _draw_background_circle(self, screen):
        """绘制背景光圈效果"""
        config = self.quality_configs[self.current_pack_quality]
        circle_texture = self.textures.get(config["circle_texture"])
        
        if circle_texture:
            center_x = self.screen_width // 2
            center_y = self.screen_height // 2 - 30 + self.content_offset_y
            
            # 应用旋转和呼吸效果
            rotated_circle = pygame.transform.rotate(circle_texture, self.circle_rotation)
            scale = self.circle_breath_scale
            scaled_circle = pygame.transform.scale(
                rotated_circle,
                (int(rotated_circle.get_width() * scale),
                 int(rotated_circle.get_height() * scale))
            )
            
            circle_rect = scaled_circle.get_rect(center=(center_x, center_y))
            
            # 添加外层发光效果
            # glow_color = config["glow_color"]
            # glow_surface = pygame.Surface(scaled_circle.get_size(), pygame.SRCALPHA)
            # glow_surface.fill(glow_color)
            # glow_rect = circle_rect.copy()
            # glow_rect.inflate_ip(30, 30)
            # screen.blit(glow_surface, glow_rect)
            
            screen.blit(scaled_circle, circle_rect)

    def _draw_pack(self, screen):
        """绘制卡包（应用原有动画逻辑）"""
        pack_image = self.current_packet_image
        if not pack_image:
            return
        
        # 计算卡包位置 - 保持原始比例 256:492
        pack_display_height = 500  # 设定高度
        pack_display_width = int(pack_display_height * (256 / 492))  # 按比例计算宽度 ≈ 208
        
        pack_x = self.screen_width // 2 - pack_display_width // 2
        pack_y = self.screen_height // 2 - pack_display_height // 2 - 30 + self.content_offset_y
        
        # 根据动画状态绘制效果
        if self.animation_state == AnimationState.SELECTION or self.animation_state == AnimationState.IDLE:
            # 静态显示（带弹跳）
            scaled_pack = pygame.transform.scale(pack_image, (pack_display_width, pack_display_height))
            screen.blit(scaled_pack, (pack_x, pack_y + self.pack_bounce_offset))
        
        elif self.animation_state == AnimationState.OPENING:
            # 开包震动动画
            shake_intensity = min(self.animation_timer / 2.0, 1.0) * 10
            shake_x = random.uniform(-shake_intensity, shake_intensity)
            shake_y = random.uniform(-shake_intensity, shake_intensity)
            
            scale_factor = 1.0 + (self.animation_timer / 2.0) * 0.3
            scaled_width = int(pack_display_width * scale_factor)
            scaled_height = int(pack_display_height * scale_factor)
            
            scaled_pack = pygame.transform.scale(pack_image, (scaled_width, scaled_height))
            screen.blit(scaled_pack, (pack_x + shake_x - (scaled_width - pack_display_width) // 2, 
                                pack_y + shake_y - (scaled_height - pack_display_height) // 2))
        
        elif self.animation_state == AnimationState.REVEALING:
            # 光芒展示动画
            scaled_pack = pygame.transform.scale(pack_image, (pack_display_width, pack_display_height))
            
            # 强化的光芒效果
            glow_alpha = int(200 * abs(math.sin(self.animation_timer * 4)))
            glow_surface = pygame.Surface((pack_display_width + 60, pack_display_height + 60), pygame.SRCALPHA)
            
            # 多层光芒
            for i in range(4):
                layer_alpha = glow_alpha // (i + 1)
                pygame.draw.rect(glow_surface, (255, 255, 255, layer_alpha),
                            (i * 8, i * 8, pack_display_width + 60 - i * 16, pack_display_height + 60 - i * 16),
                            border_radius=Theme.get_size('border_radius_xl'))
            
            screen.blit(glow_surface, (pack_x - 30, pack_y - 30))
            screen.blit(scaled_pack, (pack_x, pack_y))
        
        elif self.animation_state == AnimationState.COMPLETED:
            # 完成状态
            scaled_pack = pygame.transform.scale(pack_image, (pack_display_width, pack_display_height))
            screen.blit(scaled_pack, (pack_x, pack_y))

    def _draw_selection_ui(self, screen):
        """绘制选择阶段的UI"""
        # 绘制品质标题 - 屏幕上方
        quality_names = {
            PackQuality.BASIC: "Paquete Básico",
            PackQuality.PREMIUM: "Paquete Premium", 
            PackQuality.LEGENDARY: "Paquete Legendario"
        }
        
        title = quality_names.get(self.current_pack_quality, "Paquete")
        font = pygame.font.Font(None, 56)
        title_color = self.quality_configs[self.current_pack_quality]["circle_color"]
        title_surface = font.render(title, True, title_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 100 + self.content_offset_y))
        screen.blit(title_surface, title_rect)

    def _draw_cards(self, screen):
        """绘制获得的卡牌（现代风格）"""
        if not self.obtained_cards:
            return
        
        # 计算卡牌布局 - 屏幕下方
        card_width = 120
        card_height = 160
        card_spacing = 25
        total_width = len(self.obtained_cards) * card_width + (len(self.obtained_cards) - 1) * card_spacing
        
        start_x = self.screen_width // 2 - total_width // 2
        start_y = self.screen_height - 220 + self.content_offset_y  # 下方位置
        
        # 稀有度对应的现代边框颜色
        rarity_colors = {
            "Common": (156, 163, 175),      # 灰色
            "Uncommon": (34, 197, 94),      # 绿色
            "Rare": (59, 130, 246),         # 蓝色
            "Epic": (147, 51, 234),         # 紫色
            "Legendary": (245, 158, 11)     # 橙色
        }
        
        # 绘制每张卡牌
        for i, card in enumerate(self.obtained_cards):
            card_x = start_x + i * (card_width + card_spacing)
            card_rect = pygame.Rect(card_x, start_y, card_width, card_height)
            
            # 毛玻璃卡牌背景
            GlassEffect.draw_glass_rect(
                screen, card_rect, alpha=200, border_alpha=80,
                radius=Theme.get_size('border_radius_medium')
            )
            
            # 稀有度边框
            border_color = rarity_colors.get(card.rarity, (156, 163, 175))
            border_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            pygame.draw.rect(border_surface, border_color + (200,),
                           (0, 0, card_width, card_height), 
                           width=4, border_radius=Theme.get_size('border_radius_medium'))
            screen.blit(border_surface, card_rect.topleft)
            
            # 卡牌名称
            name_font = pygame.font.Font(None, 20)
            name_text = name_font.render(card.name[:10], True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(card_rect.centerx, card_rect.bottom - 15))
            screen.blit(name_text, name_rect)
            
            # 稀有度标识
            rarity_font = pygame.font.Font(None, 16)
            rarity_text = rarity_font.render(card.rarity, True, border_color)
            rarity_rect = rarity_text.get_rect(center=(card_rect.centerx, card_rect.bottom - 35))
            screen.blit(rarity_text, rarity_rect)

    def _draw_ui_elements(self, screen):
        """绘制UI元素"""
        # 绘制交互按钮
        if self.animation_state == AnimationState.SELECTION:
            self.left_arrow_button.draw(screen)
            self.right_arrow_button.draw(screen)
        
        # 关闭按钮（完成后显示）
        if self.can_close:
            self.close_button.draw(screen)
        
        # 状态提示 - 屏幕下方
        status_messages = {
            AnimationState.SELECTION: "Toca el paquete para abrir | ← → para cambiar",
            AnimationState.IDLE: "Preparando...",
            AnimationState.OPENING: "Abriendo paquete...",
            AnimationState.REVEALING: "Revelando cartas...",
            AnimationState.COMPLETED: f"¡Obtienes {len(self.obtained_cards)} cartas!"
        }
        
        status_text = status_messages.get(self.animation_state, "")
        if status_text and self.animation_state != AnimationState.COMPLETED:
            font = pygame.font.Font(None, 28)
            text_surface = font.render(status_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 80 + self.content_offset_y))
            screen.blit(text_surface, text_rect)

# 测试用例
if __name__ == "__main__":
    # class MockGameManager:
    #     def __init__(self):
    #         self.user_packs = {"basic": 5, "premium": 3, "legendary": 1}
        
    #     def open_pack_complete_flow(self, quality: str):
    #         if self.user_packs.get(quality, 0) <= 0:
    #             return {"success": False, "error": "insufficient_packs"}
            
    #         self.user_packs[quality] -= 1
    #         # 使用新的卡牌格式
    #         mock_cards = [
    #             {"id": "sm3-1", "name": "Caterpie", "rarity": "Common", "image": "images/sm3-1.png", "hp": 50},
    #             {"id": "sm3-2", "name": "Pikachu", "rarity": "Rare", "image": "images/sm3-2.png", "hp": 60},
    #             {"id": "sm3-3", "name": "Charizard", "rarity": "Legendary", "image": "images/sm3-3.png", "hp": 150}
    #         ]
    #         return {"success": True, "cards": mock_cards}
    
    # pygame.init()
    # screen = pygame.display.set_mode((1400, 900))
    # pygame.display.set_caption("Apertura de Paquetes - Pantalla Completa")
    # clock = pygame.time.Clock()
    
    # game_manager = MockGameManager()
    # pack_window = PackOpeningWindow(1400, 900, game_manager)
    # pack_window.show()
    
    # running = True
    # while running:
    #     dt = clock.tick(60) / 1000.0
        
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False
    #         else:
    #             pack_window.handle_event(event)
        
    #     pack_window.update(dt)
        
    #     # 渐变背景
    #     screen.fill(Theme.get_color('background'))
    #     pack_window.draw(screen)
        
    #     pygame.display.flip()
    
    pygame.quit()