"""
卡片数据管理器
从网络API获取和管理Pokemon卡片数据
"""

import requests
import json
import time
import os
from typing import Dict, List, Optional
import threading
from concurrent.futures import ThreadPoolExecutor

class CardDataManager:
    """
    卡片数据管理器
    从 pocket.pokemongohub.net 和 PokeAPI 获取卡片数据
    """
    
    def __init__(self, cache_dir: str = "data/cache"):
        """
        初始化卡片数据管理器
        
        Args:
            cache_dir: 缓存目录
        """
        self.cache_dir = cache_dir
        self.card_cache = {}
        self.pokemon_cache = {}
        self.last_update = 0
        self.cache_duration = 24 * 60 * 60  # 24小时缓存
        
        # API配置
        self.pokehub_base_url = "https://pocket.pokemongohub.net/api"
        self.pokeapi_base_url = "https://pokeapi.co/api/v2"
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 加载缓存数据
        self._load_cache()
        
        print("🃏 卡片数据管理器初始化完成")
    
    def _load_cache(self):
        """加载缓存数据"""
        cache_file = os.path.join(self.cache_dir, "card_cache.json")
        
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.card_cache = cache_data.get('cards', {})
                    self.pokemon_cache = cache_data.get('pokemon', {})
                    self.last_update = cache_data.get('last_update', 0)
                    print(f"✅ 加载缓存数据: {len(self.card_cache)} 张卡片")
        except Exception as e:
            print(f"❌ 加载缓存失败: {e}")
    
    def _save_cache(self):
        """保存缓存数据"""
        cache_file = os.path.join(self.cache_dir, "card_cache.json")
        
        try:
            cache_data = {
                'cards': self.card_cache,
                'pokemon': self.pokemon_cache,
                'last_update': time.time()
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            print(f"💾 缓存已保存: {len(self.card_cache)} 张卡片")
        except Exception as e:
            print(f"❌ 保存缓存失败: {e}")
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        return (time.time() - self.last_update) < self.cache_duration
    
    def get_card_pool(self, force_refresh: bool = False) -> List[Dict]:
        """
        获取卡片池
        
        Args:
            force_refresh: 是否强制刷新
            
        Returns:
            卡片数据列表
        """
        if not force_refresh and self._is_cache_valid() and self.card_cache:
            print(f"📦 使用缓存卡片池: {len(self.card_cache)} 张卡片")
            return list(self.card_cache.values())
        
        print("🔄 刷新卡片数据...")
        
        # 尝试从多个源获取数据
        cards = []
        
        # 1. 尝试从 Pokemon TCG Pocket Hub 获取
        try:
            pocket_cards = self._fetch_from_pocket_hub()
            if pocket_cards:
                cards.extend(pocket_cards)
                print(f"✅ 从 Pocket Hub 获取 {len(pocket_cards)} 张卡片")
        except Exception as e:
            print(f"⚠️ Pocket Hub 获取失败: {e}")
        
        # 2. 如果数据不足，从 PokeAPI 补充
        if len(cards) < 50:
            try:
                pokeapi_cards = self._fetch_from_pokeapi()
                cards.extend(pokeapi_cards)
                print(f"✅ 从 PokeAPI 补充 {len(pokeapi_cards)} 张卡片")
            except Exception as e:
                print(f"⚠️ PokeAPI 获取失败: {e}")
        
        # 3. 如果还是没有足够数据，使用默认卡片
        if len(cards) < 20:
            default_cards = self._generate_default_cards()
            cards.extend(default_cards)
            print(f"🔧 使用默认卡片: {len(default_cards)} 张")
        
        # 更新缓存
        self.card_cache = {card['id']: card for card in cards}
        self.last_update = time.time()
        self._save_cache()
        
        return cards
    
    def _fetch_from_pocket_hub(self) -> List[Dict]:
        """从 Pokemon TCG Pocket Hub 获取卡片数据"""
        cards = []
        
        try:
            # 注意：这个API可能不存在，这里是示例实现
            # 实际需要根据网站的API文档进行调整
            response = requests.get(
                f"{self.pokehub_base_url}/cards",
                timeout=10,
                headers={'User-Agent': 'PokemonTCG-Game/1.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for card_data in data.get('cards', []):
                    card = self._parse_pocket_hub_card(card_data)
                    if card:
                        cards.append(card)
            
        except requests.RequestException as e:
            print(f"🌐 Pocket Hub 网络请求失败: {e}")
            # 如果API不可用，返回空列表，让系统使用其他数据源
            return []
        
        return cards
    
    def _parse_pocket_hub_card(self, card_data: Dict) -> Optional[Dict]:
        """解析 Pocket Hub 卡片数据"""
        try:
            return {
                'id': f"pocket_{card_data.get('id', '')}",
                'name': card_data.get('name', 'Unknown'),
                'rarity': self._map_rarity(card_data.get('rarity', 'common')),
                'type': card_data.get('type', 'pokemon').lower(),
                'hp': card_data.get('hp', 0),
                'image_url': card_data.get('image_url', ''),
                'attacks': card_data.get('attacks', []),
                'weakness': card_data.get('weakness', {}),
                'resistance': card_data.get('resistance', {}),
                'retreat_cost': card_data.get('retreat_cost', 0),
                'source': 'pocket_hub'
            }
        except Exception as e:
            print(f"❌ 解析 Pocket Hub 卡片失败: {e}")
            return None
    
    def _fetch_from_pokeapi(self) -> List[Dict]:
        """从 PokeAPI 获取Pokemon数据并转换为卡片"""
        cards = []
        
        try:
            # 获取前151个Pokemon（第一代）
            pokemon_list = self._get_pokemon_list(1, 151)
            
            # 使用线程池并行获取Pokemon详情
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                
                for pokemon_basic in pokemon_list:
                    future = executor.submit(self._fetch_pokemon_details, pokemon_basic)
                    futures.append(future)
                
                # 收集结果
                for future in futures:
                    try:
                        pokemon_card = future.result(timeout=5)
                        if pokemon_card:
                            cards.append(pokemon_card)
                    except Exception as e:
                        print(f"⚠️ 获取Pokemon详情失败: {e}")
                        continue
        
        except Exception as e:
            print(f"❌ PokeAPI 批量获取失败: {e}")
        
        return cards
    
    def _get_pokemon_list(self, offset: int = 0, limit: int = 151) -> List[Dict]:
        """获取Pokemon列表"""
        try:
            response = requests.get(
                f"{self.pokeapi_base_url}/pokemon",
                params={'offset': offset, 'limit': limit},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            
        except requests.RequestException as e:
            print(f"❌ 获取Pokemon列表失败: {e}")
        
        return []
    
    def _fetch_pokemon_details(self, pokemon_basic: Dict) -> Optional[Dict]:
        """获取Pokemon详细信息"""
        try:
            pokemon_url = pokemon_basic.get('url', '')
            if not pokemon_url:
                return None
            
            response = requests.get(pokemon_url, timeout=5)
            if response.status_code != 200:
                return None
            
            pokemon_data = response.json()
            
            # 转换为卡片格式
            card = self._convert_pokemon_to_card(pokemon_data)
            return card
            
        except Exception as e:
            print(f"❌ 获取Pokemon详情失败 {pokemon_basic.get('name', '')}: {e}")
            return None
    
    def _convert_pokemon_to_card(self, pokemon_data: Dict) -> Dict:
        """将Pokemon数据转换为卡片格式"""
        pokemon_id = pokemon_data.get('id', 0)
        name = pokemon_data.get('name', '').title()
        
        # 获取Pokemon类型
        types = [t['type']['name'] for t in pokemon_data.get('types', [])]
        primary_type = types[0] if types else 'normal'
        
        # 获取属性值
        stats = {stat['stat']['name']: stat['base_stat'] 
                for stat in pokemon_data.get('stats', [])}
        
        # 计算HP（基于生命值属性）
        hp = stats.get('hp', 50)
        
        # 生成攻击技能
        attacks = self._generate_attacks_from_pokemon(pokemon_data, primary_type)
        
        # 确定稀有度（基于基础统计值总和）
        total_stats = sum(stats.values())
        rarity = self._determine_rarity_by_stats(total_stats)
        
        # 获取图片URL
        sprites = pokemon_data.get('sprites', {})
        image_url = (
            sprites.get('other', {}).get('official-artwork', {}).get('front_default') or
            sprites.get('front_default') or
            f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_id}.png"
        )
        
        return {
            'id': f"pokemon_{pokemon_id}",
            'name': name,
            'rarity': rarity,
            'type': 'pokemon',
            'pokemon_type': primary_type,
            'hp': hp,
            'image_url': image_url,
            'attacks': attacks,
            'weakness': self._get_type_weakness(primary_type),
            'resistance': self._get_type_resistance(primary_type),
            'retreat_cost': max(1, (stats.get('speed', 50) // 25)),
            'pokedex_number': pokemon_id,
            'source': 'pokeapi'
        }
    
    def _generate_attacks_from_pokemon(self, pokemon_data: Dict, primary_type: str) -> List[Dict]:
        """根据Pokemon数据生成攻击技能"""
        stats = {stat['stat']['name']: stat['base_stat'] 
                for stat in pokemon_data.get('stats', [])}
        
        attacks = []
        
        # 基础攻击
        basic_attack = {
            'name': f'{primary_type.title()} Attack',
            'cost': [primary_type],
            'damage': max(10, stats.get('attack', 50) // 3),
            'description': f'A basic {primary_type} type attack.'
        }
        attacks.append(basic_attack)
        
        # 强力攻击（如果攻击力足够高）
        if stats.get('attack', 0) > 80:
            power_attack = {
                'name': f'Powerful {primary_type.title()} Strike',
                'cost': [primary_type, primary_type],
                'damage': max(30, stats.get('attack', 80) // 2),
                'description': f'A powerful {primary_type} attack that deals heavy damage.'
            }
            attacks.append(power_attack)
        
        return attacks
    
    def _determine_rarity_by_stats(self, total_stats: int) -> str:
        """根据属性总值确定稀有度"""
        if total_stats >= 600:
            return 'legendary'
        elif total_stats >= 520:
            return 'epic'
        elif total_stats >= 450:
            return 'rare'
        elif total_stats >= 380:
            return 'uncommon'
        else:
            return 'common'
    
    def _get_type_weakness(self, pokemon_type: str) -> Dict:
        """获取属性弱点"""
        type_chart = {
            'fire': {'type': 'water', 'multiplier': 2},
            'water': {'type': 'electric', 'multiplier': 2},
            'grass': {'type': 'fire', 'multiplier': 2},
            'electric': {'type': 'ground', 'multiplier': 2},
            'normal': {'type': 'fighting', 'multiplier': 2},
            'fighting': {'type': 'psychic', 'multiplier': 2},
            'psychic': {'type': 'ghost', 'multiplier': 2},
        }
        return type_chart.get(pokemon_type, {})
    
    def _get_type_resistance(self, pokemon_type: str) -> Dict:
        """获取属性抗性"""
        resistance_chart = {
            'fire': {'type': 'grass', 'reduction': 20},
            'water': {'type': 'fire', 'reduction': 20},
            'grass': {'type': 'water', 'reduction': 20},
            'electric': {'type': 'flying', 'reduction': 20},
        }
        return resistance_chart.get(pokemon_type, {})
    
    def _map_rarity(self, original_rarity: str) -> str:
        """映射稀有度名称"""
        rarity_map = {
            'common': 'common',
            'uncommon': 'uncommon',
            'rare': 'rare',
            'ultra-rare': 'epic',
            'secret-rare': 'legendary',
            'promo': 'special'
        }
        return rarity_map.get(original_rarity.lower(), 'common')
    
    def _generate_default_cards(self) -> List[Dict]:
        """生成默认卡片数据（当网络获取失败时使用）"""
        print("🔧 生成默认卡片数据...")
        
        default_pokemon = [
            {'name': 'Pikachu', 'type': 'electric', 'hp': 60, 'rarity': 'uncommon'},
            {'name': 'Charizard', 'type': 'fire', 'hp': 150, 'rarity': 'rare'},
            {'name': 'Blastoise', 'type': 'water', 'hp': 140, 'rarity': 'rare'},
            {'name': 'Venusaur', 'type': 'grass', 'hp': 140, 'rarity': 'rare'},
            {'name': 'Mewtwo', 'type': 'psychic', 'hp': 120, 'rarity': 'legendary'},
            {'name': 'Mew', 'type': 'psychic', 'hp': 100, 'rarity': 'legendary'},
            {'name': 'Eevee', 'type': 'normal', 'hp': 50, 'rarity': 'common'},
            {'name': 'Snorlax', 'type': 'normal', 'hp': 180, 'rarity': 'epic'},
            {'name': 'Dragonite', 'type': 'dragon', 'hp': 160, 'rarity': 'epic'},
            {'name': 'Gyarados', 'type': 'water', 'hp': 130, 'rarity': 'rare'},
        ]
        
        cards = []
        for i, pokemon in enumerate(default_pokemon):
            # 为每个Pokemon生成多张不同的卡片变体
            for variant in range(3):
                card = {
                    'id': f"default_{i}_{variant}",
                    'name': pokemon['name'],
                    'rarity': pokemon['rarity'],
                    'type': 'pokemon',
                    'pokemon_type': pokemon['type'],
                    'hp': pokemon['hp'] + (variant * 10),
                    'image_url': f"assets/sprites/pokemon/{pokemon['name'].lower()}.png",
                    'attacks': self._generate_default_attacks(pokemon['type'], pokemon['hp']),
                    'weakness': self._get_type_weakness(pokemon['type']),
                    'resistance': self._get_type_resistance(pokemon['type']),
                    'retreat_cost': max(1, pokemon['hp'] // 50),
                    'source': 'default'
                }
                cards.append(card)
        
        # 添加一些常见卡片来填充数量
        common_names = [
            'Rattata', 'Pidgey', 'Weedle', 'Caterpie', 'Zubat',
            'Geodude', 'Magikarp', 'Psyduck', 'Slowpoke', 'Oddish'
        ]
        
        for i, name in enumerate(common_names):
            card = {
                'id': f"common_{i}",
                'name': name,
                'rarity': 'common',
                'type': 'pokemon',
                'pokemon_type': 'normal',
                'hp': 40 + (i % 3) * 10,
                'image_url': f"assets/sprites/pokemon/{name.lower()}.png",
                'attacks': self._generate_default_attacks('normal', 40),
                'weakness': {'type': 'fighting', 'multiplier': 2},
                'resistance': {},
                'retreat_cost': 1,
                'source': 'default'
            }
            cards.append(card)
        
        return cards
    
    def _generate_default_attacks(self, pokemon_type: str, hp: int) -> List[Dict]:
        """为默认Pokemon生成攻击技能"""
        attacks = []
        
        # 基础攻击
        basic_damage = max(10, hp // 4)
        attacks.append({
            'name': 'Quick Attack',
            'cost': [pokemon_type],
            'damage': basic_damage,
            'description': 'A quick strike.'
        })
        
        # 如果HP较高，添加强力攻击
        if hp > 80:
            power_damage = max(30, hp // 2)
            attacks.append({
                'name': f'{pokemon_type.title()} Blast',
                'cost': [pokemon_type, pokemon_type],
                'damage': power_damage,
                'description': f'A powerful {pokemon_type} attack.'
            })
        
        return attacks
    
    def get_card_by_id(self, card_id: str) -> Optional[Dict]:
        """根据ID获取卡片"""
        return self.card_cache.get(card_id)
    
    def search_cards(self, query: str, filters: Dict = None) -> List[Dict]:
        """搜索卡片"""
        results = []
        query = query.lower()
        
        for card in self.card_cache.values():
            # 名称匹配
            if query in card.get('name', '').lower():
                results.append(card)
                continue
            
            # 类型匹配
            if query in card.get('pokemon_type', '').lower():
                results.append(card)
                continue
        
        # 应用过滤器
        if filters:
            results = self._apply_filters(results, filters)
        
        return results
    
    def _apply_filters(self, cards: List[Dict], filters: Dict) -> List[Dict]:
        """应用搜索过滤器"""
        filtered = cards
        
        if 'rarity' in filters:
            filtered = [c for c in filtered if c.get('rarity') == filters['rarity']]
        
        if 'type' in filters:
            filtered = [c for c in filtered if c.get('pokemon_type') == filters['type']]
        
        if 'min_hp' in filters:
            filtered = [c for c in filtered if c.get('hp', 0) >= filters['min_hp']]
        
        if 'max_hp' in filters:
            filtered = [c for c in filtered if c.get('hp', 0) <= filters['max_hp']]
        
        return filtered
    
    def get_cards_by_rarity(self, rarity: str) -> List[Dict]:
        """获取指定稀有度的卡片"""
        return [card for card in self.card_cache.values() 
                if card.get('rarity') == rarity]
    
    def get_rarity_distribution(self) -> Dict[str, int]:
        """获取稀有度分布"""
        distribution = {}
        for card in self.card_cache.values():
            rarity = card.get('rarity', 'common')
            distribution[rarity] = distribution.get(rarity, 0) + 1
        return distribution
    
    def refresh_data(self):
        """刷新数据（强制重新获取）"""
        self.get_card_pool(force_refresh=True)
    
    def get_cache_info(self) -> Dict:
        """获取缓存信息"""
        return {
            'card_count': len(self.card_cache),
            'last_update': self.last_update,
            'cache_age_hours': (time.time() - self.last_update) / 3600,
            'is_valid': self._is_cache_valid()
        }