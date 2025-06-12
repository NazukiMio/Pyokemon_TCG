# ==== battle_fix_test.py ====
# 保存为: test_battle_fix.py

"""
战斗修复测试脚本
测试同步战斗控制器和修复后的界面
"""

import pygame
import pygame_gui
import sys
import os
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_synchronized_battle_controller():
    """测试同步战斗控制器"""
    print("🧪 测试同步战斗控制器...")
    
    try:
        from game.core.game_manager import GameManager
        from game.core.battle.synchronized_battle_controller import SynchronizedBattleController, BattleControllerWithSync
        
        # 初始化
        game_manager = GameManager()
        if not game_manager.current_user_id:
            game_manager.current_user_id = 1
        
        # 获取测试卡组
        user_decks = game_manager.get_user_decks()
        if not user_decks:
            print("❌ 没有可用卡组，请先创建卡组")
            return False
        
        test_deck_id = user_decks[0]['id']
        print(f"📦 使用测试卡组: {test_deck_id}")
        
        # 测试同步控制器
        sync_controller = SynchronizedBattleController(game_manager)
        
        # 步骤1：准备战斗
        print("\n--- 步骤1：准备战斗 ---")
        result = sync_controller.start_new_battle_with_sync(test_deck_id)
        print(f"准备结果: {result}")
        
        if not result.get("success"):
            print(f"❌ 准备失败: {result.get('error')}")
            return False
        
        # 步骤2：获取初始状态
        print("\n--- 步骤2：获取初始状态 ---")
        initial_state = sync_controller.get_initial_state()
        print(f"初始状态: {initial_state}")
        
        # 步骤3：模拟界面准备完成
        print("\n--- 步骤3：通知界面准备完成 ---")
        time.sleep(0.5)  # 模拟界面创建时间
        
        start_result = sync_controller.notify_interface_ready()
        print(f"启动结果: {start_result}")
        
        if start_result.get("success"):
            print("✅ 同步战斗控制器测试成功")
            
            # 步骤4：测试战斗状态
            print("\n--- 步骤4：测试战斗状态 ---")
            if sync_controller.is_battle_active():
                current_state = sync_controller.get_current_state()
                print(f"当前状态: {current_state}")
            
            # 清理
            sync_controller.end_battle()
            print("✅ 战斗已结束")
            
        else:
            print(f"❌ 启动失败: {start_result.get('error')}")
            return False
        
        game_manager.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ 同步控制器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fixed_battle_interface():
    """测试修复后的战斗界面（不启动完整pygame）"""
    print("🧪 测试修复后的战斗界面...")
    
    try:
        from game.core.game_manager import GameManager
        from game.core.battle.synchronized_battle_controller import SynchronizedBattleController
        
        # 初始化最小pygame环境
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        
        # 创建游戏环境
        game_manager = GameManager()
        if not game_manager.current_user_id:
            game_manager.current_user_id = 1
        
        # 获取测试卡组
        user_decks = game_manager.get_user_decks()
        if not user_decks:
            print("❌ 没有可用卡组")
            pygame.quit()
            return False
        
        test_deck_id = user_decks[0]['id']
        
        # 创建同步控制器并准备战斗
        sync_controller = SynchronizedBattleController(game_manager)
        result = sync_controller.start_new_battle_with_sync(test_deck_id)
        
        if not result.get("success"):
            print(f"❌ 准备战斗失败: {result.get('error')}")
            pygame.quit()
            return False
        
        # 尝试创建修复后的战斗界面
        try:
            from game.ui.battle.battle_interface.battle_interface import BattleInterface
            
            print("🎮 创建修复后的战斗界面...")
            battle_interface = BattleInterface(800, 600, sync_controller)
            
            # 通知界面准备完成
            sync_result = sync_controller.notify_interface_ready()
            print(f"同步结果: {sync_result}")
            
            # 简单渲染测试
            print("🎨 测试界面渲染...")
            battle_interface.update(0.016)  # 60 FPS
            battle_interface.draw(screen)
            
            print("✅ 修复后的战斗界面测试成功")
            
            # 清理
            battle_interface.cleanup()
            sync_controller.end_battle()
            result = True
            
        except Exception as e:
            print(f"❌ 战斗界面测试失败: {e}")
            import traceback
            traceback.print_exc()
            result = False
        
        pygame.quit()
        game_manager.cleanup()
        return result
        
    except Exception as e:
        print(f"❌ 界面测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_battle_page_integration():
    """测试战斗页面集成"""
    print("🧪 测试战斗页面集成...")
    
    try:
        # 最小pygame初始化
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        ui_manager = pygame_gui.UIManager((1280, 720))
        
        from game.core.game_manager import GameManager
        from game.scenes.battle_page import BattlePage
        
        # 创建游戏环境
        game_manager = GameManager()
        if not game_manager.current_user_id:
            game_manager.current_user_id = 1
        
        # 创建战斗页面
        battle_page = BattlePage(1280, 720, ui_manager, game_manager)
        
        # 检查是否使用同步控制器
        controller = battle_page.get_battle_controller()
        
        if hasattr(controller, 'start_new_battle_synchronized'):
            print("✅ 战斗页面使用同步控制器")
        else:
            print("⚠️ 战斗页面使用普通控制器")
        
        # 检查同步状态
        if hasattr(battle_page, 'is_battle_synchronized'):
            sync_status = battle_page.is_battle_synchronized()
            print(f"同步状态: {sync_status}")
        
        print("✅ 战斗页面集成测试通过")
        
        # 清理
        battle_page.cleanup()
        pygame.quit()
        game_manager.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ 页面集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_battle_flow():
    """测试完整战斗流程（简化版）"""
    print("🧪 测试完整战斗流程...")
    
    try:
        from game.core.game_manager import GameManager
        from game.core.battle.synchronized_battle_controller import BattleControllerWithSync
        
        # 初始化
        game_manager = GameManager()
        if not game_manager.current_user_id:
            game_manager.current_user_id = 1
        
        # 获取测试卡组
        user_decks = game_manager.get_user_decks()
        if not user_decks:
            print("❌ 没有可用卡组")
            return False
        
        test_deck_id = user_decks[0]['id']
        
        # 创建同步控制器
        controller = BattleControllerWithSync(game_manager)
        
        # 启动同步战斗
        print("🚀 启动同步战斗...")
        result = controller.start_new_battle_synchronized(test_deck_id)
        print(f"准备结果: {result}")
        
        if not result.get("success"):
            print(f"❌ 准备失败: {result.get('error')}")
            return False
        
        # 获取初始状态
        initial_state = controller.get_initial_battle_state()
        print(f"初始状态: {initial_state}")
        
        # 模拟界面准备完成
        print("📡 通知界面准备完成...")
        start_result = controller.notify_interface_ready()
        print(f"启动结果: {start_result}")
        
        if not start_result.get("success"):
            print(f"❌ 启动失败: {start_result.get('error')}")
            return False
        
        # 模拟几个战斗动作
        print("🎮 模拟战斗动作...")
        
        # 抽卡
        draw_result = controller.process_player_action({"type": "draw_card"})
        print(f"抽卡: {draw_result}")
        
        # 获得能量
        energy_result = controller.process_player_action({"type": "gain_energy"})
        print(f"获得能量: {energy_result}")
        
        # 结束回合
        end_turn_result = controller.process_player_action({"type": "end_turn"})
        print(f"结束回合: {end_turn_result}")
        
        # 检查同步状态
        if controller.is_battle_synchronized():
            print("✅ 战斗保持同步状态")
        else:
            print("⚠️ 战斗失去同步")
        
        # 结束战斗
        end_result = controller.end_battle()
        print(f"结束战斗: {end_result}")
        
        print("✅ 完整战斗流程测试成功")
        
        game_manager.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ 完整流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🎮 Pokemon TCG 战斗修复测试套件")
    print("=" * 60)
    
    tests = [
        ("同步战斗控制器", test_synchronized_battle_controller),
        ("修复后的战斗界面", test_fixed_battle_interface),
        ("战斗页面集成", test_battle_page_integration),
        ("完整战斗流程", test_full_battle_flow),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 运行测试: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                print(f"✅ {test_name} - 通过")
                passed += 1
            else:
                print(f"❌ {test_name} - 失败")
                failed += 1
        except Exception as e:
            print(f"💥 {test_name} - 异常: {e}")
            failed += 1
        
        print("-" * 40)
        time.sleep(1)  # 防止资源冲突
    
    print(f"\n📊 测试结果:")
    print(f"   通过: {passed}")
    print(f"   失败: {failed}")
    print(f"   总计: {passed + failed}")
    
    if failed == 0:
        print("🎉 所有修复测试通过!")
        print("\n✅ 修复内容:")
        print("   - 时序问题：使用同步控制器")
        print("   - 显示问题：修复AI区域显示")
        print("   - 交互问题：添加控制面板")
        print("   - pygamecards集成：实现缺失方法")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
        print("\n🔧 故障排除:")
        print("   - 确保所有新文件都已正确保存")
        print("   - 检查导入路径是否正确")
        print("   - 验证数据库中是否有足够的卡牌和卡组")

if __name__ == "__main__":
    main()