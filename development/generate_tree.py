import os
from graphviz import Digraph

def ask_exclusions():
    print("请输入要排除的目录（多个目录用英文逗号 , 分隔），直接回车使用默认值：assets, development, __pycache__, images, icons, sounds, fonts")
    print("Please enter folders to exclude (comma-separated), or press Enter to use default: assets, development, __pycache__, images, icons, sounds, fonts")
    print("Por favor, introduzca carpetas para excluir (separadas por comas), o pulse Enter para usar: assets, development, __pycache__, images, icons, sounds, fonts")
    print("除外するフォルダをカンマで指定してください。Enterキーでデフォルト（assets, development, __pycache__, images, icons, sounds, fonts）を使います。")
    
    raw = input(">> ").strip()
    if raw:
        return {item.strip() for item in raw.split(",")}
    return {"assets", "development", "__pycache__", "images", "icons", "sounds", "fonts"}

def generate_tree_lines(path, excluded, prefix=""):
    entries = [e for e in sorted(os.listdir(path)) if not e.startswith(".")]
    entries = [e for e in entries if e not in excluded]

    lines = []
    for index, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = "└── " if index == len(entries) - 1 else "├── "
        display_line = f"{prefix}{connector}{entry}"

        if os.path.isdir(full_path):
            lines.append(display_line + "/")
            sub_prefix = f"{prefix}    " if index == len(entries) - 1 else f"{prefix}│   "
            lines.extend(generate_tree_lines(full_path, excluded, sub_prefix))
        else:
            lines.append(display_line)
    return lines

def build_graphviz_tree(dot, path, parent, excluded):
    entries = [e for e in sorted(os.listdir(path)) if not e.startswith(".")]
    entries = [e for e in entries if e not in excluded]

    for entry in entries:
        full_path = os.path.join(path, entry)
        node_id = os.path.relpath(full_path).replace("\\", "/")
        label = entry + "/" if os.path.isdir(full_path) else entry

        dot.node(node_id, label)
        dot.edge(parent, node_id)

        if os.path.isdir(full_path):
            build_graphviz_tree(dot, full_path, node_id, excluded)

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(current_dir) != "development":
        print(f"❌ 当前脚本必须从 development/ 文件夹中运行！当前文件夹为：{current_dir}")
        print(f"❌ This script must be run from inside the 'development/' folder! Current folder: {current_dir}")
        print(f"❌ Este script debe ejecutarse desde la carpeta 'development/'! Carpeta actual: {current_dir}")
        print(f"❌ このスクリプトは 'development/' フォルダ内で実行する必要があります！現在のフォルダ: {current_dir}")
        print("请切换到 development/ 目录后再运行此脚本。")
        print("Please switch to the 'development/' directory and run this script again.")
        print("Por favor, cambie al directorio 'development/' y ejecute este script de nuevo.")
        print("このスクリプトを実行する前に、'development/' ディレクトリに切り替えてください。")
        return

    excluded_dirs = ask_exclusions()
    parent_dir = os.path.abspath(os.path.join(current_dir, ".."))

    txt_file = os.path.join(current_dir, "directory_tree.txt")
    img_file = os.path.join(current_dir, "directory_tree.png")

    print("📁 正在从项目根目录生成目录树（排除 development 与用户指定目录）...")
    print("📁 Generating tree from project root (excluding development and user-specified folders)...")
    print("📁 Generando árbol desde el directorio raíz (excluyendo development y carpetas especificadas)...")
    print("📁 プロジェクトのルートディレクトリからツリーを生成中（developmentおよび指定されたフォルダを除外）...")

    # 文本输出
    lines = ["project_root/"]
    lines.extend(generate_tree_lines(parent_dir, excluded_dirs))
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✅ 文本输出完成：{txt_file}")
    print(f"✅ Text output completed: {txt_file}")
    print(f"✅ Salida de texto completada: {txt_file}")
    print(f"✅ テキスト出力完了：{txt_file}")

    # 图像输出
    dot = Digraph(comment="Directory Tree", format="png")
    dot.attr("node", fontname="Consolas", fontsize="10")

    root_id = "project_root"
    dot.node(root_id, "project_root/")
    build_graphviz_tree(dot, parent_dir, root_id, excluded_dirs)
    dot.render(filename=img_file, directory=current_dir, cleanup=True)
    print(f"✅ 图像输出完成：{img_file}")
    print(f"✅ Image output completed: {img_file}")
    print(f"✅ Salida de imagen completada: {img_file}")
    print(f"✅ 画像出力完了：{img_file}")

if __name__ == "__main__":
    main()
