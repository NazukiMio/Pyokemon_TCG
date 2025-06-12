"""
已弃用的商店绘制混入类
重构后不再使用复杂的自绘制，改用pygame_gui
此文件保留仅为兼容性，建议删除对此文件的导入
"""

import pygame
from typing import Tuple, List, Optional, Dict, Any


class TiendaDrawMixin:
    """
    已弃用的商店绘制混入类
    
    重构说明：
    - 原有的复杂自绘制代码已移除
    - 现在使用纯pygame_gui实现
    - 此类保留仅为向后兼容
    - 建议从代码中移除对此类的引用
    """
    
    def __init__(self):
        print("⚠️ TiendaDrawMixin已弃用，请使用纯pygame_gui的ModernTiendaWindow")
    
    # 保留一些空方法以防止导入错误
    def create_gradient_surface(self, *args, **kwargs):
        """已弃用：创建渐变表面"""
        pass
    
    def draw_glass_effect(self, *args, **kwargs):
        """已弃用：绘制毛玻璃效果"""
        pass
    
    def draw_soft_shadow(self, *args, **kwargs):
        """已弃用：绘制柔和阴影"""
        pass
    
    def draw_animated_border(self, *args, **kwargs):
        """已弃用：绘制动画边框"""
        pass
    
    def draw_main_window(self, *args, **kwargs):
        """已弃用：绘制主窗口"""
        pass
    
    def draw_header_section(self, *args, **kwargs):
        """已弃用：绘制标题区域"""
        pass
    
    def draw_close_button(self, *args, **kwargs):
        """已弃用：绘制关闭按钮"""
        pass
    
    def draw_categories_sidebar(self, *args, **kwargs):
        """已弃用：绘制分类侧边栏"""
        pass
    
    def draw_main_content_area(self, *args, **kwargs):
        """已弃用：绘制主要内容区域"""
        pass
    
    def draw_shop_effects(self, *args, **kwargs):
        """已弃用：绘制商店效果"""
        pass
    
    # 其他所有原有方法都标记为已弃用
    def __getattr__(self, name):
        """拦截所有未定义的方法调用"""
        print(f"⚠️ 方法 {name} 已弃用，TiendaDrawMixin不再使用")
        return lambda *args, **kwargs: None


# 兼容性警告
def show_deprecation_warning():
    """显示弃用警告"""
    print("=" * 60)
    print("⚠️  弃用警告: TiendaDrawMixin")
    print("=" * 60)
    print("此模块中的TiendaDrawMixin类已被弃用。")
    print("请使用重构后的ModernTiendaWindow，它使用纯pygame_gui实现。")
    print("")
    print("迁移建议：")
    print("1. 移除对TiendaDrawMixin的导入")
    print("2. 使用ModernTiendaWindow代替")
    print("3. 删除对自绘制方法的调用")
    print("=" * 60)


# 如果直接运行此文件，显示弃用警告
if __name__ == "__main__":
    show_deprecation_warning()