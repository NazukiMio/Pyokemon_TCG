#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全机制测试脚本
测试新的token认证系统和collection_manager集成
"""

import sys
import os
import getpass

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.core.auth.auth_manager import get_auth_manager
from game.core.database.database_manager import DatabaseManager
from game.core.cards.collection_manager import CardManager

class AuthTestApp:
    def __init__(self):
        self.auth = get_auth_manager()
        self.db = DatabaseManager()
        self.card_manager = CardManager(self.db.connection)
        self.running = True
        
    def print_header(self):
        """打印程序头部"""
        print("=" * 60)
        print("🔐 安全认证系统测试程序")
        print("=" * 60)
        print()
    
    def print_menu(self):
        """打印菜单"""
        if self.auth.is_logged_in():
            user_info = self.auth.get_user_info()
            username = user_info.get('username', 'Unknown') if user_info else 'Unknown'
            print(f"当前用户: {username} (已登录)")
            print("\n可用指令:")
            print("  stats     - 查看卡牌统计信息")
            print("  featured  - 查看精选卡牌")
            print("  daily     - 查看每日精选卡牌")
            print("  search    - 搜索卡牌")
            print("  pack      - 开启卡包")
            print("  whoami    - 查看当前用户信息")
            print("  logout    - 退出登录")
            print("  quit      - 退出程序")
        else:
            print("当前状态: 未登录")
            print("\n可用指令:")
            print("  login     - 登录")
            print("  register  - 注册新用户")
            print("  quit      - 退出程序")
        print("-" * 40)
    
    def handle_login(self):
        """处理登录"""
        print("\n📝 用户登录")
        username = input("用户名: ").strip()
        if not username:
            print("❌ 用户名不能为空")
            return
        
        password = getpass.getpass("密码: ")
        if not password:
            print("❌ 密码不能为空")
            return
        
        print("正在验证...")
        success, message = self.auth.login(username, password)
        
        if success:
            print(f"✅ {message}")
            user_id = self.auth.get_current_user_id()
            print(f"🆔 用户ID: {user_id}")
        else:
            print(f"❌ {message}")
    
    def handle_register(self):
        """处理注册"""
        print("\n📝 用户注册")
        username = input("用户名: ").strip()
        if not username:
            print("❌ 用户名不能为空")
            return
        
        password = getpass.getpass("密码: ")
        if not password:
            print("❌ 密码不能为空")
            return
        
        confirm_password = getpass.getpass("确认密码: ")
        if password != confirm_password:
            print("❌ 两次输入的密码不一致")
            return
        
        print("正在注册...")
        success, message = self.auth.register(username, password)
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    def handle_stats(self):
        """查看卡牌统计"""
        print("\n📊 卡牌统计信息")
        try:
            stats = self.card_manager.get_card_statistics()
            print(f"总卡牌数: {stats['total_cards']}")
            print(f"总系列数: {stats['total_sets']}")
            print(f"可用稀有度: {len(stats['available_rarities'])}")
            print(f"可用类型: {len(stats['available_types'])}")
            
            print("\n稀有度分布:")
            for rarity, count in list(stats['rarity_distribution'].items())[:5]:
                print(f"  {rarity}: {count}")
            
            print("\n类型分布:")
            for card_type, count in list(stats['type_distribution'].items())[:5]:
                print(f"  {card_type}: {count}")
                
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
    
    def handle_featured(self):
        """查看精选卡牌"""
        print("\n⭐ 精选卡牌")
        try:
            featured_cards = self.card_manager.get_featured_cards(5)
            
            if featured_cards:
                for i, card in enumerate(featured_cards, 1):
                    print(f"{i}. {card.name} ({card.rarity})")
                    if card.types:
                        print(f"   类型: {', '.join(card.types)}")
                    if card.hp:
                        print(f"   HP: {card.hp}")
                    print()
            else:
                print("没有找到精选卡牌")
                
        except Exception as e:
            print(f"❌ 获取精选卡牌失败: {e}")
    
    def handle_daily(self):
        """查看每日精选卡牌"""
        print("\n🌟 每日精选卡牌")
        try:
            daily_card = self.card_manager.get_daily_featured_card()
            
            if daily_card:
                print(f"今日精选: {daily_card.name}")
                print(f"稀有度: {daily_card.rarity}")
                if daily_card.types:
                    print(f"类型: {', '.join(daily_card.types)}")
                if daily_card.hp:
                    print(f"HP: {daily_card.hp}")
                if daily_card.set_name:
                    print(f"系列: {daily_card.set_name}")
            else:
                print("今日暂无精选卡牌")
                
        except Exception as e:
            print(f"❌ 获取每日精选失败: {e}")
    
    def handle_search(self):
        """搜索卡牌"""
        print("\n🔍 卡牌搜索")
        keyword = input("输入卡牌名称关键词 (直接回车搜索所有): ").strip()
        
        try:
            if keyword:
                cards = self.card_manager.search_cards(name=keyword, limit=10)
            else:
                cards = self.card_manager.search_cards(limit=10)
            
            if cards:
                print(f"\n找到 {len(cards)} 张卡牌:")
                for i, card in enumerate(cards, 1):
                    print(f"{i}. {card.name} ({card.rarity})")
                    if card.types:
                        print(f"   类型: {', '.join(card.types)}")
            else:
                print("没有找到匹配的卡牌")
                
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
    
    def handle_pack(self):
        """开启卡包"""
        print("\n🎁 开启卡包")
        print("可选卡包类型:")
        print("  1. basic   - 基础包 (5张卡，保底 Uncommon)")
        print("  2. premium - 高级包 (5张卡，保底 Rare)")
        print("  3. ultra   - 究极包 (3张卡，保底 Ultra Rare)")
        
        choice = input("选择卡包类型 (1-3): ").strip()
        pack_types = {"1": "basic", "2": "premium", "3": "ultra"}
        
        pack_type = pack_types.get(choice, "basic")
        
        try:
            print(f"正在开启 {pack_type} 卡包...")
            cards = self.card_manager.open_pack(pack_type)
            
            if cards:
                print(f"\n🎉 获得 {len(cards)} 张卡牌:")
                for i, card in enumerate(cards, 1):
                    print(f"{i}. {card.name} ({card.rarity})")
                    if card.types:
                        print(f"   类型: {', '.join(card.types)}")
            else:
                print("卡包开启失败")
                
        except Exception as e:
            print(f"❌ 开启卡包失败: {e}")
    
    def handle_whoami(self):
        """查看当前用户信息"""
        print("\n👤 当前用户信息")
        try:
            user_id = self.auth.get_current_user_id()
            user_info = self.auth.get_user_info()
            
            if user_info:
                print(f"用户ID: {user_id}")
                print(f"用户名: {user_info.get('username', 'Unknown')}")
                print(f"注册时间: {user_info.get('created_at', 'Unknown')}")
                
                # 显示当前token (前20个字符)
                if hasattr(self.auth, 'current_token') and self.auth.current_token:
                    token_preview = self.auth.current_token[:20] + "..."
                    print(f"当前Token: {token_preview}")
                    print(f"Token长度: {len(self.auth.current_token)} 字符")
            else:
                print("无法获取用户信息")
                
        except Exception as e:
            print(f"❌ 获取用户信息失败: {e}")
    
    def handle_logout(self):
        """处理登出"""
        print("\n👋 退出登录")
        if self.auth.logout():
            print("✅ 已成功退出登录")
        else:
            print("❌ 退出登录失败")
    
    def handle_command(self, command):
        """处理用户命令"""
        command = command.lower().strip()
        
        # 通用命令
        if command == "quit":
            print("\n👋 再见!")
            self.running = False
            return
        
        # 未登录状态的命令
        if not self.auth.is_logged_in():
            if command == "login":
                self.handle_login()
            elif command == "register":
                self.handle_register()
            else:
                print("❌ 请先登录或注册")
            return
        
        # 已登录状态的命令
        if command == "stats":
            self.handle_stats()
        elif command == "featured":
            self.handle_featured()
        elif command == "daily":
            self.handle_daily()
        elif command == "search":
            self.handle_search()
        elif command == "pack":
            self.handle_pack()
        elif command == "whoami":
            self.handle_whoami()
        elif command == "logout":
            self.handle_logout()
        else:
            print(f"❌ 未知命令: {command}")
    
    def run(self):
        """运行测试程序"""
        self.print_header()
        
        while self.running:
            try:
                print()
                self.print_menu()
                command = input("\n请输入命令: ").strip()
                
                if not command:
                    continue
                
                self.handle_command(command)
                
            except KeyboardInterrupt:
                print("\n\n👋 程序被中断，再见!")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                print("请重试或输入 'quit' 退出")
        
        # 清理资源
        if hasattr(self, 'db'):
            self.db.close()


def main():
    """主函数"""
    try:
        app = AuthTestApp()
        app.run()
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        print("请确保数据库和相关模块正常工作")


if __name__ == "__main__":
    main()