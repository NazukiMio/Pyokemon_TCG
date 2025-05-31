"""
现代化窗口基类
为所有现代化窗口提供统一的接口和基础功能
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow
from pygame_gui.core import ObjectID
from abc import ABC, abstractmethod
from typing import Dict, Optional, Callable, Any
from game.scenes.styles.theme import Theme
from game.scenes.styles.fonts import font_manager
from game.scenes.components.message_component import MessageManager

class ModernWindowBase(ABC):
    """
    现代化窗口基类
    所有现代化窗口都应该继承此类
    """
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager,
                 window_title: str = "", window_id: str = "modern_window"):
        """
        初始化现代化窗口基类
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            ui_manager: pygame_gui UI管理器
            window_title: 窗口标题
            window_id: 窗口ID
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        self.window_title = window_title
        self.window_id = window_id
        
        # 窗口状态
        self.is_visible = False
        self.is_modal = False  # 是否为模态窗口
        self.is_resizable = False
        self.window = None
        
        # 缩放和主题
        self.scale_factor = min(screen_width / 1920, screen_height / 1080)
        self.theme = Theme
        
        # 窗口尺寸（子类需要设置）
        self.window_width = 800
        self.window_height = 600
        
        # 回调函数
        self.on_close: Optional[Callable] = None
        self.on_show: Optional[Callable] = None
        self.on_hide: Optional[Callable] = None
        self.on_resize: Optional[Callable] = None
        
        # 事件处理
        self.event_handlers = {}
        
        # 窗口数据
        self.window_data = {}
        
        # 初始化标志
        self._initialized = False
    
    @abstractmethod
    def _calculate_window_size(self):
        """计算窗口尺寸（子类必须实现）"""
        pass
    
    @abstractmethod
    def _create_window_content(self):
        """创建窗口内容（子类必须实现）"""
        pass
    
    def initialize(self):
        """初始化窗口（模板方法）"""
        if self._initialized:
            return True
        
        try:
            # 1. 计算窗口尺寸
            self._calculate_window_size()
            
            # 2. 创建主窗口
            self._create_main_window()
            
            # 3. 创建窗口内容
            self._create_window_content()
            
            # 4. 设置初始状态
            self._setup_initial_state()
            
            self._initialized = True
            self.is_visible = True
            
            if self.on_show:
                self.on_show()
            
            print(f"✅ 窗口初始化完成: {self.window_id}")
            return True
            
        except Exception as e:
            print(f"❌ 窗口初始化失败 {self.window_id}: {e}")
            return False
    
    def _create_main_window(self):
        """创建主窗口"""
        # 计算居中位置
        window_x = (self.screen_width - self.window_width) // 2
        window_y = (self.screen_height - self.window_height) // 2
        
        # 创建pygame_gui窗口
        self.window = UIWindow(
            rect=pygame.Rect(window_x, window_y, self.window_width, self.window_height),
            manager=self.ui_manager,
            window_display_title=self.window_title,
            object_id=ObjectID(f'#{self.window_id}'),
            resizable=self.is_resizable
        )
    
    def _setup_initial_state(self):
        """设置初始状态（子类可以重写）"""
        pass
    
    def show(self):
        """显示窗口"""
        if not self._initialized:
            self.initialize()
        
        if self.window and not self.is_visible:
            self.window.show()
            self.is_visible = True
            
            if self.on_show:
                self.on_show()
            
            print(f"👁️ 窗口显示: {self.window_id}")
    
    def hide(self):
        """隐藏窗口"""
        if self.window and self.is_visible:
            self.window.hide()
            self.is_visible = False
            
            if self.on_hide:
                self.on_hide()
            
            print(f"🙈 窗口隐藏: {self.window_id}")
    
    def close(self):
        """关闭窗口"""
        if self.is_visible:
            self.is_visible = False
            
            if self.window:
                self.window.kill()
                self.window = None
            
            # 清理资源
            self.cleanup()
            
            if self.on_close:
                self.on_close()
            
            print(f"🚪 窗口关闭: {self.window_id}")
    
    def set_modal(self, modal: bool):
        """设置模态状态"""
        self.is_modal = modal
        if modal:
            print(f"🔒 窗口设为模态: {self.window_id}")
        else:
            print(f"🔓 窗口取消模态: {self.window_id}")
    
    def set_data(self, key: str, value: Any):
        """设置窗口数据"""
        self.window_data[key] = value
    
    def get_data(self, key: str, default=None):
        """获取窗口数据"""
        return self.window_data.get(key, default)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """注册事件处理器"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def emit_event(self, event_type: str, event_data: Any = None):
        """触发事件"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event_data)
                except Exception as e:
                    print(f"⚠️ 事件处理器错误 {event_type}: {e}")
    
    def handle_event(self, event):
        """处理事件（基础实现）"""
        if not self.is_visible:
            return None
        
        # 处理窗口关闭事件
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self.close()
                return "close"
        
        # 处理窗口大小调整事件
        if event.type == pygame.VIDEORESIZE:
            self._handle_resize(event.size)
        
        # 子类可以重写此方法添加更多事件处理
        return self._handle_custom_events(event)
    
    def _handle_resize(self, new_size):
        """处理窗口大小调整"""
        old_width, old_height = self.screen_width, self.screen_height
        self.screen_width, self.screen_height = new_size
        
        # 重新计算缩放因子
        self.scale_factor = min(self.screen_width / 1920, self.screen_height / 1080)
        
        if self.on_resize:
            self.on_resize(old_width, old_height, self.screen_width, self.screen_height)
    
    @abstractmethod
    def _handle_custom_events(self, event):
        """处理自定义事件（子类必须实现）"""
        pass
    
    def update(self, time_delta: float):
        """更新窗口状态（基础实现）"""
        if not self.is_visible:
            return
        
        # 子类可以重写此方法添加更多更新逻辑
        self._update_custom_content(time_delta)
    
    @abstractmethod
    def _update_custom_content(self, time_delta: float):
        """更新自定义内容（子类必须实现）"""
        pass
    
    def draw_custom_content(self, screen: pygame.Surface):
        """绘制自定义内容（基础实现）"""
        if not self.is_visible:
            return
        
        # 子类可以重写此方法添加自定义绘制
        self._draw_window_decorations(screen)
        self._draw_custom_elements(screen)
    
    def _draw_window_decorations(self, screen: pygame.Surface):
        """绘制窗口装饰（可选）"""
        pass
    
    @abstractmethod
    def _draw_custom_elements(self, screen: pygame.Surface):
        """绘制自定义元素（子类必须实现）"""
        pass
    
    def get_window_rect(self) -> pygame.Rect:
        """获取窗口矩形"""
        if self.window:
            return self.window.rect
        return pygame.Rect(0, 0, self.window_width, self.window_height)
    
    def get_content_rect(self) -> pygame.Rect:
        """获取内容区域矩形"""
        window_rect = self.get_window_rect()
        # 减去标题栏高度等
        return pygame.Rect(window_rect.x, window_rect.y + 30, 
                         window_rect.width, window_rect.height - 30)
    
    def is_point_inside(self, point: tuple) -> bool:
        """检查点是否在窗口内"""
        if not self.is_visible or not self.window:
            return False
        return self.window.rect.collidepoint(point)
    
    def bring_to_front(self):
        """置顶窗口"""
        if self.window:
            self.window.bring_to_front()
            print(f"⬆️ 窗口置顶: {self.window_id}")
    
    def send_to_back(self):
        """窗口置底"""
        if self.window:
            self.window.send_to_back()
            print(f"⬇️ 窗口置底: {self.window_id}")
    
    def set_position(self, x: int, y: int):
        """设置窗口位置"""
        if self.window:
            self.window.set_position((x, y))
    
    def set_size(self, width: int, height: int):
        """设置窗口大小"""
        self.window_width = width
        self.window_height = height
        
        if self.window and self.is_resizable:
            # pygame_gui窗口大小调整
            self.window.set_dimensions((width, height))
    
    def center_on_screen(self):
        """窗口居中"""
        x = (self.screen_width - self.window_width) // 2
        y = (self.screen_height - self.window_height) // 2
        self.set_position(x, y)
    
    def cleanup(self):
        """清理资源（子类可以重写）"""
        # 清理事件处理器
        self.event_handlers.clear()
        
        # 清理窗口数据
        self.window_data.clear()
        
        # 清理回调
        self.on_close = None
        self.on_show = None
        self.on_hide = None
        self.on_resize = None
        
        print(f"🧹 窗口资源清理: {self.window_id}")
    
    def get_window_info(self) -> Dict:
        """获取窗口信息"""
        return {
            'window_id': self.window_id,
            'title': self.window_title,
            'size': (self.window_width, self.window_height),
            'position': (self.window.rect.x, self.window.rect.y) if self.window else (0, 0),
            'is_visible': self.is_visible,
            'is_modal': self.is_modal,
            'is_resizable': self.is_resizable,
            'scale_factor': self.scale_factor,
            'data_keys': list(self.window_data.keys())
        }
    
    def __str__(self):
        return f"ModernWindow({self.window_id}, visible={self.is_visible})"
    
    def __repr__(self):
        return f"ModernWindow(id='{self.window_id}', title='{self.window_title}', size=({self.window_width}, {self.window_height}))"

