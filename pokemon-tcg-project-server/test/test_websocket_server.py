#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente de Prueba WebSocket para Servidor Pokemon TCG
Prueba la conectividad del servidor desplegado y funciones de autenticación
"""

import asyncio
import json
import getpass
import sys
import os
from datetime import datetime
import threading
import time

# Manejo de versiones de websockets
try:
    import websockets
    import websockets.exceptions
    # Verificar si existe ConnectionRefused en la versión actual
    if not hasattr(websockets.exceptions, 'ConnectionRefused'):
        # En versiones más nuevas, usar las excepciones estándar de Python
        websockets.exceptions.ConnectionRefused = ConnectionRefusedError
except ImportError:
    print("❌ Error: Módulo 'websockets' no encontrado")
    print("Instale con: pip install websockets")
    sys.exit(1)

class ClientePruebaWebSocket:
    def __init__(self, server_ip, server_port=8765):
        self.server_ip = server_ip
        self.server_port = server_port
        self.websocket = None
        self.connected = False
        self.token = None
        self.username = None
        self.ejecutando = True
        
    def imprimir_cabecera(self):
        """Imprimir cabecera del programa"""
        print("=" * 70)
        print("CLIENTE DE PRUEBA WEBSOCKET - POKEMON TCG SERVER")
        print("=" * 70)
        print(f"Servidor objetivo: ws://{self.server_ip}:{self.server_port}")
        print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def imprimir_estado_conexion(self):
        """Mostrar estado actual de la conexión"""
        if self.connected:
            status = "🟢 CONECTADO"
            user_info = f" | Usuario: {self.username}" if self.username else ""
            token_info = f" | Token: {self.token[:20]}..." if self.token else ""
        else:
            status = "🔴 DESCONECTADO"
            user_info = ""
            token_info = ""
        
        print(f"Estado: {status}{user_info}{token_info}")
    
    def imprimir_menu(self):
        """Imprimir menú de opciones"""
        self.imprimir_estado_conexion()
        print("\nComandos disponibles:")
        
        if not self.connected:
            print("  connect    - Conectar al servidor WebSocket")
            print("  quit       - Salir del programa")
        else:
            if not self.token:
                print("  ping       - Enviar ping al servidor")
                print("  register   - Registrar nuevo usuario")
                print("  login      - Iniciar sesión")
                print("  status     - Ver estado del servidor")
                print("  disconnect - Desconectar del servidor")
            else:
                print("  ping       - Enviar ping al servidor")
                print("  userinfo   - Obtener información del usuario")
                print("  status     - Ver estado del servidor")
                print("  logout     - Cerrar sesión")
                print("  disconnect - Desconectar del servidor")
        
        print("  quit       - Salir del programa")
        print("-" * 50)
    
    async def conectar_servidor(self):
        """Conectar al servidor WebSocket"""
        try:
            print(f"🔄 Conectando a ws://{self.server_ip}:{self.server_port}...")
            
            # Usar asyncio.wait_for para timeout en lugar del parámetro timeout
            self.websocket = await asyncio.wait_for(
                websockets.connect(f"ws://{self.server_ip}:{self.server_port}"),
                timeout=10
            )
            
            self.connected = True
            print("✅ Conexión establecida exitosamente")
            
            # Escuchar mensaje de bienvenida
            try:
                welcome_msg = await asyncio.wait_for(self.websocket.recv(), timeout=5)
                welcome_data = json.loads(welcome_msg)
                if welcome_data.get('type') == 'welcome':
                    print(f"📨 Mensaje de bienvenida: {welcome_data.get('message', 'Sin mensaje')}")
                    print(f"🏷️  Versión del servidor: {welcome_data.get('server_version', 'Desconocida')}")
            except asyncio.TimeoutError:
                print("⚠️  No se recibió mensaje de bienvenida (timeout)")
            except json.JSONDecodeError:
                print("⚠️  Mensaje de bienvenida no es JSON válido")
            
            return True
            
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError, OSError) as e:
            if "Connection refused" in str(e) or isinstance(e, ConnectionRefusedError):
                print("❌ Error: Conexión rechazada. Verifique que el servidor esté ejecutándose")
            else:
                print(f"❌ Error de conexión: {e}")
            return False
        except asyncio.TimeoutError:
            print("❌ Error: Timeout de conexión. El servidor no responde")
            return False
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
            
            return True
            
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError, OSError) as e:
            if "Connection refused" in str(e) or isinstance(e, ConnectionRefusedError):
                print("❌ Error: Conexión rechazada. Verifique que el servidor esté ejecutándose")
            else:
                print(f"❌ Error de conexión: {e}")
            return False
        except asyncio.TimeoutError:
            print("❌ Error: Timeout de conexión. El servidor no responde")
            return False
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    async def desconectar_servidor(self):
        """Desconectar del servidor"""
        if self.websocket and self.connected:
            try:
                await self.websocket.close()
                print("👋 Desconectado del servidor")
            except Exception as e:
                print(f"⚠️  Error al desconectar: {e}")
        
        self.connected = False
        self.websocket = None
        self.token = None
        self.username = None
    
    async def enviar_mensaje(self, data):
        """Enviar mensaje al servidor y recibir respuesta"""
        if not self.connected or not self.websocket:
            print("❌ No hay conexión activa")
            return None
        
        try:
            # Enviar mensaje
            mensaje_json = json.dumps(data)
            await self.websocket.send(mensaje_json)
            print(f"📤 Enviado: {data.get('action', 'desconocido')}")
            
            # Recibir respuesta
            respuesta = await asyncio.wait_for(self.websocket.recv(), timeout=10)
            respuesta_data = json.loads(respuesta)
            print(f"📨 Recibido: {json.dumps(respuesta_data, indent=2, ensure_ascii=False)}")
            
            return respuesta_data
            
        except asyncio.TimeoutError:
            print("❌ Timeout esperando respuesta del servidor")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Error decodificando respuesta JSON: {e}")
            return None
        except Exception as e:
            print(f"❌ Error enviando/recibiendo mensaje: {e}")
            return None
    
    async def handle_ping(self):
        """Enviar ping al servidor"""
        print("\n🏓 PING AL SERVIDOR")
        print("=" * 25)
        
        start_time = time.time()
        respuesta = await self.enviar_mensaje({"action": "ping"})
        end_time = time.time()
        
        if respuesta:
            latency = (end_time - start_time) * 1000
            if respuesta.get('success'):
                print(f"✅ Pong recibido - Latencia: {latency:.2f}ms")
            else:
                print(f"⚠️  Respuesta de ping inesperada")
        else:
            print("❌ No se recibió respuesta al ping")
    
    async def handle_register(self):
        """Registrar nuevo usuario"""
        print("\n📝 REGISTRO DE USUARIO")
        print("=" * 30)
        
        username = input("Nombre de usuario: ").strip()
        if not username:
            print("❌ El nombre de usuario no puede estar vacío")
            return
        
        password = getpass.getpass("Contraseña: ")
        if not password:
            print("❌ La contraseña no puede estar vacía")
            return
        
        confirm_password = getpass.getpass("Confirmar contraseña: ")
        if password != confirm_password:
            print("❌ Las contraseñas no coinciden")
            return
        
        data = {
            "action": "register",
            "username": username,
            "password": password,
            "confirm_password": confirm_password
        }
        
        respuesta = await self.enviar_mensaje(data)
        if respuesta:
            if respuesta.get('success'):
                print("✅ Usuario registrado exitosamente")
            else:
                print(f"❌ Error en registro: {respuesta.get('message', 'Error desconocido')}")
    
    async def handle_login(self):
        """Iniciar sesión"""
        print("\n🔐 INICIO DE SESIÓN")
        print("=" * 25)
        
        username = input("Nombre de usuario: ").strip()
        if not username:
            print("❌ El nombre de usuario no puede estar vacío")
            return
        
        password = getpass.getpass("Contraseña: ")
        if not password:
            print("❌ La contraseña no puede estar vacía")
            return
        
        data = {
            "action": "login",
            "username": username,
            "password": password
        }
        
        respuesta = await self.enviar_mensaje(data)
        if respuesta:
            if respuesta.get('success'):
                self.token = respuesta.get('token')
                self.username = username
                user_info = respuesta.get('user', {})
                print(f"✅ Inicio de sesión exitoso")
                print(f"👤 Usuario: {user_info.get('username', username)}")
                print(f"🆔 ID: {user_info.get('id', 'Desconocido')}")
                print(f"🎫 Token: {self.token[:20]}..." if self.token else "Sin token")
            else:
                print(f"❌ Error en login: {respuesta.get('message', 'Error desconocido')}")
    
    async def handle_logout(self):
        """Cerrar sesión"""
        print("\n👋 CERRAR SESIÓN")
        print("=" * 20)
        
        data = {"action": "logout"}
        respuesta = await self.enviar_mensaje(data)
        
        if respuesta:
            if respuesta.get('success'):
                print("✅ Sesión cerrada exitosamente")
                self.token = None
                self.username = None
            else:
                print(f"❌ Error cerrando sesión: {respuesta.get('message', 'Error desconocido')}")
    
    async def handle_user_info(self):
        """Obtener información del usuario"""
        print("\n👤 INFORMACIÓN DEL USUARIO")
        print("=" * 35)
        
        if not self.token:
            print("❌ No hay token de sesión activo")
            return
        
        data = {
            "action": "get_user_data",
            "token": self.token
        }
        
        respuesta = await self.enviar_mensaje(data)
        if respuesta:
            if respuesta.get('success'):
                user_info = respuesta.get('user', {})
                print(f"👤 Usuario: {user_info.get('username', 'Desconocido')}")
                print(f"🆔 ID: {user_info.get('id', 'Desconocido')}")
                print(f"📅 Registrado: {user_info.get('created_at', 'Desconocido')}")
            else:
                print(f"❌ Error obteniendo info: {respuesta.get('message', 'Error desconocido')}")
                # Token puede haber expirado
                if "token" in respuesta.get('message', '').lower():
                    self.token = None
                    self.username = None
    
    async def handle_server_status(self):
        """Obtener estado del servidor"""
        print("\n📊 ESTADO DEL SERVIDOR")
        print("=" * 30)
        
        data = {"action": "get_server_status"}
        respuesta = await self.enviar_mensaje(data)
        
        if respuesta:
            if respuesta.get('success'):
                status = respuesta.get('server_status', {})
                print(f"🏷️  Versión: {status.get('version', 'Desconocida')}")
                print(f"⏱️  Uptime: {status.get('uptime', 0):.2f}s")
                print(f"👥 Clientes conectados: {status.get('connected_clients', 0)}")
                print(f"🔐 Clientes autenticados: {status.get('authenticated_clients', 0)}")
                print(f"📈 Estado: {status.get('status', 'Desconocido')}")
            else:
                print(f"❌ Error obteniendo estado: {respuesta.get('message', 'Error desconocido')}")
    
    async def handle_comando(self, comando):
        """Manejar comandos del usuario"""
        comando = comando.lower().strip()
        
        if comando == "quit":
            print("\n👋 ¡Hasta luego!")
            self.ejecutando = False
            return
        
        if comando == "connect":
            if not self.connected:
                await self.conectar_servidor()
            else:
                print("⚠️  Ya está conectado")
        
        elif comando == "disconnect":
            if self.connected:
                await self.desconectar_servidor()
            else:
                print("⚠️  No hay conexión activa")
        
        elif self.connected:
            if comando == "ping":
                await self.handle_ping()
            elif comando == "register":
                await self.handle_register()
            elif comando == "login":
                await self.handle_login()
            elif comando == "logout":
                await self.handle_logout()
            elif comando == "userinfo":
                await self.handle_user_info()
            elif comando == "status":
                await self.handle_server_status()
            else:
                print(f"❌ Comando desconocido: {comando}")
        else:
            print("❌ Debe conectarse primero (comando: connect)")
    
    async def ejecutar(self):
        """Ejecutar cliente de prueba"""
        self.imprimir_cabecera()
        
        while self.ejecutando:
            try:
                print()
                self.imprimir_menu()
                comando = input("\n🎮 Ingrese comando: ").strip()
                
                if not comando:
                    continue
                
                await self.handle_comando(comando)
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Programa interrumpido")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Intente de nuevo o escriba 'quit' para salir")
        
        # Limpiar conexión al salir
        if self.connected:
            await self.desconectar_servidor()


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python3 test_websocket_server.py <SERVER_IP> [PORT]")
        print("Ejemplo: python3 test_websocket_server.py 54.123.45.67")
        print("Ejemplo: python3 test_websocket_server.py 54.123.45.67 8765")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
    
    try:
        cliente = ClientePruebaWebSocket(server_ip, server_port)
        asyncio.run(cliente.ejecutar())
    except Exception as e:
        print(f"❌ Error al iniciar cliente: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()