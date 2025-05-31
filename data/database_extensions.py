"""
数据库管理器扩展
为现有数据库管理器添加卡片和开包相关功能
"""

import sqlite3
import json
import time
from typing import Dict, List, Optional, Any

class DatabaseManagerExtensions:
    """
    数据库管理器扩展
    为现有的DatabaseManager类添加新功能
    """
    
    def __init__(self, database_manager):
        """
        初始化扩展
        
        Args:
            database_manager: 现有的数据库管理器实例
        """
        self.db_manager = database_manager
        self.db_path = database_manager.db_path
        
        # 创建新的表结构
        self._create_extended_tables()
        
        print("🔧 数据库管理器扩展初始化完成")
    
    def _create_extended_tables(self):
        """创建扩展的表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 用户卡片收藏表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_cards (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        card_id TEXT NOT NULL,
                        card_name TEXT NOT NULL,
                        rarity TEXT NOT NULL,
                        card_data TEXT,  -- JSON格式的完整卡片数据
                        obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_favorite BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # 用户卡组表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_decks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        deck_name TEXT NOT NULL,
                        deck_data TEXT,  -- JSON格式的卡组数据
                        is_default BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # 开包历史表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pack_openings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        pack_type TEXT NOT NULL,
                        cards_obtained TEXT,  -- JSON格式的获得卡片列表
                        opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # 对战历史表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS battle_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        player1_id INTEGER NOT NULL,
                        player2_id INTEGER,  -- NULL表示AI对战
                        player1_deck TEXT,   -- 使用的卡组
                        player2_deck TEXT,
                        winner_id INTEGER,
                        battle_data TEXT,    -- JSON格式的对战详情
                        battle_type TEXT DEFAULT 'casual',  -- casual, ranked, tournament
                        duration INTEGER,    -- 对战时长（秒）
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (player1_id) REFERENCES users (id),
                        FOREIGN KEY (player2_id) REFERENCES users (id),
                        FOREIGN KEY (winner_id) REFERENCES users (id)
                    )
                ''')
                
                # 用户成就表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_achievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        achievement_id TEXT NOT NULL,
                        achievement_name TEXT NOT NULL,
                        description TEXT,
                        unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # 添加users表的新字段（如果不存在）
                try:
                    cursor.execute('ALTER TABLE users ADD COLUMN pack_chances TEXT DEFAULT "{}"')
                except sqlite3.OperationalError:
                    pass  # 字段已存在
                
                try:
                    cursor.execute('ALTER TABLE users ADD COLUMN last_daily_claim INTEGER DEFAULT 0')
                except sqlite3.OperationalError:
                    pass  # 字段已存在
                
                try:
                    cursor.execute('ALTER TABLE users ADD COLUMN total_cards_opened INTEGER DEFAULT 0')
                except sqlite3.OperationalError:
                    pass  # 字段已存在
                
                try:
                    cursor.execute('ALTER TABLE users ADD COLUMN wins INTEGER DEFAULT 0')
                except sqlite3.OperationalError:
                    pass  # 字段已存在
                
                try:
                    cursor.execute('ALTER TABLE users ADD COLUMN losses INTEGER DEFAULT 0')
                except sqlite3.OperationalError:
                    pass  # 字段已存在
                
                # 创建索引以提高查询性能
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_cards_user_id ON user_cards(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_cards_card_id ON user_cards(card_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_decks_user_id ON user_decks(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_pack_openings_user_id ON pack_openings(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_battle_history_player1 ON battle_history(player1_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_battle_history_player2 ON battle_history(player2_id)')
                
                conn.commit()
                print("✅ 扩展表结构创建完成")
                
        except Exception as e:
            print(f"❌ 创建扩展表失败: {e}")
    
    def save_user_cards(self, user_id: int, cards: List[Dict]) -> bool:
        """
        保存用户获得的卡片
        
        Args:
            user_id: 用户ID
            cards: 卡片列表
            
        Returns:
            是否保存成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for card in cards:
                    cursor.execute('''
                        INSERT INTO user_cards (user_id, card_id, card_name, rarity, card_data)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        user_id,
                        card['id'],
                        card['name'],
                        card.get('rarity', 'common'),
                        json.dumps(card)
                    ))
                
                # 更新用户的总卡片数
                cursor.execute('''
                    UPDATE users 
                    SET total_cards_opened = total_cards_opened + ?
                    WHERE id = ?
                ''', (len(cards), user_id))
                
                conn.commit()
                print(f"💾 保存用户卡片成功: {len(cards)} 张卡片")
                return True
                
        except Exception as e:
            print(f"❌ 保存用户卡片失败: {e}")
            return False
    
    def get_user_cards(self, user_id: int, card_id: str = None) -> List[Dict]:
        """
        获取用户的卡片收藏
        
        Args:
            user_id: 用户ID
            card_id: 可选的特定卡片ID
            
        Returns:
            卡片列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if card_id:
                    cursor.execute('''
                        SELECT card_data, obtained_at, is_favorite
                        FROM user_cards
                        WHERE user_id = ? AND card_id = ?
                        ORDER BY obtained_at DESC
                    ''', (user_id, card_id))
                else:
                    cursor.execute('''
                        SELECT card_data, obtained_at, is_favorite
                        FROM user_cards
                        WHERE user_id = ?
                        ORDER BY obtained_at DESC
                    ''', (user_id,))
                
                cards = []
                for row in cursor.fetchall():
                    try:
                        card_data = json.loads(row[0])
                        card_data['obtained_at'] = row[1]
                        card_data['is_favorite'] = bool(row[2])
                        cards.append(card_data)
                    except json.JSONDecodeError:
                        continue
                
                return cards
                
        except Exception as e:
            print(f"❌ 获取用户卡片失败: {e}")
            return []
    
    def get_user_card_collection_summary(self, user_id: int) -> Dict:
        """
        获取用户卡片收藏摘要
        
        Args:
            user_id: 用户ID
            
        Returns:
            收藏摘要数据
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 总卡片数
                cursor.execute('''
                    SELECT COUNT(*) FROM user_cards WHERE user_id = ?
                ''', (user_id,))
                total_cards = cursor.fetchone()[0]
                
                # 唯一卡片数
                cursor.execute('''
                    SELECT COUNT(DISTINCT card_id) FROM user_cards WHERE user_id = ?
                ''', (user_id,))
                unique_cards = cursor.fetchone()[0]
                
                # 稀有度分布
                cursor.execute('''
                    SELECT rarity, COUNT(*) 
                    FROM user_cards 
                    WHERE user_id = ? 
                    GROUP BY rarity
                ''', (user_id,))
                rarity_distribution = dict(cursor.fetchall())
                
                # 收藏夹卡片数
                cursor.execute('''
                    SELECT COUNT(*) FROM user_cards 
                    WHERE user_id = ? AND is_favorite = 1
                ''', (user_id,))
                favorite_cards = cursor.fetchone()[0]
                
                return {
                    'total_cards': total_cards,
                    'unique_cards': unique_cards,
                    'rarity_distribution': rarity_distribution,
                    'favorite_cards': favorite_cards
                }
                
        except Exception as e:
            print(f"❌ 获取收藏摘要失败: {e}")
            return {}
    
    def update_user_data(self, user_id: int, **kwargs) -> bool:
        """
        更新用户数据（扩展版本）
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段
            
        Returns:
            是否更新成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 构建更新语句
                set_clauses = []
                values = []
                
                for key, value in kwargs.items():
                    if key in ['pack_chances', 'card_data']:
                        # JSON字段需要序列化
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value)
                    
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                
                if not set_clauses:
                    return True
                
                values.append(user_id)
                
                query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"
                cursor.execute(query, values)
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"❌ 更新用户数据失败: {e}")
            return False
    
    def save_pack_opening(self, user_id: int, pack_type: str, cards_obtained: List[Dict]) -> bool:
        """
        保存开包记录
        
        Args:
            user_id: 用户ID
            pack_type: 卡包类型
            cards_obtained: 获得的卡片列表
            
        Returns:
            是否保存成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO pack_openings (user_id, pack_type, cards_obtained)
                    VALUES (?, ?, ?)
                ''', (
                    user_id,
                    pack_type,
                    json.dumps(cards_obtained)
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ 保存开包记录失败: {e}")
            return False
    
    def get_pack_opening_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """
        获取开包历史
        
        Args:
            user_id: 用户ID
            limit: 返回记录数限制
            
        Returns:
            开包历史列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT pack_type, cards_obtained, opened_at
                    FROM pack_openings
                    WHERE user_id = ?
                    ORDER BY opened_at DESC
                    LIMIT ?
                ''', (user_id, limit))
                
                history = []
                for row in cursor.fetchall():
                    try:
                        cards = json.loads(row[1])
                        history.append({
                            'pack_type': row[0],
                            'cards_obtained': cards,
                            'opened_at': row[2],
                            'card_count': len(cards)
                        })
                    except json.JSONDecodeError:
                        continue
                
                return history
                
        except Exception as e:
            print(f"❌ 获取开包历史失败: {e}")
            return []
    
    def save_user_deck(self, user_id: int, deck_name: str, deck_cards: List[str], 
                       is_default: bool = False) -> Optional[int]:
        """
        保存用户卡组
        
        Args:
            user_id: 用户ID
            deck_name: 卡组名称
            deck_cards: 卡组中的卡片ID列表
            is_default: 是否为默认卡组
            
        Returns:
            卡组ID，失败返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 如果设置为默认卡组，先清除其他默认标记
                if is_default:
                    cursor.execute('''
                        UPDATE user_decks 
                        SET is_default = FALSE 
                        WHERE user_id = ?
                    ''', (user_id,))
                
                deck_data = {
                    'cards': deck_cards,
                    'card_count': len(deck_cards)
                }
                
                cursor.execute('''
                    INSERT INTO user_decks (user_id, deck_name, deck_data, is_default)
                    VALUES (?, ?, ?, ?)
                ''', (
                    user_id,
                    deck_name,
                    json.dumps(deck_data),
                    is_default
                ))
                
                deck_id = cursor.lastrowid
                conn.commit()
                
                print(f"💾 保存卡组成功: {deck_name} (ID: {deck_id})")
                return deck_id
                
        except Exception as e:
            print(f"❌ 保存卡组失败: {e}")
            return None
    
    def get_user_decks(self, user_id: int) -> List[Dict]:
        """
        获取用户的卡组列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            卡组列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, deck_name, deck_data, is_default, created_at, updated_at
                    FROM user_decks
                    WHERE user_id = ?
                    ORDER BY is_default DESC, updated_at DESC
                ''', (user_id,))
                
                decks = []
                for row in cursor.fetchall():
                    try:
                        deck_data = json.loads(row[2])
                        decks.append({
                            'id': row[0],
                            'name': row[1],
                            'cards': deck_data.get('cards', []),
                            'card_count': deck_data.get('card_count', 0),
                            'is_default': bool(row[3]),
                            'created_at': row[4],
                            'updated_at': row[5]
                        })
                    except json.JSONDecodeError:
                        continue
                
                return decks
                
        except Exception as e:
            print(f"❌ 获取用户卡组失败: {e}")
            return []
    
    def update_user_deck(self, deck_id: int, deck_name: str = None, 
                        deck_cards: List[str] = None, is_default: bool = None) -> bool:
        """
        更新用户卡组
        
        Args:
            deck_id: 卡组ID
            deck_name: 新的卡组名称
            deck_cards: 新的卡片列表
            is_default: 是否设为默认卡组
            
        Returns:
            是否更新成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取当前卡组信息
                cursor.execute('''
                    SELECT user_id, deck_data FROM user_decks WHERE id = ?
                ''', (deck_id,))
                
                row = cursor.fetchone()
                if not row:
                    return False
                
                user_id, current_deck_data = row
                deck_data = json.loads(current_deck_data)
                
                # 更新字段
                update_fields = []
                update_values = []
                
                if deck_name is not None:
                    update_fields.append("deck_name = ?")
                    update_values.append(deck_name)
                
                if deck_cards is not None:
                    deck_data['cards'] = deck_cards
                    deck_data['card_count'] = len(deck_cards)
                    update_fields.append("deck_data = ?")
                    update_values.append(json.dumps(deck_data))
                
                if is_default is not None:
                    if is_default:
                        # 清除其他默认标记
                        cursor.execute('''
                            UPDATE user_decks 
                            SET is_default = FALSE 
                            WHERE user_id = ? AND id != ?
                        ''', (user_id, deck_id))
                    
                    update_fields.append("is_default = ?")
                    update_values.append(is_default)
                
                if update_fields:
                    update_fields.append("updated_at = CURRENT_TIMESTAMP")
                    update_values.append(deck_id)
                    
                    query = f"UPDATE user_decks SET {', '.join(update_fields)} WHERE id = ?"
                    cursor.execute(query, update_values)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ 更新卡组失败: {e}")
            return False
    
    def delete_user_deck(self, deck_id: int) -> bool:
        """
        删除用户卡组
        
        Args:
            deck_id: 卡组ID
            
        Returns:
            是否删除成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM user_decks WHERE id = ?', (deck_id,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"❌ 删除卡组失败: {e}")
            return False
    
    def save_battle_result(self, player1_id: int, player2_id: Optional[int], 
                          winner_id: int, battle_data: Dict, 
                          battle_type: str = "casual", duration: int = 0) -> bool:
        """
        保存对战结果
        
        Args:
            player1_id: 玩家1 ID
            player2_id: 玩家2 ID（AI对战时为None）
            winner_id: 获胜者ID
            battle_data: 对战详细数据
            battle_type: 对战类型
            duration: 对战时长（秒）
            
        Returns:
            是否保存成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO battle_history 
                    (player1_id, player2_id, winner_id, player1_deck, player2_deck, 
                     battle_data, battle_type, duration)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    player1_id,
                    player2_id,
                    winner_id,
                    json.dumps(battle_data.get('player1_deck', {})),
                    json.dumps(battle_data.get('player2_deck', {})),
                    json.dumps(battle_data),
                    battle_type,
                    duration
                ))
                
                # 更新用户胜负记录
                if winner_id == player1_id:
                    cursor.execute('UPDATE users SET wins = wins + 1 WHERE id = ?', (player1_id,))
                    if player2_id:
                        cursor.execute('UPDATE users SET losses = losses + 1 WHERE id = ?', (player2_id,))
                elif winner_id == player2_id and player2_id:
                    cursor.execute('UPDATE users SET wins = wins + 1 WHERE id = ?', (player2_id,))
                    cursor.execute('UPDATE users SET losses = losses + 1 WHERE id = ?', (player1_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"❌ 保存对战结果失败: {e}")
            return False
    
    def get_user_battle_stats(self, user_id: int) -> Dict:
        """
        获取用户对战统计
        
        Args:
            user_id: 用户ID
            
        Returns:
            对战统计数据
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 基础胜负统计
                cursor.execute('''
                    SELECT wins, losses FROM users WHERE id = ?
                ''', (user_id,))
                
                row = cursor.fetchone()
                wins, losses = row if row else (0, 0)
                
                # 对战历史统计
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_battles,
                        SUM(CASE WHEN winner_id = ? THEN 1 ELSE 0 END) as victories,
                        AVG(duration) as avg_duration
                    FROM battle_history 
                    WHERE player1_id = ? OR player2_id = ?
                ''', (user_id, user_id, user_id))
                
                battle_row = cursor.fetchone()
                total_battles, victories, avg_duration = battle_row if battle_row else (0, 0, 0)
                
                # 按对战类型统计
                cursor.execute('''
                    SELECT battle_type, COUNT(*) 
                    FROM battle_history 
                    WHERE player1_id = ? OR player2_id = ?
                    GROUP BY battle_type
                ''', (user_id, user_id))
                
                battle_types = dict(cursor.fetchall())
                
                win_rate = (victories / total_battles * 100) if total_battles > 0 else 0
                
                return {
                    'wins': wins,
                    'losses': losses,
                    'total_battles': total_battles,
                    'win_rate': win_rate,
                    'avg_duration': avg_duration or 0,
                    'battle_types': battle_types
                }
                
        except Exception as e:
            print(f"❌ 获取对战统计失败: {e}")
            return {}
    
    def unlock_achievement(self, user_id: int, achievement_id: str, 
                          achievement_name: str, description: str = "") -> bool:
        """
        解锁用户成就
        
        Args:
            user_id: 用户ID
            achievement_id: 成就ID
            achievement_name: 成就名称
            description: 成就描述
            
        Returns:
            是否解锁成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 检查是否已经解锁
                cursor.execute('''
                    SELECT id FROM user_achievements 
                    WHERE user_id = ? AND achievement_id = ?
                ''', (user_id, achievement_id))
                
                if cursor.fetchone():
                    return False  # 已经解锁
                
                # 解锁成就
                cursor.execute('''
                    INSERT INTO user_achievements 
                    (user_id, achievement_id, achievement_name, description)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, achievement_id, achievement_name, description))
                
                conn.commit()
                print(f"🏆 用户 {user_id} 解锁成就: {achievement_name}")
                return True
                
        except Exception as e:
            print(f"❌ 解锁成就失败: {e}")
            return False
    
    def get_user_achievements(self, user_id: int) -> List[Dict]:
        """
        获取用户成就列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            成就列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT achievement_id, achievement_name, description, unlocked_at
                    FROM user_achievements
                    WHERE user_id = ?
                    ORDER BY unlocked_at DESC
                ''', (user_id,))
                
                achievements = []
                for row in cursor.fetchall():
                    achievements.append({
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'unlocked_at': row[3]
                    })
                
                return achievements
                
        except Exception as e:
            print(f"❌ 获取用户成就失败: {e}")
            return []
    
    def check_and_unlock_achievements(self, user_id: int) -> List[str]:
        """
        检查并解锁符合条件的成就
        
        Args:
            user_id: 用户ID
            
        Returns:
            新解锁的成就列表
        """
        unlocked_achievements = []
        
        try:
            # 获取用户数据
            collection_summary = self.get_user_card_collection_summary(user_id)
            battle_stats = self.get_user_battle_stats(user_id)
            
            # 定义成就条件
            achievements_to_check = [
                {
                    'id': 'first_card',
                    'name': 'Primera Carta',
                    'description': 'Obtén tu primera carta',
                    'condition': collection_summary.get('total_cards', 0) >= 1
                },
                {
                    'id': 'collector_10',
                    'name': 'Coleccionista Novato',
                    'description': 'Obtén 10 cartas diferentes',
                    'condition': collection_summary.get('unique_cards', 0) >= 10
                },
                {
                    'id': 'collector_50',
                    'name': 'Coleccionista Experto',
                    'description': 'Obtén 50 cartas diferentes',
                    'condition': collection_summary.get('unique_cards', 0) >= 50
                },
                {
                    'id': 'first_legendary',
                    'name': 'Leyenda Encontrada',
                    'description': 'Obtén tu primera carta legendaria',
                    'condition': collection_summary.get('rarity_distribution', {}).get('legendary', 0) >= 1
                },
                {
                    'id': 'first_win',
                    'name': 'Primera Victoria',
                    'description': 'Gana tu primera batalla',
                    'condition': battle_stats.get('wins', 0) >= 1
                },
                {
                    'id': 'win_streak_5',
                    'name': 'Racha Ganadora',
                    'description': 'Gana 5 batallas consecutivas',
                    'condition': battle_stats.get('wins', 0) >= 5
                },
                {
                    'id': 'battle_veteran',
                    'name': 'Veterano de Batalla',
                    'description': 'Participa en 100 batallas',
                    'condition': battle_stats.get('total_battles', 0) >= 100
                }
            ]
            
            # 检查每个成就
            for achievement in achievements_to_check:
                if achievement['condition']:
                    if self.unlock_achievement(
                        user_id, 
                        achievement['id'], 
                        achievement['name'], 
                        achievement['description']
                    ):
                        unlocked_achievements.append(achievement['name'])
            
        except Exception as e:
            print(f"❌ 检查成就失败: {e}")
        
        return unlocked_achievements
    
    def get_leaderboard(self, category: str = "wins", limit: int = 10) -> List[Dict]:
        """
        获取排行榜
        
        Args:
            category: 排行类别 (wins, total_cards, unique_cards)
            limit: 返回数量限制
            
        Returns:
            排行榜列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if category == "wins":
                    cursor.execute('''
                        SELECT username, wins, losses
                        FROM users
                        WHERE wins > 0
                        ORDER BY wins DESC, losses ASC
                        LIMIT ?
                    ''', (limit,))
                    
                    leaderboard = []
                    for i, row in enumerate(cursor.fetchall(), 1):
                        leaderboard.append({
                            'rank': i,
                            'username': row[0],
                            'wins': row[1],
                            'losses': row[2],
                            'win_rate': (row[1] / (row[1] + row[2]) * 100) if (row[1] + row[2]) > 0 else 0
                        })
                
                elif category == "total_cards":
                    cursor.execute('''
                        SELECT u.username, u.total_cards_opened
                        FROM users u
                        WHERE u.total_cards_opened > 0
                        ORDER BY u.total_cards_opened DESC
                        LIMIT ?
                    ''', (limit,))
                    
                    leaderboard = []
                    for i, row in enumerate(cursor.fetchall(), 1):
                        leaderboard.append({
                            'rank': i,
                            'username': row[0],
                            'total_cards': row[1]
                        })
                
                elif category == "unique_cards":
                    cursor.execute('''
                        SELECT u.username, COUNT(DISTINCT uc.card_id) as unique_cards
                        FROM users u
                        LEFT JOIN user_cards uc ON u.id = uc.user_id
                        GROUP BY u.id, u.username
                        HAVING unique_cards > 0
                        ORDER BY unique_cards DESC
                        LIMIT ?
                    ''', (limit,))
                    
                    leaderboard = []
                    for i, row in enumerate(cursor.fetchall(), 1):
                        leaderboard.append({
                            'rank': i,
                            'username': row[0],
                            'unique_cards': row[1]
                        })
                
                return leaderboard
                
        except Exception as e:
            print(f"❌ 获取排行榜失败: {e}")
            return []
    
    def get_database_stats(self) -> Dict:
        """
        获取数据库统计信息
        
        Returns:
            数据库统计数据
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # 用户统计
                cursor.execute('SELECT COUNT(*) FROM users')
                stats['total_users'] = cursor.fetchone()[0]
                
                # 卡片统计
                cursor.execute('SELECT COUNT(*) FROM user_cards')
                stats['total_cards_collected'] = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(DISTINCT card_id) FROM user_cards')
                stats['unique_cards_collected'] = cursor.fetchone()[0]
                
                # 卡组统计
                cursor.execute('SELECT COUNT(*) FROM user_decks')
                stats['total_decks'] = cursor.fetchone()[0]
                
                # 对战统计
                cursor.execute('SELECT COUNT(*) FROM battle_history')
                stats['total_battles'] = cursor.fetchone()[0]
                
                # 开包统计
                cursor.execute('SELECT COUNT(*) FROM pack_openings')
                stats['total_pack_openings'] = cursor.fetchone()[0]
                
                # 成就统计
                cursor.execute('SELECT COUNT(*) FROM user_achievements')
                stats['total_achievements_unlocked'] = cursor.fetchone()[0]
                
                # 稀有度分布
                cursor.execute('''
                    SELECT rarity, COUNT(*) 
                    FROM user_cards 
                    GROUP BY rarity
                ''')
                stats['rarity_distribution'] = dict(cursor.fetchall())
                
                return stats
                
        except Exception as e:
            print(f"❌ 获取数据库统计失败: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 90) -> bool:
        """
        清理旧数据
        
        Args:
            days: 保留最近几天的数据
            
        Returns:
            是否清理成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 清理旧的对战记录
                cursor.execute('''
                    DELETE FROM battle_history 
                    WHERE started_at < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_battles = cursor.rowcount
                
                # 清理旧的开包记录
                cursor.execute('''
                    DELETE FROM pack_openings 
                    WHERE opened_at < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_packs = cursor.rowcount
                
                conn.commit()
                
                print(f"🧹 数据清理完成: 删除 {deleted_battles} 场对战记录, {deleted_packs} 次开包记录")
                return True
                
        except Exception as e:
            print(f"❌ 数据清理失败: {e}")
            return False
    
    def backup_user_data(self, user_id: int) -> Dict:
        """
        备份用户数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户数据备份
        """
        try:
            backup_data = {
                'user_info': {},
                'cards': [],
                'decks': [],
                'achievements': [],
                'battle_stats': {},
                'pack_history': []
            }
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 用户基本信息
                cursor.execute('''
                    SELECT username, email, coins, pack_chances, wins, losses, total_cards_opened
                    FROM users WHERE id = ?
                ''', (user_id,))
                
                user_row = cursor.fetchone()
                if user_row:
                    backup_data['user_info'] = {
                        'username': user_row[0],
                        'email': user_row[1],
                        'coins': user_row[2],
                        'pack_chances': user_row[3],
                        'wins': user_row[4],
                        'losses': user_row[5],
                        'total_cards_opened': user_row[6]
                    }
                
                # 卡片收藏
                backup_data['cards'] = self.get_user_cards(user_id)
                
                # 卡组
                backup_data['decks'] = self.get_user_decks(user_id)
                
                # 成就
                backup_data['achievements'] = self.get_user_achievements(user_id)
                
                # 对战统计
                backup_data['battle_stats'] = self.get_user_battle_stats(user_id)
                
                # 开包历史
                backup_data['pack_history'] = self.get_pack_opening_history(user_id)
            
            backup_data['backup_timestamp'] = time.time()
            return backup_data
            
        except Exception as e:
            print(f"❌ 备份用户数据失败: {e}")
            return {}

# 使用示例和测试函数
def test_database_extensions():
    """测试数据库扩展功能"""
    # 这里可以添加测试代码
    print("🧪 数据库扩展功能测试")
    
    # 模拟测试数据
    test_user_id = 1
    test_cards = [
        {
            'id': 'pokemon_25',
            'name': 'Pikachu',
            'rarity': 'uncommon',
            'type': 'pokemon',
            'hp': 60
        }
    ]
    
    print("测试数据准备完成")