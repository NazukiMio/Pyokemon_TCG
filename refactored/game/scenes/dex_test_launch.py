"""
DexPage测试启动器
独立测试TCG卡牌图鉴页面的所有功能
"""

import pygame
import pygame_gui
import json
import os
import sys
import importlib.util  # 添加这一行
from typing import Dict, List, Any, Optional

# 在文件开头的导入部分添加
try:
    from dex_page import DexPage
except ImportError:
    print("❌ 无法导入DexPage，请确保dex_page.py在同一目录")
    DexPage = None

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..")
sys.path.insert(0, project_root)

# 模拟Card类
class MockCard:
    """模拟卡牌类"""
    def __init__(self, card_data: Dict[str, Any]):
        self.id = card_data.get('id', '')
        self.name = card_data.get('name', 'Unknown Card')
        self.hp = card_data.get('hp', 0)
        self.types = card_data.get('types', [])
        self.rarity = card_data.get('rarity', 'Common')
        self.attacks = card_data.get('attacks', [])
        self.image_path = card_data.get('image', '')
        self.set_name = card_data.get('set_name', '')
        self.card_number = card_data.get('card_number', '')
        self.description = card_data.get('description', '')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'hp': self.hp,
            'types': json.dumps(self.types) if isinstance(self.types, list) else self.types,
            'rarity': self.rarity,
            'attacks': json.dumps(self.attacks) if isinstance(self.attacks, list) else self.attacks,
            'image_path': self.image_path,
            'set_name': self.set_name,
            'card_number': self.card_number,
            'description': self.description
        }

# 模拟CardDAO
class MockCardDAO:
    """模拟卡牌数据访问对象"""
    
    def __init__(self):
        self.cards = []
        self.load_cards()
    
    def load_cards(self):
        """加载卡牌数据"""
        # 尝试加载真实的cards.json
        cards_path = os.path.join(project_root, "assets", "card_assets", "cards.json")
        
        if os.path.exists(cards_path):
            try:
                with open(cards_path, 'r', encoding='utf-8') as f:
                    cards_data = json.load(f)
                
                print(f"✅ 从 {cards_path} 加载了 {len(cards_data)} 张卡牌")
                
                for card_data in cards_data[:200]:  # 限制到200张进行测试
                    self.cards.append(MockCard(card_data))
                
            except Exception as e:
                print(f"❌ 加载cards.json失败: {e}")
                self.create_mock_cards()
        else:
            print(f"⚠️ 未找到cards.json，使用模拟数据")
            self.create_mock_cards()
    
    def create_mock_cards(self):
        """创建模拟卡牌数据"""
        rarities = ['Common', 'Uncommon', 'Rare', 'Rare Holo', 'Rare Holo EX', 'Ultra Rare', 'Rare Secret']
        types_list = ['Grass', 'Fire', 'Water', 'Lightning', 'Psychic', 'Fighting', 'Darkness', 'Metal', 'Fairy', 'Dragon', 'Colorless']
        
        for i in range(100):
            card_data = {
                'id': f'test-{i+1:03d}',
                'name': f'Carta de Prueba {i+1}',
                'hp': 50 + (i * 5) % 200,
                'types': [types_list[i % len(types_list)]],
                'rarity': rarities[i % len(rarities)],
                'attacks': [
                    {
                        'name': 'Ataque Básico',
                        'damage': str(20 + (i * 3) % 100),
                        'text': 'Un ataque poderoso que causa daño.' if i % 3 == 0 else ''
                    }
                ] if i % 2 == 0 else [],
                'image': f'images/test-{i+1:03d}.png'
            }
            self.cards.append(MockCard(card_data))
        
        print(f"✅ 创建了 {len(self.cards)} 张模拟卡牌")
    
    def search_cards(self, limit=10000):
        """搜索卡牌"""
        return self.cards[:min(limit, len(self.cards))]
    
    def get_all_rarities(self):
        """获取所有稀有度"""
        rarities = set()
        for card in self.cards:
            rarities.add(card.rarity)
        return sorted(list(rarities))
    
    def get_all_types(self):
        """获取所有类型"""
        types = set()
        for card in self.cards:
            if isinstance(card.types, list):
                types.update(card.types)
            elif isinstance(card.types, str):
                try:
                    card_types = json.loads(card.types)
                    if isinstance(card_types, list):
                        types.update(card_types)
                except:
                    pass
        return sorted(list(types))

