"""
动画管理器
统一管理各种动画效果
"""

import pygame
import math
import time
from ..styles.theme import Theme

class AnimationManager:
    """动画管理器，处理各种动画效果"""
    
    def __init__(self):
        self.animations = {}
        self.start_time = time.time()
    
    def create_button_animation(self, button_id):
        """
        创建按钮动画
        
        Args:
            button_id: 按钮ID
            
        Returns:
            dict: 动画状态字典
        """
        if button_id not in self.animations:
            self.animations[button_id] = {
                'scale': Theme.ANIMATION['scale_normal'],
                'target_scale': Theme.ANIMATION['scale_normal'],
                'glow': 0.0,
                'flash': 0.0,
                'hover': False,
                'type': 'button'
            }
        return self.animations[button_id]
    
    def create_fade_animation(self, fade_id, initial_alpha=255, fade_direction=-1):
        """
        创建淡入淡出动画
        
        Args:
            fade_id: 动画ID
            initial_alpha: 初始透明度
            fade_direction: 淡化方向 (-1淡入, 1淡出)
            
        Returns:
            dict: 动画状态字典
        """
        if fade_id not in self.animations:
            self.animations[fade_id] = {
                'alpha': initial_alpha,
                'direction': fade_direction,
                'speed': Theme.ANIMATION['fade_speed'],
                'target_alpha': 0 if fade_direction == -1 else 255,
                'callback': None,
                'type': 'fade'
            }
        return self.animations[fade_id]
    
    def create_breath_animation(self, breath_id):
        """
        创建呼吸动画
        
        Args:
            breath_id: 动画ID
            
        Returns:
            dict: 动画状态字典
        """
        if breath_id not in self.animations:
            self.animations[breath_id] = {
                'scale': Theme.ANIMATION['breath_scale_min'],
                'time': 0.0,
                'speed': Theme.ANIMATION['breath_speed'],
                'type': 'breath'
            }
        return self.animations[breath_id]
    
    def update_button_hover(self, button_id, is_hover):
        """
        更新按钮悬停状态
        
        Args:
            button_id: 按钮ID
            is_hover: 是否悬停
        """
        anim = self.create_button_animation(button_id)
        if anim['hover'] != is_hover:
            anim['hover'] = is_hover
            if is_hover:
                anim['target_scale'] = Theme.ANIMATION['scale_hover']
                anim['glow'] = 0.3
            else:
                anim['target_scale'] = Theme.ANIMATION['scale_normal']
                anim['glow'] = 0.0
    
    def trigger_button_flash(self, button_id, intensity=1.0):
        """
        触发按钮闪光效果
        
        Args:
            button_id: 按钮ID
            intensity: 闪光强度
        """
        anim = self.create_button_animation(button_id)
        anim['flash'] = intensity
    
    def start_fade_out(self, fade_id, callback=None):
        """
        开始淡出动画
        
        Args:
            fade_id: 动画ID
            callback: 完成回调函数
        """
        anim = self.create_fade_animation(fade_id, 0, 1)
        anim['direction'] = 1
        anim['callback'] = callback
    
    def start_fade_in(self, fade_id, callback=None):
        """
        开始淡入动画
        
        Args:
            fade_id: 动画ID
            callback: 完成回调函数
        """
        anim = self.create_fade_animation(fade_id, 255, -1)
        anim['direction'] = -1
        anim['callback'] = callback
    
    def update(self, dt):
        """
        更新所有动画
        
        Args:
            dt: 时间增量（秒）
            
        Returns:
            list: 完成的动画回调函数列表
        """
        completed_callbacks = []
        
        for anim_id, anim in self.animations.items():
            if anim['type'] == 'button':
                self._update_button_animation(anim, dt)
            elif anim['type'] == 'fade':
                callback = self._update_fade_animation(anim, dt)
                if callback:
                    completed_callbacks.append(callback)
            elif anim['type'] == 'breath':
                self._update_breath_animation(anim, dt)
        
        return completed_callbacks
    
    def _update_button_animation(self, anim, dt):
        """更新按钮动画"""
        # 缩放动画
        scale_diff = anim['target_scale'] - anim['scale']
        if abs(scale_diff) < 0.01:
            anim['scale'] = anim['target_scale']
        else:
            anim['scale'] += scale_diff * Theme.ANIMATION['speed_normal']
        
        # 闪光动画
        if anim['flash'] > 0:
            anim['flash'] -= dt * 4
            anim['flash'] = max(0, anim['flash'])
    
    def _update_fade_animation(self, anim, dt):
        """更新淡入淡出动画"""
        if anim['direction'] != 0:
            anim['alpha'] += anim['direction'] * anim['speed'] * dt * 255
            
            if anim['direction'] == -1:  # 淡入
                if anim['alpha'] <= 0:
                    anim['alpha'] = 0
                    anim['direction'] = 0
            else:  # 淡出
                if anim['alpha'] >= 255:
                    anim['alpha'] = 255
                    anim['direction'] = 0
                    # 返回回调函数
                    callback = anim['callback']
                    anim['callback'] = None
                    return callback
        
        return None
    
    def _update_breath_animation(self, anim, dt):
        """更新呼吸动画"""
        anim['time'] += dt
        # 使用正弦波创建平滑的呼吸效果
        progress = (math.sin(anim['time'] * anim['speed']) + 1) / 2
        min_scale = Theme.ANIMATION['breath_scale_min']
        max_scale = Theme.ANIMATION['breath_scale_max']
        anim['scale'] = min_scale + (max_scale - min_scale) * progress
    
    def get_animation(self, anim_id):
        """
        获取动画状态
        
        Args:
            anim_id: 动画ID
            
        Returns:
            dict: 动画状态字典，如果不存在返回None
        """
        return self.animations.get(anim_id)
    
    def remove_animation(self, anim_id):
        """
        移除动画
        
        Args:
            anim_id: 动画ID
        """
        if anim_id in self.animations:
            del self.animations[anim_id]
    
    def clear_all(self):
        """清除所有动画"""
        self.animations.clear()
    
    def is_animating(self, anim_id):
        """
        检查动画是否正在进行
        
        Args:
            anim_id: 动画ID
            
        Returns:
            bool: 是否正在动画
        """
        anim = self.animations.get(anim_id)
        if not anim:
            return False
        
        if anim['type'] == 'fade':
            return anim['direction'] != 0
        elif anim['type'] == 'button':
            return abs(anim['scale'] - anim['target_scale']) > 0.01 or anim['flash'] > 0
        elif anim['type'] == 'breath':
            return True  # 呼吸动画始终进行
        
        return False