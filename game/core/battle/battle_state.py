"""
战斗状态管理
管理整个战斗的状态信息
"""

import time
import json
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass

class BattlePhase(Enum):
    """战斗阶段枚举"""
    SETUP = "setup"           # 初始化阶段
    DRAW = "draw"             # 抽卡阶段
    ENERGY = "energy"         # 能量阶段
    ACTION = "action"         # 行动阶段
    END_TURN = "end_turn"     # 回合结束
    BATTLE_END = "battle_end" # 战斗结束

class GameResult(Enum):
    """游戏结果枚举"""
    ONGOING = "ongoing"
    PLAYER_WIN = "player_win"
    OPPONENT_WIN = "opponent_win"
    DRAW = "draw"
    FORFEIT = "forfeit"

@dataclass
class BattleAction:
    """战斗行动数据类"""
    action_type: str          # 行动类型
    player_id: int           # 执行玩家ID
    source_pokemon: Optional[str] = None  # 源Pokemon ID
    target_pokemon: Optional[str] = None  # 目标Pokemon ID
    card_id: Optional[str] = None         # 使用的卡牌ID
    damage: int = 0          # 造成的伤害
    effects: List[str] = None # 附加效果
    timestamp: float = None   # 时间戳
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = []
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'action_type': self.action_type,
            'player_id': self.player_id,
            'source_pokemon': self.source_pokemon,
            'target_pokemon': self.target_pokemon,
            'card_id': self.card_id,
            'damage': self.damage,
            'effects': self.effects,
            'timestamp': self.timestamp
        }