# 模拟DatabaseManager
class MockDatabaseManager:
    """模拟数据库管理器"""
    
    def __init__(self):
        self.card_dao = MockCardDAO()
        self.user_collection = self.generate_mock_collection()
    
    def generate_mock_collection(self):
        """生成模拟用户收集数据"""
        collection = {}
        cards = self.card_dao.search_cards()
        
        # 模拟用户拥有30%的卡牌
        for i, card in enumerate(cards):
            if i % 3 == 0:  # 每三张卡拥有一张
                collection[card.id] = {
                    'quantity': 1 + (i % 3),
                    'obtained_at': f'2024-{(i%12)+1:02d}-{(i%28)+1:02d}'
                }
        
        print(f"✅ 生成模拟收集数据: {len(collection)} 张卡牌")
        return collection
    
    def get_user_cards(self, user_id):
        """获取用户卡牌"""
        return [
            {
                'card_id': card_id,
                'quantity': data['quantity'],
                'obtained_at': data['obtained_at']
            }
            for card_id, data in self.user_collection.items()
        ]

# 模拟认证管理器
class MockAuthManager:
    """模拟认证管理器"""
    
    def get_user_info(self):
        return {
            'id': 1,
            'username': 'test_user',
            'email': 'test@example.com'
        }

# 全局认证函数
def get_auth_manager():
    return MockAuthManager()

# 导入DexPage（需要在模拟类定义之后）
try:
    # 临时替换导入
    import sys
    original_modules = {}
    
    # 保存原始模块
    modules_to_mock = [
        'game.core.database.database_manager',
        'game.core.cards.card_data', 
        'game.core.auth.auth_manager'
    ]
    
    for module_name in modules_to_mock:
        if module_name in sys.modules:
            original_modules[module_name] = sys.modules[module_name]
    
    # 创建模拟模块
    from types import ModuleType
    
    # 模拟database_manager模块
    db_module = ModuleType('database_manager')
    db_module.DatabaseManager = MockDatabaseManager
    sys.modules['game.core.database.database_manager'] = db_module
    
    # 模拟card_data模块
    card_module = ModuleType('card_data')
    card_module.Card = MockCard
    sys.modules['game.core.cards.card_data'] = card_module
    
    # 模拟auth_manager模块
    auth_module = ModuleType('auth_manager')
    auth_module.get_auth_manager = get_auth_manager
    sys.modules['game.core.auth.auth_manager'] = auth_module
    

    # 现在导入DexPage
    dex_page_path = os.path.join(current_dir, 'dex_page.py')
    spec = importlib.util.spec_from_file_location("dex_page", dex_page_path)
    dex_page_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dex_page_module)
    DexPage = dex_page_module.DexPage
    
except Exception as e:
    print(f"❌ 导入DexPage失败: {e}")
    # 如果导入失败，直接复制DexPage代码
    print("使用内嵌的DexPage代码...")

