#!/usr/bin/env python3
"""
Archivo principal del servidor de Pokemon TCG
Soporta conexiones WebSocket y autenticación de usuarios
"""

import asyncio
import websockets
import json
import logging
import signal
import sys
from pathlib import Path
import os

# Configurar ruta de Python
directorio_actual = Path(__file__).parent
sys.path.insert(0, str(directorio_actual))

# Configurar registros (logs)
directorio_logs = directorio_actual / "logs"
directorio_logs.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(directorio_logs / 'server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PokemonTCGServer:
    def __init__(self):
        self.clients = set()
        self.authenticated_clients = {}

        # Inicializar gestores
        try:
            from game.core.auth.auth_manager import get_auth_manager
            from game.core.database.database_manager import DatabaseManager

            self.auth_manager = get_auth_manager()
            self.db_manager = DatabaseManager()
            logger.info("✅ Gestores inicializados correctamente")
        except ImportError as e:
            logger.error(f"❌ Error de importación: {e}")
            logger.error("Por favor, asegúrese de que todos los módulos necesarios estén en el lugar correcto")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Error al inicializar: {e}")
            sys.exit(1)

        logger.info("🎮 Servidor de Pokemon TCG inicializado")

    async def register_client(self, websocket):
        """Registrar nueva conexión de cliente"""
        client_ip = websocket.remote_address[0]
        client_port = websocket.remote_address[1]
        client_id = f"{client_ip}:{client_port}"

        self.clients.add(websocket)
        logger.info(f"🔗 Cliente conectado: {client_id} (Total: {len(self.clients)})")

        try:
            # Enviar mensaje de bienvenida
            welcome_msg = {
                "type": "welcome",
                "message": "¡Bienvenido al servidor de Pokemon TCG!",
                "server_version": "1.0.0",
                "timestamp": str(asyncio.get_event_loop().time())
            }
            await websocket.send(json.dumps(welcome_msg))

            # Procesar mensajes del cliente
            await self.handle_client(websocket, client_id)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Cliente desconectado normalmente: {client_id}")
        except websockets.exceptions.WebSocketException as e:
            logger.warning(f"⚠️ Excepción de WebSocket {client_id}: {e}")
        except Exception as e:
            logger.error(f"❌ Error al manejar cliente {client_id}: {e}")
        finally:
            # Limpiar cliente
            self.clients.discard(websocket)
            if client_id in self.authenticated_clients:
                del self.authenticated_clients[client_id]
            logger.info(f"🗑️ Cliente eliminado: {client_id} (Restantes: {len(self.clients)})")

    async def handle_client(self, websocket, client_id):
        """Bucle para procesar mensajes del cliente"""
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.debug(f"📨 Mensaje recibido {client_id}: {data.get('action', 'unknown')}")

                response = await self.process_message(data, websocket, client_id)

                if response:
                    await websocket.send(json.dumps(response))
                    logger.debug(f"📤 Respuesta enviada {client_id}: {response.get('success', 'unknown')}")

            except json.JSONDecodeError:
                error_response = {
                    "success": False,
                    "error": "invalid_json",
                    "message": "Formato de mensaje inválido. Envíe JSON válido."
                }
                await websocket.send(json.dumps(error_response))
                logger.warning(f"⚠️ Error al analizar JSON {client_id}")

            except Exception as e:
                error_response = {
                    "success": False,
                    "error": "server_error",
                    "message": "Error interno del servidor"
                }
                await websocket.send(json.dumps(error_response))
                logger.error(f"❌ Error al procesar mensaje {client_id}: {e}")

    async def process_message(self, data, websocket, client_id):
        """Procesar tipo específico de mensaje"""
        action = data.get('action', '')

        if action == 'ping':
            return {
                "success": True,
                "action": "pong",
                "timestamp": str(asyncio.get_event_loop().time())
            }

        elif action == 'register':
            try:
                username = data.get('username', '')
                password = data.get('password', '')
                confirm_password = data.get('confirm_password', '')
                
                # 添加详细日志
                logger.info(f"开始注册用户: {username}")
                
                success, message = self.auth_manager.register(username, password, confirm_password)
                
                logger.info(f"注册结果: {success}, {message}")
                
                return {
                    "success": success,
                    "message": message
                }
            except Exception as e:
                logger.error(f"注册异常: {e}")
                import traceback
                traceback.print_exc()
                return {
                    "success": False,
                    "message": f"注册时发生错误: {str(e)}"
                }

        elif action == 'login':
            return await self.handle_login(data, client_id)

        elif action == 'logout':
            return await self.handle_logout(data, client_id)

        elif action == 'get_user_info':
            return await self.handle_get_user_info(data, client_id)

        elif action == 'get_server_status':
            return await self.handle_get_server_status(data, client_id)

        else:
            return {
                "success": False,
                "error": "unknown_action",
                "message": f"Acción desconocida: {action}",
                "available_actions": ["ping", "register", "login", "logout", "get_user_info", "get_server_status"]
            }

    async def handle_register(self, data, client_id):
        """Procesar registro de usuario"""
        username = data.get('username', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')

        logger.info(f"📝 Solicitud de registro: {username} desde {client_id}")

        if not username or not password:
            return {
                "success": False,
                "error": "missing_fields",
                "message": "El nombre de usuario y la contraseña no pueden estar vacíos."
            }

        if len(username) < 3:
            return {
                "success": False,
                "error": "username_too_short",
                "message": "El nombre de usuario debe tener al menos 3 caracteres."
            }

        if len(password) < 6:
            return {
                "success": False,
                "error": "password_too_short",
                "message": "La contraseña debe tener al menos 6 caracteres."
            }

        if password != confirm_password:
            return {
                "success": False,
                "error": "password_mismatch",
                "message": "Las contraseñas no coinciden."
            }

        try:
            success, message = self.auth_manager.register(username, password, confirm_password)

            if success:
                logger.info(f"✅ Registro exitoso: {username}")
                return {
                    "success": True,
                    "message": message,
                    "username": username
                }
            else:
                logger.warning(f"❌ Registro fallido: {username} - {message}")
                return {
                    "success": False,
                    "error": "registration_failed",
                    "message": message
                }

        except Exception as e:
            logger.error(f"❌ Excepción durante registro: {username} - {e}")
            return {
                "success": False,
                "error": "server_error",
                "message": "Ocurrió un error durante el registro."
            }

    async def handle_login(self, data, client_id):
        """Procesar inicio de sesión"""
        username = data.get('username', '').strip()
        password = data.get('password', '')

        logger.info(f"🔐 Solicitud de inicio de sesión: {username} desde {client_id}")

        if not username or not password:
            return {
                "success": False,
                "error": "missing_credentials",
                "message": "Por favor, proporcione nombre de usuario y contraseña."
            }

        try:
            success, message = self.auth_manager.login(username, password)

            if success:
                user_info = self.auth_manager.get_user_info()
                token = self.auth_manager.current_token

                self.authenticated_clients[client_id] = {
                    "username": username,
                    "token": token,
                    "login_time": asyncio.get_event_loop().time()
                }

                logger.info(f"✅ Inicio de sesión exitoso: {username}")

                return {
                    "success": True,
                    "message": message,
                    "token": token,
                    "user": {
                        "id": user_info.get('id'),
                        "username": user_info.get('username'),
                        "created_at": user_info.get('created_at')
                    }
                }
            else:
                logger.warning(f"❌ Fallo en inicio de sesión: {username} - {message}")
                return {
                    "success": False,
                    "error": "login_failed",
                    "message": message
                }

        except Exception as e:
            logger.error(f"❌ Excepción durante inicio de sesión: {username} - {e}")
            return {
                "success": False,
                "error": "server_error",
                "message": "Ocurrió un error durante el inicio de sesión."
            }

    async def handle_logout(self, data, client_id):
        """Procesar cierre de sesión"""
        if client_id in self.authenticated_clients:
            username = self.authenticated_clients[client_id]["username"]
            del self.authenticated_clients[client_id]
            logger.info(f"👋 Usuario cerró sesión: {username}")

            return {
                "success": True,
                "message": "Sesión cerrada correctamente."
            }
        else:
            return {
                "success": False,
                "error": "not_logged_in",
                "message": "El usuario no ha iniciado sesión."
            }

    async def handle_get_user_info(self, data, client_id):
        """Obtener información del usuario"""
        token = data.get('token', '')

        if not token:
            return {
                "success": False,
                "error": "missing_token",
                "message": "Por favor, proporcione el token de acceso."
            }

        try:
            self.auth_manager.current_token = token

            if self.auth_manager.is_logged_in():
                user_info = self.auth_manager.get_user_info()

                return {
                    "success": True,
                    "user": {
                        "id": user_info.get('id'),
                        "username": user_info.get('username'),
                        "created_at": user_info.get('created_at')
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "invalid_token",
                    "message": "Token inválido o expirado."
                }

        except Exception as e:
            logger.error(f"❌ Excepción al obtener información del usuario: {e}")
            return {
                "success": False,
                "error": "server_error",
                "message": "Ocurrió un error al obtener la información del usuario."
            }

    async def handle_get_server_status(self, data, client_id):
        """Obtener estado del servidor"""
        return {
            "success": True,
            "server_status": {
                "version": "1.0.0",
                "uptime": asyncio.get_event_loop().time(),
                "connected_clients": len(self.clients),
                "authenticated_clients": len(self.authenticated_clients),
                "status": "running"
            }
        }

    def setup_signal_handlers(self):
        """Configurar manejadores de señales"""
        def signal_handler(signum, frame):
            logger.info(f"🛑 Señal recibida {signum}, cerrando servidor...")
            self.shutdown()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def shutdown(self):
        """Cerrar servidor"""
        logger.info("🔄 Cerrando servidor...")

        if hasattr(self, 'db_manager'):
            self.db_manager.close()

        logger.info("👋 Servidor cerrado")
        sys.exit(0)

async def main():
    """Función principal"""
    print("🎮 Iniciando servidor de Pokemon TCG...")

    base_dir = Path(__file__).parent
    (base_dir / "logs").mkdir(exist_ok=True)
    (base_dir / "data").mkdir(exist_ok=True)

    try:
        server = PokemonTCGServer()
        server.setup_signal_handlers()

        host = "0.0.0.0"
        port = 8765

        logger.info(f"🚀 Iniciando WebSocket en {host}:{port}")

        async with websockets.serve(server.register_client, host, port):
            logger.info("✅ Servidor Pokemon TCG en ejecución")
            logger.info(f"📡 WebSocket disponible en: ws://{host}:{port}")
            logger.info("🎯 Esperando conexiones de clientes...")

            await asyncio.Future()  # Ejecutar indefinidamente

    except Exception as e:
        logger.error(f"❌ Error al iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error del servidor: {e}")
        sys.exit(1)
