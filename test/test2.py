import pygame
import sys
import json
import cv2
import math
import numpy as np

# 初始化
pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
pygame.display.set_caption("Juego de Cartas Coleccionables")
clock = pygame.time.Clock()

video_path = "assets/mages/video/bg.mp4"
# 视频背景初始化
class VideoBackground:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print(f"错误：无法打开视频文件 {video_path}")
            self.is_valid = False
            return
        self.is_valid = True
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"视频加载成功：{self.width}x{self.height}, {self.frame_count}帧, {self.fps}fps")
        
        # 读取第一帧
        self.success, self.current_frame = self.cap.read()
        
        # 创建Pygame表面用于显示视频
        self.surface = None
        self.update_surface()
    
    def update(self):
        if not self.is_valid:
            return None
            
        # 读取下一帧
        self.success, self.current_frame = self.cap.read()
        
        # 如果到达视频末尾，重新开始
        if not self.success:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.success, self.current_frame = self.cap.read()
            
        self.update_surface()
        return self.surface
    
    def update_surface(self):
        if not self.is_valid or self.current_frame is None:
            return
            
        # 将OpenCV的BGR格式转换为Pygame的RGB格式
        frame = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        
        # 创建Pygame表面
        self.surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    
    def resize(self, target_width, target_height):
        if not self.is_valid or self.current_frame is None:
            return None
            
        # 计算缩放比例
        w_scale = target_width / self.width
        h_scale = target_height / self.height
        
        # 选择较大的缩放比例以确保覆盖整个屏幕
        scale = max(w_scale, h_scale)
        
        new_width = int(self.width * scale)
        new_height = int(self.height * scale)
        
        # 缩放OpenCV帧
        resized_frame = cv2.resize(self.current_frame, (new_width, new_height))
        
        # 裁剪到目标尺寸（如果需要）
        start_x = max(0, (new_width - target_width) // 2)
        start_y = max(0, (new_height - target_height) // 2)
        cropped_frame = resized_frame[start_y:start_y+target_height, start_x:start_x+target_width]
        
        # 确保裁剪后的尺寸匹配目标尺寸
        if cropped_frame.shape[1] != target_width or cropped_frame.shape[0] != target_height:
            cropped_frame = cv2.resize(cropped_frame, (target_width, target_height))
        
        # 转换为RGB并创建Pygame表面
        rgb_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)
        return pygame.surfarray.make_surface(rgb_frame.swapaxes(0, 1))
    
    def close(self):
        if self.is_valid:
            self.cap.release()

# 初始化视频背景
try:
    # 替换为你的视频文件路径
    video_bg = VideoBackground("background_video.mp4")
except Exception as e:
    print(f"视频加载错误: {e}")
    video_bg = None

# 加载字体
def load_font(size, font_name="arial"):
    try:
        if font_name.lower() == "pokemon":
            return pygame.font.Font("pokemon.ttf", size)
        else:
            return pygame.font.SysFont(font_name, size, bold=True)
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
breath_alpha = 255  # 呼吸效果的透明度
breath_direction = -1  # 呼吸效果的方向，-1为减小，1为增加
breath_speed = 6.0  # 呼吸效果的速度（每帧透明度变化值）

# 绘图函数
def draw_subtitle(screen, w, h):
    # 使用Arial字体，并且让字体变小
    font = load_font(int(h * 0.035), "arial")
    text = font.render("Juego de Cartas Coleccionables", True, WHITE)
    
    # 将位置调整到logo下方，进一步往下移动
    # 给logo留出更多空间，确保不会重叠
    text_rect = text.get_rect(center=(w // 2, int(h * 0.35)))

    # 计算背景矩形
    bg_rect = text_rect.inflate(w * 0.015, h * 0.01)  # 缩小背景矩形
    
    # 绘制圆角矩形
    border_radius = 15  # 设置圆角半径
    
    # 绘制外边框效果
    pygame.draw.rect(screen, DARK_BLUE, bg_rect.inflate(10, 10), border_radius=border_radius)
    
    # 绘制矩形背景
    pygame.draw.rect(screen, RED, bg_rect, border_radius=border_radius)
    
    # 绘制下半部分（平坦化处理）
    bottom_rect = pygame.Rect(bg_rect.x, bg_rect.y + bg_rect.height // 2 - 5, 
                              bg_rect.width, bg_rect.height // 2 + 5)
    pygame.draw.rect(screen, DARK_RED, bottom_rect, border_radius=border_radius)

    # 文字阴影
    for dx in [-1, 1]:
        for dy in [-1, 1]:
            screen.blit(font.render("Juego de Cartas Coleccionables", True, DARK_RED), text_rect.move(dx, dy))
    screen.blit(text, text_rect)

def draw_start_button(screen, w, h, alpha):
    font = load_font(int(h * 0.045))
    
    # 渲染文本
    text = font.render("¡Getto Daze!", True, WHITE)
    
    # 计算文本位置（居中）
    text_rect = text.get_rect(center=(w // 2, int(h * 0.65)))
    
    # 创建一个带有一些内边距的按钮碰撞区域（比文本区域大）
    padding = 20
    button_rect = text_rect.inflate(padding * 2, padding * 2)
    
    # 创建临时表面绘制带透明度的文本
    temp_surface = pygame.Surface((text.get_width(), text.get_height()), pygame.SRCALPHA)
    temp_surface.fill((0, 0, 0, 0))  # 完全透明背景
    temp_surface.blit(text, (0, 0))
    temp_surface.set_alpha(alpha)
    
    # 绘制到屏幕
    screen.blit(temp_surface, text_rect)
    
    # 调试 - 显示按钮点击区域（测试完成后可注释掉）
    # pygame.draw.rect(screen, (255, 0, 0, 128), button_rect, 2)  
    
    return button_rect

def draw_logo(screen, screen_w, screen_h):
    try:
        with open("assets/images/json/logopoke_pixel_1024w.json", "r") as f:
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

def draw_version(screen, w, h):
    font = load_font(int(h * 0.025))
    text = font.render("Pygame Edition", True, WHITE)
    screen.blit(text, (30, h - 50))

def draw_main_menu_buttons(screen, w, h):
    font = load_font(int(h * 0.045))
    texts = ["Iniciar sesión", "Registrarse", "Salir"]
    buttons = []
    for i, t in enumerate(texts):
        rect = pygame.Rect(w // 2 - 150, int(h * 0.42 + i * h * 0.1), 300, 70)
        pygame.draw.rect(screen, (255, 255, 0), rect, border_radius=12)
        pygame.draw.rect(screen, (150, 100, 0), rect, 4, border_radius=12)
        txt = font.render(t, True, BLACK)
        screen.blit(txt, txt.get_rect(center=rect.center))
        buttons.append(rect)
    return buttons

# 主循环
try:
    while True:
        w, h = screen.get_size()
        
        # 更新并绘制视频背景
        if video_bg and video_bg.is_valid:
            # 调整视频尺寸以适应当前窗口
            bg_surface = video_bg.resize(w, h)
            if bg_surface:
                screen.blit(bg_surface, (0, 0))
            else:
                # 如果视频帧处理失败，使用纯色背景
                screen.fill((30, 30, 60))
                
            # 更新视频到下一帧
            video_bg.update()
        else:
            # 如果没有有效的视频背景，使用纯色背景
            screen.fill((30, 30, 60))
            
        # 绘制UI元素
        draw_logo(screen, w, h)
        draw_subtitle(screen, w, h)

        if show_main_menu:
            menu_buttons = draw_main_menu_buttons(screen, w, h)
        else:
            draw_version(screen, w, h)
            
            # 呼吸效果动画计算
            breath_alpha += breath_direction * breath_speed
            if breath_alpha <= 120:  # 最小透明度为120
                breath_alpha = 120
                breath_direction = 1
            elif breath_alpha >= 255:  # 最大透明度为255
                breath_alpha = 255
                breath_direction = -1
            
            # 绘制按钮并获取碰撞区域    
            btn_rect = draw_start_button(screen, w, h, breath_alpha)
            
            # 调试 - 绘制点击区域的边界框
            # pygame.draw.rect(screen, (255, 0, 0), btn_rect, 2)

        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if video_bg:
                    video_bg.close()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # 如果在主菜单前的状态，检查"¡Getto Daze!"按钮是否被点击
                if not show_main_menu:
                    if btn_rect.collidepoint(mouse_pos):
                        print("按钮被点击!")  # 调试输出
                        start_clicked = True
                        show_main_menu = True  # 直接切换到主菜单
                # 如果在主菜单状态，检查菜单按钮是否被点击
                else:
                    for i, button in enumerate(menu_buttons):
                        if button.collidepoint(mouse_pos):
                            print(f"菜单按钮 {i} 被点击!")  # 调试输出
                            # 这里可以添加菜单按钮的处理逻辑
                            if i == 2:  # "Salir" 按钮
                                if video_bg:
                                    video_bg.close()
                                pygame.quit()
                                sys.exit()

        # 处理按钮点击后的效果
        if start_clicked:
            # 已经在鼠标点击事件中直接设置了 show_main_menu = True
            pass
            
        pygame.display.flip()
        clock.tick(60)
        
except Exception as e:
    print(f"发生错误: {e}")
    if video_bg:
        video_bg.close()
    pygame.quit()
    sys.exit()