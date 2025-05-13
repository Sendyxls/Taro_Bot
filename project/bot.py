import random

import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton,
    LabeledPrice, PreCheckoutQuery, Message
)
from openai import OpenAI
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import asyncio

# --- Настройки ---
TELEGRAM_TOKEN = "7549107815:AAFnvC8Fe9FoSAHGBtdSgVpW8TrVzP6YDVY"
GPT_API_KEY = "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"
client = OpenAI(api_key=GPT_API_KEY, base_url="https://openrouter.ai/api/v1")
SHOP_ID = "1061384"
PROVIDER_TOKEN = "381764678:TEST:116332"
CURRENCY = "RUB"

bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- Карты Таро ---
TAROT_CARDS = [
    # Старшие Арканы (22 карты)
    "Шут", "Маг", "Верховная Жрица", "Императрица", "Император", "Иерофант",
    "Влюблённые", "Колесница", "Сила", "Отшельник", "Колесо Фортуны", "Справедливость",
    "Повешенный", "Смерть", "Умеренность", "Дьявол", "Башня", "Звезда", "Луна", "Солнце",
    "Суд", "Мир",

    # Младшие Арканы (56 карт)
    # Жезлы
    "Туз Жезлов", "Двойка Жезлов", "Тройка Жезлов", "Четвёрка Жезлов", "Пятёрка Жезлов",
    "Шестёрка Жезлов", "Семёрка Жезлов", "Восьмёрка Жезлов", "Девятка Жезлов", "Десятка Жезлов",
    "Паж Жезлов", "Рыцарь Жезлов", "Королева Жезлов", "Король Жезлов",

    # Кубки
    "Туз Кубков", "Двойка Кубков", "Тройка Кубков", "Четвёрка Кубков", "Пятёрка Кубков",
    "Шестёрка Кубков", "Семёрка Кубков", "Восьмёрка Кубков", "Девятка Кубков", "Десятка Кубков",
    "Паж Кубков", "Рыцарь Кубков", "Королева Кубков", "Король Кубков",

    # Мечи
    "Туз Мечей", "Двойка Мечей", "Тройка Мечей", "Четвёрка Мечей", "Пятёрка Мечей",
    "Шестёрка Мечей", "Семёрка Мечей", "Восьмёрка Мечей", "Девятка Мечей", "Десятка Мечей",
    "Паж Мечей", "Рыцарь Мечей", "Королева Мечей", "Король Мечей",

    # Пентакли
    "Туз Пентаклей", "Двойка Пентаклей", "Тройка Пентаклей", "Четвёрка Пентаклей", "Пятёрка Пентаклей",
    "Шестёрка Пентаклей", "Семёрка Пентаклей", "Восьмёрка Пентаклей", "Девятка Пентаклей", "Десятка Пентаклей",
    "Паж Пентаклей", "Рыцарь Пентаклей", "Королева Пентаклей", "Король Пентаклей"
]
# --- Состояния ---
class TarotState(StatesGroup):
    waiting_for_question = State()

class PostPaymentState(StatesGroup):
    waiting_for_post_payment_input = State()

# --- Выбор случайных карт ---
def draw_tarot_cards():
    return [f"{card} (Перевёрнутая)" if random.choice([True, False]) else card for card in random.sample(TAROT_CARDS, 3)]

# --- Получение трактовки от GPT ---
def get_tarot_interpretation_llama(question, cards):
    try:
        with open("Promt.txt", "r", encoding="utf-8") as file:
            content = file.read().strip()
        full_prompt = f"{content}\n\nВопрос: {question}. Выпали карты: {', '.join(cards)}."

        response = client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324:free",  # или deepseek-chat
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": full_prompt},
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка: {str(e)}"

# --- Старт ---
@dp.message(CommandStart())
async def send_welcome(message: Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🔮Задать вопрос"), KeyboardButton(text="🤔Как это работает?")]
    ], resize_keyboard=True)
    await message.answer("Привет,! Я Enigma 🔮 \n"
                         "Добро пожаловать в мир Таро — зеркало твоей души \n"
                         "Задай вопрос, который тебя волнует, и я помогу найти ответ с помощью древних карт 🌟 \n"
                         "🔮 Готов(а) получить предсказание?", reply_markup=keyboard)

