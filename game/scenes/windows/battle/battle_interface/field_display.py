# ==== field_display.py ====
# 保存为: game/ui/battle/battle_interface/field_display.py

"""
战场显示 - 显示Pokemon战场
"""

import pygame
from typing import Optional, Dict, Any

class PokemonSlot:
    """Pokemon槽位"""
    
    def __init__(self, rect: pygame.Rect, is_active: bool = False):
        self.rect = rect
        self.is_active = is_active
        self.pokemon = None
        self.is_enemy = False
        
        # 颜色
        self.active_color = (100, 180, 100)  # 绿色 - 前排
        self.bench_color = (100, 100, 180)   # 蓝色 - 后备
        self.empty_color = (80, 80, 80)      # 灰色 - 空
        self.enemy_color = (180, 100, 100)   # 红色 - 敌方
        
        # 字体
        try:
            self.font = pygame.font.SysFont("arial", 12)
            self.small_font = pygame.font.SysFont("arial", 10)
        except:
            self.font = pygame.font.Font(None, 12)
            self.small_font = pygame.font.Font(None, 10)
    
    def set_pokemon(self, pokemon):
        """设置Pokemon"""
        self.pokemon = pokemon
    
    def draw(self, screen):
        """绘制槽位"""
        # 确定颜色
        if self.pokemon is None:
            color = self.empty_color
        elif self.is_enemy:
            color = self.enemy_color
        elif self.is_active:
            color = self.active_color
        else:
            color = self.bench_color
        
        # 绘制槽位
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
        
        if self.pokemon:
            # Pokemon名称
            name = self.pokemon.card.name
            if len(name) > 8:
                name = name[:6] + ".."
            
            name_text = self.font.render(name, True, (255, 255, 255))
            name_rect = name_text.get_rect(centerx=self.rect.centerx, y=self.rect.y + 5)
            screen.blit(name_text, name_rect)
            
            # HP信息
            hp_text = f"{self.pokemon.current_hp}/{self.pokemon.card.hp}"
            hp_surface = self.small_font.render(hp_text, True, (255, 255, 255))
            hp_rect = hp_surface.get_rect(centerx=self.rect.centerx, y=self.rect.bottom - 15)
            screen.blit(hp_surface, hp_rect)
        else:
            # 空槽位文字
            empty_text = "Vacío"
            empty_surface = self.font.render(empty_text, True, (150, 150, 150))
            empty_rect = empty_surface.get_rect(center=self.rect.center)
            screen.blit(empty_surface, empty_rect)


class FieldDisplay:
    """战场显示类"""
    
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.player_slots = []
        self.enemy_slots = []
        
        # 创建槽位
        self._create_slots()
    
    def _create_slots(self):
        """创建Pokemon槽位"""
        slot_width = 100
        slot_height = 80
        slot_spacing = 10
        
        # 敌方区域 (上方)
        enemy_y = self.rect.y + 20
        enemy_center_x = self.rect.centerx
        
        # 敌方前排 (1个)
        enemy_active_rect = pygame.Rect(
            enemy_center_x - slot_width // 2,
            enemy_y,
            slot_width,
            slot_height
        )
        enemy_active_slot = PokemonSlot(enemy_active_rect, is_active=True)
        enemy_active_slot.is_enemy = True
        self.enemy_slots.append(enemy_active_slot)
        
        # 敌方后备 (5个)
        bench_start_x = enemy_center_x - (5 * (slot_width + slot_spacing) - slot_spacing) // 2
        bench_y = enemy_y + slot_height + 10
        
        for i in range(5):
            bench_x = bench_start_x + i * (slot_width + slot_spacing)
            bench_rect = pygame.Rect(bench_x, bench_y, slot_width, slot_height)
            bench_slot = PokemonSlot(bench_rect, is_active=False)
            bench_slot.is_enemy = True
            self.enemy_slots.append(bench_slot)
        
        # 玩家区域 (下方)
        player_y = self.rect.bottom - 20 - slot_height
        
        # 玩家前排 (1个)
        player_active_rect = pygame.Rect(
            enemy_center_x - slot_width // 2,
            player_y,
            slot_width,
            slot_height
        )
        player_active_slot = PokemonSlot(player_active_rect, is_active=True)
        self.player_slots.append(player_active_slot)
        
        # 玩家后备 (5个)
        player_bench_y = player_y - slot_height - 10
        
        for i in range(5):
            bench_x = bench_start_x + i * (slot_width + slot_spacing)
            bench_rect = pygame.Rect(bench_x, player_bench_y, slot_width, slot_height)
            bench_slot = PokemonSlot(bench_rect, is_active=False)
            self.player_slots.append(bench_slot)
    
    def update_field_state(self, battle_state):
        """更新战场状态"""
        if not battle_state:
            return
        
        try:
            # 更新玩家Pokemon
            player_state = battle_state.player_states.get(battle_state.current_player_id)
            if player_state:
                # 前排Pokemon
                if player_state.active_pokemon and len(self.player_slots) > 0:
                    self.player_slots[0].set_pokemon(player_state.active_pokemon)
                
                # 后备Pokemon
                for i, bench_pokemon in enumerate(player_state.bench_pokemon):
                    if i + 1 < len(self.player_slots):
                        self.player_slots[i + 1].set_pokemon(bench_pokemon)
            
            # 更新敌方Pokemon（简化）
            enemy_id = None
            for pid in battle_state.player_states.keys():
                if pid != battle_state.current_player_id:
                    enemy_id = pid
                    break
            
            if enemy_id:
                enemy_state = battle_state.player_states[enemy_id]
                # 敌方前排
                if enemy_state.active_pokemon and len(self.enemy_slots) > 0:
                    self.enemy_slots[0].set_pokemon(enemy_state.active_pokemon)
                
                # 敌方后备
                for i, bench_pokemon in enumerate(enemy_state.bench_pokemon):
                    if i + 1 < len(self.enemy_slots):
                        self.enemy_slots[i + 1].set_pokemon(bench_pokemon)
        
        except Exception as e:
            print(f"❌ 更新战场状态失败: {e}")
    
    def draw(self, screen):
        """绘制战场"""
        # 背景
        pygame.draw.rect(screen, (30, 35, 45), self.rect)
        pygame.draw.rect(screen, (70, 80, 90), self.rect, 2)
        
        # 标题
        try:
            title_font = pygame.font.SysFont("arial", 18, bold=True)
        except:
            title_font = pygame.font.Font(None, 18)
        
        # title_text = title_font.render("战场", True, (255, 255, 255))
        # español_title = title_font.render("Campo de batalla", True, (255, 255, 255))
        title_text = title_font.render("Campo de batalla", True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=self.rect.centerx, y=self.rect.y + 5)
        screen.blit(title_text, title_rect)
        
        # 分隔线
        center_y = self.rect.centery
        pygame.draw.line(screen, (100, 100, 100), 
                        (self.rect.x + 10, center_y), 
                        (self.rect.right - 10, center_y), 2)
        
        # 绘制所有槽位
        for slot in self.enemy_slots + self.player_slots:
            slot.draw(screen)