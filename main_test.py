import pygame
import sys
import json
import cv2
import numpy as np
from threading import Thread
import time

# 导入认证相关模块 - 添加在其他import语句后
from game.core.scene_manager import SceneManager
from game.scenes.login_scene import LoginScene
from game.scenes.register_scene import RegisterScene
from game.scenes.main_menu_scene import MainMenuScene

# 初始化
pygame.init()
screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
pygame.display.set_caption("Juego de Cartas Coleccionables")
clock = pygame.time.Clock()

class VideoBackground:
    def __init__(self, video_path, target_size=(1920, 1080)):
        self.video_path = video_path
        self.target_size = target_size
        self.cap = cv2.VideoCapture(video_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame = None
        self.surface = None
        self.running = True
        
        # 启动线程读取视频
        self.thread = Thread(target=self._update, daemon=True)
        self.thread.start()
    
    def _update(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                # 视频结束，重新开始播放
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    break
            
            # 调整帧的大小以匹配目标尺寸
            frame = cv2.resize(frame, self.target_size)
            # 从BGR（OpenCV默认）转换为RGB（Pygame使用）
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_frame = frame
            
            # 控制帧率
            time.sleep(1 / self.fps)
    
    def get_surface(self, size=None):
        if self.current_frame is None:
            return None
        
        target_size = size if size else self.target_size
        # 如果尺寸不同，调整大小
        if target_size != (self.current_frame.shape[1], self.current_frame.shape[0]):
            frame = cv2.resize(self.current_frame, target_size)
        else:
            frame = self.current_frame
        
        # 创建空的pygame表面
        surface = pygame.Surface(target_size)
        
        # 将numpy数组转换为pygame surface，不使用surfarray
        # 这避免了旋转问题
        pygame_frame = pygame.image.frombuffer(
            frame.tobytes(), (frame.shape[1], frame.shape[0]), 'RGB')
        
        # 如果目标尺寸与帧尺寸不同，再次调整大小
        if target_size != (frame.shape[1], frame.shape[0]):
            pygame_frame = pygame.transform.scale(pygame_frame, target_size)
        
        return pygame_frame
    
    def update_size(self, new_size):
        self.target_size = new_size
    
    def close(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap is not None:
            self.cap.release()

video_bg = VideoBackground("assets/videos/bg.mp4")

# 加载字体
def load_font(size, font_name="default", bold=False):
    try:
        if font_name.lower() == "pokemon":
            # 尝试加载宝可梦字体
            return pygame.font.Font("assets/fonts/Pokemon-Solid-Normal.ttf", size)
        elif font_name.lower() == "power_clear":
            # 尝试加载power-clear字体
            return pygame.font.Font("assets/fonts/power-clear.ttf", size)
        else:
            # 默认使用power-clear
            try:
                return pygame.font.Font("arial", size, bold=bold)
            except:
                # 回落到Arial
                return pygame.font.SysFont("arial", size, bold=bold)
    except Exception as e:
        print(f"字体加载错误: {e}")
        # 出错时回落到系统Arial字体
        return pygame.font.SysFont("arial", size, bold=bold)

# 颜色
RED = (200, 0, 0)
DARK_RED = (150, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 150)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# 新的颜色方案 - 基于#422a77
BUTTON_BASE = (66, 42, 119)  # #422a77
BUTTON_GRADIENT_TOP = (86, 62, 139)  # 比基础色略亮
BUTTON_GRADIENT_BOTTOM = (46, 32, 99)  # 比基础色略暗

# 悬停状态下的色彩
BUTTON_HOVER_GRADIENT_TOP = (106, 82, 159)  # 悬停时顶部颜色更亮
BUTTON_HOVER_GRADIENT_BOTTOM = (76, 52, 129)  # 悬停时底部颜色也更亮

# 边框和装饰颜色
BUTTON_BORDER = (36, 22, 89)  # 比基础色更暗，用于边框
BUTTON_TEXT_SHADOW = (26, 12, 69)  # 文字阴影颜色

# 对话框颜色保持不变
DIALOG_BG = (245, 245, 245, 230)  # 对话框背景（带透明度）
DIALOG_BORDER = (80, 80, 80)  # 对话框边框

# 高亮颜色 - 用于按钮内部高光
HIGHLIGHT_COLOR = (150, 130, 220, 80)  # 淡紫色高光，半透明

# 状态
show_main_menu = False
start_blink = True
blink_timer = 0
start_clicked = False
breath_alpha = 255  # 新增：呼吸效果的透明度
breath_direction = -1  # 新增：呼吸效果的方向，-1为减小，1为增加
breath_speed = 8
show_exit_dialog = False  # 是否显示退出对话框
active_button = -1  # 当前悬停的按钮
dialog_confirm_hover = False  # 确认按钮悬停状态
dialog_cancel_hover = False  # 取消按钮悬停状态
getto_float_offset = 0  # 浮动偏移值
getto_float_speed = 0.5  # 浮动速度
getto_float_range = 8  # 浮动范围（像素）
getto_star_timer = 0  # 星星动画计时器

def load_button_resources():
    # 尝试加载按钮装饰图像
    try:
        button_decoration = pygame.image.load("assets/images/button_decoration.png").convert_alpha()
        button_decoration = pygame.transform.scale(button_decoration, (40, 40))
    except:
        # 如果加载失败，创建一个简单的装饰图形
        button_decoration = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(button_decoration, (255, 255, 255, 180), (20, 20), 15, 2)
        pygame.draw.circle(button_decoration, (255, 255, 255, 120), (20, 20), 12, 1)
    
    return button_decoration

button_decoration = load_button_resources()

# 创建渐变表面
def create_gradient_surface(width, height, color_top, color_bottom):
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        # 计算当前行的颜色
        r = int(color_top[0] * (1 - y/height) + color_bottom[0] * (y/height))
        g = int(color_top[1] * (1 - y/height) + color_bottom[1] * (y/height))
        b = int(color_top[2] * (1 - y/height) + color_bottom[2] * (y/height))
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    return surface

# 绘制美化的按钮
def draw_fancy_button(screen, rect, text, font, is_hover=False, decoration=None):
    # 创建圆角矩形路径
    border_radius = 15
    
    # 选择颜色基于悬停状态
    top_color = BUTTON_HOVER_GRADIENT_TOP if is_hover else BUTTON_GRADIENT_TOP
    bottom_color = BUTTON_HOVER_GRADIENT_BOTTOM if is_hover else BUTTON_GRADIENT_BOTTOM
    
    # 创建一个临时表面来绘制按钮（包括透明度）
    temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
    # 创建渐变背景
    gradient = create_gradient_surface(rect.width, rect.height, top_color, bottom_color)
    
    # 创建圆角蒙版
    mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255), (0, 0, rect.width, rect.height), border_radius=border_radius)
    
    # 在临时表面上绘制渐变和蒙版
    temp_surface.blit(gradient, (0, 0))
    
    # 使用BLEND_RGBA_MULT混合模式将蒙版应用到渐变
    # 这会保留蒙版中透明的部分，使渐变只在圆角矩形内显示
    final_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    final_surface.blit(temp_surface, (0, 0))
    final_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    
    # 绘制按钮阴影（只在矩形下方绘制）
    shadow_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 80), 
                     (0, 0, rect.width, rect.height), border_radius=border_radius)
    screen.blit(shadow_surface, (rect.x + 4, rect.y + 4))
    
    # 绘制按钮（应用了蒙版的渐变）
    screen.blit(final_surface, rect.topleft)
    
    # 绘制内边缘高光
    if is_hover:
        highlight_rect = pygame.Rect(2, 2, rect.width - 4, rect.height - 4)
        pygame.draw.rect(final_surface, (255, 255, 255, 60), 
                         highlight_rect, width=2, border_radius=border_radius-3)
        screen.blit(final_surface, rect.topleft)
    
    # 绘制边框
    pygame.draw.rect(screen, BUTTON_BORDER, rect, width=2, border_radius=border_radius)
    
    # 绘制装饰（如果有）
    if decoration:
        dec_rect = decoration.get_rect()
        dec_rect.midleft = (rect.x + 15, rect.centery)
        screen.blit(decoration, dec_rect)
        
        # 绘制装饰右侧
        dec_rect.midright = (rect.right - 15, rect.centery)
        screen.blit(decoration, dec_rect)
    
    # 绘制文本
    text_surface = font.render(text, True, WHITE)
    # 添加文本阴影
    text_shadow = font.render(text, True, (30, 30, 30))
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
    screen.blit(text_surface, text_rect)

    return rect