@dp.message(F.text == "🤔Как это работает?")
async def explain(message: Message):
    await message.answer("🔮Добро пожаловать в Enigma! \n"
                         "Ты попал сюда не случайно — карты уже начали свой танец вокруг твоего вопроса. Следуй подсказкам на экране, и когда Enigma попросит тебя написать вопрос, сформулируй то, что тебя беспокоит или интересует. Древние знания Таро помогут раскрыть тайны и дать тебе мудрые ответы ✨ \n"
                         "Как правильно задать вопрос? \n"
                         "Например: \n"
                         "❌«Что меня ждёт?» — слишком общий вопрос. \n"
                         "✅«Что мне нужно знать о моих отношениях с [имя]?» — чёткий и конкретный. \n"
                         "Доверься интуиции — карты уже ждут твоего запроса...🃏")

@dp.message(F.text == "🔮Задать вопрос")
async def choose_theme(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="💖 Любовь и отношения")],
        [KeyboardButton(text="💼 Карьера и деньги")],
        [KeyboardButton(text="🌀 Личное развитие и духовный путь")],
        [KeyboardButton(text="🔮 Общий расклад")]
    ])
    await message.answer("Выбери сферу:", reply_markup=markup)

@dp.message(F.text.in_(["💖 Любовь и отношения", "💼 Карьера и деньги", "🌀 Личное развитие и духовный путь", "🔮 Общий расклад"]))
async def ask_question(message: Message, state: FSMContext):
    await message.answer("✨ Напиши свой вопрос:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(TarotState.waiting_for_question)

@dp.message(TarotState.waiting_for_question)
async def process_tarot_reading(message: Message, state: FSMContext):
    question = message.text
    cards = draw_tarot_cards()
    interpretation =  get_tarot_interpretation_llama(question, cards)
    await message.answer(
        f"✨ Твой расклад:\n1️⃣ {cards[0]}\n2️⃣ {cards[1]}\n3️⃣ {cards[2]}\n\n🔮 Трактовка:\n{interpretation}"
    )
    await ask_for_feedback(message)
    await state.clear()

async def ask_for_feedback(message: Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="👍 Нравится"), KeyboardButton(text="👎 Не нравится")]
    ])
    await message.answer("Тебе понравился расклад?", reply_markup=keyboard)

@dp.message(F.text == "👍 Нравится")
async def like(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🔮 Получить Подробный расклад")],
        [KeyboardButton(text="⬅️ Оставить всё как есть")]
    ])
    await message.answer("Похоже, карты Таро заговорили с тобой! 🔮✨ "
                         "Их послание откликнулось тебе, но это лишь часть истории. "
                         "Хочешь раскрыть ещё больше деталей и получить личный совет? "
                         "Получи Подробный расклад, где каждая карта расскажет больше! 🃏🔥", reply_markup=markup)

@dp.message(F.text == "👎 Не нравится")
async def dislike(message: Message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="🔮 Получить Подробный расклад")],
        [KeyboardButton(text="⬅️ Оставить всё как есть")]
    ])
    await message.answer("Не совсем то, что ты ожидал? "
                         "🤔 Возможно, тебе нужно более точное послание. "
                         "Подробный расклад с дополнительными картами и личным советом поможет глубже "
                         "разобраться в ситуации и увидеть скрытые возможности! 🔮✨", reply_markup=markup)

@dp.message(F.text == "🔮 Получить Подробный расклад")
async def show_payment_options(message: Message):
    await message.answer("Выберите вариант:", reply_markup=get_purchase_keyboard())

@dp.message(F.text == "⬅️ Оставить всё как есть")
async def back_to_start(message: Message):
    await send_welcome(message)

def get_purchase_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 PRO (Расширенный расклад) – 99₽", callback_data="buy_1")],
        [InlineKeyboardButton(text="💎 MASTER (Глубокий анализ) – 199₽", callback_data="buy_2")],
        [InlineKeyboardButton(text="👑 ULTIMATE (Таро-коучинг) – 399₽", callback_data="buy_3")],
    ])

