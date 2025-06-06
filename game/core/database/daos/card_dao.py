"""
卡牌数据访问对象 (DAO)
处理卡牌相关的数据库操作 - 第一部分
"""

import sqlite3
import json
from typing import List, Dict, Optional, Any, Tuple
from game.core.cards.card_data import Card, Attack

class CardDAO:
    """卡牌数据访问对象"""
    
    def __init__(self, connection):
        """
        初始化卡牌DAO
        
        Args:
            connection: 数据库连接对象
        """
        self.connection = connection
        self.cursor = connection.cursor()
    
    def create_card_tables(self):
        """创建卡牌相关表"""
        try:
            # 创建卡牌基础信息表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                hp INTEGER,
                types TEXT,
                rarity TEXT NOT NULL,
                attacks TEXT,
                image_path TEXT,
                set_name TEXT,
                card_number TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建稀有度配置表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rarity_config (
                rarity TEXT PRIMARY KEY,
                probability REAL NOT NULL,
                dust_value INTEGER DEFAULT 0,
                description TEXT,
                sort_order INTEGER DEFAULT 0
            )
            ''')
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"创建卡牌表失败: {e}")
            return False
    
    def insert_card(self, card: Card) -> bool:
        """
        插入或更新卡牌数据
        
        Args:
            card: 卡牌对象
        
        Returns:
            成功标志
        """
        try:
            card_dict = card.to_dict()
            self.cursor.execute('''
            INSERT OR REPLACE INTO cards 
            (id, name, hp, types, rarity, attacks, image_path, set_name, card_number, description, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                card_dict['id'],
                card_dict['name'],
                card_dict['hp'],
                card_dict['types'],
                card_dict['rarity'],
                card_dict['attacks'],
                card_dict['image_path'],
                card_dict['set_name'],
                card_dict['card_number'],
                card_dict['description']
            ))
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"插入卡牌失败 {card.id}: {e}")
            return False
    
    def insert_cards_batch(self, cards: List[Card]) -> Tuple[int, int]:
        """
        批量插入卡牌数据
        
        Args:
            cards: 卡牌列表
        
        Returns:
            (成功数量, 失败数量)
        """
        success_count = 0
        failed_count = 0
        
        try:
            # 开始事务
            self.cursor.execute("BEGIN TRANSACTION")
            
            for card in cards:
                try:
                    card_dict = card.to_dict()
                    self.cursor.execute('''
                    INSERT OR REPLACE INTO cards 
                    (id, name, hp, types, rarity, attacks, image_path, set_name, card_number, description, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (
                        card_dict['id'],
                        card_dict['name'],
                        card_dict['hp'],
                        card_dict['types'],
                        card_dict['rarity'],
                        card_dict['attacks'],
                        card_dict['image_path'],
                        card_dict['set_name'],
                        card_dict['card_number'],
                        card_dict['description']
                    ))
                    success_count += 1
                except sqlite3.Error as e:
                    print(f"插入卡牌失败 {card.id}: {e}")
                    failed_count += 1
                    continue
            
            self.connection.commit()
            print(f"批量插入完成: 成功 {success_count}, 失败 {failed_count}")
            return success_count, failed_count
            
        except sqlite3.Error as e:
            self.connection.rollback()
            print(f"批量插入事务失败: {e}")
            return 0, len(cards)
    
    def get_card_by_id(self, card_id: str) -> Optional[Card]:
        """
        根据ID获取卡牌
        
        Args:
            card_id: 卡牌ID
        
        Returns:
            卡牌对象或None
        """
        try:
            self.cursor.execute(
                "SELECT * FROM cards WHERE id = ?",
                (card_id,)
            )
            row = self.cursor.fetchone()
            
            if row:
                # 转换为字典
                card_data = {
                    'id': row[0],
                    'name': row[1],
                    'hp': row[2],
                    'types': row[3],
                    'rarity': row[4],
                    'attacks': row[5],
                    'image_path': row[6],
                    'set_name': row[7],
                    'card_number': row[8],
                    'description': row[9]
                }
                return Card.from_dict(card_data)
            return None
        except sqlite3.Error as e:
            print(f"获取卡牌失败 {card_id}: {e}")
            return None
    
    def get_cards_by_ids(self, card_ids: List[str]) -> List[Card]:
        """
        根据ID列表获取多张卡牌
        
        Args:
            card_ids: 卡牌ID列表
        
        Returns:
            卡牌列表
        """
        if not card_ids:
            return []
        
        try:
            placeholders = ','.join(['?' for _ in card_ids])
            self.cursor.execute(
                f"SELECT * FROM cards WHERE id IN ({placeholders})",
                card_ids
            )
            rows = self.cursor.fetchall()
            
            cards = []
            for row in rows:
                card_data = {
                    'id': row[0],
                    'name': row[1],
                    'hp': row[2],
                    'types': row[3],
                    'rarity': row[4],
                    'attacks': row[5],
                    'image_path': row[6],
                    'set_name': row[7],
                    'card_number': row[8],
                    'description': row[9]
                }
                cards.append(Card.from_dict(card_data))
            
            return cards
        except sqlite3.Error as e:
            print(f"批量获取卡牌失败: {e}")
            return []
    
    def delete_card(self, card_id: str) -> bool:
        """
        删除卡牌
        
        Args:
            card_id: 卡牌ID
        
        Returns:
            成功标志
        """
        try:
            self.cursor.execute("DELETE FROM cards WHERE id = ?", (card_id,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"删除卡牌失败 {card_id}: {e}")
            return False
    
    def clear_all_cards(self) -> bool:
        """
        清空所有卡牌数据
        
        Returns:
            成功标志
        """
        try:
            self.cursor.execute("DELETE FROM cards")
            self.connection.commit()
            print("已清空所有卡牌数据")
            return True
        except sqlite3.Error as e:
            print(f"清空卡牌数据失败: {e}")
            return False
        
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
        try:
            conditions = []
            params = []
            
            if name:
                conditions.append("name LIKE ?")
                params.append(f"%{name}%")
            
            if card_type:
                conditions.append("types LIKE ?")
                params.append(f'%"{card_type}"%')
            
            if rarity:
                conditions.append("rarity = ?")
                params.append(rarity)
            
            if set_name:
                conditions.append("set_name = ?")
                params.append(set_name)
            
            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
            
            query = f"""
            SELECT * FROM cards 
            {where_clause}
            ORDER BY name 
            LIMIT ? OFFSET ?
            """
            
            params.extend([limit, offset])
            
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            
            cards = []
            for row in rows:
                card_data = {
                    'id': row[0],
                    'name': row[1],
                    'hp': row[2],
                    'types': row[3],
                    'rarity': row[4],
                    'attacks': row[5],
                    'image_path': row[6],
                    'set_name': row[7],
                    'card_number': row[8],
                    'description': row[9]
                }
                cards.append(Card.from_dict(card_data))
            
            return cards
        except sqlite3.Error as e:
            print(f"搜索卡牌失败: {e}")
            return []
    
    def get_cards_by_rarity(self, rarity: str, limit: int = 100) -> List[Card]:
        """
        根据稀有度获取卡牌
        
        Args:
            rarity: 稀有度
            limit: 限制数量
        
        Returns:
            卡牌列表
        """
        try:
            self.cursor.execute(
                "SELECT * FROM cards WHERE rarity = ? ORDER BY name LIMIT ?",
                (rarity, limit)
            )
            rows = self.cursor.fetchall()
            
            cards = []
            for row in rows:
                card_data = {
                    'id': row[0],
                    'name': row[1],
                    'hp': row[2],
                    'types': row[3],
                    'rarity': row[4],
                    'attacks': row[5],
                    'image_path': row[6],
                    'set_name': row[7],
                    'card_number': row[8],
                    'description': row[9]
                }
                cards.append(Card.from_dict(card_data))
            
            return cards
        except sqlite3.Error as e:
            print(f"根据稀有度获取卡牌失败: {e}")
            return []
    
    def get_cards_by_type(self, card_type: str, limit: int = 100) -> List[Card]:
        """
        根据类型获取卡牌
        
        Args:
            card_type: 卡牌类型
            limit: 限制数量
        
        Returns:
            卡牌列表
        """
        try:
            self.cursor.execute(
                'SELECT * FROM cards WHERE types LIKE ? ORDER BY name LIMIT ?',
                (f'%"{card_type}"%', limit)
            )
            rows = self.cursor.fetchall()
            
            cards = []
            for row in rows:
                card_data = {
                    'id': row[0],
                    'name': row[1],
                    'hp': row[2],
                    'types': row[3],
                    'rarity': row[4],
                    'attacks': row[5],
                    'image_path': row[6],
                    'set_name': row[7],
                    'card_number': row[8],
                    'description': row[9]
                }
                cards.append(Card.from_dict(card_data))
            
            return cards
        except sqlite3.Error as e:
            print(f"根据类型获取卡牌失败: {e}")
            return []
    
    def get_random_cards(self, count: int, rarity: str = None) -> List[Card]:
        """
        获取随机卡牌
        
        Args:
            count: 数量
            rarity: 指定稀有度（可选）
        
        Returns:
            随机卡牌列表
        """
        try:
            if rarity:
                self.cursor.execute(
                    "SELECT * FROM cards WHERE rarity = ? ORDER BY RANDOM() LIMIT ?",
                    (rarity, count)
                )
            else:
                self.cursor.execute(
                    "SELECT * FROM cards ORDER BY RANDOM() LIMIT ?",
                    (count,)
                )
            
            rows = self.cursor.fetchall()
            
            cards = []
            for row in rows:
                card_data = {
                    'id': row[0],
                    'name': row[1],
                    'hp': row[2],
                    'types': row[3],
                    'rarity': row[4],
                    'attacks': row[5],
                    'image_path': row[6],
                    'set_name': row[7],
                    'card_number': row[8],
                    'description': row[9]
                }
                cards.append(Card.from_dict(card_data))
            
            return cards
        except sqlite3.Error as e:
            print(f"获取随机卡牌失败: {e}")
            return []
        
    def get_all_sets(self) -> List[str]:
        """
        获取所有卡牌系列
        
        Returns:
            系列名称列表
        """
        try:
            self.cursor.execute(
                "SELECT DISTINCT set_name FROM cards WHERE set_name IS NOT NULL AND set_name != '' ORDER BY set_name"
            )
            rows = self.cursor.fetchall()
            return [row[0] for row in rows]
        except sqlite3.Error as e:
            print(f"获取卡牌系列失败: {e}")
            return []
    
    def get_all_rarities(self) -> List[str]:
        """
        获取所有稀有度
        
        Returns:
            稀有度列表
        """
        try:
            self.cursor.execute(
                "SELECT DISTINCT rarity FROM cards ORDER BY rarity"
            )
            rows = self.cursor.fetchall()
            return [row[0] for row in rows]
        except sqlite3.Error as e:
            print(f"获取稀有度列表失败: {e}")
            return []
    
    def get_all_types(self) -> List[str]:
        """
        获取所有卡牌类型
        
        Returns:
            类型列表
        """
        try:
            # 获取所有类型字段
            self.cursor.execute("SELECT DISTINCT types FROM cards WHERE types IS NOT NULL")
            rows = self.cursor.fetchall()
            
            # 解析JSON数据并合并类型
            all_types = set()
            for row in rows:
                try:
                    types = json.loads(row[0])
                    if isinstance(types, list):
                        all_types.update(types)
                except (json.JSONDecodeError, TypeError):
                    continue
            
            return sorted(list(all_types))
        except sqlite3.Error as e:
            print(f"获取卡牌类型失败: {e}")
            return []
    
    def get_card_count(self) -> int:
        """
        获取卡牌总数
        
        Returns:
            卡牌数量
        """
        try:
            self.cursor.execute("SELECT COUNT(*) FROM cards")
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"获取卡牌数量失败: {e}")
            return 0
    
    def get_rarity_statistics(self) -> Dict[str, int]:
        """
        获取稀有度统计
        
        Returns:
            稀有度统计字典
        """
        try:
            self.cursor.execute(
                "SELECT rarity, COUNT(*) FROM cards GROUP BY rarity ORDER BY COUNT(*) DESC"
            )
            rows = self.cursor.fetchall()
            return {row[0]: row[1] for row in rows}
        except sqlite3.Error as e:
            print(f"获取稀有度统计失败: {e}")
            return {}
    
    def get_type_statistics(self) -> Dict[str, int]:
        """
        获取类型统计
        
        Returns:
            类型统计字典
        """
        try:
            # 这个查询比较复杂，需要解析JSON数据
            self.cursor.execute("SELECT types FROM cards WHERE types IS NOT NULL")
            rows = self.cursor.fetchall()
            
            type_count = {}
            for row in rows:
                try:
                    types = json.loads(row[0])
                    if isinstance(types, list):
                        for card_type in types:
                            type_count[card_type] = type_count.get(card_type, 0) + 1
                except (json.JSONDecodeError, TypeError):
                    continue
            
            return type_count
        except sqlite3.Error as e:
            print(f"获取类型统计失败: {e}")
            return {}
    
    def get_set_statistics(self) -> Dict[str, int]:
        """
        获取系列统计
        
        Returns:
            系列统计字典
        """
        try:
            self.cursor.execute(
                "SELECT set_name, COUNT(*) FROM cards WHERE set_name IS NOT NULL AND set_name != '' GROUP BY set_name ORDER BY COUNT(*) DESC"
            )
            rows = self.cursor.fetchall()
            return {row[0]: row[1] for row in rows}
        except sqlite3.Error as e:
            print(f"获取系列统计失败: {e}")
            return {}
    
    # 稀有度配置相关方法
    def insert_rarity_config(self, rarity: str, probability: float, dust_value: int = 0, sort_order: int = 0, description: str = "") -> bool:
        """
        插入稀有度配置
        
        Args:
            rarity: 稀有度名称
            probability: 概率
            dust_value: 分解价值
            sort_order: 排序权重
            description: 描述
        
        Returns:
            成功标志
        """
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO rarity_config (rarity, probability, dust_value, sort_order, description)
            VALUES (?, ?, ?, ?, ?)
            ''', (rarity, probability, dust_value, sort_order, description))
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"插入稀有度配置失败: {e}")
            return False
    
    def get_rarity_config(self) -> Dict[str, Dict[str, Any]]:
        """
        获取稀有度配置
        
        Returns:
            稀有度配置字典
        """
        try:
            self.cursor.execute(
                "SELECT rarity, probability, dust_value, sort_order, description FROM rarity_config ORDER BY sort_order"
            )
            rows = self.cursor.fetchall()
            
            config = {}
            for row in rows:
                config[row[0]] = {
                    'probability': row[1],
                    'dust_value': row[2],
                    'sort_order': row[3],
                    'description': row[4] if row[4] else ""
                }
            
            return config
        except sqlite3.Error as e:
            print(f"获取稀有度配置失败: {e}")
            return {}
    
    def get_rarity_probabilities(self) -> Dict[str, float]:
        """
        获取稀有度概率
        
        Returns:
            稀有度概率字典
        """
        try:
            self.cursor.execute(
                "SELECT rarity, probability FROM rarity_config ORDER BY sort_order"
            )
            rows = self.cursor.fetchall()
            return {row[0]: row[1] for row in rows}
        except sqlite3.Error as e:
            print(f"获取稀有度概率失败: {e}")
            return {}
    
    def get_rarity_dust_values(self) -> Dict[str, int]:
        """
        获取稀有度分解价值
        
        Returns:
            稀有度分解价值字典
        """
        try:
            self.cursor.execute(
                "SELECT rarity, dust_value FROM rarity_config ORDER BY sort_order"
            )
            rows = self.cursor.fetchall()
            return {row[0]: row[1] for row in rows}
        except sqlite3.Error as e:
            print(f"获取稀有度分解价值失败: {e}")
            return {}
    
    def update_rarity_config(self, rarity: str, **kwargs) -> bool:
        """
        更新稀有度配置
        
        Args:
            rarity: 稀有度名称
            **kwargs: 要更新的字段
        
        Returns:
            成功标志
        """
        try:
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['probability', 'dust_value', 'sort_order', 'description']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return True
            
            values.append(rarity)
            sql = f"UPDATE rarity_config SET {', '.join(set_clauses)} WHERE rarity = ?"
            
            self.cursor.execute(sql, values)
            self.connection.commit()
            
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"更新稀有度配置失败: {e}")
            return False
    
    def delete_rarity_config(self, rarity: str) -> bool:
        """
        删除稀有度配置
        
        Args:
            rarity: 稀有度名称
        
        Returns:
            成功标志
        """
        try:
            self.cursor.execute("DELETE FROM rarity_config WHERE rarity = ?", (rarity,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"删除稀有度配置失败: {e}")
            return False
        
    # 高级查询方法
    def search_cards_advanced(self, 
                             filters: Dict[str, Any],
                             sort_by: str = "name",
                             sort_order: str = "ASC",
                             limit: int = 50,
                             offset: int = 0) -> Tuple[List[Card], int]:
        """
        高级卡牌搜索
        
        Args:
            filters: 过滤条件字典
            sort_by: 排序字段
            sort_order: 排序方向 (ASC/DESC)
            limit: 限制数量
            offset: 偏移量
        
        Returns:
            (卡牌列表, 总数量)
        """
        try:
            conditions = []
            params = []
            
            # 构建WHERE子句
            if filters.get('name'):
                conditions.append("name LIKE ?")
                params.append(f"%{filters['name']}%")
            
            if filters.get('type'):
                conditions.append("types LIKE ?")
                params.append(f'%"{filters["type"]}"%')
            
            if filters.get('rarity'):
                if isinstance(filters['rarity'], list):
                    placeholders = ','.join(['?' for _ in filters['rarity']])
                    conditions.append(f"rarity IN ({placeholders})")
                    params.extend(filters['rarity'])
                else:
                    conditions.append("rarity = ?")
                    params.append(filters['rarity'])
            
            if filters.get('set_name'):
                conditions.append("set_name = ?")
                params.append(filters['set_name'])
            
            if filters.get('hp_min'):
                conditions.append("hp >= ?")
                params.append(filters['hp_min'])
            
            if filters.get('hp_max'):
                conditions.append("hp <= ?")
                params.append(filters['hp_max'])
            
            if filters.get('has_attacks'):
                if filters['has_attacks']:
                    conditions.append("attacks IS NOT NULL AND attacks != '[]'")
                else:
                    conditions.append("(attacks IS NULL OR attacks = '[]')")
            
            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
            
            # 验证排序字段
            valid_sort_fields = ['name', 'rarity', 'hp', 'set_name', 'card_number', 'created_at']
            if sort_by not in valid_sort_fields:
                sort_by = 'name'
            
            sort_order = sort_order.upper()
            if sort_order not in ['ASC', 'DESC']:
                sort_order = 'ASC'
            
            # 查询总数
            count_query = f"SELECT COUNT(*) FROM cards {where_clause}"
            self.cursor.execute(count_query, params)
            total_count = self.cursor.fetchone()[0]
            
            # 查询数据
            data_query = f"""
            SELECT * FROM cards 
            {where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT ? OFFSET ?
            """
            
            params.extend([limit, offset])
            self.cursor.execute(data_query, params)
            rows = self.cursor.fetchall()
            
            cards = []
            for row in rows:
                card_data = {
                    'id': row[0],
                    'name': row[1],
                    'hp': row[2],
                    'types': row[3],
                    'rarity': row[4],
                    'attacks': row[5],
                    'image_path': row[6],
                    'set_name': row[7],
                    'card_number': row[8],
                    'description': row[9]
                }
                cards.append(Card.from_dict(card_data))
            
            return cards, total_count
            
        except sqlite3.Error as e:
            print(f"高级搜索失败: {e}")
            return [], 0
    
    def get_cards_by_set_with_pagination(self, set_name: str, limit: int = 50, offset: int = 0) -> Tuple[List[Card], int]:
        """
        分页获取指定系列的卡牌
        
        Args:
            set_name: 系列名称
            limit: 限制数量
            offset: 偏移量
        
        Returns:
            (卡牌列表, 总数量)
        """
        try:
            # 查询总数
            self.cursor.execute(
                "SELECT COUNT(*) FROM cards WHERE set_name = ?",
                (set_name,)
            )
            total_count = self.cursor.fetchone()[0]
            
            # 查询数据
            self.cursor.execute(
                "SELECT * FROM cards WHERE set_name = ? ORDER BY card_number, name LIMIT ? OFFSET ?",
                (set_name, limit, offset)
            )
            rows = self.cursor.fetchall()
            
            cards = []
            for row in rows:
                card_data = {
                    'id': row[0],
                    'name': row[1],
                    'hp': row[2],
                    'types': row[3],
                    'rarity': row[4],
                    'attacks': row[5],
                    'image_path': row[6],
                    'set_name': row[7],
                    'card_number': row[8],
                    'description': row[9]
                }
                cards.append(Card.from_dict(card_data))
            
            return cards, total_count
            
        except sqlite3.Error as e:
            print(f"分页获取系列卡牌失败: {e}")
            return [], 0
    
    def get_cards_with_attacks_containing(self, search_term: str) -> List[Card]:
        """
        搜索攻击技能包含特定关键词的卡牌
        
        Args:
            search_term: 搜索关键词
        
        Returns:
            卡牌列表
        """
        try:
            self.cursor.execute(
                "SELECT * FROM cards WHERE attacks LIKE ? ORDER BY name",
                (f"%{search_term}%",)
            )
            rows = self.cursor.fetchall()
            
            cards = []
            for row in rows:
                card_data = {
                    'id': row[0],
                    'name': row[1],
                    'hp': row[2],
                    'types': row[3],
                    'rarity': row[4],
                    'attacks': row[5],
                    'image_path': row[6],
                    'set_name': row[7],
                    'card_number': row[8],
                    'description': row[9]
                }
                cards.append(Card.from_dict(card_data))
            
            return cards
        except sqlite3.Error as e:
            print(f"搜索攻击技能失败: {e}")
            return []
    
    def get_cards_by_hp_range(self, min_hp: int = 0, max_hp: int = 1000) -> List[Card]:
        """
        根据HP范围获取卡牌
        
        Args:
            min_hp: 最小HP
            max_hp: 最大HP
        
        Returns:
            卡牌列表
        """
        try:
            self.cursor.execute(
                "SELECT * FROM cards WHERE hp >= ? AND hp <= ? ORDER BY hp DESC, name",
                (min_hp, max_hp)
            )
            rows = self.cursor.fetchall()
            
            cards = []
            for row in rows:
                card_data = {
                    'id': row[0],
                    'name': row[1],
                    'hp': row[2],
                    'types': row[3],
                    'rarity': row[4],
                    'attacks': row[5],
                    'image_path': row[6],
                    'set_name': row[7],
                    'card_number': row[8],
                    'description': row[9]
                }
                cards.append(Card.from_dict(card_data))
            
            return cards
        except sqlite3.Error as e:
            print(f"根据HP范围获取卡牌失败: {e}")
            return []
    
    # 数据完整性和维护方法
    def validate_database_integrity(self) -> Dict[str, Any]:
        """
        验证数据库完整性
        
        Returns:
            验证结果字典
        """
        try:
            validation_result = {
                'valid': True,
                'issues': [],
                'statistics': {}
            }
            
            # 检查空ID
            self.cursor.execute("SELECT COUNT(*) FROM cards WHERE id IS NULL OR id = ''")
            empty_ids = self.cursor.fetchone()[0]
            if empty_ids > 0:
                validation_result['valid'] = False
                validation_result['issues'].append(f"发现 {empty_ids} 张卡牌ID为空")
            
            # 检查空名称
            self.cursor.execute("SELECT COUNT(*) FROM cards WHERE name IS NULL OR name = ''")
            empty_names = self.cursor.fetchone()[0]
            if empty_names > 0:
                validation_result['valid'] = False
                validation_result['issues'].append(f"发现 {empty_names} 张卡牌名称为空")
            
            # 检查重复ID
            self.cursor.execute("""
                SELECT id, COUNT(*) as count 
                FROM cards 
                GROUP BY id 
                HAVING COUNT(*) > 1
            """)
            duplicate_ids = self.cursor.fetchall()
            if duplicate_ids:
                validation_result['valid'] = False
                validation_result['issues'].append(f"发现 {len(duplicate_ids)} 个重复ID")
            
            # 检查JSON格式
            self.cursor.execute("SELECT id, types, attacks FROM cards")
            rows = self.cursor.fetchall()
            json_errors = 0
            
            for row in rows:
                card_id, types, attacks = row
                try:
                    if types:
                        json.loads(types)
                    if attacks:
                        json.loads(attacks)
                except json.JSONDecodeError:
                    json_errors += 1
            
            if json_errors > 0:
                validation_result['valid'] = False
                validation_result['issues'].append(f"发现 {json_errors} 张卡牌JSON格式错误")
            
            # 统计信息
            validation_result['statistics'] = {
                'total_cards': self.get_card_count(),
                'total_sets': len(self.get_all_sets()),
                'total_rarities': len(self.get_all_rarities()),
                'total_types': len(self.get_all_types())
            }
            
            return validation_result
            
        except sqlite3.Error as e:
            print(f"验证数据库完整性失败: {e}")
            return {'valid': False, 'issues': [f"验证过程出错: {e}"], 'statistics': {}}
    
    def cleanup_invalid_data(self, dry_run: bool = True) -> Dict[str, int]:
        """
        清理无效数据
        
        Args:
            dry_run: 是否为试运行（不实际删除）
        
        Returns:
            清理统计信息
        """
        try:
            cleanup_stats = {
                'empty_ids_removed': 0,
                'empty_names_removed': 0,
                'json_errors_fixed': 0,
                'duplicates_removed': 0
            }
            
            if not dry_run:
                # 删除空ID的记录
                self.cursor.execute("DELETE FROM cards WHERE id IS NULL OR id = ''")
                cleanup_stats['empty_ids_removed'] = self.cursor.rowcount
                
                # 删除空名称的记录
                self.cursor.execute("DELETE FROM cards WHERE name IS NULL OR name = ''")
                cleanup_stats['empty_names_removed'] = self.cursor.rowcount
                
                # 修复JSON错误（设为空）
                self.cursor.execute("SELECT id, types, attacks FROM cards")
                rows = self.cursor.fetchall()
                
                for row in rows:
                    card_id, types, attacks = row
                    updated = False
                    
                    try:
                        if types:
                            json.loads(types)
                    except json.JSONDecodeError:
                        self.cursor.execute("UPDATE cards SET types = '[]' WHERE id = ?", (card_id,))
                        updated = True
                    
                    try:
                        if attacks:
                            json.loads(attacks)
                    except json.JSONDecodeError:
                        self.cursor.execute("UPDATE cards SET attacks = '[]' WHERE id = ?", (card_id,))
                        updated = True
                    
                    if updated:
                        cleanup_stats['json_errors_fixed'] += 1
                
                # 处理重复ID（保留最新的）
                self.cursor.execute("""
                    DELETE FROM cards 
                    WHERE rowid NOT IN (
                        SELECT MAX(rowid) 
                        FROM cards 
                        GROUP BY id
                    )
                """)
                cleanup_stats['duplicates_removed'] = self.cursor.rowcount
                
                self.connection.commit()
            else:
                # 试运行：只统计不删除
                self.cursor.execute("SELECT COUNT(*) FROM cards WHERE id IS NULL OR id = ''")
                cleanup_stats['empty_ids_removed'] = self.cursor.fetchone()[0]
                
                self.cursor.execute("SELECT COUNT(*) FROM cards WHERE name IS NULL OR name = ''")
                cleanup_stats['empty_names_removed'] = self.cursor.fetchone()[0]
                
                # 统计JSON错误
                self.cursor.execute("SELECT types, attacks FROM cards")
                rows = self.cursor.fetchall()
                json_errors = 0
                
                for row in rows:
                    types, attacks = row
                    try:
                        if types:
                            json.loads(types)
                        if attacks:
                            json.loads(attacks)
                    except json.JSONDecodeError:
                        json_errors += 1
                
                cleanup_stats['json_errors_fixed'] = json_errors
                
                # 统计重复
                self.cursor.execute("""
                    SELECT COUNT(*) - COUNT(DISTINCT id) 
                    FROM cards
                """)
                cleanup_stats['duplicates_removed'] = self.cursor.fetchone()[0]
            
            return cleanup_stats
            
        except sqlite3.Error as e:
            print(f"清理数据失败: {e}")
            return {}
    
    def optimize_database(self) -> bool:
        """
        优化数据库性能
        
        Returns:
            成功标志
        """
        try:
            # 分析表
            self.cursor.execute("ANALYZE cards")
            self.cursor.execute("ANALYZE rarity_config")
            
            # 重建索引
            self.cursor.execute("REINDEX")
            
            # 清理碎片
            self.cursor.execute("VACUUM")
            
            self.connection.commit()
            print("✅ 数据库优化完成")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ 数据库优化失败: {e}")
            return False
    
    def export_cards_to_json(self, output_file: str, filters: Dict[str, Any] = None) -> bool:
        """
        导出卡牌数据到JSON文件
        
        Args:
            output_file: 输出文件路径
            filters: 过滤条件
        
        Returns:
            成功标志
        """
        try:
            if filters:
                cards, _ = self.search_cards_advanced(filters, limit=10000)
            else:
                cards = self.search_cards(limit=10000)
            
            cards_data = []
            for card in cards:
                card_dict = card.to_dict()
                # 转换JSON字符串回列表
                if isinstance(card_dict.get('types'), str):
                    try:
                        card_dict['types'] = json.loads(card_dict['types'])
                    except json.JSONDecodeError:
                        card_dict['types'] = []
                
                if isinstance(card_dict.get('attacks'), str):
                    try:
                        card_dict['attacks'] = json.loads(card_dict['attacks'])
                    except json.JSONDecodeError:
                        card_dict['attacks'] = []
                
                cards_data.append(card_dict)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cards_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 成功导出 {len(cards_data)} 张卡牌到 {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 导出卡牌失败: {e}")
            return False
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """
        获取数据库统计信息
        
        Returns:
            统计信息字典
        """
        try:
            stats = {
                'total_cards': self.get_card_count(),
                'rarity_distribution': self.get_rarity_statistics(),
                'type_distribution': self.get_type_statistics(),
                'set_distribution': self.get_set_statistics(),
                'hp_statistics': {},
                'attack_statistics': {}
            }
            
            # HP统计
            self.cursor.execute("SELECT MIN(hp), MAX(hp), AVG(hp) FROM cards WHERE hp IS NOT NULL")
            hp_stats = self.cursor.fetchone()
            if hp_stats:
                stats['hp_statistics'] = {
                    'min_hp': hp_stats[0],
                    'max_hp': hp_stats[1],
                    'avg_hp': round(hp_stats[2], 2) if hp_stats[2] else 0
                }
            
            # 攻击技能统计
            self.cursor.execute("SELECT COUNT(*) FROM cards WHERE attacks IS NOT NULL AND attacks != '[]'")
            cards_with_attacks = self.cursor.fetchone()[0]
            stats['attack_statistics'] = {
                'cards_with_attacks': cards_with_attacks,
                'cards_without_attacks': stats['total_cards'] - cards_with_attacks
            }
            
            return stats
            
        except sqlite3.Error as e:
            print(f"获取数据库统计失败: {e}")
            return {}
        
    # 工具和辅助方法
    def create_database_indexes(self) -> bool:
        """
        创建数据库索引以提高查询性能
        
        Returns:
            成功标志
        """
        try:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name)",
                "CREATE INDEX IF NOT EXISTS idx_cards_rarity ON cards(rarity)",
                "CREATE INDEX IF NOT EXISTS idx_cards_set_name ON cards(set_name)",
                "CREATE INDEX IF NOT EXISTS idx_cards_hp ON cards(hp)",
                "CREATE INDEX IF NOT EXISTS idx_cards_types ON cards(types)",
                "CREATE INDEX IF NOT EXISTS idx_cards_created_at ON cards(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_rarity_config_sort_order ON rarity_config(sort_order)"
            ]
            
            for index_sql in indexes:
                self.cursor.execute(index_sql)
            
            self.connection.commit()
            print("✅ 数据库索引创建完成")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ 创建数据库索引失败: {e}")
            return False
    
    def drop_database_indexes(self) -> bool:
        """
        删除数据库索引
        
        Returns:
            成功标志
        """
        try:
            indexes = [
                "DROP INDEX IF EXISTS idx_cards_name",
                "DROP INDEX IF EXISTS idx_cards_rarity", 
                "DROP INDEX IF EXISTS idx_cards_set_name",
                "DROP INDEX IF EXISTS idx_cards_hp",
                "DROP INDEX IF EXISTS idx_cards_types",
                "DROP INDEX IF EXISTS idx_cards_created_at",
                "DROP INDEX IF EXISTS idx_rarity_config_sort_order"
            ]
            
            for index_sql in indexes:
                self.cursor.execute(index_sql)
            
            self.connection.commit()
            print("✅ 数据库索引删除完成")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ 删除数据库索引失败: {e}")
            return False
    
    def check_card_exists(self, card_id: str) -> bool:
        """
        检查卡牌是否存在
        
        Args:
            card_id: 卡牌ID
        
        Returns:
            是否存在
        """
        try:
            self.cursor.execute("SELECT 1 FROM cards WHERE id = ?", (card_id,))
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"检查卡牌存在性失败: {e}")
            return False
    
    def get_cards_missing_images(self) -> List[Dict[str, str]]:
        """
        获取缺失图片的卡牌
        
        Returns:
            缺失图片的卡牌列表
        """
        try:
            import os
            
            self.cursor.execute("SELECT id, name, image_path FROM cards")
            rows = self.cursor.fetchall()
            
            missing_images = []
            for row in rows:
                card_id, name, image_path = row
                if not image_path or not os.path.exists(image_path):
                    missing_images.append({
                        'id': card_id,
                        'name': name,
                        'expected_path': image_path or f"images/{card_id}.png"
                    })
            
            return missing_images
            
        except Exception as e:
            print(f"检查图片文件失败: {e}")
            return []
    
    def update_image_paths(self, path_mapping: Dict[str, str]) -> int:
        """
        批量更新图片路径
        
        Args:
            path_mapping: 卡牌ID到图片路径的映射
        
        Returns:
            更新的卡牌数量
        """
        try:
            updated_count = 0
            
            for card_id, image_path in path_mapping.items():
                self.cursor.execute(
                    "UPDATE cards SET image_path = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (image_path, card_id)
                )
                if self.cursor.rowcount > 0:
                    updated_count += 1
            
            self.connection.commit()
            print(f"✅ 更新了 {updated_count} 张卡牌的图片路径")
            return updated_count
            
        except sqlite3.Error as e:
            print(f"❌ 更新图片路径失败: {e}")
            return 0
    
    def get_cards_by_pattern(self, pattern: str, field: str = "name") -> List[Card]:
        """
        根据模式匹配获取卡牌
        
        Args:
            pattern: SQL LIKE模式
            field: 要搜索的字段
        
        Returns:
            匹配的卡牌列表
        """
        try:
            valid_fields = ['name', 'description', 'set_name', 'card_number']
            if field not in valid_fields:
                field = 'name'
            
            query = f"SELECT * FROM cards WHERE {field} LIKE ? ORDER BY {field}"
            self.cursor.execute(query, (pattern,))
            rows = self.cursor.fetchall()
            
            cards = []
            for row in rows:
                card_data = {
                    'id': row[0],
                    'name': row[1],
                    'hp': row[2],
                    'types': row[3],
                    'rarity': row[4],
                    'attacks': row[5],
                    'image_path': row[6],
                    'set_name': row[7],
                    'card_number': row[8],
                    'description': row[9]
                }
                cards.append(Card.from_dict(card_data))
            
            return cards
            
        except sqlite3.Error as e:
            print(f"模式匹配搜索失败: {e}")
            return []
    
    def backup_table(self, backup_table_name: str) -> bool:
        """
        备份卡牌表
        
        Args:
            backup_table_name: 备份表名称
        
        Returns:
            成功标志
        """
        try:
            # 创建备份表
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {backup_table_name} AS 
                SELECT * FROM cards WHERE 1=0
            """)
            
            # 复制数据
            self.cursor.execute(f"""
                INSERT INTO {backup_table_name} 
                SELECT * FROM cards
            """)
            
            self.connection.commit()
            print(f"✅ 卡牌表备份到 {backup_table_name} 完成")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ 备份卡牌表失败: {e}")
            return False
    
    def restore_from_backup(self, backup_table_name: str) -> bool:
        """
        从备份表恢复数据
        
        Args:
            backup_table_name: 备份表名称
        
        Returns:
            成功标志
        """
        try:
            # 检查备份表是否存在
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (backup_table_name,)
            )
            if not self.cursor.fetchone():
                print(f"❌ 备份表 {backup_table_name} 不存在")
                return False
            
            # 清空当前表
            self.cursor.execute("DELETE FROM cards")
            
            # 从备份恢复
            self.cursor.execute(f"""
                INSERT INTO cards 
                SELECT * FROM {backup_table_name}
            """)
            
            self.connection.commit()
            print(f"✅ 从 {backup_table_name} 恢复数据完成")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ 从备份恢复失败: {e}")
            return False
    
    def get_dao_status(self) -> Dict[str, Any]:
        """
        获取DAO状态信息
        
        Returns:
            状态信息字典
        """
        try:
            status = {
                'connection_active': self.connection is not None,
                'tables_exist': False,
                'indexes_exist': False,
                'data_loaded': False,
                'last_operation': 'get_dao_status'
            }
            
            # 检查表是否存在
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('cards', 'rarity_config')"
            )
            tables = self.cursor.fetchall()
            status['tables_exist'] = len(tables) >= 2
            
            # 检查是否有数据
            if status['tables_exist']:
                card_count = self.get_card_count()
                status['data_loaded'] = card_count > 0
                status['card_count'] = card_count
            
            # 检查索引
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_cards_%'"
            )
            indexes = self.cursor.fetchall()
            status['indexes_exist'] = len(indexes) > 0
            status['index_count'] = len(indexes)
            
            return status
            
        except Exception as e:
            return {
                'connection_active': False,
                'error': str(e),
                'last_operation': 'get_dao_status'
            }
    
    def execute_custom_query(self, query: str, params: tuple = None, fetch_results: bool = True) -> Any:
        """
        执行自定义SQL查询（谨慎使用）
        
        Args:
            query: SQL查询语句
            params: 查询参数
            fetch_results: 是否获取结果
        
        Returns:
            查询结果或影响行数
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if query.strip().upper().startswith(('SELECT', 'WITH')):
                if fetch_results:
                    return self.cursor.fetchall()
                else:
                    return self.cursor.fetchone()
            else:
                self.connection.commit()
                return self.cursor.rowcount
                
        except sqlite3.Error as e:
            print(f"❌ 执行自定义查询失败: {e}")
            return None
    
    def close(self):
        """
        关闭DAO（通常由DatabaseManager管理，此处为兼容性保留）
        """
        # DAO本身不关闭连接，由DatabaseManager管理
        pass
    
    def __str__(self) -> str:
        """字符串表示"""
        status = self.get_dao_status()
        return f"CardDAO(cards={status.get('card_count', 0)}, tables={status.get('tables_exist', False)})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return self.__str__()