class ModernWindowManager:
    """现代化窗口管理器"""
    
    def __init__(self):
        self.windows = {}  # window_id -> ModernWindowBase
        self.window_stack = []  # Z-order stack
        self.modal_window = None
        
    def register_window(self, window: ModernWindowBase):
        """注册窗口"""
        self.windows[window.window_id] = window
        
        # 设置关闭回调
        original_on_close = window.on_close
        
        def on_close_wrapper():
            self.unregister_window(window.window_id)
            if original_on_close:
                original_on_close()
        
        window.on_close = on_close_wrapper
        print(f"📝 注册窗口: {window.window_id}")
    
    def unregister_window(self, window_id: str):
        """注销窗口"""
        if window_id in self.windows:
            window = self.windows[window_id]
            
            # 从栈中移除
            if window in self.window_stack:
                self.window_stack.remove(window)
            
            # 如果是模态窗口，清除模态状态
            if self.modal_window == window:
                self.modal_window = None
            
            del self.windows[window_id]
            print(f"📝 注销窗口: {window_id}")
    
    def show_window(self, window_id: str):
        """显示窗口"""
        if window_id in self.windows:
            window = self.windows[window_id]
            window.show()
            
            # 添加到栈顶
            if window in self.window_stack:
                self.window_stack.remove(window)
            self.window_stack.append(window)
            
            # 处理模态窗口
            if window.is_modal:
                self.modal_window = window
    
    def hide_window(self, window_id: str):
        """隐藏窗口"""
        if window_id in self.windows:
            window = self.windows[window_id]
            window.hide()
            
            # 从栈中移除
            if window in self.window_stack:
                self.window_stack.remove(window)
            
            # 如果是模态窗口，清除模态状态
            if self.modal_window == window:
                self.modal_window = None
    
    def close_window(self, window_id: str):
        """关闭窗口"""
        if window_id in self.windows:
            self.windows[window_id].close()
    
    def close_all_windows(self):
        """关闭所有窗口"""
        window_ids = list(self.windows.keys())
        for window_id in window_ids:
            self.close_window(window_id)
    
    def get_window(self, window_id: str) -> Optional[ModernWindowBase]:
        """获取窗口"""
        return self.windows.get(window_id)
    
    def is_window_open(self, window_id: str) -> bool:
        """检查窗口是否打开"""
        window = self.get_window(window_id)
        return window is not None and window.is_visible
    
    def get_top_window(self) -> Optional[ModernWindowBase]:
        """获取顶层窗口"""
        return self.window_stack[-1] if self.window_stack else None
    
    def handle_event(self, event):
        """处理事件"""
        # 如果有模态窗口，只处理模态窗口的事件
        if self.modal_window and self.modal_window.is_visible:
            return self.modal_window.handle_event(event)
        
        # 从顶层窗口开始处理事件
        for window in reversed(self.window_stack):
            if window.is_visible:
                result = window.handle_event(event)
                if result:
                    return result
        
        return None
    
    def update(self, time_delta: float):
        """更新所有窗口"""
        for window in self.window_stack:
            if window.is_visible:
                window.update(time_delta)
    
    def draw(self, screen: pygame.Surface):
        """绘制所有窗口的自定义内容"""
        for window in self.window_stack:
            if window.is_visible:
                window.draw_custom_content(screen)
    
    def get_window_count(self) -> int:
        """获取窗口数量"""
        return len(self.windows)
    
    def get_visible_window_count(self) -> int:
        """获取可见窗口数量"""
        return sum(1 for window in self.windows.values() if window.is_visible)
    
    def get_window_list(self) -> list:
        """获取窗口列表"""
        return list(self.windows.keys())

