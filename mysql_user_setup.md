# MySQL 用户数据库搭建指南

## 1. 创建数据库和账号

登录 MySQL：

```bash
mysql -u root -p
```

创建数据库和业务账号：

```sql
CREATE DATABASE `drone-detection-sql`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

CREATE USER 'drone_app'@'localhost' IDENTIFIED BY '请替换为强密码';

GRANT ALL PRIVILEGES ON `drone-detection-sql`.* TO 'drone_app'@'localhost';

FLUSH PRIVILEGES;
```

如果后端不在 MySQL 同一台机器上，把 `localhost` 改成后端服务器 IP 或 `%`。

如果你想直接在 Navicat 中建表，可以执行：

```text
docs/mysql_user_schema.sql
```

## 2. 配置后端环境变量

在启动后端前设置：

```bash
export DB_DRIVER=mysql
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=drone_app
export MYSQL_PASSWORD='请替换为强密码'
export MYSQL_DATABASE='drone-detection-sql'
export DEFAULT_ADMIN_USERNAME=your_admin_username
export DEFAULT_ADMIN_PASSWORD=your_secure_password
```

也可以直接在后端目录新建真实配置文件：

```text
backend/.env.example
```

推荐做法：

1. 复制 `backend/.env.example` 为 `backend/.env`
2. 把其中的 MySQL 用户名、密码、数据库名改成你本地实际值
3. 再启动后端

例如 `backend/.env`：

```env
DB_DRIVER=mysql
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的MySQL密码
MYSQL_DATABASE=drone-detection-sql
DEFAULT_ADMIN_USERNAME=your_admin_username
DEFAULT_ADMIN_PASSWORD=your_secure_password
```

后端现在会自动读取这些文件：

```text
.env
.env.local
backend/.env
backend/.env.local
```

然后启动后端：

```bash
.venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

后端启动时会自动创建以下表：

```text
role_configs
users
user_quotas
sessions
detection_logs
quota_change_logs
```

第一次启动前需先通过环境变量 `DEFAULT_ADMIN_USERNAME` 和 `DEFAULT_ADMIN_PASSWORD` 配置管理员账号密码，系统才会自动创建管理员。如果这两个环境变量未设置，则不会自动创建任何管理员账号。

## 3. 用户角色

当前支持三个角色：

```text
NORMAL 普通用户：每账号每日默认 30 次免费检测，可查看自己的检测日志，额度用完后可升级为 Pro。
PRO Pro 用户：每账号每日默认 30000 次免费检测，可查看自己的检测日志。
ADMIN 管理员：可查看所有日志、增删改查用户、检查和调整用户额度。
```

## 4. 额度规则

系统当前实现的额度逻辑如下：

```text
普通用户每次成功检测扣减 1 次额度。
Pro 用户每次成功检测扣减 1 次额度，但默认每日总额度更高。
管理员默认视为高额度账号，可直接使用。
如果检测失败，后端会自动回滚本次扣减。
管理员可以设置 custom_limit 覆盖角色默认额度，也可以恢复为默认额度。
```

## 5. 本地兜底模式

如果不设置 `DB_DRIVER=mysql`，系统会继续使用本地 SQLite 文件：

```text
backend/app.db
```

这适合开发测试；正式部署建议使用 MySQL。
