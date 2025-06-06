#!/usr/bin/env python3
"""
项目结构创建脚本
自动创建重构后的游戏项目目录结构和空文件
"""

import os
import sys
from pathlib import Path

class ProjectStructureCreator:
    """项目结构创建器"""
    
    def __init__(self, base_path="."):
        """
        初始化创建器
        
        Args:
            base_path: 项目根目录路径
        """
        self.base_path = Path(base_path).resolve()
        self.created_dirs = []
        self.created_files = []
        
        # 定义项目结构
        self.project_structure = {
            # 根目录文件
            "": [
                "main.py",
                "README.md",
                "requirements.txt",
                ".gitignore"
            ],
            
            # 游戏核心模块
            "game": ["__init__.py"],
            "game/core": ["__init__.py"],
            "game/core/auth": [
                "__init__.py",
                "auth_manager.py"
            ],
            "game/core/database": [
                "__init__.py", 
                "database_manager.py"
            ],
            "game/core/database/daos": [
                "__init__.py",
                "user_dao.py"
            ],
            
            # 场景模块
            "game/scenes": [
                "__init__.py",
                "login_scene.py",
                "register_scene.py"
            ],
            "game/scenes/components": [
                "__init__.py",
                "button_component.py",
                "input_component.py", 
                "message_component.py"
            ],
            "game/scenes/animations": [
                "__init__.py",
                "animation_manager.py",
                "transitions.py"
            ],
            "game/scenes/styles": [
                "__init__.py",
                "theme.py",
                "fonts.py"
            ],
            
            # 工具模块
            "game/utils": [
                "__init__.py",
                "video_background.py",
                "load_font.py"
            ],
            
            # 资源目录
            "assets": [],
            "assets/fonts": [],
            "assets/images": [],
            "assets/images/logo": [],
            "assets/images/icon": [],
            "assets/images/sprites": [],
            "assets/images/sprites/animated": [],
            "assets/images/sprites/animated/female": [],
            "assets/images/sprites/animated/shiny": [],
            "assets/images/sprites/animated/shiny/female": [],
            "assets/videos": [],
            "assets/audio": [],
            "assets/audio/music": [],
            "assets/audio/sfx": [],
            
            # 数据目录
            "data": [],
            "data/backup": [],
            
            # 配置和文档
            "docs": [],
            "config": ["__init__.py"],
            
            # 测试目录
            "tests": [
                "__init__.py",
                "test_auth.py",
                "test_database.py",
                "test_scenes.py"
            ],
            "tests/fixtures": [],
            
            # 脚本目录
            "scripts": [
                "build.py",
                "deploy.py"
            ]
        }
        
        # 文件模板内容
        self.file_templates = {
            "__init__.py": '"""{}模块初始化文件"""',
            "README.md": self.get_readme_template(),
            "requirements.txt": self.get_requirements_template(),
            ".gitignore": self.get_gitignore_template(),
            "main.py": '"""主启动器文件"""\n\nif __name__ == "__main__":\n    print("游戏启动器 - 待实现")',
        }
    
    def get_readme_template(self):
        """获取README模板"""
        return """# Juego de Cartas Coleccionables - Pygame Edition

## 项目描述
基于Pygame的现代化卡牌收集游戏，采用组件化架构设计。

## 项目结构
```
project_root/
├── main.py                   # 主启动器，入口文件
├── game/                     # 游戏主要文件夹
│   ├── core/                 # 核心系统
│   │   ├── auth/            # 认证系统
│   │   └── database/        # 数据库系统
│   ├── scenes/              # 游戏场景
│   │   ├── components/      # UI组件
│   │   ├── animations/      # 动画系统
│   │   └── styles/          # 样式主题
│   └── utils/               # 工具类
├── assets/                  # 游戏资源
├── data/                    # 数据文件
├── tests/                   # 测试文件
└── docs/                    # 文档
```

## 安装依赖
```bash
pip install -r requirements.txt
```

## 运行游戏
```bash
python main.py
```

## 功能特性
- 现代毛玻璃UI风格
- 响应式布局设计
- 流畅的动画效果
- 完整的用户认证系统
- 组件化架构
- 可扩展的场景管理

## 开发说明
- 使用Python 3.8+
- 基于Pygame 2.0+
- 采用组件化设计模式
- 支持主题自定义

## 许可证
MIT License
"""
    
    def get_requirements_template(self):
        """获取依赖文件模板"""
        return """# 核心依赖
pygame>=2.0.0
pygame-gui>=0.6.0

# 可选依赖（视频背景支持）
opencv-python>=4.5.0

# 开发依赖
pytest>=6.0.0
black>=21.0.0
flake8>=3.9.0

# 文档生成
sphinx>=4.0.0
"""
    
    def get_gitignore_template(self):
        """获取gitignore模板"""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Game specific
