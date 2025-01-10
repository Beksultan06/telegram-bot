from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async
from telegram.management.commands.app.db import create_product, create_product_image, get_car_brand_title, get_car_model_title
from car.models import CarBrand, CarModel
from telegram.management.commands.app.button import generate_car_buttons, get_car_models_by_brand, inline_type_users
import os

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
async def handle_brand(callback_query: types.CallbackQuery, state: FSMContext):
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
            await state.update_data(car_brand_id=brand_id)
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
        await state.update_data(car_model_id=model_id)
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

async def create_product_with_images(price, description, car_model, car_brand, photos, bot):
    directory = 'product_images'
    if not os.path.exists(directory):
        os.makedirs(directory)
    product = await create_product(price, description, car_model, car_brand)
    for i, file_id in enumerate(photos):
        file = await bot.get_file(file_id)
        file_path = f"{directory}/{file.file_unique_id}.jpg"
        await bot.download(file, file_path)

        is_main_image = i == 0
        await create_product_image(product, file_path, is_main_image)
    return product

@router.message(CarForm.waiting_for_price)
async def get_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение цены.")
        return
    data = await state.get_data()
    photos = data.get("photos", [])
    description = data.get("description")
    car_model_id = data.get("car_model_id")
    car_brand_id = data.get("car_brand_id")
    if not (photos and description and car_model_id and car_brand_id):
        await message.answer("Недостаточно данных для создания товара. Пожалуйста, убедитесь, что все поля заполнены.")
        return
    try:
        car_model = await sync_to_async(CarModel.objects.get)(id=car_model_id)
    except ObjectDoesNotExist:
        await message.answer("Ошибка: модель автомобиля не найдена.")
        return
    try:
        car_brand = await sync_to_async(CarBrand.objects.get)(id=car_brand_id)
    except ObjectDoesNotExist:
        await message.answer("Ошибка: марка автомобиля не найдена.")
        return
    product = await create_product_with_images(price, description, car_model, car_brand, photos, message.bot)
    await message.answer(f"Товар успешно добавлен: {product.title}. Описание: {description}. Цена: {price} USD.")
    await state.clear()

@router.callback_query(lambda callback: callback.data == "no_models")
async def handle_no_models(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("К сожалению, нет доступных моделей.")

@router.callback_query(lambda callback: callback.data == "no_brands")
async def handle_no_brands(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("К сожалению, нет доступных марок.")