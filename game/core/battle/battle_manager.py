"""
战斗管理器
负责整个战斗流程的控制和管理
"""

import time
import random
from typing import Dict, List, Optional, Any, Tuple

from game.core.battle.battle_state import BattleState, BattlePhase, GameResult, BattleAction
from game.core.battle.player_state import PlayerState
from game.core.battle.battle_actions import ActionProcessor, ActionRequest, ActionResponse, ActionResult
from game.core.battle.ai_opponent import AIDecisionMaker, AIDifficulty, get_ai_opponent, get_random_ai_opponent
from game.core.cards.card_data import Card

class BattleManager:
    """战斗管理器类"""
    AI_PLAYER_ID = 999
    def __init__(self, game_manager, player_id: int, player_deck_id: int, 
                 opponent_type: str = "AI", opponent_id: Optional[int] = None):
        """
        初始化战斗管理器
        
        Args:
            game_manager: 游戏管理器实例
            player_id: 玩家ID
            player_deck_id: 玩家卡组ID
            opponent_type: 对手类型 ("AI" 或 "PVP")
            opponent_id: 对手ID (AI对战时为难度等级，PVP时为对手玩家ID)
        """
        self.game_manager = game_manager
        # self.message_manager = game_manager.message_manager
        self.player_id = player_id
        self.opponent_type = opponent_type
        self.opponent_id = opponent_id
        
        # 战斗状态
        self.battle_state: Optional[BattleState] = None
        self.player_states: Dict[int, PlayerState] = {}
        self.action_processor: Optional[ActionProcessor] = None
        
        # AI系统 (如果是AI对战)
        self.ai_decision_maker: Optional[AIDecisionMaker] = None
        
        # 战斗配置
        self.auto_play_ai = True  # 自动执行AI回合
        self.battle_speed = 1.0   # 战斗速度倍率
        
        # 初始化战斗
        self._initialize_battle(player_deck_id)
        
        print(f"🎮 战斗管理器初始化完成")
        print(f"   玩家: {player_id} vs {opponent_type}")
        print(f"   战斗ID: {self.battle_state.battle_id if self.battle_state else 'None'}")
    
    def _initialize_battle(self, player_deck_id: int) -> bool:
        """
        初始化战斗
        
        Args:
            player_deck_id: 玩家卡组ID
        
        Returns:
            是否成功初始化
        """
        try:
            # 1. 创建战斗记录
            if self.opponent_type == "AI":
                opponent_deck_id = None
                actual_opponent_id = None
            else:
                opponent_deck_id = self.opponent_id  # PVP模式下需要传入对手卡组ID
                actual_opponent_id = self.opponent_id
            
            success, battle_id = self.game_manager.db_manager.create_battle_record(
                self.player_id, actual_opponent_id, player_deck_id, opponent_deck_id, self.opponent_type
            )
            
            if not success:
                print(f"❌ 创建战斗记录失败: {battle_id}")
                return False
            
            # 2. 创建战斗状态
            self.battle_state = BattleState(battle_id, self.player_id, actual_opponent_id)
            
            # 3. 准备卡组
            player_deck = self._prepare_deck(player_deck_id)
            if not player_deck:
                print(f"❌ 玩家卡组准备失败")
                return False
            
            if self.opponent_type == "AI":
                opponent_deck = self._prepare_ai_deck()
                opponent_player_id = self.AI_PLAYER_ID  # AI使用-1作为ID
            else:
                # PVP模式：加载对手卡组
                opponent_deck = self._prepare_deck(opponent_deck_id)
                opponent_player_id = actual_opponent_id
            
            if not opponent_deck:
                print(f"❌ 对手卡组准备失败")
                return False
            
            # 4. 创建玩家状态
            self.player_states[self.player_id] = PlayerState(
                self.player_id, player_deck, is_ai=False
            )
            self.player_states[opponent_player_id] = PlayerState(
                opponent_player_id, opponent_deck, is_ai=(self.opponent_type == "AI")
            )
            
            # 5. 初始化AI (如果需要)
            if self.opponent_type == "AI":
                ai_personality = self._get_ai_personality()
                self.ai_decision_maker = AIDecisionMaker(ai_personality)
            
            # 6. 创建行动处理器
            self.action_processor = ActionProcessor(self)
            
            # 7. 执行初始设置
            self._setup_initial_game_state()
            
            print(f"✅ 战斗初始化成功，战斗ID: {battle_id}")
            return True
            
        except Exception as e:
            print(f"❌ 战斗初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # def _ensure_playable_hands(self):
    #     """确保所有玩家的起始手牌可用（包含Pokemon）"""
    #     print("🛡️ 执行手牌保护检查...")
        
    #     for player_id, player_state in self.player_states.items():
    #         try:
    #             print(f"🔍 检查玩家 {player_id} 的手牌...")
                
    #             # 获取手牌中的Pokemon
    #             hand_pokemon = player_state.get_hand_pokemon()
    #             print(f"   手牌Pokemon数量: {len(hand_pokemon)}")
                
    #             if not hand_pokemon:
    #                 print(f"⚠️ 玩家 {player_id} 手牌中没有Pokemon，尝试从卡组补充...")
                    
    #                 # 从卡组中找Pokemon
    #                 pokemon_found = False
    #                 for card in player_state.deck[:]:  # 复制列表避免修改时出错
    #                     if hasattr(card, 'card') and hasattr(card.card, 'hp') and card.card.hp is not None:  # 是Pokemon
    #                         print(f"🔄 将Pokemon {card.card.name} 从卡组移动到手牌")
    #                         player_state.deck.remove(card)
    #                         card.position = "hand" 
    #                         player_state.hand.append(card)
    #                         pokemon_found = True
    #                         break
                    
    #                 if not pokemon_found:
    #                     print(f"❌ 玩家 {player_id} 卡组中没有可用的Pokemon！")
    #                 else:
    #                     print(f"✅ 玩家 {player_id} 手牌Pokemon补充完成")
    #             else:
    #                 print(f"✅ 玩家 {player_id} 手牌Pokemon检查通过")
                    
    #         except Exception as e:
    #             print(f"❌ 玩家 {player_id} 手牌保护检查失败: {e}")
    #             # 继续处理其他玩家，不中断整个流程
    #             continue
        
    #     print("🛡️ 手牌保护检查完成")

    def _prepare_deck(self, deck_id: int) -> List[Card]:
        """
        准备卡组
        
        Args:
            deck_id: 卡组ID
        
        Returns:
            卡牌列表
        """
        try:
            # 获取卡组卡牌
            deck_cards_data = self.game_manager.get_deck_cards(deck_id)
            if not deck_cards_data:
                print(f"❌ 卡组 {deck_id} 为空")
                return []
            
            # 构建卡牌列表
            deck_cards = []
            for card_data in deck_cards_data:
                card = self.game_manager.get_card_by_id(card_data['card_id'])
                if card:
                    # 根据数量添加卡牌
                    for _ in range(card_data['quantity']):
                        deck_cards.append(card)
                else:
                    print(f"⚠️ 卡牌 {card_data['card_id']} 不存在")
            
            print(f"📦 卡组准备完成: {len(deck_cards)} 张卡牌")
            return deck_cards
            
        except Exception as e:
            print(f"❌ 准备卡组失败: {e}")
            return []
    
    def _prepare_ai_deck(self) -> List[Card]:
        """
        为AI准备卡组
        
        Returns:
            AI卡组
        """
        try:
            # 简单的AI卡组生成策略
            # 获取所有可用卡牌
            all_cards = self.game_manager.search_cards(limit=1000)
            
            if not all_cards:
                print(f"❌ 数据库中没有卡牌，无法生成AI卡组")
                return []
            
            # 分类卡牌
            pokemon_cards = [card for card in all_cards if card.hp is not None]
            trainer_cards = [card for card in all_cards if card.hp is None]
            
            # 生成平衡的AI卡组 (20张卡)
            ai_deck = []
            
            # 添加Pokemon (15张)
            if pokemon_cards:
                # 按稀有度分层选择
                common_pokemon = [c for c in pokemon_cards if c.rarity == "Common"]
                uncommon_pokemon = [c for c in pokemon_cards if c.rarity == "Uncommon"]
                rare_pokemon = [c for c in pokemon_cards if c.rarity in ["Rare", "Ultra Rare"]]
                
                # 8张Common, 5张Uncommon, 2张Rare
                ai_deck.extend(random.sample(common_pokemon, min(8, len(common_pokemon))))
                ai_deck.extend(random.sample(uncommon_pokemon, min(5, len(uncommon_pokemon))))
                ai_deck.extend(random.sample(rare_pokemon, min(2, len(rare_pokemon))))
            
            # 添加训练师卡 (5张)
            if trainer_cards:
                ai_deck.extend(random.sample(trainer_cards, min(5, len(trainer_cards))))
            
            # 如果卡牌不够，用Pokemon补充
            while len(ai_deck) < 20 and pokemon_cards:
                ai_deck.append(random.choice(pokemon_cards))
            
            print(f"🤖 AI卡组生成完成: {len(ai_deck)} 张卡牌")
            return ai_deck
            
        except Exception as e:
            print(f"❌ 生成AI卡组失败: {e}")
            return []
    
    def _get_ai_personality(self):
        """获取AI个性配置"""
        if isinstance(self.opponent_id, str):
            # 指定AI对手
            return get_ai_opponent(self.opponent_id)
        else:
            # 根据难度生成随机AI
            difficulty_map = {
                1: AIDifficulty.EASY,
                2: AIDifficulty.MEDIUM,
                3: AIDifficulty.HARD
            }
            difficulty = difficulty_map.get(self.opponent_id, AIDifficulty.EASY)
            return get_random_ai_opponent(difficulty)
    
    def _setup_initial_game_state(self):
        """设置初始游戏状态"""
        # 抽取起始手牌
        for player_state in self.player_states.values():
            player_state.draw_initial_hand(5)
            
            # 检查起始手牌是否有Pokemon
            hand_pokemon = player_state.get_hand_pokemon()
            if not hand_pokemon:
                # Mulligan: 重新洗牌并抽卡
                print(f"🔄 玩家 {player_state.player_id} 执行Mulligan")
                player_state.hand.extend(player_state.deck)
                player_state.deck = player_state.hand
                player_state.hand = []
                player_state.shuffle_deck()
                player_state.draw_initial_hand(5)
        
        # 设置起始前排Pokemon
        for player_state in self.player_states.values():
            hand_pokemon = player_state.get_hand_pokemon()
            if hand_pokemon:
                # 选择HP最高的Pokemon作为起始前排
                starter_pokemon = max(hand_pokemon, key=lambda p: p.card.hp or 0)
                player_state.play_pokemon_to_bench(starter_pokemon)
                if player_state.bench_pokemon:
                    player_state.set_active_pokemon(player_state.bench_pokemon[0])
        
        print(f"🎯 初始游戏状态设置完成")
    
    def start_battle(self) -> bool:
        """
        开始战斗
        
        Returns:
            是否成功开始
        """
        if not self.battle_state or not self.action_processor:
            print(f"❌ 战斗状态未正确初始化")
            return False
        
        try:
            print(f"🚀 战斗开始!")
            print(f"   玩家 {self.player_id} vs {self.opponent_type}")
            
            # 进入第一个回合
            self.battle_state.next_phase()  # 从SETUP到DRAW
            
            return True
            
        except Exception as e:
            print(f"❌ 开始战斗失败: {e}")
            return False
    
    def process_player_action(self, action_request: ActionRequest) -> ActionResponse:
        """
        处理玩家行动
        
        Args:
            action_request: 行动请求
        
        Returns:
            行动响应
        """
        if not self.action_processor:
            return ActionResponse(
                result=ActionResult.FAILED,
                action_request=action_request,
                message="战斗系统未初始化"
            )
        
        # 检查是否是玩家回合
        if not self.battle_state.is_player_turn(action_request.player_id):
            return ActionResponse(
                result=ActionResult.NOT_ALLOWED,
                action_request=action_request,
                message="不是你的回合"
            )
        
        # 处理行动
        response = self.action_processor.process_action(action_request)
        
        # 记录行动到战斗状态
        if response.is_success():
            battle_action = BattleAction(
                action_type=action_request.action_type.value,
                player_id=action_request.player_id,
                source_pokemon=action_request.source_id,
                target_pokemon=action_request.target_id,
                card_id=action_request.source_id,
                effects=response.effects
            )
            self.battle_state.add_action(battle_action)
        
        # 检查胜负条件
        self._check_win_conditions()
        
        # 如果是AI对战且轮到AI回合，自动执行AI行动
        if (self.opponent_type == "AI" and 
            self.auto_play_ai and 
            self.battle_state.current_turn_player == -1 and
            not self.battle_state.is_battle_over()):
            self._process_ai_turn()
        
        return response
    
    def _process_ai_turn(self):
        """处理AI回合"""
        if not self.ai_decision_maker or self.battle_state.is_battle_over():
            return
        
        max_actions_per_turn = 10  # 防止无限循环
        actions_taken = 0
        
        while (self.battle_state.current_turn_player == -1 and 
               not self.battle_state.is_battle_over() and 
               actions_taken < max_actions_per_turn):
            
            # AI决策
            ai_player_state = self.get_player_state(-1)
            opponent_player_state = self.get_player_state(self.player_id)
            
            ai_action = self.ai_decision_maker.make_decision(
                self.battle_state, ai_player_state, opponent_player_state
            )
            
            if not ai_action:
                print(f"⚠️ AI无法做出决策，强制结束回合")
                break
            
            # 执行AI行动
            response = self.action_processor.process_action(ai_action)
            
            # 记录AI决策
            self.ai_decision_maker.record_decision(ai_action, response)
            
            # 记录行动到战斗状态
            if response.is_success():
                battle_action = BattleAction(
                    action_type=ai_action.action_type.value,
                    player_id=ai_action.player_id,
                    source_pokemon=ai_action.source_id,
                    target_pokemon=ai_action.target_id,
                    card_id=ai_action.source_id,
                    effects=response.effects
                )
                self.battle_state.add_action(battle_action)
                
                print(f"🤖 AI执行: {ai_action.action_type.value}")
                if response.effects:
                    for effect in response.effects:
                        print(f"   效果: {effect}")
            else:
                print(f"❌ AI行动失败: {response.message}")
                break
            
            actions_taken += 1
            
            # 检查胜负条件
            self._check_win_conditions()
            
            # 短暂延迟，模拟AI思考
            if self.battle_speed < 2.0:
                time.sleep(0.5 / self.battle_speed)
    
    def _check_win_conditions(self):
        """检查胜负条件"""
        if self.battle_state.is_battle_over():
            return
        
        # 检查奖励卡获胜条件
        for player_id, player_state in self.player_states.items():
            if player_state.check_win_condition():
                self.battle_state.end_battle(
                    GameResult.PLAYER_WIN if player_id == self.player_id else GameResult.OPPONENT_WIN,
                    player_id
                )
                print(f"🏆 玩家 {player_id} 通过奖励卡获胜!")
                self._save_battle_result()
                return
            
            # 检查失败条件
            if player_state.check_lose_condition():
                opponent_id = self.battle_state.get_opponent_id(player_id)
                self.battle_state.end_battle(
                    GameResult.OPPONENT_WIN if player_id == self.player_id else GameResult.PLAYER_WIN,
                    opponent_id
                )
                print(f"💀 玩家 {player_id} 败北!")
                self._save_battle_result()
                return
        
        # 检查回合数限制
        if self.battle_state.turn_count >= self.battle_state.max_turns:
            self.battle_state.end_battle(GameResult.DRAW, None)
            print(f"⏰ 达到最大回合数，战斗平局!")
            self._save_battle_result()
    
    def _save_battle_result(self):
        """保存战斗结果到数据库"""
        # 检查战斗状态和数据库连接
        if not self.battle_state or not self.game_manager.db_manager.connection:
            print("⚠️ 数据库连接已关闭，跳过保存")
            return
        
        if not self.battle_state:
            return
        
        try:
            battle_data = self.battle_state.to_dict()
            duration = int(self.battle_state.get_battle_duration())
            
            success = self.game_manager.db_manager.update_battle_result(
                self.battle_state.battle_id,
                self.battle_state.winner_id,
                self.battle_state.turn_count,
                battle_data,
                duration
            )
            
            if success:
                print(f"💾 战斗结果已保存")
                
                # 更新玩家统计
                self._update_player_stats()
            else:
                print(f"❌ 保存战斗结果失败")
                
        except Exception as e:
            print(f"❌ 保存战斗结果时出错: {e}")
    
    def _update_player_stats(self):
        """更新玩家统计数据"""
        try:
            if self.battle_state.winner_id == self.player_id:
                # 玩家获胜
                stats = self.game_manager.get_user_stats()
                new_games_won = stats['games_won'] + 1
                new_games_played = stats['games_played'] + 1
                
                self.game_manager.db_manager.update_user_stats(
                    self.player_id,
                    games_won=new_games_won,
                    games_played=new_games_played
                )
                
                # 奖励金币
                reward_coins = 50 if self.opponent_type == "AI" else 100
                self.game_manager.add_currency('coins', reward_coins)
                print(f"💰 获得奖励: {reward_coins} 金币")
                
            else:
                # 玩家失败
                stats = self.game_manager.get_user_stats()
                new_games_lost = stats['games_lost'] + 1
                new_games_played = stats['games_played'] + 1
                
                self.game_manager.db_manager.update_user_stats(
                    self.player_id,
                    games_lost=new_games_lost,
                    games_played=new_games_played
                )
                
                # 安慰奖
                reward_coins = 10
                self.game_manager.add_currency('coins', reward_coins)
                print(f"💰 安慰奖: {reward_coins} 金币")
                
        except Exception as e:
            print(f"❌ 更新玩家统计失败: {e}")
    
    def get_player_state(self, player_id: int) -> Optional[PlayerState]:
        """获取玩家状态"""
        return self.player_states.get(player_id)
    
    def get_current_player_state(self) -> Optional[PlayerState]:
        """获取当前回合玩家状态"""
        current_player_id = self.battle_state.get_current_player_id()
        return self.get_player_state(current_player_id)
    
    def get_opponent_state(self, player_id: int) -> Optional[PlayerState]:
        """获取对手状态"""
        if not self.battle_state:
            print(f"🔍 battle_state为空")
            return None
        
        opponent_id = self.battle_state.get_opponent_id(player_id)
        print(f"🔍 获取到对手ID: {opponent_id}")
        
        if opponent_id is None:
            print(f"🔍 对手ID为None")
            return None
            
        opponent_state = self.get_player_state(opponent_id)
        print(f"🔍 获取到对手状态: {opponent_state}")
        return opponent_state
    
    def get_battle_summary(self) -> Dict[str, Any]:
        """获取战斗摘要"""
        if not self.battle_state:
            return {}
        
        summary = self.battle_state.get_battle_summary()
        
        # 添加玩家状态信息
        summary['player_states'] = {}
        for player_id, player_state in self.player_states.items():
            summary['player_states'][player_id] = player_state.get_field_summary()
        
        # 添加可用行动
        if not self.battle_state.is_battle_over():
            current_player_state = self.get_current_player_state()
            if current_player_state:
                from game.core.battle.battle_actions import get_available_actions
                available_actions = get_available_actions(self.battle_state, current_player_state)
                summary['available_actions'] = [action.value for action in available_actions]
        
        return summary
    
    def get_game_state_for_ui(self) -> Dict[str, Any]:
        """获取用于UI显示的游戏状态"""
        if not self.battle_state:
            return {}
        
        return {
            'battle_id': self.battle_state.battle_id,
            'phase': self.battle_state.current_phase.value,
            'turn': self.battle_state.turn_count,
            'current_player': self.battle_state.current_turn_player,
            'is_battle_over': self.battle_state.is_battle_over(),
            'result': self.battle_state.result.value,
            'winner': self.battle_state.winner_id,
            
            'player': self.get_player_state(self.player_id).get_field_summary() if self.get_player_state(self.player_id) else {},
            'opponent': self.get_opponent_state(self.player_id).get_field_summary() if self.get_opponent_state(self.player_id) else {},
            
            'can_make_action': (
                self.battle_state.is_player_turn(self.player_id) and 
                not self.battle_state.is_battle_over()
            ),
            
            'recent_actions': [
                action.to_dict() for action in self.battle_state.action_history[-5:]
            ] if self.battle_state.action_history else []
        }
    
    def surrender(self, player_id: int) -> bool:
        """
        玩家投降
        
        Args:
            player_id: 投降的玩家ID
        
        Returns:
            是否成功投降
        """
        if self.battle_state.is_battle_over():
            return False
        
        opponent_id = self.battle_state.get_opponent_id(player_id)
        self.battle_state.end_battle(GameResult.FORFEIT, opponent_id)
        
        print(f"🏳️ 玩家 {player_id} 投降")
        self._save_battle_result()
        
        return True
    
    def pause_battle(self):
        """暂停战斗"""
        self.auto_play_ai = False
        print(f"⏸️ 战斗已暂停")
    
    def resume_battle(self):
        """恢复战斗"""
        self.auto_play_ai = True
        print(f"▶️ 战斗已恢复")
        
        # 如果是AI回合，继续执行
        if (self.opponent_type == "AI" and 
            self.battle_state.current_turn_player == -1 and
            not self.battle_state.is_battle_over()):
            self._process_ai_turn()
    
    def set_battle_speed(self, speed: float):
        """
        设置战斗速度
        
        Args:
            speed: 速度倍率 (0.5-3.0)
        """
        self.battle_speed = max(0.5, min(3.0, speed))
        print(f"⚡ 战斗速度设置为: {self.battle_speed}x")
    
    def get_battle_log(self) -> List[str]:
        """获取战斗日志"""
        if not self.battle_state:
            return []
        
        log_entries = []
        
        for action in self.battle_state.action_history:
            player_name = f"玩家{action.player_id}" if action.player_id != -1 else "AI"
            
            if action.action_type == "attack":
                log_entries.append(f"{player_name} 发起攻击")
                if action.damage > 0:
                    log_entries.append(f"  造成 {action.damage} 点伤害")
            elif action.action_type == "play_pokemon":
                log_entries.append(f"{player_name} 放置了Pokemon")
            elif action.action_type == "end_turn":
                log_entries.append(f"{player_name} 结束回合")
            
            for effect in action.effects:
                log_entries.append(f"  {effect}")
        
        return log_entries
    
    def force_end_battle(self, winner_id: Optional[int] = None):
        """强制结束战斗"""
        if self.battle_state:
            self.battle_state.force_end_battle(winner_id)
            self._save_battle_result()
    
    def cleanup(self):
        """清理战斗资源"""
        if self.battle_state and not self.battle_state.is_battle_over():
            self.force_end_battle()
        
        self.battle_state = None
        self.player_states.clear()
        self.action_processor = None
        self.ai_decision_maker = None
        
        print(f"🧹 战斗管理器已清理")
    
    def __del__(self):
        """析构函数"""
        try:
            # 安全检查属性是否存在
            if hasattr(self, 'battle_state') and self.battle_state and hasattr(self.battle_state, 'is_battle_over'):
                if not self.battle_state.is_battle_over():
                    self.cleanup()
            elif hasattr(self, 'cleanup'):
                # 如果battle_state不存在，直接尝试cleanup
                self.cleanup()
        except Exception as e:
            # 析构函数中不应该抛出异常
            pass
    
    def __str__(self) -> str:
        """字符串表示"""
        if self.battle_state:
            return f"BattleManager(id={self.battle_state.battle_id}, turn={self.battle_state.turn_count})"
        else:
            return "BattleManager(未初始化)"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()