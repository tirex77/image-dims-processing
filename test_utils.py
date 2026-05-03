import os

import utils

INPUT_DIR = "input"
OUTPUT_DIR = "resized_images"


def test_resize():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = utils.find_images_recursive(INPUT_DIR)
    if not files:
        print("⚠️ Нет файлов для теста в папке input/")
        return

    print(f"🚀 Найдено {len(files)} файлов. Запуск теста...\n")

    for rel_path in files:
        input_path = os.path.join(INPUT_DIR, rel_path)
        print(f"📦 Обработка: {rel_path}")

        try:
            # 1. Подготовка изображения
            canvas, bbox = utils.prepare_image(input_path)
            x1, y1, x2, y2 = bbox

            # 2. Сохранение результата
            out_path = (
                os.path.join(OUTPUT_DIR, rel_path)
                .replace(".jpg", ".png")
                .replace(".jpeg", ".png")
            )
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            canvas.save(out_path)

            # 3. Вывод статистики
            width = x2 - x1
            height = y2 - y1
            print(f"   ✅ Сохранено: {out_path}")
            print(f"   📐 BBox: ({x1}, {y1}) → ({x2}, {y2})")
            print(f"   📏 Размер товара на холсте: {width}×{height} px\n")

        except Exception as e:
            print(f"   ❌ Ошибка: {e}\n")

    print(" Тест завершен! Проверьте папку resized_images/")


if __name__ == "__main__":
    test_resize()
