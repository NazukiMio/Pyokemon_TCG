import pygame
import pygame_gui
import json
import os

# 初始化 Pygame
pygame.init()
window_size = (1200, 700)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Pokémon Card Viewer")
manager = pygame_gui.UIManager(window_size)

clock = pygame.time.Clock()
running = True

# 设置资源路径（相对 tests 目录）
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CARD_JSON_PATH = os.path.join(BASE_DIR, "card_assets", "cards.json")
IMAGE_DIR = os.path.join(BASE_DIR, "card_assets", "images")

# 加载卡牌数据
with open(CARD_JSON_PATH, encoding='utf-8') as f:
    cards = json.load(f)

# 只显示前 10 张卡
cards = cards[:10]
card_index = 0

# 加载图片函数
def load_card_image(image_path):
    try:
        if os.path.exists(image_path):
            return pygame.image.load(image_path).convert_alpha()
        else:
            print(f"[警告] 图片不存在: {image_path}")
    except Exception as e:
        print(f"[错误] 图片加载失败: {e}")
    return None

# 创建 UI 按钮
prev_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((50, 600), (100, 50)),
                                           text='<< 上一张',
                                           manager=manager)
next_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((1050, 600), (100, 50)),
                                           text='下一张 >>',
                                           manager=manager)

# 主循环
while running:
    time_delta = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == prev_button and card_index > 0:
                    card_index -= 1
                if event.ui_element == next_button and card_index < len(cards) - 1:
                    card_index += 1

        manager.process_events(event)

    # 渲染
    window.fill((30, 30, 30))
    manager.update(time_delta)
    manager.draw_ui(window)

    # 当前卡牌信息
    card = cards[card_index]
    font = pygame.font.SysFont("Arial", 20)

    # 图片（用 card["id"] 拼接完整路径更安全）
    card_image_path = card["image"]
    if not os.path.isabs(card_image_path):
        card_image_path = os.path.join(IMAGE_DIR, os.path.basename(card_image_path))

    image = load_card_image(card_image_path)
    if image:
        image = pygame.transform.scale(image, (240, 340))
        window.blit(image, (50, 100))

    # 信息区
    y = 100
    lines = [
        f"Name: {card.get('name', '')}",
        f"HP: {card.get('hp', 0)}",
        f"Type(s): {', '.join(card.get('types', []))}",
        f"Rarity: {card.get('rarity', 'Unknown')}",
        "Attacks:"
    ] + [f" - {atk.get('name', '')} ({atk.get('damage', '')})" for atk in card.get('attacks', [])]

    for line in lines:
        text_surface = font.render(line, True, (255, 255, 255))
        window.blit(text_surface, (350, y))
        y += 30

    pygame.display.update()

pygame.quit()
