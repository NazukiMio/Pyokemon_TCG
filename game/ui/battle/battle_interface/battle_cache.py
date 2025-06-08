"""
战斗缓存系统 - 专为战斗界面优化的卡牌缓存
"""

import pygame
import os
import time
from typing import Dict, Optional, List

class BattleCardRenderer:
    """简化的战斗卡牌渲染器"""
    
    # 战斗界面专用颜色
    CARD_BG = (45, 50, 60)
    CARD_BORDER = (120, 130, 150)
    CARD_SELECTED = (255, 215, 0)  # 金色选中
    POKEMON_BORDER = (100, 180, 100)  # 绿色Pokemon边框
    TRAINER_BORDER = (100, 100, 180)  # 蓝色训练师边框
    ENERGY_BORDER = (180, 180, 100)   # 黄色能量边框
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cache = {}  # 渲染缓存
        
        # 字体
        try:
            self.name_font = pygame.font.SysFont("arial", 12, bold=True)
            self.info_font = pygame.font.SysFont("arial", 10)
        except:
            self.name_font = pygame.font.Font(None, 12)
            self.info_font = pygame.font.Font(None, 10)
    
    def render_card(self, card_instance, image_cache, selected: bool = False) -> pygame.Surface:
        """
        渲染卡牌（简化版，专注清晰度）
        
        Args:
            card_instance: 卡牌实例
            image_cache: 图片缓存
            selected: 是否选中
        """
        # 生成缓存键
        cache_key = f"{card_instance.card.id}_{self.width}_{self.height}_{selected}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 创建卡牌表面
        card_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # 确定卡牌类型和边框颜色
        border_color = self._get_card_border_color(card_instance.card)
        if selected:
            border_color = self.CARD_SELECTED
        
        # 绘制背景和边框
        pygame.draw.rect(card_surf, self.CARD_BG, card_surf.get_rect(), border_radius=4)
        border_width = 3 if selected else 2
        pygame.draw.rect(card_surf, border_color, card_surf.get_rect(), border_width, border_radius=4)
        
        # 绘制卡牌图片
        image_rect = pygame.Rect(4, 4, self.width - 8, int((self.width - 8) * 1.4))  # 保持卡牌比例
        if image_rect.bottom > self.height - 25:  # 为底部文字留空间
            image_rect.height = self.height - 29
        
        self._draw_card_image(card_surf, card_instance, image_cache, image_rect)
        
        # 绘制卡牌信息
        self._draw_card_info(card_surf, card_instance, image_rect.bottom + 2)
        
        # 缓存渲染结果
        self.cache[cache_key] = card_surf
        return card_surf
    
    def _get_card_border_color(self, card):
        """获取卡牌边框颜色"""
        if hasattr(card, 'hp') and card.hp:
            return self.POKEMON_BORDER
        elif hasattr(card, 'subtypes') and card.subtypes:
            if 'Energy' in card.subtypes:
                return self.ENERGY_BORDER
            else:
                return self.TRAINER_BORDER
        else:
            return self.TRAINER_BORDER
    
    def _draw_card_image(self, surface, card_instance, image_cache, image_rect):
        """绘制卡牌图片"""
        image_path = None
        if hasattr(card_instance.card, 'id') and card_instance.card.id:
            # 这里需要获取图片路径，可能需要传入card_manager
            # 暂时使用简化方式
            card_id = card_instance.card.id
            image_path = f"card_assets/images/{card_id}.png"
        
        if image_path and image_path in image_cache:
            # 缩放图片到适合大小
            image = image_cache[image_path]
            scaled_image = pygame.transform.scale(image, (image_rect.width, image_rect.height))
            surface.blit(scaled_image, image_rect)
        else:
            # 绘制占位符
            pygame.draw.rect(surface, (80, 80, 80), image_rect)
            
            # "无图片"文字
            no_img_text = self.info_font.render("No Image", True, (200, 200, 200))
            text_rect = no_img_text.get_rect(center=image_rect.center)
            surface.blit(no_img_text, text_rect)
    
    def _draw_card_info(self, surface, card_instance, y_start):
        """绘制卡牌信息"""
        # 卡牌名称（截断长名称）
        name = card_instance.card.name
        if len(name) > 10:
            name = name[:8] + ".."
        
        name_text = self.name_font.render(name, True, (255, 255, 255))
        name_x = (self.width - name_text.get_width()) // 2
        surface.blit(name_text, (name_x, y_start))
        
        # HP或类型信息
        info_text = ""
        if hasattr(card_instance.card, 'hp') and card_instance.card.hp:
            info_text = f"HP: {card_instance.card.hp}"
        else:
            info_text = "Trainer"
        
        info_surface = self.info_font.render(info_text, True, (200, 200, 200))
        info_x = (self.width - info_surface.get_width()) // 2
        surface.blit(info_surface, (info_x, y_start + 12))
    
    def clear_cache(self):
        """清理渲染缓存"""
        self.cache.clear()


