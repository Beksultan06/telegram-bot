from aiogram import types, Router
from aiogram.filters import Command
from telegram.management.commands.app.button import generate_car_buttons, get_car_brand_title, get_car_model_title, \
get_car_models_by_brand, inline_type_users
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto

router = Router()

class CarForm(StatesGroup):
    waiting_for_photos = State()
    waiting_for_description = State()
    waiting_for_price = State()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет, я телеграм-бот! Выберите тип пользователя:", reply_markup=inline_type_users)

@router.callback_query(lambda callback: callback.data == "bussines")
async def handle_user_type(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Вы выбрали тип: Бизнес. Теперь выберите марку автомобиля.")
    keyboard = await generate_car_buttons(choice_type="brand")
    await callback_query.message.answer("Выберите марку автомобиля:", reply_markup=keyboard)

@router.callback_query(lambda callback: callback.data.startswith("brand_"))
async def handle_brand(callback_query: types.CallbackQuery):
    brand_id = int(callback_query.data.split("_")[1])
    brand_title = await get_car_brand_title(brand_id)

    if brand_title != "Unknown Brand":
        await callback_query.message.edit_text(f"Вы выбрали марку: {brand_title}. Теперь выберите модель.")
        car_models = await get_car_models_by_brand(brand_id)

        keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[])
        if car_models:
            for model in car_models:
                keyboard.inline_keyboard.append([
                    types.InlineKeyboardButton(text=model['title'], callback_data=f"model_{model['id']}")
                ])
        else:
            keyboard.inline_keyboard.append([
                types.InlineKeyboardButton(text="Нет доступных моделей", callback_data="no_models")
            ])

        await callback_query.message.answer("Выберите модель автомобиля:", reply_markup=keyboard)
    else:
        await callback_query.message.edit_text("Ошибка: Марка не найдена.")

@router.callback_query(lambda callback: callback.data.startswith("model_"))
async def handle_model(callback_query: types.CallbackQuery, state: FSMContext):
    model_id = int(callback_query.data.split("_")[1])
    model_title = await get_car_model_title(model_id)

    if model_title != "Unknown Model":
        await callback_query.message.edit_text(f"Вы выбрали модель: {model_title}. Теперь отправьте фото автомобиля. Вы можете отправить несколько фото по одному. Когда завершите, отправьте команду /done.")
        await state.update_data(photos=[])
        await state.set_state(CarForm.waiting_for_photos)
    else:
        await callback_query.message.edit_text("Ошибка: Модель не найдена.")

@router.message(CarForm.waiting_for_photos, lambda message: message.photo)
async def get_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

    if len(photos) == 1:
        await message.answer("Фото добавлено. Отправьте ещё одно или завершите командой /done.")

@router.message(Command("done"))
async def finish_photo_upload(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    if not photos:
        await message.answer("Вы не добавили ни одного фото.")
    else:
        await message.answer(f"Вы добавили {len(photos)} фото. Продолжим заполнение.")
    await state.update_data(photo_added=False)
    await state.set_state(CarForm.waiting_for_description)

@router.message(CarForm.waiting_for_description)
async def get_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Теперь отправьте цену автомобиля.")
    await state.set_state(CarForm.waiting_for_price)

@router.message(CarForm.waiting_for_price)
async def get_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение цены.")
        return

    await state.update_data(price=price)
    data = await state.get_data()

    photos = data.get("photos", [])
    description = data.get("description")

    if photos:
        media_group = [
            InputMediaPhoto(media=photo) for photo in photos
        ]
        media_group[0].caption = f"Описание: {description}\nЦена: {price} USD"

        await message.answer_media_group(media_group)
    else:
        await message.answer(f"Описание: {description}\nЦена: {price} USD")

    await state.clear()

@router.callback_query(lambda callback: callback.data == "no_models")
async def handle_no_models(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("К сожалению, нет доступных моделей.")

@router.callback_query(lambda callback: callback.data == "no_brands")
async def handle_no_brands(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("К сожалению, нет доступных марок.")