# 绘图函数
def draw_subtitle(screen, w, h):
    # 使用Arial字体，并且让字体变小
    font = load_font(int(h * 0.025), "arial")
    text = font.render("Juego de Cartas Coleccionables", True, WHITE)
    
    # 将位置调整到logo下方，进一步往下移动
    # 给logo留出更多空间，确保不会重叠
    text_rect = text.get_rect(center=(w // 2, int(h * 0.40)))

    # 计算背景矩形
    bg_rect = text_rect.inflate(w * 0.035, h * 0.005)  # 缩小背景矩形
    
    # 绘制圆角矩形
    border_radius = 5  # 设置圆角半径
    
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
    # 使用Pokemon字体
    font = load_font(int(h * 0.065), "pokemon")  # 字体进一步放大
    
    # 基础文字位置
    text_position = (w // 2, int(h * 0.80))
    
    # 创建深层次文字阴影效果（多层）
    shadow_colors = [
        (20, 10, 60, min(alpha, 180)),  # 深紫色阴影，较透明
        (86, 62, 139, min(alpha, 200)),  # 中间色调阴影，与按钮颜色匹配
        (150, 120, 220, min(alpha, 220))  # 浅紫色阴影，更亮
    ]
    
    # 阴影偏移距离
    shadow_offsets = [
        (-4, 4),  # 左下
        (4, 4),   # 右下
        (0, -2)   # 上方
    ]
    
    # 叠加式光晕效果参数
    glow_color = (150, 120, 220, min(alpha // 3, 60))  # 浅紫色光晕，非常透明
    glow_offset = 1  # 光晕偏移（像素）
    
    # 创建临时表面，大小足以容纳文字和所有效果
    padding = 30  # 额外的填充空间
    temp_width = int(w * 0.7)  # 足够宽的临时表面
    temp_height = int(h * 0.2)  # 足够高的临时表面
    temp_surface = pygame.Surface((temp_width, temp_height), pygame.SRCALPHA)
    
    # 渲染主文本
    main_text = font.render("¡Getto Daze!", True, WHITE)
    text_rect = main_text.get_rect(center=(temp_width // 2, temp_height // 2))
    
    # 绘制外发光效果（通过绘制多个偏移的半透明文本）
    for i in range(10):
        offset = glow_offset * (i + 1)
        glow_alpha = max(5, glow_color[3] - i * 6)  # 逐渐降低透明度
        current_glow = (glow_color[0], glow_color[1], glow_color[2], glow_alpha)
        
        # 四个方向的发光
        for dx, dy in [(offset, 0), (-offset, 0), (0, offset), (0, -offset)]:
            glow_text = font.render("¡Getto Daze!", True, current_glow)
            glow_rect = glow_text.get_rect(center=(temp_width // 2 + dx, temp_height // 2 + dy))
            temp_surface.blit(glow_text, glow_rect)
    
    # 绘制主要阴影
    for color, offset in zip(shadow_colors, shadow_offsets):
        shadow_text = font.render("¡Getto Daze!", True, color)
        shadow_rect = shadow_text.get_rect(center=(temp_width // 2 + offset[0], temp_height // 2 + offset[1]))
        temp_surface.blit(shadow_text, shadow_rect)
    
    # 绘制主文本
    temp_surface.blit(main_text, text_rect)
    
    # 添加上方漂浮星星效果
    stars = []
    # 随时间变化的星星位置 - 使用当前alpha值来创建变化
    star_seed = alpha % 255
    for i in range(5):
        # 计算星星位置（相对于文字位置的偏移）
        star_x = int(temp_width // 2 + (((star_seed * (i+1)) % 100) - 50) * 1.5)
        star_y = int(temp_height // 2 - 50 - ((star_seed + i * 20) % 30))
        stars.append((star_x, star_y))
    
    # 绘制星星
    for x, y in stars:
        # 星星大小随透明度变化
        star_size = 4 + (alpha % 20) // 10
        # 星星颜色（明亮黄色/白色）
        star_color = (255, 255, 200, min(255, alpha + 50))
        # 绘制简单的星星（十字形状）
        pygame.draw.line(temp_surface, star_color, (x-star_size, y), (x+star_size, y), 2)
        pygame.draw.line(temp_surface, star_color, (x, y-star_size), (x, y+star_size), 2)
        # 添加小圆点增强光芒感
        pygame.draw.circle(temp_surface, star_color, (x, y), star_size // 2)
    
    # 设置整体透明度
    temp_surface.set_alpha(alpha)
    
    # 最终绘制到屏幕
    temp_rect = temp_surface.get_rect(center=text_position)
    screen.blit(temp_surface, temp_rect)
    
    # 计算点击区域（稍微大于文本区域）
    click_padding = 40
    button_rect = main_text.get_rect(center=text_position)
    button_rect.inflate_ip(click_padding * 2, click_padding)  # 增加点击区域大小
    
    # 调试 - 显示按钮点击区域（测试完成后可注释掉）
    # pygame.draw.rect(screen, (255, 0, 0, 128), button_rect, 2)  
    
    return button_rect

def draw_logo(screen, screen_w, screen_h):
    try:
        with open("assets/images/json/logopoke_pixel_512w.json", "r") as f:
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
    global active_button
    font = load_font(int(h * 0.04), "power_clear")
    texts = ["Iniciar Sesión", "Registrarse", "Salir"]
    buttons = []
    
    # 获取鼠标位置
    mouse_pos = pygame.mouse.get_pos()
    
    for i, t in enumerate(texts):
        # 按钮位置和大小 - 调整为更加美观的尺寸与间距
        rect = pygame.Rect(w // 2 - 180, int(h * 0.5 + i * h * 0.12), 360, 80)
        
        # 检查鼠标是否悬停在按钮上
        is_hover = rect.collidepoint(mouse_pos)
        if is_hover:
            active_button = i
        
        # 绘制美化的按钮
        draw_fancy_button(screen, rect, t, font, is_hover=(i == active_button), decoration=button_decoration)
        buttons.append(rect)
    
    return buttons
# 添加绘制退出对话框的函数
def draw_exit_dialog(screen, w, h):
    global dialog_confirm_hover, dialog_cancel_hover
    
    # 创建半透明背景
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))  # 黑色半透明
    screen.blit(overlay, (0, 0))
    
    # 对话框尺寸和位置
    dialog_width, dialog_height = int(w * 0.4), int(h * 0.3)
    dialog_rect = pygame.Rect(w // 2 - dialog_width // 2, h // 2 - dialog_height // 2, 
                              dialog_width, dialog_height)
    
    # 绘制对话框阴影
    shadow_rect = dialog_rect.copy()
    shadow_rect.x += 8
    shadow_rect.y += 8
    pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=20)
    
    # 绘制对话框背景
    pygame.draw.rect(screen, DIALOG_BG, dialog_rect, border_radius=20)
    pygame.draw.rect(screen, DIALOG_BORDER, dialog_rect, width=3, border_radius=20)
    
    # 对话框内部高光
    inner_rect = dialog_rect.inflate(-6, -6)
    pygame.draw.rect(screen, (255, 255, 255, 80), inner_rect, width=1, border_radius=18)
    
    # 绘制对话框标题
    title_font = load_font(int(h * 0.04), "power_clear")
    title_text = title_font.render("¿Salir del juego?", True, (50, 50, 50))
    title_rect = title_text.get_rect(midtop=(dialog_rect.centerx, dialog_rect.y + 20))
    screen.blit(title_text, title_rect)
    
    # 绘制对话框消息
    msg_font = load_font(int(h * 0.03), "power_clear")
    msg_text = msg_font.render("¿Estás seguro de que quieres salir?", True, (80, 80, 80))
    msg_rect = msg_text.get_rect(center=(dialog_rect.centerx, dialog_rect.centery - 10))
    screen.blit(msg_text, msg_rect)
    
    # 获取鼠标位置
    mouse_pos = pygame.mouse.get_pos()
    
    # 绘制确认和取消按钮
    button_font = load_font(int(h * 0.035), "power_clear")
    
    # 确认按钮
    confirm_rect = pygame.Rect(dialog_rect.centerx - 140, dialog_rect.bottom - 70, 120, 50)
    dialog_confirm_hover = confirm_rect.collidepoint(mouse_pos)
    draw_fancy_button(screen, confirm_rect, "Sí", button_font, dialog_confirm_hover)
    
    # 取消按钮
    cancel_rect = pygame.Rect(dialog_rect.centerx + 20, dialog_rect.bottom - 70, 120, 50)
    dialog_cancel_hover = cancel_rect.collidepoint(mouse_pos)
    draw_fancy_button(screen, cancel_rect, "No", button_font, dialog_cancel_hover)
    
    return confirm_rect, cancel_rect

# 主循环
while True:
    w, h = screen.get_size()

    # 更新视频背景大小
    video_bg.update_size((w, h))
    
    # 获取当前视频帧并绘制
    bg_surface = video_bg.get_surface((w, h))
    if bg_surface:
        screen.blit(bg_surface, (0, 0))
    else:
        # 如果视频帧不可用，填充纯色
        screen.fill((30, 30, 60))

    draw_logo(screen, w, h)
    draw_subtitle(screen, w, h)

    if show_main_menu:
        menu_buttons = draw_main_menu_buttons(screen, w, h)
        if show_exit_dialog:
            confirm_rect, cancel_rect = draw_exit_dialog(screen, w, h)
    else:
        draw_version(screen, w, h)
        
        # 呼吸效果动画计算
        breath_alpha += breath_direction * breath_speed
        if breath_alpha <= 0:  # 最小透明度为0
            breath_alpha = 0
            breath_direction = 1
        elif breath_alpha >= 255:  # 最大透明度为255
            breath_alpha = 255
            breath_direction = -1
        
        # 浮动动画计算 
        getto_float_offset += getto_float_speed
        if getto_float_offset >= getto_float_range:
            getto_float_offset = getto_float_range
            getto_float_speed *= -1
        elif getto_float_offset <= -getto_float_range:
            getto_float_offset = -getto_float_range
            getto_float_speed *= -1

        # 星星动画计时器
        getto_star_timer += 1
        if getto_star_timer >= 60:
            getto_star_timer = 0

        # 计算最终的垂直位置
        final_y = int(h * 0.80) + int(getto_float_offset)
        
        # 绘制按钮并获取碰撞区域    
        btn_rect = draw_start_button(screen, w, h, breath_alpha)
        
        # 调试 - 绘制点击区域的边界框（可选，调试完成后可以移除）
        # pygame.draw.rect(screen, (255, 0, 0), btn_rect, 1)

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 清理视频资源（如果使用了视频背景）
            if 'video_bg' in globals():
                video_bg.close()
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not show_main_menu and btn_rect.collidepoint(event.pos):
                print("按钮被点击!")  # 调试输出
                
                # 替换下面的代码：
                # start_clicked = True
                # show_main_menu = True  # 直接切换到主菜单，简化过渡效果
                
                # 新代码 - 启动认证系统
                # 创建场景管理器
                scene_manager = SceneManager(screen)
                
                # 注册场景
                scene_manager.add_scene("login", LoginScene)
                scene_manager.add_scene("register", RegisterScene)
                scene_manager.add_scene("main_menu", MainMenuScene)
                
                # 运行场景管理器，从登录场景开始
                scene_manager.run("login")
                
                # 场景管理器返回后，可以选择退出或返回主界面
                sys.exit()  # 如果想退出游戏
                # 或者不返回，继续显示原界面

    pygame.display.flip()
    clock.tick(60)