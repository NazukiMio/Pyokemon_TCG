import requests
from collections import Counter
import time

API_URL = "https://api.pokemontcg.io/v2/cards"
HEADERS = {}  # 如果你有 API KEY 可填入：{ "X-Api-Key": "your_key_here" }

MAX_CARDS = 3000
MIN_UNIQUE_RARITIES = 9
REQUIRED_RARITIES = {"Promo", "Ultra Rare"}
OUTPUT_PATH = "rarity_distribution_scan.txt"

def scan_rarity_distribution():
    page = 1
    page_size = 250
    total_scanned = 0
    rarity_counter = Counter()

    print("🔍 正在扫描卡牌稀有度字段...")

    while total_scanned < MAX_CARDS:
        params = {"page": page, "pageSize": page_size}
        response = requests.get(API_URL, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"[错误] API 请求失败: {response.status_code}")
            break

        cards = response.json().get("data", [])
        if not cards:
            print("❌ 没有更多卡牌数据可读。")
            break

        for card in cards:
            rarity = card.get("rarity", "Unknown")
            rarity_counter[rarity] += 1
            total_scanned += 1

        # 输出中间状态
        print(f"📄 已扫描卡牌总数: {total_scanned}，已发现稀有度种类: {len(rarity_counter)}")

        # 检查终止条件
        found_rarities = set(rarity_counter)
        if len(found_rarities) >= MIN_UNIQUE_RARITIES and REQUIRED_RARITIES.issubset(found_rarities):
            print("✅ 已满足条件，提前结束扫描。")
            break

        page += 1
        time.sleep(0.3)  # 避免请求过快被限流

    # 输出最终统计
    print("\n📊 扫描完成，稀有度分布如下：\n")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(f"共扫描卡牌数量: {total_scanned}\n")
        f.write(f"发现的稀有度种类数: {len(rarity_counter)}\n\n")
        for rarity, count in rarity_counter.most_common():
            line = f"{rarity:20} : {count}"
            print(line)
            f.write(line + "\n")

    print(f"\n📁 已将结果保存至 {OUTPUT_PATH}")

if __name__ == "__main__":
    scan_rarity_distribution()
