"""
视频背景处理工具
简化的视频背景实现，减少依赖
"""

import pygame
import os
import threading
import time

class VideoBackground:
    """简化的视频背景类，避免复杂的OpenCV依赖"""
    
    def __init__(self, video_path, target_size=(960, 540)):
        self.video_path = video_path
        self.target_size = target_size
        self.current_frame = None
        self.running = False
        
        # 检查文件是否存在
        if not os.path.exists(video_path):
            print(f"⚠️ 视频文件不存在: {video_path}")
            return
        
        # 尝试加载视频（如果有OpenCV）
        try:
            import cv2
            self.cap = cv2.VideoCapture(video_path)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.running = True
            
            # 启动视频更新线程
            self.thread = threading.Thread(target=self._update_video, daemon=True)
            self.thread.start()
            print(f"✅ 视频背景加载成功: {video_path}")
            
        except ImportError:
            print("⚠️ OpenCV未安装，无法使用视频背景")
            self.cap = None
        except Exception as e:
            print(f"⚠️ 视频背景加载失败: {e}")
            self.cap = None
    
    def _update_video(self):
        """更新视频帧的线程函数"""
        if not self.cap:
            return
        
        import cv2
        
        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    # 视频结束，重新开始播放
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.cap.read()
                    if not ret:
                        break
                
                # 调整帧的大小
                if frame is not None:
                    frame = cv2.resize(frame, self.target_size)
                    # 从BGR转换为RGB
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.current_frame = frame
                
                # 控制帧率
                time.sleep(1 / self.fps)
                
            except Exception as e:
                print(f"视频播放错误: {e}")
                break
    
    def get_surface(self, size=None):
        """
        获取当前视频帧的pygame表面
        
        Args:
            size: 目标尺寸，如果为None则使用默认尺寸
            
        Returns:
            pygame.Surface: 视频帧表面，如果失败返回None
        """
        if self.current_frame is None:
            return None
        
        try:
            target_size = size if size else self.target_size
            
            # 如果尺寸不同，调整大小
            if target_size != (self.current_frame.shape[1], self.current_frame.shape[0]):
                import cv2
                frame = cv2.resize(self.current_frame, target_size)
            else:
                frame = self.current_frame
            
            # 创建pygame表面
            pygame_frame = pygame.image.frombuffer(
                frame.tobytes(), (frame.shape[1], frame.shape[0]), 'RGB'
            )
            
            return pygame_frame
            
        except Exception as e:
            print(f"获取视频帧失败: {e}")
            return None
    
    def update_size(self, new_size):
        """更新目标尺寸"""
        self.target_size = new_size
    
    def update(self):
        """更新方法（为了兼容性，实际更新在线程中进行）"""
        pass
    
    def close(self):
        """关闭视频背景"""
        self.running = False
        
        if hasattr(self, 'thread') and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()

class StaticBackground:
    """静态背景类，作为视频背景的后备方案"""
    
    def __init__(self, target_size=(960, 540)):
        self.target_size = target_size
        self.background_surface = None
        self.create_gradient_background()
    
    def create_gradient_background(self):
        """创建渐变背景"""
        width, height = self.target_size
        self.background_surface = pygame.Surface((width, height))
        
        # 创建深蓝到紫色的渐变
        for y in range(height):
            progress = y / height
            r = int(20 + progress * 30)
            g = int(25 + progress * 20)
            b = int(60 + progress * 40)
            pygame.draw.line(self.background_surface, (r, g, b), (0, y), (width, y))
    
    def get_surface(self, size=None):
        """获取背景表面"""
        target_size = size if size else self.target_size
        
        if target_size != self.target_size:
            self.target_size = target_size
            self.create_gradient_background()
        
        return self.background_surface
    
    def update_size(self, new_size):
        """更新尺寸"""
        if new_size != self.target_size:
            self.target_size = new_size
            self.create_gradient_background()
    
    def update(self):
        """更新方法（静态背景无需更新）"""
        pass
    
    def close(self):
        """关闭背景（静态背景无需特殊处理）"""
        pass