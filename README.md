# drone-detection-work

项目基于 YOLOv8 模型开发，主要的开发思路：

- 利用两个 YOLOv8 模型，实现对无人机航拍图像理解后的分析、异常检测，最后给出巡检建议。
- `best.pt` 模型主要用于道路、建筑、树木、车辆等粗粒度因素的检测。
- `yolov8x-visdrone.pt` 模型主要用于这个场景下细粒度的检测。
- 两个模型都已经通过 GitHub Release 的方式上传。(用gitclone命令拉取代码时无法拉取，需要手动下载)
- 模型具体的检测性能还需要再进行实际调节
- 车辆检测与异常判断的训练方案见 `docs/training_anomaly_detection.md`。
- MySQL 用户数据库搭建与角色说明见 `docs/mysql_user_setup.md`。
- Navicat 可直接执行的建表 SQL 见 `docs/mysql_user_schema.sql`。

# 当前用户能力

- 支持 `NORMAL`、`PRO`、`ADMIN` 三种身份。
- 普通用户每账号每日默认 `30` 次免费检测。
- Pro 用户每账号每日默认 `30000` 次免费检测。
- 管理员可执行用户增删改查，并可检查、调整、恢复用户额度。
- 普通用户额度用完后，可在前端“账号与额度”页面升级为 Pro 用户。

# 运行项目流程
- 1. 在 Navicat 或 MySQL 中创建并选择数据库 `drone-detection-sql`
- 2. 执行 `docs/mysql_user_schema.sql`
- 3. 在终端进入项目目录
- 4. `source .venv/bin/activate` 激活虚拟环境
- 5. 配置 MySQL 环境变量，或参考 `backend/.env.example`
- 6. `python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000` 启动后端
- 7. 再开一个终端进入 `frontend`
- 8. 输入 `npm run dev` 启动前端（首次启动需要先 `npm install`）

# 默认管理员

首次使用前需先通过环境变量配置管理员账号密码（参考 `backend/.env.example`），否则系统不会自动创建管理员账号。示例：

```bash
export DEFAULT_ADMIN_USERNAME=your_admin_username
export DEFAULT_ADMIN_PASSWORD=your_secure_password
```