@dp.callback_query(F.data.startswith("buy_"))
async def process_callback_query(callback_query: types.CallbackQuery):
    action = callback_query.data.split("_")[1]
    prices = []
    description = ''
    if action == "1":
        description = '🔥 PRO – 99₽'
        prices = [LabeledPrice(label="Расклад из 3 карт (Прошлое – Настоящее – Будущее). Связь между картами, совет на основе энергетики расклада. Подходит для быстрого, но атмосферного ответа на вопрос.", amount=99 * 100)]
    elif action == "2":
        description = '💎 MASTER – 199₽'
        prices = [LabeledPrice(label="5 карт (Прошлое – Настоящее – Будущее – Скрытые факторы – Совет). Глубокий анализ ситуации, раскрытие скрытых аспектов, логичная связь событий. Завершается пророческим напутствием. Для тех, кто хочет больше деталей и понимания.", amount=199 * 100)]
    elif action == "3":
        description = '👑 ULTIMATE – 399₽'
        prices = [LabeledPrice(label="7 карт (Твой путь – Влияние прошлого – Ситуация сейчас – Скрытые факторы – Препятствия – Потенциал – Итог). Полноценная история судьбы с философским смыслом, архетипами и жизненными циклами. Завершается мощным инсайтом. Для глубокого погружения и трансформационного опыта.", amount=399 * 100)]

    await bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title=description,
        description=description,
        payload=f'sub{action}',
        provider_token=PROVIDER_TOKEN,
        currency=CURRENCY,
        start_parameter='test',
        prices=prices
    )

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def progress_successful_payment(message: Message, state: FSMContext):
    await message.answer("💫Оплата прошла успешно!", reply_markup=ReplyKeyboardRemove())
    await message.answer("✨ Настройся на свой вопрос ✨ \n"
                         "Сделай глубокий вдох и подумай, что именно тебя беспокоит. 🔮  \n"
                         "Теперь напиши свой вопрос сюда. Я помогу тебе раскрыть тайны карт Таро! 🌙✨", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PostPaymentState.waiting_for_post_payment_input)

@dp.message(PostPaymentState.waiting_for_post_payment_input)
async def handle_post_payment_question(message: Message, state: FSMContext):
    question = message.text
    cards = draw_tarot_cards()
    interpretation =  get_tarot_interpretation_llama(question, cards)
    await message.answer(
        f"✨ Глубинный расклад:\n1️⃣ {cards[0]}\n2️⃣ {cards[1]}\n3️⃣ {cards[2]}\n\n🔮 Трактовка:\n{interpretation}"
    )
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Да, все супер!"), KeyboardButton(text="Нет, мне не понравилось.")]
    ])
    await message.answer(
        "Тебе понравился расклад?", reply_markup=keyboard
    )

    await state.clear()

@dp.message(F.text == "Да, все супер!")
async def likepos(message: Message):
    await message.answer("🌟Спасибо, что доверился картам! \n"
                         "Если у тебя остались вопросы или хочется глубже разобраться в ситуации, колода всегда готова помочь. \n"
                         "Задай новый вопрос, и карты продолжат вести тебя по пути ясности и мудрости. ✨ \n"
                         "Твоя судьба — это книга, и я лишь помогаю прочесть её страницы...🔮")
    await send_welcome(message)

@dp.message(F.text == "Нет, мне не понравилось.")
async def dislikepos(message: Message):
    await message.answer("🌟Спасибо за твоё доверие! \n"
                         "Карты иногда говорят загадками, и их послания могут быть не сразу понятны. Если хочешь, задай новый вопрос или уточни текущий — я постараюсь раскрыть ситуацию глубже и яснее🔮 \n"
                         "Твоё удовлетворение для меня важно! ✨ \n"
                         "Иногда нужно время, чтобы услышать шёпот судьбы...")
    await send_welcome(message)


@dp.message()
async def echo_handler(message: Message):
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer('Не удалось обработать сообщение.')

# --- Запуск без asyncio.run() ---
def run_bot():
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling(bot))
    loop.run_forever()

if __name__ == "__main__":
    run_bot()

#lol
