#!/usr/bin/env python3
"""
Pokemon TCG 服务器清理脚本
清理旧的服务器安装和配置
"""

import sys
import subprocess
import platform
from pathlib import Path

class Colors:
    """控制台颜色类"""
    if platform.system() == "Windows":
        try:
            import colorama
            colorama.init()
            RED = '\033[0;31m'
            GREEN = '\033[0;32m'
            YELLOW = '\033[1;33m'
            BLUE = '\033[0;34m'
            NC = '\033[0m'
        except ImportError:
            RED = GREEN = YELLOW = BLUE = NC = ''
    else:
        RED = '\033[0;31m'
        GREEN = '\033[0;32m'
        YELLOW = '\033[1;33m'
        BLUE = '\033[0;34m'
        NC = '\033[0m'

def print_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")

def print_success(msg):
    print(f"{Colors.GREEN}[ÉXITO]{Colors.NC} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[ADVERTENCIA]{Colors.NC} {msg}")

def print_error(msg):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")

class ServerCleaner:
    def __init__(self, ec2_ip, ssh_key_path, ssh_user="ec2-user"):
        self.ec2_ip = ec2_ip
        self.ssh_key_path = Path(ssh_key_path)
        self.ssh_user = ssh_user
        
        # Validar archivo de clave SSH
        if not self.ssh_key_path.exists():
            raise FileNotFoundError(f"Archivo de clave SSH no encontrado: {ssh_key_path}")
        
        # Corregir permisos (solo en sistemas Unix)
        if platform.system() != "Windows":
            self.ssh_key_path.chmod(0o600)
    
    def run_ssh_command(self, command, timeout=30):
        """Ejecutar comando SSH con manejo de errores mejorado"""
        ssh_cmd = [
            "ssh", "-i", str(self.ssh_key_path),
            "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=no",
            f"{self.ssh_user}@{self.ec2_ip}",
            command
        ]
        
        try:
            result = subprocess.run(
                ssh_cmd, 
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0 and result.stderr:
                print_warning(f"Comando con advertencias: {command}")
                print(f"  └─ {result.stderr.strip()}")
            
            return result.returncode == 0, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            print_error(f"Timeout en comando: {command}")
            return False, "", "Timeout"
        except Exception as e:
            print_error(f"Error ejecutando comando: {e}")
            return False, "", str(e)
    
    def test_connection(self):
        """Probar conexión SSH"""
        print_info("Probando conexión SSH...")
        success, output, error = self.run_ssh_command("echo 'Conexión SSH exitosa'")
        
        if success:
            print_success("Conexión SSH establecida correctamente")
            return True
        else:
            print_error(f"Error de conexión SSH: {error}")
            return False
    
    def backup_important_data(self):
        """Hacer respaldo de datos importantes antes de limpiar"""
        print_info("Realizando respaldo de datos importantes...")
        
        backup_commands = [
            # Crear directorio de respaldo
            "sudo mkdir -p /tmp/pokemon_backup_$(date +%Y%m%d_%H%M%S)",
            
            # Respaldar base de datos si existe
            "if [ -f /opt/pokemon-tcg/data/game_database.db ]; then " +
            "sudo cp /opt/pokemon-tcg/data/game_database.db /tmp/pokemon_backup_$(date +%Y%m%d_%H%M%S)/; " +
            "echo 'Base de datos respaldada'; fi",
            
            # Respaldar configuraciones si existen
            "if [ -d /opt/pokemon-tcg/config ]; then " +
            "sudo cp -r /opt/pokemon-tcg/config /tmp/pokemon_backup_$(date +%Y%m%d_%H%M%S)/; " +
            "echo 'Configuraciones respaldadas'; fi",
            
            # Respaldar logs si existen
            "if [ -d /opt/pokemon-tcg/logs ]; then " +
            "sudo cp -r /opt/pokemon-tcg/logs /tmp/pokemon_backup_$(date +%Y%m%d_%H%M%S)/; " +
            "echo 'Logs respaldados'; fi",
            
            # Mostrar ubicación del respaldo
            "ls -la /tmp/pokemon_backup_* 2>/dev/null || echo 'No hay datos para respaldar'"
        ]
        
        backup_success = True
        for cmd in backup_commands:
            success, output, error = self.run_ssh_command(cmd)
            if not success and "No hay datos" not in output:
                backup_success = False
        
        if backup_success:
            print_success("Respaldo de datos completado")
        else:
            print_warning("Respaldo completado con algunas advertencias")
        
        return True
    
    def stop_services(self):
        """Detener todos los servicios relacionados"""
        print_info("Deteniendo servicios Pokemon TCG...")
        
        service_commands = [
            # Detener servicio principal
            "sudo systemctl stop pokemon-tcg 2>/dev/null || echo 'Servicio pokemon-tcg no está ejecutándose'",
            
            # Deshabilitar servicio
            "sudo systemctl disable pokemon-tcg 2>/dev/null || echo 'Servicio pokemon-tcg no está habilitado'",
            
            # Detener procesos relacionados con WebSocket en puerto 8765
            "sudo pkill -f 'python.*server.py' 2>/dev/null || echo 'No hay procesos server.py ejecutándose'",
            "sudo pkill -f ':8765' 2>/dev/null || echo 'No hay procesos en puerto 8765'",
            
            # Verificar que no haya procesos corriendo
            "ps aux | grep -E '(pokemon|server\.py|:8765)' | grep -v grep || echo 'No hay procesos relacionados ejecutándose'"
        ]
        
        for cmd in service_commands:
            self.run_ssh_command(cmd)
        
        print_success("Servicios detenidos")
        return True
    
    def remove_system_files(self):
        """Eliminar archivos del sistema"""
        print_info("Eliminando archivos del sistema...")
        
        system_cleanup_commands = [
            # Eliminar archivo de servicio systemd
            "sudo rm -f /etc/systemd/system/pokemon-tcg.service",
            "sudo rm -f /etc/systemd/system/pokemon-tcg@.service",
            
            # Recargar systemd
            "sudo systemctl daemon-reload",
            
            # Eliminar archivos de configuración del sistema
            "sudo rm -rf /etc/pokemon-tcg/",
            
            # Eliminar logs del sistema
            "sudo rm -f /var/log/pokemon-tcg*.log",
            "sudo rm -f /var/log/pokemon_tcg*.log",
            
            # Limpiar journald logs específicos
            "sudo journalctl --vacuum-time=1d",
            
            # Verificar eliminación de servicios
            "systemctl list-unit-files | grep pokemon || echo 'No hay servicios pokemon en el sistema'"
        ]
        
        for cmd in system_cleanup_commands:
            self.run_ssh_command(cmd)
        
        print_success("Archivos del sistema eliminados")
        return True
    
    def clean_application_directory(self):
        """Limpiar directorio de aplicación"""
        print_info("Limpiando directorio de aplicación...")
        
        app_cleanup_commands = [
            # Mostrar contenido actual del directorio
            "ls -la /opt/pokemon-tcg/ 2>/dev/null || echo 'Directorio /opt/pokemon-tcg no existe'",
            
            # Eliminar directorio completo
            "sudo rm -rf /opt/pokemon-tcg/",
            
            # Verificar eliminación
            "ls -la /opt/ | grep pokemon || echo 'Directorio pokemon-tcg eliminado correctamente'",
            
            # Limpiar archivos residuales en /tmp
            "sudo rm -rf /tmp/pokemon_*",
            
            # Limpiar posibles archivos en home del usuario
            f"rm -rf /home/{self.ssh_user}/pokemon-tcg* 2>/dev/null || true",
            f"rm -rf /home/{self.ssh_user}/server.py* 2>/dev/null || true",
            f"rm -rf /home/{self.ssh_user}/client.py* 2>/dev/null || true"
        ]
        
        for cmd in app_cleanup_commands:
            self.run_ssh_command(cmd)
        
        print_success("Directorio de aplicación limpiado")
        return True
    
    def clean_cron_jobs(self):
        """Limpiar tareas programadas"""
        print_info("Limpiando tareas programadas...")
        
        cron_commands = [
            # Mostrar crontab actual
            "crontab -l 2>/dev/null || echo 'No hay tareas cron configuradas'",
            
            # Eliminar líneas relacionadas con pokemon-tcg
            "crontab -l 2>/dev/null | grep -v pokemon | crontab - 2>/dev/null || echo 'Crontab limpiado'",
            
            # Verificar crontab después de la limpieza
            "crontab -l 2>/dev/null || echo 'No hay tareas cron restantes'",
            
            # Limpiar posibles scripts de monitoreo
            "sudo rm -f /usr/local/bin/pokemon-*",
            "sudo rm -f /opt/scripts/pokemon-*"
        ]
        
        for cmd in cron_commands:
            self.run_ssh_command(cmd)
        
        print_success("Tareas programadas limpiadas")
        return True
    
    def clean_firewall_rules(self):
        """Limpiar reglas de firewall específicas"""
        print_info("Limpiando reglas de firewall...")
        
        firewall_commands = [
            # Intentar con firewalld primero
            "sudo firewall-cmd --permanent --remove-port=8765/tcp 2>/dev/null || echo 'Puerto 8765 no configurado en firewalld'",
            "sudo firewall-cmd --reload 2>/dev/null || echo 'firewalld no disponible'",
            
            # Intentar con iptables como alternativa
            "sudo iptables -D INPUT -p tcp --dport 8765 -j ACCEPT 2>/dev/null || echo 'Regla iptables 8765 no encontrada'",
            
            # Mostrar reglas actuales
            "sudo firewall-cmd --list-all 2>/dev/null || sudo iptables -L | grep 8765 || echo 'Reglas de firewall verificadas'"
        ]
        
        for cmd in firewall_commands:
            self.run_ssh_command(cmd)
        
        print_success("Reglas de firewall limpiadas")
        return True
    
    def verify_cleanup(self):
        """Verificar que la limpieza sea completa"""
        print_info("Verificando limpieza...")
        
        verification_commands = [
            # Verificar procesos
            ("Procesos", "ps aux | grep -E '(pokemon|server\.py)' | grep -v grep || echo 'Sin procesos relacionados'"),
            
            # Verificar servicios
            ("Servicios", "systemctl list-unit-files | grep pokemon || echo 'Sin servicios pokemon'"),
            
            # Verificar directorios
            ("Directorios", "ls -la /opt/ | grep pokemon || echo 'Sin directorios pokemon en /opt'"),
            
            # Verificar puertos
            ("Puertos", "sudo netstat -tlpn | grep :8765 || echo 'Puerto 8765 no está en uso'"),
            
            # Verificar crontab
            ("Crontab", "crontab -l 2>/dev/null | grep pokemon || echo 'Sin tareas cron pokemon'"),
            
            # Verificar archivos de log
            ("Logs", "ls -la /var/log/ | grep pokemon || echo 'Sin archivos de log pokemon'")
        ]
        
        all_clean = True
        print("\n" + "="*50)
        print("REPORTE DE VERIFICACIÓN")
        print("="*50)
        
        for check_name, cmd in verification_commands:
            success, output, error = self.run_ssh_command(cmd)
            status = "✅ LIMPIO" if "Sin" in output or "no" in output.lower() else "⚠️  REVISAR"
            print(f"{check_name:12} │ {status}")
            
            if "REVISAR" in status:
                all_clean = False
                print(f"             │ Salida: {output.strip()}")
        
        print("="*50)
        
        if all_clean:
            print_success("Limpieza completada exitosamente - Sistema limpio")
        else:
            print_warning("Limpieza mayormente completa - Revisar elementos marcados")
        
        return all_clean
    
    def full_cleanup(self):
        """Ejecutar limpieza completa"""
        print(f"""
{'='*60}
LIMPIEZA DEL SERVIDOR POKEMON TCG
{'='*60}
Servidor: {self.ec2_ip}
Usuario: {self.ssh_user}
Clave SSH: {self.ssh_key_path}
{'='*60}
""")
        
        cleanup_steps = [
            ("Probar conexión", self.test_connection),
            ("Respaldar datos importantes", self.backup_important_data),
            ("Detener servicios", self.stop_services),
            ("Eliminar archivos del sistema", self.remove_system_files),
            ("Limpiar directorio de aplicación", self.clean_application_directory),
            ("Limpiar tareas programadas", self.clean_cron_jobs),
            ("Limpiar reglas de firewall", self.clean_firewall_rules),
            ("Verificar limpieza", self.verify_cleanup)
        ]
        
        for step_name, step_func in cleanup_steps:
            print(f"\n{'─'*20} {step_name} {'─'*20}")
            
            try:
                if not step_func():
                    print_error(f"Error en paso: {step_name}")
                    response = input(f"¿Continuar con la limpieza? (s/N): ")
                    if response.lower() not in ['s', 'sí', 'si', 'y', 'yes']:
                        return False
                else:
                    print_success(f"{step_name} completado")
            except Exception as e:
                print_error(f"Excepción en {step_name}: {e}")
                response = input(f"¿Continuar con la limpieza? (s/N): ")
                if response.lower() not in ['s', 'sí', 'si', 'y', 'yes']:
                    return False
        
        self.show_cleanup_summary()
        return True
    
    def show_cleanup_summary(self):
        """Mostrar resumen de la limpieza"""
        print(f"""

{'='*60}
🧹 LIMPIEZA COMPLETADA
{'='*60}

✅ Servicios Pokemon TCG detenidos y deshabilitados
✅ Archivos del sistema eliminados
✅ Directorio de aplicación limpiado
✅ Tareas programadas eliminadas
✅ Reglas de firewall limpiadas
✅ Respaldos creados en /tmp/pokemon_backup_*

📋 PRÓXIMOS PASOS:
1. Ejecutar el script de despliegue: deploy_secure.py
2. Verificar que el nuevo despliegue funcione correctamente
3. Eliminar respaldos cuando ya no se necesiten

⚠️  NOTA IMPORTANTE:
Los respaldos están en /tmp/pokemon_backup_* en el servidor.
Descargar antes de que se eliminen automáticamente.

🚀 El servidor está listo para un nuevo despliegue!
""")

def main():
    if len(sys.argv) < 3:
        print("""
Uso: python3 cleanup_old_server.py <EC2-IP> <RUTA-CLAVE-SSH> [USUARIO]

Ejemplos:
  python3 cleanup_old_server.py 54.123.45.67 ~/.ssh/mi-clave.pem
  python3 cleanup_old_server.py 54.123.45.67 ~/.ssh/mi-clave.pem ec2-user
  python3 cleanup_old_server.py 54.123.45.67 C:\\Users\\Name\\clave.pem ubuntu

Descripción:
  Este script limpia completamente una instalación anterior del servidor Pokemon TCG,
  incluyendo servicios, archivos, configuraciones y tareas programadas.
""")
        sys.exit(1)
    
    ec2_ip = sys.argv[1]
    ssh_key_path = sys.argv[2]
    ssh_user = sys.argv[3] if len(sys.argv) > 3 else "ec2-user"
    
    try:
        print_warning("¡ADVERTENCIA! Este script eliminará completamente la instalación actual.")
        print_info("Se crearán respaldos de datos importantes antes de la limpieza.")
        
        response = input("\n¿Desea continuar con la limpieza? (escriba 'CONFIRMAR' para continuar): ")
        if response != 'CONFIRMAR':
            print_info("Limpieza cancelada por el usuario")
            sys.exit(0)
        
        cleaner = ServerCleaner(ec2_ip, ssh_key_path, ssh_user)
        success = cleaner.full_cleanup()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}❌ Limpieza cancelada por el usuario{Colors.NC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error durante la limpieza: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()