# 全局窗口管理器实例
_global_window_manager = None

def get_window_manager() -> ModernWindowManager:
    """获取全局窗口管理器"""
    global _global_window_manager
    if _global_window_manager is None:
        _global_window_manager = ModernWindowManager()
        print("✅ 创建全局窗口管理器")
    return _global_window_manager

def reset_window_manager():
    """重置全局窗口管理器"""
    global _global_window_manager
    if _global_window_manager:
        _global_window_manager.close_all_windows()
    _global_window_manager = ModernWindowManager()
    print("🔄 重置全局窗口管理器")

# 装饰器：自动注册窗口
def auto_register_window(window_manager=None):
    """自动注册窗口的装饰器"""
    def decorator(window_class):
        original_init = window_class.__init__
        
        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            
            # 自动注册到窗口管理器
            manager = window_manager or get_window_manager()
            manager.register_window(self)
        
        window_class.__init__ = new_init
        return window_class
    
    return decorator

# 窗口工厂类
class WindowFactory:
    """窗口工厂，用于创建不同类型的窗口"""
    
    _window_types = {}
    
    @classmethod
    def register_window_type(cls, window_type: str, window_class):
        """注册窗口类型"""
        cls._window_types[window_type] = window_class
        print(f"📝 注册窗口类型: {window_type}")
    
    @classmethod
    def create_window(cls, window_type: str, *args, **kwargs) -> Optional[ModernWindowBase]:
        """创建窗口"""
        if window_type in cls._window_types:
            window_class = cls._window_types[window_type]
            try:
                window = window_class(*args, **kwargs)
                
                # 自动注册到全局管理器
                get_window_manager().register_window(window)
                
                print(f"✅ 创建窗口: {window_type}")
                return window
                
            except Exception as e:
                print(f"❌ 创建窗口失败 {window_type}: {e}")
                return None
        else:
            print(f"❌ 未知窗口类型: {window_type}")
            return None
    
    @classmethod
    def get_registered_types(cls) -> list:
        """获取已注册的窗口类型"""
        return list(cls._window_types.keys())

