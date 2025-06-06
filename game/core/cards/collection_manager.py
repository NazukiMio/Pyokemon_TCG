"""
卡牌管理器
处理卡牌相关的所有业务逻辑
"""

import json
import random
import os
from typing import List, Dict, Optional, Any, Tuple
from game.core.cards.card_data import Card, parse_cards_from_json_file, get_rarity_probabilities
from game.core.database.daos.card_dao import CardDAO

class CardManager:
    """卡牌管理器类"""
    
    def __init__(self, db_connection, cards_json_path: str = "cards.json"):
        """
        初始化卡牌管理器
        
        Args:
            db_connection: 数据库连接
            cards_json_path: 卡牌JSON文件路径
        """
        self.card_dao = CardDAO(db_connection)
        self.cards_json_path = cards_json_path
        self.rarity_probabilities = get_rarity_probabilities()
        
        # 初始化数据库表
        self.card_dao.create_card_tables()
        
        # 如果数据库为空且存在JSON文件，则导入数据
        if self.card_dao.get_card_count() == 0 and os.path.exists(cards_json_path):
            self.load_cards_from_json()
        
        # 初始化稀有度配置
        self._init_rarity_config()
    
    def _init_rarity_config(self):
        """初始化稀有度配置"""
        rarity_configs = {
            "Common": {"probability": 0.35, "dust_value": 5, "sort_order": 1},
            "Uncommon": {"probability": 0.25, "dust_value": 10, "sort_order": 2},
            "Rare": {"probability": 0.15, "dust_value": 20, "sort_order": 3},
            "Rare Holo": {"probability": 0.1, "dust_value": 40, "sort_order": 4},
            "Promo": {"probability": 0.05, "dust_value": 30, "sort_order": 5},
            "Rare Holo EX": {"probability": 0.03, "dust_value": 100, "sort_order": 6},
            "Ultra Rare": {"probability": 0.025, "dust_value": 200, "sort_order": 7},
            "Rare Secret": {"probability": 0.02, "dust_value": 300, "sort_order": 8},
            "Rare Holo GX": {"probability": 0.015, "dust_value": 400, "sort_order": 9},
            "Rare Shiny": {"probability": 0.01, "dust_value": 500, "sort_order": 10},
            "Rare Holo V": {"probability": 0.005, "dust_value": 800, "sort_order": 11},
            "Rare BREAK": {"probability": 0.005, "dust_value": 600, "sort_order": 12},
            "Rare Ultra": {"probability": 0.005, "dust_value": 700, "sort_order": 13},
            "Rare Prism Star": {"probability": 0.005, "dust_value": 900, "sort_order": 14},
            "Amazing Rare": {"probability": 0.005, "dust_value": 1000, "sort_order": 15},
            "Rare Shining": {"probability": 0.005, "dust_value": 1200, "sort_order": 16}
        }
        
        for rarity, config in rarity_configs.items():
            self.card_dao.insert_rarity_config(
                rarity=rarity,
                probability=config["probability"],
                dust_value=config["dust_value"],
                sort_order=config["sort_order"]
            )
    
    def load_cards_from_json(self) -> Tuple[int, int]:
        """
        从JSON文件加载卡牌到数据库
        
        Returns:
            (成功数量, 失败数量)
        """
        try:
            print(f"正在从 {self.cards_json_path} 加载卡牌数据...")
            cards = parse_cards_from_json_file(self.cards_json_path)
            
            if not cards:
                print("❌ 没有找到卡牌数据")
                return 0, 0
            
            print(f"解析到 {len(cards)} 张卡牌，开始导入数据库...")
            success_count, failed_count = self.card_dao.insert_cards_batch(cards)
            
            print(f"✅ 卡牌导入完成: 成功 {success_count}, 失败 {failed_count}")
            return success_count, failed_count
            
        except Exception as e:
            print(f"❌ 加载卡牌数据失败: {e}")
            return 0, 0
    
    def get_card_by_id(self, card_id: str) -> Optional[Card]:
        """
        根据ID获取卡牌
        
        Args:
            card_id: 卡牌ID
        
        Returns:
            卡牌对象或None
        """
        return self.card_dao.get_card_by_id(card_id)
    
    def get_cards_by_ids(self, card_ids: List[str]) -> List[Card]:
        """
        根据ID列表获取多张卡牌
        
        Args:
            card_ids: 卡牌ID列表
        
        Returns:
            卡牌列表
        """
        return self.card_dao.get_cards_by_ids(card_ids)
    
    def search_cards(self, 
                    name: str = None,
                    card_type: str = None,
                    rarity: str = None,
                    set_name: str = None,
                    limit: int = 50,
                    offset: int = 0) -> List[Card]:
        """
        搜索卡牌
        
        Args:
            name: 卡牌名称关键词
            card_type: 卡牌类型
            rarity: 稀有度
            set_name: 系列名称
            limit: 限制数量
            offset: 偏移量
        
        Returns:
            卡牌列表
        """
        return self.card_dao.search_cards(name, card_type, rarity, set_name, limit, offset)
    
    def get_random_card_by_rarity(self, rarity: str) -> Optional[Card]:
        """
        根据稀有度获取随机卡牌
        
        Args:
            rarity: 稀有度
        
        Returns:
            随机卡牌或None
        """
        cards = self.card_dao.get_random_cards(1, rarity)
        return cards[0] if cards else None
    
    def get_random_cards_by_probability(self, count: int) -> List[Card]:
        """
        根据概率获取随机卡牌
        
        Args:
            count: 需要的卡牌数量
        
        Returns:
            随机卡牌列表
        """
        result_cards = []
        rarity_probabilities = self.card_dao.get_rarity_probabilities()
        
        if not rarity_probabilities:
            # 如果没有配置，使用默认概率
            rarity_probabilities = self.rarity_probabilities
        
        # 创建稀有度池
        rarity_pool = []
        for rarity, probability in rarity_probabilities.items():
            # 将概率转换为整数权重（乘以10000以保持精度）
            weight = int(probability * 10000)
            rarity_pool.extend([rarity] * weight)
        
        for _ in range(count):
            if rarity_pool:
                # 随机选择稀有度
                selected_rarity = random.choice(rarity_pool)
                # 根据稀有度获取随机卡牌
                card = self.get_random_card_by_rarity(selected_rarity)
                if card:
                    result_cards.append(card)
        
        return result_cards
    
    def open_pack(self, pack_type: str = "basic", guaranteed_rarity: str = None) -> List[Card]:
        """
        开启卡包
        
        Args:
            pack_type: 卡包类型
            guaranteed_rarity: 保底稀有度
        
        Returns:
            获得的卡牌列表
        """
        pack_configs = {
            "basic": {"count": 5, "guaranteed": "Uncommon"},
            "premium": {"count": 5, "guaranteed": "Rare"},
            "ultra": {"count": 3, "guaranteed": "Ultra Rare"}
        }
        
        config = pack_configs.get(pack_type, pack_configs["basic"])
        count = config["count"]
        guaranteed = guaranteed_rarity or config["guaranteed"]
        
        # 获取随机卡牌
        cards = self.get_random_cards_by_probability(count - 1)
        
        # 添加保底卡牌
        guaranteed_card = self.get_random_card_by_rarity(guaranteed)
        if guaranteed_card:
            cards.append(guaranteed_card)
        
        return cards
    
    def get_card_statistics(self) -> Dict[str, Any]:
        """
        获取卡牌统计信息
        
        Returns:
            统计信息字典
        """
        total_cards = self.card_dao.get_card_count()
        rarity_stats = self.card_dao.get_rarity_statistics()
        type_stats = self.card_dao.get_type_statistics()
        all_sets = self.card_dao.get_all_sets()
        
        return {
            "total_cards": total_cards,
            "total_sets": len(all_sets),
            "sets": all_sets,
            "rarity_distribution": rarity_stats,
            "type_distribution": type_stats,
            "available_rarities": list(rarity_stats.keys()),
            "available_types": list(type_stats.keys())
        }
    
    def get_collection_progress(self, user_cards: List[str]) -> Dict[str, Any]:
        """
        计算收藏进度
        
        Args:
            user_cards: 用户拥有的卡牌ID列表
        
        Returns:
            收藏进度信息
        """
        total_cards = self.card_dao.get_card_count()
        collected_count = len(set(user_cards))  # 去重计算
        
        # 按稀有度统计收藏进度
        rarity_stats = self.card_dao.get_rarity_statistics()
        rarity_progress = {}
        
        for rarity in rarity_stats.keys():
            rarity_cards = self.card_dao.get_cards_by_rarity(rarity, 1000)
            rarity_card_ids = {card.id for card in rarity_cards}
            collected_rarity = len(rarity_card_ids.intersection(set(user_cards)))
            
            rarity_progress[rarity] = {
                "collected": collected_rarity,
                "total": len(rarity_card_ids),
                "percentage": round((collected_rarity / len(rarity_card_ids)) * 100, 2) if rarity_card_ids else 0
            }
        
        # 按系列统计收藏进度
        all_sets = self.card_dao.get_all_sets()
        set_progress = {}
        
        for set_name in all_sets:
            set_cards = self.search_cards(set_name=set_name, limit=1000)
            set_card_ids = {card.id for card in set_cards}
            collected_set = len(set_card_ids.intersection(set(user_cards)))
            
            set_progress[set_name] = {
                "collected": collected_set,
                "total": len(set_card_ids),
                "percentage": round((collected_set / len(set_card_ids)) * 100, 2) if set_card_ids else 0
            }
        
        return {
            "total_progress": {
                "collected": collected_count,
                "total": total_cards,
                "percentage": round((collected_count / total_cards) * 100, 2) if total_cards > 0 else 0
            },
            "rarity_progress": rarity_progress,
            "set_progress": set_progress
        }
    
    def recommend_cards_for_deck(self, existing_cards: List[str], deck_type: str = None) -> List[Card]:
        """
        为卡组推荐卡牌
        
        Args:
            existing_cards: 已有的卡牌ID列表
            deck_type: 卡组类型（基于主要元素类型）
        
        Returns:
            推荐的卡牌列表
        """
        recommendations = []
        
        if deck_type:
            # 根据类型推荐
            type_cards = self.card_dao.get_cards_by_type(deck_type, 20)
            # 过滤掉已有的卡牌
            recommendations = [card for card in type_cards if card.id not in existing_cards]
        else:
            # 通用推荐：获取一些平衡的卡牌
            recommendations.extend(self.card_dao.get_random_cards(5, "Common"))
            recommendations.extend(self.card_dao.get_random_cards(3, "Uncommon"))
            recommendations.extend(self.card_dao.get_random_cards(2, "Rare"))
        
        return recommendations[:10]  # 限制推荐数量
    
    def validate_deck_composition(self, card_ids: List[str]) -> Dict[str, Any]:
        """
        验证卡组构成
        
        Args:
            card_ids: 卡组中的卡牌ID列表
        
        Returns:
            验证结果
        """
        cards = self.get_cards_by_ids(card_ids)
        
        # 统计信息
        total_cards = len(card_ids)
        unique_cards = len(set(card_ids))
        
        # 类型分布
        type_count = {}
        rarity_count = {}
        
        for card in cards:
            # 统计类型
            for card_type in card.types:
                type_count[card_type] = type_count.get(card_type, 0) + 1
            
            # 统计稀有度
            rarity_count[card.rarity] = rarity_count.get(card.rarity, 0) + 1
        
        # 卡组规则验证
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # 基本数量检查
        if total_cards < 20:
            validation_results["is_valid"] = False
            validation_results["errors"].append(f"卡组至少需要20张卡牌，当前只有{total_cards}张")
        elif total_cards > 60:
            validation_results["is_valid"] = False
            validation_results["errors"].append(f"卡组最多60张卡牌，当前有{total_cards}张")
        
        # 检查重复卡牌数量（假设每种卡牌最多4张）
        card_counts = {}
        for card_id in card_ids:
            card_counts[card_id] = card_counts.get(card_id, 0) + 1
        
        for card_id, count in card_counts.items():
            if count > 4:
                card = self.get_card_by_id(card_id)
                card_name = card.name if card else card_id
                validation_results["errors"].append(f"卡牌 {card_name} 超过数量限制（{count}/4）")
                validation_results["is_valid"] = False
        
        # 类型平衡建议
        if len(type_count) == 1:
            validation_results["warnings"].append("卡组只有一种类型，考虑添加其他类型增加战术多样性")
        elif len(type_count) > 3:
            validation_results["warnings"].append("卡组类型过多，可能缺乏聚焦，建议专注1-2种主要类型")
        
        # 稀有度平衡建议
        rare_cards = sum(count for rarity, count in rarity_count.items() if rarity not in ["Common", "Uncommon"])
        if rare_cards > total_cards * 0.6:
            validation_results["warnings"].append("高稀有度卡牌过多，可能影响卡组稳定性")
        elif rare_cards < total_cards * 0.1:
            validation_results["suggestions"].append("考虑添加一些稀有卡牌提升卡组强度")
        
        return {
            "validation": validation_results,
            "statistics": {
                "total_cards": total_cards,
                "unique_cards": unique_cards,
                "type_distribution": type_count,
                "rarity_distribution": rarity_count,
                "card_counts": card_counts
            }
        }
    
    def get_featured_cards(self, count: int = 10) -> List[Card]:
        """
        获取精选卡牌（用于展示）
        
        Args:
            count: 数量
        
        Returns:
            精选卡牌列表
        """
        featured_cards = []
        
        # 获取一些高稀有度卡牌
        rare_cards = self.card_dao.get_random_cards(count // 2, "Ultra Rare")
        featured_cards.extend(rare_cards)
        
        # 补充其他稀有卡牌
        other_rare = self.card_dao.get_random_cards(count - len(featured_cards), "Rare Holo")
        featured_cards.extend(other_rare)
        
        # 如果还不够，用普通稀有卡牌补充
        if len(featured_cards) < count:
            remaining = count - len(featured_cards)
            common_rare = self.card_dao.get_random_cards(remaining, "Rare")
            featured_cards.extend(common_rare)
        
        return featured_cards[:count]
    
    def get_daily_featured_card(self) -> Optional[Card]:
        """
        获取每日精选卡牌（基于日期的伪随机）
        
        Returns:
            每日精选卡牌
        """
        import datetime
        
        # 使用当前日期作为随机种子，确保每天的精选卡牌相同
        today = datetime.date.today()
        seed = int(today.strftime("%Y%m%d"))
        random.seed(seed)
        
        # 优先选择稀有卡牌
        rare_cards = self.card_dao.get_cards_by_rarity("Ultra Rare", 100)
        if not rare_cards:
            rare_cards = self.card_dao.get_cards_by_rarity("Rare Holo", 100)
        if not rare_cards:
            rare_cards = self.card_dao.get_cards_by_rarity("Rare", 100)
        
        # 恢复随机种子
        random.seed()
        
        return random.choice(rare_cards) if rare_cards else None
    
    def import_new_cards(self, new_cards_data: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        导入新的卡牌数据
        
        Args:
            new_cards_data: 新卡牌数据列表
        
        Returns:
            (成功数量, 失败数量)
        """
        try:
            cards = []
            for card_data in new_cards_data:
                try:
                    card = Card.from_json_card(card_data)
                    cards.append(card)
                except Exception as e:
                    print(f"解析新卡牌数据失败 {card_data.get('id', 'unknown')}: {e}")
                    continue
            
            if cards:
                return self.card_dao.insert_cards_batch(cards)
            else:
                return 0, len(new_cards_data)
                
        except Exception as e:
            print(f"导入新卡牌失败: {e}")
            return 0, len(new_cards_data) if new_cards_data else 0
    
    def export_cards_to_json(self, output_path: str, filters: Dict[str, Any] = None) -> bool:
        """
        导出卡牌数据到JSON文件
        
        Args:
            output_path: 输出文件路径
            filters: 过滤条件
        
        Returns:
            成功标志
        """
        try:
            # 根据过滤条件获取卡牌
            if filters:
                cards = self.search_cards(
                    name=filters.get('name'),
                    card_type=filters.get('type'),
                    rarity=filters.get('rarity'),
                    set_name=filters.get('set'),
                    limit=filters.get('limit', 10000)
                )
            else:
                # 获取所有卡牌
                cards = self.search_cards(limit=10000)
            
            # 转换为JSON格式
            cards_data = []
            for card in cards:
                card_dict = {
                    'id': card.id,
                    'name': card.name,
                    'hp': card.hp,
                    'types': card.types,
                    'rarity': card.rarity,
                    'attacks': [attack.to_dict() for attack in card.attacks],
                    'image': card.image_path,
                    'set_name': card.set_name,
                    'card_number': card.card_number
                }
                cards_data.append(card_dict)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(cards_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 成功导出 {len(cards_data)} 张卡牌到 {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 导出卡牌失败: {e}")
            return False
    
    def get_card_image_path(self, card_id: str) -> Optional[str]:
        """
        获取卡牌图片路径
        
        Args:
            card_id: 卡牌ID
        
        Returns:
            图片路径或None
        """
        card = self.get_card_by_id(card_id)
        if card and card.image_path:
            # 确保路径格式正确
            image_path = card.image_path.replace('\\', '/')
            
            # 如果是相对路径，添加card_assets前缀
            if not image_path.startswith('/') and not image_path.startswith('card_assets'):
                image_path = f"card_assets/{image_path}"
            
            return image_path
        return None
    
    def validate_card_images(self) -> Dict[str, Any]:
        """
        验证卡牌图片文件是否存在
        
        Returns:
            验证结果
        """
        all_cards = self.search_cards(limit=10000)
        
        existing_images = 0
        missing_images = []
        
        for card in all_cards:
            image_path = self.get_card_image_path(card.id)
            if image_path and os.path.exists(image_path):
                existing_images += 1
            else:
                missing_images.append({
                    'id': card.id,
                    'name': card.name,
                    'expected_path': image_path
                })
        
        return {
            'total_cards': len(all_cards),
            'existing_images': existing_images,
            'missing_images': len(missing_images),
            'missing_details': missing_images[:10],  # 只显示前10个
            'completion_rate': round((existing_images / len(all_cards)) * 100, 2) if all_cards else 0
        }
    
    def cleanup_invalid_cards(self) -> int:
        """
        清理无效的卡牌数据
        
        Returns:
            清理的卡牌数量
        """
        # 这里可以实现清理逻辑，比如删除没有名称的卡牌等
        # 为了安全起见，暂时不实现自动删除
        print("清理功能需要手动实现具体的清理规则")
        return 0
    
    def refresh_card_cache(self):
        """刷新卡牌缓存（如果有的话）"""
        # 重新加载稀有度概率
        self.rarity_probabilities = self.card_dao.get_rarity_probabilities()
        if not self.rarity_probabilities:
            self.rarity_probabilities = get_rarity_probabilities()
        
        print("✅ 卡牌缓存已刷新")
    
    def get_manager_status(self) -> Dict[str, Any]:
        """
        获取管理器状态信息
        
        Returns:
            状态信息字典
        """
        stats = self.get_card_statistics()
        image_validation = self.validate_card_images()
        
        return {
            'cards_loaded': stats['total_cards'] > 0,
            'total_cards': stats['total_cards'],
            'total_sets': stats['total_sets'],
            'available_rarities': len(stats['available_rarities']),
            'available_types': len(stats['available_types']),
            'image_completion_rate': image_validation['completion_rate'],
            'json_file_exists': os.path.exists(self.cards_json_path),
            'rarity_config_loaded': len(self.rarity_probabilities) > 0
        }