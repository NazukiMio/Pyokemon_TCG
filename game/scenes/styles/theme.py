"""
游戏主题配置文件
统一管理所有颜色、尺寸和样式配置
"""

class Theme:
    """现代毛玻璃风格主题配置"""
    
    # 颜色配置
    COLORS = {
        # 背景色
        'background': (230, 235, 245),
        'background_gradient_start': (230, 235, 245),
        'background_gradient_end': (250, 252, 255),
        
        # 主色调
        'accent': (88, 101, 242),  # 紫蓝色
        'accent_hover': (67, 78, 216),
        'accent_light': (120, 130, 255),
        
        # 文字颜色
        'text': (55, 65, 81),
        'text_secondary': (107, 114, 128),
        'text_white': (255, 255, 255),
        'text_placeholder': (156, 163, 175),
        
        # 毛玻璃效果
        'glass_bg': (255, 255, 255, 217),  # 0.85 * 255
        'glass_bg_hover': (255, 255, 255, 235),  # 0.92 * 255
        'glass_border': (255, 255, 255, 76),  # 0.3 * 255
        'glass_border_hover': (255, 255, 255, 102),  # 0.4 * 255
        
        # 按钮相关
        'button_hover_bg': (248, 249, 255),
        'button_shadow_light': (255, 255, 255, 153),  # 0.6 * 255
        'button_gradient_start': (248, 249, 255),
        'button_gradient_end': (240, 242, 247),
        
        # 边框和分割线
        'border': (209, 213, 219),
        'modern_border': (229, 231, 235),
        'border_focus': (88, 101, 242),
        
        # 阴影
        'shadow': (0, 0, 0, 38),  # 0.15 * 255
        'shadow_light': (0, 0, 0, 25),  # 0.1 * 255
        'shadow_dark': (0, 0, 0, 51),  # 0.2 * 255
        
        # 状态颜色
        'success': (34, 197, 94),
        'error': (239, 68, 68),
        'warning': (245, 158, 11),
        'info': (59, 130, 246),
        
        # 密码强度颜色
        'password_strength_weak': (239, 68, 68),
        'password_strength_medium': (245, 158, 11),
        'password_strength_strong': (34, 197, 94),
        
        # 浮雕效果
        'emboss_light': (255, 255, 255, 120),
        'emboss_shadow': (0, 0, 0, 60),
        
        # 高光效果
        'highlight': (255, 255, 255, 80),
        'highlight_strong': (255, 255, 255, 120),
    }
    
    # 尺寸配置
    SIZES = {
        # 圆角半径
        'border_radius_small': 8,
        'border_radius_medium': 12,
        'border_radius_large': 16,
        'border_radius_xl': 20,
        
        # 按钮尺寸
        'button_height_small': 40,
        'button_height_medium': 50,
        'button_height_large': 56,
        
        # 输入框尺寸
        'input_height': 50,
        'input_padding': 12,
        
        # 间距
        'spacing_xs': 4,
        'spacing_sm': 8,
        'spacing_md': 16,
        'spacing_lg': 24,
        'spacing_xl': 32,
        'spacing_2xl': 48,
        
        # 阴影
        'shadow_blur': 4,
        'shadow_offset': 2,
        'shadow_blur_large': 8,
        'shadow_offset_large': 4,
    }
    
    # 动画配置
    ANIMATION = {
        # 动画速度
        'speed_fast': 0.25,
        'speed_normal': 0.12,
        'speed_slow': 0.08,
        
        # 缩放
        'scale_normal': 1.0,
        'scale_hover': 1.05,
        'scale_active': 0.98,
        
        # 透明度
        'fade_speed': 8,
        'transition_duration': 300,  # 毫秒
        
        # 呼吸效果
        'breath_scale_min': 1.0,
        'breath_scale_max': 1.05,
        'breath_speed': 1.5,
    }
    
    # 字体配置
    FONTS = {
        'default_family': 'arial',
        'custom_family': 'power-clear.ttf',
        'fallback_family': 'arial',
        
        # 字体大小倍数（相对于屏幕高度）
        'size_xs': 0.016,   # 很小
        'size_sm': 0.020,   # 小
        'size_md': 0.025,   # 中等
        'size_lg': 0.032,   # 大
        'size_xl': 0.040,   # 很大
        'size_2xl': 0.048,  # 特大
        
        # 字体路径
        'custom_font_path': 'assets/fonts/power-clear.ttf',
    }
    
    # UI主题数据（pygame-gui）
    UI_THEME_DATA = {
        'text_entry_line': {
            'colours': {
                'normal_bg': '#FFFFFF00',  # 完全透明
                'focused_bg': '#FFFFFF00',
                'normal_border': '#00000000',
                'focused_border': '#00000000',
                'normal_text': '#374151',
                'selected_text': '#FFFFFF',
                'selected_bg': '#5865F2'
            },
            'misc': {
                'border_width': '0',
                'border_radius': '12',
                'padding': '12,8'
            }
        },
        'button': {
            'colours': {
                'normal_bg': '#00000000',
                'hovered_bg': '#00000000', 
                'selected_bg': '#00000000',
                'normal_border': '#00000000',
                'hovered_border': '#00000000',
                'selected_border': '#00000000',
                'normal_text': '#00000000',
                'hovered_text': '#00000000'
            },
            'misc': {
                'border_width': '0',
                'border_radius': '16',
                'shadow_width': '0'
            }
        }
    }
    
    @classmethod
    def get_color(cls, color_name):
        """获取颜色值"""
        return cls.COLORS.get(color_name, (255, 255, 255))
    
    @classmethod
    def get_size(cls, size_name):
        """获取尺寸值"""
        return cls.SIZES.get(size_name, 0)
    
    @classmethod
    def get_font_size(cls, size_name, screen_height):
        """根据屏幕高度计算字体大小"""
        multiplier = cls.FONTS.get(size_name, 0.025)
        return int(screen_height * multiplier)
    
    @classmethod
    def get_scaled_size(cls, size_name, scale_factor):
        """根据缩放因子获取缩放后的尺寸"""
        base_size = cls.get_size(size_name)
        return int(base_size * scale_factor)