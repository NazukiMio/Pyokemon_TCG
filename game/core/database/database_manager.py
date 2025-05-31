"""
重构后的数据库管理器
使用DAO模式分离数据访问逻辑
"""

import sqlite3
import os
from datetime import datetime
from .daos.user_dao import UserDAO

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
                print("✅ 数据库连接已关闭")
            except sqlite3.Error as e:
                print(f"❌ 关闭数据库连接时出错: {e}")
    
    def setup_database(self):
        """设置数据库表结构"""
        try:
            # 创建用户表
            if self.user_dao:
                self.user_dao.create_user_table()
            
            # 用户卡牌收藏表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pokemon_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                UNIQUE(user_id, pokemon_id)
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
            
            # 卡组中的卡牌表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS deck_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER NOT NULL,
                pokemon_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deck_id) REFERENCES decks (id) ON DELETE CASCADE,
                UNIQUE(deck_id, pokemon_id)
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
                last_played TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
            ''')
            
            self.connection.commit()
            print("✅ 数据库表结构设置完成")
            return True
            
        except sqlite3.Error as e:
            print(f"❌ 设置数据库表结构失败: {e}")
            return False
    
    # 用户相关方法（委托给UserDAO）
    def register_user(self, username, password, email=None):
        """
        注册新用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱（可选）
        
        Returns:
            (成功标志, 消息)
        """
        if not self.user_dao:
            return False, "数据库未初始化"
        
        success, result = self.user_dao.create_user(username, password, email)
        if success:
            # 创建用户游戏统计记录
            self._create_user_stats(result)
            return True, "Usuario registrado con éxito"
        else:
            return False, result
    
    def login_user(self, username, password):
        """
        用户登录验证
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            (成功标志, 用户ID或错误消息)
        """
        if not self.user_dao:
            return False, "数据库未初始化"
        
        return self.user_dao.authenticate_user(username, password)
    
    def get_user_info(self, user_id):
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户信息字典或None
        """
        if not self.user_dao:
            return None
        
        return self.user_dao.get_user_by_id(user_id)
    
    def update_user_password(self, user_id, new_password):
        """
        更新用户密码
        
        Args:
            user_id: 用户ID
            new_password: 新密码
        
        Returns:
            (成功标志, 消息)
        """
        if not self.user_dao:
            return False, "数据库未初始化"
        
        return self.user_dao.update_user_password(user_id, new_password)
    
    def delete_user(self, user_id):
        """
        删除用户
        
        Args:
            user_id: 用户ID
        
        Returns:
            (成功标志, 消息)
        """
        if not self.user_dao:
            return False, "数据库未初始化"
        
        return self.user_dao.delete_user(user_id)
    
    # 游戏统计相关方法
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
    
    def get_user_stats(self, user_id):
        """
        获取用户游戏统计
        
        Args:
            user_id: 用户ID
        
        Returns:
            统计信息字典或None
        """
        try:
            self.cursor.execute(
                "SELECT * FROM game_stats WHERE user_id = ?",
                (user_id,)
            )
            stats = self.cursor.fetchone()
            
            if stats:
                return dict(stats)
            return None
        except sqlite3.Error as e:
            print(f"获取用户统计失败: {e}")
            return None
    
    def update_user_stats(self, user_id, **kwargs):
        """
        更新用户游戏统计
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的统计字段
        
        Returns:
            成功标志
        """
        try:
            # 构建更新SQL
            set_clauses = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['games_played', 'games_won', 'games_lost', 'cards_collected']:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clauses:
                return True
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(user_id)
            
            sql = f"UPDATE game_stats SET {', '.join(set_clauses)} WHERE user_id = ?"
            
            self.cursor.execute(sql, values)
            self.connection.commit()
            
            return True
        except sqlite3.Error as e:
            print(f"更新用户统计失败: {e}")
            return False
    
    # 卡牌相关方法
    def get_user_cards(self, user_id):
        """
        获取用户的所有卡牌
        
        Args:
            user_id: 用户ID
        
        Returns:
            卡牌列表或空列表
        """
        try:
            self.cursor.execute(
                "SELECT pokemon_id, quantity, obtained_at FROM user_cards WHERE user_id = ? ORDER BY obtained_at DESC",
                (user_id,)
            )
            cards = self.cursor.fetchall()
            
            return [dict(card) for card in cards] if cards else []
        except sqlite3.Error as e:
            print(f"获取用户卡牌失败: {e}")
            return []
    
    def add_card_to_user(self, user_id, pokemon_id, quantity=1):
        """
        向用户收藏添加卡牌
        
        Args:
            user_id: 用户ID
            pokemon_id: 宝可梦ID
            quantity: 添加数量
        
        Returns:
            成功标志
        """
        try:
            # 使用UPSERT操作
            self.cursor.execute(
                """
                INSERT INTO user_cards (user_id, pokemon_id, quantity)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, pokemon_id)
                DO UPDATE SET quantity = quantity + ?, obtained_at = CURRENT_TIMESTAMP
                """,
                (user_id, pokemon_id, quantity, quantity)
            )
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"添加用户卡牌失败: {e}")
            return False
    
    # 卡组相关方法
    def get_user_decks(self, user_id):
        """
        获取用户的所有卡组
        
        Args:
            user_id: 用户ID
        
        Returns:
            卡组列表或空列表
        """
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
        """
        为用户创建新卡组
        
        Args:
            user_id: 用户ID
            deck_name: 卡组名称
            description: 卡组描述
        
        Returns:
            (成功标志, 卡组ID或错误消息)
        """
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
    
    def add_card_to_deck(self, deck_id, pokemon_id, quantity=1):
        """
        向卡组添加卡牌
        
        Args:
            deck_id: 卡组ID
            pokemon_id: 宝可梦ID
            quantity: 添加数量
        
        Returns:
            成功标志
        """
        try:
            # 使用UPSERT操作
            self.cursor.execute(
                """
                INSERT INTO deck_cards (deck_id, pokemon_id, quantity)
                VALUES (?, ?, ?)
                ON CONFLICT(deck_id, pokemon_id)
                DO UPDATE SET quantity = quantity + ?, added_at = CURRENT_TIMESTAMP
                """,
                (deck_id, pokemon_id, quantity, quantity)
            )
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"向卡组添加卡牌失败: {e}")
            return False
    
    def get_deck_cards(self, deck_id):
        """
        获取卡组中的所有卡牌
        
        Args:
            deck_id: 卡组ID
        
        Returns:
            卡牌列表或空列表
        """
        try:
            self.cursor.execute(
                "SELECT pokemon_id, quantity, added_at FROM deck_cards WHERE deck_id = ? ORDER BY added_at DESC",
                (deck_id,)
            )
            cards = self.cursor.fetchall()
            
            return [dict(card) for card in cards] if cards else []
        except sqlite3.Error as e:
            print(f"获取卡组卡牌失败: {e}")
            return []
    
    def remove_card_from_deck(self, deck_id, pokemon_id, quantity=1):
        """
        从卡组移除卡牌
        
        Args:
            deck_id: 卡组ID
            pokemon_id: 宝可梦ID
            quantity: 移除数量
        
        Returns:
            成功标志
        """
        try:
            # 先获取当前数量
            self.cursor.execute(
                "SELECT quantity FROM deck_cards WHERE deck_id = ? AND pokemon_id = ?",
                (deck_id, pokemon_id)
            )
            result = self.cursor.fetchone()
            
            if not result:
                return False  # 卡牌不在卡组中
            
            current_quantity = result[0]
            new_quantity = current_quantity - quantity
            
            if new_quantity <= 0:
                # 完全移除卡牌
                self.cursor.execute(
                    "DELETE FROM deck_cards WHERE deck_id = ? AND pokemon_id = ?",
                    (deck_id, pokemon_id)
                )
            else:
                # 减少数量
                self.cursor.execute(
                    "UPDATE deck_cards SET quantity = ? WHERE deck_id = ? AND pokemon_id = ?",
                    (new_quantity, deck_id, pokemon_id)
                )
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"从卡组移除卡牌失败: {e}")
            return False
    
    def delete_deck(self, deck_id):
        """
        删除卡组（软删除）
        
        Args:
            deck_id: 卡组ID
        
        Returns:
            (成功标志, 消息)
        """
        try:
            self.cursor.execute(
                "UPDATE decks SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (deck_id,)
            )
            self.connection.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Mazo eliminado con éxito"
            else:
                return False, "Mazo no encontrado"
        except sqlite3.Error as e:
            print(f"删除卡组失败: {e}")
            return False, f"Error al eliminar mazo: {str(e)}"
    
    # 数据库维护方法
    def backup_database(self, backup_path=None):
        """
        备份数据库
        
        Args:
            backup_path: 备份文件路径，如果为None则使用默认路径
        
        Returns:
            成功标志
        """
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"data/backup/game_database_{timestamp}.db"
            
            # 确保备份目录存在
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # 创建备份
            backup_conn = sqlite3.connect(backup_path)
            self.connection.backup(backup_conn)
            backup_conn.close()
            
            print(f"✅ 数据库备份成功: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ 数据库备份失败: {e}")
            return False
    
    def vacuum_database(self):
        """
        清理数据库（回收空间）
        
        Returns:
            成功标志
        """
        try:
            self.cursor.execute("VACUUM")
            self.connection.commit()
            print("✅ 数据库清理完成")
            return True
        except sqlite3.Error as e:
            print(f"❌ 数据库清理失败: {e}")
            return False
    
    def get_database_info(self):
        """
        获取数据库信息
        
        Returns:
            数据库信息字典
        """
        try:
            info = {}
            
            # 获取数据库大小
            if os.path.exists(self.db_path):
                info['size_bytes'] = os.path.getsize(self.db_path)
                info['size_mb'] = round(info['size_bytes'] / (1024 * 1024), 2)
            
            # 获取表数量和记录数
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            info['table_count'] = len(tables)
            
            # 获取各表的记录数
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
    
    def execute_custom_query(self, query, params=None, fetch_all=True):
        """
        执行自定义查询（谨慎使用）
        
        Args:
            query: SQL查询语句
            params: 查询参数
            fetch_all: 是否获取所有结果
        
        Returns:
            查询结果或None
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                self.connection.commit()
                return self.cursor.rowcount
            else:
                if fetch_all:
                    return self.cursor.fetchall()
                else:
                    return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"执行自定义查询失败: {e}")
            return None
    
    # 高级查询方法
    def get_user_collection_summary(self, user_id):
        """
        获取用户收藏摘要
        
        Args:
            user_id: 用户ID
        
        Returns:
            收藏摘要字典
        """
        try:
            # 总卡牌数量
            self.cursor.execute(
                "SELECT COUNT(DISTINCT pokemon_id), SUM(quantity) FROM user_cards WHERE user_id = ?",
                (user_id,)
            )
            unique_cards, total_cards = self.cursor.fetchone()
            
            # 最新获得的卡牌
            self.cursor.execute(
                "SELECT pokemon_id, quantity, obtained_at FROM user_cards WHERE user_id = ? ORDER BY obtained_at DESC LIMIT 5",
                (user_id,)
            )
            recent_cards = [dict(row) for row in self.cursor.fetchall()]
            
            return {
                'unique_cards': unique_cards or 0,
                'total_cards': total_cards or 0,
                'recent_cards': recent_cards
            }
        except sqlite3.Error as e:
            print(f"获取用户收藏摘要失败: {e}")
            return {'unique_cards': 0, 'total_cards': 0, 'recent_cards': []}
    
    def get_deck_summary(self, deck_id):
        """
        获取卡组摘要
        
        Args:
            deck_id: 卡组ID
        
        Returns:
            卡组摘要字典
        """
        try:
            # 卡组基本信息
            self.cursor.execute(
                "SELECT name, description, created_at FROM decks WHERE id = ? AND is_active = 1",
                (deck_id,)
            )
            deck_info = self.cursor.fetchone()
            
            if not deck_info:
                return None
            
            # 卡牌统计
            self.cursor.execute(
                "SELECT COUNT(DISTINCT pokemon_id), SUM(quantity) FROM deck_cards WHERE deck_id = ?",
                (deck_id,)
            )
            unique_cards, total_cards = self.cursor.fetchone()
            
            return {
                'name': deck_info[0],
                'description': deck_info[1],
                'created_at': deck_info[2],
                'unique_cards': unique_cards or 0,
                'total_cards': total_cards or 0
            }
        except sqlite3.Error as e:
            print(f"获取卡组摘要失败: {e}")
            return None
    
    def search_user_cards(self, user_id, search_term=None, limit=50):
        """
        搜索用户卡牌
        
        Args:
            user_id: 用户ID
            search_term: 搜索关键词（可选）
            limit: 结果限制数量
        
        Returns:
            卡牌列表
        """
        try:
            if search_term:
                # 这里假设有一个pokemon表存储宝可梦信息
                # 实际实现时需要根据您的数据结构调整
                self.cursor.execute(
                    """
                    SELECT uc.pokemon_id, uc.quantity, uc.obtained_at 
                    FROM user_cards uc 
                    WHERE uc.user_id = ? AND uc.pokemon_id LIKE ?
                    ORDER BY uc.obtained_at DESC 
                    LIMIT ?
                    """,
                    (user_id, f"%{search_term}%", limit)
                )
            else:
                self.cursor.execute(
                    "SELECT pokemon_id, quantity, obtained_at FROM user_cards WHERE user_id = ? ORDER BY obtained_at DESC LIMIT ?",
                    (user_id, limit)
                )
            
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"搜索用户卡牌失败: {e}")
            return []
    
    def get_popular_cards(self, limit=20):
        """
        获取热门卡牌（被收藏最多的）
        
        Args:
            limit: 结果限制数量
        
        Returns:
            热门卡牌列表
        """
        try:
            self.cursor.execute(
                """
                SELECT pokemon_id, COUNT(DISTINCT user_id) as collectors, SUM(quantity) as total_quantity
                FROM user_cards 
                GROUP BY pokemon_id 
                ORDER BY collectors DESC, total_quantity DESC 
                LIMIT ?
                """,
                (limit,)
            )
            
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"获取热门卡牌失败: {e}")
            return []
    
    # 上下文管理器支持
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if exc_type is not None:
            print(f"数据库操作发生异常: {exc_val}")
            if self.connection:
                self.connection.rollback()
        self.close()
    
    def __del__(self):
        """析构函数"""
        self.close()