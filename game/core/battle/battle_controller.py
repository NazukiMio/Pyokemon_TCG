from typing import Dict, Any, Optional, Union
from game.core.battle.battle_manager import BattleManager
from game.core.game_manager import GameManager

class BattleController:
    """Controlador de Batalla - Punto de entrada unificado para batallas individuales"""
    
    def __init__(self, game_manager: GameManager):
        """
        Inicializar controlador de batalla
        
        Args:
            game_manager: Instancia del administrador de juego (desde escena principal)
        """
        self.game_manager = game_manager
        self.current_battle: Optional[BattleManager] = None
    
    def start_new_battle(self, player_deck_id: int, opponent_type: str = "AI", 
                        opponent_difficulty: str = "rookie_trainer") -> Dict[str, Any]:
        """
        Iniciar nueva batalla
        
        Args:
            player_deck_id: ID del mazo del jugador (pasado desde escena principal)
            opponent_type: Tipo de oponente
            opponent_difficulty: ID del oponente (puede ser número o clave de AI)
            
        Returns:
            Resultado del inicio
        """
        try:
            # Limpiar batalla anterior
            if self.current_battle:
                self.current_battle.cleanup()
            
            # Obtener ID del usuario logueado actual
            player_id = self.game_manager.current_user_id
            if not player_id:
                return {"success": False, "error": "Usuario no logueado"}
            
            # Verificar que el mazo existe y pertenece al usuario
            deck_cards = self.game_manager.get_deck_cards(player_deck_id)
            if not deck_cards:
                return {"success": False, "error": f"Mazo {player_deck_id} no existe o está vacío"}
            
            print(f"🚀 Iniciando batalla: Jugador={player_id}, Mazo={player_deck_id}, Oponente={opponent_type}:{opponent_difficulty}")
            
            # Crear administrador de batalla (usando constructor completo existente)
            self.current_battle = BattleManager(
                self.game_manager, 
                player_id, 
                player_deck_id,
                opponent_type,
                opponent_difficulty
            )
            
            # Verificar si la inicialización fue exitosa
            if self.current_battle.battle_state and len(self.current_battle.player_states) > 0:
                # Iniciar batalla
                if self.current_battle.start_battle():
                    return {
                        "success": True,
                        "battle_id": self.current_battle.battle_state.battle_id,
                        "message": "Batalla iniciada exitosamente"
                    }
                else:
                    return {"success": False, "error": "Fallo al iniciar batalla"}
            else:
                return {"success": False, "error": "Fallo en inicialización de batalla"}
                
        except Exception as e:
            return {"success": False, "error": f"Excepción al iniciar batalla: {e}"}
    
    def get_current_state(self) -> Dict[str, Any]:
        """Obtener estado actual de batalla"""
        
        if not self.current_battle:
            return {"success": False, "error": "No hay batalla activa"}
        
        try:
            # Usar método de estado para UI existente
            state = self.current_battle.get_game_state_for_ui()
            
            # 🔍 添加调试信息
            print(f"🔍 [调试] battle_controller.get_current_state():")
            print(f"   current_battle类型: {type(self.current_battle)}")
            print(f"   get_game_state_for_ui()返回类型: {type(state)}")
            print(f"   state属性: {[attr for attr in dir(state) if not attr.startswith('_')]}")
            print(f"   包装后返回类型: dict")
            
            return {"success": True, "state": state}
            
        except Exception as e:
            print(f"❌ [调试] get_current_state异常: {e}")
            return {"success": False, "error": f"Fallo al obtener estado: {e}"}
    
    def process_player_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesar acción del jugador"""
        if not self.current_battle:
            return {"success": False, "error": "No hay batalla activa"}
        
        try:
            # Importar clases necesarias
            from game.core.battle.battle_actions import create_action_request, ActionType
            
            action_type = action_data.get("type")
            player_id = self.game_manager.current_user_id
            
            # Crear ActionRequest estándar
            if action_type == "attack":
                action_request = create_action_request(
                    ActionType.ATTACK.value, 
                    player_id,
                    parameters=action_data.get("parameters", {})
                )
            elif action_type == "end_turn":
                action_request = create_action_request(ActionType.END_TURN.value, player_id)
            elif action_type == "draw_card":
                action_request = create_action_request(ActionType.DRAW_CARD.value, player_id)
            elif action_type == "gain_energy":
                action_request = create_action_request(ActionType.GAIN_ENERGY.value, player_id)
            else:
                return {"success": False, "error": f"Tipo de acción desconocida: {action_type}"}
            
            # Usar método de procesamiento existente
            response = self.current_battle.process_player_action(action_request)
            
            # Convertir formato de respuesta
            result = {
                "success": response.is_success(),
                "message": response.message,
                "effects": response.effects
            }
            
            # Verificar si la batalla terminó
            if self.current_battle.battle_state.is_battle_over():
                result["battle_ended"] = True
                result["winner"] = self.current_battle.battle_state.winner_id
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"Fallo al procesar acción: {e}"}
    
    def end_battle(self) -> Dict[str, Any]:
        """Terminar batalla actual"""
        if not self.current_battle:
            return {"success": False, "error": "No hay batalla activa"}
        
        try:
            # Obtener resultado de batalla
            battle_summary = self.current_battle.get_battle_summary()
            
            result = {
                "success": True,
                "battle_id": self.current_battle.battle_state.battle_id,
                "result": battle_summary.get("status", {}).get("result", "unknown"),
                "winner": battle_summary.get("status", {}).get("winner"),
                "duration": self.current_battle.battle_state.get_battle_duration()
            }
            
            # Limpiar recursos
            self.current_battle.cleanup()
            self.current_battle = None
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"Fallo al terminar batalla: {e}"}
    
    def is_battle_active(self) -> bool:
        """Verificar si hay batalla activa"""
        return self.current_battle is not None and not self.current_battle.battle_state.is_battle_over()

# =============================================================================
# Bloque de pruebas - Verificar funcionalidad de BattleController con datos reales
# =============================================================================

if __name__ == "__main__":
    def test_battle_controller():
        """Probar flujo completo del controlador de batalla"""
        print("🧪 Iniciando pruebas de BattleController...")
        
        # Crear administrador de juego y simular login
        print("\n--- Inicializar entorno de juego ---")
        game_manager = GameManager()
        
        # Simular login de usuario (usar usuario por defecto)
        if not game_manager.current_user_id:
            game_manager.current_user_id = 1  # Asumir ID de usuario = 1
        
        # Obtener mazos del usuario
        user_decks = game_manager.get_user_decks()
        if not user_decks:
            print("❌ Usuario no tiene mazos disponibles, crear mazos primero en interfaz principal")
            return
        
        test_deck_id = user_decks[0]['id']  # Usar primer mazo
        print(f"✅ Usando mazo de usuario: {test_deck_id}")
        
        # Crear controlador
        controller = BattleController(game_manager)
        
        # Prueba 1: Iniciar batalla
        print("\n--- Prueba 1: Iniciar batalla ---")
        # Usar clave de AI en lugar de número
        start_result = controller.start_new_battle(test_deck_id, opponent_difficulty="rookie_trainer")
        print(f"Resultado de inicio: {'✅ Éxito' if start_result['success'] else '❌ Fallo'}")
        
        if not start_result['success']:
            print(f"Error: {start_result['error']}")
            game_manager.cleanup()
            return
        
        print(f"ID de batalla: {start_result['battle_id']}")
        
        # Prueba 2: Obtener estado de batalla
        print("\n--- Prueba 2: Obtener estado de batalla ---")
        state_result = controller.get_current_state()
        if not state_result['success']:
            print(f"❌ Fallo al obtener estado: {state_result['error']}")
        else:
            state = state_result['state']
            print(f"✅ Jugador actual: {state['current_player']}")
            print(f"✅ Fase actual: {state['phase']}")
            print(f"✅ Número de turno: {state['turn']}")
        
        # Prueba 3: Simular algunos turnos de batalla
        print("\n--- Prueba 3: Simular flujo de batalla ---")
        for turn in range(3):
            print(f"\nPrueba turno {turn + 1}:")
            
            # Obtener estado actual
            state_result = controller.get_current_state()
            if not state_result['success']:
                break
                
            state = state_result['state']
            current_player = state["current_player"]
            print(f"Jugador actual: {current_player}, Fase: {state['phase']}")
            
            # Si es turno del jugador
            if current_player == game_manager.current_user_id:
                # Ejecutar acciones correspondientes según la fase
                if state["phase"] == "draw":
                    print("Ejecutando robo de carta...")
                    action_result = controller.process_player_action({"type": "draw_card"})
                    print(f"Resultado de robo: {action_result}")
                
                elif state["phase"] == "energy":
                    print("Obteniendo energía...")
                    action_result = controller.process_player_action({"type": "gain_energy"})
                    print(f"Resultado de energía: {action_result}")
                
                elif state["phase"] == "action":
                    print("Intentando atacar...")
                    action_result = controller.process_player_action({"type": "attack"})
                    print(f"Resultado de ataque: {action_result}")
                    
                    # Terminar turno
                    print("Terminando turno...")
                    end_turn_result = controller.process_player_action({"type": "end_turn"})
                    print(f"Resultado de fin de turno: {end_turn_result}")
                    
                    # Verificar si la batalla terminó
                    if end_turn_result.get("battle_ended"):
                        print(f"🏁 ¡Batalla terminada! Ganador: {end_turn_result.get('winner')}")
                        break
            else:
                print("🤖 Turno de IA (procesamiento automático)")
                import time
                time.sleep(1)  # Esperar procesamiento de IA
        
        # Prueba 4: Terminar batalla
        print("\n--- Prueba 4: Terminar batalla ---")
        if controller.is_battle_active():
            end_result = controller.end_battle()
            print(f"Resultado de fin de batalla: {end_result}")
        else:
            print("Batalla ya terminó naturalmente")
        
        # Limpiar
        game_manager.cleanup()
        print("\n🎉 ¡Pruebas de BattleController completadas!")

    # Ejecutar pruebas
    test_battle_controller()