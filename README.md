# drone-detection-work
-项目基于yolov8模型开发，主要的开发思路为：利用两个yolov8的模型，实现对无人机航拍图像理解后的分析、异常检测最后给出巡检建议
-best.pt模型主要用于道路、建筑、树木、水域、车辆等粗粒度因素的检测
-yolov8x-visdrone.pt模型主要用于这个场景下细粒度的检测
-两个模型都已经通过Github Release的方式上传
