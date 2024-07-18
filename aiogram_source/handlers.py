from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram_source import keyboards
from config import available_region, browsers
import selenium_scraping
import save_csv

busy = False
router = Router()
link3 = {}


class ChoiceRegion(StatesGroup):
    choosing_things = State()
    choosing_price = State()
    choosing_region = State()
    choosing_region_town = State()


@router.message(Command("st"))
async def input_things(message: Message, state: FSMContext):
    await message.answer(text="Що шукаєте ?")
    await state.set_state(ChoiceRegion.choosing_things)


@router.message(ChoiceRegion.choosing_things)
async def choosing_price(message: Message, state: FSMContext):
    await state.update_data(chosen_thing=message.text)
    await message.answer(text="Максимальна ціна?")
    await state.set_state(ChoiceRegion.choosing_price)


@router.message(ChoiceRegion.choosing_price)
async def choosing_things(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(choosing_price=message.text)
        await message.answer(
            "Виберіть область:",
            reply_markup=keyboards.make_multiline_keyboard(available_region, 4),
        )
        await state.set_state(ChoiceRegion.choosing_region)
    else:
        await state.update_data(choosing_price=0)
        await message.answer(text="Помилка. Вкажіть максимальну ціну:")


@router.message(
    ChoiceRegion.choosing_region,
    F.text.in_(list(available_region.keys()))
)
async def region_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_region=message.text)
    await message.answer(
        text="Дякую. Тепер виберіть місто:",
        reply_markup=keyboards.make_row_keyboard(available_region[message.text])
    )
    await state.set_state(ChoiceRegion.choosing_region_town)


@router.message(ChoiceRegion.choosing_region)
async def region_chosen_incorrectly(message: Message):
    await message.answer(text="Не вірно, спробуйте ще", reply_markup=keyboards.make_multiline_keyboard(available_region, 4))


@router.message(ChoiceRegion.choosing_region_town)
async def choosing_things(message: Message, state: FSMContext):
    global busy, link3
    user_data = await state.get_data()
    if message.text in available_region[user_data['chosen_region']]:
        await state.update_data(town=message.text)
        order = await state.get_data()
        driver = selenium_scraping.run_driver(browsers[2])
        await message.answer(text="Почекайте, шукаю усі варіанти...", reply_markup=ReplyKeyboardRemove())
        print(
            f"Шукаю: {order['chosen_thing']} у {order['chosen_region']} місто: {order['town']},"
            f" максимальна ціна: {order['choosing_price']}"
        )
        if not busy:
            busy = True
            cards = selenium_scraping.choice_things(order['chosen_thing'], order['chosen_region'], order['town'])
            n = 0
            for i in range(len(cards)):
                rez, describe_link = selenium_scraping.get_things(i, order['choosing_price'], cards[i])
                link3[f'item_{i}'] = (i, describe_link)

                if (i + 1) % 4 == 0:
                    selenium_scraping.scroll(cards[i])
                if rez:
                    n += 1
                    await message.answer(text=f"id={i}, {rez}")
                    keyboards_items = {"Дивитись на OLX:": {'url': describe_link}, "Отримати контакти": {'callback_data': f"item_{i}"}}

                    await message.answer(
                        'Детальніше',
                        reply_markup=keyboards.make_row_inline_keyboard(keyboards_items)
                    )
            await message.answer(text=f"Пошук завершено. Знайдено {n} із {len(cards)} варіантів")
            driver.quit()

            # save_csv.wright_csv(selenium_scraping.card_to_file)

            busy = False
    else:
        user_data = await state.get_data()
        await message.answer(
            text="Не вірно, спробуйте ще",
            reply_markup=keyboards.make_row_keyboard(available_region[user_data['chosen_region']])
        )


@router.callback_query(F.data.startswith("item_"))
async def send_random_value(callback: CallbackQuery):
    global busy
    if not busy:
        busy = True
        action = callback.data
        driver = selenium_scraping.run_driver(browsers[2])
        phone = selenium_scraping.get_contacts(link3[action][1])
        await callback.message.answer(f"Для id={link3[action][0]} Номер продавця: {phone}")
        busy = False
        driver.quit()
    else:
        await callback.message.answer("Відмова, я ще не закінчив пошук оголошень")

