"""
现代化设置窗口 - 第一部分
导入声明和确认对话框类
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UIWindow, UIButton, UITextEntryLine, UIHorizontalSlider
from pygame_gui.core import ObjectID
from typing import Dict, Optional, Callable
from game.scenes.styles.theme import Theme
from game.scenes.styles.fonts import font_manager
from game.scenes.components.button_component import ModernButton
from game.scenes.components.input_component import ModernInput, PasswordStrengthIndicator
from game.scenes.components.message_component import MessageManager

class ConfirmationDialog:
    """确认对话框"""
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager, 
                 title: str, message: str, confirm_text: str = "Confirmar", 
                 cancel_text: str = "Cancelar"):
        """
        初始化确认对话框
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            ui_manager: pygame_gui UI管理器
            title: 对话框标题
            message: 确认消息
            confirm_text: 确认按钮文本
            cancel_text: 取消按钮文本
        """
        self.ui_manager = ui_manager
        self.title = title
        self.message = message
        
        # 对话框尺寸
        self.dialog_width = 400
        self.dialog_height = 200
        
        # 计算居中位置
        dialog_x = (screen_width - self.dialog_width) // 2
        dialog_y = (screen_height - self.dialog_height) // 2
        
        # 创建对话框窗口
        self.window = UIWindow(
            rect=pygame.Rect(dialog_x, dialog_y, self.dialog_width, self.dialog_height),
            manager=ui_manager,
            window_display_title=title,
            object_id=ObjectID('#confirmation_dialog'),
            resizable=False
        )
        
        # 状态
        self.is_visible = True
        self.result = None  # None, True (确认), False (取消)
        
        # 创建UI元素
        self._create_ui_elements(confirm_text, cancel_text)
    
    def _create_ui_elements(self, confirm_text: str, cancel_text: str):
        """创建UI元素"""
        # 消息标签
        self.message_label = UILabel(
            relative_rect=pygame.Rect(20, 20, self.dialog_width - 40, 100),
            text=self.message,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#dialog_message')
        )
        
        # 按钮区域
        button_width = 120
        button_height = 40
        button_y = self.dialog_height - 70
        
        # 取消按钮
        cancel_x = (self.dialog_width // 2) - button_width - 10
        self.cancel_button = UIButton(
            relative_rect=pygame.Rect(cancel_x, button_y, button_width, button_height),
            text=cancel_text,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#dialog_cancel')
        )
        
        # 确认按钮
        confirm_x = (self.dialog_width // 2) + 10
        self.confirm_button = UIButton(
            relative_rect=pygame.Rect(confirm_x, button_y, button_width, button_height),
            text=confirm_text,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#dialog_confirm')
        )
    
    def handle_event(self, event):
        """处理事件"""
        if not self.is_visible:
            return None
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.confirm_button:
                self.result = True
                self.close()
                return "confirm"
            elif event.ui_element == self.cancel_button:
                self.result = False
                self.close()
                return "cancel"
        
        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self.result = False
                self.close()
                return "cancel"
        
        return None
    
    def close(self):
        """关闭对话框"""
        if self.is_visible:
            self.is_visible = False
            if self.window:
                self.window.kill()
    
    def cleanup(self):
        """清理资源"""
        if self.window:
            self.window.kill()

class ModernSettingsWindow:
    """
    现代化设置窗口
    包含用户设置、游戏设置、退出功能
    """
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager, 
                 user_data: Dict, message_manager: MessageManager, 
                 database_manager=None, auth_manager=None):
        """
        初始化设置窗口
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            ui_manager: pygame_gui UI管理器
            user_data: 用户数据
            message_manager: 消息管理器
            database_manager: 数据库管理器
            auth_manager: 认证管理器
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        self.user_data = user_data
        self.message_manager = message_manager
        self.database_manager = database_manager
        self.auth_manager = auth_manager
        
        # 窗口尺寸
        self.window_width = min(800, int(screen_width * 0.8))
        self.window_height = min(700, int(screen_height * 0.85))
        
        # 计算居中位置
        window_x = (screen_width - self.window_width) // 2
        window_y = (screen_height - self.window_height) // 2
        
        # 创建主窗口
        self.window = UIWindow(
            rect=pygame.Rect(window_x, window_y, self.window_width, self.window_height),
            manager=ui_manager,
            window_display_title="",
            object_id=ObjectID('#modern_settings_window'),
            resizable=False
        )
        
        # 状态管理
        self.is_visible = True
        self.current_tab = "user"  # user, game, about
        self.scale_factor = min(screen_width / 1920, screen_height / 1080)
        self.confirmation_dialog = None
        self.pending_action = ""
        
        # 设置数据
        self.settings = {
            'master_volume': 0.8,
            'music_volume': 0.7,
            'sfx_volume': 0.6,
            'fullscreen': False,
            'vsync': True,
            'auto_save': True,
            'language': 'es'
        }
        
        # UI元素
        self.modern_buttons = []
        self.modern_inputs = []
        self.password_strength = None
        
        # 回调函数
        self.on_close: Optional[Callable] = None
        self.on_logout: Optional[Callable] = None
        self.on_exit_game: Optional[Callable] = None
        
        # 创建UI
        self._create_modern_ui()
        
        print(f"⚙️ 创建设置窗口 - 用户: {self.user_data.get('username', 'Unknown')}")
    
    def _create_modern_ui(self):
        """创建现代化UI"""
        # 创建标题栏
        self._create_title_bar()
        
        # 创建标签页
        self._create_tab_bar()
        
        # 创建内容区域
        self._create_content_area()
        
        # 创建底部按钮
        self._create_bottom_buttons()
    
    def _create_title_bar(self):
        """创建标题栏"""
        title_rect = pygame.Rect(0, 0, self.window_width, 60)
        self.title_panel = UIPanel(
            relative_rect=title_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#settings_title_panel')
        )
        
        # 标题
        self.title_label = UILabel(
            relative_rect=pygame.Rect(20, 15, 300, 30),
            text="Configuración",
            manager=self.ui_manager,
            container=self.title_panel,
            object_id=ObjectID('#settings_title')
        )
        
        # 用户信息
        username = self.user_data.get('username', 'Usuario')
        user_info_text = f"Usuario: {username}"
        self.user_info_label = UILabel(
            relative_rect=pygame.Rect(self.window_width - 250, 15, 200, 30),
            text=user_info_text,
            manager=self.ui_manager,
            container=self.title_panel,
            object_id=ObjectID('#user_info')
        )
        
        # 关闭按钮
        close_rect = pygame.Rect(self.window_width - 50, 10, 40, 40)
        self.close_button = ModernButton(
            rect=close_rect,
            text="✕",
            button_type="text",
            font_size="lg"
        )
        self.modern_buttons.append(self.close_button)
    
    def _create_tab_bar(self):
        """创建标签页栏"""
        tab_rect = pygame.Rect(10, 70, self.window_width - 20, 50)
        self.tab_panel = UIPanel(
            relative_rect=tab_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#tab_panel')
        )
        
        # 标签页按钮
        tab_width = 150
        tab_height = 40
        tab_y = 5
        
        # 用户设置标签
        user_tab_rect = pygame.Rect(20, tab_y, tab_width, tab_height)
        self.user_tab_button = ModernButton(
            rect=user_tab_rect,
            text="Usuario",
            button_type="primary" if self.current_tab == "user" else "secondary",
            font_size="md"
        )
        self.modern_buttons.append(self.user_tab_button)
        
        # 游戏设置标签
        game_tab_rect = pygame.Rect(180, tab_y, tab_width, tab_height)
        self.game_tab_button = ModernButton(
            rect=game_tab_rect,
            text="Juego",
            button_type="primary" if self.current_tab == "game" else "secondary",
            font_size="md"
        )
        self.modern_buttons.append(self.game_tab_button)
        
        # 关于标签
        about_tab_rect = pygame.Rect(340, tab_y, tab_width, tab_height)
        self.about_tab_button = ModernButton(
            rect=about_tab_rect,
            text="Acerca de",
            button_type="primary" if self.current_tab == "about" else "secondary",
            font_size="md"
        )
        self.modern_buttons.append(self.about_tab_button)
    
    def _create_content_area(self):
        """创建内容区域"""
        content_rect = pygame.Rect(10, 130, self.window_width - 20, self.window_height - 220)
        self.content_panel = UIPanel(
            relative_rect=content_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#content_panel')
        )
        
        # 根据当前标签页创建内容
        self._update_content_area()
    
    def _create_bottom_buttons(self):
        """创建底部按钮"""
        button_y = self.window_height - 60
        
        # 退出游戏按钮
        exit_game_rect = pygame.Rect(self.window_width - 160, button_y, 140, 40)
        self.exit_game_button = ModernButton(
            rect=exit_game_rect,
            text="Salir del Juego",
            button_type="secondary",
            font_size="md"
        )
        self.modern_buttons.append(self.exit_game_button)

    def _update_content_area(self):
        """更新内容区域"""
        # 清除现有的输入组件
        for input_comp in self.modern_inputs:
            input_comp.kill()
        self.modern_inputs.clear()
        
        # 移除与标签页相关的按钮（保留固定按钮）
        fixed_buttons = [self.close_button, self.user_tab_button, 
                        self.game_tab_button, self.about_tab_button, self.exit_game_button]
        self.modern_buttons = [btn for btn in self.modern_buttons if btn in fixed_buttons]
        
        if self.current_tab == "user":
            self._create_user_settings()
        elif self.current_tab == "game":
            self._create_game_settings()
        elif self.current_tab == "about":
            self._create_about_content()
    
    def _create_user_settings(self):
        """创建用户设置内容"""
        # 修改密码区域
        password_title = UILabel(
            relative_rect=pygame.Rect(20, 20, 300, 30),
            text="Cambiar Contraseña",
            manager=self.ui_manager,
            container=self.content_panel,
            object_id=ObjectID('#password_title')
        )
        
        # 当前密码输入
        current_password_input = ModernInput(
            rect=pygame.Rect(20, 60, 300, 40),
            placeholder="Contraseña actual",
            label="Contraseña Actual:",
            is_password=True,
            ui_manager=self.ui_manager
        )
        self.modern_inputs.append(current_password_input)
        
        # 新密码输入
        new_password_input = ModernInput(
            rect=pygame.Rect(20, 130, 300, 40),
            placeholder="Nueva contraseña",
            label="Nueva Contraseña:",
            is_password=True,
            ui_manager=self.ui_manager
        )
        self.modern_inputs.append(new_password_input)
        
        # 密码强度指示器
        self.password_strength = PasswordStrengthIndicator(new_password_input)
        
        # 确认新密码输入
        confirm_password_input = ModernInput(
            rect=pygame.Rect(20, 220, 300, 40),
            placeholder="Confirmar nueva contraseña",
            label="Confirmar Contraseña:",
            is_password=True,
            ui_manager=self.ui_manager
        )
        self.modern_inputs.append(confirm_password_input)
        
        # 修改密码按钮
        change_password_rect = pygame.Rect(20, 290, 150, 40)
        self.change_password_button = ModernButton(
            rect=change_password_rect,
            text="Cambiar Contraseña",
            button_type="primary",
            font_size="md"
        )
        self.modern_buttons.append(self.change_password_button)
        
        # 账户信息区域
        account_title = UILabel(
            relative_rect=pygame.Rect(380, 20, 300, 30),
            text="Información de la Cuenta",
            manager=self.ui_manager,
            container=self.content_panel,
            object_id=ObjectID('#account_title')
        )
        
        # 显示账户信息
        username = self.user_data.get('username', 'N/A')
        email = self.user_data.get('email', 'N/A')
        created_at = self.user_data.get('created_at', 'N/A')
        
        account_info = f"""Usuario: {username}
Email: {email}
Fecha de registro: {created_at}
Monedas: {self.user_data.get('coins', 0)}
Cartas totales: {len(self.user_data.get('card_collection', []))}"""
        
        account_info_label = UILabel(
            relative_rect=pygame.Rect(380, 60, 350, 150),
            text=account_info,
            manager=self.ui_manager,
            container=self.content_panel,
            object_id=ObjectID('#account_info')
        )
        
        # 关闭sesión按钮
        logout_rect = pygame.Rect(380, 230, 150, 40)
        self.logout_button = ModernButton(
            rect=logout_rect,
            text="Cerrar Sesión",
            button_type="secondary",
            font_size="md"
        )
        self.modern_buttons.append(self.logout_button)
        
        # 删除账户按钮
        delete_account_rect = pygame.Rect(540, 230, 150, 40)
        self.delete_account_button = ModernButton(
            rect=delete_account_rect,
            text="Eliminar Cuenta",
            button_type="secondary",
            font_size="md"
        )
        self.modern_buttons.append(self.delete_account_button)

    def _create_game_settings(self):
        """创建游戏设置内容"""
        # 音频设置
        audio_title = UILabel(
            relative_rect=pygame.Rect(20, 20, 300, 30),
            text="Configuración de Audio",
            manager=self.ui_manager,
            container=self.content_panel,
            object_id=ObjectID('#audio_title')
        )
        
        # 主音量滑块
        master_volume_label = UILabel(
            relative_rect=pygame.Rect(20, 60, 150, 25),
            text="Volumen Principal:",
            manager=self.ui_manager,
            container=self.content_panel
        )
        
        self.master_volume_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(180, 60, 200, 25),
            start_value=self.settings['master_volume'],
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
            container=self.content_panel
        )
        
        # 音乐音量滑块
        music_volume_label = UILabel(
            relative_rect=pygame.Rect(20, 100, 150, 25),
            text="Volumen de Música:",
            manager=self.ui_manager,
            container=self.content_panel
        )
        
        self.music_volume_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(180, 100, 200, 25),
            start_value=self.settings['music_volume'],
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
            container=self.content_panel
        )
        
        # 音效音量滑块
        sfx_volume_label = UILabel(
            relative_rect=pygame.Rect(20, 140, 150, 25),
            text="Volumen de Efectos:",
            manager=self.ui_manager,
            container=self.content_panel
        )
        
        self.sfx_volume_slider = UIHorizontalSlider(
            relative_rect=pygame.Rect(180, 140, 200, 25),
            start_value=self.settings['sfx_volume'],
            value_range=(0.0, 1.0),
            manager=self.ui_manager,
            container=self.content_panel
        )
        
        # 图形设置
        graphics_title = UILabel(
            relative_rect=pygame.Rect(20, 200, 300, 30),
            text="Configuración Gráfica",
            manager=self.ui_manager,
            container=self.content_panel,
            object_id=ObjectID('#graphics_title')
        )
        
        # 全屏按钮
        fullscreen_rect = pygame.Rect(20, 240, 180, 40)
        fullscreen_text = "Desactivar Pantalla Completa" if self.settings['fullscreen'] else "Activar Pantalla Completa"
        self.fullscreen_button = ModernButton(
            rect=fullscreen_rect,
            text=fullscreen_text,
            button_type="secondary",
            font_size="sm"
        )
        self.modern_buttons.append(self.fullscreen_button)
        
        # VSync按钮
        vsync_rect = pygame.Rect(210, 240, 120, 40)
        vsync_text = "Desactivar VSync" if self.settings['vsync'] else "Activar VSync"
        self.vsync_button = ModernButton(
            rect=vsync_rect,
            text=vsync_text,
            button_type="secondary",
            font_size="sm"
        )
        self.modern_buttons.append(self.vsync_button)
        
        # 其他设置
        other_title = UILabel(
            relative_rect=pygame.Rect(400, 20, 300, 30),
            text="Otras Configuraciones",
            manager=self.ui_manager,
            container=self.content_panel,
            object_id=ObjectID('#other_title')
        )
        
        # 自动保存按钮
        auto_save_rect = pygame.Rect(400, 60, 150, 40)
        auto_save_text = "Desactivar Auto-guardado" if self.settings['auto_save'] else "Activar Auto-guardado"
        self.auto_save_button = ModernButton(
            rect=auto_save_rect,
            text=auto_save_text,
            button_type="secondary",
            font_size="sm"
        )
        self.modern_buttons.append(self.auto_save_button)
        
        # 重置设置按钮
        reset_settings_rect = pygame.Rect(400, 120, 150, 40)
        self.reset_settings_button = ModernButton(
            rect=reset_settings_rect,
            text="Restablecer Configuración",
            button_type="secondary",
            font_size="sm"
        )
        self.modern_buttons.append(self.reset_settings_button)
        
        # 应用设置按钮
        apply_settings_rect = pygame.Rect(400, 180, 150, 40)
        self.apply_settings_button = ModernButton(
            rect=apply_settings_rect,
            text="Aplicar Cambios",
            button_type="primary",
            font_size="md"
        )
        self.modern_buttons.append(self.apply_settings_button)
    
    def _create_about_content(self):
        """创建关于内容"""
        # 游戏信息
        game_info = """Pokémon TCG - Edición de Coleccionista

Versión: 1.0.0
Desarrollado con: Python & Pygame

Características:
• Colecciona cartas Pokémon auténticas
• Sistema de combate estratégico
• Intercambio con otros entrenadores
• Torneos y eventos especiales

© 2024 - Todos los derechos reservados
Pokémon es una marca registrada de Nintendo/Game Freak"""
        
        info_label = UILabel(
            relative_rect=pygame.Rect(20, 20, self.window_width - 60, 300),
            text=game_info,
            manager=self.ui_manager,
            container=self.content_panel,
            object_id=ObjectID('#game_info')
        )
        
        # créditos
        credits_title = UILabel(
            relative_rect=pygame.Rect(20, 340, 300, 30),
            text="Créditos del Desarrollo",
            manager=self.ui_manager,
            container=self.content_panel,
            object_id=ObjectID('#credits_title')
        )
        
        credits_text = """Programación: Equipo de Desarrollo
Diseño de UI: Departamento de Arte
Datos de Cartas: PokeAPI & Pocket Hub
Música y Sonidos: Biblioteca de Audio Libre

Agradecimientos especiales a la comunidad
de desarrolladores de Pokémon por su apoyo."""
        
        credits_label = UILabel(
            relative_rect=pygame.Rect(20, 380, self.window_width - 60, 150),
            text=credits_text,
            manager=self.ui_manager,
            container=self.content_panel,
            object_id=ObjectID('#credits_info')
        )

    def handle_event(self, event):
        """处理事件"""
        if not self.is_visible:
            return None
        
        # 处理确认对话框事件
        if self.confirmation_dialog:
            result = self.confirmation_dialog.handle_event(event)
            if result == "confirm":
                dialog_result = self._handle_confirmation_result(True)
                self.confirmation_dialog = None
                return dialog_result
            elif result == "cancel":
                self.confirmation_dialog = None
                return "dialog_cancelled"
        
        # 处理输入组件事件
        for input_comp in self.modern_inputs:
            input_comp.handle_event(event)
        
        # 更新密码强度
        if self.password_strength and len(self.modern_inputs) >= 2:
            new_password = self.modern_inputs[1].get_text()  # 新密码输入框
            self.password_strength.update_strength(new_password)
        
        # 更新按钮悬停状态
        mouse_pos = pygame.mouse.get_pos()
        for button in self.modern_buttons:
            window_pos = (
                mouse_pos[0] - self.window.rect.x,
                mouse_pos[1] - self.window.rect.y
            )
            button.update_hover(window_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            window_pos = (
                mouse_pos[0] - self.window.rect.x,
                mouse_pos[1] - self.window.rect.y
            )
            
            for button in self.modern_buttons:
                if button.rect.collidepoint(window_pos):
                    button.trigger_flash()
                    return self._handle_button_click(button)
        
        # 处理滑块事件
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if self.current_tab == "game":
                if hasattr(self, 'master_volume_slider') and event.ui_element == self.master_volume_slider:
                    self.settings['master_volume'] = event.value
                elif hasattr(self, 'music_volume_slider') and event.ui_element == self.music_volume_slider:
                    self.settings['music_volume'] = event.value
                elif hasattr(self, 'sfx_volume_slider') and event.ui_element == self.sfx_volume_slider:
                    self.settings['sfx_volume'] = event.value
        
        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self.close()
                return "close"
        
        return None
    
    def _handle_button_click(self, button):
        """处理按钮点击"""
        if button == self.close_button:
            self.close()
            return "close"
        
        # 标签页按钮
        elif button == self.user_tab_button:
            self._switch_tab("user")
            return "tab_user"
        elif button == self.game_tab_button:
            self._switch_tab("game")
            return "tab_game"
        elif button == self.about_tab_button:
            self._switch_tab("about")
            return "tab_about"
        
        # 用户设置按钮
        elif button == getattr(self, 'change_password_button', None):
            return self._handle_change_password()
        elif button == getattr(self, 'logout_button', None):
            self._show_confirmation_dialog(
                "Cerrar Sesión",
                "¿Estás seguro de que quieres cerrar sesión?",
                "logout"
            )
            return "logout_confirm"
        elif button == getattr(self, 'delete_account_button', None):
            self._show_confirmation_dialog(
                "Eliminar Cuenta",
                "¿Estás seguro de que quieres eliminar tu cuenta?\nEsta acción no se puede deshacer.",
                "delete_account"
            )
            return "delete_account_confirm"
        
        # 游戏设置按钮
        elif button == getattr(self, 'fullscreen_button', None):
            self._toggle_fullscreen()
            return "toggle_fullscreen"
        elif button == getattr(self, 'vsync_button', None):
            self._toggle_vsync()
            return "toggle_vsync"
        elif button == getattr(self, 'auto_save_button', None):
            self._toggle_auto_save()
            return "toggle_auto_save"
        elif button == getattr(self, 'reset_settings_button', None):
            self._show_confirmation_dialog(
                "Restablecer Configuración",
                "¿Quieres restablecer todas las configuraciones a los valores predeterminados?",
                "reset_settings"
            )
            return "reset_settings_confirm"
        elif button == getattr(self, 'apply_settings_button', None):
            self._apply_game_settings()
            return "apply_settings"
        
        # 退出游戏按钮
        elif button == self.exit_game_button:
            self._show_confirmation_dialog(
                "Salir del Juego",
                "¿Estás seguro de que quieres salir del juego?",
                "exit_game"
            )
            return "exit_game_confirm"
        
        return None
    
    def _switch_tab(self, tab_name: str):
        """切换标签页"""
        self.current_tab = tab_name
        
        # 更新标签页按钮状态
        self.user_tab_button.button_type = "primary" if tab_name == "user" else "secondary"
        self.game_tab_button.button_type = "primary" if tab_name == "game" else "secondary"
        self.about_tab_button.button_type = "primary" if tab_name == "about" else "secondary"
        
        # 更新内容区域
        self._update_content_area()
    
    def _handle_change_password(self):
        """处理修改密码"""
        if len(self.modern_inputs) < 3:
            self.message_manager.show_message("Error interno: faltan campos de entrada", "error")
            return "password_change_error"
        
        current_password = self.modern_inputs[0].get_text()
        new_password = self.modern_inputs[1].get_text()
        confirm_password = self.modern_inputs[2].get_text()
        
        # 验证输入
        if not current_password:
            self.message_manager.show_message("Ingresa tu contraseña actual", "warning")
            return "password_change_error"
        
        if not new_password:
            self.message_manager.show_message("Ingresa una nueva contraseña", "warning")
            return "password_change_error"
        
        if new_password != confirm_password:
            self.message_manager.show_message("Las contraseñas no coinciden", "error")
            return "password_change_error"
        
        if len(new_password) < 6:
            self.message_manager.show_message("La contraseña debe tener al menos 6 caracteres", "warning")
            return "password_change_error"
        
        # 验证当前密码并更新
        if self.auth_manager:
            try:
                if self.auth_manager.verify_password(self.user_data['username'], current_password):
                    success = self.auth_manager.change_password(
                        self.user_data['username'], 
                        current_password, 
                        new_password
                    )
                    
                    if success:
                        # 清空输入框
                        for input_comp in self.modern_inputs:
                            input_comp.clear()
                        
                        self.message_manager.show_message("Contraseña cambiada exitosamente", "success")
                        return "password_changed"
                    else:
                        self.message_manager.show_message("Error al cambiar la contraseña", "error")
                        return "password_change_error"
                else:
                    self.message_manager.show_message("Contraseña actual incorrecta", "error")
                    return "password_change_error"
            except Exception as e:
                self.message_manager.show_message(f"Error: {str(e)}", "error")
                return "password_change_error"
        else:
            self.message_manager.show_message("Sistema de autenticación no disponible", "error")
            return "password_change_error"
    
    def _toggle_fullscreen(self):
        """切换全屏状态"""
        self.settings['fullscreen'] = not self.settings['fullscreen']
        button_text = "Desactivar Pantalla Completa" if self.settings['fullscreen'] else "Activar Pantalla Completa"
        self.fullscreen_button.text = button_text
        
        self.message_manager.show_message(
            f"Pantalla completa {'activada' if self.settings['fullscreen'] else 'desactivada'}",
            "info"
        )
    
    def _toggle_vsync(self):
        """切换垂直同步"""
        self.settings['vsync'] = not self.settings['vsync']
        button_text = "Desactivar VSync" if self.settings['vsync'] else "Activar VSync"
        self.vsync_button.text = button_text
        
        self.message_manager.show_message(
            f"VSync {'activado' if self.settings['vsync'] else 'desactivado'}",
            "info"
        )
    
    def _toggle_auto_save(self):
        """切换自动保存"""
        self.settings['auto_save'] = not self.settings['auto_save']
        button_text = "Desactivar Auto-guardado" if self.settings['auto_save'] else "Activar Auto-guardado"
        self.auto_save_button.text = button_text
        
        self.message_manager.show_message(
            f"Auto-guardado {'activado' if self.settings['auto_save'] else 'desactivado'}",
            "info"
        )
    
    def _apply_game_settings(self):
        """应用游戏设置"""
        # 这里可以添加实际的设置应用逻辑
        # 比如调整音量、改变显示模式等
        
        self.message_manager.show_message("Configuración aplicada exitosamente", "success")
        print(f"⚙️ 应用游戏设置: {self.settings}")
    
    def _show_confirmation_dialog(self, title: str, message: str, action: str):
        """显示确认对话框"""
        self.confirmation_dialog = ConfirmationDialog(
            self.screen_width, self.screen_height, self.ui_manager,
            title, message
        )
        self.pending_action = action

    def _handle_confirmation_result(self, confirmed: bool):
        """处理确认对话框结果"""
        if not confirmed:
            return "confirmation_cancelled"
        
        action = getattr(self, 'pending_action', '')
        
        if action == "logout":
            if self.on_logout:
                self.on_logout()
            self.close()
            return "logout_confirmed"
        
        elif action == "delete_account":
            # 删除账户逻辑
            if self.database_manager and self.auth_manager:
                try:
                    success = self.auth_manager.delete_user(self.user_data['username'])
                    if success:
                        self.message_manager.show_message("Cuenta eliminada exitosamente", "success")
                        if self.on_logout:
                            self.on_logout()
                        self.close()
                        return "account_deleted"
                    else:
                        self.message_manager.show_message("Error al eliminar la cuenta", "error")
                        return "delete_account_error"
                except Exception as e:
                    self.message_manager.show_message(f"Error: {str(e)}", "error")
                    return "delete_account_error"
            else:
                self.message_manager.show_message("Sistema no disponible", "error")
                return "delete_account_error"
        
        elif action == "reset_settings":
            self._reset_to_defaults()
            return "settings_reset"
        
        elif action == "exit_game":
            if self.on_exit_game:
                self.on_exit_game()
            return "exit_game_confirmed"
        
        return "confirmation_completed"
    
    def _reset_to_defaults(self):
        """重置设置到默认值"""
        self.settings = {
            'master_volume': 0.8,
            'music_volume': 0.7,
            'sfx_volume': 0.6,
            'fullscreen': False,
            'vsync': True,
            'auto_save': True,
            'language': 'es'
        }
        
        # 更新UI元素
        if self.current_tab == "game":
            if hasattr(self, 'master_volume_slider'):
                self.master_volume_slider.set_current_value(self.settings['master_volume'])
            if hasattr(self, 'music_volume_slider'):
                self.music_volume_slider.set_current_value(self.settings['music_volume'])
            if hasattr(self, 'sfx_volume_slider'):
                self.sfx_volume_slider.set_current_value(self.settings['sfx_volume'])
            
            # 更新按钮文本
            if hasattr(self, 'fullscreen_button'):
                self.fullscreen_button.text = "Activar Pantalla Completa"
            if hasattr(self, 'vsync_button'):
                self.vsync_button.text = "Desactivar VSync"
            if hasattr(self, 'auto_save_button'):
                self.auto_save_button.text = "Desactivar Auto-guardado"
        
        self.message_manager.show_message("Configuración restablecida a valores predeterminados", "success")
    
    def get_settings(self) -> Dict:
        """获取当前设置"""
        return self.settings.copy()
    
    def apply_settings(self, settings: Dict):
        """应用外部设置"""
        self.settings.update(settings)
        
        # 如果当前在游戏设置标签页，更新UI
        if self.current_tab == "game":
            self._update_content_area()

    def update(self, time_delta: float):
        """更新窗口状态"""
        # 更新按钮动画
        for button in self.modern_buttons:
            button.update_animation(time_delta)
        
        # 更新输入组件
        for input_comp in self.modern_inputs:
            input_comp.update(time_delta)
        
        # 更新确认对话框
        if self.confirmation_dialog:
            # 确认对话框由pygame_gui自动更新
            pass
    
    def draw_custom_content(self, screen: pygame.Surface):
        """绘制自定义内容"""
        if not self.is_visible:
            return
        
        # 绘制输入组件背景
        for input_comp in self.modern_inputs:
            input_comp.draw_background(screen, self.scale_factor)
        
        # 绘制密码强度指示器
        if self.password_strength and self.current_tab == "user":
            # 密码强度指示器绘制在新密码输入框下方
            try:
                # 计算指示器位置
                if len(self.modern_inputs) >= 2:
                    new_password_input = self.modern_inputs[1]
                    indicator_y = (self.window.rect.y + 130 + 40 + 
                                 new_password_input.rect.height + 10)
                    
                    # 创建临时指示器对象来绘制
                    temp_indicator = PasswordStrengthIndicator(new_password_input)
                    temp_indicator.visible = self.password_strength.visible
                    temp_indicator.strength = self.password_strength.strength
                    temp_indicator.message = self.password_strength.message
                    
                    temp_indicator.draw(screen, self.scale_factor)
            except Exception as e:
                # 如果绘制密码强度指示器失败，继续执行而不中断
                print(f"警告：密码强度指示器绘制失败: {e}")
        
        # 绘制现代按钮
        self._draw_modern_buttons(screen)
    
    def _draw_modern_buttons(self, screen: pygame.Surface):
        """绘制现代按钮"""
        for button in self.modern_buttons:
            # 转换到屏幕坐标
            screen_rect = pygame.Rect(
                self.window.rect.x + button.rect.x,
                self.window.rect.y + button.rect.y,
                button.rect.width,
                button.rect.height
            )
            
            # 创建临时按钮进行绘制
            temp_button = type(button)(
                screen_rect,
                button.text,
                getattr(button, 'icon', ''),
                button.button_type,
                button.font_size
            )
            temp_button.scale = button.scale
            temp_button.is_hover = button.is_hover
            temp_button.flash = button.flash
            
            temp_button.draw(screen, self.scale_factor)
    
    def close(self):
        """关闭窗口"""
        if self.is_visible:
            self.is_visible = False
            
            # 清理确认对话框
            if self.confirmation_dialog:
                self.confirmation_dialog.cleanup()
                self.confirmation_dialog = None
            
            # 清理输入组件
            for input_comp in self.modern_inputs:
                input_comp.kill()
            
            if self.window:
                self.window.kill()
            
            if self.on_close:
                self.on_close()
            
            print("🚪 关闭设置窗口")
    
    def cleanup(self):
        """清理资源"""
        if self.confirmation_dialog:
            self.confirmation_dialog.cleanup()
        
        for input_comp in self.modern_inputs:
            input_comp.kill()
        
        if self.window:
            self.window.kill()
        
        self.modern_buttons.clear()
        self.modern_inputs.clear()

# 使用示例和测试函数
def test_settings_window():
    """测试设置窗口功能"""
    print("🧪 设置窗口功能测试")
    
    # 模拟用户数据
    test_user_data = {
        'user_id': 1,
        'username': 'test_user',
        'email': 'test@example.com',
        'created_at': '2024-01-01',
        'coins': 1500,
        'card_collection': []
    }
    
    print("设置窗口测试数据准备完成")

if __name__ == "__main__":
    test_settings_window()