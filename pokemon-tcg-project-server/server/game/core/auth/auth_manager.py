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
        # self.current_user_id = None
        self.current_token = None
        self.username = None
    
    def _generate_session_token(self, user_id):
        """Generar un token de sesión para el usuario"""
        import uuid
        import base64
        import time
        import hashlib
        
        # Crear el token de sesión
        timestamp = str(int(time.time()))
        random_part = str(uuid.uuid4())
        raw_token = f"{user_id}:{timestamp}:{random_part}"
        
        # Crear checksum
        checksum = hashlib.md5(raw_token.encode()).hexdigest()[:8]
        
        # Combinar el token y el checksum
        full_token = f"{raw_token}:{checksum}"
        encoded_token = base64.b64encode(full_token.encode()).decode()
        
        return encoded_token
    
    def _validate_token_format(self, token):
        """Validar token de sesión"""
        try:
            import base64
            import hashlib
            
            # Decodificar el token
            decoded = base64.b64decode(token.encode()).decode()
            parts = decoded.split(':')
            
            if len(parts) != 4:
                return None
            
            user_id, timestamp, random_part, checksum = parts
            
            # Validar checksum
            raw_token = f"{user_id}:{timestamp}:{random_part}"
            expected_checksum = hashlib.md5(raw_token.encode()).hexdigest()[:8]
            
            if checksum != expected_checksum:
                return None
            
            return int(user_id)
        except Exception:
            return None

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
        Inicio de sesión de usuario
        
        Args:
            username: Usuario
            password: Contraseña
        
        Returns:
            (Signatura de exito, Mensaje)
        """
        if not username or not password:
            return False, "El nombre de usuario y la contraseña son obligatorios"
        
        success, result = self.db_manager.login_user(username, password)
        
        if success:
            # Inicio de sesión exitoso, generar token de sesión
            session_token = self._generate_session_token(result)
            
            # Calcular fecha de expiración (después de 2 horas)
            import datetime
            expires_at = datetime.datetime.now() + datetime.timedelta(hours=2)
            
            # Guardar la sesión en la base de datos
            if self.db_manager.save_session(session_token, result, expires_at):
                self.current_token = session_token
                self.username = username
                return True, "Inicio de sesión exitoso"
            else:
                return False, "Error al crear sesión"
        else:
            # Inicio de sesión fallido
            return False, result

    def logout(self):
        """
        Cerrar la sesión del usuario actual
        
        Returns:
            Signatura de exito
        """
        if self.current_token:
            self.db_manager.delete_session(self.current_token)
        
        self.current_token = None
        self.username = None
        return True
    
    def is_logged_in(self):
        """
        Comprueba si el usuario actual está autenticado
        
        Returns:
            El valor buleano presente a la autenticación
        """
        # return self.current_user_id is not None
        return self.get_current_user_id() is not None
    
    def get_current_user_id(self):
        """
        Obtener el ID del usuario actual
        
        Returns:
            ID del usuario o None
        """
        if not self.current_token:
            return None
        
        # Validar el formato del token
        user_id = self._validate_token_format(self.current_token)
        if not user_id:
            self.current_token = None  # Eliminar token no válido
            return None
        
        # Validar la sesión en la base de datos
        validated_user_id = self.db_manager.validate_session(self.current_token)
        if not validated_user_id:
            self.current_token = None  # Eliminar token expirado
            return None
        
        return validated_user_id
    
    def get_current_username(self):
        """
        获取当前登录用户的用户名
        
        Returns:
            用户名或None
        """
        return self.username
    
    # def get_user_info(self):
    #     """
    #     获取当前登录用户的信息
        
    #     Returns:
    #         用户信息字典或None
    #     """
    #     if not self.current_user_id:
    #         return None
        
    #     return self.db_manager.get_user_info(self.current_user_id)

    def get_user_info(self):
        """
        获取当前登录用户的信息
        
        Returns:
            用户信息字典或None
        """
        user_id = self.get_current_user_id()
        if not user_id:
            return None
        
        return self.db_manager.get_user_info(user_id)
    
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