import pygame

pygame.init()
pygame.font.init()

fonts = pygame.font.get_fonts()
print("系统支持的字体数量:", len(fonts))
for name in sorted(fonts):
    print(name)
