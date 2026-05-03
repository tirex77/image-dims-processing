import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

IMAGE_SIZE = (900, 1200)

DIMENSIONS = {"L": 21, "W": 15, "H": 8}

DISCLAIMER_TEXT = (
    "В комплект поставки входит только товар как на этом фото прочие дополнительные аксессуары "
    "использованы в медиа материалах исключительно в художественных и рекламных целях"
)

# ВАЖНО: Убедитесь, что файл шрифта существует!
FONT_PATH = "Montserrat-Light.ttf"
