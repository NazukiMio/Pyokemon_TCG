from PIL import Image
import json

def gif_to_json(gif_path, json_path, resize_width=None):
    gif = Image.open(gif_path)
    frames = []

    # 计算按比例缩放高度
    original_width, original_height = gif.size
    if resize_width:
        resize_width = int(resize_width)
        resize_height = int(original_height * (resize_width / original_width))
        resize = (resize_width, resize_height)
        print(f"✔ 将图像缩放至: {resize}")
    else:
        resize = None

    frame_index = 0
    try:
        while True:
            frame = gif.convert('RGBA')
            if resize:
                frame = frame.resize(resize)

            pixels = list(frame.getdata())
            width, height = frame.size

            frames.append({
                'index': frame_index,
                'width': width,
                'height': height,
                'pixels': pixels
            })

            frame_index += 1
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass

    with open(json_path, 'w') as f:
        json.dump(frames, f)

    print(f"\n🎉 转换完成！共 {len(frames)} 帧，输出至：{json_path}")

# 用户输入部分
if __name__ == '__main__':
    gif_path = input("请输入 GIF 文件路径（例如 input.gif）：").strip()
    json_path = input("请输入输出 JSON 文件路径（例如 output.json）：").strip()
    resize_width = input("请输入目标宽度（例如 64，留空则不缩放）：").strip() or None

    gif_to_json(gif_path, json_path, resize_width)
