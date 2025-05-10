import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, PreCheckoutQuery

TELEGRAM_TOKEN = "7675944363:AAHj62NAb8PCYj2i2JGLuP2m5gYlmwysAcs"


PROVIDER_TOKEN = "381764678:TEST:116332"
CURRENCY = "RUB"
dp = Dispatcher()

def get_purchase_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Купить 1 раз", callback_data="buy_1")],
        [InlineKeyboardButton(text="Купить 2 раза", callback_data="buy_2")]
    ])


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Время покупочек!", reply_markup=get_purchase_keyboard())


@dp.callback_query()
async def process_callback_query(callback_query: types.CallbackQuery, bot: Bot) -> None:
    action = callback_query.data.split("_")[1]
    prices = []
    description = ''
    if action == "1":
        description = 'Купить 1 раз'
        prices = [LabeledPrice(label="Оплата заказа №1", amount=100 * 100)] # подставить свои значения цены
    elif action == "2":
        description = 'Купить 2 раза'
        prices = [LabeledPrice(label="Оплата заказа №2", amount=200 * 100)] # подставить свои значения цены

    if prices:
        await bot.send_invoice(
            chat_id=callback_query.from_user.id,
            title=f'Покупка {action}',
            description=description,
            payload=f'sub{action}',
            provider_token=PROVIDER_TOKEN,
            currency=CURRENCY,
            start_parameter='test',
            prices=prices
        )

@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot) -> None:
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    # поменять подписки
@dp.message(F.successful_payment)
async def progress_successful_payment(message: Message) -> None:
    playload_to_message = {
        'sub1': 'Подписка 1',
        'sub2': 'Подписка 2',
    }
    response_message = playload_to_message.get(message.successful_payment.invoice_payload, 'Оплата успешна!')
    await message.answer(response_message)


@dp.message()
async  def echo_handler(message: Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer('Nice try!')


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    asyncio.run(main())