# 窗口状态管理器
class WindowStateManager:
    """窗口状态管理器，用于保存和恢复窗口状态"""
    
    def __init__(self):
        self.saved_states = {}
    
    def save_window_state(self, window: ModernWindowBase, state_name: str):
        """保存窗口状态"""
        try:
            state = {
                'window_id': window.window_id,
                'position': (window.window.rect.x, window.window.rect.y) if window.window else (0, 0),
                'size': (window.window_width, window.window_height),
                'is_visible': window.is_visible,
                'is_modal': window.is_modal,
                'window_data': window.window_data.copy()
            }
            
            self.saved_states[state_name] = state
            print(f"💾 保存窗口状态: {state_name}")
            return True
            
        except Exception as e:
            print(f"❌ 保存窗口状态失败 {state_name}: {e}")
            return False
    
    def restore_window_state(self, window: ModernWindowBase, state_name: str):
        """恢复窗口状态"""
        if state_name not in self.saved_states:
            print(f"❌ 未找到窗口状态: {state_name}")
            return False
        
        try:
            state = self.saved_states[state_name]
            
            # 恢复位置和大小
            window.set_position(*state['position'])
            window.set_size(*state['size'])
            
            # 恢复可见性
            if state['is_visible']:
                window.show()
            else:
                window.hide()
            
            # 恢复模态状态
            window.set_modal(state['is_modal'])
            
            # 恢复窗口数据
            window.window_data.update(state['window_data'])
            
            print(f"🔄 恢复窗口状态: {state_name}")
            return True
            
        except Exception as e:
            print(f"❌ 恢复窗口状态失败 {state_name}: {e}")
            return False
    
    def delete_saved_state(self, state_name: str):
        """删除保存的状态"""
        if state_name in self.saved_states:
            del self.saved_states[state_name]
            print(f"🗑️ 删除窗口状态: {state_name}")
    
    def get_saved_states(self) -> list:
        """获取保存的状态列表"""
        return list(self.saved_states.keys())

