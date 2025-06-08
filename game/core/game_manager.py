"""
游戏核心管理器
整合数据库管理器和卡牌管理器，提供统一的游戏逻辑接口
"""

import random
import time
import datetime
import pygame
import pygame.image
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from game.core.database.database_manager import DatabaseManager
from game.core.cards.collection_manager import CardManager
from game.core.battle.battle_manager import BattleManager
from game.core.cards.card_data import Card

class GameManager:
    """
    游戏核心管理器
    负责处理用户数据、卡包开启、卡牌收集等核心游戏逻辑
    """
    
    def __init__(self):
        """初始化游戏管理器"""
        try:
            # 初始化数据库管理器
            self.db_manager = DatabaseManager()
            
            # 初始化卡牌管理器
            self.card_manager = CardManager(
                self.db_manager.connection,
                "card_assets/cards.json"  # 卡牌数据文件路径
            )
            print("✅ 游戏管理器初始化成功")
            # return True
        except Exception as e:
            print(f"❌ 游戏管理器初始化失败: {e}")
            return False
        
        # 🆕 添加game_manager引用，用于缓存系统
        self.card_manager.game_manager = self
        print(f"✅ CardManager已关联GameManager，缓存系统启用")
        
        # 🆕 验证设置是否成功
        print(f"🔍 GameManager中的CardManager有game_manager: {hasattr(self.card_manager, 'game_manager')}")
        print(f"🔍 GameManager中的CardManager.game_manager类型: {type(getattr(self.card_manager, 'game_manager', None))}")

        # 当前用户ID（可以通过登录设置）
        self.current_user_id = 1
        
        # 确保默认用户存在
        self._ensure_default_user()
        
        # 卡包配置
        self.pack_configs = {
            'pack_1': {
                'name': 'Festival Brillante',
                'display_name': 'Festival Brillante',
                'price_coins': 100,
                'price_gems': 0,
                'cards_per_pack': 5,
                'guaranteed_rarity': 'Uncommon',
                'pack_type': 'basic'
            },
            'pack_2': {
                'name': 'Guardianes Celestiales',
                'display_name': 'Guardianes Celestiales',
                'price_coins': 200,
                'price_gems': 0,
                'cards_per_pack': 5,
                'guaranteed_rarity': 'Rare',
                'pack_type': 'premium'
            },
            'pack_3': {
                'name': 'Ultra Premium',
                'display_name': 'Ultra Premium',
                'price_coins': 0,
                'price_gems': 50,
                'cards_per_pack': 3,
                'guaranteed_rarity': 'Ultra Rare',
                'pack_type': 'ultra'
            }
        }
        
        print("✅ GameManager 初始化完成")

        # # 添加缓存系统
        # self._card_cache = {
        #     'all_cards': None,
        #     'version': 0,
        #     'last_update': None
        # }
        # self._image_cache = {}  # 图片缓存
        # print(f"🔄 初始化卡牌缓存系统，版本: {self._card_cache['version']}")
        # print(f"图片缓存系统已初始化，当前缓存大小: {len(self._image_cache)}")

        # 添加缓存系统
        self._card_cache = {
            'all_cards': None,
            'version': 0,
            'last_update': None
        }
        self._image_cache = {}  # 图片缓存

        # 🆕 检查是否需要加载卡牌缓存
        self._check_and_load_card_cache()

        self.battle_manager = None
        print("✅ GameManager 战斗系统准备就绪")

        print(f"图片缓存系统已初始化，当前缓存大小: {len(self._image_cache)}")

    def _check_and_load_card_cache(self):
        """检查并加载卡牌缓存（带持久化版本检查）"""
        cache_info_file = "cache_info.txt"
        
        # 读取持久化的缓存信息
        try:
            with open(cache_info_file, 'r') as f:
                lines = f.read().strip().split('\n')
                last_cache_time = float(lines[0])
                last_cache_version = int(lines[1]) if len(lines) > 1 else 1
        except (OSError, ValueError, IndexError):
            last_cache_time = 0
            last_cache_version = 0
        
        # 获取cards.json的修改时间
        try:
            cards_mtime = os.path.getmtime("card_assets/cards.json")
        except OSError:
            cards_mtime = 0
        
        # 检查是否需要更新
        if cards_mtime > last_cache_time + 1:  # +1秒容错
            print(f"🔄 检测到卡牌库文件更新，需要重新加载缓存...")
            print(f"   📅 cards.json修改时间: {datetime.fromtimestamp(cards_mtime) if cards_mtime > 0 else '未知'}")
            print(f"   📅 上次缓存时间: {datetime.fromtimestamp(last_cache_time) if last_cache_time > 0 else '从未缓存'}")
            
            # 🆕 关键修改：只清空缓存数据，不重置版本号
            self._card_cache['all_cards'] = None
            self._card_cache['version'] = last_cache_version  # 保持版本号连续性
            self._card_cache['last_update'] = None
            self._pending_cache_time = cards_mtime
        else:
            print(f"✅ 卡牌库无变化，使用缓存版本 v{last_cache_version}")
            # 🆕 关键修改：恢复完整的缓存状态，包括缓存数据
            self._card_cache['version'] = last_cache_version
            self._card_cache['last_update'] = last_cache_time
            self._card_cache['all_cards'] = "CACHED"  # 🆕 标记为已缓存，避免重新加载
            self._pending_cache_time = None

    def get_cached_cards(self):
        """获取缓存的卡牌数据"""
        # 🆕 检查是否已经有有效缓存
        if self._card_cache['all_cards'] == "CACHED":
            # 从数据库重新加载（这比从cards.json加载快很多）
            print("📦 从数据库快速加载卡牌数据...")
            cards = self.card_manager.search_cards(limit=10000)
            self._card_cache['all_cards'] = cards
            print(f"✅ 快速加载完成: {len(cards)} 张卡牌")
            return cards
        elif self._card_cache['all_cards'] is None:
            # 需要完整加载
            self._load_cards_to_cache()
        
        return self._card_cache['all_cards']
    
    def _load_cards_to_cache(self):
        """加载卡牌到缓存"""
        print("🔄 正在加载卡牌到缓存...")
        cards = self.card_manager.search_cards(limit=10000)
        self._card_cache['all_cards'] = cards
        self._card_cache['version'] += 1  # 版本号递增
        self._card_cache['last_update'] = time.time()
        
        # 🆕 保存缓存信息到文件
        try:
            cache_info_file = "cache_info.txt"
            with open(cache_info_file, 'w') as f:
                # 使用实际的文件修改时间，而不是当前时间
                cache_time = getattr(self, '_pending_cache_time', None) or time.time()
                f.write(f"{cache_time}\n{self._card_cache['version']}")
            print(f"💾 缓存信息已保存 (版本: v{self._card_cache['version']})")
        except OSError as e:
            print(f"⚠️ 无法保存缓存信息: {e}")
        
        print(f"✅ 卡牌缓存完成: {len(cards)} 张卡牌")
    
    def get_card_cache_version(self):
        """获取缓存版本号"""
        return self._card_cache['version']
    
    def invalidate_card_cache(self):
        """清理卡牌缓存（卡牌库更新时调用）"""
        print("🗑️ 清理卡牌缓存...")
        self._card_cache['all_cards'] = None
        self._image_cache.clear()
        
    def get_cached_image(self, image_path):
        """获取缓存的图片"""
        # print(f"📸 get_cached_image被调用: {image_path}")
        
        # 确保pygame已初始化
        if not pygame.get_init():
            print("⚠️ pygame未初始化，跳过图片缓存")
            return None
            
        if image_path not in self._image_cache:
            # print(f"🔄 首次加载图片到缓存: {image_path}")
            if os.path.exists(image_path):
                try:
                    self._image_cache[image_path] = pygame.image.load(image_path)
                    # print(f"✅ 图片缓存成功: {image_path}")
                except Exception as e:
                    print(f"❌ 加载图片失败 {image_path}: {e}")
                    return None
            else:
                print(f"❌ 图片文件不存在: {image_path}")
                return None
        else:
            print(f"📦 从缓存获取图片: {image_path}")
        
        return self._image_cache[image_path]

    def _ensure_default_user(self):
        """确保默认用户存在"""
        user = self.db_manager.get_user_info(self.current_user_id)
        if not user:
            # 创建默认用户
            success, result = self.db_manager.register_user(
                username="player1",
                password="default",
                email="player1@game.com"
            )
            if success:
                self.current_user_id = result
                print(f"✅ 创建默认用户，ID: {self.current_user_id}")
            else:
                print(f"❌ 创建默认用户失败: {result}")
    
    # ==================== 用户管理 ====================
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        return self.db_manager.get_user_info(self.current_user_id)
    
    def get_user_economy(self) -> Dict[str, Any]:
        """获取用户经济数据"""
        economy = self.db_manager.get_user_economy(self.current_user_id)
        if not economy:
            # 如果没有经济数据，创建默认的
            self.db_manager._create_user_economy(self.current_user_id)
            economy = self.db_manager.get_user_economy(self.current_user_id)
        
        return economy or {
            'user_id': self.current_user_id,
            'coins': 500,
            'gems': 10,
            'pack_points': 0,
            'dust': 0
        }
    
    def get_user_stats(self) -> Dict[str, Any]:
        """获取用户统计数据"""
        stats = self.db_manager.get_user_stats(self.current_user_id)
        if not stats:
            # 如果没有统计数据，创建默认的
            self.db_manager._create_user_stats(self.current_user_id)
            stats = self.db_manager.get_user_stats(self.current_user_id)
        
        return stats or {
            'user_id': self.current_user_id,
            'games_played': 0,
            'games_won': 0,
            'games_lost': 0,
            'cards_collected': 0,
            'packs_opened': 0,
            'dust_earned': 0
        }
    
    def add_currency(self, currency_type: str, amount: int) -> bool:
        """添加货币"""
        return self.db_manager.add_currency(self.current_user_id, currency_type, amount)
    
    def spend_currency(self, currency_type: str, amount: int) -> bool:
        """花费货币"""
        return self.db_manager.spend_currency(self.current_user_id, currency_type, amount)
    
    def can_afford(self, currency_type: str, amount: int) -> bool:
        """检查是否能够支付"""
        economy = self.get_user_economy()
        return economy.get(currency_type, 0) >= amount
    
    # ==================== 卡包管理 ====================
    def get_available_packs(self) -> List[Dict[str, Any]]:
        """获取可用的卡包列表"""
        packs = []
        for pack_id, config in self.pack_configs.items():
            packs.append({
                'id': pack_id,
                'name': config['display_name'],
                'description': f"包含 {config['cards_per_pack']} 张卡牌，保底 {config['guaranteed_rarity']}",
                'price_coins': config['price_coins'],
                'price_gems': config['price_gems'],
                'cards_per_pack': config['cards_per_pack'],
                'guaranteed_rarity': config['guaranteed_rarity']
            })
        return packs
    
    def can_open_pack(self, pack_id: str) -> Tuple[bool, str]:
        """检查是否能开启卡包"""
        if pack_id not in self.pack_configs:
            return False, "未知的卡包类型"
        
        config = self.pack_configs[pack_id]
        economy = self.get_user_economy()
        
        # 检查金币
        if config['price_coins'] > 0:
            if economy.get('coins', 0) < config['price_coins']:
                return False, f"金币不足，需要 {config['price_coins']} 金币"
        
        # 检查宝石
        if config['price_gems'] > 0:
            if economy.get('gems', 0) < config['price_gems']:
                return False, f"宝石不足，需要 {config['price_gems']} 宝石"
        
        return True, "可以开启"
    
    def open_pack_complete_flow(self, pack_quality: str) -> Dict[str, Any]:
        """完整的开包流程（适配PackOpeningWindow）"""
        
        # 映射pack_quality到pack_id
        quality_to_pack_id = {
            "basic": "pack_1",
            "premium": "pack_2", 
            "legendary": "pack_3"
        }
        
        pack_id = quality_to_pack_id.get(pack_quality)
        if not pack_id:
            return {
                "success": False,
                "error": "unknown_pack_type",
                "cards": []
            }
        
        # 调用现有的open_pack方法
        success, cards, message = self.open_pack(pack_id)
        
        if success:
            cards_data = []
            print(f"🖼️ 检查卡牌图片路径:")
            
            for i, card in enumerate(cards):
                # 🔑 使用CardManager的get_card_image_path方法（与图鉴页面一致）
                print(f"  卡牌{i+1}: {card.name}")
                print(f"    ID: '{card.id}'")
                print(f"    数据库原始image_path: '{getattr(card, 'image_path', 'None')}'")
                
                # 🔑 使用CardManager的get_card_image_path方法处理路径
                processed_image_path = self.card_manager.get_card_image_path(card.id)
                print(f"    CardManager处理后路径: '{processed_image_path}'")
                
                # ✅ 手动验证和修正路径（双重保险）
                final_image_path = processed_image_path
                if processed_image_path:
                    import os
                    if os.path.exists(processed_image_path):
                        print(f"    ✅ 图片文件存在: {processed_image_path}")
                        final_image_path = processed_image_path
                    else:
                        print(f"    ❌ 处理后的路径不存在，尝试手动修正...")
                        # 手动修正路径
                        raw_path = getattr(card, 'image_path', '')
                        if raw_path:
                            # ✅ 保持Windows路径格式，只添加card_assets前缀
                            corrected_path = raw_path
                            # 添加card_assets前缀（使用os.path.join确保路径正确）
                            if not (corrected_path.startswith('card_assets') or corrected_path.startswith('card_assets\\')):
                                corrected_path = os.path.join('card_assets', corrected_path)
                            
                            print(f"    手动修正路径: '{corrected_path}'")
                            if os.path.exists(corrected_path):
                                print(f"    ✅ 手动修正成功: {corrected_path}")
                                final_image_path = corrected_path
                            else:
                                print(f"    ❌ 手动修正也失败: {corrected_path}")
                                final_image_path = None
                else:
                    print(f"    ❌ CardManager返回空路径")
                    final_image_path = None

                card_data = {
                    "id": card.id,
                    "name": card.name,
                    "rarity": card.rarity,
                    "image": final_image_path,  # ✅ 使用CardManager处理后的路径
                    "hp": getattr(card, 'hp', None),
                    "types": card.types if hasattr(card, 'types') else []
                }

                print(f"    最终传递给界面的image: '{card_data['image']}'")
                cards_data.append(card_data)

            print(f"🎮 传给PackOpeningWindow的数据:")
            print(f"  success: {True}")
            print(f"  cards数量: {len(cards_data)}")
            
            return {
                "success": True,
                "cards": cards_data,
                "message": message
            }
        else:
            # 映射错误消息到PackOpeningWindow期望的错误类型
            error_type = "unknown_error"
            if "金币不足" in message or "宝石不足" in message:
                error_type = "insufficient_packs"
            elif "扣除" in message:
                error_type = "deduct_pack_failed"
            elif "失败" in message:
                error_type = "transaction_failed"
            
            return {
                "success": False,
                "error": error_type,
                "cards": [],
                "message": message
            }

    def open_pack(self, pack_id: str) -> Tuple[bool, List[Card], str]:
        """
        开启卡包
        
        Returns:
            (成功标志, 获得的卡牌列表, 消息)
        """
        # 检查是否能开启
        can_open, message = self.can_open_pack(pack_id)
        if not can_open:
            return False, [], message
        
        config = self.pack_configs[pack_id]
        
        try:
            # ✅ 添加调试：检查CardManager是否有数据
            print(f"🔍 调试信息：")
            print(f"  CardManager对象: {self.card_manager}")

            # # 检查CardManager是否加载了卡片数据
            # if hasattr(self.card_manager, 'cards') and self.card_manager.cards:
            #     print(f"  已加载卡片数量: {len(self.card_manager.cards)}")
            #     print(f"  前5张卡片ID: {list(self.card_manager.cards.keys())[:5]}")
            # else:
            #     print("  ❌ CardManager没有加载任何卡片数据！")
            #     return False, [], "卡片数据未加载"

            # ✅ 使用CardDAO检查数据库中的卡片数量
            try:
                total_cards = self.card_manager.card_dao.get_card_count()
                print(f"  数据库中卡片数量: {total_cards}")
                
                if total_cards == 0:
                    print("  ❌ 数据库中没有卡片数据！")
                    return False, [], "数据库中无卡片数据"
                
                # ✅ 测试能否获取随机卡片
                test_card = self.card_manager.get_random_card_by_rarity('Common')
                if test_card:
                    print(f"  ✅ 测试获取随机卡片成功: {test_card.name}")
                else:
                    print("  ❌ 无法获取随机卡片")

            except Exception as e:
                print(f"  ❌ 检查CardManager数据时出错: {e}")
                return False, [], f"CardManager数据检查失败: {str(e)}"

            # 扣除费用
            if config['price_coins'] > 0:
                if not self.spend_currency('coins', config['price_coins']):
                    return False, [], "扣除金币失败"
            
            if config['price_gems'] > 0:
                if not self.spend_currency('gems', config['price_gems']):
                    return False, [], "扣除宝石失败"
            
            # 开启卡包获得卡牌
            print(f"  准备开包: pack_type={config['pack_type']}, guaranteed_rarity={config['guaranteed_rarity']}")

            obtained_cards = self.card_manager.open_pack(
                pack_type=config['pack_type'],
                guaranteed_rarity=config['guaranteed_rarity']
            )
            
            # # 检查CardManager是否加载了卡片数据
            # if hasattr(self.card_manager, 'cards') and self.card_manager.cards:
            #     print(f"  已加载卡片数量: {len(self.card_manager.cards)}")
            #     print(f"  前5张卡片ID: {list(self.card_manager.cards.keys())[:5]}")
            # else:
            #     print("  ❌ CardManager没有加载任何卡片数据！")
            #     return False, [], "卡片数据未加载"

            # ✅ 详细检查开包结果
            print(f"  开包结果:")
            print(f"    返回类型: {type(obtained_cards)}")
            print(f"    是否为None: {obtained_cards is None}")
            print(f"    获得卡牌数量: {len(obtained_cards) if obtained_cards else 0}")
            
            if obtained_cards:
                for i, card in enumerate(obtained_cards):
                    print(f"    卡牌{i+1}: ID='{card.id}', 名称='{card.name}', 稀有度='{card.rarity}'")
            else:
                print("    ❌ 没有获得任何卡牌")
                return False, [], "开包未获得卡牌"

            # 将卡牌添加到用户收藏
            for card in obtained_cards:
                success = self.db_manager.add_card_to_user(self.current_user_id, card.id, 1)
                print(f"    添加卡牌 {card.id} 到用户收藏: {'成功' if success else '失败'}")
            
            # 记录开包历史
            pack_type_id = list(self.pack_configs.keys()).index(pack_id) + 1
            cost_type = 'coins' if config['price_coins'] > 0 else 'gems'
            cost_amount = config['price_coins'] if config['price_coins'] > 0 else config['price_gems']
            
            card_ids = [card.id for card in obtained_cards]
            record_success = self.db_manager.record_pack_opening(
                self.current_user_id,
                pack_type_id,
                card_ids,
                cost_type,
                cost_amount
            )
            print(f"    记录开包历史: {'成功' if record_success else '失败'}")
            
            # 更新统计
            current_stats = self.get_user_stats()
            new_packs_opened = current_stats['packs_opened'] + 1
            new_cards_collected = current_stats['cards_collected'] + len(obtained_cards)
            
            stats_success = self.db_manager.update_user_stats(
                self.current_user_id,
                packs_opened=new_packs_opened,
                cards_collected=new_cards_collected
            )
            print(f"    更新统计: {'成功' if stats_success else '失败'}")
            
            return True, obtained_cards, f"成功开启 {config['display_name']}！"
            
        except Exception as e:
            print(f"❌ 开包失败: {e}")
            import traceback
            traceback.print_exc()
            return False, [], f"开包失败: {str(e)}"
    
    # ==================== 卡牌管理 ====================
    def get_user_cards(self) -> List[Dict[str, Any]]:
        """获取用户的所有卡牌"""
        user_cards_data = self.db_manager.get_user_cards(self.current_user_id)
        result = []
        
        for card_data in user_cards_data:
            card = self.card_manager.get_card_by_id(card_data['card_id'])
            if card:
                result.append({
                    'card': card,
                    'quantity': card_data['quantity'],
                    'obtained_at': card_data['obtained_at']
                })
        
        return result
    
    def get_user_collection_stats(self) -> Dict[str, Any]:
        """获取用户收藏统计"""
        user_cards = self.get_user_cards()
        user_card_ids = [card_info['card'].id for card_info in user_cards]
        
        # 使用卡牌管理器获取收藏进度
        collection_progress = self.card_manager.get_collection_progress(user_card_ids)
        
        # 添加一些额外的统计
        total_owned = sum(card_info['quantity'] for card_info in user_cards)
        unique_owned = len(user_cards)
        
        collection_progress['owned_stats'] = {
            'total_cards_owned': total_owned,
            'unique_cards_owned': unique_owned,
            'average_copies': round(total_owned / unique_owned, 2) if unique_owned > 0 else 0
        }
        
        return collection_progress
    
    def search_cards(self, **kwargs) -> List[Card]:
        """搜索卡牌"""
        return self.card_manager.search_cards(**kwargs)
    
    def get_card_by_id(self, card_id: str) -> Optional[Card]:
        """根据ID获取卡牌"""
        return self.card_manager.get_card_by_id(card_id)
    
    def get_featured_cards(self, count: int = 10) -> List[Card]:
        """获取精选卡牌"""
        return self.card_manager.get_featured_cards(count)
    
    def get_daily_featured_card(self) -> Optional[Card]:
        """获取每日精选卡牌"""
        return self.card_manager.get_daily_featured_card()
    
    # ==================== 卡组管理 ====================
    def get_user_decks(self) -> List[Dict[str, Any]]:
        """获取用户卡组"""
        return self.db_manager.get_user_decks(self.current_user_id)
    
    def create_deck(self, name: str, description: str = "") -> Tuple[bool, Any]:
        """创建新卡组"""
        return self.db_manager.create_new_deck(self.current_user_id, name, description)
    
    def add_card_to_deck(self, deck_id: int, card_id: str, quantity: int = 1) -> bool:
        """向卡组添加卡牌"""
        return self.db_manager.add_card_to_deck(deck_id, card_id, quantity)
    
    def get_deck_cards(self, deck_id: int) -> List[Dict[str, Any]]:
        """获取卡组中的卡牌"""
        return self.db_manager.get_deck_cards(deck_id)
    
    # ==================== 成就和任务 ====================
    def get_user_achievements(self) -> List[Dict[str, Any]]:
        """获取用户成就"""
        return self.db_manager.get_user_achievements(self.current_user_id)
    
    def update_achievement_progress(self, achievement_name: str, progress: int) -> Tuple[bool, str]:
        """更新成就进度"""
        return self.db_manager.update_achievement_progress(self.current_user_id, achievement_name, progress)
    
    def get_daily_quests(self) -> List[Dict[str, Any]]:
        """获取每日任务"""
        today = datetime.date.today().isoformat()
        return self.db_manager.get_daily_quests(self.current_user_id, today)
    
    def update_quest_progress(self, quest_type: str, progress: int) -> Tuple[bool, str]:
        """更新任务进度"""
        today = datetime.date.today().isoformat()
        return self.db_manager.update_quest_progress(self.current_user_id, quest_type, today, progress)
    
    # ==================== 游戏统计 ====================
    def get_pack_opening_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取开包历史"""
        return self.db_manager.get_pack_opening_history(self.current_user_id, limit)
    
    def get_card_statistics(self) -> Dict[str, Any]:
        """获取卡牌统计信息"""
        return self.card_manager.get_card_statistics()
    
    def get_game_overview(self) -> Dict[str, Any]:
        """获取游戏概览信息"""
        user = self.get_current_user()
        economy = self.get_user_economy()
        stats = self.get_user_stats()
        collection_stats = self.get_user_collection_stats()
        
        return {
            'user': user,
            'economy': economy,
            'stats': stats,
            'collection': collection_stats,
            'available_packs': self.get_available_packs(),
            'recent_pack_openings': self.get_pack_opening_history(5)
        }
    
    # ==================== 每日奖励 ====================
    def claim_daily_bonus(self) -> Tuple[bool, str, Dict[str, int]]:
        """领取每日奖励"""
        economy = self.get_user_economy()
        last_bonus = economy.get('last_daily_bonus')
        today = datetime.date.today().isoformat()
        
        if last_bonus == today:
            return False, "今日已领取每日奖励", {}
        
        # 每日奖励配置
        daily_rewards = {
            'coins': 50,
            'gems': 1
        }
        
        # 发放奖励
        success = True
        for currency, amount in daily_rewards.items():
            if not self.add_currency(currency, amount):
                success = False
                break
        
        if success:
            # 更新最后领取时间
            self.db_manager.update_user_economy(
                self.current_user_id,
                last_daily_bonus=today
            )
            return True, "每日奖励领取成功！", daily_rewards
        else:
            return False, "领取每日奖励失败", {}
    
    def can_claim_daily_bonus(self) -> bool:
        """检查是否可以领取每日奖励"""
        economy = self.get_user_economy()
        last_bonus = economy.get('last_daily_bonus')
        today = datetime.date.today().isoformat()
        return last_bonus != today
    
    # ==================== 辅助方法 ====================
    def generate_test_data(self):
        """生成测试数据（开发用）"""
        print("🔧 生成测试数据...")
        
        # 给用户一些初始货币
        self.add_currency('coins', 1000)
        self.add_currency('gems', 50)
        
        # 创建一些成就
        achievements = [
            ("collector", "收藏家", "收集100张不同的卡牌", 100, 100, 5),
            ("pack_opener", "开包达人", "开启50个卡包", 50, 50, 3),
            ("rare_hunter", "稀有猎人", "获得10张Ultra Rare卡牌", 10, 200, 10)
        ]
        
        for ach_type, ach_name, desc, target, reward_coins, reward_gems in achievements:
            self.db_manager.create_achievement(
                self.current_user_id, ach_type, ach_name, desc, target, reward_coins, reward_gems
            )
        
        # 创建一些每日任务
        today = datetime.date.today().isoformat()
        quests = [
            ("open_pack", "开启一个卡包", 1, 25, 0),
            ("collect_cards", "收集5张新卡牌", 5, 50, 1),
            ("login", "登录游戏", 1, 10, 0)
        ]
        
        for quest_type, desc, target, reward_coins, reward_gems in quests:
            self.db_manager.create_daily_quest(
                self.current_user_id, quest_type, desc, target, today, reward_coins, reward_gems
            )
        
        print("✅ 测试数据生成完成")
    
    # ==================== 战斗系统 ====================
    def create_battle_manager(self, player_deck_id, opponent_type="AI", opponent_id=None):
        """创建战斗管理器"""
        try:
            self.battle_manager = BattleManager(
                game_manager=self,
                player_id=self.current_user_id,
                player_deck_id=player_deck_id,
                opponent_type=opponent_type,
                opponent_id=opponent_id
            )
            return True, "战斗管理器创建成功"
        except Exception as e:
            print(f"创建战斗管理器失败: {e}")
            return False, str(e)

    def get_battle_manager(self):
        """获取当前战斗管理器"""
        return self.battle_manager

    def end_current_battle(self):
        """结束当前战斗"""
        if self.battle_manager:
            self.battle_manager.cleanup()
            self.battle_manager = None

    def get_user_battle_stats(self):
        """获取用户战斗统计"""
        try:
            battles = self.db_manager.get_user_battles(self.current_user_id, limit=1000)
            
            total_battles = len(battles)
            pve_wins = sum(1 for b in battles if b['battle_type'] == 'PVE' and b['winner_id'] == self.current_user_id)
            pvp_wins = sum(1 for b in battles if b['battle_type'] == 'PVP' and b['winner_id'] == self.current_user_id)
            
            return {
                'total_battles': total_battles,
                'pve_battles': len([b for b in battles if b['battle_type'] == 'PVE']),
                'pvp_battles': len([b for b in battles if b['battle_type'] == 'PVP']),
                'pve_wins': pve_wins,
                'pvp_wins': pvp_wins,
                'total_wins': pve_wins + pvp_wins,
                'win_rate': round((pve_wins + pvp_wins) / total_battles * 100, 2) if total_battles > 0 else 0
            }
        except Exception as e:
            print(f"获取战斗统计失败: {e}")
            return {}

    def validate_deck_for_battle(self, deck_id):
        """验证卡组是否适合战斗"""
        try:
            deck_cards = self.get_deck_cards(deck_id)
            if not deck_cards:
                return False, "卡组为空"
            
            if len(deck_cards) < 20:
                return False, f"卡组至少需要20张卡牌，当前只有{len(deck_cards)}张"
            
            # 检查是否有Pokemon
            pokemon_count = 0
            for card_data in deck_cards:
                card = self.get_card_by_id(card_data['card_id'])
                if card and card.hp:  # 有HP的卡牌是Pokemon
                    pokemon_count += card_data['quantity']
            
            if pokemon_count < 5:
                return False, "卡组至少需要5只Pokemon"
            
            return True, "卡组验证通过"
        except Exception as e:
            return False, f"卡组验证失败: {str(e)}"

    def reset_user_data(self):
        """重置用户数据（开发用）"""
        print("🔄 重置用户数据...")
        
        # 重置经济数据
        self.db_manager.update_user_economy(
            self.current_user_id,
            coins=500,
            gems=10,
            pack_points=0,
            dust=0
        )
        
        # 重置统计数据
        self.db_manager.update_user_stats(
            self.current_user_id,
            games_played=0,
            games_won=0,
            games_lost=0,
            cards_collected=0,
            packs_opened=0,
            dust_earned=0
        )
        
        print("✅ 用户数据重置完成")
    
    def cleanup(self):
        """清理资源"""
        # 清理战斗管理器
        if self.battle_manager:
            self.battle_manager.cleanup()
            self.battle_manager = None

        if self.db_manager:
            self.db_manager.close()
        print("🧹 GameManager 资源清理完成")
    
    def __del__(self):
        """析构函数"""
        self.cleanup()