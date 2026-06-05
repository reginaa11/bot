import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import time
import os
from config import VK_TOKEN, GROUP_ID
from functions import get_synonyms_bs4, get_definition_api, get_rhyme_api, get_example_api

# Хранилище последнего слова для каждого пользователя
user_last_word = {}

def log_to_file(user_id, message, response_text):
    if not os.path.exists("logs"):
        os.makedirs("logs")
    with open(f"logs/{user_id}.log", "a", encoding="utf-8") as f:
        f.write(f"[{time.ctime()}] Запрос: {message}\n")
        f.write(f"[{time.ctime()}] Ответ: {response_text}\n")
        f.write("-" * 50 + "\n")
    print(f"Лог сохранён для {user_id}")

def get_main_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("🔍 Синоним", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("📖 Толкование", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🎭 Рифма", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("💡 Пример", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("❓ Помощь", color=VkKeyboardColor.SECONDARY)
    return keyboard

def get_word_input_keyboard(action):
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button(f"✏️ Введи слово для {action}", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🔙 Отмена", color=VkKeyboardColor.NEGATIVE)
    return keyboard

def get_action_keyboard(word):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button(f"🔍 Синоним к '{word[:15]}'", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button(f"📖 Толкование '{word[:15]}'", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button(f"🎭 Рифма к '{word[:15]}'", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button(f"💡 Пример с '{word[:15]}'", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🔄 Новое слово", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("❓ Помощь", color=VkKeyboardColor.SECONDARY)
    return keyboard

def main():
    print("Бот с кнопками запущен...")
    print(f"ID группы: {GROUP_ID}")
    
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    
    user_state = {}
    
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                msg = event.object.message
                user_id = msg['from_id']
                peer_id = msg['peer_id']
                message_text = msg['text'].strip()
                
                print(f"Сообщение от {user_id}: {message_text}")
                answer = ""
                keyboard = None
                
                # Главное меню / Помощь
                if message_text.lower() in ["помощь", "help", "start", "начать", "/start"] or message_text == "❓ Помощь":
                    answer = "📖 *Выбери действие на кнопках ниже:*\n\nНажми на кнопку, затем введи слово."
                    keyboard = get_main_keyboard()
                    user_state.pop(user_id, None)
                
                # Кнопки действий
                elif message_text == "🔍 Синоним":
                    answer = "🔍 *Введи слово, для которого нужно найти синонимы:*"
                    keyboard = get_word_input_keyboard("синонима")
                    user_state[user_id] = {'action': 'synonym', 'waiting_for_word': True}
                
                elif message_text == "📖 Толкование":
                    answer = "📖 *Введи слово, для которого нужно толкование:*"
                    keyboard = get_word_input_keyboard("толкования")
                    user_state[user_id] = {'action': 'definition', 'waiting_for_word': True}
                
                elif message_text == "🎭 Рифма":
                    answer = "🎭 *Введи слово, для которого нужно подобрать рифму:*"
                    keyboard = get_word_input_keyboard("рифмы")
                    user_state[user_id] = {'action': 'rhyme', 'waiting_for_word': True}
                
                elif message_text == "💡 Пример":
                    answer = "💡 *Введи слово, для которого нужны примеры:*"
                    keyboard = get_word_input_keyboard("примера")
                    user_state[user_id] = {'action': 'example', 'waiting_for_word': True}
                
                elif message_text == "🔙 Отмена":
                    answer = "❌ Действие отменено. Выбери новое действие:"
                    keyboard = get_main_keyboard()
                    user_state.pop(user_id, None)
                
                elif message_text == "🔄 Новое слово":
                    answer = "✏️ *Введи новое слово:*"
                    keyboard = get_word_input_keyboard("работы")
                    user_state[user_id] = {'waiting_for_word': True}
                
                # Действия с конкретным словом
                elif message_text.startswith("🔍 Синоним к '"):
                    word = message_text.replace("🔍 Синоним к '", "").rstrip("'")
                    answer = get_synonyms_bs4(word)
                    keyboard = get_action_keyboard(word)
                    user_last_word[user_id] = word
                
                elif message_text.startswith("📖 Толкование '"):
                    word = message_text.replace("📖 Толкование '", "").rstrip("'")
                    answer = get_definition_api(word)
                    keyboard = get_action_keyboard(word)
                    user_last_word[user_id] = word
                
                elif message_text.startswith("🎭 Рифма к '"):
                    word = message_text.replace("🎭 Рифма к '", "").rstrip("'")
                    answer = get_rhyme_api(word)
                    keyboard = get_action_keyboard(word)
                    user_last_word[user_id] = word
                
                elif message_text.startswith("💡 Пример с '"):
                    word = message_text.replace("💡 Пример с '", "").rstrip("'")
                    answer = get_example_api(word)
                    keyboard = get_action_keyboard(word)
                    user_last_word[user_id] = word
                
                # Ожидание ввода слова
                elif user_id in user_state and user_state[user_id].get('waiting_for_word'):
                    word = message_text.strip()
                    action = user_state[user_id].get('action', 'synonym')
                    
                    if len(word) < 2:
                        answer = "❌ Слишком короткое слово. Попробуй ещё раз:"
                        keyboard = get_word_input_keyboard(action)
                    else:
                        if action == 'synonym':
                            answer = get_synonyms_bs4(word)
                        elif action == 'definition':
                            answer = get_definition_api(word)
                        elif action == 'rhyme':
                            answer = get_rhyme_api(word)
                        elif action == 'example':
                            answer = get_example_api(word)
                        else:
                            answer = get_synonyms_bs4(word)
                        
                        keyboard = get_action_keyboard(word)
                        user_last_word[user_id] = word
                        user_state.pop(user_id, None)
                
                # Просто слово
                elif len(message_text) >= 2 and len(message_text) <= 30 and message_text.replace(' ', '').isalpha():
                    word = message_text.strip()
                    answer = f"🔍 *Что делать со словом '{word}'?*"
                    keyboard = get_action_keyboard(word)
                    user_last_word[user_id] = word
                
                # Непонятная команда
                else:
                    answer = """❓ *Я не понял запрос.*

Нажми на кнопку внизу, чтобы выбрать действие:

🔍 Синоним — найти похожие слова
📖 Толкование — узнать значение
🎭 Рифма — подобрать рифму
💡 Пример — посмотреть примеры использования

Или просто напиши слово, и я предложу варианты!"""
                    keyboard = get_main_keyboard()
                
                vk.messages.send(
                    peer_id=peer_id,
                    message=answer,
                    random_id=random.randint(1, 2**31),
                    keyboard=keyboard.get_keyboard() if keyboard else None
                )
                
                log_to_file(user_id, message_text, answer[:200] + "..." if len(answer) > 200 else answer)
                
            except Exception as e:
                print(f"Ошибка: {e}")
                try:
                    vk.messages.send(
                        peer_id=peer_id,
                        message=f"⚠️ Ошибка: {str(e)[:100]}",
                        random_id=random.randint(1, 2**31)
                    )
                except:
                    pass

if __name__ == "__main__":
    main()