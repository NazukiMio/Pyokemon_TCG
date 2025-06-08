from typing import Dict, Any, Optional
from game.core.battle.battle_manager import BattleManager
from game.core.game_manager import GameManager

class BattleController:
    """战斗控制器 - 单机版战斗的统一入口"""
    
    def __init__(self, game_manager: GameManager):
        """
        初始化战斗控制器
        
        Args:
            game_manager: 游戏管理器实例（来自主场景）
        """
        self.game_manager = game_manager
        self.current_battle: Optional[BattleManager] = None
    
    def start_new_battle(self, player_deck_id: int, opponent_type: str = "AI", opponent_id: int = 1) -> Dict[str, Any]:
        """
        开始新战斗
        
        Args:
            player_deck_id: 玩家卡组ID（从主场景传入）
            opponent_type: 对手类型
            opponent_id: 对手ID
            
        Returns:
            启动结果
        """
        try:
            # 清理之前的战斗
            if self.current_battle:
                self.current_battle.cleanup()
            
            # 获取当前登录用户ID
            player_id = self.game_manager.current_user_id
            if not player_id:
                return {"success": False, "error": "未登录用户"}
            
            # 验证卡组是否存在且属于用户
            deck_cards = self.game_manager.get_deck_cards(player_deck_id)
            if not deck_cards:
                return {"success": False, "error": f"卡组 {player_deck_id} 不存在或为空"}
            
            # 创建战斗管理器（使用现有的完整构造函数）
            self.current_battle = BattleManager(
                self.game_manager, 
                player_id, 
                player_deck_id,
                opponent_type,
                opponent_id
            )
            
            # 检查初始化是否成功
            if self.current_battle.battle_state and len(self.current_battle.player_states) > 0:
                # 开始战斗
                if self.current_battle.start_battle():
                    return {
                        "success": True,
                        "battle_id": self.current_battle.battle_state.battle_id,
                        "message": "战斗开始成功"
                    }
                else:
                    return {"success": False, "error": "战斗启动失败"}
            else:
                return {"success": False, "error": "战斗初始化失败"}
                
        except Exception as e:
            return {"success": False, "error": f"战斗启动异常: {e}"}
    
    def get_current_state(self) -> Dict[str, Any]:
        """获取当前战斗状态"""
        if not self.current_battle:
            return {"success": False, "error": "没有活跃的战斗"}
        
        try:
            # 使用现有的UI状态方法
            state = self.current_battle.get_game_state_for_ui()
            return {"success": True, "state": state}
            
        except Exception as e:
            return {"success": False, "error": f"获取状态失败: {e}"}
    
    def process_player_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理玩家行动"""
        if not self.current_battle:
            return {"success": False, "error": "没有活跃的战斗"}
        
        try:
            # 导入必要的类
            from game.core.battle.battle_actions import create_action_request, ActionType
            
            action_type = action_data.get("type")
            player_id = self.game_manager.current_user_id
            
            # 创建标准的ActionRequest
            if action_type == "attack":
                action_request = create_action_request(
                    ActionType.ATTACK.value, 
                    player_id,
                    parameters=action_data.get("parameters", {})
                )
            elif action_type == "end_turn":
                action_request = create_action_request(ActionType.END_TURN.value, player_id)
            elif action_type == "draw_card":
                action_request = create_action_request(ActionType.DRAW_CARD.value, player_id)
            elif action_type == "gain_energy":
                action_request = create_action_request(ActionType.GAIN_ENERGY.value, player_id)
            else:
                return {"success": False, "error": f"未知的行动类型: {action_type}"}
            
            # 使用现有的处理方法
            response = self.current_battle.process_player_action(action_request)
            
            # 转换响应格式
            result = {
                "success": response.is_success(),
                "message": response.message,
                "effects": response.effects
            }
            
            # 检查战斗是否结束
            if self.current_battle.battle_state.is_battle_over():
                result["battle_ended"] = True
                result["winner"] = self.current_battle.battle_state.winner_id
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"处理行动失败: {e}"}
    
    def end_battle(self) -> Dict[str, Any]:
        """结束当前战斗"""
        if not self.current_battle:
            return {"success": False, "error": "没有活跃的战斗"}
        
        try:
            # 获取战斗结果
            battle_summary = self.current_battle.get_battle_summary()
            
            result = {
                "success": True,
                "battle_id": self.current_battle.battle_state.battle_id,
                "result": battle_summary.get("status", {}).get("result", "unknown"),
                "winner": battle_summary.get("status", {}).get("winner"),
                "duration": self.current_battle.battle_state.get_battle_duration()
            }
            
            # 清理资源
            self.current_battle.cleanup()
            self.current_battle = None
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"结束战斗失败: {e}"}
    
    def is_battle_active(self) -> bool:
        """检查是否有活跃的战斗"""
        return self.current_battle is not None and not self.current_battle.battle_state.is_battle_over()
    
# =============================================================================
# 测试块 - 使用真实数据验证BattleController功能
# =============================================================================

if __name__ == "__main__":
    def test_battle_controller():
        """测试战斗控制器的完整流程"""
        print("🧪 开始测试BattleController...")
        
        # 创建游戏管理器并模拟登录
        print("\n--- 初始化游戏环境 ---")
        game_manager = GameManager()
        
        # 模拟用户登录（使用默认用户）
        if not game_manager.current_user_id:
            game_manager.current_user_id = 1  # 假设用户ID为1
        
        # 获取用户的卡组
        user_decks = game_manager.get_user_decks()
        if not user_decks:
            print("❌ 用户没有可用卡组，请先在主界面创建卡组")
            return
        
        test_deck_id = user_decks[0]['id']  # 使用第一个卡组
        print(f"✅ 使用用户卡组: {test_deck_id}")
        
        # 创建控制器
        controller = BattleController(game_manager)
        
        # 测试1: 启动战斗
        print("\n--- 测试1: 启动战斗 ---")
        start_result = controller.start_new_battle(test_deck_id)
        print(f"启动结果: {'✅ 成功' if start_result['success'] else '❌ 失败'}")
        
        if not start_result['success']:
            print(f"错误: {start_result['error']}")
            game_manager.cleanup()
            return
        
        print(f"战斗ID: {start_result['battle_id']}")
        
        # 测试2: 获取战斗状态
        print("\n--- 测试2: 获取战斗状态 ---")
        state_result = controller.get_current_state()
        if not state_result['success']:
            print(f"❌ 获取状态失败: {state_result['error']}")
        else:
            state = state_result['state']
            print(f"✅ 当前玩家: {state['current_player']}")
            print(f"✅ 当前阶段: {state['phase']}")
            print(f"✅ 回合数: {state['turn']}")
        
        # 测试3: 模拟几个回合的战斗
        print("\n--- 测试3: 模拟战斗流程 ---")
        for turn in range(3):
            print(f"\n第 {turn + 1} 轮测试:")
            
            # 获取当前状态
            state_result = controller.get_current_state()
            if not state_result['success']:
                break
                
            state = state_result['state']
            current_player = state["current_player"]
            print(f"当前玩家: {current_player}, 阶段: {state['phase']}")
            
            # 如果是玩家回合
            if current_player == game_manager.current_user_id:
                # 根据阶段执行对应行动
                if state["phase"] == "draw":
                    print("执行抽卡...")
                    action_result = controller.process_player_action({"type": "draw_card"})
                    print(f"抽卡结果: {action_result}")
                
                elif state["phase"] == "energy":
                    print("获得能量...")
                    action_result = controller.process_player_action({"type": "gain_energy"})
                    print(f"能量结果: {action_result}")
                
                elif state["phase"] == "action":
                    print("尝试攻击...")
                    action_result = controller.process_player_action({"type": "attack"})
                    print(f"攻击结果: {action_result}")
                    
                    # 结束回合
                    print("结束回合...")
                    end_turn_result = controller.process_player_action({"type": "end_turn"})
                    print(f"结束回合结果: {end_turn_result}")
                    
                    # 检查战斗是否结束
                    if end_turn_result.get("battle_ended"):
                        print(f"🏁 战斗结束! 获胜者: {end_turn_result.get('winner')}")
                        break
            else:
                print("🤖 AI回合 (自动处理)")
                import time
                time.sleep(1)  # 等待AI处理
        
        # 测试4: 结束战斗
        print("\n--- 测试4: 结束战斗 ---")
        if controller.is_battle_active():
            end_result = controller.end_battle()
            print(f"结束战斗结果: {end_result}")
        else:
            print("战斗已自然结束")
        
        # 清理
        game_manager.cleanup()
        print("\n🎉 BattleController测试完成!")

    # 运行测试
    test_battle_controller()