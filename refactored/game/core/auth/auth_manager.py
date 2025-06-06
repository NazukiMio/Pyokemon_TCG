"""
重构后的认证管理器
修复导入路径并优化代码结构
"""

from game.core.database.database_manager import DatabaseManager

class AuthManager:
    """
    管理用户认证相关的类
    处理用户登录、注册和会话管理
    """
    
    def __init__(self, db_manager=None):
        """
        初始化认证管理器
        
        Args:
            db_manager: 数据库管理器实例，如果为None则创建新实例
        """
        self.db_manager = db_manager if db_manager else DatabaseManager()
        self.current_user_id = None
        self.username = None
    
    def register(self, username, password, confirm_password):
        """
        注册新用户
        
        Args:
            username: 用户名
            password: 密码
            confirm_password: 确认密码
        
        Returns:
            (成功标志, 消息)
        """
        # 数据验证
        if not username or not password:
            return False, "El nombre de usuario y la contraseña son obligatorios"
        
        if password != confirm_password:
            return False, "Las contraseñas no coinciden"
        
        if len(username) < 3:
            return False, "El nombre de usuario debe tener al menos 3 caracteres"
        
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        # 验证密码强度
        is_strong, strength_message = self.validate_password_strength(password)
        if not is_strong:
            return False, strength_message
        
        # 注册用户
        return self.db_manager.register_user(username, password)
    
    def login(self, username, password):
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            (成功标志, 消息)
        """
        if not username or not password:
            return False, "El nombre de usuario y la contraseña son obligatorios"
        
        success, result = self.db_manager.login_user(username, password)
        
        if success:
            # 登录成功，保存用户信息
            self.current_user_id = result
            self.username = username
            return True, "Inicio de sesión exitoso"
        else:
            # 登录失败，返回错误消息
            return False, result
    
    def logout(self):
        """
        退出登录
        
        Returns:
            成功标志
        """
        self.current_user_id = None
        self.username = None
        return True
    
    def is_logged_in(self):
        """
        检查用户是否已登录
        
        Returns:
            布尔值表示登录状态
        """
        return self.current_user_id is not None
    
    def get_current_user_id(self):
        """
        获取当前登录用户的ID
        
        Returns:
            用户ID或None
        """
        return self.current_user_id
    
    def get_current_username(self):
        """
        获取当前登录用户的用户名
        
        Returns:
            用户名或None
        """
        return self.username
    
    def get_user_info(self):
        """
        获取当前登录用户的信息
        
        Returns:
            用户信息字典或None
        """
        if not self.current_user_id:
            return None
        
        return self.db_manager.get_user_info(self.current_user_id)
    
    def validate_password_strength(self, password):
        """
        验证密码强度
        
        Args:
            password: 待验证的密码
        
        Returns:
            (强度是否足够的布尔值, 提示消息)
        """
        # 基本长度检查
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        # 检查是否包含数字
        has_digit = any(char.isdigit() for char in password)
        # 检查是否包含字母
        has_alpha = any(char.isalpha() for char in password)
        
        if not (has_digit and has_alpha):
            return False, "La contraseña debe contener al menos un número y una letra"
        
        return True, "Contraseña válida"
    
    def change_password(self, old_password, new_password, confirm_password):
        """
        修改密码
        
        Args:
            old_password: 旧密码
            new_password: 新密码
            confirm_password: 确认新密码
        
        Returns:
            (成功标志, 消息)
        """
        if not self.is_logged_in():
            return False, "Debe iniciar sesión primero"
        
        if new_password != confirm_password:
            return False, "Las contraseñas nuevas no coinciden"
        
        # 验证新密码强度
        is_strong, strength_message = self.validate_password_strength(new_password)
        if not is_strong:
            return False, strength_message
        
        # 验证旧密码
        success, _ = self.db_manager.login_user(self.username, old_password)
        if not success:
            return False, "La contraseña actual es incorrecta"
        
        # 更新密码
        return self.db_manager.update_user_password(self.current_user_id, new_password)
    
    def delete_account(self, password):
        """
        删除账户
        
        Args:
            password: 确认密码
        
        Returns:
            (成功标志, 消息)
        """
        if not self.is_logged_in():
            return False, "Debe iniciar sesión primero"
        
        # 验证密码
        success, _ = self.db_manager.login_user(self.username, password)
        if not success:
            return False, "Contraseña incorrecta"
        
        # 删除用户
        success, message = self.db_manager.delete_user(self.current_user_id)
        if success:
            self.logout()
        
        return success, message
    
_auth_instance = None

def get_auth_manager():
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = AuthManager()
    return _auth_instance