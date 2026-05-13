# drone-detection-work

项目基于 YOLOv8 模型开发，主要的开发思路：

- 利用两个 YOLOv8 模型，实现对无人机航拍图像理解后的分析、异常检测，最后给出巡检建议。
- `best.pt` 模型主要用于道路、建筑、树木、水域、车辆等粗粒度因素的检测。
- `yolov8x-visdrone.pt` 模型主要用于这个场景下细粒度的检测。
- 两个模型都已经通过 GitHub Release 的方式上传。(用gitclone命令拉取代码时无法拉取，需要手动下载)
- 模型具体的检测性能还需要再进行实际调节

# 运行项目流程
- 1.在终端中进入项目目录
- 2.source .venv/bin/activate激活虚拟环境
- 3.python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000启动后端
- 4.再开一个终端进入项目目录
- 5.输入npm run dev启动前端（首次启动需要先npm install）
