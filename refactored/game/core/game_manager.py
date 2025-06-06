"""
游戏核心管理器
整合数据库管理器和卡牌管理器，提供统一的游戏逻辑接口
"""

import random
import time
import datetime
from typing import Dict, List, Optional, Any, Tuple
from game.core.database.database_manager import DatabaseManager
from game.core.cards.collection_manager import CardManager
from game.core.cards.card_data import Card

class GameManager:
    """
    游戏核心管理器
    负责处理用户数据、卡包开启、卡牌收集等核心游戏逻辑
    """
    
    def __init__(self):
        """初始化游戏管理器"""
        try:
            # 初始化数据库管理器
            self.db_manager = DatabaseManager()
            
            # 初始化卡牌管理器
            self.card_manager = CardManager(
                self.db_manager.connection,
                "card_assets/cards.json"  # 卡牌数据文件路径
            )
            print("✅ 游戏管理器初始化成功")
            # return True
        except Exception as e:
            print(f"❌ 游戏管理器初始化失败: {e}")
            return False
        
        # 当前用户ID（可以通过登录设置）
        self.current_user_id = 1
        
        # 确保默认用户存在
        self._ensure_default_user()
        
        # 卡包配置
        self.pack_configs = {
            'pack_1': {
                'name': 'Festival Brillante',
                'display_name': 'Festival Brillante',
                'price_coins': 100,
                'price_gems': 0,
                'cards_per_pack': 5,
                'guaranteed_rarity': 'Uncommon',
                'pack_type': 'basic'
            },
            'pack_2': {
                'name': 'Guardianes Celestiales',
                'display_name': 'Guardianes Celestiales',
                'price_coins': 200,
                'price_gems': 0,
                'cards_per_pack': 5,
                'guaranteed_rarity': 'Rare',
                'pack_type': 'premium'
            },
            'pack_3': {
                'name': 'Ultra Premium',
                'display_name': 'Ultra Premium',
                'price_coins': 0,
                'price_gems': 50,
                'cards_per_pack': 3,
                'guaranteed_rarity': 'Ultra Rare',
                'pack_type': 'ultra'
            }
        }
        
        print("✅ GameManager 初始化完成")
    
    def _ensure_default_user(self):
        """确保默认用户存在"""
        user = self.db_manager.get_user_info(self.current_user_id)
        if not user:
            # 创建默认用户
            success, result = self.db_manager.register_user(
                username="player1",
                password="default",
                email="player1@game.com"
            )
            if success:
                self.current_user_id = result
                print(f"✅ 创建默认用户，ID: {self.current_user_id}")
            else:
                print(f"❌ 创建默认用户失败: {result}")
    
    # ==================== 用户管理 ====================
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        return self.db_manager.get_user_info(self.current_user_id)
    
    def get_user_economy(self) -> Dict[str, Any]:
        """获取用户经济数据"""
        economy = self.db_manager.get_user_economy(self.current_user_id)
        if not economy:
            # 如果没有经济数据，创建默认的
            self.db_manager._create_user_economy(self.current_user_id)
            economy = self.db_manager.get_user_economy(self.current_user_id)
        
        return economy or {
            'user_id': self.current_user_id,
            'coins': 500,
            'gems': 10,
            'pack_points': 0,
            'dust': 0
        }
    
    def get_user_stats(self) -> Dict[str, Any]:
        """获取用户统计数据"""
        stats = self.db_manager.get_user_stats(self.current_user_id)
        if not stats:
            # 如果没有统计数据，创建默认的
            self.db_manager._create_user_stats(self.current_user_id)
            stats = self.db_manager.get_user_stats(self.current_user_id)
        
        return stats or {
            'user_id': self.current_user_id,
            'games_played': 0,
            'games_won': 0,
            'games_lost': 0,
            'cards_collected': 0,
            'packs_opened': 0,
            'dust_earned': 0
        }
    
    def add_currency(self, currency_type: str, amount: int) -> bool:
        """添加货币"""
        return self.db_manager.add_currency(self.current_user_id, currency_type, amount)
    
    def spend_currency(self, currency_type: str, amount: int) -> bool:
        """花费货币"""
        return self.db_manager.spend_currency(self.current_user_id, currency_type, amount)
    
    def can_afford(self, currency_type: str, amount: int) -> bool:
        """检查是否能够支付"""
        economy = self.get_user_economy()
        return economy.get(currency_type, 0) >= amount
    
    # ==================== 卡包管理 ====================
    def get_available_packs(self) -> List[Dict[str, Any]]:
        """获取可用的卡包列表"""
        packs = []
        for pack_id, config in self.pack_configs.items():
            packs.append({
                'id': pack_id,
                'name': config['display_name'],
                'description': f"包含 {config['cards_per_pack']} 张卡牌，保底 {config['guaranteed_rarity']}",
                'price_coins': config['price_coins'],
                'price_gems': config['price_gems'],
                'cards_per_pack': config['cards_per_pack'],
                'guaranteed_rarity': config['guaranteed_rarity']
            })
        return packs
    
    def can_open_pack(self, pack_id: str) -> Tuple[bool, str]:
        """检查是否能开启卡包"""
        if pack_id not in self.pack_configs:
            return False, "未知的卡包类型"
        
        config = self.pack_configs[pack_id]
        economy = self.get_user_economy()
        
        # 检查金币
        if config['price_coins'] > 0:
            if economy.get('coins', 0) < config['price_coins']:
                return False, f"金币不足，需要 {config['price_coins']} 金币"
        
        # 检查宝石
        if config['price_gems'] > 0:
            if economy.get('gems', 0) < config['price_gems']:
                return False, f"宝石不足，需要 {config['price_gems']} 宝石"
        
        return True, "可以开启"
    
    def open_pack_complete_flow(self, pack_quality: str) -> Dict[str, Any]:
        """完整的开包流程（适配PackOpeningWindow）"""
        
        # 映射pack_quality到pack_id
        quality_to_pack_id = {
            "basic": "pack_1",
            "premium": "pack_2", 
            "legendary": "pack_3"
        }
        
        pack_id = quality_to_pack_id.get(pack_quality)
        if not pack_id:
            return {
                "success": False,
                "error": "unknown_pack_type",
                "cards": []
            }
        
        # 调用现有的open_pack方法
        success, cards, message = self.open_pack(pack_id)
        
        if success:
            # 转换卡牌数据格式，适配PackOpeningWindow期望的格式
            cards_data = []
            for card in cards:
                cards_data.append({
                    "id": card.id,
                    "name": card.name,
                    "rarity": card.rarity,
                    "image": getattr(card, 'image_path', ''),  # ✅ 使用image_path字段
                    "hp": getattr(card, 'hp', None),
                    "types": card.types if hasattr(card, 'types') else []  # ✅ 更安全的类型获取
                })
            
            return {
                "success": True,
                "cards": cards_data,
                "message": message
            }
        else:
            # 映射错误消息到PackOpeningWindow期望的错误类型
            error_type = "unknown_error"
            if "金币不足" in message or "宝石不足" in message:
                error_type = "insufficient_packs"
            elif "扣除" in message:
                error_type = "deduct_pack_failed"
            elif "失败" in message:
                error_type = "transaction_failed"
            
            return {
                "success": False,
                "error": error_type,
                "cards": [],
                "message": message
            }

    def open_pack(self, pack_id: str) -> Tuple[bool, List[Card], str]:
        """
        开启卡包
        
        Returns:
            (成功标志, 获得的卡牌列表, 消息)
        """
        # 检查是否能开启
        can_open, message = self.can_open_pack(pack_id)
        if not can_open:
            return False, [], message
        
        config = self.pack_configs[pack_id]
        
        try:
            # 扣除费用
            if config['price_coins'] > 0:
                if not self.spend_currency('coins', config['price_coins']):
                    return False, [], "扣除金币失败"
            
            if config['price_gems'] > 0:
                if not self.spend_currency('gems', config['price_gems']):
                    return False, [], "扣除宝石失败"
            
            # 开启卡包获得卡牌
            obtained_cards = self.card_manager.open_pack(
                pack_type=config['pack_type'],
                guaranteed_rarity=config['guaranteed_rarity']
            )
            
            # 将卡牌添加到用户收藏
            for card in obtained_cards:
                self.db_manager.add_card_to_user(self.current_user_id, card.id, 1)
            
            # 记录开包历史
            pack_type_id = list(self.pack_configs.keys()).index(pack_id) + 1
            cost_type = 'coins' if config['price_coins'] > 0 else 'gems'
            cost_amount = config['price_coins'] if config['price_coins'] > 0 else config['price_gems']
            
            card_ids = [card.id for card in obtained_cards]
            self.db_manager.record_pack_opening(
                self.current_user_id,
                pack_type_id,
                card_ids,
                cost_type,
                cost_amount
            )
            
            # 更新统计
            current_stats = self.get_user_stats()
            new_packs_opened = current_stats['packs_opened'] + 1
            new_cards_collected = current_stats['cards_collected'] + len(obtained_cards)
            
            self.db_manager.update_user_stats(
                self.current_user_id,
                packs_opened=new_packs_opened,
                cards_collected=new_cards_collected
            )
            
            return True, obtained_cards, f"成功开启 {config['display_name']}！"
            
        except Exception as e:
            print(f"❌ 开包失败: {e}")
            return False, [], f"开包失败: {str(e)}"
    
    # ==================== 卡牌管理 ====================
    def get_user_cards(self) -> List[Dict[str, Any]]:
        """获取用户的所有卡牌"""
        user_cards_data = self.db_manager.get_user_cards(self.current_user_id)
        result = []
        
        for card_data in user_cards_data:
            card = self.card_manager.get_card_by_id(card_data['card_id'])
            if card:
                result.append({
                    'card': card,
                    'quantity': card_data['quantity'],
                    'obtained_at': card_data['obtained_at']
                })
        
        return result
    
    def get_user_collection_stats(self) -> Dict[str, Any]:
        """获取用户收藏统计"""
        user_cards = self.get_user_cards()
        user_card_ids = [card_info['card']['id'] for card_info in user_cards]
        
        # 使用卡牌管理器获取收藏进度
        collection_progress = self.card_manager.get_collection_progress(user_card_ids)
        
        # 添加一些额外的统计
        total_owned = sum(card_info['quantity'] for card_info in user_cards)
        unique_owned = len(user_cards)
        
        collection_progress['owned_stats'] = {
            'total_cards_owned': total_owned,
            'unique_cards_owned': unique_owned,
            'average_copies': round(total_owned / unique_owned, 2) if unique_owned > 0 else 0
        }
        
        return collection_progress
    
    def search_cards(self, **kwargs) -> List[Card]:
        """搜索卡牌"""
        return self.card_manager.search_cards(**kwargs)
    
    def get_card_by_id(self, card_id: str) -> Optional[Card]:
        """根据ID获取卡牌"""
        return self.card_manager.get_card_by_id(card_id)
    
    def get_featured_cards(self, count: int = 10) -> List[Card]:
        """获取精选卡牌"""
        return self.card_manager.get_featured_cards(count)
    
    def get_daily_featured_card(self) -> Optional[Card]:
        """获取每日精选卡牌"""
        return self.card_manager.get_daily_featured_card()
    
    # ==================== 卡组管理 ====================
    def get_user_decks(self) -> List[Dict[str, Any]]:
        """获取用户卡组"""
        return self.db_manager.get_user_decks(self.current_user_id)
    
    def create_deck(self, name: str, description: str = "") -> Tuple[bool, Any]:
        """创建新卡组"""
        return self.db_manager.create_new_deck(self.current_user_id, name, description)
    
    def add_card_to_deck(self, deck_id: int, card_id: str, quantity: int = 1) -> bool:
        """向卡组添加卡牌"""
        return self.db_manager.add_card_to_deck(deck_id, card_id, quantity)
    
    def get_deck_cards(self, deck_id: int) -> List[Dict[str, Any]]:
        """获取卡组中的卡牌"""
        return self.db_manager.get_deck_cards(deck_id)
    
    # ==================== 成就和任务 ====================
    def get_user_achievements(self) -> List[Dict[str, Any]]:
        """获取用户成就"""
        return self.db_manager.get_user_achievements(self.current_user_id)
    
    def update_achievement_progress(self, achievement_name: str, progress: int) -> Tuple[bool, str]:
        """更新成就进度"""
        return self.db_manager.update_achievement_progress(self.current_user_id, achievement_name, progress)
    
    def get_daily_quests(self) -> List[Dict[str, Any]]:
        """获取每日任务"""
        today = datetime.date.today().isoformat()
        return self.db_manager.get_daily_quests(self.current_user_id, today)
    
    def update_quest_progress(self, quest_type: str, progress: int) -> Tuple[bool, str]:
        """更新任务进度"""
        today = datetime.date.today().isoformat()
        return self.db_manager.update_quest_progress(self.current_user_id, quest_type, today, progress)
    
    # ==================== 游戏统计 ====================
    def get_pack_opening_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取开包历史"""
        return self.db_manager.get_pack_opening_history(self.current_user_id, limit)
    
    def get_card_statistics(self) -> Dict[str, Any]:
        """获取卡牌统计信息"""
        return self.card_manager.get_card_statistics()
    
    def get_game_overview(self) -> Dict[str, Any]:
        """获取游戏概览信息"""
        user = self.get_current_user()
        economy = self.get_user_economy()
        stats = self.get_user_stats()
        collection_stats = self.get_user_collection_stats()
        
        return {
            'user': user,
            'economy': economy,
            'stats': stats,
            'collection': collection_stats,
            'available_packs': self.get_available_packs(),
            'recent_pack_openings': self.get_pack_opening_history(5)
        }
    
    # ==================== 每日奖励 ====================
    def claim_daily_bonus(self) -> Tuple[bool, str, Dict[str, int]]:
        """领取每日奖励"""
        economy = self.get_user_economy()
        last_bonus = economy.get('last_daily_bonus')
        today = datetime.date.today().isoformat()
        
        if last_bonus == today:
            return False, "今日已领取每日奖励", {}
        
        # 每日奖励配置
        daily_rewards = {
            'coins': 50,
            'gems': 1
        }
        
        # 发放奖励
        success = True
        for currency, amount in daily_rewards.items():
            if not self.add_currency(currency, amount):
                success = False
                break
        
        if success:
            # 更新最后领取时间
            self.db_manager.update_user_economy(
                self.current_user_id,
                last_daily_bonus=today
            )
            return True, "每日奖励领取成功！", daily_rewards
        else:
            return False, "领取每日奖励失败", {}
    
    def can_claim_daily_bonus(self) -> bool:
        """检查是否可以领取每日奖励"""
        economy = self.get_user_economy()
        last_bonus = economy.get('last_daily_bonus')
        today = datetime.date.today().isoformat()
        return last_bonus != today
    
    # ==================== 辅助方法 ====================
    def generate_test_data(self):
        """生成测试数据（开发用）"""
        print("🔧 生成测试数据...")
        
        # 给用户一些初始货币
        self.add_currency('coins', 1000)
        self.add_currency('gems', 50)
        
        # 创建一些成就
        achievements = [
            ("collector", "收藏家", "收集100张不同的卡牌", 100, 100, 5),
            ("pack_opener", "开包达人", "开启50个卡包", 50, 50, 3),
            ("rare_hunter", "稀有猎人", "获得10张Ultra Rare卡牌", 10, 200, 10)
        ]
        
        for ach_type, ach_name, desc, target, reward_coins, reward_gems in achievements:
            self.db_manager.create_achievement(
                self.current_user_id, ach_type, ach_name, desc, target, reward_coins, reward_gems
            )
        
        # 创建一些每日任务
        today = datetime.date.today().isoformat()
        quests = [
            ("open_pack", "开启一个卡包", 1, 25, 0),
            ("collect_cards", "收集5张新卡牌", 5, 50, 1),
            ("login", "登录游戏", 1, 10, 0)
        ]
        
        for quest_type, desc, target, reward_coins, reward_gems in quests:
            self.db_manager.create_daily_quest(
                self.current_user_id, quest_type, desc, target, today, reward_coins, reward_gems
            )
        
        print("✅ 测试数据生成完成")
    
    def reset_user_data(self):
        """重置用户数据（开发用）"""
        print("🔄 重置用户数据...")
        
        # 重置经济数据
        self.db_manager.update_user_economy(
            self.current_user_id,
            coins=500,
            gems=10,
            pack_points=0,
            dust=0
        )
        
        # 重置统计数据
        self.db_manager.update_user_stats(
            self.current_user_id,
            games_played=0,
            games_won=0,
            games_lost=0,
            cards_collected=0,
            packs_opened=0,
            dust_earned=0
        )
        
        print("✅ 用户数据重置完成")
    
    def cleanup(self):
        """清理资源"""
        if self.db_manager:
            self.db_manager.close()
        print("🧹 GameManager 资源清理完成")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()