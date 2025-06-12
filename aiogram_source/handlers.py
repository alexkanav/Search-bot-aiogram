from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram_source import keyboards
import asyncio

from selenium_scraping import run_driver, get_contacts, choice_things, get_things, scroll
from config import available_region, BROWSERS
import save_csv

router = Router()


class Choice(StatesGroup):
    choosing_things = State()
    choosing_price = State()
    choosing_region = State()
    choosing_region_town = State()
    quit_search = State()
    busy_flag  = False
    scraped_links  = {}


@router.message(Command("start"))
async def start_command(message: Message, state: FSMContext):
    await message.answer(text="Що шукаєте ?")
    await state.set_state(Choice.choosing_things)


@router.message(Command("stop"))
async def stop_command(message: Message, state: FSMContext):
    await message.answer(text="Пошук завершено")
    await state.clear()


@router.message(Choice.choosing_things)
async def choosing_price(message: Message, state: FSMContext):
    await state.update_data(chosen_thing=message.text)
    await message.answer(text="Максимальна ціна?")
    await state.set_state(Choice.choosing_price)


@router.message(Choice.choosing_price)
async def choosing_things(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(choosing_price=message.text)
        await message.answer(
            "Виберіть область:",
            reply_markup=keyboards.make_multiline_keyboard(available_region, 4),
        )
        await state.set_state(Choice.choosing_region)
    else:
        await state.update_data(choosing_price=0)
        await message.answer(text="Помилка. Вкажіть максимальну ціну:")


@router.message(Choice.choosing_region, F.text.in_(list(available_region.keys())))
async def region_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_region=message.text)
    await message.answer(
        text="Дякую. Тепер виберіть місто:",
        reply_markup=keyboards.make_row_keyboard(available_region[message.text])
    )
    await state.set_state(Choice.choosing_region_town)


@router.message(Choice.choosing_region)
async def region_chosen_incorrectly(message: Message):
    await message.answer(text="Не вірно, спробуйте ще",
                         reply_markup=keyboards.make_multiline_keyboard(available_region, 4))


@router.message(Choice.choosing_region_town)
async def choosing_things(message: Message, state: FSMContext):
    user_data = await state.get_data()
    if message.text in available_region[user_data['chosen_region']]:
        await state.update_data(town=message.text)
        order = await state.get_data()

        await message.answer(text="Почекайте, шукаю усі варіанти...", reply_markup=ReplyKeyboardRemove())
        print(
            f"Шукаю: {order['chosen_thing']} у {order['chosen_region']} місто: {order['town']},"
            f" максимальна ціна: {order['choosing_price']}"
        )

        n1, n2 = await searching(message, order['chosen_thing'], order['chosen_region'], order['town'],
                                 order['choosing_price'])
        await message.answer(text=f"Пошук завершено. Знайдено {n1} із {n2} варіантів")

        await message.answer(
            text='Що бажаєте? Завершити пошук, або шукати нові об\'яви кожну годину',
            reply_markup=keyboards.make_row_keyboard(['Завершити', 'Шукати далі'])
        )
        await state.set_state(Choice.quit_search)

        # save_csv.wright_csv(selenium_scraping.card_to_file)

    else:
        user_data = await state.get_data()
        await message.answer(
            text="Не вірно, спробуйте ще",
            reply_markup=keyboards.make_row_keyboard(available_region[user_data['chosen_region']])
        )


@router.callback_query(F.data.startswith("item_"))
async def send_random_value(callback: CallbackQuery):
    if not Choice.busy_flag :
        Choice.busy_flag  = True
        action = callback.data
        driver = run_driver(BROWSERS)
        phone = get_contacts(Choice.scraped_links [action][1], driver)
        await callback.message.answer(f"Для id={Choice.scraped_links [action][0]} Номер продавця: {phone}")
        driver.quit()
        Choice.busy_flag  = False
    else:
        await callback.message.answer("Відмова, я ще не закінчив пошук")


@router.message(Choice.quit_search)
async def continue_searching(message: Message, state: FSMContext):
    while True:
        if message.text == 'Завершити':
            await state.clear()
            await message.answer(text="Звертайтесь ще, в мене немає вихідних)", reply_markup=ReplyKeyboardRemove())


        elif message.text == 'Шукати далі':
            await message.answer("Чекаю нові об'яви...")
            user_data = await state.get_data()
            await asyncio.sleep(1800)
            await searching(message, user_data['chosen_thing'], user_data['chosen_region'], user_data['town'],
                            user_data['choosing_price'])


async def searching(message: Message, chosen_thing: str, chosen_region: str, town, price: str):
    if not Choice.busy_flag :
        Choice.busy_flag  = True
        cards = ''
        n = 0
        driver = run_driver(BROWSERS)
        try:
            cards = choice_things(driver, chosen_thing, chosen_region, town)

            for i in range(len(cards)):
                card_id, res3, describe_link = get_things(i, price, cards[i])
                Choice.scraped_links [f'item_{card_id}'] = (card_id, describe_link)

                if (i + 1) % 4 == 0:
                    scroll(driver, cards[i])
                if res3:
                    n += 1
                    await message.answer(
                        text=f"id={card_id}, {res3}",
                        reply_markup=keyboards.make_row_inline_keyboard([
                            {"Дивитись на OLX:": {'url': describe_link}},
                            {"Отримати контакти": {'callback_data': f"item_{card_id}"}}
                        ])

                    )

        finally:
            driver.quit()

        Choice.busy_flag  = False
        return n, len(cards)

    else:
        await message.answer(text="Відмова, я ще не закінчив пошук")
        return None, None
