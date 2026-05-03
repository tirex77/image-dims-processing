import os
import textwrap

import config
from PIL import Image, ImageDraw, ImageFont


def draw_dimensions(canvas, bbox, dimensions, output_path, font_path=None):
    """
    Рисует размерные линии и текст на готовом холсте.
    :param canvas: PIL.Image (уже 900x1200 с товаром)
    :param bbox: (x_min, y_min, x_max, y_max)
    :param dimensions: dict {"L": 21, "W": 15, "H": 8}
    :param output_path: путь для сохранения
    """
    x_min, y_min, x_max, y_max = bbox
    width_obj = x_max - x_min
    height_obj = y_max - y_min

    draw = ImageDraw.Draw(canvas)

    # Шрифты
    try:
        font_dim = ImageFont.truetype(font_path or config.FONT_PATH, 28)
        font_text = ImageFont.truetype(font_path or config.FONT_PATH, 16)
    except Exception:
        font_dim = ImageFont.load_default()
        font_text = ImageFont.load_default()

    color = (0, 0, 0)
    line_width = 2

    # Динамические отступы (зависят от размера объекта)
    # Чем больше объект, тем больше отступы для линий
    margin_h = max(40, int(width_obj * 0.08))
    margin_w = max(40, int(height_obj * 0.08))
    tick_len = 12

    # === 1. L (Длина) - горизонтальная снизу ===
    l_y = y_max + margin_w
    l_x_start = x_min
    l_x_end = x_max

    draw.line([(l_x_start, l_y), (l_x_end, l_y)], fill=color, width=line_width)
    draw.line(
        [(l_x_start, l_y - tick_len), (l_x_start, l_y + tick_len)],
        fill=color,
        width=line_width,
    )
    draw.line(
        [(l_x_end, l_y - tick_len), (l_x_end, l_y + tick_len)],
        fill=color,
        width=line_width,
    )

    l_text = f"L {dimensions['L']}"
    l_bbox = draw.textbbox((0, 0), l_text, font=font_dim)
    l_text_w = l_bbox[2] - l_bbox[0]
    draw.text(
        ((l_x_start + l_x_end) // 2 - l_text_w // 2, l_y + 15),
        l_text,
        fill=color,
        font=font_dim,
    )

    # === 2. H (Высота) - вертикальная справа ===
    h_x = x_max + margin_h
    h_y_start = y_min
    h_y_end = y_max

    draw.line([(h_x, h_y_start), (h_x, h_y_end)], fill=color, width=line_width)
    # Стрелка сверху
    draw.polygon(
        [(h_x, h_y_start), (h_x - 6, h_y_start + 12), (h_x + 6, h_y_start + 12)],
        fill=color,
    )
    # Засечка снизу
    draw.line([(h_x - 6, h_y_end), (h_x + 6, h_y_end)], fill=color, width=line_width)
    draw.text(
        (h_x + 12, (h_y_start + h_y_end) // 2 - 8),
        f"H {dimensions['H']}",
        fill=color,
        font=font_dim,
    )

    # === 3. W (Глубина) - диагональ от конца L ===
    w_start = (l_x_end, l_y)
    # Вектор глубины: 30% от ширины вправо, 25% от высоты вверх
    w_dx = int(width_obj * 0.3)
    w_dy = int(height_obj * 0.25)
    w_end = (w_start[0] + w_dx, w_start[1] - w_dy)

    draw.line([w_start, w_end], fill=color, width=line_width)
    draw.text(
        (w_end[0] + 5, w_end[1] - 5), f"W {dimensions['W']}", fill=color, font=font_dim
    )

    # === 4. Дисклеймер (динамический отступ) ===
    # Находим самую нижнюю точку (либо низ линии L, либо низ линии W)
    lowest_point = max(l_y + tick_len + 15, w_end[1] + 15)
    current_y = lowest_point + 50

    lines = textwrap.wrap(config.DISCLAIMER_TEXT, width=100)
    for line in lines:
        bbox_txt = draw.textbbox((0, 0), line, font=font_text)
        text_width = bbox_txt[2] - bbox_txt[0]
        text_x = (canvas.width - text_width) // 2
        draw.text((text_x, current_y), line, fill=(50, 50, 50), font=font_text)
        current_y += 22

    canvas.save(output_path, format="PNG")
    print(f"   ✅ Размеры нанесены: {output_path}")
