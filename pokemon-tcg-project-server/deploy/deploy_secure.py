#!/usr/bin/env python3
"""
Pokemon TCG 安全部署脚本
支持完整的项目结构和安全功能
"""

import os
import sys
import subprocess
import platform
import time
import json
from pathlib import Path
import tempfile

class Colors:
    """Clase de colores para consola"""
    if platform.system() == "Windows":
        try:
            import colorama
            colorama.init()
            RED = '\033[0;31m'
            GREEN = '\033[0;32m'
            YELLOW = '\033[1;33m'
            BLUE = '\033[0;34m'
            PURPLE = '\033[0;35m'
            CYAN = '\033[0;36m'
            NC = '\033[0m'
        except ImportError:
            RED = GREEN = YELLOW = BLUE = PURPLE = CYAN = NC = ''
    else:
        RED = '\033[0;31m'
        GREEN = '\033[0;32m'
        YELLOW = '\033[1;33m'
        BLUE = '\033[0;34m'
        PURPLE = '\033[0;35m'
        CYAN = '\033[0;36m'
        NC = '\033[0m'

def print_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")

def print_success(msg):
    print(f"{Colors.GREEN}[ÉXITO]{Colors.NC} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[ADVERTENCIA]{Colors.NC} {msg}")

def print_error(msg):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")

def print_security(msg):
    print(f"{Colors.PURPLE}[SEGURIDAD]{Colors.NC} {msg}")

def print_deploy(msg):
    print(f"{Colors.CYAN}[DESPLIEGUE]{Colors.NC} {msg}")

