import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIPanel, UILabel, UIWindow
from pygame_gui.core import ObjectID
import random
import os

class PackageWindow:
    """
    卡包开启窗口 - 弹出式对话框
    包含卡包动画、开包效果和卡牌展示
    """
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager, pack_index: int = 0, pack_type: str = "basic"):
        """
        初始化卡包窗口
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            ui_manager: pygame_gui UI管理器
            pack_index: 卡包索引
            pack_type: 卡包类型
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        self.pack_index = pack_index
        self.pack_type = pack_type
        
        # 窗口尺寸
        self.window_width = min(800, int(screen_width * 0.8))
        self.window_height = min(600, int(screen_height * 0.8))
        
        # 计算居中位置
        window_x = (screen_width - self.window_width) // 2
        window_y = (screen_height - self.window_height) // 2
        
        # 创建主窗口
        self.window = UIWindow(
            rect=pygame.Rect(window_x, window_y, self.window_width, self.window_height),
            manager=ui_manager,
            window_display_title=f"Abrir Sobre - {self.get_pack_name()}",
            object_id=ObjectID('#package_window'),
            resizable=False
        )
        
        # 状态管理
        self.is_visible = True
        self.animation_state = "idle"  # idle, opening, revealing, completed
        self.animation_timer = 0
        
        # 卡包图片
        self.pack_image = None
        self.load_pack_image()
        
        # 创建UI元素
        self.create_ui_elements()
        
        # 回调函数
        self.on_close = None
        
        print(f"📦 创建卡包窗口: {self.get_pack_name()} (索引: {pack_index})")
    
    def get_pack_name(self) -> str:
        """获取卡包名称"""
        pack_names = {
            "basic": "Sobre Básico",
            "advanced": "Sobre Avanzado", 
            "legendary": "Sobre Legendario",
            "pack_1": "Festival Brillante",
            "pack_2": "Guardianes Celestiales",
            "pack_3": "Guardianes Celestiales"
        }
        return pack_names.get(self.pack_type, f"Sobre {self.pack_index + 1}")
    
    def load_pack_image(self):
        """加载卡包图片"""
        pack_dir = os.path.join("assets", "images", "packets")
        
        # 尝试加载对应的卡包图片
        pack_files = [
            f"packet{self.pack_index + 1}.png",
            f"packet{random.randint(1, 12)}.png",  # 随机备选
            "packet1.png"  # 默认
        ]
        
        for pack_file in pack_files:
            pack_path = os.path.join(pack_dir, pack_file)
            if os.path.exists(pack_path):
                try:
                    self.pack_image = pygame.image.load(pack_path)
                    print(f"✅ 已加载卡包图片: {pack_file}")
                    break
                except Exception as e:
                    print(f"❌ 加载卡包图片失败 {pack_file}: {e}")
        
        if not self.pack_image:
            print("⚠️ 未找到卡包图片，将使用占位符")
    
    def create_ui_elements(self):
        """创建UI元素"""
        # 卡包信息标签
        info_rect = pygame.Rect(20, 20, self.window_width - 40, 60)
        self.info_label = UILabel(
            relative_rect=info_rect,
            text=f"¡Vas a abrir un {self.get_pack_name()}!",
            manager=self.ui_manager,
            container=self.window
        )
        
        # 开包按钮
        button_width = 200
        button_height = 50
        button_x = (self.window_width - button_width) // 2
        button_y = self.window_height - 120
        
        self.open_button = UIButton(
            relative_rect=pygame.Rect(button_x, button_y, button_width, button_height),
            text="¡Abrir Sobre!",
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#open_pack_button')
        )
        
        # 关闭按钮
        close_button_y = button_y + 60
        self.close_button = UIButton(
            relative_rect=pygame.Rect(button_x, close_button_y, button_width, button_height),
            text="Cerrar",
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#close_button')
        )
        
        # 动画状态标签
        status_y = button_y - 50
        self.status_label = UILabel(
            relative_rect=pygame.Rect(20, status_y, self.window_width - 40, 30),
            text="Haz clic en '¡Abrir Sobre!' para comenzar",
            manager=self.ui_manager,
            container=self.window
        )
    
    def handle_event(self, event):
        """处理事件"""
        if not self.is_visible:
            return None
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.open_button:
                self.start_opening_animation()
                return "open_pack"
            
            elif event.ui_element == self.close_button:
                self.close()
                return "close"
        
        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self.close()
                return "close"
        
        return None
    
    def start_opening_animation(self):
        """开始开包动画"""
        if self.animation_state == "idle":
            self.animation_state = "opening"
            self.animation_timer = 0
            self.open_button.disable()
            self.status_label.set_text("¡Abriendo sobre...")
            print(f"🎴 开始开包动画: {self.get_pack_name()}")
    
    def update(self, time_delta: float):
        """更新动画状态"""
        if not self.is_visible:
            return
        
        if self.animation_state == "opening":
            self.animation_timer += time_delta
            
            if self.animation_timer >= 2.0:  # 2秒开包动画
                self.animation_state = "revealing"
                self.animation_timer = 0
                self.status_label.set_text("¡Revelando cartas...")
                print("🎊 卡包开启完成，开始展示卡牌")
        
        elif self.animation_state == "revealing":
            self.animation_timer += time_delta
            
            if self.animation_timer >= 1.5:  # 1.5秒展示动画
                self.animation_state = "completed"
                self.status_label.set_text("¡Cartas obtenidas! Revisa tu colección.")
                self.open_button.enable()
                self.open_button.set_text("Abrir Otro")
                print("✨ 卡牌展示完成")
    
    def draw_custom_content(self, screen: pygame.Surface):
        """绘制自定义内容（卡包图片和动画效果）"""
        if not self.is_visible or not self.pack_image:
            return
        
        # 获取窗口内容区域
        content_rect = self.window.get_container().get_rect()
        
        # 计算卡包图片位置
        pack_display_size = 200
        pack_x = content_rect.centerx - pack_display_size // 2
        pack_y = content_rect.y + 100
        
        # 根据动画状态绘制效果
        if self.animation_state == "idle":
            # 静态显示卡包
            scaled_pack = pygame.transform.scale(self.pack_image, (pack_display_size, pack_display_size))
            screen.blit(scaled_pack, (pack_x, pack_y))
        
        elif self.animation_state == "opening":
            # 开包动画 - 震动和缩放效果
            shake_intensity = min(self.animation_timer / 2.0, 1.0) * 5
            shake_x = random.uniform(-shake_intensity, shake_intensity)
            shake_y = random.uniform(-shake_intensity, shake_intensity)
            
            scale_factor = 1.0 + (self.animation_timer / 2.0) * 0.2
            scaled_size = int(pack_display_size * scale_factor)
            
            scaled_pack = pygame.transform.scale(self.pack_image, (scaled_size, scaled_size))
            screen.blit(scaled_pack, (pack_x + shake_x - (scaled_size - pack_display_size) // 2, 
                                   pack_y + shake_y - (scaled_size - pack_display_size) // 2))
        
        elif self.animation_state == "revealing":
            # 展示动画 - 光芒效果
            scaled_pack = pygame.transform.scale(self.pack_image, (pack_display_size, pack_display_size))
            
            # 添加光芒效果（简单的白色叠加）
            glow_alpha = int(128 * abs(pygame.math.sin(self.animation_timer * 3)))
            glow_surface = pygame.Surface((pack_display_size, pack_display_size), pygame.SRCALPHA)
            glow_surface.fill((255, 255, 255, glow_alpha))
            
            screen.blit(scaled_pack, (pack_x, pack_y))
            screen.blit(glow_surface, (pack_x, pack_y))
        
        elif self.animation_state == "completed":
            # 完成状态 - 正常显示
            scaled_pack = pygame.transform.scale(self.pack_image, (pack_display_size, pack_display_size))
            screen.blit(scaled_pack, (pack_x, pack_y))
    
    def close(self):
        """关闭窗口"""
        if self.is_visible:
            self.is_visible = False
            if self.window:
                self.window.kill()
            if self.on_close:
                self.on_close()
            print(f"🚪 关闭卡包窗口: {self.get_pack_name()}")
    
    def cleanup(self):
        """清理资源"""
        if self.window:
            self.window.kill()
        if self.pack_image:
            del self.pack_image