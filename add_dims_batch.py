import os
import textwrap

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def auto_annotate_product(img, output_path, font_path=None):
    """
    Функция обработки одного изображения.
    Принимает объект Image и путь для сохранения.
    """
    img = img.convert("RGB")
    img_array = np.array(img)
    w, h = img.size

    # 1. ПОИСК ГРАНИЦ ОБЪЕКТА
    gray = np.mean(img_array, axis=2)
    mask = gray < 245
    coords = np.column_stack(np.where(mask))

    if len(coords) == 0:
        print(f"   ⚠️ Не удалось найти объект в {output_path}")
        return

    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)

    # Отступы для чертежа
    margin_h = 60
    margin_w = 60

    # Создаем рабочий холст (текущий размер изображения уже может быть 900x1200, если мы его обработали ранее)
    # Если исходные файлы уже приведены к 3:4, работаем с ними.
    # Если нет, лучше сначала привести к 3:4 здесь, но для простоты используем текущий размер.
    # Для соответствия заданию "формат 3:4 900x1200" добавим ресайз внутрь функции.

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

    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    canvas_base = Image.new("RGB", (target_width, target_height), (255, 255, 255))
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    canvas_base.paste(img_resized, (paste_x, paste_y))

    # Пересчитываем координаты объекта для ресайза
    # (Это упрощенно, если масштаб равномерный, координаты тоже масштабируются)
    scale_x = new_width / img.width
    scale_y = new_height / img.height

    # Обновляем координаты с учетом масштабирования
    x_min, x_max = int(x_min * scale_x), int(x_max * scale_x)
    y_min, y_max = int(y_min * scale_y), int(y_max * scale_y)
    # Корректируем на отступ вставки (если картинка меньше холста)
    x_min += paste_x
    x_max += paste_x
    y_min += paste_y
    y_max += paste_y

    canvas = canvas_base.copy()  # Копируем, чтобы рисовать
    draw = ImageDraw.Draw(canvas)

    # Шрифт
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

    # === РАЗМЕРЫ ===

    # 1. L (Длина)
    l_y = y_max + margin_w
    l_x_start = x_min
    l_x_end = x_max

    draw.line([(l_x_start, l_y), (l_x_end, l_y)], fill=color, width=line_width)
    draw.line(
        [(l_x_start, l_y - 12), (l_x_start, l_y + 12)], fill=color, width=line_width
    )
    draw.line([(l_x_end, l_y - 12), (l_x_end, l_y + 12)], fill=color, width=line_width)
    draw.text(
        ((l_x_start + l_x_end) // 2 - 25, l_y + 15), "L 21", fill=color, font=font_dim
    )

    # 2. H (Высота)
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

    # 3. W (Ширина) - ВВЕРХ-ВПРАВО
    w_start = (l_x_end, l_y)
    w_end = (w_start[0] + 50, w_start[1] - 50)

    draw.line([w_start, w_end], fill=color, width=line_width)
    draw.text((w_end[0] + 5, w_end[1] - 5), "W 15", fill=color, font=font_dim)

    # === ДИСКЛЕЙМЕР (Динамический отступ) ===
    lowest_point = max(l_y + 20, w_end[1] + 20)
    current_y = lowest_point + 50  # Отступ 50px

    disclaimer = "В комплект поставки входит только товар как на этом фото прочие дополнительные аксессуары использованы в медиа материалах исключительно в художественных и рекламных целях"
    lines = textwrap.wrap(disclaimer, width=100)

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_text)
        text_width = bbox[2] - bbox[0]
        text_x = (target_width - text_width) // 2
        draw.text((text_x, current_y), line, fill=(50, 50, 50), font=font_text)
        current_y += 22

    # Сохранение в PNG
    canvas.save(output_path, format="PNG")
    print(f"   ✅ Готово: {output_path}")


# --- ГЛАВНЫЙ ЦИКЛ ---
if __name__ == "__main__":
    INPUT_DIR = "input"
    OUTPUT_DIR = "output"
    DIMENSIONS_SUFFIX = "_21x15x8"  # L=21, W=15, H=8
    FONT_FILE = "Montserrat-Light.ttf"

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 Создана папка: {OUTPUT_DIR}")

    files = [
        f
        for f in os.listdir(INPUT_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]

    print(f"🔄 Найдено {len(files)} файлов в {INPUT_DIR}")

    for filename in files:
        base_name = os.path.splitext(filename)[0]
        ext = os.path.splitext(filename)[1]

        input_path = os.path.join(INPUT_DIR, filename)

        # Новое имя: original_name + [L]x[W]x[H]
        output_filename = f"{base_name}{DIMENSIONS_SUFFIX}.png"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        print(f"\n⚙️ Обработка: {filename}")
        try:
            img = Image.open(input_path)
            auto_annotate_product(img, output_path, font_path=FONT_FILE)
        except Exception as e:
            print(f"   ❌ Ошибка при обработке {filename}: {e}")

    print("\n Пакетная обработка завершена!")
