# ==== synchronized_battle_controller.py ====
# 保存为: game/core/battle/synchronized_battle_controller.py

"""
同步战斗控制器 - 解决时序问题
确保界面和战斗逻辑同步
"""

from typing import Dict, Any, Optional
from game.core.battle.battle_controller import BattleController
from game.core.game_manager import GameManager

class SynchronizedBattleController(BattleController):
    """同步战斗控制器 - 修复时序问题"""
    
    def __init__(self, game_manager: GameManager):
        super().__init__(game_manager)
        self.battle_prepared = False
        self.interface_ready = False
        
    def start_new_battle_with_sync(self, player_deck_id: int, opponent_type: str = "AI", 
                                 opponent_difficulty: str = "rookie_trainer") -> Dict[str, Any]:
        """
        同步启动新战斗 - 分两个阶段
        1. 准备战斗但不开始
        2. 等待界面准备完成后开始
        """
        try:
            print(f"🚀 [同步控制器] 开始准备战斗...")
            
            # 清理前一个战斗
            if self.current_battle:
                self.current_battle.cleanup()
                
            # 获取玩家ID
            player_id = self.game_manager.current_user_id
            if not player_id:
                return {"success": False, "error": "用户未登录"}
                
            # 验证卡组
            deck_cards = self.game_manager.get_deck_cards(player_deck_id)
            if not deck_cards:
                return {"success": False, "error": f"卡组 {player_deck_id} 不存在或为空"}
                
            print(f"🔧 [同步控制器] 创建战斗管理器...")
            
            # 创建战斗管理器（但不立即开始）
            from game.core.battle.battle_manager import BattleManager
            
            self.current_battle = BattleManager(
                self.game_manager,
                player_id,
                player_deck_id,
                opponent_type,
                opponent_difficulty
            )
            
            # 验证初始化
            if not self.current_battle.battle_state or len(self.current_battle.player_states) == 0:
                return {"success": False, "error": "战斗管理器初始化失败"}
                
            self.battle_prepared = True
            print(f"✅ [同步控制器] 战斗准备完成，等待界面...")
            
            return {
                "success": True,
                "battle_id": self.current_battle.battle_state.battle_id,
                "status": "prepared",
                "message": "战斗已准备，等待界面同步"
            }
            
        except Exception as e:
            print(f"❌ [同步控制器] 准备战斗失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"准备战斗异常: {str(e)}"}
    
    def notify_interface_ready(self) -> Dict[str, Any]:
        """
        通知界面准备完成，开始战斗
        """
        if not self.battle_prepared:
            return {"success": False, "error": "战斗尚未准备"}
            
        if not self.current_battle:
            return {"success": False, "error": "没有活跃的战斗"}
            
        try:
            print(f"🎮 [同步控制器] 界面准备完成，开始战斗...")
            
            # 现在开始战斗
            success = self.current_battle.start_battle()
            
            if success:
                self.interface_ready = True
                print(f"✅ [同步控制器] 战斗成功启动")
                
                return {
                    "success": True,
                    "battle_id": self.current_battle.battle_state.battle_id,
                    "status": "started",
                    "message": "战斗已开始"
                }
            else:
                return {"success": False, "error": "启动战斗失败"}
                
        except Exception as e:
            print(f"❌ [同步控制器] 启动战斗失败: {e}")
            return {"success": False, "error": f"启动战斗异常: {str(e)}"}
    
    def get_initial_state(self) -> Dict[str, Any]:
        """
        获取初始战斗状态（用于界面初始化）
        """
        if not self.current_battle:
            return {"success": False, "error": "没有活跃的战斗"}
            
        try:
            # 获取详细的初始状态
            battle_state = self.current_battle.battle_state
            player_state = self.current_battle.get_player_state(1)
            ai_state = self.current_battle.get_player_state(999)
            
            initial_state = {
                "success": True,
                "battle_id": battle_state.battle_id,
                "current_player": battle_state.current_turn_player,
                "phase": battle_state.current_phase.value,
                "turn": battle_state.turn_count,
                "player_state": {
                    "hand_count": len(player_state.hand) if player_state else 0,
                    "deck_count": len(player_state.deck) if player_state else 0,
                    "energy_points": player_state.energy_points if player_state else 0,
                    "active_pokemon": bool(player_state.active_pokemon) if player_state else False,
                    "bench_count": len(player_state.bench_pokemon) if player_state else 0
                },
                "ai_state": {
                    "hand_count": len(ai_state.hand) if ai_state else 0,
                    "deck_count": len(ai_state.deck) if ai_state else 0,
                    "active_pokemon": bool(ai_state.active_pokemon) if ai_state else False,
                    "bench_count": len(ai_state.bench_pokemon) if ai_state else 0
                }
            }
            
            print(f"📊 [同步控制器] 初始状态: {initial_state}")
            return initial_state
            
        except Exception as e:
            print(f"❌ [同步控制器] 获取初始状态失败: {e}")
            return {"success": False, "error": f"获取状态异常: {str(e)}"}
    
    def is_synchronized(self) -> bool:
        """检查是否已同步"""
        return self.battle_prepared and self.interface_ready
    
    def reset_sync_state(self):
        """重置同步状态"""
        self.battle_prepared = False
        self.interface_ready = False
        
    def end_battle(self) -> Dict[str, Any]:
        """结束战斗并重置同步状态"""
        result = super().end_battle()
        self.reset_sync_state()
        return result

# 更新原有的BattleController，添加同步方法
class BattleControllerWithSync(BattleController):
    """为原有控制器添加同步功能"""
    
    def __init__(self, game_manager: GameManager):
        super().__init__(game_manager)
        self._sync_controller = SynchronizedBattleController(game_manager)
    
    def start_new_battle_synchronized(self, player_deck_id: int, opponent_type: str = "AI", 
                                    opponent_difficulty: str = "rookie_trainer") -> Dict[str, Any]:
        """同步启动战斗"""
        return self._sync_controller.start_new_battle_with_sync(
            player_deck_id, opponent_type, opponent_difficulty
        )
    
    def notify_interface_ready(self) -> Dict[str, Any]:
        """通知界面准备完成"""
        return self._sync_controller.notify_interface_ready()
    
    def get_initial_battle_state(self) -> Dict[str, Any]:
        """获取初始战斗状态"""
        return self._sync_controller.get_initial_state()
    
    def is_battle_synchronized(self) -> bool:
        """检查战斗是否已同步"""
        return self._sync_controller.is_synchronized()
    
    # 代理方法，确保使用同步控制器的战斗
    def get_current_state(self):
        if self._sync_controller.current_battle:
            return self._sync_controller.get_current_state()
        return super().get_current_state()
    
    def process_player_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        if self._sync_controller.current_battle:
            return self._sync_controller.process_player_action(action_data)
        return super().process_player_action(action_data)
    
    def is_battle_active(self) -> bool:
        if self._sync_controller.current_battle:
            return self._sync_controller.is_battle_active()
        return super().is_battle_active()
    
    def end_battle(self) -> Dict[str, Any]:
        if self._sync_controller.current_battle:
            return self._sync_controller.end_battle()
        return super().end_battle()