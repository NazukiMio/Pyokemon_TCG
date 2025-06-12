# Pokemon TCG 项目结构

这是你的Pokemon TCG游戏服务器项目的基础结构。

## 目录说明

### deploy/
- 部署脚本目录
- cleanup_old_server.py: 服务器清理脚本

### server/
- 服务器端代码主目录
- config/: 配置文件目录

### server/game/core/
- 游戏核心逻辑模块

#### database/
- database_manager.py: 数据库管理器
- daos/: 数据访问对象
  - user_dao.py: 用户数据访问
  - card_dao.py: 卡牌数据访问

#### auth/
- auth_manager.py: 身份验证管理器

#### security/
- 安全相关模块（可选）

### server/utils/
- 通用工具模块（可选）

### client/
- 客户端测试文件

## 下一步操作

1. 将你现有的文件移动到对应目录
2. 下载部署脚本到deploy目录
3. 运行部署脚本

详细说明请参考部署指南。
