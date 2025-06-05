"""
主题化窗口组件 - ThemedUIWindow
继承pygame_gui的UIWindow，自动应用自定义主题样式
"""

import pygame
import pygame_gui
from pygame_gui.elements import UIWindow
from pygame_gui.core import ObjectID
from typing import Union, Optional, Dict, Any


class ThemedUIWindow(UIWindow):
    """
    主题化UI窗口类
    
    继承pygame_gui的UIWindow，在创建后自动为标题栏和关闭按钮
    设置自定义的object_id，使其能够匹配主题文件中的样式。
    
    使用示例:
        window = ThemedUIWindow(
            rect=pygame.Rect(100, 100, 800, 600),
            manager=ui_manager,
            window_display_title="我的窗口",
            theme_class="@my_window"  # 可选，默认为@themed_window
        )
    """
    
    def __init__(self, 
                 rect: pygame.Rect,
                 manager,
                 window_display_title: str = "",
                 object_id: Optional[Union[ObjectID, str]] = None,
                 resizable: bool = True,
                 theme_class: str = "@themed_window",
                 **kwargs):
        """
        初始化主题化窗口
        
        Args:
            rect: 窗口矩形区域
            manager: pygame_gui UI管理器
            window_display_title: 窗口标题
            object_id: 自定义object_id（可选）
            resizable: 是否可调整大小
            theme_class: 主题类名，默认为"@themed_window"
            **kwargs: 其他传递给UIWindow的参数
        """
        
        # 设置窗口本身的object_id
        if object_id is None:
            object_id = ObjectID(class_id=theme_class)
        elif isinstance(object_id, str):
            object_id = ObjectID(class_id=theme_class, object_id=object_id)
        
        # 存储主题类名，用于子元素
        self.theme_class = theme_class
        
        # 调用父类初始化 - 确保所有内部属性正确创建
        super().__init__(
            rect=rect,
            manager=manager,
            window_display_title=window_display_title,
            object_id=object_id,
            resizable=resizable,
            **kwargs
        )
        
        # 在父类完全初始化后，安全地应用主题样式
        self._apply_themed_styles()
        
        print(f"✅ 主题窗口创建完成: {theme_class}")
    
    def _apply_themed_styles(self):
        """
        安全地应用主题样式到窗口的子元素
        
        为标题栏和关闭按钮设置匹配主题文件的object_id
        """
        try:
            # 设置标题栏的主题样式
            if hasattr(self, 'title_bar') and self.title_bar is not None:
                self._apply_title_bar_theme()
            
            # 设置关闭按钮的主题样式  
            if hasattr(self, 'close_window_button') and self.close_window_button is not None:
                self._apply_close_button_theme()
            
            print(f"🎨 主题样式应用成功: {self.theme_class}")
            
        except Exception as e:
            print(f"⚠️ 应用主题样式时出错: {e}")
            # 不抛出异常，确保窗口仍然可用
    
    def _apply_title_bar_theme(self):
        """应用标题栏主题"""
        try:
            title_bar_class = f"{self.theme_class}.title_bar"
            
            # 检查set_object_id方法是否存在
            if hasattr(self.title_bar, 'set_object_id'):
                self.title_bar.set_object_id(ObjectID(class_id=title_bar_class))
                print(f"🏷️ 标题栏样式设置: {title_bar_class}")
            else:
                # 备用方法：直接设置most_specific_combined_id
                self.title_bar.most_specific_combined_id = ObjectID(class_id=title_bar_class)
                print(f"🏷️ 标题栏样式设置(备用): {title_bar_class}")
            
            # 尝试重建主题
            self._rebuild_element_theme(self.title_bar, "标题栏")
            
        except Exception as e:
            print(f"❌ 设置标题栏主题失败: {e}")
    
    def _apply_close_button_theme(self):
        """应用关闭按钮主题"""
        try:
            close_button_class = f"{self.theme_class}.close_button"
            
            # 检查set_object_id方法是否存在
            if hasattr(self.close_window_button, 'set_object_id'):
                self.close_window_button.set_object_id(ObjectID(class_id=close_button_class))
                print(f"❌ 关闭按钮样式设置: {close_button_class}")
            else:
                # 备用方法：直接设置most_specific_combined_id
                self.close_window_button.most_specific_combined_id = ObjectID(class_id=close_button_class)
                print(f"❌ 关闭按钮样式设置(备用): {close_button_class}")
            
            # 尝试重建主题
            self._rebuild_element_theme(self.close_window_button, "关闭按钮")
            
        except Exception as e:
            print(f"❌ 设置关闭按钮主题失败: {e}")
    
    def _rebuild_element_theme(self, element, element_name: str):
        """
        尝试重建元素主题
        
        Args:
            element: 要重建主题的UI元素
            element_name: 元素名称（用于日志）
        """
        try:
            # 尝试不同的重建方法
            if hasattr(element, 'rebuild'):
                element.rebuild()
                print(f"🔄 {element_name}主题重建成功(rebuild)")
            elif hasattr(element, 'rebuild_from_changed_theme_data'):
                element.rebuild_from_changed_theme_data()
                print(f"🔄 {element_name}主题重建成功(rebuild_from_changed_theme_data)")
            else:
                print(f"⚠️ {element_name}无可用的重建方法")
                
        except Exception as e:
            print(f"❌ {element_name}主题重建失败: {e}")
    
    def set_theme_class(self, new_theme_class: str):
        """
        动态更改主题类
        
        Args:
            new_theme_class: 新的主题类名
        """
        self.theme_class = new_theme_class
        
        # 重新设置窗口object_id
        if hasattr(self, 'set_object_id'):
            self.set_object_id(ObjectID(class_id=new_theme_class))
        
        # 重新应用子元素样式
        self._apply_themed_styles()
        
        print(f"🔄 主题类已更改为: {new_theme_class}")
    
    def get_theme_info(self) -> Dict[str, Any]:
        """
        获取当前主题信息
        
        Returns:
            包含主题信息的字典
        """
        return {
            'theme_class': self.theme_class,
            'window_title': getattr(self, 'window_display_title', ''),
            'has_title_bar': hasattr(self, 'title_bar') and self.title_bar is not None,
            'has_close_button': hasattr(self, 'close_window_button') and self.close_window_button is not None,
            'is_resizable': getattr(self, 'resizable', False)
        }
    
    def debug_theme_info(self):
        """打印调试信息"""
        info = self.get_theme_info()
        print("🔍 主题窗口调试信息:")
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # 打印object_id信息
        if hasattr(self, 'object_ids'):
            print(f"   窗口object_ids: {self.object_ids}")
        
        if hasattr(self, 'title_bar') and self.title_bar and hasattr(self.title_bar, 'object_ids'):
            print(f"   标题栏object_ids: {self.title_bar.object_ids}")
        
        if hasattr(self, 'close_window_button') and self.close_window_button and hasattr(self.close_window_button, 'object_ids'):
            print(f"   关闭按钮object_ids: {self.close_window_button.object_ids}")


# 预定义的主题窗口类
class ShopWindow(ThemedUIWindow):
    """商店窗口 - 预设主题为@shop_window"""
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('theme_class', '@shop_window')
        super().__init__(*args, **kwargs)


class InventoryWindow(ThemedUIWindow):
    """背包窗口 - 预设主题为@inventory_window"""
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('theme_class', '@inventory_window')
        super().__init__(*args, **kwargs)


class SettingsWindow(ThemedUIWindow):
    """设置窗口 - 预设主题为@settings_window"""
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('theme_class', '@settings_window')
        super().__init__(*args, **kwargs)


# 使用示例和测试
if __name__ == "__main__":
    print("🎨 主题化窗口组件 - ThemedUIWindow")
    print("✅ 自动为标题栏和关闭按钮应用主题样式")
    print("🔧 支持动态主题切换和调试信息")
    print("📦 提供预定义的专用窗口类")
    
    # 使用示例
    print("\n📋 使用示例:")
    print("from game.gui.widgets.themed_window import ThemedUIWindow, ShopWindow")
    print("window = ShopWindow(rect, manager, '商店标题')")
    print("window.debug_theme_info()  # 查看主题信息")