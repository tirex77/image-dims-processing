import os
import textwrap

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def auto_annotate_product(image_path, output_path, font_path=None):
    print(f"📂 Загрузка {image_path}...")

    if not os.path.exists(image_path):
        print(f"❌ Файл не найден: {image_path}")
        return

    img = Image.open(image_path).convert("RGB")

    # 1. ФОРМАТ 3:4 (900×1200)
    target_width = 900
    target_height = 1200

    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        new_width = target_width
        new_height = int(target_width / img_ratio)
    else:
        new_height = target_height
        new_width = int(target_height * img_ratio)

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    canvas_base = Image.new("RGB", (target_width, target_height), (255, 255, 255))
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    canvas_base.paste(img, (paste_x, paste_y))

    img_array = np.array(canvas_base)
    w, h = target_width, target_height

    # 2. ПОИСК ГРАНИЦ ОБЪЕКТА
    gray = np.mean(img_array, axis=2)
    mask = gray < 245
    coords = np.column_stack(np.where(mask))

    if len(coords) == 0:
        print("❌ Не удалось найти объект.")
        return

    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)

    # Отступы для чертежа
    margin_h = 60  # Отступ справа для H
    margin_w = 60  # Отступ снизу для L

    canvas = Image.new("RGB", (w, h), (255, 255, 255))
    canvas.paste(canvas_base, (0, 0))
    draw = ImageDraw.Draw(canvas)

    # 3. ШРИФТ
    if font_path is None:
        candidates = ["Montserrat-Light.ttf", "C:/Windows/Fonts/Montserrat-Light.ttf"]
        for p in candidates:
            if os.path.exists(p):
                font_path = p
                break

    try:
        font_dim = ImageFont.truetype(font_path, 28)
        font_text = ImageFont.truetype(font_path, 16)
    except:
        font_dim = ImageFont.load_default()
        font_text = ImageFont.load_default()

    color = (0, 0, 0)
    line_width = 2

    # === ЭТАП 1: РИСУЕМ СТРЕЛКИ ===

    # 1. L (Длина) - под объектом
    l_y = y_max + margin_w
    l_x_start = x_min
    l_x_end = x_max

    draw.line([(l_x_start, l_y), (l_x_end, l_y)], fill=color, width=line_width)
    draw.line(
        [(l_x_start, l_y - 12), (l_x_start, l_y + 12)], fill=color, width=line_width
    )
    draw.line([(l_x_end, l_y - 12), (l_x_end, l_y + 12)], fill=color, width=line_width)

    # Текст L
    draw.text(
        ((l_x_start + l_x_end) // 2 - 25, l_y + 15), "L 21", fill=color, font=font_dim
    )

    # 2. H (Высота) - справа
    h_x = x_max + margin_h
    h_y_start = y_min
    h_y_end = y_max

    draw.line([(h_x, h_y_start), (h_x, h_y_end)], fill=color, width=line_width)
    draw.polygon(
        [(h_x, h_y_start), (h_x - 6, h_y_start + 12), (h_x + 6, h_y_start + 12)],
        fill=color,
    )
    draw.line([(h_x - 6, h_y_end), (h_x + 6, h_y_end)], fill=color, width=line_width)
    draw.text(
        (h_x + 12, (h_y_start + h_y_end) // 2 - 8), "H 8", fill=color, font=font_dim
    )

    # 3. W (Ширина) - диагональ ВВЕРХ-ВПРАВО от конца L
    w_start = (l_x_end, l_y)
    # Вектор: +X (вправо), -Y (вверх) - это создает правильный угол перспективы
    w_end = (w_start[0] + 50, w_start[1] - 50)

    draw.line([w_start, w_end], fill=color, width=line_width)
    draw.text((w_end[0] + 5, w_end[1] - 5), "W 15", fill=color, font=font_dim)

    # === ЭТАП 2: ДОБАВЛЯЕМ ДИСКЛЕЙМЕР ===
    # Вычисляем самую нижнюю точку, которую заняли стрелки
    # Это либо низ линии L (l_y + 12), либо низ текста W
    lowest_point = max(l_y + 20, w_end[1] + 20)

    # Дисклеймер
    disclaimer = "В комплект поставки входит только товар как на этом фото прочие дополнительные аксессуары использованы в медиа материалах исключительно в художественных и рекламных целях"
    lines = textwrap.wrap(disclaimer, width=100)

    # Начинаем рисовать текст с отступом 40px от самой нижней стрелки
    current_y = lowest_point + 50

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_text)
        text_width = bbox[2] - bbox[0]
        text_x = (w - text_width) // 2  # По центру

        draw.text((text_x, current_y), line, fill=(50, 50, 50), font=font_text)
        current_y += 22

    canvas.save(output_path, quality=95)
    print(f"✅ Готово! Результат: {output_path}")


if __name__ == "__main__":
    my_font = "Montserrat-Light.ttf"
    auto_annotate_product(
        image_path=r"input\100003.jpg",
        output_path="result_step_by_step.jpg",
        font_path=my_font,
    )
