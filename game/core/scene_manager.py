import pygame
import time
from game.core.simple_transition import SimpleTransition
from game.scenes.welcome_scene import WelcomeScene
from game.scenes.login_scene import LoginScene
from game.scenes.register_scene import RegisterScene
from game.scenes.main_scene import MainScene

class SceneManager:
    def __init__(self, screen):
        """初始化场景管理器"""
        self.screen = screen
        self.scenes = {}
        self.current_scene = None
        self.transition = SimpleTransition(screen)
        print("🎮 场景管理器初始化完成")
    
    def add_scene(self, name, scene_class):
        """添加场景类"""
        self.scenes[name] = scene_class
        print(f"📝 注册场景: {name}")
    
    def run(self, initial_scene):
        """运行场景管理器主循环"""
        print(f"🚀 启动场景管理器，初始场景: {initial_scene}")
        
        # 启动初始场景
        if not self.start_scene(initial_scene):
            print(f"❌ 无法启动初始场景: {initial_scene}")
            return False
        
        # 主循环
        clock = pygame.time.Clock()
        last_time = time.time()
        running = True
        
        while running and self.current_scene is not None:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                
                # 传递事件给当前场景
                if self.current_scene and hasattr(self.current_scene, 'handle_event'):
                    self.current_scene.handle_event(event)
            
            if not running:
                break
            
            # 计算时间差
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            dt = min(dt, 0.05)  # 限制最大时间步长
            
            # 更新场景管理器
            if not self.update(dt):
                print("🛑 场景管理器更新返回False，退出主循环")
                break
            
            # 绘制
            self.screen.fill((0, 0, 0))  # 清屏
            self.draw()
            pygame.display.flip()
            
            # 控制帧率
            clock.tick(60)
        
        print("🏁 场景管理器主循环结束")
        self.cleanup()
        return True
    
    def start_scene(self, scene_name, *args, **kwargs):
        """启动初始场景"""
        return self.switch_scene(scene_name, *args, **kwargs)
    
    def update(self, dt):
        """更新场景管理器"""
        # 更新转换动画
        self.transition.update(dt)
        
        # 检查是否需要切换场景
        if self.transition.is_switch_ready():
            target_scene = self.transition.get_target_scene()
            print(f"🔄 执行场景切换: {target_scene}")
            
            # 执行场景切换
            if self.switch_scene(target_scene):
                self.transition.confirm_switch()  # 确认切换，开始淡入
        
        # 更新当前场景（只有在不繁忙时才更新）
        if self.current_scene and not self.transition.is_busy():
            if hasattr(self.current_scene, 'update'):
                scene_result = self.current_scene.update(dt)
                if scene_result is False:
                    return False
        
        return True
    
    def draw(self):
        """绘制场景和转换效果"""
        # 绘制当前场景
        if self.current_scene and hasattr(self.current_scene, 'draw'):
            self.current_scene.draw()
        
        # 绘制转换遮罩
        self.transition.draw()
    
    def scene_callback(self, result):
        """场景回调函数 - 现在只是触发转换"""
        print(f"📞 场景请求: {result}")
        
        if result == "login":
            self.transition.start_transition("login")
        elif result == "register":
            self.transition.start_transition("register")
        elif result == "back":
            self.transition.start_transition("welcome")
        elif result == "game_main":
            self.transition.start_transition("game_main")
        elif result == "exit":
            print("👋 用户退出")
            self.current_scene = None
        else:
            print(f"⚠️ 未知请求: {result}")
    
    def switch_scene(self, scene_name, *args, **kwargs):
        """切换到指定场景"""
        if scene_name not in self.scenes:
            print(f"❌ 场景不存在: {scene_name}")
            return False
        
        try:
            # 清理当前场景
            if self.current_scene and hasattr(self.current_scene, 'cleanup'):
                self.current_scene.cleanup()
            
            # 创建新场景
            scene_class = self.scenes[scene_name]
            self.current_scene = scene_class(
                screen=self.screen,
                callback=self.scene_callback,
                *args, **kwargs
            )
            
            print(f"✅ 已切换到场景: {scene_name}")
            return True
            
        except Exception as e:
            print(f"❌ 切换场景失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """清理场景管理器"""
        if self.current_scene and hasattr(self.current_scene, 'cleanup'):
            self.current_scene.cleanup()
        self.current_scene = None
        print("🧹 场景管理器已清理")