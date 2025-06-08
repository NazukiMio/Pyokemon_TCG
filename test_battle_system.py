"""
战斗系统测试脚本
测试BattlePage、窗口组件和BattleController的集成
"""

import pygame
import pygame_gui
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_battle_system():
    """测试战斗系统的基本功能"""
    print("🧪 开始测试战斗系统...")
    
    # 初始化pygame
    pygame.init()
    
    # 设置窗口
    screen_size = (1200, 800)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Pokemon TCG - 战斗系统测试")
    
    # 创建UI管理器
    ui_manager = pygame_gui.UIManager(screen_size)
    
    # 模拟游戏环境
    try:
        from game.core.game_manager import GameManager
        from game.scenes.battle_page import BattlePage
        
        print("📚 初始化游戏管理器...")
        game_manager = GameManager()
        
        # 模拟用户登录
        if not game_manager.current_user_id:
            game_manager.current_user_id = 1
            print("👤 模拟用户登录: ID=1")
        
        print("⚔️ 创建战斗页面...")
        battle_page = BattlePage(
            screen_size[0], 
            screen_size[1], 
            ui_manager, 
            game_manager, 
            nav_height=0
        )
        
        # 设置回调
        def on_battle_started(battle_id):
            print(f"🎮 战斗开始回调触发: {battle_id}")
        
        battle_page.on_battle_started = on_battle_started
        
        print("✅ 战斗系统初始化完成")
        print("\n🎮 控制说明:")
        print("   点击 '卡组构建' 按钮 - 打开卡组构建窗口")
        print("   点击 '对战准备' 按钮 - 打开对战准备窗口")
        print("   ESC键 - 退出测试")
        print("   F11键 - 切换全屏")
        
        # 主循环
        clock = pygame.time.Clock()
        running = True
        
        while running:
            time_delta = clock.tick(60) / 1000.0
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                
                # 处理UI管理器事件
                ui_manager.process_events(event)
                
                # 处理战斗页面事件
                result = battle_page.handle_event(event)
                if result:
                    print(f"📝 战斗页面事件: {result}")
            
            # 更新
            ui_manager.update(time_delta)
            battle_page.update(time_delta)
            
            # 绘制
            screen.fill((240, 245, 251))  # 浅蓝灰背景
            battle_page.draw(screen)
            ui_manager.draw_ui(screen)
            
            pygame.display.flip()
        
        print("🧹 清理资源...")
        battle_page.cleanup()
        game_manager.cleanup()
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保所有必要的文件已创建")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()
        print("✅ 测试完成")

def test_battle_controller_only():
    """仅测试BattleController（不需要pygame）"""
    print("🧪 测试BattleController...")
    
    try:
        from game.core.game_manager import GameManager
        from game.core.battle.battle_controller import BattleController
        
        # 初始化
        game_manager = GameManager()
        if not game_manager.current_user_id:
            game_manager.current_user_id = 1
        
        # 检查是否有可用卡组
        user_decks = game_manager.get_user_decks()
        if not user_decks:
            print("❌ 没有可用卡组，无法测试战斗控制器")
            print("提示：请先在主程序中创建一些卡组")
            return
        
        test_deck_id = user_decks[0]['id']
        print(f"📦 使用测试卡组: {test_deck_id}")
        
        # 测试控制器
        controller = BattleController(game_manager)
        
        # 启动战斗
        result = controller.start_new_battle(test_deck_id)
        print(f"🚀 启动结果: {result}")
        
        if result["success"]:
            # 获取状态
            state = controller.get_current_state()
            print(f"📊 战斗状态: {state}")
            
            # 结束战斗
            end_result = controller.end_battle()
            print(f"🏁 结束结果: {end_result}")
        
        game_manager.cleanup()
        print("✅ BattleController测试完成")
        
    except Exception as e:
        print(f"❌ BattleController测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_window_creation():
    """测试窗口创建（不启动完整UI）"""
    print("🧪 测试窗口创建...")
    
    try:
        import pygame
        pygame.init()
        
        # 最小化pygame设置
        screen = pygame.display.set_mode((800, 600))
        ui_manager = pygame_gui.UIManager((800, 600))
        
        from game.core.game_manager import GameManager
        
        game_manager = GameManager()
        if not game_manager.current_user_id:
            game_manager.current_user_id = 1
        
        # 测试卡组构建窗口
        print("🏗️ 测试卡组构建窗口...")
        from game.scenes.windows.battle.deck_builder.deck_builder_window import DeckBuilderWindow
        
        deck_window = DeckBuilderWindow(
            rect=pygame.Rect(100, 100, 600, 400),
            ui_manager=ui_manager,
            game_manager=game_manager
        )
        print("✅ 卡组构建窗口创建成功")
        deck_window.kill()
        
        # 测试对战准备窗口
        print("⚔️ 测试对战准备窗口...")
        from game.scenes.windows.battle.battle_prep.battle_prep_window import BattlePrepWindow
        from game.core.battle.battle_controller import BattleController
        
        battle_controller = BattleController(game_manager)
        prep_window = BattlePrepWindow(
            rect=pygame.Rect(100, 100, 500, 400),
            ui_manager=ui_manager,
            game_manager=game_manager,
            battle_controller=battle_controller
        )
        print("✅ 对战准备窗口创建成功")
        prep_window.kill()
        
        game_manager.cleanup()
        pygame.quit()
        print("✅ 窗口创建测试完成")
        
    except Exception as e:
        print(f"❌ 窗口创建测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主测试入口"""
    print("🎮 Pokemon TCG 战斗系统测试套件")
    print("=" * 50)
    
    test_options = {
        "1": ("完整系统测试（需要pygame）", test_battle_system),
        "2": ("BattleController测试", test_battle_controller_only),
        "3": ("窗口创建测试", test_window_creation),
        "4": ("运行所有测试", None)
    }
    
    print("选择测试选项:")
    for key, (description, _) in test_options.items():
        print(f"  {key}. {description}")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == "4":
        # 运行所有测试
        print("\n🔄 运行所有测试...")
        test_battle_controller_only()
        print("\n" + "-" * 30)
        test_window_creation()
        print("\n" + "-" * 30)
        test_battle_system()
    elif choice in test_options and test_options[choice][1]:
        print(f"\n🔄 运行: {test_options[choice][0]}")
        test_options[choice][1]()
    else:
        print("❌ 无效选项")

if __name__ == "__main__":
    main()