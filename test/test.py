import pygame
import sys
import os
import json

# 初始化
pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
pygame.display.set_caption("Juego de Cartas Coleccionables")
clock = pygame.time.Clock()

# 加载字体（你可以用Pokemon字体替换路径）
def load_font(size):
    try:
        return pygame.font.Font("pokemon.ttf", size)
    except:
        return pygame.font.SysFont("arial", size, bold=True)

# 颜色
RED = (200, 0, 0)
DARK_RED = (150, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 150)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 状态
show_main_menu = False
start_blink = True
blink_timer = 0
start_clicked = False

# 加载背景帧
frame_files = [f for f in os.listdir('assets/images/frame/framesBGMain') if f.endswith('.png')]
frame_files.sort()  # 确保帧按顺序加载
frames = [pygame.image.load(os.path.join('assets/images/frame/framesBGMain', f)) for f in frame_files]

# 控制动画播放
frame_index = 0
frame_timer = 0

# 工具函数

def draw_subtitle():
    font = load_font(60)
    text = font.render("Juego de Cartas Coleccionables", True, WHITE)
    text_rect = text.get_rect(center=(960, 250))

    # 红色背景 + 蓝色边框
    bg_rect = text_rect.inflate(40, 40)
    border_rect = bg_rect.inflate(10, 10)

    # 画蓝色边框 + 内斜面（简单模拟：偏移的暗蓝层）
    pygame.draw.rect(screen, DARK_BLUE, border_rect.move(4, 4))
    pygame.draw.rect(screen, BLUE, border_rect)

    # 画红色背景（上亮下暗形成立体感）
    pygame.draw.rect(screen, RED, bg_rect)
    pygame.draw.rect(screen, DARK_RED, (bg_rect.x, bg_rect.y + bg_rect.height // 2, bg_rect.width, bg_rect.height // 2))

    # 文字描边（稍暗的红色）
    for dx in [-2, 2]:
        for dy in [-2, 2]:
            screen.blit(font.render("Juego de Cartas Coleccionables", True, DARK_RED), text_rect.move(dx, dy))
    screen.blit(text, text_rect)

def draw_start_button(blink):
    font = load_font(50)
    color = WHITE if blink else DARK_RED
    text = font.render("Comenzar Juego", True, color)
    text_rect = text.get_rect(center=(960, 600))
    screen.blit(text, text_rect)
    return text_rect

def draw_logo(screen, screen_w, screen_h):
    try:
        with open("assets/images/json/logopoke_pixel_256w.json", "r") as f:
            data = json.load(f)

        pixels = data["pixels"]
        img_w = data["width"]
        img_h = data["height"]

        # 创建一个支持Alpha的Surface
        logo_surface = pygame.Surface((img_w, img_h), pygame.SRCALPHA)

        # 将像素数据绘制到Surface
        for y in range(img_h):
            for x in range(img_w):
                r, g, b, a = pixels[y][x]
                logo_surface.set_at((x, y), (r, g, b, a))

        # 计算缩放比例
        max_width = int(screen_w * 0.4)
        scale = max_width / img_w
        scaled_size = (int(img_w * scale), int(img_h * scale))
        logo_surface = pygame.transform.smoothscale(logo_surface, scaled_size)

        # 居中绘制
        pos_x = screen_w // 2 - scaled_size[0] // 2
        pos_y = int(screen_h * 0.08)
        screen.blit(logo_surface, (pos_x, pos_y))

    except Exception as e:
        print(f"[LOGO ERROR] {e}")
        pygame.draw.rect(screen, (180, 180, 180), (screen_w//2 - 100, int(screen_h * 0.07), 200, 100), border_radius=10)

def draw_version():
    font = load_font(30)
    text = font.render("Pygame Edition", True, WHITE)
    screen.blit(text, (30, 1020))

def draw_main_menu_buttons():
    font = load_font(48)
    texts = ["Iniciar sesión", "Registrarse", "Salir"]
    buttons = []
    for i, t in enumerate(texts):
        rect = pygame.Rect(810, 450 + i * 100, 300, 70)
        pygame.draw.rect(screen, (255, 255, 0), rect, border_radius=12)
        pygame.draw.rect(screen, (150, 100, 0), rect, 4, border_radius=12)  # 边框模拟精灵风格
        txt = font.render(t, True, BLACK)
        screen.blit(txt, txt.get_rect(center=rect.center))
        buttons.append(rect)
    return buttons

# 主循环
while True:
    screen.fill((30, 30, 60))

    # 处理背景帧
    frame_timer += 1
    if frame_timer >= 4:  # 每4帧显示1帧（15fps时，40帧 = 1秒）
        frame_timer = 0
        frame_index = (frame_index + 1) % len(frames)  # 循环播放帧
    screen.blit(frames[frame_index], (0, 0))  # 绘制背景帧

    draw_logo(screen, screen.get_width(), screen.get_height())
    draw_subtitle()

    if show_main_menu:
        draw_main_menu_buttons()
    else:
        draw_version()
        blink_timer += 1
        if blink_timer >= 30:
            start_blink = not start_blink
            blink_timer = 0
        btn_rect = draw_start_button(start_blink)

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not show_main_menu and btn_rect.collidepoint(event.pos):
                start_clicked = True

    if start_clicked:
        blink_timer += 1
        if blink_timer % 5 == 0:
            start_blink = not start_blink
        if blink_timer > 25:
            show_main_menu = True
            start_clicked = False
            blink_timer = 0

    pygame.display.flip()
    clock.tick(60)  # 控制帧率