data/*.db
data/backup/*.db
assets/temp/
logs/
*.log

# OS specific
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
*.tmp
*.temp
"""
    
    def create_directory(self, dir_path):
        """
        创建目录
        
        Args:
            dir_path: 目录路径
        """
        full_path = self.base_path / dir_path
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            self.created_dirs.append(str(full_path))
            print(f"📁 创建目录: {dir_path}")
        except Exception as e:
            print(f"❌ 创建目录失败 {dir_path}: {e}")
    
    def create_file(self, file_path, content=""):
        """
        创建文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
        """
        full_path = self.base_path / file_path
        try:
            # 确保父目录存在
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.created_files.append(str(full_path))
            print(f"📄 创建文件: {file_path}")
        except Exception as e:
            print(f"❌ 创建文件失败 {file_path}: {e}")
    
    def get_file_content(self, filename, dir_path=""):
        """
        获取文件内容
        
        Args:
            filename: 文件名
            dir_path: 目录路径
            
        Returns:
            str: 文件内容
        """
        if filename in self.file_templates:
            if filename == "__init__.py":
                # 为__init__.py生成模块描述
                module_name = dir_path.replace("/", ".") if dir_path else "根模块"
                return self.file_templates[filename].format(module_name)
            else:
                return self.file_templates[filename]
        else:
            # 为Python文件生成基础模板
            if filename.endswith('.py'):
                module_desc = filename.replace('.py', '').replace('_', ' ').title()
                return f'"""\n{module_desc}\n待实现\n"""\n\n# TODO: 实现{module_desc}功能'
            else:
                return f"# {filename}\n# 待配置"
    
    def create_project_structure(self):
        """创建完整的项目结构"""
        print("🚀 开始创建项目结构...")
        print(f"📍 项目根目录: {self.base_path}")
        print("=" * 60)
        
        # 创建所有目录和文件
        for dir_path, files in self.project_structure.items():
            # 创建目录（如果不是根目录）
            if dir_path:
                self.create_directory(dir_path)
            
            # 创建文件
            for filename in files:
                file_path = os.path.join(dir_path, filename) if dir_path else filename
                content = self.get_file_content(filename, dir_path)
                self.create_file(file_path, content)
        
        print("=" * 60)
        print("✅ 项目结构创建完成!")
        self.print_summary()
    
    def print_summary(self):
        """打印创建摘要"""
        print(f"\n📊 创建摘要:")
        print(f"   📁 目录数量: {len(self.created_dirs)}")
        print(f"   📄 文件数量: {len(self.created_files)}")
        
        print(f"\n📁 创建的主要目录:")
        main_dirs = [d for d in self.created_dirs if len(d.split(os.sep)) <= 3][:10]
        for dir_path in sorted(main_dirs):
            relative_path = os.path.relpath(dir_path, self.base_path)
            print(f"   • {relative_path}")
        
        if len(self.created_dirs) > 10:
            print(f"   ... 还有 {len(self.created_dirs) - 10} 个目录")
        
        print(f"\n📄 创建的主要文件:")
        main_files = [f for f in self.created_files if not f.endswith('__init__.py')][:15]
        for file_path in sorted(main_files):
            relative_path = os.path.relpath(file_path, self.base_path)
            print(f"   • {relative_path}")
        
        if len([f for f in self.created_files if not f.endswith('__init__.py')]) > 15:
            remaining = len([f for f in self.created_files if not f.endswith('__init__.py')]) - 15
            print(f"   ... 还有 {remaining} 个文件")
    
    def create_tree_view(self):
        """创建项目树状结构视图"""
        print(f"\n🌳 项目结构树状图:")
        print("```")
        
        # 收集所有路径
        all_paths = set()
        for dir_path, files in self.project_structure.items():
            if dir_path:
                all_paths.add(dir_path)
            for filename in files:
                file_path = os.path.join(dir_path, filename) if dir_path else filename
                all_paths.add(file_path)
        
        # 排序并显示
        sorted_paths = sorted(all_paths)
        for path in sorted_paths[:30]:  # 限制显示数量
            level = path.count('/')
            if level == 0:
                print(f"├── {path}")
            else:
                indent = "│   " * (level - 1) + "├── "
                basename = os.path.basename(path)
                print(f"{indent}{basename}")
        
        if len(sorted_paths) > 30:
            print(f"... 还有 {len(sorted_paths) - 30} 个项目")
        
        print("```")
    
    def verify_structure(self):
        """验证创建的结构"""
        print(f"\n🔍 验证项目结构...")
        
        missing_dirs = []
        missing_files = []
        
        for dir_path, files in self.project_structure.items():
            # 检查目录
            if dir_path:
                full_dir_path = self.base_path / dir_path
                if not full_dir_path.exists():
                    missing_dirs.append(dir_path)
            
            # 检查文件
            for filename in files:
                file_path = os.path.join(dir_path, filename) if dir_path else filename
                full_file_path = self.base_path / file_path
                if not full_file_path.exists():
                    missing_files.append(file_path)
        
        if not missing_dirs and not missing_files:
            print("✅ 项目结构验证通过!")
        else:
            if missing_dirs:
                print(f"❌ 缺失目录: {missing_dirs}")
            if missing_files:
                print(f"❌ 缺失文件: {missing_files}")

def main():
    """主函数"""
    print("🎮 Juego de Cartas Coleccionables - 项目结构创建器")
    print("=" * 60)
    
    # 获取目标目录
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = input("请输入项目目录路径 (回车使用当前目录): ").strip()
        if not target_dir:
            target_dir = "."
    
    # 确认创建
    target_path = Path(target_dir).resolve()
    print(f"📍 将在以下位置创建项目: {target_path}")
    
    if target_path.exists() and any(target_path.iterdir()):
        response = input("⚠️  目录不为空，是否继续? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ 操作已取消")
            return
    
    try:
        # 创建项目结构
        creator = ProjectStructureCreator(target_dir)
        creator.create_project_structure()
        
        # 创建树状视图
        creator.create_tree_view()
        
        # 验证结构
        creator.verify_structure()
        
        print(f"\n🎉 项目结构创建完成!")
        print(f"📂 项目位置: {target_path}")
        print(f"\n📝 下一步:")
        print(f"   1. cd {target_path}")
        print(f"   2. 将重构后的代码文件复制到对应位置")
        print(f"   3. pip install -r requirements.txt")
        print(f"   4. python main.py")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  操作被用户中断")
    except Exception as e:
        print(f"\n❌ 创建过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()