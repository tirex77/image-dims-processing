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


def prepare_image(input_path, target_size=(900, 1200), content_scale=0.80):
    """
    1. Удаляет фон (AI, CPU)
    2. Накладывает на белый слой
    3. Обрезает по границам товара
    4. Масштабирует товар в content_scale от target_size (оставляя отступы)
    5. Центрирует и возвращает (холст, bbox)
    """
    img = Image.open(input_path).convert("RGBA")

    # AI удаление фона (CPU режим)
    img_no_bg = remove(img, providers=["CPUExecutionProvider"])

    # Гарантированный белый фон
    white_bg = Image.new("RGBA", img_no_bg.size, (255, 255, 255))
    img_clean = Image.alpha_composite(white_bg, img_no_bg).convert("RGB")
    img_array = np.array(img_clean)

    # Поиск границ товара
    gray = np.mean(img_array, axis=2)
    mask = gray < 250
    coords = np.column_stack(np.where(mask))

    if len(coords) == 0:
        y_min, x_min, y_max, x_max = 0, 0, img_clean.height, img_clean.width
    else:
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)

    # Обрезка
    product_img = img_clean.crop((x_min, y_min, x_max, y_max))
    orig_w, orig_h = product_img.size

    # 🟢 ВАЖНО: Масштабируем не до 100% холста, а до content_scale (80%)
    # Это гарантирует ~20% свободного места вокруг товара для линий
    target_w, target_h = target_size
    safe_w = target_w * content_scale
    safe_h = target_h * content_scale

    scale = min(safe_w / orig_w, safe_h / orig_h)

    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    resized_product = product_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Центрирование на полном холсте 900x1200
    canvas = Image.new("RGB", target_size, (255, 255, 255))
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    canvas.paste(resized_product, (paste_x, paste_y))

    # Координаты товара относительно холста
    new_bbox = (paste_x, paste_y, paste_x + new_w, paste_y + new_h)

    return canvas, new_bbox
