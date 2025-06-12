import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIPanel, UILabel, UIWindow, UISelectionList
from pygame_gui.core import ObjectID
import random

class EMagicaWindow:
    """
    魔法选择窗口 - 弹出式对话框
    包含各种魔法挑战和特殊战斗模式
    """
    
    def __init__(self, screen_width: int, screen_height: int, ui_manager):
        """
        初始化魔法选择窗口
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            ui_manager: pygame_gui UI管理器
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_manager = ui_manager
        
        # 窗口尺寸
        self.window_width = min(700, int(screen_width * 0.75))
        self.window_height = min(550, int(screen_height * 0.8))
        
        # 计算居中位置
        window_x = (screen_width - self.window_width) // 2
        window_y = (screen_height - self.window_height) // 2
        
        # 创建主窗口
        self.window = UIWindow(
            rect=pygame.Rect(window_x, window_y, self.window_width, self.window_height),
            manager=ui_manager,
            window_display_title="✨ Elecciones Mágicas",
            object_id=ObjectID('#emagica_window'),
            resizable=False
        )
        
        # 状态管理
        self.is_visible = True
        self.selected_challenge = None
        
        # 魔法挑战数据
        self.magic_challenges = [
            {
                'name': '🌟 Desafío Estelar',
                'description': 'Batalla contra criaturas celestiales',
                'difficulty': 'Fácil',
                'reward': '100 monedas + carta especial'
            },
            {
                'name': '🔥 Prueba de Fuego',
                'description': 'Enfrenta a poderosos dragones',
                'difficulty': 'Medio',
                'reward': '200 monedas + sobre premium'
            },
            {
                'name': '⚡ Tormenta Eléctrica',
                'description': 'Domina el poder del rayo',
                'difficulty': 'Difícil',
                'reward': '300 monedas + carta legendaria'
            },
            {
                'name': '🌊 Mareas Místicas',
                'description': 'Navega por aguas encantadas',
                'difficulty': 'Medio',
                'reward': '150 monedas + fragmento de cristal'
            },
            {
                'name': '🌪️ Vórtice Temporal',
                'description': 'Viaja a través del tiempo',
                'difficulty': 'Muy Difícil',
                'reward': '500 monedas + carta mítica'
            },
            {
                'name': '🌙 Eclipse Lunar',
                'description': 'Batalla bajo la luna llena',
                'difficulty': 'Medio',
                'reward': '180 monedas + poción rara'
            }
        ]
        
        # 创建UI元素
        self.create_ui_elements()
        
        # 回调函数
        self.on_close = None
        
        print("✨ 创建魔法选择窗口")
    
    def create_ui_elements(self):
        """创建UI元素"""
        # 标题标签
        title_rect = pygame.Rect(20, 20, self.window_width - 40, 50)
        self.title_label = UILabel(
            relative_rect=title_rect,
            text="Elige tu desafío mágico y demuestra tu valor:",
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#title_label')
        )
        
        # 挑战列表
        list_rect = pygame.Rect(20, 80, self.window_width - 280, 300)
        challenge_names = [f"{challenge['name']} - {challenge['difficulty']}" 
                          for challenge in self.magic_challenges]
        
        self.challenge_list = UISelectionList(
            relative_rect=list_rect,
            item_list=challenge_names,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#challenge_list')
        )
        
        # 详情面板
        details_rect = pygame.Rect(self.window_width - 250, 80, 230, 300)
        self.details_panel = UIPanel(
            relative_rect=details_rect,
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#details_panel')
        )
        
        # 详情标签 - 描述
        self.description_label = UILabel(
            relative_rect=pygame.Rect(10, 10, 210, 100),
            text="Selecciona un desafío para ver los detalles",
            manager=self.ui_manager,
            container=self.details_panel,
            object_id=ObjectID('#description_label')
        )
        
        # 详情标签 - 奖励
        self.reward_label = UILabel(
            relative_rect=pygame.Rect(10, 120, 210, 80),
            text="",
            manager=self.ui_manager,
            container=self.details_panel,
            object_id=ObjectID('#reward_label')
        )
        
        # 随机挑战按钮
        random_button_rect = pygame.Rect(20, self.window_height - 120, 150, 40)
        self.random_button = UIButton(
            relative_rect=random_button_rect,
            text="🎲 Aleatorio",
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#random_button')
        )
        
        # 开始挑战按钮  
        start_button_rect = pygame.Rect(180, self.window_height - 120, 150, 40)
        self.start_button = UIButton(
            relative_rect=start_button_rect,
            text="⚔️ Comenzar",
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#start_button')
        )
        self.start_button.disable()  # 初始禁用
        
        # 关闭按钮
        close_button_rect = pygame.Rect(340, self.window_height - 120, 100, 40)
        self.close_button = UIButton(
            relative_rect=close_button_rect,
            text="Cerrar",
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#close_button')
        )
        
        # 状态标签
        self.status_label = UILabel(
            relative_rect=pygame.Rect(20, self.window_height - 70, self.window_width - 40, 30),
            text="💡 Selecciona un desafío para comenzar tu aventura mágica",
            manager=self.ui_manager,
            container=self.window,
            object_id=ObjectID('#status_label')
        )
    
    def handle_event(self, event):
        """处理事件"""
        if not self.is_visible:
            return None
        
        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.challenge_list:
                # 获取选中的挑战
                selected_text = event.text
                selected_index = None
                
                # 找到对应的挑战索引
                for i, challenge in enumerate(self.magic_challenges):
                    if selected_text.startswith(challenge['name']):
                        selected_index = i
                        break
                
                if selected_index is not None:
                    self.selected_challenge = selected_index
                    self.update_challenge_details()
                    self.start_button.enable()
                    print(f"✨ 选择挑战: {self.magic_challenges[selected_index]['name']}")
                
                return "challenge_selected"
        
        elif event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.random_button:
                # 随机选择挑战
                random_index = random.randint(0, len(self.magic_challenges) - 1)
                self.selected_challenge = random_index
                self.challenge_list.set_single_selection(random_index)
                self.update_challenge_details()
                self.start_button.enable()
                print(f"🎲 随机选择: {self.magic_challenges[random_index]['name']}")
                return "random_selected"
            
            elif event.ui_element == self.start_button:
                if self.selected_challenge is not None:
                    challenge = self.magic_challenges[self.selected_challenge]
                    self.status_label.set_text(f"🚀 ¡Iniciando {challenge['name']}!")
                    print(f"⚔️ 开始挑战: {challenge['name']}")
                    # 这里可以添加实际的挑战启动逻辑
                    return "start_challenge"
            
            elif event.ui_element == self.close_button:
                self.close()
                return "close"
        
        elif event.type == pygame_gui.UI_WINDOW_CLOSE:
            if event.ui_element == self.window:
                self.close()
                return "close"
        
        return None
    
    def update_challenge_details(self):
        """更新挑战详情显示"""
        if self.selected_challenge is None:
            return
        
        challenge = self.magic_challenges[self.selected_challenge]
        
        # 更新描述
        description_text = f"🎯 {challenge['description']}\n\n📊 Dificultad: {challenge['difficulty']}"
        self.description_label.set_text(description_text)
        
        # 更新奖励
        reward_text = f"🏆 Recompensas:\n{challenge['reward']}"
        self.reward_label.set_text(reward_text)
        
        # 更新状态
        self.status_label.set_text(f"✅ {challenge['name']} seleccionado. ¡Listo para la batalla!")
    
    def draw_magical_effects(self, screen: pygame.Surface):
        """绘制魔法特效"""
        if not self.is_visible:
            return
        
        # 获取窗口内容区域
        try:
            content_rect = self.window.get_container().get_rect()
        except:
            return
        
        # 简单的星星效果
        import time
        import math
        current_time = time.time()
        
        for i in range(8):
            # 计算星星位置
            angle = math.radians((current_time * 50 + i * 45) % 360)
            radius = 30 + i * 5
            star_x = content_rect.centerx + radius * math.cos(angle)
            star_y = content_rect.top + 40 + radius * math.sin(angle)
            
            # 绘制星星
            star_size = 3 + (i % 3)
            alpha = int(128 + 127 * math.sin(current_time * 3 + i))
            alpha = max(0, min(255, alpha))  # 确保alpha在有效范围内
            
            star_surface = pygame.Surface((star_size * 2, star_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(star_surface, (255, 255, 150, alpha), (star_size, star_size), star_size)
            
            screen.blit(star_surface, (int(star_x - star_size), int(star_y - star_size)))
    
    def update(self, time_delta: float):
        """更新窗口状态"""
        # 这里可以添加动画更新逻辑
        pass
    
    def close(self):
        """关闭窗口"""
        if self.is_visible:
            self.is_visible = False
            if self.window:
                self.window.kill()
            if self.on_close:
                self.on_close()
            print("🚪 关闭魔法选择窗口")
    
    def cleanup(self):
        """清理资源"""
        if self.window:
            self.window.kill()