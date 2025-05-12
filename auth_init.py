import pygame
import sys
import os
import time

# 导入游戏模块
from game.core.scene_manager import SceneManager
from game.scenes.login_scene import LoginScene
from game.scenes.register_scene import RegisterScene
from game.scenes.main_menu_scene import MainMenuScene

def main():
    """
    初始化游戏并启动认证模块
    """
    # 初始化pygame
    pygame.init()
    
    # 设置窗口标题
    pygame.display.set_caption("Juego de Cartas Coleccionables - Pygame Edition")
    
    # 获取显示器信息
    display_info = pygame.display.Info()
    screen_width = int(display_info.current_w * 0.8)
    screen_height = int(display_info.current_h * 0.8)
    
    # 创建窗口
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    
    # 设置窗口图标（如果有）
    try:
        icon_path = os.path.join("assets", "images", "icon", "game_icon.png")
        if os.path.exists(icon_path):
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
    except Exception as e:
        print(f"无法加载图标: {e}")
    
    # 创建场景管理器
    scene_manager = SceneManager(screen)
    
    # 注册场景
    scene_manager.add_scene("login", LoginScene)
    scene_manager.add_scene("register", RegisterScene)
    scene_manager.add_scene("main_menu", MainMenuScene)
    
    # 运行场景管理器，从登录场景开始
    scene_manager.run("login")
    
    # 游戏结束，清理资源
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()