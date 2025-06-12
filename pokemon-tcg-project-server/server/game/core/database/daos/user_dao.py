"""
用户数据访问对象 (DAO)
分离数据访问逻辑
"""

import sqlite3
import hashlib
from datetime import datetime

class UserDAO:
    """用户数据访问对象，处理用户相关的数据库操作"""
    
    def __init__(self, connection):
        """
        初始化用户DAO
        
        Args:
            connection: 数据库连接对象
        """
        self.connection = connection
        self.cursor = connection.cursor()
    
    def create_user_table(self):
        """创建用户表"""
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
            ''')
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"创建用户表失败: {e}")
            return False
    
    def hash_password(self, password):
        """
        对密码进行哈希处理
        
        Args:
            password: 原始密码
        
        Returns:
            哈希后的密码
        """
        # 使用SHA-256进行哈希，实际生产环境建议使用bcrypt
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password, email=None):
        """
        创建新用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱（可选）
        
        Returns:
            (成功标志, 用户ID或错误消息)
        """
        try:
            # 检查用户名是否已存在
            if self.username_exists(username):
                return False, "El nombre de usuario ya existe"
            
            # 哈希密码
            hashed_password = self.hash_password(password)
            
            # 插入新用户
            self.cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, hashed_password, email)
            )
            self.connection.commit()
            
            user_id = self.cursor.lastrowid
            return True, user_id
            
        except sqlite3.Error as e:
            print(f"创建用户失败: {e}")
            return False, f"Error al crear usuario: {str(e)}"
    
    def authenticate_user(self, username, password):
        """
        验证用户身份
        
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
                "SELECT id FROM users WHERE username = ? AND password = ? AND is_active = 1",
                (username, hashed_password)
            )
            user = self.cursor.fetchone()
            
            if user:
                return True, user[0]
            else:
                return False, "Nombre de usuario o contraseña incorrectos"
                
        except sqlite3.Error as e:
            print(f"用户认证失败: {e}")
            return False, f"Error de autenticación: {str(e)}"
    
    def get_user_by_id(self, user_id):
        """
        根据ID获取用户信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户信息字典或None
        """
        try:
            self.cursor.execute(
                "SELECT id, username, email, created_at, updated_at FROM users WHERE id = ? AND is_active = 1",
                (user_id,)
            )
            user = self.cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'created_at': user[3],
                    'updated_at': user[4]
                }
            return None
            
        except sqlite3.Error as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    def get_user_by_username(self, username):
        """
        根据用户名获取用户信息
        
        Args:
            username: 用户名
        
        Returns:
            用户信息字典或None
        """
        try:
            self.cursor.execute(
                "SELECT id, username, email, created_at, updated_at FROM users WHERE username = ? AND is_active = 1",
                (username,)
            )
            user = self.cursor.fetchone()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'created_at': user[3],
                    'updated_at': user[4]
                }
            return None
            
        except sqlite3.Error as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    def username_exists(self, username):
        """
        检查用户名是否存在
        
        Args:
            username: 用户名
        
        Returns:
            布尔值
        """
        try:
            self.cursor.execute(
                "SELECT 1 FROM users WHERE username = ? AND is_active = 1",
                (username,)
            )
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"检查用户名存在性失败: {e}")
            return False
    
    def update_user_password(self, user_id, new_password):
        """
        更新用户密码
        
        Args:
            user_id: 用户ID
            new_password: 新密码
        
        Returns:
            (成功标志, 消息)
        """
        try:
            hashed_password = self.hash_password(new_password)
            
            self.cursor.execute(
                "UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (hashed_password, user_id)
            )
            self.connection.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Contraseña actualizada exitosamente"
            else:
                return False, "Usuario no encontrado"
                
        except sqlite3.Error as e:
            print(f"更新密码失败: {e}")
            return False, f"Error al actualizar contraseña: {str(e)}"
    
    def update_user_email(self, user_id, email):
        """
        更新用户邮箱
        
        Args:
            user_id: 用户ID
            email: 新邮箱
        
        Returns:
            (成功标志, 消息)
        """
        try:
            self.cursor.execute(
                "UPDATE users SET email = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (email, user_id)
            )
            self.connection.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Email actualizado exitosamente"
            else:
                return False, "Usuario no encontrado"
                
        except sqlite3.Error as e:
            print(f"更新邮箱失败: {e}")
            return False, f"Error al actualizar email: {str(e)}"
    
    def delete_user(self, user_id):
        """
        删除用户（软删除）
        
        Args:
            user_id: 用户ID
        
        Returns:
            (成功标志, 消息)
        """
        try:
            # 软删除：将is_active设为0而不是真正删除记录
            self.cursor.execute(
                "UPDATE users SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
            self.connection.commit()
            
            if self.cursor.rowcount > 0:
                return True, "Cuenta eliminada exitosamente"
            else:
                return False, "Usuario no encontrado"
                
        except sqlite3.Error as e:
            print(f"删除用户失败: {e}")
            return False, f"Error al eliminar cuenta: {str(e)}"
    
    def get_user_count(self):
        """
        获取活跃用户数量
        
        Returns:
            用户数量
        """
        try:
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"获取用户数量失败: {e}")
            return 0
    
    def get_recent_users(self, limit=10):
        """
        获取最近注册的用户
        
        Args:
            limit: 限制数量
        
        Returns:
            用户列表
        """
        try:
            self.cursor.execute(
                "SELECT id, username, created_at FROM users WHERE is_active = 1 ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            users = self.cursor.fetchall()
            
            return [
                {
                    'id': user[0],
                    'username': user[1],
                    'created_at': user[2]
                }
                for user in users
            ]
            
        except sqlite3.Error as e:
            print(f"获取最近用户失败: {e}")
            return []