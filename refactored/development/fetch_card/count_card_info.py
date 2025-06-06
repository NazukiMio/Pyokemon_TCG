import json
from collections import Counter
import os

# 路径：相对于当前运行目录
json_path = os.path.join("card_assets", "cards.json")

# 读取 JSON 数据
with open(json_path, "r", encoding="utf-8") as f:
    card_list = json.load(f)

# 初始化计数器
type_counter = Counter()
rarity_counter = Counter()

# 遍历每张卡牌
for card in card_list:
    # 累计每种 type（可能是列表）
    types = card.get("types", [])
    type_counter.update(types)

    # 累计 rarity（是字符串）
    rarity = card.get("rarity", "Unknown")
    rarity_counter[rarity] += 1

# 输出统计结果
print("🧬 类型（types）统计：")
for t, count in type_counter.most_common():
    print(f"  {t}: {count} 张")

print("\n🎖️ 稀有度（rarity）统计：")
for r, count in rarity_counter.most_common():
    print(f"  {r}: {count} 张")

# 拼接保存路径（保存在当前脚本目录）
output_path = os.path.join("development", "fetch_card", "type_rarity_summary.txt")

# 写入统计结果
with open(output_path, "w", encoding="utf-8") as f_out:
    f_out.write("🧬 类型（types）统计：\n")
    for t, count in type_counter.most_common():
        f_out.write(f"  {t}: {count} 张\n")

    f_out.write("\n🎖️ 稀有度（rarity）统计：\n")
    for r, count in rarity_counter.most_common():
        f_out.write(f"  {r}: {count} 张\n")

print(f"\n📁 统计结果已保存至: {output_path}")

