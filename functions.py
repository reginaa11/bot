import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

# --- Функция 1: ПАРСИНГ синонимов (честный скрапинг HTML) ---
def get_synonyms_bs4(word):
    print(f"[Скрапинг] Ищу синонимы для: {word}")
    try:
        encoded_word = urllib.parse.quote(word)
        url = f"https://sinonim.org/s/{encoded_word}"
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем блок с синонимами
        content = soup.find('div', {'id': 'content'})
        if content:
            # Ищем все ссылки и слова
            all_words = re.findall(r'[А-Яа-яёЁ]{3,}', content.get_text())
            synonyms = []
            for w in all_words[:30]:
                if w.lower() != word.lower() and len(w) > 2:
                    synonyms.append(w.lower())
            synonyms = list(dict.fromkeys(synonyms))[:12]
            
            if synonyms:
                return f"🔗 *Синонимы к '{word}' (парсинг sinonim.org):*\n" + ", ".join(synonyms)
        
        return f"😕 Не удалось найти синонимы для '{word}' на сайте"
    except Exception as e:
        return f"⚠️ Ошибка парсинга: {str(e)[:100]}"

# --- Функция 2: ТОЛКОВАНИЕ (честный HTTP API) ---
def get_definition_api(word):
    print(f"[API] Ищу толкование для: {word}")
    try:
        # Пробуем русскоязычный бесплатный API
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            meaning = data[0]['meanings'][0]
            definition = meaning['definitions'][0]['definition']
            part_of_speech = meaning.get('partOfSpeech', '')
            return f"📚 *Толкование '{word}':*\n{part_of_speech}: {definition[:300]}"
        else:
            return f"📚 *'{word}'*\nСлово не найдено в словаре. Попробуй: love, house, beautiful (английские слова)"
    except Exception as e:
        return f"⚠️ Ошибка API: {str(e)[:100]}\nПопробуй английское слово"

# --- Функция 3: РИФМЫ (честный HTTP API) ---
def get_rhyme_api(word):
    print(f"[API] Ищу рифму для: {word}")
    try:
        # Datamuse API — отличный сервис для рифм (работает с английскими словами)
        url = f"https://api.datamuse.com/words?rel_rhy={word}&max=12"
        response = requests.get(url, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            rhymes = [item['word'] for item in data]
            if rhymes:
                return f"🎭 *Рифмы к '{word}' (через API):*\n" + ", ".join(rhymes[:12])
            else:
                return f"🎭 *Рифмы к '{word}'*\nНе найдено. Попробуй: day, night, love, happy"
        else:
            return "🎭 Сервис рифм временно недоступен"
    except Exception as e:
        return f"⚠️ Ошибка API рифм: {str(e)[:100]}"

# --- Функция 4: ПРИМЕРЫ (честный HTTP API) ---
def get_example_api(word):
    print(f"[API] Ищу примеры для: {word}")
    try:
        # Datamuse API может давать примеры через теги
        url = f"https://api.datamuse.com/words?sp={word}&md=p&max=5"
        response = requests.get(url, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            if data and 'tags' in data[0]:
                return f"💡 *Примеры со словом '{word}':*\nИспользуй слово в контексте:«It's a {word} day!»"
        return f"💡 *Примеры со словом '{word}':*\nПопробуй составить предложение сам!"
    except Exception as e:
        return f"⚠️ Ошибка: {str(e)[:80]}"