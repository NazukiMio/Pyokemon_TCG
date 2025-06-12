"""
战斗系统测试脚本
用于测试和演示战斗系统的基本功能
"""

import sys
import os
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from game.core.game_manager import GameManager
from game.core.battle import BattleManager, create_action_request, ActionType
from game.core.cards.card_data import Card, Attack

def get_real_card_deck(game_manager):
    """获取真实的卡牌卡组"""
    test_card_ids = [
        "xy5-1", "det1-1", "xy2-1", "sm9-2", "xy11-1", 
        "bw1-1", "sm115-1", "sm3-1", "bw10-1", "xy7-1", 
        "sm1-1", "sm12-2", "bw1-2", "swsh35-2", "det1-3", 
        "sm9-3", "sm2-1", "xy4-1", "bw11-1", "bw9-1"
    ]
    
    deck_cards = []
    for card_id in test_card_ids:
        card = game_manager.get_card_by_id(card_id)
        if card:
            deck_cards.append(card)
        else:
            print(f"⚠️ 卡牌不存在: {card_id}")
    
    print(f"📦 获取到 {len(deck_cards)} 张真实卡牌")
    return deck_cards

def test_battle_initialization():
    """测试战斗初始化"""
    print("=" * 50)
    print("🧪 测试战斗系统初始化")
    print("=" * 50)
    
    try:
        # 创建游戏管理器
        game_manager = GameManager()
        
        # 获取真实卡组
        test_deck = get_real_card_deck(game_manager)
        if len(test_deck) < 20:
            print(f"❌ 可用卡牌不足: {len(test_deck)}/20")
            return False
        print(f"✅ 获取真实卡组: {len(test_deck)} 张卡牌")

        # 创建测试卡组记录
        deck_success, deck_id = game_manager.create_deck("测试卡组", "用于测试战斗系统")
        if not deck_success:
            print(f"❌ 创建卡组失败: {deck_id}")
            return False

        # 添加卡牌到卡组，每张卡添加2份确保卡组足够大
        for card in test_deck:
            for _ in range(2):
                success = game_manager.add_card_to_deck(deck_id, card.id, 1)
                if not success:
                    print(f"⚠️ 添加卡牌失败: {card.id}")
        
        print(f"✅ 测试卡组创建成功，ID: {deck_id}")
        
        # 创建战斗管理器
        success, message = game_manager.create_battle_manager(
            player_deck_id=deck_id,
            opponent_type="AI",
            opponent_id=1  # 简单AI
        )
        
        if success:
            print(f"✅ 战斗管理器创建成功")
            battle_manager = game_manager.get_battle_manager()
            
            # 显示战斗信息
            battle_summary = battle_manager.get_battle_summary()
            print(f"📊 战斗摘要:")
            print(f"   战斗ID: {battle_summary['battle_id']}")
            print(f"   当前回合: {battle_summary['status']['turn']}")
            print(f"   当前阶段: {battle_summary['status']['phase']}")
            print(f"   当前玩家: {battle_summary['status']['current_player']}")
            
            return True
        else:
            print(f"❌ 创建战斗管理器失败: {message}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_battle_flow():
    """测试战斗流程"""
    print("\n" + "=" * 50)
    print("🎮 测试战斗流程")
    print("=" * 50)
    
    try:
        # 初始化战斗
        game_manager = GameManager()
        test_deck = get_real_card_deck(game_manager)
        if len(test_deck) < 20:
            print(f"❌ 可用卡牌不足: {len(test_deck)}/20")
            return False
        
        deck_success, deck_id = game_manager.create_deck("流程测试卡组", "")
        if not deck_success:
            return False
        
        # # 简化：直接添加卡牌到数据库
        # for i, card in enumerate(test_deck[:20]):
        #     game_manager.card_manager.card_dao.insert_card(card)
        #     game_manager.add_card_to_deck(deck_id, card.id, 1)

        # 改为直接添加到卡组：
        for card in test_deck:
            # 每张卡添加1-2份到卡组
            for _ in range(2):
                game_manager.add_card_to_deck(deck_id, card.id, 1)
        
        success, message = game_manager.create_battle_manager(
            player_deck_id=deck_id,
            opponent_type="AI",
            opponent_id=1
        )
        
        if not success:
            print(f"❌ 初始化失败: {message}")
            return False
        
        battle_manager = game_manager.get_battle_manager()
        
        # 开始战斗
        if not battle_manager.start_battle():
            print("❌ 开始战斗失败")
            return False
        
        print("✅ 战斗已开始")
        
        # 模拟几个回合
        turn_count = 0
        max_turns = 5
        
        while not battle_manager.battle_state.is_battle_over() and turn_count < max_turns:
            print(f"\n--- 回合 {battle_manager.battle_state.turn_count + 1} ---")
            
            current_player = battle_manager.battle_state.get_current_player_id()
            player_state = battle_manager.get_player_state(current_player)
            
            print(f"当前玩家: {current_player}")
            print(f"阶段: {battle_manager.battle_state.current_phase.value}")
            
            if current_player == game_manager.current_user_id:
                # 玩家回合 - 模拟自动操作
                print("🎮 玩家回合")
                
                if battle_manager.battle_state.current_phase.value == "draw":
                    # 抽卡
                    action = create_action_request("draw_card", current_player)
                    response = battle_manager.process_player_action(action)
                    print(f"   抽卡: {response.message}")
                
                elif battle_manager.battle_state.current_phase.value == "energy":
                    # 获得能量
                    action = create_action_request("gain_energy", current_player)
                    response = battle_manager.process_player_action(action)
                    print(f"   获得能量: {response.message}")
                
                elif battle_manager.battle_state.current_phase.value == "action":
                    # 行动阶段 - 尝试攻击或结束回合
                    if player_state.can_attack():
                        action = create_action_request(
                            "attack", 
                            current_player,
                            parameters={'attack_index': 0}
                        )
                        response = battle_manager.process_player_action(action)
                        print(f"   攻击: {response.message}")
                    else:
                        # 结束回合
                        action = create_action_request("end_turn", current_player)
                        response = battle_manager.process_player_action(action)
                        print(f"   结束回合: {response.message}")
            
            else:
                # AI回合会自动处理
                print("🤖 AI回合 (自动处理)")
                time.sleep(1)  # 稍作等待观察
            
            turn_count += 1
        
        # 显示战斗结果
        battle_summary = battle_manager.get_battle_summary()
        print(f"\n🏁 战斗结束")
        print(f"   结果: {battle_summary['status']['result']}")
        print(f"   获胜者: {battle_summary['status']['winner']}")
        print(f"   总回合数: {battle_summary['status']['turn']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 战斗流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_decision():
    """测试AI决策"""
    print("\n" + "=" * 50)
    print("🤖 测试AI决策系统")
    print("=" * 50)
    
    try:
        from game.core.battle.ai_opponent import get_ai_opponent, get_random_ai_opponent, AIDifficulty
        
        # 测试获取AI对手
        ai_easy = get_random_ai_opponent(AIDifficulty.EASY)
        ai_hard = get_random_ai_opponent(AIDifficulty.HARD)
        
        print(f"✅ 简单AI: {ai_easy.name} (攻击性: {ai_easy.aggression})")
        print(f"✅ 困难AI: {ai_hard.name} (攻击性: {ai_hard.aggression})")
        
        # 测试AI个性配置
        from game.core.battle.ai_opponent import AI_OPPONENTS
        print(f"✅ 可用AI对手: {len(AI_OPPONENTS)} 个")
        for ai_id, ai_config in AI_OPPONENTS.items():
            print(f"   {ai_id}: {ai_config.name} ({ai_config.difficulty.value})")
        
        return True
        
    except Exception as e:
        print(f"❌ AI测试失败: {e}")
        return False

def test_battle_rules():
    """测试战斗规则"""
    print("\n" + "=" * 50)
    print("📋 测试战斗规则系统")
    print("=" * 50)
    
    try:
        from game.core.battle.battle_rules import BattleRules, is_valid_deck
        
        # 测试卡组验证
        # 创建临时游戏管理器用于测试
        temp_game_manager = GameManager()
        test_deck = get_real_card_deck(temp_game_manager)
        temp_game_manager.cleanup()
        
        # 测试有效卡组
        result = BattleRules.validate_deck_composition(test_deck)
        print(f"✅ 卡组验证: {result.is_valid} - {result.message}")
        
        # 测试无效卡组（太少卡牌）
        small_deck = test_deck[:5]
        result = BattleRules.validate_deck_composition(small_deck)
        print(f"❌ 小卡组验证: {result.is_valid} - {result.message}")
        
        # 测试类型相性
        fire_vs_grass = BattleRules.get_type_effectiveness("Fire", "Grass")
        water_vs_fire = BattleRules.get_type_effectiveness("Water", "Fire")
        print(f"✅ 类型相性测试:")
        print(f"   火 vs 草: {fire_vs_grass}x")
        print(f"   水 vs 火: {water_vs_fire}x")
        
        # 测试伤害计算
        damage = BattleRules.calculate_damage(30, "Fire", "Grass")
        print(f"   火系30伤害 vs 草系: {damage}")
        
        return True
        
    except Exception as e:
        print(f"❌ 规则测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎮 Pokemon TCG Battle System Test Suite")
    print("=" * 60)
    
    tests = [
        ("战斗初始化", test_battle_initialization),
        ("AI决策系统", test_ai_decision),
        ("战斗规则", test_battle_rules),
        ("战斗流程", test_battle_flow),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 运行测试: {test_name}")
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
    
    print(f"\n📊 测试结果:")
    print(f"   通过: {passed}")
    print(f"   失败: {failed}")
    print(f"   总计: {passed + failed}")
    
    if failed == 0:
        print("🎉 所有测试通过!")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")

if __name__ == "__main__":
    main()