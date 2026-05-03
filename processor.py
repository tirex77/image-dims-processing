import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

import config


def draw_dimensions(canvas, bbox, dimensions, output_path, font_path=None):
    """
    Рисует размерные линии и текст на готовом холсте.
    """
    x_min, y_min, x_max, y_max = bbox
    width_obj = x_max - x_min
    height_obj = y_max - y_min

    draw = ImageDraw.Draw(canvas)
    w_canvas, h_canvas = canvas.size

    # Шрифты
    try:
        font_dim = ImageFont.truetype(font_path or config.FONT_PATH, 28)
        font_text = ImageFont.truetype(font_path or config.FONT_PATH, 16)
    except Exception:
        font_dim = ImageFont.load_default()
        font_text = ImageFont.load_default()

    color = (0, 0, 0)
    line_width = 2
    tick_len = 12

    # 1. БЕЗОПАСНЫЕ ОТСТУПЫ (не дадут линиям улететь за край)
    # Максимально возможный отступ справа = 900 - x_max - 40px (резерв)
    max_margin_h = max(30, w_canvas - x_max - 60)
    margin_h = min(int(width_obj * 0.08), max_margin_h)

    # Максимально возможный отступ снизу = 1200 - y_max - 60px
    max_margin_w = max(30, h_canvas - y_max - 80)
    margin_w = min(int(height_obj * 0.08), max_margin_w)

    # === 1. L (Длина) ===
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

    # === 2. H (Высота) ===
    h_x = x_max + margin_h
    h_y_start = y_min
    h_y_end = y_max

    draw.line([(h_x, h_y_start), (h_x, h_y_end)], fill=color, width=line_width)
    draw.polygon(
        [(h_x, h_y_start), (h_x - 6, h_y_start + 12), (h_x + 6, h_y_start + 12)],
        fill=color,
    )
    draw.line([(h_x - 6, h_y_end), (h_x + 6, h_y_end)], fill=color, width=line_width)

    # Текст H с проверкой выхода за правый край
    h_text = f"H {dimensions['H']}"
    h_text_x = h_x + 12
    h_text_y = (h_y_start + h_y_end) // 2 - 8

    # Если текст упирается в край, сдвигаем влево
    h_text_bbox = draw.textbbox((0, 0), h_text, font=font_dim)
    if h_text_x + h_text_bbox[2] > w_canvas - 10:
        h_text_x = h_x - h_text_bbox[2] - 12  # Рисуем слева от линии

    draw.text((h_text_x, h_text_y), h_text, fill=color, font=font_dim)

    # === 3. W (Глубина) ===
    w_start = (l_x_end, l_y)

    # Динамическая длина, но не более 70px, чтобы не вылезти
    w_len = min(70, int(width_obj * 0.15))
    w_dx = int(w_len * 0.8)
    w_dy = int(w_len * 0.8)  # Вверх

    w_end = (w_start[0] + w_dx, w_start[1] - w_dy)

    # Финальная защита от выхода за холст
    if w_end[0] > w_canvas - 20:
        w_end = (w_canvas - 20, w_end[1])

    draw.line([w_start, w_end], fill=color, width=line_width)
    draw.text(
        (w_end[0] + 5, w_end[1] - 5), f"W {dimensions['W']}", fill=color, font=font_dim
    )

    # === 4. Дисклеймер (Безопасная позиция) ===
    lowest_point = max(l_y + tick_len + 15, w_end[1] + 15)

    # Резервируем 80px снизу под текст
    current_y = min(lowest_point + 60, h_canvas - 80)

    lines = textwrap.wrap(config.DISCLAIMER_TEXT, width=100)
    for line in lines:
        bbox_txt = draw.textbbox((0, 0), line, font=font_text)
        text_width = bbox_txt[2] - bbox_txt[0]
        text_x = (w_canvas - text_width) // 2

        # Если текст упирается в низ, уменьшаем отступ
        if current_y + bbox_txt[3] > h_canvas - 10:
            current_y = h_canvas - bbox_txt[3] - 10

        draw.text((text_x, current_y), line, fill=(50, 50, 50), font=font_text)
        current_y += 22

    canvas.save(output_path, format="PNG")
    print(f"   ✅ Сохранено: {output_path}")
