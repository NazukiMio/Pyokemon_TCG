import pygame
import random
import time
from enum import Enum
from typing import Dict, List, Optional
from pack_opening_window import PackOpeningWindow, PackQuality

class TestScenario(Enum):
    SUCCESS = "success"
    NO_PACKS = "no_packs"
    NETWORK_ERROR = "network_error"
    TRANSACTION_FAILED = "transaction_failed"

class MockGameManager:
    """模拟游戏管理器 - 用于测试各种场景"""
    
    def __init__(self):
        # 模拟用户数据
        self.user_id = "test_user_001"
        self.user_packs = {
            "basic": 5,
            "premium": 3,
            "legendary": 1
        }
        self.user_cards = []
        self.user_stats = {
            "packs_opened": 0,
            "cards_collected": 0,
            "total_currency": 1000
        }
        
        # 测试控制
        self.test_scenario = TestScenario.SUCCESS
        self.response_delay = 0.0  # 模拟网络延迟
        
        # 卡牌池
        self.card_pool = self._create_card_pool()
        
        print("🧪 模拟游戏管理器初始化完成")
        print(f"📦 用户卡包: {self.user_packs}")

    def _create_card_pool(self) -> List[Dict]:
        """创建测试卡牌池"""
        return [
            # 普通卡牌
            {"id": "001", "name": "小火球", "rarity": "common", "image_path": ""},
            {"id": "002", "name": "治疗术", "rarity": "common", "image_path": ""},
            {"id": "003", "name": "护甲术", "rarity": "common", "image_path": ""},
            {"id": "004", "name": "疾风步", "rarity": "common", "image_path": ""},
            
            # 非凡卡牌
            {"id": "011", "name": "火焰风暴", "rarity": "uncommon", "image_path": ""},
            {"id": "012", "name": "冰霜护盾", "rarity": "uncommon", "image_path": ""},
            {"id": "013", "name": "闪电链", "rarity": "uncommon", "image_path": ""},
            
            # 稀有卡牌
            {"id": "021", "name": "烈焰龙息", "rarity": "rare", "image_path": ""},
            {"id": "022", "name": "寒冰风暴", "rarity": "rare", "image_path": ""},
            {"id": "023", "name": "雷霆之怒", "rarity": "rare", "image_path": ""},
            
            # 史诗卡牌
            {"id": "031", "name": "凤凰重生", "rarity": "epic", "image_path": ""},
            {"id": "032", "name": "时间静止", "rarity": "epic", "image_path": ""},
            
            # 传说卡牌
            {"id": "041", "name": "毁灭之神", "rarity": "legendary", "image_path": ""},
            {"id": "042", "name": "创世之光", "rarity": "legendary", "image_path": ""},
        ]

    def set_test_scenario(self, scenario: TestScenario):
        """设置测试场景"""
        self.test_scenario = scenario
        print(f"🎭 切换测试场景: {scenario.value}")

    def set_response_delay(self, delay: float):
        """设置响应延迟（模拟网络状况）"""
        self.response_delay = delay
        print(f"⏱️ 设置响应延迟: {delay}秒")

    def open_pack_complete_flow(self, quality: str) -> Dict:
        """模拟完整的开包流程"""
        print(f"🎴 开始模拟开包: {quality}")
        
        # 模拟网络延迟
        if self.response_delay > 0:
            time.sleep(self.response_delay)
        
        # 根据测试场景返回不同结果
        if self.test_scenario == TestScenario.NO_PACKS:
            return {"success": False, "error": "insufficient_packs"}
        
        elif self.test_scenario == TestScenario.NETWORK_ERROR:
            return {"success": False, "error": "network_timeout"}
        
        elif self.test_scenario == TestScenario.TRANSACTION_FAILED:
            return {"success": False, "error": "transaction_failed"}
        
        # 成功场景
        elif self.test_scenario == TestScenario.SUCCESS:
            # 检查卡包数量
            if self.user_packs.get(quality, 0) <= 0:
                return {"success": False, "error": "insufficient_packs"}
            
            # 扣除卡包
            self.user_packs[quality] -= 1
            
            # 生成卡牌
            cards = self._generate_cards_for_quality(quality)
            
            # 更新统计
            self.user_stats["packs_opened"] += 1
            self.user_stats["cards_collected"] += len(cards)
            self.user_cards.extend(cards)
            
            print(f"✅ 开包成功，获得 {len(cards)} 张卡牌")
            print(f"📊 剩余卡包: {self.user_packs}")
            
            return {
                "success": True,
                "cards": cards,
                "pack_quality": quality,
                "cards_count": len(cards)
            }
        
        return {"success": False, "error": "unknown_error"}

    def _generate_cards_for_quality(self, quality: str) -> List[Dict]:
        """根据卡包品质生成卡牌"""
        if quality == "basic":
            # 基础包：主要普通卡，少量非凡
            cards = []
            for _ in range(5):  # 5张卡
                if random.random() < 0.8:  # 80%普通
                    rarity = "common"
                else:  # 20%非凡
                    rarity = "uncommon"
                cards.append(self._get_random_card(rarity))
            
        elif quality == "premium":
            # 高级包：保证至少1张稀有，可能有史诗
            cards = []
            for _ in range(4):  # 4张普通/非凡卡
                if random.random() < 0.6:
                    rarity = "common"
                else:
                    rarity = "uncommon"
                cards.append(self._get_random_card(rarity))
            
            # 保证1张稀有或更高
            if random.random() < 0.1:  # 10%史诗
                cards.append(self._get_random_card("epic"))
            else:  # 90%稀有
                cards.append(self._get_random_card("rare"))
        
        elif quality == "legendary":
            # 传说包：保证至少1张传说，多张稀有/史诗
            cards = []
            
            # 保证1张传说
            cards.append(self._get_random_card("legendary"))
            
            # 2-3张稀有/史诗
            for _ in range(random.randint(2, 3)):
                if random.random() < 0.7:  # 70%稀有
                    rarity = "rare"
                else:  # 30%史诗
                    rarity = "epic"
                cards.append(self._get_random_card(rarity))
            
            # 填充到7张
            while len(cards) < 7:
                cards.append(self._get_random_card("uncommon"))
        
        return cards

    def _get_random_card(self, rarity: str) -> Dict:
        """获取指定稀有度的随机卡牌"""
        matching_cards = [card for card in self.card_pool if card["rarity"] == rarity]
        if matching_cards:
            return random.choice(matching_cards).copy()
        else:
            # 备用卡牌
            return {
                "id": f"backup_{random.randint(1000, 9999)}",
                "name": f"测试{rarity}卡牌",
                "rarity": rarity,
                "image_path": ""
            }

    def get_user_pack_inventory(self) -> Dict[str, int]:
        """获取用户卡包库存"""
        return self.user_packs.copy()

    def add_test_packs(self, quality: str, count: int):
        """添加测试卡包"""
        self.user_packs[quality] = self.user_packs.get(quality, 0) + count
        print(f"➕ 添加 {count} 个 {quality} 卡包，当前: {self.user_packs[quality]}")


