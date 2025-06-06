"""
重构后的主启动器
统一的入口点，简化的架构
"""

import pygame
import sys
import os
import traceback

# 导入核心模块
from game.core.scene_manager import SceneManager
from game.scenes.login_scene import LoginScene
from game.scenes.register_scene import RegisterScene
from game.scenes.main_scene import MainScene
from game.scenes.styles.theme import Theme
from game.scenes.styles.fonts import font_manager

class GameLauncher:
    """游戏启动器，统一的入口点"""
    
    def __init__(self):
        """初始化启动器"""
        self.screen = None
        self.clock = None
        self.running = False
        
        # 初始化pygame
        self.init_pygame()
        
        # 设置窗口
        self.setup_window()
        
        print("🎮 游戏启动器初始化完成")
    
    def init_pygame(self):
        """初始化pygame"""
        try:
            pygame.init()
            pygame.font.init()
            print("✅ Pygame初始化成功")
        except Exception as e:
            print(f"❌ Pygame初始化失败: {e}")
            sys.exit(1)
    
    def setup_window(self):
        """设置游戏窗口"""
        try:
            # 获取显示器信息
            display_info = pygame.display.Info()
            screen_width = int(display_info.current_w * 0.75)
            screen_height = int(display_info.current_h * 0.75)
            
            # 创建窗口
            self.screen = pygame.display.set_mode(
                (screen_width, screen_height), 
                pygame.RESIZABLE
            )
            
            # 设置窗口标题
            pygame.display.set_caption("Juego de Cartas Coleccionables - Pygame Edition")
            
            # 设置窗口图标
            self.set_window_icon()
            
            # 创建时钟
            self.clock = pygame.time.Clock()
            
            print(f"✅ 游戏窗口创建成功 ({screen_width}x{screen_height})")
            
        except Exception as e:
            print(f"❌ 窗口设置失败: {e}")
            sys.exit(1)
    
    def set_window_icon(self):
        """设置窗口图标"""
        try:
            icon_path = os.path.join("assets", "images", "icon", "game_icon.png")
            if os.path.exists(icon_path):
                icon = pygame.image.load(icon_path)
                pygame.display.set_icon(icon)
                print("✅ 窗口图标设置成功")
        except Exception as e:
            print(f"⚠️ 无法设置窗口图标: {e}")
    
    def show_startup_screen(self):
        """显示启动画面"""
        try:
            # 创建渐变背景
            width, height = self.screen.get_size()
            
            for y in range(height):
                progress = y / height
                start_color = Theme.get_color('background_gradient_start')
                end_color = Theme.get_color('background_gradient_end')
                
                r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
                pygame.draw.line(self.screen, (r, g, b), (0, y), (width, y))
            
            # 显示加载文本
            loading_text = "Cargando..."
            text_color = Theme.get_color('text')
            text_surface = font_manager.render_text(loading_text, 'xl', height, text_color)
            text_rect = text_surface.get_rect(center=(width // 2, height // 2))
            self.screen.blit(text_surface, text_rect)
            
            # 显示版本信息
            version_text = "Pygame Edition v1.0"
            version_surface = font_manager.render_text(version_text, 'md', height, text_color)
            version_rect = version_surface.get_rect(center=(width // 2, height // 2 + 60))
            self.screen.blit(version_surface, version_rect)
            
            pygame.display.flip()
            pygame.time.delay(1000)  # 显示1秒
            
        except Exception as e:
            print(f"⚠️ 启动画面显示失败: {e}")
    
    # def run_auth_system(self):
    #     """
    #     运行认证系统
        
    #     Returns:
    #         int: 用户ID（如果登录成功）或None（用户退出）
    #     """
    #     try:
    #         print("🔐 启动认证系统...")
            
    #         # 导入场景类
    #         from game.scenes.welcome_scene import WelcomeScene
    #         from game.scenes.login_scene import LoginScene
    #         from game.scenes.register_scene import RegisterScene
            
    #         # 创建场景管理器
    #         scene_manager = SceneManager(self.screen)
            
    #         # 注册场景
    #         scene_manager.add_scene("welcome", WelcomeScene)
    #         scene_manager.add_scene("login", LoginScene)
    #         scene_manager.add_scene("register", RegisterScene)
            
    #         # 运行场景管理器，让用户在各场景间自由切换
    #         # 只有登录成功或明确退出才结束
    #         result = scene_manager.run("welcome")
            
    #         if isinstance(result, int) and result > 0:
    #             print(f"✅ 用户登录成功，用户ID: {result}")
    #             return result
    #         else:
    #             print("ℹ️ 用户退出游戏")
    #             return None
                
    #     except Exception as e:
    #         print(f"❌ 认证系统运行失败: {e}")
    #         traceback.print_exc()
    #         return None
    
    def run_main_game(self, user_id):
        """
        运行主游戏
        
        Args:
            user_id: 已登录的用户ID
        """
        print(f"🎮 启动主游戏，用户ID: {user_id}")
        
        # 这里将来会启动主游戏界面
        # 目前只显示一个简单的成功页面
        self.show_success_screen(user_id)
    
    def show_success_screen(self, user_id):
        """
        显示登录成功页面
        
        Args:
            user_id: 用户ID
        """
        width, height = self.screen.get_size()
        
        while True:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                    width, height = self.screen.get_size()
            
            # 绘制背景
            start_color = Theme.get_color('background_gradient_start')
            end_color = Theme.get_color('background_gradient_end')
            
            for y in range(height):
                progress = y / height
                r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
                pygame.draw.line(self.screen, (r, g, b), (0, y), (width, y))
            
            # 显示成功信息
            success_text = "¡Inicio de sesión exitoso!"
            text_color = Theme.get_color('success')
            text_surface = font_manager.render_text(success_text, 'xl', height, text_color)
            text_rect = text_surface.get_rect(center=(width // 2, height // 2 - 50))
            self.screen.blit(text_surface, text_rect)
            
            # 显示用户ID
            user_text = f"Usuario ID: {user_id}"
            user_color = Theme.get_color('text')
            user_surface = font_manager.render_text(user_text, 'lg', height, user_color)
            user_rect = user_surface.get_rect(center=(width // 2, height // 2))
            self.screen.blit(user_surface, user_rect)
            
            # 显示提示
            hint_text = "Presiona ESC para salir"
            hint_color = Theme.get_color('text_secondary')
            hint_surface = font_manager.render_text(hint_text, 'md', height, hint_color)
            hint_rect = hint_surface.get_rect(center=(width // 2, height // 2 + 100))
            self.screen.blit(hint_surface, hint_rect)
            
            # 显示游戏接口提示
            game_text = "Aquí se cargará la interfaz principal del juego"
            game_surface = font_manager.render_text(game_text, 'md', height, hint_color)
            game_rect = game_surface.get_rect(center=(width // 2, height // 2 + 150))
            self.screen.blit(game_surface, game_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def run(self):
        """运行游戏主程序"""
        try:
            print("🚀 游戏启动...")

            # # 显示引导层
            # if not self.show_intro_screen():
            #     print("ℹ️ 用户在引导层退出")
            #     return
            
            # 导入场景类
            from game.scenes.welcome_scene import WelcomeScene
            from game.scenes.login_scene import LoginScene
            from game.scenes.register_scene import RegisterScene
            
            # 创建场景管理器
            scene_manager = SceneManager(self.screen)
            
            # 注册场景
            scene_manager.add_scene("welcome", WelcomeScene)
            scene_manager.add_scene("login", LoginScene)
            scene_manager.add_scene("register", RegisterScene)
            scene_manager.add_scene('game_main', MainScene)
            
            # 运行场景管理器，从欢迎页面开始
            scene_manager.run("welcome")
            
            print("🎮 游戏结束")
            
        except Exception as e:
            print(f"❌ 游戏运行失败: {e}")
            traceback.print_exc()
        finally:
            self.cleanup()

    # 删除 run_auth_system() 方法
    
    def cleanup(self):
        """清理资源"""
        try:
            print("🧹 清理游戏资源...")
            
            # 清理字体缓存
            font_manager.clear_cache()
            
            # 退出pygame
            pygame.quit()
            
            print("✅ 资源清理完成")
            
        except Exception as e:
            print(f"⚠️ 资源清理时发生错误: {e}")

def main():
    """主函数"""
    try:
        print("=" * 50)
        print("🎮 Juego de Cartas Coleccionables")
        print("📝 Pygame Edition - 重构版本")
        print("=" * 50)
        
        # 创建并运行游戏启动器
        launcher = GameLauncher()
        launcher.run()
        
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        traceback.print_exc()
    finally:
        print("👋 程序结束")
        sys.exit(0)

if __name__ == "__main__":
    main()