# 示例实现：消息对话框窗口
class MessageDialogWindow(ModernWindowBase):
    """消息对话框窗口示例"""
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager,
                 message: str, title: str = "消息", dialog_type: str = "info"):
        self.message = message
        self.dialog_type = dialog_type
        self.result = None
        
        super().__init__(screen_width, screen_height, ui_manager, title, "message_dialog")
    
    def _calculate_window_size(self):
        self.window_width = 400
        self.window_height = 200
    
    def _create_window_content(self):
        from pygame_gui.elements import UILabel, UIButton
        
        # 消息标签
        self.message_label = UILabel(
            relative_rect=pygame.Rect(20, 20, self.window_width - 40, 100),
            text=self.message,
            manager=self.ui_manager,
            container=self.window
        )
        
        # 确定按钮
        self.ok_button = UIButton(
            relative_rect=pygame.Rect(self.window_width - 120, self.window_height - 60, 100, 40),
            text="确定",
            manager=self.ui_manager,
            container=self.window
        )
    
    def _handle_custom_events(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.ok_button:
                self.result = "ok"
                self.close()
                return "ok"
        return None
    
    def _update_custom_content(self, time_delta: float):
        pass
    
    def _draw_custom_elements(self, screen: pygame.Surface):
        pass

# 注册示例窗口类型
WindowFactory.register_window_type("message_dialog", MessageDialogWindow)

# 便捷函数
def show_message_dialog(message: str, title: str = "消息", dialog_type: str = "info"):
    """显示消息对话框"""
    try:
        import pygame
        screen = pygame.display.get_surface()
        if screen:
            screen_width, screen_height = screen.get_size()
            
            # 这里需要获取UI管理器，实际使用时需要传入
            dialog = WindowFactory.create_window(
                "message_dialog", 
                screen_width, screen_height, None,  # ui_manager需要传入
                message, title, dialog_type
            )
            
            if dialog:
                get_window_manager().show_window(dialog.window_id)
                return dialog
    except Exception as e:
        print(f"❌ 显示消息对话框失败: {e}")
    
    return None

def close_all_windows():
    """关闭所有窗口的便捷函数"""
    get_window_manager().close_all_windows()

def get_window_by_id(window_id: str) -> Optional[ModernWindowBase]:
    """根据ID获取窗口的便捷函数"""
    return get_window_manager().get_window(window_id)

# 测试函数
def test_window_system():
    """测试窗口系统"""
    print("🧪 窗口系统测试")
    
    # 测试窗口管理器
    manager = get_window_manager()
    print(f"窗口管理器创建: {manager}")
    
    # 测试窗口工厂
    registered_types = WindowFactory.get_registered_types()
    print(f"已注册窗口类型: {registered_types}")
    
    print("✅ 窗口系统测试完成")

if __name__ == "__main__":
    test_window_system()