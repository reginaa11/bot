import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

# ВСТРОЕННЫЙ СЛОВАРЬ ДЛЯ РУССКИХ СЛОВ
russian_data = {
    "красивый": {
        "synonyms": ["прекрасный", "великолепный", "восхитительный", "привлекательный", "обаятельный", "живописный", "изящный"],
        "definition": "Вызывающий восхищение своей внешностью, гармоничный, приятный для глаз.",
        "rhymes": ["нетерпеливый", "спесивый", "игривый", "живучий", "справедливый"],
        "examples": ["У неё был очень красивый голос.", "Это красивый поступок.", "Красивый закат на море."]
    },
    "хороший": {
        "synonyms": ["отличный", "превосходный", "замечательный", "классный", "добротный", "качественный"],
        "definition": "Положительный по своим качествам, добротный, удовлетворительный.",
        "rhymes": ["похожий", "пригожий", "осторожный", "сложный", "горошек"],
        "examples": ["Хороший человек всегда поможет.", "Это хорошая новость!", "У тебя хороший вкус."]
    },
    "большой": {
        "synonyms": ["огромный", "громадный", "крупный", "грандиозный", "гигантский", "колоссальный"],
        "definition": "Значительный по размеру, величине, объёму.",
        "rhymes": ["хороший", "пригожий", "чужой", "немой", "золотой"],
        "examples": ["Большой дом на холме.", "У него большое сердце.", "Большой успех ждёт тебя."]
    },
    "маленький": {
        "synonyms": ["крошечный", "мелкий", "небольшой", "миниатюрный", "малый", "компактный"],
        "definition": "Незначительный по размеру, объёму, небольшой.",
        "rhymes": ["спокойненький", "хорошенький", "тоненький", "беленький", "чистенький"],
        "examples": ["Маленький котёнок спал на диване.", "Это маленький секрет.", "Маленькими шагами к большой цели."]
    },
    "умный": {
        "synonyms": ["разумный", "толковый", "сообразительный", "смышленый", "интеллигентный", "мудрый"],
        "definition": "Обладающий ясным умом, сообразительный, толковый.",
        "rhymes": ["шумный", "бездумный", "искусный", "трудный", "чудный"],
        "examples": ["Умный человек учится на чужих ошибках.", "Это очень умное решение."]
    },
    "добрый": {
        "synonyms": ["отзывчивый", "сердечный", "душевный", "милосердный", "благожелательный", "человечный"],
        "definition": "Проявляющий участие, готовый помочь, отзывчивый.",
        "rhymes": ["бодрый", "щедрый", "мудрый", "хитрый", "мокрый"],
        "examples": ["Добрый взгляд всегда согревает.", "Сделай доброе дело сегодня."]
    },
    "любовь": {
        "synonyms": ["обожание", "страсть", "влюблённость", "привязанность", "симпатия", "нежность"],
        "definition": "Глубокое эмоциональное влечение, сердечная привязанность.",
        "rhymes": ["кровь", "вновь", "морковь", "свекровь", "бровь"],
        "examples": ["Любовь к жизни помогает во всём.", "Первая любовь не забывается."]
    },
    "счастье": {
        "synonyms": ["блаженство", "радость", "восторг", "наслаждение", "успех", "удача"],
        "definition": "Состояние абсолютной удовлетворённости жизнью.",
        "rhymes": ["ненастье", "напастье", "пристрастье", "участье", "пастье"],
        "examples": ["Счастье — когда тебя понимают.", "Желаю тебе счастья!"] 
    },
    "доброта": {
        "synonyms": ["отзывчивость", "сердечность", "милосердие", "благожелательность", "человечность"],
        "definition": "Проявление добрых чувств, заботы и внимания к другим.",
        "rhymes": ["высота", "красота", "пустота", "теснота", "частота"],
        "examples": ["Доброта спасёт мир.", "Его доброта известна всем."]
    },
    "радость": {
        "synonyms": ["веселье", "восторг", "ликование", "удовольствие", "счастье"],
        "definition": "Чувство большого удовольствия, душевного удовлетворения.",
        "rhymes": ["сладость", "младость", "гадость", "тягость", "бодрость"],
        "examples": ["Радость переполняла его сердце.", "Дети — наша радость."]
    }
}

