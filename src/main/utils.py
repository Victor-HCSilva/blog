import math
from django.utils.html import strip_tags


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calcula o tempo estimado de leitura em minutos para um texto."""
    if not text:
        return 1
    clean_text = strip_tags(text)
    words = len(clean_text.split())
    minutes = math.ceil(words / words_per_minute)
    return max(1, minutes)
