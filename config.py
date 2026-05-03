import os

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Настройки изображения
IMAGE_SIZE = (900, 1200)  # Ширина, Высота

# Размеры (L, W, H)
DIMENSIONS = {"L": 21, "W": 15, "H": 8}

# Текст дисклеймера
DISCLAIMER_TEXT = (
    "В комплект поставки входит только товар как на этом фото прочие дополнительные аксессуары "
    "использованы в медиа материалах исключительно в художественных и рекламных целях"
)

# Шрифт
FONT_PATH = "Montserrat-Light.ttf"  # Убедитесь, что файл лежит рядом со скриптами
