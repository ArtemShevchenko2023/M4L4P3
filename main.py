import telebot
import sqlite3
from telebot import types

# Инициализация бота
bot = telebot.TeleBot("")

# Подключение к базе данных SQLite
conn = sqlite3.connect('notes.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''create table if not exists notes
                  (id integer primary key, user_id integer, note text)''')
conn.commit()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Этот бот поможет вам управлять заметками. Используйте /help для получения списка команд.")

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, "/add - добавить новую заметку\n/delete - удалить заметку\n/list - список заметок\n/edit - редактировать заметку")

# Обработчик команды /add
@bot.message_handler(commands=['add'])
def add_note(message):
    bot.reply_to(message, "Введите заметку:")
    bot.register_next_step_handler(message, save_note)

def save_note(message):
    user_id = message.from_user.id
    note = message.text
    cursor.execute("insert into notes (user_id, note) values (?, ?)", (user_id, note))
    conn.commit()
    bot.reply_to(message, "Заметка успешно добавлена!")

# Обработчик команды /delete
@bot.message_handler(commands=['delete'])
def delete_note(message):
    bot.reply_to(message, "Введите номер заметки, которую нужно удалить:")
    bot.register_next_step_handler(message, remove_note)

def remove_note(message):
    try:
        note_id = int(message.text)
        cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))
        conn.commit()
        bot.reply_to(message, "Заметка удалена успешно!")
    except ValueError:
        bot.reply_to(message, "Узнайте номер заметки в /list и пропишите /delete снова.")

# Обработчик команды /list
@bot.message_handler(commands=['list'])
def list_notes(message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM notes WHERE user_id=?", (user_id,))
    notes = cursor.fetchall()
    if notes:
        for note in notes:
            bot.send_message(message.chat.id, f"Заметка {note[0]}: {note[2]}")
    else:
        bot.reply_to(message, "У вас пока нет заметок.")

# Обработчик команды /edit
@bot.message_handler(commands=['edit'])
def edit_note_step1(message):
    bot.reply_to(message, "Введите номер заметки, которую нужно отредактировать:")
    bot.register_next_step_handler(message, edit_note_step2)

def edit_note_step2(message):
    try:
        note_id = int(message.text)
        bot.reply_to(message, "Введите новый текст заметки:")
        bot.register_next_step_handler(message, lambda msg: edit_note_save(msg, note_id))
    except ValueError:
        bot.reply_to(message, "Узнайте номер заметки в /list и пропишите /edit снова.")

def edit_note_save(message, note_id):
    new_text = message.text
    cursor.execute("UPDATE notes SET note=? WHERE id=?", (new_text, note_id))
    conn.commit()
    bot.reply_to(message, "Заметка успешно отредактирована!")

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Используйте /help для получения списка команд.")

# Запуск бота
bot.polling()