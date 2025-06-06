#!/usr/bin/env python3
"""
Pokédex 页面独立测试启动器
快速测试Dex页面的功能和视觉效果
"""

import pygame
import sys
import os

# 添加当前目录到Python路径，确保可以导入模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 模拟数据库管理器
class MockDatabaseManager:
    """模拟数据库管理器用于测试"""
    
    def __init__(self):
        # 模拟用户收集数据
        self.mock_collection = {
            1: {'is_shiny': False, 'caught_date': '2024-01-01'},
            3: {'is_shiny': False, 'caught_date': '2024-01-02'}, 
            5: {'is_shiny': True, 'caught_date': '2024-01-03'},   # Shiny Charmeleon
            6: {'is_shiny': False, 'caught_date': '2024-01-04'},
            9: {'is_shiny': True, 'caught_date': '2024-01-05'},   # Shiny Blastoise
            12: {'is_shiny': False, 'caught_date': '2024-01-06'},
            15: {'is_shiny': False, 'caught_date': '2024-01-07'},
            18: {'is_shiny': False, 'caught_date': '2024-01-08'},
            21: {'is_shiny': False, 'caught_date': '2024-01-09'},
            24: {'is_shiny': False, 'caught_date': '2024-01-10'},
            25: {'is_shiny': True, 'caught_date': '2024-01-11'},  # Shiny Pikachu
            27: {'is_shiny': False, 'caught_date': '2024-01-12'},
            30: {'is_shiny': False, 'caught_date': '2024-01-13'},
            33: {'is_shiny': False, 'caught_date': '2024-01-14'},
            36: {'is_shiny': False, 'caught_date': '2024-01-15'},
        }
        print(f"🎮 模拟数据库初始化 - {len(self.mock_collection)}个Pokemon已收集")
    
    def get_user_pokemon_collection(self, user_id):
        """获取用户Pokemon收集数据"""
        return self.mock_collection.copy()


# 导入Dex场景
try:
    from dex_scene import DexScene, DexColors
    print("✅ DexScene导入成功")
except ImportError:
    print("❌ 无法导入DexScene，请确保dex_scene.py在同一目录下")
    sys.exit(1)


class DexTestLauncher:
    """Dex页面测试启动器"""
    
    def __init__(self):
        # 初始化pygame
        pygame.init()
        
        # 设置显示
        self.screen_width = 1200
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("🔍 Pokédex 测试启动器")
        
        # 设置图标（如果有的话）
        try:
            icon = pygame.Surface((32, 32))
            icon.fill(DexColors.PRIMARY)
            pygame.display.set_icon(icon)
        except:
            pass
        
        # 初始化时钟
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # 创建模拟数据库
        self.db_manager = MockDatabaseManager()
        
        # 创建Dex场景
        self.dex_scene = DexScene(self.screen_width, self.screen_height, self.db_manager)
        
        # 运行状态
        self.running = True
        
        print(f"🚀 测试启动器初始化完成 - {self.screen_width}x{self.screen_height} @ {self.fps}FPS")
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                print("👋 用户关闭窗口")
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    print("👋 用户按下ESC退出")
                elif event.key == pygame.K_F11:
                    # 切换全屏
                    pygame.display.toggle_fullscreen()
                    print("🖥️ 切换全屏模式")
                elif event.key == pygame.K_F5:
                    # 重新加载场景
                    self.dex_scene = DexScene(self.screen_width, self.screen_height, self.db_manager)
                    print("🔄 重新加载Dex场景")
            
            # 传递事件给Dex场景
            result = self.dex_scene.handle_event(event)
            if result == "back_to_home":
                print("🏠 请求返回主页 - 但这是测试模式，继续运行")
    
    def update(self, dt):
        """更新逻辑"""
        self.dex_scene.update(dt)
    
    def draw(self):
        """绘制"""
        # 清除屏幕
        self.screen.fill(DexColors.BACKGROUND)
        
        # 绘制Dex场景
        self.dex_scene.draw(self.screen)
        
        # 绘制调试信息
        self._draw_debug_info()
        
        # 更新显示
        pygame.display.flip()
    
    def _draw_debug_info(self):
        """绘制调试信息"""
        font = pygame.font.Font(None, 20)
        
        # FPS信息
        fps_text = f"FPS: {self.clock.get_fps():.1f}"
        fps_surf = font.render(fps_text, True, DexColors.TEXT_MUTED)
        self.screen.blit(fps_surf, (10, self.screen_height - 30))
        
        # 控制提示
        controls = [
            "ESC: 退出",
            "F11: 全屏", 
            "F5: 重载",
            "滚轮: 滚动"
        ]
        
        for i, control in enumerate(controls):
            control_surf = font.render(control, True, DexColors.TEXT_MUTED)
            self.screen.blit(control_surf, (10, self.screen_height - 120 + i * 22))
    
    def run(self):
        """运行主循环"""
        print("🎮 开始运行Dex测试启动器...")
        print("=" * 50)
        print("🎯 控制说明:")
        print("   - 鼠标滚轮: 上下滚动")
        print("   - 点击搜索框: 输入搜索内容")
        print("   - 点击过滤标签: 筛选Pokemon")
        print("   - ESC: 退出程序")
        print("   - F11: 全屏/窗口切换")
        print("   - F5: 重新加载场景")
        print("=" * 50)
        
        while self.running:
            # 计算帧时间
            dt = self.clock.tick(self.fps) / 1000.0
            
            # 处理事件
            self.handle_events()
            
            # 更新逻辑
            self.update(dt)
            
            # 绘制
            self.draw()
        
        # 清理资源
        self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理资源...")
        self.dex_scene.cleanup()
        pygame.quit()
        print("✅ 清理完成")


def main():
    """主函数"""
    print("🚀 启动Pokédex测试程序...")
    
    try:
        launcher = DexTestLauncher()
        launcher.run()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序")
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("👋 程序结束")


if __name__ == "__main__":
    main()