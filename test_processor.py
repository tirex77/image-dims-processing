import os

from PIL import Image, ImageDraw

import config
import processor


def test_with_mock():
    print("🧪 Тест процессора с учетом отступов...")

    # Создаем холст 900x1200
    canvas = Image.new("RGB", (900, 1200), (255, 255, 255))
    d = ImageDraw.Draw(canvas)

    # 🟢 Имитируем bbox с отступами ~80px по краям
    # Как если бы utils.scale=0.80 отработал на вертикальном товаре
    mock_bbox = (75, 90, 825, 1110)

    # Рисуем "товар" для наглядности
    d.rectangle(mock_bbox, fill=(220, 220, 220), outline=(50, 50, 50), width=3)

    print(f"📐 Mock BBox: {mock_bbox}")
    print(f"   Отступ слева/справа: ~{mock_bbox[0]} px")
    print(f"   Отступ сверху/снизу: ~{mock_bbox[1]} px")

    mock_dimensions = {"L": 21, "W": 15, "H": 8}
    output_path = "test_output.png"

    try:
        processor.draw_dimensions(
            canvas=canvas,
            bbox=mock_bbox,
            dimensions=mock_dimensions,
            output_path=output_path,
            font_path=config.FONT_PATH,
        )
        print(f"\n🎉 Готово! Откройте: {output_path}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_with_mock()