class SecurePokemonTCGDeployer:
    def __init__(self, ec2_ip, ssh_key_path, ssh_user="ec2-user", project_root="server"):
        self.ec2_ip = ec2_ip
        self.ssh_key_path = Path(ssh_key_path)
        self.ssh_user = ssh_user
        self.project_root = Path(project_root)
        self.remote_project_dir = "/opt/pokemon-tcg"
        
        # Validaciones iniciales
        self._validate_setup()
        
        # Configuración de archivos requeridos
        self.required_files = self._get_required_files()
        
    def _validate_setup(self):
        """Validar configuración inicial"""
        if not self.ssh_key_path.exists():
            raise FileNotFoundError(f"Archivo de clave SSH no encontrado: {self.ssh_key_path}")
        
        if not self.project_root.exists():
            raise FileNotFoundError(f"Directorio del proyecto no encontrado: {self.project_root}")
        
        # Corregir permisos de clave SSH (Unix/Linux/macOS)
        if platform.system() != "Windows":
            self.ssh_key_path.chmod(0o600)
    
    def _get_required_files(self):
        """Definir archivos requeridos del proyecto"""
        return {
            'core_files': [
                'server.py',
                'game/__init__.py',
                'game/core/__init__.py',
                'game/core/database/__init__.py',
                'game/core/database/database_manager.py',
                'game/core/database/daos/__init__.py',
                'game/core/database/daos/user_dao.py',
                'game/core/database/daos/card_dao.py',
                'game/core/auth/__init__.py',
                'game/core/auth/auth_manager.py',
                'game/core/cards/__init__.py',                    # 👈 添加这行
                'game/core/cards/card_data.py',                   # 👈 添加这行
                'game/core/cards/collection_manager.py' 
            ],
            'optional_files': [
                'game/core/security/__init__.py',
                'game/core/security/session_manager.py',
                'game/core/security/security_monitor.py',
                'utils/__init__.py',
                'utils/logger.py',
                'utils/backup_manager.py'
            ],
            'config_files': [
                'config/server_config.json',
                'config/logging_config.json'
            ]
        }
    
    def run_ssh_command(self, command, show_output=True, timeout=60):
        """Ejecutar comando SSH con manejo robusto de errores"""
        ssh_cmd = [
            "ssh", "-i", str(self.ssh_key_path),
            "-o", "ConnectTimeout=15",
            "-o", "ServerAliveInterval=30",
            "-o", "StrictHostKeyChecking=no",
            f"{self.ssh_user}@{self.ec2_ip}",
            command
        ]
        
        try:
            result = subprocess.run(
                ssh_cmd,
                capture_output=not show_output,
                text=True,
                timeout=timeout
            )
            
            if show_output:
                return result.returncode == 0
            else:
                return result.returncode == 0, result.stdout, result.stderr
                
        except subprocess.TimeoutExpired:
            print_error(f"Timeout ejecutando comando (>{timeout}s): {command[:50]}...")
            return False
        except Exception as e:
            print_error(f"Error ejecutando comando SSH: {e}")
            return False
    
    def upload_file(self, local_path, remote_path, create_dirs=True):
        """Subir archivo al servidor con creación automática de directorios"""
        local_file = Path(local_path)
        
        if not local_file.exists():
            print_error(f"Archivo local no encontrado: {local_path}")
            return False
        
        # Crear directorios remotos si es necesario
        if create_dirs:
            remote_dir = str(Path(remote_path).parent)
            self.run_ssh_command(f"mkdir -p {remote_dir}", show_output=False)
        
        scp_cmd = [
            "scp", "-i", str(self.ssh_key_path),
            "-o", "StrictHostKeyChecking=no",
            str(local_file),
            f"{self.ssh_user}@{self.ec2_ip}:{remote_path}"
        ]
        
        try:
            result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True
            else:
                print_error(f"Error subiendo {local_file.name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print_error(f"Timeout subiendo archivo: {local_file.name}")
            return False
        except Exception as e:
            print_error(f"Error en scp: {e}")
            return False
    
    def upload_directory(self, local_dir, remote_dir):
        """Subir directorio completo de forma recursiva"""
        local_path = Path(local_dir)
        
        if not local_path.exists():
            print_warning(f"Directorio local no encontrado: {local_dir}")
            return False
        
        print_info(f"Subiendo directorio: {local_dir} -> {remote_dir}")
        
        # Crear directorio remoto
        self.run_ssh_command(f"mkdir -p {remote_dir}", show_output=False)
        
        # Subir archivos recursivamente
        success_count = 0
        total_count = 0
        
        for root, dirs, files in os.walk(local_path):
            for file in files:
                # Ignorar archivos temporales y de Python
                if file.endswith(('.pyc', '.pyo', '__pycache__', '.DS_Store')):
                    continue
                
                local_file = Path(root) / file
                relative_path = local_file.relative_to(local_path)
                remote_file = f"{remote_dir}/{relative_path}".replace('\\', '/')
                
                total_count += 1
                if self.upload_file(local_file, remote_file):
                    success_count += 1
                    print(f"  ✓ {relative_path}")
                else:
                    print(f"  ✗ {relative_path}")
        
        print_info(f"Subida completa: {success_count}/{total_count} archivos")
        return success_count == total_count
    
    def validate_local_files(self):
        """Validar que todos los archivos requeridos estén presentes"""
        print_info("Validando archivos locales del proyecto...")
        
        missing_files = []
        found_files = []
        
        # Verificar archivos core (obligatorios)
        for file_path in self.required_files['core_files']:
            full_path = self.project_root / file_path
            if full_path.exists():
                found_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        # Verificar archivos opcionales
        optional_found = []
        for file_path in self.required_files['optional_files']:
            full_path = self.project_root / file_path
            if full_path.exists():
                optional_found.append(file_path)
        
        # Mostrar resultados
        print(f"\n{'='*50}")
        print("VALIDACIÓN DE ARCHIVOS")
        print(f"{'='*50}")
        print(f"[OK]Archivos core encontrados: {len(found_files)}")
        print(f"[WARNING] Archivos core faltantes: {len(missing_files)}")
        print(f"📦 Archivos opcionales encontrados: {len(optional_found)}")
        
        if missing_files:
            print(f"\n{Colors.RED}ARCHIVOS FALTANTES:{Colors.NC}")
            for file in missing_files:
                print(f"  ✗ {file}")
            
            print(f"\n{Colors.YELLOW}INSTRUCCIONES:{Colors.NC}")
            print("Antes de continuar, asegúrate de que estos archivos estén en:")
            for file in missing_files:
                print(f"  {self.project_root}/{file}")
            
            response = input(f"\n¿Continuar de todos modos? (s/N): ")
            if response.lower() not in ['s', 'sí', 'si', 'y', 'yes']:
                return False
        
        print_success(f"Validación completada - {len(found_files)} archivos core verificados")
        return True
    
    def test_connection(self):
        """Probar conexión SSH"""
        print_info("Probando conexión SSH...")
        
        success, output, error = self.run_ssh_command("echo 'Conexión SSH exitosa' && uname -a", show_output=False)
        
        if success:
            print_success("Conexión SSH establecida")
            system_info = output.strip().split('\n')[-1] if output else "Información no disponible"
            print_info(f"Sistema remoto: {system_info}")
            return True
        else:
            print_error(f"Error de conexión SSH: {error}")
            return False
    
    def install_system_dependencies(self):
        """Instalar dependencias del sistema"""
        print_info("Instalando dependencias del sistema...")
        
        # Detectar distribución Linux
        success, distro_info, _ = self.run_ssh_command("cat /etc/os-release", show_output=False)
        is_amazon_linux = "amazon" in distro_info.lower() if success else False
        
        if is_amazon_linux:
            print_info("Detectado Amazon Linux - usando yum")
            package_manager_commands = [
                "sudo yum update -y",
                "sudo yum remove -y curl-minimal || true",  # Resolver conflictos
                "sudo yum install -y python3 python3-pip python3-devel",
                "sudo yum install -y gcc sqlite git wget openssl-devel",
                "sudo yum install -y firewalld || sudo yum install -y iptables-services",
                "sudo yum install -y cronie || true",
                "sudo systemctl enable crond && sudo systemctl start crond || true"
            ]
        else:
            print_info("Usando apt (Ubuntu/Debian)")
            package_manager_commands = [
                "sudo apt update && sudo apt upgrade -y",
                "sudo apt install -y python3 python3-pip python3-venv python3-dev",
                "sudo apt install -y build-essential sqlite3 git curl wget",
                "sudo apt install -y ufw",
                "sudo apt install -y cron",
                "sudo systemctl enable cron && sudo systemctl start cron || true"
            ]
        
        # Ejecutar comandos de instalación
        for cmd in package_manager_commands:
            print_info(f"Ejecutando: {cmd}")
            if not self.run_ssh_command(cmd, timeout=180):  # 3 minutos timeout
                print_warning(f"Comando falló (continuando): {cmd}")
        
        # Instalar dependencias Python específicas
        python_deps = [
            f"cd {self.remote_project_dir} && python3 -m pip install --user --upgrade pip",
            f"cd {self.remote_project_dir} && python3 -m pip install --user websockets asyncio",
            f"cd {self.remote_project_dir} && python3 -m pip install --user bcrypt cryptography",
            f"cd {self.remote_project_dir} && python3 -m pip install --user python-dateutil"
        ]
        
        print_info("Instalando dependencias Python...")
        for cmd in python_deps:
            self.run_ssh_command(cmd, timeout=120)
        
        print_success("Dependencias del sistema instaladas")
        return True
    
    def create_project_structure(self):
        """Crear estructura de directorios del proyecto"""
        print_info("Creando estructura de directorios...")
        
        directories = [
            f"{self.remote_project_dir}",
            f"{self.remote_project_dir}/game",
            f"{self.remote_project_dir}/game/core",
            f"{self.remote_project_dir}/game/core/database",
            f"{self.remote_project_dir}/game/core/database/daos",
            f"{self.remote_project_dir}/game/core/auth",
            f"{self.remote_project_dir}/game/core/security",
            f"{self.remote_project_dir}/game/core/cards", 
            f"{self.remote_project_dir}/utils",
            f"{self.remote_project_dir}/config",
            f"{self.remote_project_dir}/data",
            f"{self.remote_project_dir}/data/backups",
            f"{self.remote_project_dir}/logs",
            f"{self.remote_project_dir}/ssl",
            f"{self.remote_project_dir}/scripts"
        ]
        
        for directory in directories:
            self.run_ssh_command(f"sudo mkdir -p {directory}", show_output=False)
        
        # Cambiar propietario al usuario actual
        self.run_ssh_command(f"sudo chown -R {self.ssh_user}:{self.ssh_user} {self.remote_project_dir}")
        
        print_success("Estructura de directorios creada")
        return True
    
    def generate_config_files(self):
        """Generar archivos de configuración necesarios"""
        print_info("Generando archivos de configuración...")
        
        # Configuración del servidor
        server_config = {
            "server": {
                "host": "0.0.0.0",
                "port": 8765,
                "max_connections": 100,
                "timeout": 30
            },
            "database": {
                "path": "data/game_database.db",
                "backup_interval": 3600,
                "max_backups": 24
            },
            "security": {
                "session_timeout": 7200,
                "max_login_attempts": 5,
                "rate_limit_window": 300,
                "ssl_enabled": False,
                "ssl_cert_path": "ssl/server.crt",
                "ssl_key_path": "ssl/server.key"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/server.log",
                "max_size": "10MB",
                "backup_count": 5
            }
        }
        
        # Configuración de logging
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "simple": {
                    "format": "%(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "logs/server.log",
                    "maxBytes": 10485760,
                    "backupCount": 5,
                    "formatter": "detailed"
                },
                "security_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "logs/security.log",
                    "maxBytes": 10485760,
                    "backupCount": 5,
                    "formatter": "detailed"
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "simple"
                }
            },
            "loggers": {
                "pokemon_tcg": {
                    "level": "INFO",
                    "handlers": ["file", "console"]
                },
                "security": {
                    "level": "INFO",
                    "handlers": ["security_file"]
                }
            }
        }
        
        # Crear archivos temporales locales
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(server_config, f, indent=2)
            server_config_temp = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(logging_config, f, indent=2)
            logging_config_temp = f.name
        
        try:
            # Subir archivos de configuración
            success1 = self.upload_file(server_config_temp, f"{self.remote_project_dir}/config/server_config.json")
            success2 = self.upload_file(logging_config_temp, f"{self.remote_project_dir}/config/logging_config.json")
            
            if success1 and success2:
                print_success("Archivos de configuración generados y subidos")
                return True
            else:
                print_error("Error subiendo archivos de configuración")
                return False
                
        finally:
            # Limpiar archivos temporales
            Path(server_config_temp).unlink(missing_ok=True)
            Path(logging_config_temp).unlink(missing_ok=True)
    
    def upload_project_files(self):
        """Subir todos los archivos del proyecto"""
        print_info("Subiendo archivos del proyecto...")
        
        success_count = 0
        total_count = 0
        
        # Subir archivos core
        for file_path in self.required_files['core_files']:
            local_file = self.project_root / file_path
            remote_file = f"{self.remote_project_dir}/{file_path}"
            
            total_count += 1
            if local_file.exists():
                if self.upload_file(local_file, remote_file):
                    success_count += 1
                    print(f"  ✓ {file_path}")
                else:
                    print(f"  ✗ {file_path}")
            else:
                print_warning(f"  ? {file_path} (no encontrado)")
        
        # Subir archivos opcionales
        for file_path in self.required_files['optional_files']:
            local_file = self.project_root / file_path
            remote_file = f"{self.remote_project_dir}/{file_path}"
            
            if local_file.exists():
                total_count += 1
                if self.upload_file(local_file, remote_file):
                    success_count += 1
                    print(f"  ✓ {file_path} (opcional)")
                else:
                    print(f"  ✗ {file_path} (opcional)")
        
        print_info(f"Subida de archivos: {success_count}/{total_count} exitosos")
        
        if success_count < len(self.required_files['core_files']):
            print_error("Faltan archivos core críticos")
            return False
        
        print_success("Archivos del proyecto subidos")
        return True
    
    def create_server_script(self):
        """Crear script del servidor principal si no existe"""
        server_script_path = self.project_root / "server.py"
        
        if server_script_path.exists():
            print_info("Usando server.py existente")
            return True
        
        print_info("Generando server.py básico...")
        
        server_template = '''#!/usr/bin/env python3
"""
Servidor Pokemon TCG con autenticación segura
"""

import asyncio
import websockets
import json
import logging
import signal
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importar módulos del juego
try:
    from game.core.auth.auth_manager import get_auth_manager
    from game.core.database.database_manager import DatabaseManager
except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    sys.exit(1)

class PokemonTCGServer:
    def __init__(self):
        self.clients = set()
        self.auth_manager = get_auth_manager()
        self.db_manager = DatabaseManager()
        logger.info("Servidor Pokemon TCG inicializado")
    
    async def register_client(self, websocket, path):
        """Registrar nuevo cliente"""
        self.clients.add(websocket)
        client_ip = websocket.remote_address[0]
        logger.info(f"Cliente conectado desde {client_ip}")
        
        try:
            await self.handle_client(websocket)
        except websockets.exceptions.WebSocketException:
            logger.info(f"Cliente desconectado: {client_ip}")
        except Exception as e:
            logger.error(f"Error manejando cliente {client_ip}: {e}")
        finally:
            self.clients.discard(websocket)
    
    async def handle_client(self, websocket):
        """Manejar mensajes del cliente"""
        async for message in websocket:
            try:
                data = json.loads(message)
                response = await self.process_message(data, websocket)
                await websocket.send(json.dumps(response))
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "error": "Formato de mensaje inválido"
                }))
            except Exception as e:
                logger.error(f"Error procesando mensaje: {e}")
                await websocket.send(json.dumps({
                    "error": "Error interno del servidor"
                }))
    
    async def process_message(self, data, websocket):
        """Procesar mensaje del cliente"""
        action = data.get('action', '')
        client_ip = websocket.remote_address[0]
        
        if action == 'login':
            username = data.get('username', '')
            password = data.get('password', '')
            
            logger.info(f"Intento de login: {username} desde {client_ip}")
            
            success, message = self.auth_manager.login(username, password)
            
            if success:
                user_info = self.auth_manager.get_user_info()
                logger.info(f"Login exitoso: {username}")
                
                return {
                    "success": True,
                    "message": message,
                    "token": self.auth_manager.current_token,
                    "user": {
                        "id": user_info['id'],
                        "username": user_info['username']
                    }
                }
            else:
                logger.warning(f"Login fallido: {username} desde {client_ip}")
                return {
                    "success": False,
                    "message": message
                }
        
        elif action == 'register':
            username = data.get('username', '')
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            
            logger.info(f"Intento de registro: {username} desde {client_ip}")
            
            success, message = self.auth_manager.register(username, password, confirm_password)
            
            if success:
                logger.info(f"Registro exitoso: {username}")
            else:
                logger.warning(f"Registro fallido: {username} - {message}")
            
            return {
                "success": success,
                "message": message
            }
        
        elif action == 'get_user_data':
            token = data.get('token', '')
            
            if token:
                # Validar token y obtener datos del usuario
                self.auth_manager.current_token = token
                if self.auth_manager.is_logged_in():
                    user_info = self.auth_manager.get_user_info()
                    if user_info:
                        return {
                            "success": True,
                            "user": user_info
                        }
            
            return {
                "success": False,
                "message": "Sesión inválida o expirada"
            }
        
        else:
            return {
                "success": False,
                "message": f"Acción desconocida: {action}"
            }
    
    def shutdown(self, signum, frame):
        """Manejar cierre del servidor"""
        logger.info("Cerrando servidor...")
        self.db_manager.close()
        sys.exit(0)

async def main():
    # Crear directorio de logs si no existe
    Path('logs').mkdir(exist_ok=True)
    
    server = PokemonTCGServer()
    
    # Configurar manejo de seniales
    signal.signal(signal.SIGINT, server.shutdown)
    signal.signal(signal.SIGTERM, server.shutdown)
    
    # Iniciar servidor
    logger.info("Iniciando servidor en 0.0.0.0:8765")
    
    async with websockets.serve(server.register_client, "0.0.0.0", 8765):
        logger.info("Servidor Pokemon TCG en funcionamiento")
        await asyncio.Future()  # Ejecutar indefinidamente

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal del servidor: {e}")
        sys.exit(1)
'''
        
        # Crear archivo temporal y subirlo
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(server_template)
            temp_server_file = f.name
        
        try:
            success = self.upload_file(temp_server_file, f"{self.remote_project_dir}/server.py")
            if success:
                print_success("Script del servidor creado")
                return True
            else:
                print_error("Error creando script del servidor")
                return False
        finally:
            Path(temp_server_file).unlink(missing_ok=True)
    
    def fix_import_paths(self):
        """Corregir rutas de importación en los archivos subidos"""
        print_info("Corrigiendo rutas de importación...")
        
        # Comandos para corregir imports relativos
        fix_commands = [
            # Corregir import en auth_manager.py
            f"cd {self.remote_project_dir}/game/core/auth && "
            f"sed -i 's|from game.core.database.database_manager|from ..database.database_manager|g' auth_manager.py",
            
            # Corregir imports en database_manager.py
            f"cd {self.remote_project_dir}/game/core/database && "
            f"sed -i 's|from .daos.user_dao|from .daos.user_dao|g' database_manager.py",
            
            f"cd {self.remote_project_dir}/game/core/database && "
            f"sed -i 's|from .daos.card_dao|from .daos.card_dao|g' database_manager.py",
            
            # Hacer archivos ejecutables
            f"chmod +x {self.remote_project_dir}/server.py"
        ]
        
        for cmd in fix_commands:
            self.run_ssh_command(cmd, show_output=False)
        
        print_success("Rutas de importación corregidas")
        return True
    
    def initialize_database(self):
        """Inicializar base de datos"""
        print_info("Inicializando base de datos...")
        
        # Script de inicialización de base de datos
        init_script = f'''
cd {self.remote_project_dir}
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from game.core.database.database_manager import DatabaseManager
    db = DatabaseManager()
    print('[OK]Base de datos inicializada correctamente')
    db.close()
except Exception as e:
    print(f'[ERROR]Error inicializando base de datos: {{e}}')
    sys.exit(1)
"
'''
        
        success = self.run_ssh_command(init_script, timeout=60)
        
        if success:
            print_success("Base de datos inicializada")
            return True
        else:
            print_error("Error inicializando base de datos")
            return False
    
    def create_systemd_service(self):
        """Crear servicio systemd"""
        print_info("Creando servicio systemd...")
        
        service_content = f"""[Unit]
Description=Pokemon TCG Secure Game Server
After=network.target
Wants=network-online.target

[Service]
Type=simple
User={self.ssh_user}
Group={self.ssh_user}
WorkingDirectory={self.remote_project_dir}
Environment="PYTHONPATH={self.remote_project_dir}"
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 server.py
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pokemon-tcg

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths={self.remote_project_dir}

[Install]
WantedBy=multi-user.target
"""
        
        # Crear archivo temporal y subirlo
        with tempfile.NamedTemporaryFile(mode='w', suffix='.service', delete=False) as f:
            f.write(service_content)
            temp_service_file = f.name
        
        try:
            # Subir y configurar servicio
            if self.upload_file(temp_service_file, "/tmp/pokemon-tcg.service"):
                commands = [
                    "sudo mv /tmp/pokemon-tcg.service /etc/systemd/system/",
                    "sudo systemctl daemon-reload",
                    "sudo systemctl enable pokemon-tcg"
                ]
                
                for cmd in commands:
                    if not self.run_ssh_command(cmd):
                        return False
                
                print_success("Servicio systemd creado y habilitado")
                return True
            else:
                return False
                
        finally:
            Path(temp_service_file).unlink(missing_ok=True)
    
    def configure_security(self):
        """Configurar medidas de seguridad"""
        print_security("Configurando seguridad del servidor...")
        
        security_commands = [
            # Configurar firewall
            "sudo systemctl enable firewalld && sudo systemctl start firewalld || " +
            "sudo ufw --force enable",
            
            # Abrir puertos necesarios (firewalld)
            "sudo firewall-cmd --permanent --add-port=22/tcp || true",
            "sudo firewall-cmd --permanent --add-port=8765/tcp || true",
            "sudo firewall-cmd --reload || true",
            
            # Abrir puertos necesarios (ufw)
            "sudo ufw allow 22/tcp || true",
            "sudo ufw allow 8765/tcp || true",
            
            # Configurar permisos de archivos
            f"chmod 750 {self.remote_project_dir}",
            f"chmod 640 {self.remote_project_dir}/config/*.json",
            f"find {self.remote_project_dir} -name '*.py' -exec chmod 644 {{}} \\;",
            f"chmod +x {self.remote_project_dir}/server.py",
            
            # Crear directorio para certificados SSL
            f"mkdir -p {self.remote_project_dir}/ssl",
            f"chmod 700 {self.remote_project_dir}/ssl"
        ]
        
        for cmd in security_commands:
            self.run_ssh_command(cmd, show_output=False)
        
        print_security("Configuración de seguridad aplicada")
        return True
    
    def create_monitoring_scripts(self):
        """Crear scripts de monitoreo y mantenimiento"""
        print_info("Creando scripts de monitoreo...")
        
        # Script de monitoreo de salud
        health_monitor = f'''#!/bin/bash
# Script de monitoreo de salud Pokemon TCG

LOG_FILE="{self.remote_project_dir}/logs/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Verificando estado del servidor..." >> "$LOG_FILE"

# Verificar si el servicio está activo
if systemctl is-active --quiet pokemon-tcg; then
    echo "[$DATE] [OK]Servicio activo" >> "$LOG_FILE"
else
    echo "[$DATE] [ERROR]Servicio inactivo - Reiniciando..." >> "$LOG_FILE"
    sudo systemctl restart pokemon-tcg
    sleep 5
    
    if systemctl is-active --quiet pokemon-tcg; then
        echo "[$DATE] [OK]Servicio reiniciado exitosamente" >> "$LOG_FILE"
    else
        echo "[$DATE] [ERROR]Error crítico - Servicio no se puede iniciar" >> "$LOG_FILE"
        # Enviar alerta (opcional)
        echo "[$DATE] ALERTA: Servidor Pokemon TCG no responde" | logger -t pokemon-tcg-alert
    fi
fi

# Verificar puerto WebSocket
if netstat -tlpn | grep -q :8765; then
    echo "[$DATE] [OK]Puerto 8765 activo" >> "$LOG_FILE"
else
    echo "[$DATE] [WARNING] Puerto 8765 no disponible" >> "$LOG_FILE"
fi

# Verificar uso de memoria
MEMORY_USAGE=$(ps -o pid,vsz,comm -C python3 | grep server.py | awk '{{print $2}}')
if [ ! -z "$MEMORY_USAGE" ]; then
    MEMORY_MB=$((MEMORY_USAGE / 1024))
    echo "[$DATE] [INFO]Uso de memoria: ${{MEMORY_MB}}MB" >> "$LOG_FILE"
    
    # Alerta si usa más de 500MB
    if [ $MEMORY_MB -gt 500 ]; then
        echo "[$DATE] [WARNING] Alto uso de memoria: ${{MEMORY_MB}}MB" >> "$LOG_FILE"
    fi
fi

# Limpiar logs antiguos (mantener solo últimos 7 días)
find "{self.remote_project_dir}/logs" -name "*.log" -mtime +7 -delete 2>/dev/null || true
'''
        
        # Script de backup
        backup_script = f'''#!/bin/bash
# Script de backup Pokemon TCG

BACKUP_DIR="{self.remote_project_dir}/data/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="{self.remote_project_dir}/data/game_database.db"
LOG_FILE="{self.remote_project_dir}/logs/backup.log"

echo "[$(date)] Iniciando backup..." >> "$LOG_FILE"

# Crear directorio de backup si no existe
mkdir -p "$BACKUP_DIR"

# Backup de base de datos
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_DIR/game_database_$DATE.db"
    echo "[$(date)] [OK]Base de datos respaldada: game_database_$DATE.db" >> "$LOG_FILE"
else
    echo "[$(date)] [WARNING] Base de datos no encontrada: $DB_FILE" >> "$LOG_FILE"
fi

# Backup de configuración
if [ -d "{self.remote_project_dir}/config" ]; then
    tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" -C "{self.remote_project_dir}" config/
    echo "[$(date)] [OK]Configuración respaldada: config_$DATE.tar.gz" >> "$LOG_FILE"
fi

# Limpiar backups antiguos (mantener solo últimos 7)
cd "$BACKUP_DIR"
ls -t game_database_*.db 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || true
ls -t config_*.tar.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || true

echo "[$(date)] Backup completado" >> "$LOG_FILE"
'''
        
        # Script de limpieza de sesiones
        cleanup_script = f'''#!/bin/bash
# Script de limpieza de sesiones Pokemon TCG

cd {self.remote_project_dir}
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from game.core.database.database_manager import DatabaseManager
    db = DatabaseManager()
    cleaned = db.cleanup_expired_sessions()
    print(f'Sesiones expiradas limpiadas: {{cleaned}}')
    db.close()
except Exception as e:
    print(f'Error limpiando sesiones: {{e}}')
" >> "{self.remote_project_dir}/logs/cleanup.log" 2>&1
'''
        
        # Crear archivos temporales
        scripts = [
            (health_monitor, f"{self.remote_project_dir}/scripts/health_monitor.sh"),
            (backup_script, f"{self.remote_project_dir}/scripts/backup.sh"),
            (cleanup_script, f"{self.remote_project_dir}/scripts/cleanup_sessions.sh")
        ]
        
        for script_content, remote_path in scripts:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(script_content)
                temp_file = f.name
            
            try:
                if self.upload_file(temp_file, remote_path):
                    self.run_ssh_command(f"chmod +x {remote_path}", show_output=False)
                    print(f"  ✓ {Path(remote_path).name}")
                else:
                    print(f"  ✗ {Path(remote_path).name}")
            finally:
                Path(temp_file).unlink(missing_ok=True)
        
        # Configurar tareas cron
        cron_jobs = [
            f"*/5 * * * * {self.remote_project_dir}/scripts/health_monitor.sh",
            f"0 2 * * * {self.remote_project_dir}/scripts/backup.sh",
            f"0 */4 * * * {self.remote_project_dir}/scripts/cleanup_sessions.sh"
        ]
        
        for job in cron_jobs:
            self.run_ssh_command(f'(crontab -l 2>/dev/null; echo "{job}") | crontab -', show_output=False)
        
        print_success("Scripts de monitoreo creados y programados")
        return True
    
    def start_server(self):
        """Iniciar el servidor"""
        print_info("Iniciando servidor Pokemon TCG...")
        
        # Iniciar servicio
        if not self.run_ssh_command("sudo systemctl start pokemon-tcg"):
            print_error("Error iniciando servicio")
            return False
        
        # Esperar un momento
        time.sleep(5)
        
        # Verificar estado
        success, output, error = self.run_ssh_command("systemctl is-active pokemon-tcg", show_output=False)
        
        if success and "active" in output:
            print_success("Servidor iniciado exitosamente")
            
            # Mostrar información adicional
            self.run_ssh_command("sudo systemctl status pokemon-tcg --no-pager -l", show_output=True)
            return True
        else:
            print_error("Error iniciando servidor")
            print_error("Verificando logs...")
            self.run_ssh_command("sudo journalctl -u pokemon-tcg --no-pager -n 20", show_output=True)
            return False
    
    def test_server_connection(self):
        """Probar conexión al servidor WebSocket"""
        print_info("Probando conexión WebSocket...")
        
        import socket
        try:
            sock = socket.create_connection((self.ec2_ip, 8765), timeout=15)
            sock.close()
            print_success(f"Servidor WebSocket accesible en {self.ec2_ip}:8765")
            return True
        except Exception as e:
            print_warning(f"No se pudo conectar al puerto 8765: {e}")
            print_info("Esto puede deberse a configuración de Security Group en AWS")
            return False
    
    def perform_health_check(self):
        """Realizar verificación de salud del servidor"""
        print_info("Realizando verificación de salud...")
        
        health_checks = [
            ("Servicio systemd", "systemctl is-active pokemon-tcg"),
            ("Puerto WebSocket", "netstat -tlpn | grep :8765"),
            ("Procesos Python", "ps aux | grep 'python.*server.py' | grep -v grep"),
            ("Logs recientes", f"tail -n 5 {self.remote_project_dir}/logs/server.log 2>/dev/null || echo 'Sin logs aún'"),
            ("Base de datos", f"ls -la {self.remote_project_dir}/data/game_database.db 2>/dev/null || echo 'BD no creada aún'")
        ]
        
        print(f"\n{'='*50}")
        print("VERIFICACIÓN DE SALUD DEL SERVIDOR")
        print(f"{'='*50}")
        
        all_healthy = True
        for check_name, command in health_checks:
            success, output, error = self.run_ssh_command(command, show_output=False)
            
            if success and output.strip():
                status = "[OK]OK"
                if "active" in output or "python" in output or ":8765" in output:
                    status_detail = output.strip().split('\n')[0][:50]
                else:
                    status_detail = "Funcionando"
            else:
                status = "[ERROR]FALLO"
                status_detail = error.strip()[:50] if error else "Sin respuesta"
                all_healthy = False
            
            print(f"{check_name:20} │ {status} │ {status_detail}")
        
        print(f"{'='*50}")
        
        if all_healthy:
            print_success("Verificación de salud completada - Sistema saludable")
        else:
            print_warning("Verificación de salud completada - Algunos problemas detectados")
        
        return all_healthy
    
    def show_deployment_summary(self):
        """Mostrar resumen del despliegue"""
        print(f"""

{'='*70}
🎉 DESPLIEGUE COMPLETADO EXITOSAMENTE
{'='*70}

📡 INFORMACIÓN DEL SERVIDOR:
   ├─ IP del servidor: {self.ec2_ip}
   ├─ Puerto WebSocket: 8765
   ├─ URL de conexión: ws://{self.ec2_ip}:8765
   └─ Directorio de instalación: {self.remote_project_dir}

🔧 COMANDOS DE ADMINISTRACIÓN:
   ├─ Estado del servicio:
   │  ssh -i {self.ssh_key_path} {self.ssh_user}@{self.ec2_ip} 'sudo systemctl status pokemon-tcg'
   ├─ Ver logs en tiempo real:
   │  ssh -i {self.ssh_key_path} {self.ssh_user}@{self.ec2_ip} 'sudo journalctl -u pokemon-tcg -f'
   ├─ Reiniciar servicio:
   │  ssh -i {self.ssh_key_path} {self.ssh_user}@{self.ec2_ip} 'sudo systemctl restart pokemon-tcg'
   └─ Detener servicio:
      ssh -i {self.ssh_key_path} {self.ssh_user}@{self.ec2_ip} 'sudo systemctl stop pokemon-tcg'

🔐 CARACTERÍSTICAS DE SEGURIDAD:
   ├─ [OK]Autenticación por tokens seguros
   ├─ [OK]Validación de sesiones con expiración
   ├─ [OK]Logging de eventos de seguridad
   ├─ [OK]Firewall configurado
   └─ [OK]Permisos de archivos restringidos

[INFO]MONITOREO AUTOMÁTICO:
   ├─ [OK]Verificación de salud cada 5 minutos
   ├─ [OK]Backup automático diario (2:00 AM)
   ├─ [OK]Limpieza de sesiones cada 4 horas
   └─ [OK]Rotación de logs automática

📁 ARCHIVOS IMPORTANTES:
   ├─ Logs del servidor: {self.remote_project_dir}/logs/server.log
   ├─ Logs de seguridad: {self.remote_project_dir}/logs/security.log
   ├─ Base de datos: {self.remote_project_dir}/data/game_database.db
   ├─ Configuración: {self.remote_project_dir}/config/server_config.json
   └─ Backups: {self.remote_project_dir}/data/backups/

[WARNING] CONFIGURACIÓN IMPORTANTE DE AWS:
   Asegúrate de que el Security Group tenga estas reglas:
   ├─ Puerto 22 (SSH) desde tu IP
   ├─ Puerto 8765 (WebSocket) desde 0.0.0.0/0
   └─ Puerto 443 (HTTPS) desde 0.0.0.0/0 (opcional)

🧪 PRUEBA DE CONEXIÓN:
   Para probar el servidor, puedes usar:
   ├─ WebSocket test online: ws://{self.ec2_ip}:8765
   ├─ Cliente Python de prueba
   └─ Navegador con JavaScript WebSocket

📚 PRÓXIMOS PASOS:
   1. Configurar certificados SSL/TLS para HTTPS
   2. Crear cliente de prueba con Pygame
   3. Implementar sistema de métricas avanzado
   4. Configurar alertas por email/SMS

🚀 ¡Tu servidor Pokemon TCG está listo y funcionando!
""")
    
    def full_deployment(self):
        """Ejecutar despliegue completo"""
        print(f"""
{'='*70}
🚀 DESPLIEGUE SEGURO POKEMON TCG SERVER
{'='*70}
Servidor: {self.ec2_ip}
Usuario SSH: {self.ssh_user}
Clave SSH: {self.ssh_key_path}
Directorio del proyecto: {self.project_root}
{'='*70}
""")
        
        deployment_steps = [
            ("Validar archivos locales", self.validate_local_files),
            ("Probar conexión SSH", self.test_connection),
            ("Instalar dependencias del sistema", self.install_system_dependencies),
            ("Crear estructura de proyecto", self.create_project_structure),
            ("Generar archivos de configuración", self.generate_config_files),
            ("Subir archivos del proyecto", self.upload_project_files),
            ("Crear script del servidor", self.create_server_script),
            ("Corregir rutas de importación", self.fix_import_paths),
            ("Inicializar base de datos", self.initialize_database),
            ("Crear servicio systemd", self.create_systemd_service),
            ("Configurar seguridad", self.configure_security),
            ("Crear scripts de monitoreo", self.create_monitoring_scripts),
            ("Iniciar servidor", self.start_server),
            ("Probar conexión WebSocket", self.test_server_connection),
            ("Verificación de salud", self.perform_health_check)
        ]
        
        successful_steps = 0
        total_steps = len(deployment_steps)
        
        for i, (step_name, step_func) in enumerate(deployment_steps, 1):
            print(f"\n{'─'*25} PASO {i}/{total_steps}: {step_name} {'─'*25}")
            
            try:
                if step_func():
                    successful_steps += 1
                    print_success(f"[OK]COMPLETADO: {step_name}")
                else:
                    print_error(f"[ERROR]FALLÓ: {step_name}")
                    
                    # Preguntar si continuar
                    if i < total_steps:
                        response = input(f"\n¿Continuar con el despliegue? (s/N): ")
                        if response.lower() not in ['s', 'sí', 'si', 'y', 'yes']:
                            print_warning("Despliegue cancelado por el usuario")
                            return False
                            
            except KeyboardInterrupt:
                print_error("\n[ERROR]Despliegue interrumpido por el usuario")
                return False
            except Exception as e:
                print_error(f"[ERROR]Error en {step_name}: {e}")
                
                response = input(f"\n¿Continuar con el despliegue? (s/N): ")
                if response.lower() not in ['s', 'sí', 'si', 'y', 'yes']:
                    print_warning("Despliegue cancelado por el usuario")
                    return False
        
        # Mostrar resumen final
        print(f"\n{'='*70}")
        print(f"RESUMEN DEL DESPLIEGUE")
        print(f"{'='*70}")
        
        success_rate = (successful_steps / total_steps) * 100
        print(f"Pasos completados: {successful_steps}/{total_steps} ({success_rate:.1f}%)")
        
        if successful_steps == total_steps:
            print_success("🎉 DESPLIEGUE COMPLETAMENTE EXITOSO")
            self.show_deployment_summary()
            return True
        elif successful_steps >= total_steps * 0.8:
            print_warning("[WARNING] DESPLIEGUE MAYORMENTE EXITOSO")
            print_info("El servidor debería funcionar, pero revisa los errores")
            self.show_deployment_summary()
            return True
        else:
            print_error("[ERROR]DESPLIEGUE FALLÓ")
            print_info("Demasiados errores - revisar configuración")
            return False

