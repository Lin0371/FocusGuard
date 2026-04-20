import os
from PIL import Image, ImageDraw

# 确保 assets 目录存在
assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
os.makedirs(assets_dir, exist_ok=True)

size = 64
img = Image.new('RGBA', (size, size), (0,0,0,0))
draw = ImageDraw.Draw(img)
# 紫色圆底
draw.ellipse([2,2,62,62], fill='#6366f1')
# 眼睛外轮廓（菱形）
eye_points = [(12,32),(32,18),(52,32),(32,46)]
draw.polygon(eye_points, fill='#e8e8f0')
# 虹膜
draw.ellipse([24,24,40,40], fill='#16162a')
# 瞳孔高光
draw.ellipse([29,28,35,34], fill='#e8e8f0')

icon_path = os.path.join(assets_dir, 'icon.ico')
img.save(icon_path, format='ICO')
print(f"[生成] 托盘图标已保存: {icon_path}")
