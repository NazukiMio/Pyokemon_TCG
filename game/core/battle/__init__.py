"""
战斗系统模块
集成了Pokemon TCG Pocket风格的战斗机制
"""

from .battle_manager import BattleManager
from .battle_state import BattleState, BattlePhase, GameResult, BattleAction
from .player_state import PlayerState, CardInstance
from .pokemon_instance import PokemonInstance, StatusEffect, DamageRecord
from .battle_actions import (
    ActionType, ActionResult, ActionRequest, ActionResponse,
    ActionValidator, ActionProcessor, create_action_request, get_available_actions
)
from .ai_opponent import (
    AIDecisionMaker, AIDifficulty, AIPersonality,
    get_ai_opponent, get_random_ai_opponent, AI_OPPONENTS
)

__version__ = "1.0.0"
__author__ = "Pokemon TCG Game Development Team"

# 导出主要类和函数
__all__ = [
    # 核心管理类
    'BattleManager',
    
    # 状态管理
    'BattleState',
    'PlayerState', 
    'PokemonInstance',
    
    # 枚举和数据类
    'BattlePhase',
    'GameResult',
    'BattleAction',
    'StatusEffect',
    'DamageRecord',
    'CardInstance',
    
    # 行动系统
    'ActionType',
    'ActionResult', 
    'ActionRequest',
    'ActionResponse',
    'ActionValidator',
    'ActionProcessor',
    'create_action_request',
    'get_available_actions',
    
    # AI系统
    'AIDecisionMaker',
    'AIDifficulty',
    'AIPersonality',
    'get_ai_opponent',
    'get_random_ai_opponent',
    'AI_OPPONENTS'
]

def create_battle_manager(game_manager, player_id: int, player_deck_id: int, 
                         opponent_type: str = "AI", opponent_id = None) -> BattleManager:
    """
    创建战斗管理器的便捷函数
    
    Args:
        game_manager: 游戏管理器实例
        player_id: 玩家ID
        player_deck_id: 玩家卡组ID
        opponent_type: 对手类型 ("AI" 或 "PVP")
        opponent_id: 对手ID
    
    Returns:
        战斗管理器实例
    """
    return BattleManager(game_manager, player_id, player_deck_id, opponent_type, opponent_id)

def get_battle_system_info() -> dict:
    """
    获取战斗系统信息
    
    Returns:
        系统信息字典
    """
    return {
        'version': __version__,
        'author': __author__,
        'supported_modes': ['PVE', 'PVP'],
        'ai_difficulties': [difficulty.value for difficulty in AIDifficulty],
        'available_ai_opponents': list(AI_OPPONENTS.keys()),
        'max_hand_size': 7,
        'max_bench_size': 3,
        'prize_cards_to_win': 3,
        'max_turns': 50
    }

# 模块级常量
BATTLE_CONFIG = {
    'MAX_HAND_SIZE': 7,
    'MAX_BENCH_SIZE': 3,
    'PRIZE_CARDS_TO_WIN': 3,
    'MAX_TURNS': 50,
    'INITIAL_HAND_SIZE': 5,
    'ENERGY_PER_TURN': 1,
    'MIN_DECK_SIZE': 20,
    'MAX_DECK_SIZE': 60
}

print(f"🎮 Pokemon TCG Battle System v{__version__} 已加载")
print(f"   支持模式: PVE (AI对战), PVP (玩家对战)")
print(f"   AI难度级别: {len(AI_OPPONENTS)} 种")
print(f"   战斗规则: {BATTLE_CONFIG['PRIZE_CARDS_TO_WIN']} 张奖励卡获胜")