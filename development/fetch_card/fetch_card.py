import os
import json
import shutil
import requests
from tqdm import tqdm

# 你的实际比例分布（包含全部稀有度，示例可改）
RARITY_DISTRIBUTION = {
    "Common": 0.35,
    "Uncommon": 0.25,
    "Rare": 0.15,
    "Rare Holo": 0.1,
    "Promo": 0.05,
    "Rare Holo EX": 0.03,
    "Ultra Rare": 0.025,
    "Rare Secret": 0.02,
    "Rare Holo GX": 0.015,
    "Rare Shiny": 0.01,
    "Rare Holo V": 0.005,
    "Rare BREAK": 0.005,
    "Rare Ultra": 0.005,
    "Rare Prism Star": 0.005,
    "Amazing Rare": 0.005,
    "Rare Shining": 0.005
}

API_URL = "https://api.pokemontcg.io/v2/cards"
HEADERS = {}

OUTPUT_DIR = "card_assets"
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")
CARDS_JSON = os.path.join(OUTPUT_DIR, "cards.json")

# 清理旧图片内容
def check_and_clean_images():
    if os.path.exists(IMAGE_DIR) and os.listdir(IMAGE_DIR):
        print(f"⚠️ 发现已有图片资源在 {IMAGE_DIR}")
        choice = input("是否清空所有旧图片并重新下载？(y/n): ").strip().lower()
        if choice == 'y':
            shutil.rmtree(IMAGE_DIR)
            os.makedirs(IMAGE_DIR, exist_ok=True)
            print("✅ 图片目录已清空")
        else:
            print("❌ 保留旧图片，可能会导致 JSON 与图像不一致")
    else:
        os.makedirs(IMAGE_DIR, exist_ok=True)

# 获取卡牌数据
def fetch_cards_by_rarity(total_cards):
    final_cards = []
    for rarity, ratio in RARITY_DISTRIBUTION.items():
        count = max(1, int(round(total_cards * ratio)))
        print(f"📦 获取 {rarity} 稀有度的卡牌：目标 {count} 张")
        cards = []
        page = 1
        while len(cards) < count:
            params = {
                "q": f"rarity:\"{rarity}\"",
                "page": page,
                "pageSize": 250
            }
            r = requests.get(API_URL, headers=HEADERS, params=params)
            if r.status_code != 200:
                print(f"[错误] 请求失败: {r.status_code}")
                break
            data = r.json().get("data", [])
            if not data:
                break
            for card in data:
                if len(cards) >= count:
                    break
                if "images" not in card or "small" not in card["images"]:
                    continue
                cards.append(card)
            page += 1
        print(f"✅ 获取到 {len(cards)} 张 {rarity}")
        final_cards.extend(cards)
    return final_cards

# 下载卡牌图像
def download_images(cards):
    for card in tqdm(cards, desc="⬇️ 下载卡牌图片"):
        image_url = card.get("images", {}).get("small")
        if not image_url:
            continue
        image_path = os.path.join(IMAGE_DIR, f"{card['id']}.png")
        try:
            img_data = requests.get(image_url).content
            with open(image_path, "wb") as f:
                f.write(img_data)
            card["image"] = os.path.relpath(image_path, OUTPUT_DIR)
        except Exception as e:
            print(f"[错误] 下载失败 {card['id']}: {e}")
    return cards

# 简化存储
def simplify_and_save(cards):
    simplified = []
    for card in cards:
        simplified.append({
            "id": card["id"],
            "name": card.get("name", ""),
            "hp": int(card.get("hp", "0")) if card.get("hp", "0").isdigit() else 0,
            "types": card.get("types", []),
            "rarity": card.get("rarity", "Unknown"),
            "attacks": [{
                "name": atk.get("name", ""),
                "damage": atk.get("damage", ""),
                "text": atk.get("text", "")
            } for atk in card.get("attacks", [])],
            "image": card.get("image", "")
        })
    with open(CARDS_JSON, "w", encoding="utf-8") as f:
        json.dump(simplified, f, indent=2, ensure_ascii=False)
    print(f"✅ 卡牌数据保存至 {CARDS_JSON}，共 {len(simplified)} 张")

# 主入口
if __name__ == "__main__":
    total = input("请输入你要获取的卡牌总数（推荐500）: ").strip()
    try:
        total = int(total)
        if total <= 0:
            raise ValueError
    except ValueError:
        print("❌ 输入无效，必须是一个正整数")
        exit()

    check_and_clean_images()
    cards = fetch_cards_by_rarity(total)
    cards = download_images(cards)
    simplify_and_save(cards)
