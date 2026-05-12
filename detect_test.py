from ultralytics import YOLO
from pathlib import Path
import json

# 加载 YOLOv8n 模型
model = YOLO("models/best.pt")

# 测试图片路径，后面换成你的航拍图
image_path = "bus.jpg"

# 执行检测
results = model(image_path)

output = []

for result in results:
    boxes = result.boxes

    for box in boxes:
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]
        conf = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        output.append({
            "class_id": cls_id,
            "class_name": cls_name,
            "confidence": round(conf, 4),
            "box": {
                "x1": round(x1, 2),
                "y1": round(y1, 2),
                "x2": round(x2, 2),
                "y2": round(y2, 2)
            },
            "area": round((x2 - x1) * (y2 - y1), 2)
        })

# 保存检测后的图片
save_dir = Path("outputs")
save_dir.mkdir(exist_ok=True)

for result in results:
    result.save(filename=str(save_dir / "result.jpg"))

# 保存 JSON 结果
with open(save_dir / "result.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("检测完成")
print("检测目标数量：", len(output))
print("结果图片：outputs/result.jpg")
print("JSON结果：outputs/result.json")
print(json.dumps(output, ensure_ascii=False, indent=2))