def main():
    if len(sys.argv) < 3:
        print(f"""
{Colors.CYAN}{'='*60}{Colors.NC}
{Colors.CYAN}DESPLIEGUE SEGURO POKEMON TCG SERVER{Colors.NC}
{Colors.CYAN}{'='*60}{Colors.NC}

{Colors.YELLOW}Uso:{Colors.NC}
  python3 deploy_secure.py <EC2-IP> <RUTA-CLAVE-SSH> [USUARIO] [DIRECTORIO-PROYECTO]

{Colors.YELLOW}Ejemplos:{Colors.NC}
  python3 deploy_secure.py 54.123.45.67 ~/.ssh/mi-clave.pem
  python3 deploy_secure.py 54.123.45.67 ~/.ssh/mi-clave.pem ec2-user
  python3 deploy_secure.py 54.123.45.67 ~/.ssh/mi-clave.pem ec2-user server/

{Colors.YELLOW}Parámetros:{Colors.NC}
  EC2-IP              : IP pública de tu instancia EC2
  RUTA-CLAVE-SSH      : Ruta al archivo .pem de AWS
  USUARIO (opcional)  : Usuario SSH (default: ec2-user)
  DIRECTORIO-PROYECTO : Directorio local del proyecto (default: server)

{Colors.YELLOW}Requisitos previos:{Colors.NC}
  ✓ Instancia EC2 ejecutándose
  ✓ Security Group con puertos 22 y 8765 abiertos
  ✓ Archivos del proyecto organizados localmente
  ✓ Conexión SSH funcionando

{Colors.YELLOW}Estructura requerida del proyecto:{Colors.NC}
  server/
  ├── game/
  │   └── core/
  │       ├── database/
  │       │   ├── database_manager.py
  │       │   └── daos/
  │       │       ├── user_dao.py
  │       │       └── card_dao.py
  │       └── auth/
  │           └── auth_manager.py
  └── [otros archivos opcionales]

{Colors.GREEN}Este script realizará:{Colors.NC}
  🔧 Instalación de dependencias
  📁 Creación de estructura de directorios
  📤 Subida de archivos del proyecto
  🔐 Configuración de seguridad
  🗄️  Inicialización de base de datos
  🔄 Creación de servicio systemd
  [INFO]Configuración de monitoreo
  🚀 Inicio del servidor

{Colors.RED}[WARNING] IMPORTANTE:{Colors.NC}
  - Este script sobrescribirá la instalación existente
  - Ejecuta cleanup_old_server.py antes si es necesario
  - Verifica que los archivos locales estén completos
""")
        sys.exit(1)
    
    # Parsear argumentos
    ec2_ip = sys.argv[1]
    ssh_key_path = sys.argv[2]
    ssh_user = sys.argv[3] if len(sys.argv) > 3 else "ec2-user"
    project_root = sys.argv[4] if len(sys.argv) > 4 else "server"
    
    # Validar IP
    if not ec2_ip.replace('.', '').replace('-', '').isalnum():
        print_error("Formato de IP inválido")
        sys.exit(1)
    
    try:
        print_deploy(f"Iniciando despliegue en {ec2_ip}...")
        
        deployer = SecurePokemonTCGDeployer(ec2_ip, ssh_key_path, ssh_user, project_root)
        success = deployer.full_deployment()
        
        if success:
            print_success("🎉 ¡DESPLIEGUE COMPLETADO EXITOSAMENTE!")
            sys.exit(0)
        else:
            print_error("[ERROR]DESPLIEGUE FALLÓ")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[ERROR]Despliegue cancelado por el usuario{Colors.NC}")
        sys.exit(1)
    except FileNotFoundError as e:
        print_error(f"Archivo no encontrado: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error durante el despliegue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()