class DexPageLauncher:
    """DexPage启动器"""
    
    def __init__(self):
        # 初始化pygame
        pygame.init()
        
        # 设置窗口
        self.screen_width = 1400
        self.screen_height = 900
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("🔍 TCG卡牌图鉴测试器")
        
        # 时钟
        self.clock = pygame.time.Clock()
        
        # UI管理器
        self.ui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))
        
        # 数据库管理器
        self.db_manager = MockDatabaseManager()
        
        # 导航栏高度
        self.nav_bar_height = 90
        
        # DexPage实例
        try:
            self.dex_page = DexPage(
                self.screen_width, 
                self.screen_height, 
                self.ui_manager, 
                self.db_manager, 
                self.nav_bar_height
            )
            print("✅ DexPage创建成功")
        except Exception as e:
            print(f"❌ 创建DexPage失败: {e}")
            self.dex_page = None
        
        # 背景渐变
        self.background_surface = self.create_gradient_background()
        
        # 运行状态
        self.running = True
        
        print("🚀 DexPage启动器初始化完成")
        print("📋 控制说明:")
        print("   - 鼠标滚轮: 滚动页面")
        print("   - ESC: 退出程序") 
        print("   - 搜索框: 输入卡牌名称")
        print("   - 下拉菜单: 选择稀有度和类型")
        print("   - 按钮: 切换收集状态和效果筛选")
    
    def create_gradient_background(self):
        """创建渐变背景"""
        background = pygame.Surface((self.screen_width, self.screen_height))
        
        # 与MainScene相同的渐变色
        top_color = (240, 245, 251)
        bottom_color = (229, 231, 235)
        
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            
            pygame.draw.line(background, (r, g, b), (0, y), (self.screen_width, y))
        
        return background
    
    def draw_mock_navigation(self):
        """绘制模拟导航栏"""
        # 导航栏背景
        nav_surface = pygame.Surface((self.screen_width, self.nav_bar_height), pygame.SRCALPHA)
        nav_surface.fill((255, 255, 255, 220))
        self.screen.blit(nav_surface, (0, self.screen_height - self.nav_bar_height))
        
        # 导航栏标题
        nav_font = pygame.font.Font(None, 24)
        nav_text = nav_font.render("🔍 Modo Prueba - Colección TCG", True, (55, 65, 81))
        nav_rect = nav_text.get_rect(center=(self.screen_width // 2, self.screen_height - self.nav_bar_height // 2))
        self.screen.blit(nav_text, nav_rect)
        
        # 退出提示
        exit_font = pygame.font.Font(None, 16)
        exit_text = exit_font.render("Presiona ESC para salir", True, (107, 114, 128))
        self.screen.blit(exit_text, (20, self.screen_height - 25))
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F11:
                    # 切换全屏
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_r:
                    # 重新加载DexPage
                    if self.dex_page:
                        self.dex_page.cleanup()
                    self.dex_page = DexPage(
                        self.screen_width, 
                        self.screen_height, 
                        self.ui_manager, 
                        self.db_manager, 
                        self.nav_bar_height
                    )
                    print("🔄 DexPage重新加载")
            
            elif event.type == pygame.VIDEORESIZE:
                # 窗口大小调整
                self.screen_width, self.screen_height = event.size
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
                
                # 更新UI管理器
                self.ui_manager.set_window_resolution((self.screen_width, self.screen_height))
                
                # 更新DexPage
                if self.dex_page:
                    self.dex_page.resize(self.screen_width, self.screen_height)
                
                # 重新创建背景
                self.background_surface = self.create_gradient_background()
                
                print(f"📐 窗口调整: {self.screen_width}x{self.screen_height}")
            
            # 处理UI事件
            self.ui_manager.process_events(event)
            
            # 处理DexPage事件
            if self.dex_page:
                result = self.dex_page.handle_event(event)
                if result == "back_to_home":
                    print("🏠 返回主页信号接收")
    
    def update(self, dt):
        """更新"""
        # 更新UI管理器
        self.ui_manager.update(dt)
        
        # 更新DexPage
        if self.dex_page:
            self.dex_page.update(dt)
    
    def draw(self):
        """绘制"""
        # 绘制背景
        self.screen.blit(self.background_surface, (0, 0))
        
        # 绘制DexPage
        if self.dex_page:
            self.dex_page.draw(self.screen)
        else:
            # 错误状态
            error_font = pygame.font.Font(None, 36)
            error_text = error_font.render("❌ DexPage加载失败", True, (220, 38, 127))
            error_rect = error_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(error_text, error_rect)
        
        # 绘制模拟导航栏
        self.draw_mock_navigation()
        
        # 绘制性能信息
        self.draw_performance_info()
        
        # 更新显示
        pygame.display.flip()
    
    def draw_performance_info(self):
        """绘制性能信息"""
        fps = self.clock.get_fps()
        fps_color = (16, 185, 129) if fps >= 55 else (245, 158, 11) if fps >= 30 else (239, 68, 68)
        
        perf_font = pygame.font.Font(None, 18)
        fps_text = perf_font.render(f"FPS: {fps:.1f}", True, fps_color)
        self.screen.blit(fps_text, (self.screen_width - 80, 10))
        
        # 显示卡牌统计
        if self.dex_page:
            stats_text = perf_font.render(
                f"Cartas: {len(self.dex_page.filtered_cards)}/{self.dex_page.total_cards}", 
                True, (107, 114, 128)
            )
            self.screen.blit(stats_text, (self.screen_width - 150, 30))
    
    def run(self):
        """运行启动器"""
        print("🎮 启动DexPage测试器...")
        
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
        
        # 清理
        if self.dex_page:
            self.dex_page.cleanup()
        
        pygame.quit()
        print("✅ DexPage测试器退出")

def main():
    """主函数"""
    print("🚀 启动TCG卡牌图鉴测试器")
    print("=" * 50)
    
    try:
        launcher = DexPageLauncher()
        launcher.run()
    except Exception as e:
        print(f"❌ 启动器运行失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)
    print("👋 测试完成")

if __name__ == "__main__":
    main()