#  ФУНКЦИЯ 1: СИНОНИМЫ (парсинг + словарь) 
def get_synonyms_bs4(word):
    print(f"[Скрапинг] Ищу синонимы для: {word}")
    word_lower = word.lower()
    
    # Сначала проверяем встроенный словарь
    if word_lower in russian_data:
        syns = russian_data[word_lower]["synonyms"]
        return f"🔗 *Синонимы к '{word}':*\n" + ", ".join(syns[:12])
    
    # Пробуем парсинг сайта
    try:
        encoded_word = urllib.parse.quote(word_lower)
        url = f"https://sinonim.org/s/{encoded_word}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content = soup.find('div', {'id': 'content'})
        if content:
            words = re.findall(r'[А-Яа-яёЁ]{3,}', content.get_text())
            synonyms = []
            for w in words[:30]:
                if w.lower() != word_lower and len(w) > 2:
                    synonyms.append(w.lower())
            synonyms = list(dict.fromkeys(synonyms))[:12]
            if synonyms:
                return f"🔗 *Синонимы к '{word}' (парсинг):*\n" + ", ".join(synonyms)
    except Exception as e:
        print(f"Парсинг ошибка: {e}")
    
    return f"😕 Синонимы для '{word}' не найдены.\nПопробуй: красивый, добрый, умный, большой"

# ФУНКЦИЯ 2: ТОЛКОВАНИЕ 
def get_definition_api(word):
    print(f"[API] Ищу толкование для: {word}")
    word_lower = word.lower()
    
    # Русские слова из словаря
    if word_lower in russian_data:
        return f"📚 *Толкование слова '{word}':*\n{russian_data[word_lower]['definition']}"
    
    # Английские слова через API
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word_lower}"
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            data = response.json()
            definition = data[0]['meanings'][0]['definitions'][0]['definition']
            return f"📚 *Значение '{word}' (из API):*\n{definition[:300]}"
    except:
        pass
    
    return f"📚 *'{word}'*\nПопробуй русские слова: любовь, счастье, доброта, красивый\nИли английские: love, happy, beautiful"

# ФУНКЦИЯ 3: РИФМЫ
def get_rhyme_api(word):
    print(f"[API] Ищу рифму для: {word}")
    word_lower = word.lower()
    
    # Русские слова
    if word_lower in russian_data and "rhymes" in russian_data[word_lower]:
        rhymes = russian_data[word_lower]["rhymes"]
        return f"🎭 *Рифмы к '{word}':*\n" + ", ".join(rhymes[:10])
    
    # Английские слова через API
    try:
        url = f"https://api.datamuse.com/words?rel_rhy={word_lower}&max=10"
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            rhymes = [item['word'] for item in response.json()]
            if rhymes:
                return f"🎭 *Рифмы к '{word}' (из API):*\n" + ", ".join(rhymes[:10])
    except:
        pass
    
    return f"🎭 *Рифмы к '{word}'*\nПопробуй: день, ночь, любовь, красивый\nИли английские: day, night, love"

# ФУНКЦИЯ 4: ПРИМЕРЫ 
def get_example_api(word):
    print(f"[API] Ищу примеры для: {word}")
    word_lower = word.lower()
    
    # Русские слова
    if word_lower in russian_data and "examples" in russian_data[word_lower]:
        examples = russian_data[word_lower]["examples"]
        return "💡 *Примеры со словом '" + word + "':*\n" + "\n".join([f"• {ex}" for ex in examples[:3]])
    
    return f"💡 *Примеры с '{word}':*\n«Это {word} день!»\n«Он был очень {word} человеком»"