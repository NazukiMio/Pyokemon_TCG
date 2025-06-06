# Juego de Cartas Coleccionables - Pygame Edition

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