class BattleCache:
    """战斗缓存系统"""
    
    def __init__(self, game_manager):
        self.game_manager = game_manager
        
        # 图片缓存
        self._image_cache = {}
        
        # 卡牌渲染器
        self.card_renderers = {
            'hand': BattleCardRenderer(80, 110),      # 手牌大小
            'field': BattleCardRenderer(100, 140),    # 战场大小
            'bench': BattleCardRenderer(60, 84),      # 后备大小
            'hover': BattleCardRenderer(160, 220)     # 悬停放大
        }
        
        # 预加载状态
        self._preloaded = False
        
        print("🎮 战斗缓存系统已初始化")
    
    def preload_battle_assets(self):
        """预加载战斗资源"""
        if self._preloaded:
            print("✅ 战斗资源已预加载")
            return
        
        print("📦 开始预加载战斗资源...")
        start_time = time.time()
        
        try:
            # 预加载常用卡牌图片
            self._preload_card_images()
            
            self._preloaded = True
            load_time = time.time() - start_time
            print(f"✅ 战斗资源预加载完成 ({load_time:.2f}秒)")
            print(f"   图片缓存: {len(self._image_cache)} 张")
            
        except Exception as e:
            print(f"❌ 预加载战斗资源失败: {e}")
    
    def _preload_card_images(self):
        """预加载卡牌图片"""
        # 获取当前可能用到的卡牌（来自游戏状态）
        cards_to_preload = []
        
        # 可以从battle_controller获取当前战斗中的卡牌
        # 这里先实现基础版本，预加载一些常见卡牌
        
        # 获取图片路径并加载
        for card_id in cards_to_preload[:50]:  # 限制预加载数量
            image_path = f"card_assets/images/{card_id}.png"
            self._load_image_to_cache(image_path)
    
    def _load_image_to_cache(self, image_path: str):
        """加载图片到缓存"""
        if image_path in self._image_cache:
            return
        
        if os.path.exists(image_path):
            try:
                self._image_cache[image_path] = pygame.image.load(image_path)
                # print(f"📸 加载图片: {image_path}")
            except Exception as e:
                print(f"❌ 加载图片失败 {image_path}: {e}")
    
    def get_cached_image(self, image_path: str) -> Optional[pygame.Surface]:
        """获取缓存图片"""
        if image_path not in self._image_cache:
            self._load_image_to_cache(image_path)
        
        return self._image_cache.get(image_path)
    
    def render_card(self, card_instance, size_type: str = 'hand', selected: bool = False) -> Optional[pygame.Surface]:
        """
        渲染卡牌
        
        Args:
            card_instance: 卡牌实例
            size_type: 大小类型 ('hand', 'field', 'bench', 'hover')
            selected: 是否选中
        """
        if size_type not in self.card_renderers:
            size_type = 'hand'
        
        renderer = self.card_renderers[size_type]
        return renderer.render_card(card_instance, self._image_cache, selected)
    
    def get_card_image_path(self, card_id: str) -> str:
        """获取卡牌图片路径"""
        return f"card_assets/images/{card_id}.png"
    
    def preload_cards_from_battle(self, battle_controller):
        """从战斗控制器预加载卡牌"""
        if not battle_controller or not battle_controller.current_battle:
            return
        
        print("🃏 从战斗状态预加载卡牌图片...")
        
        try:
            battle = battle_controller.current_battle
            cards_to_load = set()
            
            # 收集所有玩家的卡牌
            for player_id, player_state in battle.player_states.items():
                # 手牌
                for card in player_state.hand:
                    if hasattr(card.card, 'id'):
                        cards_to_load.add(card.card.id)
                
                # 卡组（只预加载前几张）
                for card in player_state.deck[:10]:  # 限制数量
                    if hasattr(card.card, 'id'):
                        cards_to_load.add(card.card.id)
                
                # 战场上的Pokemon
                if player_state.active_pokemon and hasattr(player_state.active_pokemon.card, 'id'):
                    cards_to_load.add(player_state.active_pokemon.card.id)
                
                for pokemon in player_state.bench_pokemon:
                    if hasattr(pokemon.card, 'id'):
                        cards_to_load.add(pokemon.card.id)
            
            # 加载图片
            loaded_count = 0
            for card_id in cards_to_load:
                image_path = self.get_card_image_path(card_id)
                if self.get_cached_image(image_path):
                    loaded_count += 1
            
            print(f"✅ 预加载完成: {loaded_count}/{len(cards_to_load)} 张卡牌图片")
            
        except Exception as e:
            print(f"❌ 从战斗状态预加载失败: {e}")
    
    def cleanup(self):
        """清理缓存"""
        print("🧹 清理战斗缓存...")
        
        self._image_cache.clear()
        for renderer in self.card_renderers.values():
            renderer.clear_cache()
        
        self._preloaded = False
        print("✅ 战斗缓存清理完成")