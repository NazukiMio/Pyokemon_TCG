"""
场景转换效果
统一管理场景之间的转换动画
"""

import pygame
from ..styles.theme import Theme

class TransitionManager:
    """转换管理器，处理场景之间的转换效果"""
    
    def __init__(self, screen, fade_speed=500):
        """
        初始化淡入淡出转换效果
        
        Args:
            screen: pygame屏幕对象
            fade_speed: 淡入淡出速度
        """
        self.screen = screen
        self.fade_speed = fade_speed
        
        # 转换状态
        self.fade_out = False
        self.fade_in = False
        self.alpha = 0
        self.callback = None
        
        # 创建覆盖层
        self.overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        
        print("✅ 淡入淡出转换管理器初始化完成")
        
    def start_fade_transition(self, callback=None):
        """
        开始淡入淡出转换
        
        Args:
            callback: 转换完成后的回调函数
        """
        self.current_transition = 'fade'
        self.transition_progress = 0.0
        self.callback = callback
    
    def start_slide_transition(self, direction='left', callback=None):
        """
        开始滑动转换
        
        Args:
            direction: 滑动方向 ('left', 'right', 'up', 'down')
            callback: 转换完成后的回调函数
        """
        self.current_transition = f'slide_{direction}'
        self.transition_progress = 0.0
        self.callback = callback
    
    def update(self, dt):
        """更新转换动画"""
        if self.fade_out:
            old_alpha = self.alpha
            self.alpha += dt * self.fade_speed
            print(f"🎬 淡出进度: {old_alpha:.1f} -> {self.alpha:.1f} (目标: 255)")
            
            if self.alpha >= 255:
                self.alpha = 255
                print("🎬 淡出完成，执行回调")
                
                # 确保回调存在并执行
                if self.callback:
                    print(f"🔄 执行回调函数: {self.callback}")
                    try:
                        self.callback()
                        print("✅ 回调函数执行成功")
                    except Exception as e:
                        print(f"❌ 回调函数执行失败: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print("⚠️ 没有回调函数")
                
                self.fade_out = False
                self.fade_in = True
                self.callback = None  # 清除回调，避免重复执行
                return True
        
        elif self.fade_in:
            old_alpha = self.alpha
            self.alpha -= dt * self.fade_speed
            print(f"🎬 淡入进度: {old_alpha:.1f} -> {self.alpha:.1f} (目标: 0)")
            
            if self.alpha <= 0:
                self.alpha = 0
                self.fade_in = False
                print("🎬 淡入完成")
                return True
        
        return self.fade_out or self.fade_in  # 只有在转换进行中时返回True
    
    def draw(self):
        """绘制转换效果"""
        if not self.current_transition:
            return
        
        if self.current_transition == 'fade':
            self._draw_fade_transition()
        elif self.current_transition.startswith('slide_'):
            direction = self.current_transition.split('_')[1]
            self._draw_slide_transition(direction)
    
    def _draw_fade_transition(self):
        """绘制淡入淡出转换"""
        # 计算透明度
        if self.transition_progress <= 1.0:
            alpha = int(255 * self.transition_progress)
        else:
            alpha = int(255 * (2.0 - self.transition_progress))
        
        if alpha > 0:
            fade_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            fade_surface.fill((0, 0, 0, alpha))
            self.screen.blit(fade_surface, (0, 0))
    
    def _draw_slide_transition(self, direction):
        """绘制滑动转换"""
        screen_width, screen_height = self.screen.get_size()
        
        # 计算偏移量
        if self.transition_progress <= 1.0:
            progress = self.transition_progress
        else:
            progress = 2.0 - self.transition_progress
        
        # 使用缓动函数
        eased_progress = self._ease_in_out_cubic(progress)
        
        if direction == 'left':
            offset_x = int(screen_width * eased_progress)
            overlay_rect = pygame.Rect(screen_width - offset_x, 0, offset_x, screen_height)
        elif direction == 'right':
            offset_x = int(screen_width * eased_progress)
            overlay_rect = pygame.Rect(0, 0, offset_x, screen_height)
        elif direction == 'up':
            offset_y = int(screen_height * eased_progress)
            overlay_rect = pygame.Rect(0, screen_height - offset_y, screen_width, offset_y)
        else:  # down
            offset_y = int(screen_height * eased_progress)
            overlay_rect = pygame.Rect(0, 0, screen_width, offset_y)
        
        # 绘制滑动覆盖层
        overlay_surface = pygame.Surface((overlay_rect.width, overlay_rect.height), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 200))
        self.screen.blit(overlay_surface, overlay_rect)
    
    def _ease_in_out_cubic(self, t):
        """三次缓动函数"""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
    
    def is_transitioning(self):
        """检查是否正在转换"""
        return self.current_transition is not None
    
    def get_progress(self):
        """获取转换进度"""
        return self.transition_progress
    
    def force_complete(self):
        """强制完成转换"""
        if self.current_transition:
            self.transition_progress = 2.0
            self.current_transition = None
            if self.callback:
                self.callback()
                self.callback = None

class FadeTransition:
    """淡入淡出转换效果"""
    
    def __init__(self, screen, fade_speed=500):
        """
        初始化淡入淡出转换效果
        
        Args:
            screen: pygame屏幕对象
            fade_speed: 淡入淡出速度
        """
        self.screen = screen
        self.fade_speed = fade_speed
        
        # 转换状态
        self.fade_out = False
        self.fade_in = False
        self.alpha = 0
        self.callback = None
        
        # 创建覆盖层
        self.overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        
        print("✅ 淡入淡出转换管理器初始化完成")
    
    def start_fade_out(self, callback=None):
        """开始淡出动画"""
        print(f"🎬 开始淡出动画，回调: {callback}")
        self.fade_out = True
        self.fade_in = False
        self.alpha = 0
        self.callback = callback
        print(f"🎬 淡出动画状态设置完成")
    
    def start_fade_in(self):
        """开始淡入动画"""
        print("🎬 开始淡入动画")
        self.fade_in = True
        self.fade_out = False
        self.alpha = 255
    
    def update(self, dt):
        """更新转换动画"""
        if self.fade_out:
            self.alpha += dt * self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                print("🎬 淡出完成，执行回调")
                if self.callback:
                    self.callback()
                self.fade_out = False
                self.fade_in = True
                return True
        
        elif self.fade_in:
            self.alpha -= dt * self.fade_speed
            if self.alpha <= 0:
                self.alpha = 0
                self.fade_in = False
                print("🎬 淡入完成")
                return True
        
        return True
    
    def draw(self):
        """绘制转换效果"""
        if self.fade_out or self.fade_in:
            # 确保alpha值在有效范围内
            alpha = max(0, min(255, int(self.alpha)))
            self.overlay.fill((0, 0, 0, alpha))
            self.screen.blit(self.overlay, (0, 0))
    
    def is_active(self):
        """检查转换是否激活"""
        return self.fade_out or self.fade_in