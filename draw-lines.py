from PIL import Image, ImageDraw
import math
import cv2
import numpy as np
from pathlib import Path


def draw_dots(input: Image, density=100, radius_range=32):
    canvas = Image.new('L', input.size, color='white')
    width, height = input.size
    scale = density / min(width, height)
    width = int(width * scale)
    height = int(height * scale)
    input = input.resize((width, height))
    draw = ImageDraw.Draw(canvas)
    offset = int(min(canvas.size) / density / 2)

    for i in range(width):
        for j in range(height):
            # 根据像素点的亮度
            luminosity = 255 - input.getpixel((i, j))
            radius = int(luminosity / radius_range / 2)
            center = round(i / scale + offset), round(j / scale + offset)
            if radius == 0:
                draw.point(center, fill='black')
            else:
                upperleft = (center[0] - radius, center[1] - radius)
                lowerright = (center[0] + radius, center[1] + radius)
                draw.ellipse([upperleft, lowerright], outline='black')
    canvas.show()
    return canvas


def draw_lines(input: Image):
    """用折线绘制图片"""
    # 是否纵向绘制
    vertical = False
    # 是否反转绘制策略
    # False - 白底黑线，越密表示原图中对应位置越暗
    # True  - 黑底白线，越密表示原图中对应位置越亮
    reverse = False
    # 这三个值相辅相成
    fixed_height = 3200  # 输出图像的纵向分辨率
    density = 200  # 输出图像所包含的所有折线的数量
    thickness = 4  # 线条的粗细
    # 折线的宽度
    scale = fixed_height / density
    # 折线上下的留边
    offset = (1, 0)
    # 折线的角度范围
    angle_range = (32, 85)

    foreground = 'black' if not reverse else 'white'
    background = 'white' if not reverse else 'black'
    if vertical:
        input = input.transpose(Image.ROTATE_90)
    width, height = input.size
    width = int(fixed_height / height * width)
    height = fixed_height
    input = input.resize((width, height))
    canvas = Image.new('L', (width, height), color=background)
    draw = ImageDraw.Draw(canvas)

    # 仅根据当前像素点的亮度调整频率
    for j in range(density):
        i = 0
        while (i < width):
            # 量化为 0~16
            luminosity = input.getpixel((i, scale * j + 5))
            if not reverse:
                luminosity = 255 - luminosity
            luminosity /= 255
            if luminosity < 1 / 16:
                # 如果是纯白色，则
                p1 = (i, scale * j + scale - offset[0])
                p3 = (i + scale, scale * j + scale - offset[0])
                draw.line([p1, p3], fill=foreground, width=thickness)
            else:
                angle = (angle_range[1] -
                         angle_range[0]) * luminosity + angle_range[0]
                angle *= math.pi / 180
                cot = 1 / math.tan(angle)
                p1 = (i, scale * j + scale - offset[0])
                p2 = (i + scale * cot, scale * j + offset[1])
                p3 = (i + 2 * scale * cot, scale * j + scale - offset[0])
                draw.line([p1, p2, p3], fill=foreground, width=thickness)
            i = p3[0]
    if vertical:
        canvas = canvas.transpose(Image.ROTATE_270)
    canvas.show()
    return canvas


def draw_lines_opencv(input,
                      height=2000,
                      density=160,
                      thickness=2,
                      vertical=False,
                      reverse=False):
    """用折线绘制图片"""
    # 是否纵向绘制
    vertical = vertical
    # 是否反转绘制策略
    # False - 白底黑线，越密表示原图中对应位置越暗
    # True  - 黑底白线，越密表示原图中对应位置越亮
    reverse = reverse
    # 这三个值相辅相成
    fixed_height = height  # 输出图像的纵向分辨率
    density = density  # 输出图像所包含的所有折线的数量
    thickness = thickness  # 线条的粗细
    # 折线的宽度
    scale = fixed_height / density
    # 折线上下的留边
    offset = (0, 1)
    # 折线的角度范围
    angle_range = (32, 82)

    foreground = (0, 0, 0) if not reverse else (255, 255, 255)
    background = (255, 255, 255) if not reverse else (0, 0, 0)
    if vertical:
        input = input.transpose(Image.ROTATE_90)
    width, height = input.size
    width = int(fixed_height / height * width)
    height = fixed_height
    input = input.resize((width, height))
    if not reverse:
        canvas = Image.new('L', (width, height), color='white')
    else:
        canvas = Image.new('L', (width, height), color='black')
    canvas = np.array(canvas)

    # 仅根据当前像素点的亮度调整频率
    for j in range(density):
        i = 0
        while (i < width):
            # 量化为 0~16
            luminosity = input.getpixel((i, scale * j + 5))
            if not reverse:
                luminosity = 255 - luminosity
            luminosity /= 255
            if luminosity < 1 / 16:
                # 如果是纯白色，则
                p1 = (round(i), round(scale * j + scale - offset[0]))
                p3 = (round(i + scale), round(scale * j + scale - offset[0]))
                cv2.line(canvas, p1, p3, foreground, thickness, cv2.LINE_AA)
            else:
                angle = (angle_range[1] -
                         angle_range[0]) * luminosity + angle_range[0]
                angle *= math.pi / 180
                cot = 1 / math.tan(angle)
                p1 = (round(i), round(scale * j + scale - offset[0]))
                p2 = (round(i + scale * cot), round(scale * j + offset[1]))
                p3 = (round(i + 2 * scale * cot),
                      round(scale * j + scale - offset[0]))
                cv2.line(canvas, p1, p2, foreground, thickness, cv2.LINE_AA)
                cv2.line(canvas, p2, p3, foreground, thickness, cv2.LINE_AA)
            i = p3[0]
    canvas = Image.fromarray(canvas)
    if vertical:
        canvas = canvas.transpose(Image.ROTATE_270)
    # canvas.show()
    return canvas


def main():
    input_dir = Path("input")
    output_dir = Path("output")
    if not output_dir.exists():
        output_dir.mkdir()
    count = 0
    for f in input_dir.iterdir():
        if f.suffix in ['.jpg', '.jpeg', '.png', '.bmp']:
            im = Image.open(f)
            im_gray = im.convert('L')
            output = draw_lines_opencv(im_gray,
                                       2500,
                                       160,
                                       2,
                                       reverse=False,
                                       vertical=False)
            output.save(output_dir / f.with_suffix('.png').name)
            count += 1
    print(f'{count} image{"" if count < 2 else "s"} processed.')


if __name__ == "__main__":
    main()
