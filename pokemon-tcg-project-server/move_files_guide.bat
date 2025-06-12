@echo off

========================================
文件移动指导脚本
========================================

请按照以下步骤移动你的现有文件：

1. 移动数据库相关文件：
   copy database_manager.py server\game\core\database\
   copy user_dao.py server\game\core\database\daos\
   copy card_dao.py server\game\core\database\daos\

2. 移动认证文件：
   copy auth_manager.py server\game\core\auth\

3. 移动其他Python文件到对应目录

4. 下载部署脚本：
   - 下载 deploy_secure.py 到 deploy\ 目录

5. 准备AWS EC2：
   - 配置Security Group开放端口22和8765
   - 准备好SSH密钥文件

6. 执行部署：
   cd deploy
   python cleanup_old_server.py <EC2-IP> <SSH-KEY-PATH>
   python deploy_secure.py <EC2-IP> <SSH-KEY-PATH>

========================================

Press any key to continue . . . 