"""
更新后的数据库管理器
添加卡牌系统支持
"""

import sqlite3
import os
from datetime import datetime
from game.core.database.daos.user_dao import UserDAO
from game.core.database.daos.card_dao import CardDAO

class DatabaseManager:
    """
    管理数据库连接和所有数据库相关操作的类
    使用DAO模式分离数据访问逻辑
    """
    
    def __init__(self, db_path="data/game_database.db"):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件的路径
        """
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        
        # DAO对象
        self.user_dao = None
        self.card_dao = None
        
        # 初始化数据库
        self.connect()
        self.setup_database()
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False  # 允许多线程访问
            )
            self.connection.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
            self.cursor = self.connection.cursor()
            
            # 启用外键约束
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            # 初始化DAO对象
            self.user_dao = UserDAO(self.connection)
            self.card_dao = CardDAO(self.connection)
            
            print("✅ 数据库连接成功")
            return True
        except sqlite3.Error as e:
            print(f"❌ 数据库连接错误: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                self.cursor = None
                self.user_dao = None
                self.card_dao = None
                print("✅ 数据库连接已关闭")
            except sqlite3.Error as e:
                print(f"❌ 关闭数据库连接时出错: {e}")
    
    def setup_database(self):
        """设置数据库表结构"""
        try:
            # 创建用户表
            if self.user_dao:
                self.user_dao.create_user_table()
            
            # 创建卡牌相关表
            if self.card_dao:
                self.card_dao.create_card_tables()
            
            # 更新用户卡牌收藏表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                card_id TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (card_id) REFERENCES cards (id) ON DELETE CASCADE,
                UNIQUE(user_id, card_id)
            )
            ''')
            
            # 卡组表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            ''')
            
            # 更新卡组中的卡牌表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS deck_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER NOT NULL,
                card_id TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE,
                FOREIGN KEY (card_id) REFERENCES cards (id) ON DELETE CASCADE,
                UNIQUE(deck_id, card_id)
            )
            ''')
            
            # 用户经济数据表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_economy (
                user_id INTEGER PRIMARY KEY,
                coins INTEGER DEFAULT 500,
                gems INTEGER DEFAULT 0,
                pack_points INTEGER DEFAULT 0,
                dust INTEGER DEFAULT 0,
                last_daily_bonus DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            ''')
            
            # 卡包类型表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pack_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                cost_coins INTEGER DEFAULT 100,
                cost_gems INTEGER DEFAULT 0,
                card_count INTEGER DEFAULT 5,
                guaranteed_rarity TEXT,
                is_available BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 卡包开启记录表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pack_openings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pack_type_id INTEGER NOT NULL,
                cards_obtained TEXT,
                cost_type TEXT,
                cost_amount INTEGER,
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (pack_type_id) REFERENCES pack_types (id)
            )
            ''')
            
            # 游戏统计表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                games_played INTEGER DEFAULT 0,
                games_won INTEGER DEFAULT 0,
                games_lost INTEGER DEFAULT 0,
                cards_collected INTEGER DEFAULT 0,
                packs_opened INTEGER DEFAULT 0,
                dust_earned INTEGER DEFAULT 0,
                last_played TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            ''')
            
            # 用户成就表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_type TEXT NOT NULL,
                achievement_name TEXT NOT NULL,
                description TEXT,
                progress INTEGER DEFAULT 0,
                target INTEGER NOT NULL,
                completed BOOLEAN DEFAULT 0,
                reward_coins INTEGER DEFAULT 0,
                reward_gems INTEGER DEFAULT 0,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user_id, achievement_name)
            )
            ''')
            
            # 每日任务表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_quests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                quest_type TEXT NOT NULL,
                description TEXT NOT NULL,
                progress INTEGER DEFAULT 0,
                target INTEGER NOT NULL,
                reward_coins INTEGER DEFAULT 50,
                reward_gems INTEGER DEFAULT 0,
                completed BOOLEAN DEFAULT 0,
                quest_date DATE NOT NULL,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user_id, quest_type, quest_date)
            )
            ''')

            # 用户会话表（安全机制）
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            ''')
            
            # 插入默认卡包类型
            self.cursor.execute('''
            INSERT OR IGNORE INTO pack_types (name, description, cost_coins, cost_gems, card_count, guaranteed_rarity) VALUES
            ('Basic Pack', 'Contains 5 random cards with at least 1 Uncommon', 100, 0, 5, 'Uncommon'),
            ('Premium Pack', 'Contains 5 cards with at least 1 Rare', 200, 0, 5, 'Rare'),
            ('Ultra Pack', 'Contains 3 cards with guaranteed Ultra Rare', 0, 50, 3, 'Ultra Rare')
            ''')

            # 战斗记录表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS battles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player1_id INTEGER NOT NULL,
                player2_id INTEGER, -- NULL表示AI对战
                player1_deck_id INTEGER,
                player2_deck_id INTEGER,
                winner_id INTEGER,
                battle_type TEXT DEFAULT 'PVE', -- PVE或PVP
                turn_count INTEGER DEFAULT 0,
                battle_data TEXT, -- JSON格式的详细战斗数据
                duration_seconds INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (player1_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (player2_id) REFERENCES users (id) ON DELETE CASCADE
            )
            ''')

            # AI对手配置表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_opponents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                difficulty TEXT DEFAULT 'easy', -- easy, medium, hard
                deck_template TEXT, -- JSON格式的AI卡组模板
                strategy_config TEXT, -- JSON格式的AI策略配置
                avatar_image TEXT,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建索引
            self._create_indexes()
            
            self.connection.commit()
            print("✅ 数据库表结构设置完成")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ 设置数据库表结构失败: {e}")
            return False
    
    def _create_indexes(self):
        """创建数据库索引"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_cards_user_id ON user_cards(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_cards_card_id ON user_cards(card_id)",
            "CREATE INDEX IF NOT EXISTS idx_deck_cards_deck_id ON deck_cards(deck_id)",
            "CREATE INDEX IF NOT EXISTS idx_cards_rarity ON cards(rarity)",
            "CREATE INDEX IF NOT EXISTS idx_cards_types ON cards(types)",
            "CREATE INDEX IF NOT EXISTS idx_pack_openings_user_id ON pack_openings(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_daily_quests_user_date ON daily_quests(user_id, quest_date)",
            "CREATE INDEX IF NOT EXISTS idx_game_stats_user_id ON game_stats(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_achievements_user_id ON user_achievements(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_battles_player1 ON battles(player1_id)",
            "CREATE INDEX IF NOT EXISTS idx_battles_player2 ON battles(player2_id)",
            "CREATE INDEX IF NOT EXISTS idx_battles_type ON battles(battle_type)",
            "CREATE INDEX IF NOT EXISTS idx_ai_opponents_difficulty ON ai_opponents(difficulty)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)"
        ]
        
        for index_sql in indexes:
            try:
                self.cursor.execute(index_sql)
            except sqlite3.Error as e:
                print(f"创建索引失败: {e}")
    
    # 保留原有的用户相关方法
    def register_user(self, username, password, email=None):
        """注册新用户"""
        if not self.user_dao:
            return False, "数据库未初始化"
        
        success, result = self.user_dao.create_user(username, password, email)
        if success:
            # 创建用户游戏统计记录
            self._create_user_stats(result)
            # 创建用户经济记录
            self._create_user_economy(result)
            return True, "Usuario registrado con éxito"
        else:
            return False, result
    
    def login_user(self, username, password):
        """用户登录验证"""
        if not self.user_dao:
            return False, "数据库未初始化"
        return self.user_dao.authenticate_user(username, password)
    
    def get_user_info(self, user_id):
        """获取用户信息"""
        if not self.user_dao:
            return None
        return self.user_dao.get_user_by_id(user_id)
    
    def _create_user_stats(self, user_id):
        """创建用户游戏统计记录"""
        try:
            self.cursor.execute(
                "INSERT INTO game_stats (user_id) VALUES (?)",
                (user_id,)
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"创建用户统计记录失败: {e}")
            return False
    
    def _create_user_economy(self, user_id):
        """创建用户经济记录"""
        try:
            self.cursor.execute(
                "INSERT INTO user_economy (user_id) VALUES (?)",
                (user_id,)
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"创建用户经济记录失败: {e}")
            return False
    
    # 新增：用户经济相关方法
    def get_user_economy(self, user_id):
        """获取用户经济数据"""
        try:
            self.cursor.execute(
                "SELECT * FROM user_economy WHERE user_id = ?",
                (user_id,)
            )
            economy = self.cursor.fetchone()
            
            if economy:
                return {
                    'user_id': economy[0],
                    'coins': economy[1],
                    'gems': economy[2],
                    'pack_points': economy[3],
                    'dust': economy[4],
                    'last_daily_bonus': economy[5]
                }
            return None
        except sqlite3.Error as e:
            print(f"获取用户经济数据失败: {e}")
            return None
    
    def update_user_economy(self, user_id, **kwargs):
        """更新用户经济数据"""
        try:
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['coins', 'gems', 'pack_points', 'dust', 'last_daily_bonus']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return True
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(user_id)
            
            sql = f"UPDATE user_economy SET {', '.join(set_clauses)} WHERE user_id = ?"
            
            self.cursor.execute(sql, values)
            self.connection.commit()
            
            return True
        except sqlite3.Error as e:
            print(f"更新用户经济数据失败: {e}")
            return False
    
    def add_currency(self, user_id, currency_type, amount):
        """添加货币"""
        try:
            if currency_type not in ['coins', 'gems', 'pack_points', 'dust']:
                return False
            
            self.cursor.execute(
                f"UPDATE user_economy SET {currency_type} = {currency_type} + ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (amount, user_id)
            )
            self.connection.commit()
            
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"添加货币失败: {e}")
            return False
    
    def spend_currency(self, user_id, currency_type, amount):
        """消费货币"""
        try:
            if currency_type not in ['coins', 'gems', 'pack_points', 'dust']:
                return False
            
            # 检查余额
            economy = self.get_user_economy(user_id)
            if not economy or economy[currency_type] < amount:
                return False
            
            self.cursor.execute(
                f"UPDATE user_economy SET {currency_type} = {currency_type} - ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (amount, user_id)
            )
            self.connection.commit()
            
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"消费货币失败: {e}")
            return False
    
    # 新增：卡包相关方法
    def get_pack_types(self):
        """获取所有卡包类型"""
        try:
            self.cursor.execute(
                "SELECT * FROM pack_types WHERE is_available = 1 ORDER BY cost_coins, cost_gems"
            )
            packs = self.cursor.fetchall()
            
            return [
                {
                    'id': pack[0],
                    'name': pack[1],
                    'description': pack[2],
                    'cost_coins': pack[3],
                    'cost_gems': pack[4],
                    'card_count': pack[5],
                    'guaranteed_rarity': pack[6]
                }
                for pack in packs
            ]
        except sqlite3.Error as e:
            print(f"获取卡包类型失败: {e}")
            return []
    
    def record_pack_opening(self, user_id, pack_type_id, cards_obtained, cost_type, cost_amount):
        """记录卡包开启"""
        try:
            import json
            
            self.cursor.execute('''
            INSERT INTO pack_openings (user_id, pack_type_id, cards_obtained, cost_type, cost_amount)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, pack_type_id, json.dumps(cards_obtained), cost_type, cost_amount))
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"记录卡包开启失败: {e}")
            return False
    
    def get_pack_opening_history(self, user_id, limit=20):
        """获取卡包开启历史"""
        try:
            self.cursor.execute('''
            SELECT po.*, pt.name as pack_name 
            FROM pack_openings po
            JOIN pack_types pt ON po.pack_type_id = pt.id
            WHERE po.user_id = ?
            ORDER BY po.opened_at DESC
            LIMIT ?
            ''', (user_id, limit))
            
            history = self.cursor.fetchall()
            
            result = []
            for record in history:
                import json
                try:
                    cards_obtained = json.loads(record[3])
                except:
                    cards_obtained = []
                
                result.append({
                    'id': record[0],
                    'pack_type_id': record[2],
                    'pack_name': record[7],
                    'cards_obtained': cards_obtained,
                    'cost_type': record[4],
                    'cost_amount': record[5],
                    'opened_at': record[6]
                })
            
            return result
        except sqlite3.Error as e:
            print(f"获取卡包开启历史失败: {e}")
            return []
    
    # 新增：成就相关方法
    def create_achievement(self, user_id, achievement_type, achievement_name, description, target, reward_coins=0, reward_gems=0):
        """创建成就"""
        try:
            self.cursor.execute('''
            INSERT OR IGNORE INTO user_achievements 
            (user_id, achievement_type, achievement_name, description, target, reward_coins, reward_gems)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, achievement_type, achievement_name, description, target, reward_coins, reward_gems))
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"创建成就失败: {e}")
            return False
    
    def update_achievement_progress(self, user_id, achievement_name, progress):
        """更新成就进度"""
        try:
            self.cursor.execute('''
            UPDATE user_achievements 
            SET progress = ?, 
                completed = CASE WHEN progress >= target THEN 1 ELSE 0 END,
                completed_at = CASE WHEN progress >= target AND completed = 0 THEN CURRENT_TIMESTAMP ELSE completed_at END
            WHERE user_id = ? AND achievement_name = ?
            ''', (progress, user_id, achievement_name))
            
            self.connection.commit()
            
            # 检查是否刚完成成就
            if self.cursor.rowcount > 0:
                self.cursor.execute(
                    "SELECT completed, reward_coins, reward_gems FROM user_achievements WHERE user_id = ? AND achievement_name = ? AND completed = 1 AND completed_at > datetime('now', '-1 minute')",
                    (user_id, achievement_name)
                )
                result = self.cursor.fetchone()
                
                if result:
                    # 发放奖励
                    if result[1] > 0:  # 金币奖励
                        self.add_currency(user_id, 'coins', result[1])
                    if result[2] > 0:  # 宝石奖励
                        self.add_currency(user_id, 'gems', result[2])
                    
                    return True, "成就完成！获得奖励"
            
            return True, "进度已更新"
        except sqlite3.Error as e:
            print(f"更新成就进度失败: {e}")
            return False, str(e)
    
    def get_user_achievements(self, user_id, completed_only=False):
        """获取用户成就"""
        try:
            if completed_only:
                condition = "WHERE user_id = ? AND completed = 1"
            else:
                condition = "WHERE user_id = ?"
            
            self.cursor.execute(f'''
            SELECT * FROM user_achievements 
            {condition}
            ORDER BY completed DESC, progress DESC
            ''', (user_id,))
            
            achievements = self.cursor.fetchall()
            
            return [
                {
                    'id': ach[0],
                    'achievement_type': ach[2],
                    'achievement_name': ach[3],
                    'description': ach[4],
                    'progress': ach[5],
                    'target': ach[6],
                    'completed': bool(ach[7]),
                    'reward_coins': ach[8],
                    'reward_gems': ach[9],
                    'completed_at': ach[10]
                }
                for ach in achievements
            ]
        except sqlite3.Error as e:
            print(f"获取用户成就失败: {e}")
            return []
    
    # 新增：每日任务相关方法
    def create_daily_quest(self, user_id, quest_type, description, target, quest_date, reward_coins=50, reward_gems=0):
        """创建每日任务"""
        try:
            self.cursor.execute('''
            INSERT OR IGNORE INTO daily_quests 
            (user_id, quest_type, description, target, quest_date, reward_coins, reward_gems)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, quest_type, description, target, quest_date, reward_coins, reward_gems))
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"创建每日任务失败: {e}")
            return False
    
    def update_quest_progress(self, user_id, quest_type, quest_date, progress):
        """更新任务进度"""
        try:
            self.cursor.execute('''
            UPDATE daily_quests 
            SET progress = ?, 
                completed = CASE WHEN progress >= target THEN 1 ELSE 0 END,
                completed_at = CASE WHEN progress >= target AND completed = 0 THEN CURRENT_TIMESTAMP ELSE completed_at END
            WHERE user_id = ? AND quest_type = ? AND quest_date = ?
            ''', (progress, user_id, quest_type, quest_date))
            
            self.connection.commit()
            
            # 检查是否刚完成任务
            if self.cursor.rowcount > 0:
                self.cursor.execute(
                    "SELECT completed, reward_coins, reward_gems FROM daily_quests WHERE user_id = ? AND quest_type = ? AND quest_date = ? AND completed = 1 AND completed_at > datetime('now', '-1 minute')",
                    (user_id, quest_type, quest_date)
                )
                result = self.cursor.fetchone()
                
                if result:
                    # 发放奖励
                    if result[1] > 0:  # 金币奖励
                        self.add_currency(user_id, 'coins', result[1])
                    if result[2] > 0:  # 宝石奖励
                        self.add_currency(user_id, 'gems', result[2])
                    
                    return True, "任务完成！获得奖励"
            
            return True, "进度已更新"
        except sqlite3.Error as e:
            print(f"更新任务进度失败: {e}")
            return False, str(e)
    
    def get_daily_quests(self, user_id, quest_date):
        """获取每日任务"""
        try:
            self.cursor.execute('''
            SELECT * FROM daily_quests 
            WHERE user_id = ? AND quest_date = ?
            ORDER BY completed, created_at
            ''', (user_id, quest_date))
            
            quests = self.cursor.fetchall()
            
            return [
                {
                    'id': quest[0],
                    'quest_type': quest[2],
                    'description': quest[3],
                    'progress': quest[4],
                    'target': quest[5],
                    'reward_coins': quest[6],
                    'reward_gems': quest[7],
                    'completed': bool(quest[8]),
                    'quest_date': quest[9],
                    'completed_at': quest[10]
                }
                for quest in quests
            ]
        except sqlite3.Error as e:
            print(f"获取每日任务失败: {e}")
            return []
    
    # 更新原有的统计方法
    def get_user_stats(self, user_id):
        """获取用户游戏统计"""
        try:
            self.cursor.execute(
                "SELECT * FROM game_stats WHERE user_id = ?",
                (user_id,)
            )
            stats = self.cursor.fetchone()
            
            if stats:
                return {
                    'user_id': stats[1],
                    'games_played': stats[2],
                    'games_won': stats[3],
                    'games_lost': stats[4],
                    'cards_collected': stats[5],
                    'packs_opened': stats[6],
                    'dust_earned': stats[7],
                    'last_played': stats[8]
                }
            return None
        except sqlite3.Error as e:
            print(f"获取用户统计失败: {e}")
            return None
    
    def update_user_stats(self, user_id, **kwargs):
        """更新用户游戏统计"""
        try:
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['games_played', 'games_won', 'games_lost', 'cards_collected', 'packs_opened', 'dust_earned']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return True
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            set_clauses.append("last_played = CURRENT_TIMESTAMP")
            values.append(user_id)
            
            sql = f"UPDATE game_stats SET {', '.join(set_clauses)} WHERE user_id = ?"
            
            self.cursor.execute(sql, values)
            self.connection.commit()
            
            return True
        except sqlite3.Error as e:
            print(f"更新用户统计失败: {e}")
            return False
    
    # 保留原有的卡牌相关方法但使用新的卡牌ID格式
    def get_user_cards(self, user_id):
        """获取用户的所有卡牌"""
        try:
            self.cursor.execute(
                "SELECT card_id, quantity, obtained_at FROM user_cards WHERE user_id = ? ORDER BY obtained_at DESC",
                (user_id,)
            )
            cards = self.cursor.fetchall()
            
            return [{'card_id': card[0], 'quantity': card[1], 'obtained_at': card[2]} for card in cards] if cards else []
        except sqlite3.Error as e:
            print(f"获取用户卡牌失败: {e}")
            return []
    
    def add_card_to_user(self, user_id, card_id, quantity=1):
        """向用户收藏添加卡牌"""
        try:
            self.cursor.execute(
                """
                INSERT INTO user_cards (user_id, card_id, quantity)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, card_id)
                DO UPDATE SET quantity = quantity + ?, obtained_at = CURRENT_TIMESTAMP
                """,
                (user_id, card_id, quantity, quantity)
            )
            
            self.connection.commit()
            
            # 更新统计
            current_stats = self.get_user_stats(user_id)
            if current_stats:
                new_cards_collected = current_stats['cards_collected'] + quantity
                self.update_user_stats(user_id, cards_collected=new_cards_collected)
            
            return True
        except sqlite3.Error as e:
            print(f"添加用户卡牌失败: {e}")
            return False
    
    # 保留原有的卡组相关方法
    def get_user_decks(self, user_id):
        """获取用户的所有卡组"""
        try:
            self.cursor.execute(
                "SELECT id, name, description, created_at, updated_at FROM decks WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC",
                (user_id,)
            )
            decks = self.cursor.fetchall()
            
            return [dict(deck) for deck in decks] if decks else []
        except sqlite3.Error as e:
            print(f"获取用户卡组失败: {e}")
            return []
    
    def create_new_deck(self, user_id, deck_name, description=""):
        """为用户创建新卡组"""
        try:
            self.cursor.execute(
                "INSERT INTO decks (user_id, name, description) VALUES (?, ?, ?)",
                (user_id, deck_name, description)
            )
            self.connection.commit()
            
            return True, self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"创建卡组失败: {e}")
            return False, f"Error al crear el mazo: {str(e)}"
    
    def add_card_to_deck(self, deck_id, card_id, quantity=1):
        """向卡组添加卡牌"""
        try:
            self.cursor.execute(
                """
                INSERT INTO deck_cards (deck_id, card_id, quantity)
                VALUES (?, ?, ?)
                ON CONFLICT(deck_id, card_id)
                DO UPDATE SET quantity = quantity + ?, added_at = CURRENT_TIMESTAMP
                """,
                (deck_id, card_id, quantity, quantity)
            )
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"向卡组添加卡牌失败: {e}")
            return False
    
    def get_deck_cards(self, deck_id):
        """获取卡组中的所有卡牌"""
        try:
            self.cursor.execute(
                "SELECT card_id, quantity, added_at FROM deck_cards WHERE deck_id = ? ORDER BY added_at DESC",
                (deck_id,)
            )
            cards = self.cursor.fetchall()
            
            return [dict(card) for card in cards] if cards else []
        except sqlite3.Error as e:
            print(f"获取卡组卡牌失败: {e}")
            return []
    
    def create_battle_record(self, player1_id, player2_id, player1_deck_id, player2_deck_id, battle_type="PVE"):
        """创建战斗记录"""
        try:
            self.cursor.execute('''
            INSERT INTO battles (player1_id, player2_id, player1_deck_id, player2_deck_id, battle_type)
            VALUES (?, ?, ?, ?, ?)
            ''', (player1_id, player2_id, player1_deck_id, player2_deck_id, battle_type))
            self.connection.commit()
            return True, self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"创建战斗记录失败: {e}")
            return False, str(e)

    def update_battle_result(self, battle_id, winner_id, turn_count, battle_data, duration_seconds):
        """更新战斗结果"""
        try:
            import json
            self.cursor.execute('''
            UPDATE battles 
            SET winner_id = ?, turn_count = ?, battle_data = ?, duration_seconds = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (winner_id, turn_count, json.dumps(battle_data), duration_seconds, battle_id))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"更新战斗结果失败: {e}")
            return False

    def get_user_battles(self, user_id, limit=20):
        """获取用户战斗历史"""
        try:
            self.cursor.execute('''
            SELECT b.*, u1.username as player1_name, u2.username as player2_name,
                d1.name as player1_deck_name, d2.name as player2_deck_name
            FROM battles b
            LEFT JOIN users u1 ON b.player1_id = u1.id
            LEFT JOIN users u2 ON b.player2_id = u2.id
            LEFT JOIN decks d1 ON b.player1_deck_id = d1.id
            LEFT JOIN decks d2 ON b.player2_deck_id = d2.id
            WHERE b.player1_id = ? OR b.player2_id = ?
            ORDER BY b.created_at DESC
            LIMIT ?
            ''', (user_id, user_id, limit))
            
            battles = self.cursor.fetchall()
            return [dict(battle) for battle in battles]
        except sqlite3.Error as e:
            print(f"获取用户战斗历史失败: {e}")
            return []

    def get_ai_opponents(self, difficulty=None):
        """获取AI对手列表"""
        try:
            if difficulty:
                self.cursor.execute(
                    "SELECT * FROM ai_opponents WHERE difficulty = ? AND is_active = 1 ORDER BY name",
                    (difficulty,)
                )
            else:
                self.cursor.execute(
                    "SELECT * FROM ai_opponents WHERE is_active = 1 ORDER BY difficulty, name"
                )
            
            opponents = self.cursor.fetchall()
            return [dict(opponent) for opponent in opponents]
        except sqlite3.Error as e:
            print(f"获取AI对手失败: {e}")
            return []

    # 保留其他原有方法...
    def backup_database(self, backup_path=None):
        """备份数据库"""
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"data/backup/game_database_{timestamp}.db"
            
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            backup_conn = sqlite3.connect(backup_path)
            self.connection.backup(backup_conn)
            backup_conn.close()
            
            print(f"✅ 数据库备份成功: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ 数据库备份失败: {e}")
            return False
    
    def get_database_info(self):
        """获取数据库信息"""
        try:
            info = {}
            
            if os.path.exists(self.db_path):
                info['size_bytes'] = os.path.getsize(self.db_path)
                info['size_mb'] = round(info['size_bytes'] / (1024 * 1024), 2)
            
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            info['table_count'] = len(tables)
            
            table_counts = {}
            for table in tables:
                table_name = table[0]
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = self.cursor.fetchone()[0]
                table_counts[table_name] = count
            
            info['table_counts'] = table_counts
            info['total_records'] = sum(table_counts.values())
            
            return info
        except Exception as e:
            print(f"获取数据库信息失败: {e}")
            return {}
    
    # 上下文管理器支持
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"数据库操作发生异常: {exc_val}")
            if self.connection:
                self.connection.rollback()
        self.close()
    
    # gestion de la session
    def save_session(self, session_token, user_id, expires_at, ip_address=None):
        """Guardar la sesión del usuario"""
        try:
            self.cursor.execute('''
            INSERT INTO user_sessions (user_id, session_token, expires_at, ip_address)
            VALUES (?, ?, ?, ?)
            ''', (user_id, session_token, expires_at, ip_address))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Guardar la sesión falló: {e}")
            return False
    
    def validate_session(self, session_token):
        """Validar la sesión del usuario"""
        try:
            self.cursor.execute('''
            SELECT user_id FROM user_sessions 
            WHERE session_token = ? AND is_active = 1 AND expires_at > CURRENT_TIMESTAMP
            ''', (session_token,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Validar la sesión falló: {e}")
            return None
    
    def delete_session(self, session_token):
        """Eliminar la sesión del usuario"""
        try:
            self.cursor.execute(
                "UPDATE user_sessions SET is_active = 0 WHERE session_token = ?",
                (session_token,)
            )
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Eliminar la sesión falló: {e}")
            return False
    
    def cleanup_expired_sessions(self):
        """Decomisionar las sesiones expiradas"""
        try:
            self.cursor.execute(
                "UPDATE user_sessions SET is_active = 0 WHERE expires_at <= CURRENT_TIMESTAMP"
            )
            self.connection.commit()
            return self.cursor.rowcount
        except sqlite3.Error as e:
            print(f"Decomisionar las sesiones expiradas falló: {e}")
            return 0
        
    def __del__(self):
        self.close()