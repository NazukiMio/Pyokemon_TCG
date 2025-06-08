"""
战斗行动系统
定义和处理各种战斗行动
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import time

class ActionType(Enum):
    """行动类型枚举"""
    # 基础行动
    DRAW_CARD = "draw_card"
    GAIN_ENERGY = "gain_energy"
    END_TURN = "end_turn"
    
    # Pokemon相关
    PLAY_POKEMON = "play_pokemon"
    EVOLVE_POKEMON = "evolve_pokemon"
    ATTACK = "attack"
    RETREAT = "retreat"
    SWITCH_ACTIVE = "switch_active"
    
    # 卡牌使用
    USE_TRAINER = "use_trainer"
    USE_ITEM = "use_item"
    USE_SUPPORTER = "use_supporter"
    
    # 特殊行动
    MULLIGAN = "mulligan"
    TAKE_PRIZE = "take_prize"
    DISCARD = "discard"
    SURRENDER = "surrender"

class ActionResult(Enum):
    """行动结果枚举"""
    SUCCESS = "success"
    FAILED = "failed"
    INVALID = "invalid"
    NOT_ALLOWED = "not_allowed"
    INSUFFICIENT_RESOURCES = "insufficient_resources"

@dataclass
class ActionRequest:
    """行动请求数据类"""
    action_type: ActionType
    player_id: int
    source_id: Optional[str] = None      # 源卡牌/Pokemon ID
    target_id: Optional[str] = None      # 目标卡牌/Pokemon ID
    parameters: Dict[str, Any] = None    # 额外参数
    timestamp: float = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
        if self.timestamp is None:
            self.timestamp = time.time()
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """获取参数值"""
        return self.parameters.get(key, default)
    
    def set_parameter(self, key: str, value: Any):
        """设置参数值"""
        self.parameters[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'action_type': self.action_type.value,
            'player_id': self.player_id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'parameters': self.parameters,
            'timestamp': self.timestamp
        }

@dataclass
class ActionResponse:
    """行动响应数据类"""
    result: ActionResult
    action_request: ActionRequest
    message: str = ""
    data: Dict[str, Any] = None
    effects: List[str] = None
    next_actions: List[ActionType] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.effects is None:
            self.effects = []
        if self.next_actions is None:
            self.next_actions = []
    
    def is_success(self) -> bool:
        """检查是否成功"""
        return self.result == ActionResult.SUCCESS
    
    def add_effect(self, effect: str):
        """添加效果描述"""
        self.effects.append(effect)
    
    def add_data(self, key: str, value: Any):
        """添加数据"""
        self.data[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'result': self.result.value,
            'action_request': self.action_request.to_dict(),
            'message': self.message,
            'data': self.data,
            'effects': self.effects,
            'next_actions': [action.value for action in self.next_actions]
        }

class ActionValidator:
    """行动验证器"""
    
    @staticmethod
    def validate_basic_requirements(request: ActionRequest, battle_state, player_state) -> Optional[str]:
        """
        验证基础要求
        
        Returns:
            错误信息，None表示验证通过
        """
        # 检查是否是玩家回合
        if not battle_state.is_player_turn(request.player_id):
            return "不是你的回合"
        
        # 检查战斗是否结束
        if battle_state.is_battle_over():
            return "战斗已结束"
        
        # 检查玩家状态
        if player_state is None:
            return "玩家状态不存在"
        
        return None
    
    @staticmethod
    def validate_draw_card(request: ActionRequest, battle_state, player_state) -> Optional[str]:
        """验证抽卡行动"""
        if len(player_state.deck) == 0:
            return "卡组为空，无法抽卡"
        
        from game.core.battle.battle_state import BattlePhase
        if battle_state.current_phase != BattlePhase.DRAW:
            return "当前阶段不能抽卡"
        
        return None
    
    @staticmethod
    def validate_gain_energy(request: ActionRequest, battle_state, player_state) -> Optional[str]:
        """验证获得能量行动"""
        from game.core.battle.battle_state import BattlePhase
        if battle_state.current_phase != BattlePhase.ENERGY:
            return "当前阶段不能获得能量"
        
        return None
    
    @staticmethod
    def validate_play_pokemon(request: ActionRequest, battle_state, player_state) -> Optional[str]:
        """验证放置Pokemon行动"""
        from game.core.battle.battle_state import BattlePhase
        if battle_state.current_phase != BattlePhase.ACTION:
            return "当前阶段不能放置Pokemon"
        
        # 检查手牌中是否有该Pokemon
        pokemon_card = None
        for card in player_state.hand:
            if card.instance_id == request.source_id:
                pokemon_card = card
                break
        
        if not pokemon_card:
            return "手牌中没有指定的Pokemon"
        
        if not pokemon_card.card.hp:
            return "该卡牌不是Pokemon"
        
        # 检查后备区是否有空位
        if len(player_state.bench_pokemon) >= player_state.max_bench_size:
            return "后备区已满"
        
        return None
    
    @staticmethod
    def validate_attack(request: ActionRequest, battle_state, player_state) -> Optional[str]:
        """验证攻击行动"""
        from game.core.battle.battle_state import BattlePhase
        if battle_state.current_phase != BattlePhase.ACTION:
            return "当前阶段不能攻击"
        
        # 检查是否有前排Pokemon
        if not player_state.active_pokemon:
            return "没有前排Pokemon"
        
        if not player_state.active_pokemon.can_attack():
            return "前排Pokemon无法攻击"
        
        # 检查攻击技能索引
        attack_index = request.get_parameter('attack_index', 0)
        if attack_index >= len(player_state.active_pokemon.attacks):
            return "攻击技能不存在"
        
        # 检查能量需求
        attack = player_state.active_pokemon.attacks[attack_index]
        energy_cost = player_state.active_pokemon._get_attack_energy_cost(attack)
        if player_state.energy_points < energy_cost:
            return f"能量不足，需要 {energy_cost} 点能量"
        
        return None
    
    @staticmethod
    def validate_retreat(request: ActionRequest, battle_state, player_state) -> Optional[str]:
        """验证撤退行动"""
        from game.core.battle.battle_state import BattlePhase
        if battle_state.current_phase != BattlePhase.ACTION:
            return "当前阶段不能撤退"
        
        if not player_state.active_pokemon:
            return "没有前排Pokemon"
        
        if not player_state.active_pokemon.can_retreat():
            return "前排Pokemon无法撤退"
        
        # 检查后备区是否有Pokemon
        if len(player_state.bench_pokemon) == 0:
            return "后备区没有Pokemon"
        
        # 检查目标Pokemon
        target_pokemon = None
        for pokemon in player_state.bench_pokemon:
            if pokemon.instance_id == request.target_id:
                target_pokemon = pokemon
                break
        
        if not target_pokemon:
            return "目标Pokemon不在后备区"
        
        # 检查撤退能量
        retreat_cost = request.get_parameter('energy_cost', 1)
        if player_state.energy_points < retreat_cost:
            return f"能量不足，撤退需要 {retreat_cost} 点能量"
        
        return None

class ActionProcessor:
    """行动处理器"""
    
    def __init__(self, battle_manager):
        """
        初始化行动处理器
        
        Args:
            battle_manager: 战斗管理器实例
        """
        self.battle_manager = battle_manager
    
    def process_action(self, request: ActionRequest) -> ActionResponse:
        """
        处理行动请求
        
        Args:
            request: 行动请求
        
        Returns:
            行动响应
        """
        # 获取战斗状态和玩家状态
        battle_state = self.battle_manager.battle_state
        player_state = self.battle_manager.get_player_state(request.player_id)
        
        # 基础验证
        error = ActionValidator.validate_basic_requirements(request, battle_state, player_state)
        if error:
            return ActionResponse(
                result=ActionResult.NOT_ALLOWED,
                action_request=request,
                message=error
            )
        
        # 根据行动类型处理
        if request.action_type == ActionType.DRAW_CARD:
            return self._process_draw_card(request, battle_state, player_state)
        elif request.action_type == ActionType.GAIN_ENERGY:
            return self._process_gain_energy(request, battle_state, player_state)
        elif request.action_type == ActionType.PLAY_POKEMON:
            return self._process_play_pokemon(request, battle_state, player_state)
        elif request.action_type == ActionType.ATTACK:
            return self._process_attack(request, battle_state, player_state)
        elif request.action_type == ActionType.RETREAT:
            return self._process_retreat(request, battle_state, player_state)
        elif request.action_type == ActionType.END_TURN:
            return self._process_end_turn(request, battle_state, player_state)
        elif request.action_type == ActionType.SURRENDER:
            return self._process_surrender(request, battle_state, player_state)
        else:
            return ActionResponse(
                result=ActionResult.INVALID,
                action_request=request,
                message=f"未支持的行动类型: {request.action_type.value}"
            )
    
    def _process_draw_card(self, request: ActionRequest, battle_state, player_state) -> ActionResponse:
        """处理抽卡行动"""
        # 验证
        error = ActionValidator.validate_draw_card(request, battle_state, player_state)
        if error:
            return ActionResponse(result=ActionResult.FAILED, action_request=request, message=error)
        
        # 执行抽卡
        count = request.get_parameter('count', 1)
        drawn_cards = player_state.draw_card(count)
        
        response = ActionResponse(
            result=ActionResult.SUCCESS,
            action_request=request,
            message=f"抽取了 {len(drawn_cards)} 张卡"
        )
        
        response.add_data('drawn_cards', [card.to_dict() for card in drawn_cards])
        response.add_effect(f"抽取 {len(drawn_cards)} 张卡")
        
        # 自动进入下一阶段
        battle_state.next_phase()
        
        return response
    
    def _process_gain_energy(self, request: ActionRequest, battle_state, player_state) -> ActionResponse:
        """处理获得能量行动"""
        # 验证
        error = ActionValidator.validate_gain_energy(request, battle_state, player_state)
        if error:
            return ActionResponse(result=ActionResult.FAILED, action_request=request, message=error)
        
        # 获得能量
        amount = request.get_parameter('amount', player_state.max_energy_per_turn)
        player_state.add_energy(amount)
        
        response = ActionResponse(
            result=ActionResult.SUCCESS,
            action_request=request,
            message=f"获得 {amount} 点能量"
        )
        
        response.add_data('energy_gained', amount)
        response.add_data('total_energy', player_state.energy_points)
        response.add_effect(f"获得 {amount} 点能量")
        
        # 自动进入下一阶段
        battle_state.next_phase()
        
        return response
    
    def _process_play_pokemon(self, request: ActionRequest, battle_state, player_state) -> ActionResponse:
        """处理放置Pokemon行动"""
        # 验证
        error = ActionValidator.validate_play_pokemon(request, battle_state, player_state)
        if error:
            return ActionResponse(result=ActionResult.FAILED, action_request=request, message=error)
        
        # 找到Pokemon卡
        pokemon_card = None
        for card in player_state.hand:
            if card.instance_id == request.source_id:
                pokemon_card = card
                break
        
        # 放置Pokemon
        success = player_state.play_pokemon_to_bench(pokemon_card)
        
        if success:
            response = ActionResponse(
                result=ActionResult.SUCCESS,
                action_request=request,
                message=f"放置 {pokemon_card.card.name} 到后备区"
            )
            
            response.add_data('pokemon_placed', pokemon_card.to_dict())
            response.add_effect(f"放置 {pokemon_card.card.name}")
            
            # 如果没有前排Pokemon，自动设置为前排
            if not player_state.active_pokemon:
                new_pokemon = player_state.bench_pokemon[-1]  # 刚放置的Pokemon
                player_state.set_active_pokemon(new_pokemon)
                response.add_effect(f"{pokemon_card.card.name} 成为前排Pokemon")
        else:
            response = ActionResponse(
                result=ActionResult.FAILED,
                action_request=request,
                message="放置Pokemon失败"
            )
        
        return response
    
    def _process_attack(self, request: ActionRequest, battle_state, player_state) -> ActionResponse:
        """处理攻击行动"""
        print(f"🔍 调试攻击: 玩家ID={player_state.player_id}")
            
        opponent_state = self.battle_manager.get_opponent_state(player_state.player_id)
        print(f"🔍 对手状态: {opponent_state}")
        print(f"🔍 可用玩家状态: {list(self.battle_manager.player_states.keys())}")
        
        if not opponent_state:
            return ActionResponse(
                result=ActionResult.FAILED,
                action_request=request,
                message="无法找到对手"
            )
    
        # 验证
        error = ActionValidator.validate_attack(request, battle_state, player_state)
        if error:
            return ActionResponse(result=ActionResult.FAILED, action_request=request, message=error)
        
        # # 获取目标
        # opponent_id = battle_state.get_opponent_id(request.player_id)
        # 获取对手状态
        opponent_state = self.battle_manager.get_opponent_state(player_state.player_id)
        if not opponent_state:
            return ActionResponse(
                result=ActionResult.FAILED,
                action_request=request,
                message="无法找到对手"
            )

        target_pokemon = opponent_state.active_pokemon
        
        if not target_pokemon:
            return ActionResponse(
                result=ActionResult.FAILED,
                action_request=request,
                message="对手没有前排Pokemon"
            )
        
        # 执行攻击
        attack_index = request.get_parameter('attack_index', 0)
        attack_result = player_state.active_pokemon.perform_attack(
            attack_index, target_pokemon, player_state.energy_points
        )
        
        if not attack_result['success']:
            return ActionResponse(
                result=ActionResult.FAILED,
                action_request=request,
                message=attack_result.get('reason', '攻击失败')
            )
        
        # 消耗能量
        energy_cost = attack_result['energy_cost']
        player_state.spend_energy(energy_cost)
        
        # 创建响应
        response = ActionResponse(
            result=ActionResult.SUCCESS,
            action_request=request,
            message=f"{player_state.active_pokemon.card.name} 攻击 {target_pokemon.card.name}"
        )
        
        response.add_data('attack_result', attack_result)
        response.add_effect(f"造成 {attack_result['damage_dealt']} 点伤害")
        
        # 检查击倒
        if attack_result['target_knocked_out']:
            opponent_state.knockout_pokemon(target_pokemon)
            player_state.take_prize_card()
            response.add_effect(f"{target_pokemon.card.name} 被击倒")
            response.add_effect("获得1张奖励卡")
            
            # 检查获胜条件
            if player_state.check_win_condition():
                battle_state.end_battle(
                    battle_state.GameResult.PLAYER_WIN if request.player_id == battle_state.player1_id else battle_state.GameResult.OPPONENT_WIN,
                    request.player_id
                )
                response.add_effect("获得胜利!")
        
        return response
    
    def _process_retreat(self, request: ActionRequest, battle_state, player_state) -> ActionResponse:
        """处理撤退行动"""
        # 验证
        error = ActionValidator.validate_retreat(request, battle_state, player_state)
        if error:
            return ActionResponse(result=ActionResult.FAILED, action_request=request, message=error)
        
        # 找到目标Pokemon
        target_pokemon = None
        for pokemon in player_state.bench_pokemon:
            if pokemon.instance_id == request.target_id:
                target_pokemon = pokemon
                break
        
        # 执行撤退
        energy_cost = request.get_parameter('energy_cost', 1)
        success = player_state.retreat_active_pokemon(target_pokemon, energy_cost)
        
        if success:
            response = ActionResponse(
                result=ActionResult.SUCCESS,
                action_request=request,
                message=f"撤退成功，{target_pokemon.card.name} 成为前排Pokemon"
            )
            
            response.add_data('energy_cost', energy_cost)
            response.add_effect(f"消耗 {energy_cost} 点能量")
            response.add_effect(f"{target_pokemon.card.name} 成为前排Pokemon")
        else:
            response = ActionResponse(
                result=ActionResult.FAILED,
                action_request=request,
                message="撤退失败"
            )
        
        return response
    
    def _process_end_turn(self, request: ActionRequest, battle_state, player_state) -> ActionResponse:
        """处理结束回合行动"""
        # 重置玩家状态
        player_state.reset_turn_actions()
        
        # 重置Pokemon状态
        for pokemon in player_state.field_pokemon:
            pokemon.reset_turn_status()
            # 处理状态效果
            status_results = pokemon.process_status_effects()
        
        response = ActionResponse(
            result=ActionResult.SUCCESS,
            action_request=request,
            message="回合结束"
        )
        
        response.add_effect("回合结束")
        
        # 切换到下一阶段（会自动切换回合）
        battle_state.next_phase()
        
        return response
    
    def _process_surrender(self, request: ActionRequest, battle_state, player_state) -> ActionResponse:
        """处理投降行动"""
        # 结束战斗
        winner_id = battle_state.get_opponent_id(request.player_id)
        battle_state.end_battle(battle_state.GameResult.FORFEIT, winner_id)
        
        response = ActionResponse(
            result=ActionResult.SUCCESS,
            action_request=request,
            message="投降"
        )
        
        response.add_effect("玩家投降")
        response.add_effect("战斗结束")
        
        return response

def create_action_request(action_type: str, player_id: int, **kwargs) -> ActionRequest:
    """
    创建行动请求的便捷函数
    
    Args:
        action_type: 行动类型字符串
        player_id: 玩家ID
        **kwargs: 其他参数
    
    Returns:
        行动请求对象
    """
    # 转换字符串为枚举
    try:
        action_enum = ActionType(action_type)
    except ValueError:
        raise ValueError(f"无效的行动类型: {action_type}")
    
    return ActionRequest(
        action_type=action_enum,
        player_id=player_id,
        source_id=kwargs.get('source_id'),
        target_id=kwargs.get('target_id'),
        parameters=kwargs.get('parameters', {})
    )

def get_available_actions(battle_state, player_state) -> List[ActionType]:
    """
    获取当前可用的行动列表
    
    Args:
        battle_state: 战斗状态
        player_state: 玩家状态
    
    Returns:
        可用行动类型列表
    """
    from game.core.battle.battle_state import BattlePhase
    
    available_actions = []
    
    if battle_state.current_phase == BattlePhase.DRAW:
        available_actions.append(ActionType.DRAW_CARD)
    
    elif battle_state.current_phase == BattlePhase.ENERGY:
        available_actions.append(ActionType.GAIN_ENERGY)
    
    elif battle_state.current_phase == BattlePhase.ACTION:
        # 基础行动
        available_actions.append(ActionType.END_TURN)
        available_actions.append(ActionType.SURRENDER)
        
        # Pokemon相关行动
        if player_state.can_play_pokemon():
            available_actions.append(ActionType.PLAY_POKEMON)
        
        if player_state.can_attack():
            available_actions.append(ActionType.ATTACK)
        
        if (player_state.active_pokemon and 
            player_state.active_pokemon.can_retreat() and 
            len(player_state.bench_pokemon) > 0):
            available_actions.append(ActionType.RETREAT)
        
        # TODO: 添加训练师卡、道具等行动
    
    return available_actions