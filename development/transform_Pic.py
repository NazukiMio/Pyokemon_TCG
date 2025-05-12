import os
import json
from PIL import Image

def image_to_pixel_array_rgba(img):
    """Convert image to 2D list of [R, G, B, A] values"""
    pixels = list(img.getdata())
    width, height = img.size
    return [pixels[i * width:(i + 1) * width] for i in range(height)]

# 获取图像路径
user_input = input("Please input the image file path, if you have put the image in folder 'Pic_to_transform' then input only filename: ").strip()
if os.path.dirname(user_input) == "":
    image_path = os.path.join("Pic_to_transform", user_input)
else:
    image_path = user_input

# 打开图像
img = Image.open(image_path).convert("RGBA")
original_width, original_height = img.size
aspect_ratio = original_height / original_width

# 获取目标宽度并计算高度
resolution_x = int(input(f"Enter desired image width (original: {original_width}): "))
resolution_y = round(resolution_x * aspect_ratio)

# 缩放图像
img = img.resize((resolution_x, resolution_y), Image.NEAREST)

# 获取像素数据
pixel_data = image_to_pixel_array_rgba(img)

# 准备输出数据
output_data = {
    "width": resolution_x,
    "height": resolution_y,
    "pixels": pixel_data,
    "mode": "RGBA"
}

# 保存到 JSON
output_folder = "Pic_transformed"
os.makedirs(output_folder, exist_ok=True)
filename = os.path.splitext(os.path.basename(image_path))[0]
json_path = os.path.join(output_folder, f"{filename}_pixel_{resolution_x}w.json")

with open(json_path, "w") as f:
    json.dump(output_data, f)

print(f"✅ Pixel data exported to JSON: {json_path}")
