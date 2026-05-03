import os

import config
from PIL import Image

import processor


def test_with_mock():
    print("🧪 Запуск теста процессора (Mock data)...")

    # 1. Ищем любую картинку в resized_images для теста
    test_dir = "resized_images"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    test_files = [f for f in os.listdir(test_dir) if f.endswith(".png")]

    if test_files:
        # Берем первый попавшийся файл
        input_file = os.path.join(test_dir, test_files[0])
        print(f"📂 Используем файл: {input_file}")
        canvas = Image.open(input_file).convert("RGB")

        # МОКОВЫЕ ДАННЫЕ (bbox, который мы получили ранее)
        # Для примера берем координаты из вашего лога: (0, 80) -> (900, 1120)
        # Если файл другой, bbox может быть неточным, но для теста сойдет
        mock_bbox = (0, 80, 900, 1120)
    else:
        # Если картинок нет, создаем белый холст 900x1200
        print("⚠️ Нет картинок в resized_images. Создаю пустой холст.")
        canvas = Image.new("RGB", (900, 1200), (255, 255, 255))
        # Рисуем серый прямоугольник для имитации товара
        from PIL import ImageDraw

        d = ImageDraw.Draw(canvas)
        d.rectangle([(50, 100), (850, 1100)], fill=(200, 200, 200))
        mock_bbox = (50, 100, 850, 1100)

    # 2. Моковые размеры
    mock_dimensions = {"L": 21, "W": 15, "H": 8}

    output_path = "test_output.png"

    # 3. Запуск процессора
    try:
        processor.draw_dimensions(
            canvas=canvas,
            bbox=mock_bbox,
            dimensions=mock_dimensions,
            output_path=output_path,
            font_path=config.FONT_PATH,
        )
        print(f"🎉 Тест успешен! Откройте файл: {output_path}")
    except Exception as e:
        print(f"❌ Ошибка при отрисовке: {e}")


if __name__ == "__main__":
    test_with_mock()
