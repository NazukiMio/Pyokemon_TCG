import pygame

class SimpleTransition:
    """简单的场景转换管理器"""
    
    def __init__(self, screen):
        self.screen = screen
        self.state = "idle"  # idle, fade_out, fade_in
        self.alpha = 0
        self.fade_speed = 500  # 淡化速度
        self.target_scene = None  # 目标场景名称
        
        # 创建黑色遮罩
        self.overlay = pygame.Surface(screen.get_size())
        self.overlay.fill((0, 0, 0))
    
    def start_transition(self, target_scene):
        """开始转换到目标场景"""
        print(f"🎬 开始转换到场景: {target_scene}")
        self.state = "fade_out"
        self.alpha = 0
        self.target_scene = target_scene
    
    def update(self, dt):
        """更新转换状态"""
        if self.state == "fade_out":
            self.alpha += dt * self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.state = "switch_ready"  # 准备切换场景
                print(f"🔄 淡出完成，准备切换到: {self.target_scene}")
        
        elif self.state == "fade_in":
            self.alpha -= dt * self.fade_speed
            if self.alpha <= 0:
                self.alpha = 0
                self.state = "idle"
                print("✨ 转换完成")
    
    def draw(self):
        """绘制遮罩"""
        if self.state != "idle":
            self.overlay.set_alpha(int(self.alpha))
            self.screen.blit(self.overlay, (0, 0))
    
    def is_switch_ready(self):
        """检查是否准备好切换场景"""
        return self.state == "switch_ready"
    
    def get_target_scene(self):
        """获取目标场景"""
        return self.target_scene
    
    def confirm_switch(self):
        """确认场景已切换，开始淡入"""
        self.state = "fade_in"
        self.target_scene = None
        print("🎬 开始淡入")
    
    def is_busy(self):
        """检查是否正在转换中"""
        return self.state != "idle"