class BattleState:
    """战斗状态管理类"""
    # 定义AI玩家ID
    AI_PLAYER_ID = 999

    def __init__(self, battle_id: int, player1_id: int, player2_id: Optional[int] = None):
        """
        初始化战斗状态
        
        Args:
            battle_id: 战斗ID
            player1_id: 玩家1 ID
            player2_id: 玩家2 ID (None表示AI对战)
        """
        self.battle_id = battle_id
        self.player1_id = player1_id
        
        # 如果是AI对战，设置AI玩家ID
        if player2_id is None:
            self.player2_id = self.AI_PLAYER_ID  # AI玩家ID
            self.is_ai_battle = True
        else:
            self.player2_id = player2_id
            self.is_ai_battle = False
        
        # 战斗流程状态
        self.current_phase = BattlePhase.SETUP
        self.current_turn_player = player1_id
        self.turn_count = 0
        self.result = GameResult.ONGOING
        self.winner_id = None
        
        # 时间记录
        self.start_time = time.time()
        self.end_time = None
        
        # 行动历史
        self.action_history: List[BattleAction] = []
        self.turn_history: List[Dict[str, Any]] = []
        
        # 游戏规则设置
        self.max_turns = 50  # 最大回合数
        self.prize_cards_to_win = 3  # 获胜需要的奖励卡数量
        
        print(f"🎮 战斗状态初始化完成: Battle {battle_id}")
        print(f"   玩家1: {player1_id}")
        print(f"   玩家2: {player2_id or 'AI'}")
    
    def next_phase(self) -> BattlePhase:
        """进入下一阶段"""
        phase_order = [
            BattlePhase.SETUP,
            BattlePhase.DRAW,
            BattlePhase.ENERGY,
            BattlePhase.ACTION,
            BattlePhase.END_TURN
        ]
        
        if self.current_phase == BattlePhase.SETUP:
            self.current_phase = BattlePhase.DRAW
        elif self.current_phase == BattlePhase.DRAW:
            self.current_phase = BattlePhase.ENERGY
        elif self.current_phase == BattlePhase.ENERGY:
            self.current_phase = BattlePhase.ACTION
        elif self.current_phase == BattlePhase.ACTION:
            self.current_phase = BattlePhase.END_TURN
        elif self.current_phase == BattlePhase.END_TURN:
            # 回合结束，切换玩家
            self.switch_turn()
            self.current_phase = BattlePhase.DRAW
        
        print(f"🔄 阶段切换: {self.current_phase.value}")
        return self.current_phase
    
    def switch_turn(self):
        """切换回合"""
        if self.current_turn_player == self.player1_id:
            self.current_turn_player = self.player2_id or self.AI_PLAYER_ID # AI用999表示
        else:
            self.current_turn_player = self.player1_id
            self.turn_count += 1
        
        # 记录回合历史
        self.turn_history.append({
            'turn': self.turn_count,
            'player': self.current_turn_player,
            'timestamp': time.time()
        })
        
        print(f"⏭️ 回合切换: 第{self.turn_count}回合, 当前玩家: {self.current_turn_player}")
    
    def add_action(self, action: BattleAction):
        """添加行动到历史"""
        self.action_history.append(action)
        print(f"📝 记录行动: {action.action_type} by {action.player_id}")
    
    def end_battle(self, result: GameResult, winner_id: Optional[int] = None):
        """结束战斗"""
        self.result = result
        self.winner_id = winner_id
        self.current_phase = BattlePhase.BATTLE_END
        self.end_time = time.time()
        
        duration = self.get_battle_duration()
        print(f"🏁 战斗结束!")
        print(f"   结果: {result.value}")
        print(f"   获胜者: {winner_id or '无'}")
        print(f"   持续时间: {duration:.1f}秒")
        print(f"   总回合数: {self.turn_count}")
    
    def is_battle_over(self) -> bool:
        """检查战斗是否结束"""
        return self.result != GameResult.ONGOING
    
    def get_battle_duration(self) -> float:
        """获取战斗持续时间（秒）"""
        end_time = self.end_time or time.time()
        return end_time - self.start_time
    
    def get_current_player_id(self) -> int:
        """获取当前回合玩家ID"""
        return self.current_turn_player
    
    def is_player_turn(self, player_id: int) -> bool:
        """检查是否是指定玩家的回合"""
        return self.current_turn_player == player_id
    
    def get_opponent_id(self, player_id: int) -> Optional[int]:
        """获取对手ID"""
        print(f"🔍 获取对手ID: 请求玩家={player_id}, player1_id={self.player1_id}, player2_id={self.player2_id}")
        
        if player_id == self.player1_id:
            print(f"🔍 返回player2_id: {self.player2_id}")
            return self.player2_id
        elif player_id == self.player2_id:
            print(f"🔍 返回player1_id: {self.player1_id}")
            return self.player1_id
        else:
            print(f"🔍 未找到匹配的玩家ID")
            return None
    
    def can_perform_action(self, player_id: int, action_type: str) -> bool:
        """检查玩家是否可以执行指定行动"""
        # 基本检查：是否是玩家回合
        if not self.is_player_turn(player_id):
            return False
        
        # 检查战斗是否结束
        if self.is_battle_over():
            return False
        
        # 根据当前阶段和行动类型判断
        if self.current_phase == BattlePhase.SETUP:
            return action_type in ["setup_pokemon", "mulligan"]
        elif self.current_phase == BattlePhase.DRAW:
            return action_type == "draw_card"
        elif self.current_phase == BattlePhase.ENERGY:
            return action_type == "gain_energy"
        elif self.current_phase == BattlePhase.ACTION:
            return action_type in [
                "play_pokemon", "evolve_pokemon", "attack", 
                "retreat", "use_trainer", "end_turn"
            ]
        elif self.current_phase == BattlePhase.END_TURN:
            return action_type == "end_turn"
        
        return False
    
    def get_last_action(self) -> Optional[BattleAction]:
        """获取最后一个行动"""
        return self.action_history[-1] if self.action_history else None
    
    def get_actions_by_turn(self, turn: int) -> List[BattleAction]:
        """获取指定回合的所有行动"""
        turn_start_time = None
        turn_end_time = None
        
        # 找到回合的时间范围
        for i, turn_record in enumerate(self.turn_history):
            if turn_record['turn'] == turn:
                turn_start_time = turn_record['timestamp']
                if i + 1 < len(self.turn_history):
                    turn_end_time = self.turn_history[i + 1]['timestamp']
                break
        
        if turn_start_time is None:
            return []
        
        # 筛选该回合的行动
        turn_actions = []
        for action in self.action_history:
            if action.timestamp >= turn_start_time:
                if turn_end_time is None or action.timestamp < turn_end_time:
                    turn_actions.append(action)
        
        return turn_actions
    
    def get_actions_by_player(self, player_id: int) -> List[BattleAction]:
        """获取指定玩家的所有行动"""
        return [action for action in self.action_history if action.player_id == player_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于数据库存储）"""
        return {
            'battle_id': self.battle_id,
            'player1_id': self.player1_id,
            'player2_id': self.player2_id,
            'is_ai_battle': self.is_ai_battle,
            'current_phase': self.current_phase.value,
            'current_turn_player': self.current_turn_player,
            'turn_count': self.turn_count,
            'result': self.result.value,
            'winner_id': self.winner_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'battle_duration': self.get_battle_duration(),
            'max_turns': self.max_turns,
            'prize_cards_to_win': self.prize_cards_to_win,
            'action_count': len(self.action_history),
            'actions': [action.to_dict() for action in self.action_history],
            'turn_history': self.turn_history
        }
    
    def get_battle_summary(self) -> Dict[str, Any]:
        """获取战斗摘要信息"""
        return {
            'battle_id': self.battle_id,
            'players': {
                'player1': self.player1_id,
                'player2': self.player2_id or 'AI'
            },
            'status': {
                'phase': self.current_phase.value,
                'turn': self.turn_count,
                'current_player': self.current_turn_player,
                'result': self.result.value,
                'winner': self.winner_id
            },
            'timing': {
                'duration': self.get_battle_duration(),
                'started_at': self.start_time,
                'ended_at': self.end_time
            },
            'statistics': {
                'total_actions': len(self.action_history),
                'player1_actions': len(self.get_actions_by_player(self.player1_id)),
                'player2_actions': len(self.get_actions_by_player(self.player2_id or 999))
            }
        }
    
    def reset_to_phase(self, phase: BattlePhase):
        """重置到指定阶段（调试用）"""
        self.current_phase = phase
        print(f"🔄 手动重置到阶段: {phase.value}")
    
    def force_end_battle(self, winner_id: Optional[int] = None):
        """强制结束战斗"""
        self.end_battle(GameResult.FORFEIT, winner_id)
        print("⚠️ 战斗被强制结束")
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Battle({self.battle_id}): Turn {self.turn_count}, Phase {self.current_phase.value}, Player {self.current_turn_player}"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"BattleState(id={self.battle_id}, p1={self.player1_id}, p2={self.player2_id}, turn={self.turn_count})"