import os
import re

import numpy as np
from PIL import Image
from rembg import remove


def find_images_recursive(directory):
    """Рекурсивный поиск файлов с фильтрацией дубликатов по имени."""
    valid_files = []
    seen_names = set()

    if not os.path.exists(directory):
        print(f"❌ Папка не найдена: {directory}")
        return valid_files

    pattern = re.compile(r"^[\d_]+\.jpe?g$", re.IGNORECASE)

    for root, dirs, files in os.walk(directory):
        files.sort()
        for filename in files:
            if pattern.match(filename):
                if filename in seen_names:
                    continue
                seen_names.add(filename)
                full_path = os.path.join(root, filename)
                valid_files.append(os.path.relpath(full_path, directory))

    return valid_files


def prepare_image(input_path, target_size=(900, 1200)):
    """
    1. Загружает изображение.
    2. Удаляет фон с помощью AI (принудительно CPU).
    3. Гарантирует белый фон (композиция).
    4. Масштабирует и центрирует.
    """
    img = Image.open(input_path).convert("RGBA")

    # 1. AI удаляет фон. providers=['CPUExecutionProvider'] убирает ошибку CUDA
    img_no_bg = remove(img, providers=["CPUExecutionProvider"])

    # 2. Создаем белый фон и накладываем на него результат
    # Это гарантирует, что фон будет белым, а не черным/прозрачным
    white_bg = Image.new("RGBA", img_no_bg.size, (255, 255, 255))
    img_clean = Image.alpha_composite(white_bg, img_no_bg)

    # Теперь работаем с RGB (без альфа-канала)
    img_clean = img_clean.convert("RGB")
    img_array = np.array(img_clean)

    # 3. Находим границы товара (на белом фоне)
    gray = np.mean(img_array, axis=2)
    # Ищем всё, что НЕ белое (255)
    mask = gray < 250
    coords = np.column_stack(np.where(mask))

    if len(coords) == 0:
        # Если не нашли (например, товар тоже белый), берем полный размер
        print(f"   ️ Фон не отделен. Используем полный размер.")
        y_min, x_min, y_max, x_max = 0, 0, img_clean.height, img_clean.width
    else:
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)

    # 4. Обрезаем лишнее
    product_img = img_clean.crop((x_min, y_min, x_max, y_max))
    orig_w, orig_h = product_img.size

    # 5. Расчет масштаба для 900x1200
    target_w, target_h = target_size
    scale = min(target_w / orig_w, target_h / orig_h)

    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    resized_product = product_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 6. Создаем финальный белый холст и вставляем товар
    canvas = Image.new("RGB", target_size, (255, 255, 255))
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    canvas.paste(resized_product, (paste_x, paste_y))

    # 7. Координаты товара на холсте
    new_bbox = (paste_x, paste_y, paste_x + new_w, paste_y + new_h)

    return canvas, new_bbox
