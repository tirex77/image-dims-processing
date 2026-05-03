import os

from PIL import Image, ImageDraw

import config
import processor


def test_with_mock():
    print("🧪 Запуск теста процессора (Mock data)...")

    # 1. Создаем простой тестовый холст
    canvas = Image.new("RGB", (900, 1200), (255, 255, 255))
    d = ImageDraw.Draw(canvas)

    # Рисуем серый прямоугольник для имитации товара
    # Координаты: слева 100, сверху 150, справа 800, снизу 1050
    mock_bbox = (100, 150, 800, 1050)
    d.rectangle(mock_bbox, fill=(200, 200, 200), outline=(100, 100, 100), width=3)

    print(f"📐 Mock BBox: {mock_bbox}")
    print(f"   Ширина объекта: {mock_bbox[2] - mock_bbox[0]} px")
    print(f"   Высота объекта: {mock_bbox[3] - mock_bbox[1]} px")

    # 2. Моковые размеры
    mock_dimensions = {"L": 21, "W": 15, "H": 8}

    output_path = "test_output.png"

    # 3. Проверка шрифта
    print(f"\n🔤 Проверка шрифта: {config.FONT_PATH}")
    if not os.path.exists(config.FONT_PATH):
        print(f"   ⚠️ Шрифт НЕ найден! Будет использован дефолтный.")
    else:
        print(f"   ✅ Шрифт найден")

    # 4. Запуск процессора
    try:
        processor.draw_dimensions(
            canvas=canvas,
            bbox=mock_bbox,
            dimensions=mock_dimensions,
            output_path=output_path,
            font_path=config.FONT_PATH,
        )
        print(f"\n🎉 Тест успешен! Откройте файл: {output_path}")
    except Exception as e:
        print(f"\n❌ Ошибка при отрисовке: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_with_mock()
