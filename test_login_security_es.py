#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Prueba del Sistema de Autenticación
Prueba el nuevo sistema de autenticación por tokens y la integración con collection_manager
"""

import sys
import os
import getpass

# Agregar ruta del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.core.auth.auth_manager import get_auth_manager
from game.core.database.database_manager import DatabaseManager
from game.core.cards.collection_manager import CardManager

class AppPruebaAuth:
    def __init__(self):
        self.auth = get_auth_manager()
        self.db = DatabaseManager()
        self.card_manager = CardManager(self.db.connection)
        self.ejecutando = True
        
    def imprimir_cabecera(self):
        """Imprimir cabecera del programa"""
        print("=" * 70)
        print("SISTEMA DE AUTENTICACIÓN SEGURA - DEMOSTRACIÓN")
        print("=" * 70)
        print("Demostración de la nueva arquitectura de seguridad basada en tokens")
        print()
    
    def imprimir_menu(self):
        """Imprimir menú"""
        if self.auth.is_logged_in():
            user_info = self.auth.get_user_info()
            username = user_info.get('username', 'Desconocido') if user_info else 'Desconocido'
            print(f"Usuario actual: {username} (Sesión activa)")
            print("\nComandos disponibles:")
            print("  stats - Ver estadísticas de cartas")
            print("  featured   - Ver cartas destacadas")
            print("  daily      - Ver carta destacada del día")
            print("  search      - search cartas")
            print("  pack       - Abrir pack de cartas")
            print("  whoami    - Ver información del usuario actual")
            print("  logout      - Cerrar sesión")
            print("  quit       - Salir del programa")
        else:
            print("Estado actual: Sin sesión activa")
            print("\nComandos disponibles:")
            print("  login      - Iniciar sesión")
            print("  register   - Registrar nuevo usuario")
            print("  quit       - Salir del programa")
        print("-" * 50)
    
    def handle_entrada(self):
        """handle inicio de sesión"""
        print("\nINICIO DE SESIÓN")
        print("=" * 30)
        username = input("Nombre de usuario: ").strip()
        if not username:
            print("El nombre de usuario no puede estar vacío")
            return
        
        password = getpass.getpass("Contraseña: ")
        if not password:
            print("La contraseña no puede estar vacía")
            return
        
        print("Verificando credenciales...")
        exito, mensaje = self.auth.login(username, password)
        
        if exito:
            print(f"{mensaje}")
            user_id = self.auth.get_current_user_id()
            print(f"ID de usuario obtenido: {user_id}")
        else:
            print(f"{mensaje}")
    
    def handle_registro(self):
        """handle registro"""
        print("\nREGISTRO DE NUEVO USUARIO")
        print("=" * 35)
        username = input("Nombre de usuario: ").strip()
        if not username:
            print("El nombre de usuario no puede estar vacío")
            return
        
        password = getpass.getpass("Contraseña: ")
        if not password:
            print("La contraseña no puede estar vacía")
            return
        
        confirm_password = getpass.getpass("Confirmar contraseña: ")
        if password != confirm_password:
            print("Las contraseñas no coinciden")
            return
        
        print("Creando usuario...")
        exito, mensaje = self.auth.register(username, password)
        
        if exito:
            print(f"{mensaje}")
        else:
            print(f"{mensaje}")
    
    def handle_stats(self):
        """Ver estadísticas de cartas"""
        print("\nESTADÍSTICAS DE CARTAS")
        print("=" * 30)
        print("Demostrando: CardManager funciona sin conocer tokens")
        try:
            stats = self.card_manager.get_card_statistics()
            print(f"Total de cartas: {stats['total_cards']}")
            print(f"Total de series: {stats['total_sets']}")
            print(f"Rarezas disponibles: {len(stats['available_rarities'])}")
            print(f"Tipos disponibles: {len(stats['available_types'])}")
            
            print("\nDistribución por rareza:")
            for rareza, cantidad in list(stats['rarity_distribution'].items())[:5]:
                print(f"  • {rareza}: {cantidad}")
            
            print("\nDistribución por tipo:")
            for tipo_carta, cantidad in list(stats['type_distribution'].items())[:5]:
                print(f"  • {tipo_carta}: {cantidad}")
                
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
    
    def handle_featured(self):
        """Ver cartas destacadas"""
        print("\nCARTAS DESTACADAS")
        print("=" * 25)
        print("Demostrando: Acceso a datos sin comprometer seguridad")
        try:
            cards_featured = self.card_manager.get_featured_cards(5)
            
            if cards_featured:
                for i, carta in enumerate(cards_featured, 1):
                    print(f"{i}. {carta.name} ({carta.rarity})")
                    if carta.types:
                        print(f"   Tipo: {', '.join(carta.types)}")
                    if carta.hp:
                        print(f"   HP: {carta.hp}")
                    print()
            else:
                print("No se encontraron cartas destacadas")
                
        except Exception as e:
            print(f"Error al obtener cartas destacadas: {e}")
    
    def handle_daily(self):
        """Ver carta destacada del día"""
        print("\n🌟 CARTA DESTACADA DEL DÍA")
        print("=" * 30)
        try:
            carta_daily = self.card_manager.get_daily_featured_card()
            
            if carta_daily:
                print(f"Destacada de hoy: {carta_daily.name}")
                print(f"Rareza: {carta_daily.rarity}")
                if carta_daily.types:
                    print(f"Tipo: {', '.join(carta_daily.types)}")
                if carta_daily.hp:
                    print(f"HP: {carta_daily.hp}")
                if carta_daily.set_name:
                    print(f"Serie: {carta_daily.set_name}")
            else:
                print("No hay carta destacada para hoy")
                
        except Exception as e:
            print(f"Error al obtener carta del día: {e}")
    
    def handle_search(self):
        """search cartas"""
        print("\n🔍 BÚSQUEDA DE CARTAS")
        print("=" * 25)
        keyword = input("🔍 Ingrese palabra clave (Enter para ver todas): ").strip()
        
        try:
            if keyword:
                cards = self.card_manager.search_cards(name=keyword, limit=10)
            else:
                cards = self.card_manager.search_cards(limit=10)
            
            if cards:
                print(f"\nSe encontraron {len(cards)} cartas:")
                for i, carta in enumerate(cards, 1):
                    print(f"{i}. {carta.name} ({carta.rarity})")
                    if carta.types:
                        print(f"   Tipo: {', '.join(carta.types)}")
            else:
                print("No se encontraron cartas que coincidan")
                
        except Exception as e:
            print(f"Error en la búsqueda: {e}")
    
    def handle_pack(self):
        """Abrir pack de cartas"""
        print("\nABRIR pack DE CARTAS")
        print("=" * 28)
        print("Tipos de packs disponibles:")
        print("  1. basic   - Básico (5 cartas, garantizada Uncommon)")
        print("  2. premium - Premium (5 cartas, garantizada Rare)")
        print("  3. ultra   - Ultra (3 cartas, garantizada Ultra Rare)")
        
        eleccion = input("Elija tipo de pack (1-3): ").strip()
        tipos_pack = {"1": "basic", "2": "premium", "3": "ultra"}
        
        tipo_pack = tipos_pack.get(eleccion, "basic")
        
        try:
            print(f"Abriendo pack {tipo_pack}...")
            cards = self.card_manager.open_pack(tipo_pack)
            
            if cards:
                print(f"\n🎉 ¡Obtuvo {len(cards)} cartas!")
                for i, carta in enumerate(cards, 1):
                    print(f"{i}. {carta.name} ({carta.rarity})")
                    if carta.types:
                        print(f"   Tipo: {', '.join(carta.types)}")
            else:
                print("Error al abrir el pack")
                
        except Exception as e:
            print(f"Error al abrir pack: {e}")
    
    def handle_whoami(self):
        """Ver información del usuario actual"""
        print("\nINFORMACIÓN DEL USUARIO ACTUAL")
        print("=" * 40)
        print("DEMOSTRACIÓN DE SEGURIDAD:")
        try:
            user_id = self.auth.get_current_user_id()
            user_info = self.auth.get_user_info()
            
            if user_info:
                print(f"ID de usuario: {user_id}")
                print(f"Nombre de usuario: {user_info.get('username', 'Desconocido')}")
                print(f"Fecha de registro: {user_info.get('created_at', 'Desconocida')}")
                
                # Mostrar token actual (primeros 20 caracteres)
                if hasattr(self.auth, 'current_token') and self.auth.current_token:
                    token_preview = self.auth.current_token[:20] + "..."
                    print(f"Token actual: {token_preview}")
                    print(f"Longitud del token: {len(self.auth.current_token)} caracteres")
            else:
                print("No se puede obtener información del usuario")
                
        except Exception as e:
            print(f"Error al obtener información del usuario: {e}")
    
    def handle_logout(self):
        """handle cierre de sesión"""
        print("\nCERRANDO SESIÓN")
        print("=" * 20)
        print("Demostrando: Invalidación segura de token")
        if self.auth.logout():
            print("Sesión cerrada exitosamente")
            print("Token invalidado en base de datos")
        else:
            print("Error al cerrar sesión")
    
    def handle_comando(self, comando):
        """handle comandos del usuario"""
        comando = comando.lower().strip()
        
        # Comandos generales
        if comando == "quit":
            print("\n¡Hasta luego!")
            self.ejecutando = False
            return
        
        # Comandos sin sesión activa
        if not self.auth.is_logged_in():
            if comando == "login":
                self.handle_entrada()
            elif comando == "register":
                self.handle_registro()
            else:
                print("Debe iniciar sesión primero")
            return
        
        # Comandos con sesión activa
        if comando == "stats":
            self.handle_stats()
        elif comando == "featured":
            self.handle_featured()
        elif comando == "daily":
            self.handle_daily()
        elif comando == "search":
            self.handle_search()
        elif comando == "pack":
            self.handle_pack()
        elif comando == "whoami":
            self.handle_whoami()
        elif comando == "logout":
            self.handle_logout()
        else:
            print(f"Comando desconocido: {comando}")
    
    def ejecutar(self):
        """Ejecutar programa de prueba"""
        self.imprimir_cabecera()
        
        while self.ejecutando:
            try:
                print()
                self.imprimir_menu()
                comando = input("\nIngrese comando: ").strip()
                
                if not comando:
                    continue
                
                self.handle_comando(comando)
                
            except KeyboardInterrupt:
                print("\n\nPrograma interrumpido, ¡hasta luego!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Por favor intente de nuevo o escriba 'quit' para terminar")
        
        # Limpiar recursos
        if hasattr(self, 'db'):
            self.db.close()


def main():
    """Función principal"""
    try:
        app = AppPruebaAuth()
        app.ejecutar()
    except Exception as e:
        print(f"Error al iniciar el programa: {e}")
        print("Verifique que la base de datos y módulos estén funcionando correctamente")


if __name__ == "__main__":
    main()