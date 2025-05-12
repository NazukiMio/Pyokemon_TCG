import sqlite3
import os
import hashlib
import time
from datetime import datetime

class DatabaseManager:
    """
    管理数据库连接和所有数据库相关操作的类
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
        self.connect()
        self.setup_database()
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
            self.cursor = self.connection.cursor()
            return True
        except sqlite3.Error as e:
            print(f"数据库连接错误: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
    
    def setup_database(self):
        """设置数据库表结构"""
        try:
            # 用户表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 用户卡牌收藏表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                pokemon_id INTEGER,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            # 卡组表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            ''')
            
            # 卡组中的卡牌表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS deck_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER,
                pokemon_id INTEGER,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY (deck_id) REFERENCES decks (id)
            )
            ''')
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"设置数据库出错: {e}")
            return False
    
    def hash_password(self, password):
        """
        对密码进行哈希处理
        
        Args:
            password: 原始密码
        
        Returns:
            哈希后的密码
        """
        # 使用SHA-256进行哈希，实际应用中应该使用更安全的方式如bcrypt
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password):
        """
        注册新用户
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            (成功标志, 消息)
        """
        try:
            # 检查用户名是否已存在
            self.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if self.cursor.fetchone():
                return False, "El nombre de usuario ya existe"
            
            # 哈希密码
            hashed_password = self.hash_password(password)
            
            # 插入新用户
            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            self.connection.commit()
            
            return True, "Usuario registrado con éxito"
        except sqlite3.Error as e:
            print(f"注册用户出错: {e}")
            return False, "Error en el registro: " + str(e)
    
    def login_user(self, username, password):
        """
        用户登录验证
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            (成功标志, 用户ID或错误消息)
        """
        try:
            # 哈希密码
            hashed_password = self.hash_password(password)
            
            # 验证用户名和密码
            self.cursor.execute(
                "SELECT id FROM users WHERE username = ? AND password = ?",
                (username, hashed_password)
            )
            user = self.cursor.fetchone()
            
            if user:
                return True, user['id']
            else:
                return False, "Nombre de usuario o contraseña incorrectos"
        except sqlite3.Error as e:
            print(f"登录验证出错: {e}")
            return False, "Error de inicio de sesión: " + str(e)
    
    def get_user_info(self, user_id):
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户信息字典或None
        """
        try:
            self.cursor.execute("SELECT id, username, created_at FROM users WHERE id = ?", (user_id,))
            user = self.cursor.fetchone()
            
            if user:
                return dict(user)
            return None
        except sqlite3.Error as e:
            print(f"获取用户信息出错: {e}")
            return None
    
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
                "SELECT pokemon_id, quantity FROM user_cards WHERE user_id = ?",
                (user_id,)
            )
            cards = self.cursor.fetchall()
            
            return [dict(card) for card in cards] if cards else []
        except sqlite3.Error as e:
            print(f"获取用户卡牌出错: {e}")
            return []
    
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
                "SELECT id, name, created_at FROM decks WHERE user_id = ?",
                (user_id,)
            )
            decks = self.cursor.fetchall()
            
            return [dict(deck) for deck in decks] if decks else []
        except sqlite3.Error as e:
            print(f"获取用户卡组出错: {e}")
            return []
    
    def create_new_deck(self, user_id, deck_name):
        """
        为用户创建新卡组
        
        Args:
            user_id: 用户ID
            deck_name: 卡组名称
        
        Returns:
            (成功标志, 卡组ID或错误消息)
        """
        try:
            self.cursor.execute(
                "INSERT INTO decks (user_id, name) VALUES (?, ?)",
                (user_id, deck_name)
            )
            self.connection.commit()
            
            return True, self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"创建卡组出错: {e}")
            return False, "Error al crear el mazo: " + str(e)
    
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
            # 检查卡牌是否已存在于用户收藏
            self.cursor.execute(
                "SELECT id, quantity FROM user_cards WHERE user_id = ? AND pokemon_id = ?",
                (user_id, pokemon_id)
            )
            card = self.cursor.fetchone()
            
            if card:
                # 更新已有卡牌数量
                new_quantity = card['quantity'] + quantity
                self.cursor.execute(
                    "UPDATE user_cards SET quantity = ? WHERE id = ?",
                    (new_quantity, card['id'])
                )
            else:
                # 添加新卡牌
                self.cursor.execute(
                    "INSERT INTO user_cards (user_id, pokemon_id, quantity) VALUES (?, ?, ?)",
                    (user_id, pokemon_id, quantity)
                )
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"添加卡牌出错: {e}")
            return False
    
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
            # 检查卡牌是否已存在于卡组
            self.cursor.execute(
                "SELECT id, quantity FROM deck_cards WHERE deck_id = ? AND pokemon_id = ?",
                (deck_id, pokemon_id)
            )
            card = self.cursor.fetchone()
            
            if card:
                # 更新已有卡牌数量
                new_quantity = card['quantity'] + quantity
                self.cursor.execute(
                    "UPDATE deck_cards SET quantity = ? WHERE id = ?",
                    (new_quantity, card['id'])
                )
            else:
                # 添加新卡牌
                self.cursor.execute(
                    "INSERT INTO deck_cards (deck_id, pokemon_id, quantity) VALUES (?, ?, ?)",
                    (deck_id, pokemon_id, quantity)
                )
            
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"向卡组添加卡牌出错: {e}")
            return False