class PackTestLauncher:
    """开包界面测试启动器"""
    
    def __init__(self):
        pygame.init()
        
        # 屏幕设置
        self.screen_width = 1400
        self.screen_height = 900
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("🎴 开包界面测试器 v1.0")
        
        # 时钟和字体
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # 创建组件
        self.game_manager = MockGameManager()
        self.pack_window = PackOpeningWindow(
            self.screen_width, 
            self.screen_height, 
            self.game_manager
        )
        
        # 测试界面状态
        self.show_debug_info = True
        self.current_fps = 0
        
        # 创建测试按钮
        self._create_test_buttons()
        
        print("🚀 开包界面测试启动器已就绪")

    def _create_test_buttons(self):
        """创建测试按钮"""
        button_width = 180
        button_height = 40
        margin = 10
        start_y = 50
        
        self.buttons = {
            # 界面控制按钮
            "show_pack_window": pygame.Rect(margin, start_y, button_width, button_height),
            "close_pack_window": pygame.Rect(margin, start_y + 50, button_width, button_height),
            
            # 测试场景按钮
            "scenario_success": pygame.Rect(margin + 200, start_y, button_width, button_height),
            "scenario_no_packs": pygame.Rect(margin + 200, start_y + 50, button_width, button_height),
            "scenario_network": pygame.Rect(margin + 200, start_y + 100, button_width, button_height),
            "scenario_failed": pygame.Rect(margin + 200, start_y + 150, button_width, button_height),
            
            # 工具按钮
            "add_packs": pygame.Rect(margin + 400, start_y, button_width, button_height),
            "reset_data": pygame.Rect(margin + 400, start_y + 50, button_width, button_height),
            "toggle_debug": pygame.Rect(margin + 400, start_y + 100, button_width, button_height),
            "stress_test": pygame.Rect(margin + 400, start_y + 150, button_width, button_height),
        }

    def handle_button_click(self, pos):
        """处理按钮点击"""
        for button_name, button_rect in self.buttons.items():
            if button_rect.collidepoint(pos):
                self._handle_button_action(button_name)
                break

    def _handle_button_action(self, action: str):
        """处理按钮动作"""
        if action == "show_pack_window":
            self.pack_window.show()  # 显示选择界面
        
        elif action == "close_pack_window":
            self.pack_window.close()
        
        elif action == "scenario_success":
            self.game_manager.set_test_scenario(TestScenario.SUCCESS)
        
        elif action == "scenario_no_packs":
            self.game_manager.set_test_scenario(TestScenario.NO_PACKS)
        
        elif action == "scenario_network":
            self.game_manager.set_test_scenario(TestScenario.NETWORK_ERROR)
        
        elif action == "scenario_failed":
            self.game_manager.set_test_scenario(TestScenario.TRANSACTION_FAILED)
        
        elif action == "add_packs":
            # 给所有类型都添加5个卡包
            for quality in ["basic", "premium", "legendary"]:
                self.game_manager.add_test_packs(quality, 5)
        
        elif action == "reset_data":
            self.game_manager.user_packs = {"basic": 5, "premium": 3, "legendary": 1}
            self.game_manager.user_cards.clear()
            self.game_manager.user_stats = {"packs_opened": 0, "cards_collected": 0, "total_currency": 1000}
            print("🔄 用户数据已重置")
        
        elif action == "toggle_debug":
            self.show_debug_info = not self.show_debug_info
            print(f"🐛 调试信息: {'开启' if self.show_debug_info else '关闭'}")
        
        elif action == "stress_test":
            self._run_stress_test()

    def _run_stress_test(self):
        """运行压力测试"""
        print("⚡ 开始压力测试...")
        
        # 添加大量卡包
        self.game_manager.add_test_packs("legendary", 10)
        
        # 快速开包
        for _ in range(3):
            self.pack_window.open_pack(PackQuality.LEGENDARY)
            pygame.time.wait(100)  # 短暂延迟

    def update(self, dt: float):
        """更新逻辑"""
        self.pack_window.update(dt)
        self.current_fps = self.clock.get_fps()

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    self.show_debug_info = not self.show_debug_info
                elif event.key == pygame.K_F5:
                    self._handle_button_action("reset_data")
                elif event.key == pygame.K_1:
                    self.pack_window.open_pack(PackQuality.BASIC)
                elif event.key == pygame.K_2:
                    self.pack_window.open_pack(PackQuality.PREMIUM)
                elif event.key == pygame.K_3:
                    self.pack_window.open_pack(PackQuality.LEGENDARY)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    # 先让开包窗口处理
                    if not self.pack_window.handle_event(event):
                        # 开包窗口没有处理，则处理测试按钮
                        self.handle_button_click(event.pos)
            else:
                # 传递其他事件给开包窗口
                self.pack_window.handle_event(event)
        
        return True

    def draw(self):
        """绘制界面"""
        # 清屏
        self.screen.fill((25, 25, 35))
        
        # 绘制测试控制界面
        self._draw_test_controls()
        
        # 绘制调试信息
        if self.show_debug_info:
            self._draw_debug_info()
        
        # 绘制开包窗口（在最上层）
        self.pack_window.draw(self.screen)
        
        # 更新显示
        pygame.display.flip()

    def _draw_test_controls(self):
        """绘制测试控制界面"""
        # 标题
        title_text = self.font.render("🎴 开包界面测试器", True, (255, 255, 255))
        self.screen.blit(title_text, (10, 10))
        
        # 绘制按钮
        button_configs = {
            "show_pack_window": ("显示开包界面", (100, 255, 100)),
            "close_pack_window": ("关闭界面", (255, 100, 100)),
            
            "scenario_success": ("正常场景", (100, 255, 100)),
            "scenario_no_packs": ("缺少卡包", (255, 100, 100)),
            "scenario_network": ("网络错误", (255, 150, 100)),
            "scenario_failed": ("交易失败", (255, 100, 150)),
            
            "add_packs": ("添加卡包", (150, 255, 150)),
            "reset_data": ("重置数据", (255, 255, 100)),
            "toggle_debug": ("调试信息", (150, 150, 255)),
            "stress_test": ("压力测试", (255, 100, 255)),
        }
        
        for button_name, (text, color) in button_configs.items():
            if button_name in self.buttons:
                button_rect = self.buttons[button_name]
                
                # 检查是否被激活
                is_active = False
                if "scenario" in button_name:
                    scenario_map = {
                        "scenario_success": TestScenario.SUCCESS,
                        "scenario_no_packs": TestScenario.NO_PACKS,
                        "scenario_network": TestScenario.NETWORK_ERROR,
                        "scenario_failed": TestScenario.TRANSACTION_FAILED,
                    }
                    is_active = self.game_manager.test_scenario == scenario_map.get(button_name)
                
                # 绘制按钮
                if is_active:
                    pygame.draw.rect(self.screen, color, button_rect)
                    pygame.draw.rect(self.screen, (255, 255, 255), button_rect, 3)
                else:
                    pygame.draw.rect(self.screen, (50, 50, 60), button_rect)
                    pygame.draw.rect(self.screen, color, button_rect, 2)
                
                # 绘制文字
                text_surface = self.small_font.render(text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=button_rect.center)
                self.screen.blit(text_surface, text_rect)

    def _draw_debug_info(self):
        """绘制调试信息"""
        debug_x = self.screen_width - 300
        debug_y = 50
        
        debug_info = [
            f"FPS: {self.current_fps:.1f}",
            f"场景: {self.game_manager.test_scenario.value}",
            f"基础包: {self.game_manager.user_packs['basic']}",
            f"高级包: {self.game_manager.user_packs['premium']}",
            f"传说包: {self.game_manager.user_packs['legendary']}",
            f"已开包: {self.game_manager.user_stats['packs_opened']}",
            f"收集卡牌: {self.game_manager.user_stats['cards_collected']}",
            # f"粒子数: {len(self.pack_window.particles)}",
            f"窗口状态: {'显示' if self.pack_window.is_visible else '隐藏'}",
            f"动画状态: {self.pack_window.animation_state.value if self.pack_window.is_visible else 'N/A'}",
        ]
        
        # 绘制调试背景
        debug_rect = pygame.Rect(debug_x - 10, debug_y - 10, 280, len(debug_info) * 25 + 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), debug_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), debug_rect, 1)
        
        for i, info in enumerate(debug_info):
            text_surface = self.small_font.render(info, True, (200, 200, 200))
            self.screen.blit(text_surface, (debug_x, debug_y + i * 25))
        
        # 快捷键提示
        shortcuts = [
            "快捷键:",
            "O - 显示开包界面",
            "C - 关闭界面", 
            "F1 - 调试信息",
            "F5 - 重置数据",
            "",
            "开包界面内:",
            "A/D - 切换卡包",
            "空格 - 确认开包",
            "ESC - 关闭"
        ]
        
        shortcut_y = debug_y + len(debug_info) * 25 + 40
        for i, shortcut in enumerate(shortcuts):
            color = (255, 255, 100) if i == 0 else (150, 150, 150)
            text_surface = self.small_font.render(shortcut, True, color)
            self.screen.blit(text_surface, (debug_x, shortcut_y + i * 20))

    def run(self):
        """运行测试器主循环"""
        print("🎮 测试器开始运行...")
        print("💡 使用 O 键显示开包界面，在界面内用 A/D 切换卡包")
        
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
        
        print("👋 测试器已退出")
        pygame.quit()


if __name__ == "__main__":
    try:
        launcher = PackTestLauncher()
        launcher.run()
    except Exception as e:
        print(f"❌ 启动器错误: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()