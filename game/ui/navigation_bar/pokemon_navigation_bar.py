import pygame
import pygame_gui
import os
import math
from typing import Optional, Callable, List

class PokemonNavigationGUI:
    """
    Pokemon风格现代毛玻璃导航栏
    使用PNG图标和浮动动效
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        """
        初始化导航栏
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 导航栏尺寸
        self.height = 90
        self.y_position = screen_height - self.height
        
        # 导航项目配置
        self.nav_items = [
            {'id': 'pokedex', 'text': 'Pokédex', 'icon': 'dex'},
            {'id': 'social', 'text': 'Social', 'icon': 'friends'},
            {'id': 'home', 'text': 'Inicio', 'icon': 'home'},
            {'id': 'battle', 'text': 'Batalla', 'icon': 'combat'},
            {'id': 'menu', 'text': 'Menú', 'icon': 'menu'}
        ]
        
        # 加载图标
        self.icons = self.load_icons()
        
        # 导航状态
        self.active_item = 'home'
        self.hover_item = None
        
        # 新增：导航状态管理
        self.navigation_history = []  # 导航历史
        self.max_history = 10
        self.navigation_locked = False  # 导航锁定状态

        # 新增：通知系统
        self.nav_notifications = {
            'pokedex': 0,    # 图鉴未读数量
            'social': 0,     # 社交通知数量
            'home': 0,       # 主页通知数量
            'battle': 0,     # 战斗邀请数量
            'menu': 0        # 设置提醒数量
        }
        
        # 新增：状态指示器
        self.nav_states = {
            'pokedex': 'normal',     # normal, active, notification
            'social': 'normal',
            'home': 'active',        # 默认激活主页
            'battle': 'normal',
            'menu': 'normal'
        }
        
        # 新增：外部回调系统
        self.state_change_callback = None
        self.notification_callback = None
        
        print("✅ 增强版导航栏初始化完成")

        # 动画参数
        self.animation_timer = 0
        self.float_offsets = {item['id']: 0 for item in self.nav_items}
        self.hover_scales = {item['id']: 1.0 for item in self.nav_items}
        
        # 计算按钮区域
        self.button_areas = self.calculate_button_areas()
        
        # 回调函数
        self.on_navigation_click: Optional[Callable] = None
        
        # 字体
        self.font = pygame.font.SysFont("arial", 11, bold=True)
    
    def load_icons(self) -> dict:
        """
        加载PNG图标文件
        
        Returns:
            图标字典 {icon_name: {'normal': surface, 'dark': surface}}
        """
        icons = {}
        
        for item in self.nav_items:
            icon_name = item['icon']
            icons[icon_name] = {}
            
            # 加载普通图标
            normal_path = os.path.join("assets", "icons", f"{icon_name}.png")
            if os.path.exists(normal_path):
                try:
                    icon_surface = pygame.image.load(normal_path)
                    icon_surface = pygame.transform.smoothscale(icon_surface, (24, 24))
                    icons[icon_name]['normal'] = icon_surface
                    print(f"✅ 普通图标加载: {icon_name}.png")
                except Exception as e:
                    print(f"❌ 普通图标加载失败 {icon_name}: {e}")
                    icons[icon_name]['normal'] = None
            else:
                print(f"⚠️ 普通图标文件不存在: {normal_path}")
                icons[icon_name]['normal'] = None
            
            # 加载dark图标
            dark_path = os.path.join("assets", "icons", f"{icon_name}_dark.png")
            if os.path.exists(dark_path):
                try:
                    dark_surface = pygame.image.load(dark_path)
                    dark_surface = pygame.transform.smoothscale(dark_surface, (24, 24))
                    icons[icon_name]['dark'] = dark_surface
                    print(f"✅ Dark图标加载: {icon_name}_dark.png")
                except Exception as e:
                    print(f"❌ Dark图标加载失败 {icon_name}: {e}")
                    icons[icon_name]['dark'] = None
            else:
                print(f"⚠️ Dark图标文件不存在: {dark_path}")
                icons[icon_name]['dark'] = None
        
        return icons
    
    def set_state_change_callback(self, callback: Callable):
        """设置状态变化回调"""
        self.state_change_callback = callback
        print("✅ 导航状态变化回调已设置")
    
    def set_notification_callback(self, callback: Callable):
        """设置通知回调"""
        self.notification_callback = callback
        print("✅ 导航通知回调已设置")
    
    def add_notification(self, nav_id: str, count: int = 1):
        """添加通知"""
        if nav_id in self.nav_notifications:
            self.nav_notifications[nav_id] += count
            self.nav_states[nav_id] = 'notification'
            
            if self.notification_callback:
                self.notification_callback('add', nav_id, count)
            
            print(f"🔔 {nav_id} 添加 {count} 个通知")
            return True
        return False
    
    def clear_notifications(self, nav_id: str):
        """清除通知"""
        if nav_id in self.nav_notifications:
            old_count = self.nav_notifications[nav_id]
            self.nav_notifications[nav_id] = 0
            
            # 如果当前是活跃状态，保持活跃，否则变为正常
            if self.active_item == nav_id:
                self.nav_states[nav_id] = 'active'
            else:
                self.nav_states[nav_id] = 'normal'
            
            if self.notification_callback and old_count > 0:
                self.notification_callback('clear', nav_id, old_count)
            
            print(f"🔕 {nav_id} 清除了 {old_count} 个通知")
            return True
        return False
    
    def get_notification_count(self, nav_id: str) -> int:
        """获取通知数量"""
        return self.nav_notifications.get(nav_id, 0)
    
    def get_total_notifications(self) -> int:
        """获取总通知数量"""
        return sum(self.nav_notifications.values())
    
    def set_navigation_locked(self, locked: bool):
        """设置导航锁定状态"""
        self.navigation_locked = locked
        if locked:
            print("🔒 导航已锁定")
        else:
            print("🔓 导航已解锁")
    
    def is_navigation_locked(self) -> bool:
        """检查导航是否锁定"""
        return self.navigation_locked
    
    def set_active(self, nav_id: str, add_to_history: bool = True):
        """设置活跃的导航项 - 增强版"""
        if nav_id in [item['id'] for item in self.nav_items]:
            old_active = self.active_item
            
            # 更新活跃项
            self.active_item = nav_id
            
            # 更新状态
            for item_id in self.nav_states:
                if item_id == nav_id:
                    self.nav_states[item_id] = 'active'
                    # 清除当前项的通知
                    self.clear_notifications(item_id)
                elif self.nav_notifications[item_id] > 0:
                    self.nav_states[item_id] = 'notification'
                else:
                    self.nav_states[item_id] = 'normal'
            
            # 添加到历史记录
            if add_to_history and old_active != nav_id:
                self.navigation_history.append(old_active)
                if len(self.navigation_history) > self.max_history:
                    self.navigation_history.pop(0)
            
            # 回调通知
            if self.state_change_callback:
                self.state_change_callback(old_active, nav_id)
            
            print(f"🧭 导航切换: {old_active} → {nav_id}")
            return True
        return False

    def go_back(self) -> Optional[str]:
        """返回上一个导航项"""
        if self.navigation_history and not self.navigation_locked:
            previous_nav = self.navigation_history.pop()
            self.set_active(previous_nav, add_to_history=False)
            return previous_nav
        return None
    
    def get_navigation_history(self) -> List[str]:
        """获取导航历史"""
        return self.navigation_history.copy()
    
    def clear_navigation_history(self):
        """清除导航历史"""
        self.navigation_history.clear()
        print("🗑️ 导航历史已清除")

    def calculate_button_areas(self):
        """计算按钮区域"""
        areas = {}
        button_width = (self.screen_width - 60) // 5
        start_x = 30
        
        for i, item in enumerate(self.nav_items):
            x = start_x + i * (button_width + 6)
            y = self.y_position + 15
            
            areas[item['id']] = pygame.Rect(x, y, button_width, 60)
        
        return areas
    
    def update_animations(self):
        """更新动画效果"""
        self.animation_timer += 1
        
        for item in self.nav_items:
            item_id = item['id']
            
            # 浮动动效
            if item_id == self.active_item:
                # 活跃项目有更明显的浮动
                phase = (self.animation_timer + hash(item_id) % 60) * 0.08
                self.float_offsets[item_id] = math.sin(phase) * 4
            elif item_id == self.hover_item:
                # 悬停项目有轻微浮动
                phase = (self.animation_timer + hash(item_id) % 60) * 0.12
                self.float_offsets[item_id] = math.sin(phase) * 2
            else:
                # 非活跃项目缓慢回到原位
                current_offset = self.float_offsets[item_id]
                self.float_offsets[item_id] = current_offset * 0.9
            
            # 缩放动效
            target_scale = 1.1 if item_id == self.hover_item else 1.0
            current_scale = self.hover_scales[item_id]
            self.hover_scales[item_id] = current_scale + (target_scale - current_scale) * 0.15
    
    def handle_mouse_motion(self, pos: tuple):
        """处理鼠标移动"""
        self.hover_item = None
        
        for item_id, rect in self.button_areas.items():
            if rect.collidepoint(pos):
                self.hover_item = item_id
                break
    
    def handle_mouse_click(self, pos: tuple) -> Optional[str]:
        """处理鼠标点击 - 增强版"""
        if self.navigation_locked:
            print("🔒 导航已锁定，无法切换")
            return None
        
        for item_id, rect in self.button_areas.items():
            if rect.collidepoint(pos):
                if self.set_active(item_id):
                    if self.on_navigation_click:
                        self.on_navigation_click(item_id)
                    return item_id
        return None
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """处理事件 - 增强版"""
        if event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                return self.handle_mouse_click(event.pos)
            elif event.button == 3:  # 右键点击 - 返回上一页
                return self.go_back()
        elif event.type == pygame.KEYDOWN:
            # 键盘快捷键
            if event.key == pygame.K_BACKSPACE:
                return self.go_back()
        
        return None
    
    def draw_notification_badge(self, screen: pygame.Surface, rect: pygame.Rect, count: int):
        """绘制通知徽章"""
        if count <= 0:
            return
        
        # 徽章配置
        badge_size = 18
        badge_x = rect.right - 8
        badge_y = rect.y + 8
        
        # 绘制徽章背景
        badge_rect = pygame.Rect(badge_x - badge_size//2, badge_y - badge_size//2, badge_size, badge_size)
        pygame.draw.circle(screen, (255, 69, 58), (badge_x, badge_y), badge_size//2)  # 红色徽章
        pygame.draw.circle(screen, (255, 255, 255), (badge_x, badge_y), badge_size//2 - 1, 1)  # 白色边框
        
        # 绘制数字
        badge_text = str(min(count, 99))  # 最多显示99
        if count > 99:
            badge_text = "99+"
        
        badge_font = pygame.font.SysFont("arial", 10, bold=True)
        text_surface = badge_font.render(badge_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(badge_x, badge_y))
        screen.blit(text_surface, text_rect)
    
    def draw_state_indicator(self, screen: pygame.Surface, rect: pygame.Rect, state: str):
        """绘制状态指示器"""
        if state == 'active':
            # 活跃状态的底部指示器（原有逻辑）
            indicator_y = self.y_position + self.height - 8
            indicator_x1 = rect.centerx - 15
            indicator_x2 = rect.centerx + 15
            pygame.draw.line(screen, (102, 126, 234), 
                           (indicator_x1, indicator_y), (indicator_x2, indicator_y), 3)
        
        elif state == 'notification':
            # 通知状态的脉冲效果
            pulse_intensity = abs(math.sin(self.animation_timer * 0.1)) * 0.3 + 0.7
            glow_color = (255, 149, 0, int(pulse_intensity * 100))  # 橙色脉冲
            
            # 绘制脉冲光环
            glow_surface = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, 
                           (0, 0, rect.width + 10, rect.height + 10), 
                           border_radius=15)
            screen.blit(glow_surface, (rect.x - 5, rect.y - 5))

    def get_active(self) -> str:
        """获取当前活跃的导航项"""
        return self.active_item
    
    def update(self, time_delta: float):
        """更新导航栏"""
        self.update_animations()

    def get_navigation_stats(self) -> dict:
        """获取导航统计信息"""
        return {
            'active_item': self.active_item,
            'total_notifications': self.get_total_notifications(),
            'notifications_by_item': self.nav_notifications.copy(),
            'navigation_history_count': len(self.navigation_history),
            'is_locked': self.navigation_locked,
            'states': self.nav_states.copy()
        }
    
    def simulate_notifications(self):
        """模拟通知（用于测试）"""
        import random
        
        # 随机添加通知
        nav_ids = ['pokedex', 'social', 'battle', 'menu']
        selected_nav = random.choice(nav_ids)
        count = random.randint(1, 5)
        
        self.add_notification(selected_nav, count)
        print(f"🧪 模拟通知: {selected_nav} +{count}")
    
    def export_state(self) -> dict:
        """导出当前状态"""
        return {
            'active_item': self.active_item,
            'notifications': self.nav_notifications.copy(),
            'states': self.nav_states.copy(),
            'history': self.navigation_history.copy(),
            'locked': self.navigation_locked
        }
    
    def import_state(self, state_data: dict):
        """导入状态"""
        try:
            if 'active_item' in state_data:
                self.active_item = state_data['active_item']
            
            if 'notifications' in state_data:
                self.nav_notifications.update(state_data['notifications'])
            
            if 'states' in state_data:
                self.nav_states.update(state_data['states'])
            
            if 'history' in state_data:
                self.navigation_history = state_data['history'][:self.max_history]
            
            if 'locked' in state_data:
                self.navigation_locked = state_data['locked']
            
            print("✅ 导航状态导入成功")
            return True
            
        except Exception as e:
            print(f"❌ 导航状态导入失败: {e}")
            return False
    
    def reset_to_default(self):
        """重置到默认状态"""
        self.active_item = 'home'
        self.hover_item = None
        self.navigation_history.clear()
        self.navigation_locked = False
        
        # 清除所有通知
        for nav_id in self.nav_notifications:
            self.nav_notifications[nav_id] = 0
        
        # 重置所有状态
        for nav_id in self.nav_states:
            if nav_id == 'home':
                self.nav_states[nav_id] = 'active'
            else:
                self.nav_states[nav_id] = 'normal'
        
        print("🔄 导航栏已重置到默认状态")
    
    def draw_glass_background(self, screen: pygame.Surface):
        """绘制毛玻璃背景效果"""
        # 创建半透明背景
        bg_surface = pygame.Surface((self.screen_width, self.height), pygame.SRCALPHA)
        
        # 毛玻璃效果背景色
        bg_color = (255, 255, 255, 217)  # 85% 透明度
        bg_surface.fill(bg_color)
        
        # 绘制顶部边框
        pygame.draw.line(bg_surface, (255, 255, 255, 77), 
                        (0, 0), (self.screen_width, 0), 1)
        
        # 绘制到主屏幕
        screen.blit(bg_surface, (0, self.y_position))
    
    def draw_separators(self, screen: pygame.Surface):
        """绘制分隔符"""
        button_width = (self.screen_width - 60) // 5
        start_x = 30
        
        # 绘制垂直分隔符（在按钮之间）
        for i in range(len(self.nav_items) - 1):  # 4条分隔符
            sep_x = start_x + (i + 1) * (button_width + 6) - 3
            sep_y1 = self.y_position + 25  # 不顶格，留出边距
            sep_y2 = self.y_position + self.height - 25
            
            # 绘制半透明的分隔线
            pygame.draw.line(screen, (74, 85, 104, 60), 
                           (sep_x, sep_y1), (sep_x, sep_y2), 1)
    
    def draw_navigation_items(self, screen: pygame.Surface):
        """绘制导航项目 - 增强版"""
        for item in self.nav_items:
            item_id = item['id']
            icon_name = item['icon']
            
            # 获取按钮区域
            rect = self.button_areas[item_id]
            
            # 应用浮动和缩放动效
            float_offset = self.float_offsets[item_id]
            scale = self.hover_scales[item_id]
            
            # 计算动效后的位置
            animated_rect = rect.copy()
            animated_rect.y += int(float_offset)
            
            if scale != 1.0:
                # 应用缩放
                scaled_width = int(rect.width * scale)
                scaled_height = int(rect.height * scale)
                animated_rect = pygame.Rect(
                    rect.centerx - scaled_width // 2,
                    rect.centery - scaled_height // 2 + int(float_offset),
                    scaled_width,
                    scaled_height
                )
            
            # 获取当前状态
            current_state = self.nav_states.get(item_id, 'normal')
            
            # 绘制状态指示器
            self.draw_state_indicator(screen, animated_rect, current_state)
            
            # 选择图标类型（活跃状态用dark图标）
            icon_type = 'dark' if item_id == self.active_item else 'normal'
            icon_surface = self.icons.get(icon_name, {}).get(icon_type)
            
            if icon_surface:
                # 绘制图标
                icon_x = animated_rect.centerx - 12
                icon_y = animated_rect.y + 8
                
                # 如果有缩放效果，也缩放图标
                if scale != 1.0:
                    scaled_size = int(24 * scale)
                    scaled_icon = pygame.transform.smoothscale(icon_surface, (scaled_size, scaled_size))
                    icon_x = animated_rect.centerx - scaled_size // 2
                    screen.blit(scaled_icon, (icon_x, icon_y))
                else:
                    screen.blit(icon_surface, (icon_x, icon_y))
            
            # 绘制文字
            text_color = (45, 55, 72) if item_id == self.active_item else (113, 128, 150)
            text_surface = self.font.render(item['text'], True, text_color)
            text_rect = text_surface.get_rect(center=(animated_rect.centerx, animated_rect.bottom - 15))
            screen.blit(text_surface, text_rect)
            
            # 绘制通知徽章
            notification_count = self.nav_notifications.get(item_id, 0)
            if notification_count > 0:
                self.draw_notification_badge(screen, animated_rect, notification_count)
            
            # 活跃状态的底部指示器
            if item_id == self.active_item:
                indicator_y = self.y_position + self.height - 8
                indicator_x1 = animated_rect.centerx - 15
                indicator_x2 = animated_rect.centerx + 15
                
                # 绘制底部指示线
                pygame.draw.line(screen, (102, 126, 234), 
                               (indicator_x1, indicator_y), (indicator_x2, indicator_y), 3)
    
    def draw(self, screen: pygame.Surface):
        """
        绘制导航栏
        
        Args:
            screen: pygame屏幕对象
        """
        # 绘制毛玻璃背景
        self.draw_glass_background(screen)
        
        # 绘制分隔符
        self.draw_separators(screen)
        
        # 绘制导航项目
        self.draw_navigation_items(screen)
    
    def resize(self, new_width: int, new_height: int):
        """调整导航栏大小"""
        self.screen_width = new_width
        self.screen_height = new_height
        self.y_position = new_height - self.height
        
        # 重新计算按钮区域
        self.button_areas = self.calculate_button_areas()
    
    def cleanup(self):
        """清理资源 - 增强版"""
        # 清理回调
        self.state_change_callback = None
        self.notification_callback = None
        
        # 清理状态
        self.navigation_history.clear()
        self.nav_notifications.clear()
        self.nav_states.clear()
        
        print("🧹 导航栏资源清理完成")
    
    def __del__(self):
        """析构函数"""
        try:
            self.cleanup()
        except:
            pass

# 工厂函数
def create_enhanced_navigation_bar(screen_width: int, screen_height: int,
                                 state_callback=None, notification_callback=None) -> PokemonNavigationGUI:
    """
    创建增强版导航栏的工厂函数
    
    Args:
        screen_width: 屏幕宽度
        screen_height: 屏幕高度
        state_callback: 状态变化回调
        notification_callback: 通知回调
        
    Returns:
        配置完成的PokemonNavigationGUI实例
    """
    nav_bar = PokemonNavigationGUI(screen_width, screen_height)
    
    if state_callback:
        nav_bar.set_state_change_callback(state_callback)
    
    if notification_callback:
        nav_bar.set_notification_callback(notification_callback)
    
    print("✅ 增强版导航栏创建完成")
    return nav_bar

# 导航栏管理器类
class NavigationManager:
    """导航栏管理器，提供高级导航控制"""
    
    def __init__(self, nav_bar: PokemonNavigationGUI):
        self.nav_bar = nav_bar
        self.navigation_rules = {}  # 导航规则
        self.blocked_navigations = set()  # 被阻止的导航
        
    def add_navigation_rule(self, from_nav: str, to_nav: str, rule_func: Callable):
        """添加导航规则"""
        key = f"{from_nav}->{to_nav}"
        self.navigation_rules[key] = rule_func
        print(f"📋 添加导航规则: {key}")
    
    def block_navigation(self, nav_id: str):
        """阻止特定导航"""
        self.blocked_navigations.add(nav_id)
        print(f"🚫 阻止导航: {nav_id}")
    
    def unblock_navigation(self, nav_id: str):
        """解除导航阻止"""
        self.blocked_navigations.discard(nav_id)
        print(f"✅ 解除导航阻止: {nav_id}")
    
    def can_navigate_to(self, nav_id: str) -> bool:
        """检查是否可以导航到指定页面"""
        if nav_id in self.blocked_navigations:
            return False
        
        current_nav = self.nav_bar.get_active()
        rule_key = f"{current_nav}->{nav_id}"
        
        if rule_key in self.navigation_rules:
            return self.navigation_rules[rule_key]()
        
        return True
    
    def navigate_with_rules(self, nav_id: str) -> bool:
        """根据规则进行导航"""
        if self.can_navigate_to(nav_id):
            return self.nav_bar.set_active(nav_id)
        else:
            print(f"🚫 导航被规则阻止: {nav_id}")
            return False