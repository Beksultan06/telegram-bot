from aiogram import types, Router
from aiogram.filters import Command
from product.models import Product
from telegram.management.commands.app.button import generate_car_buttons, get_product_by_brand, get_product_by_model, inline_type_users

router = Router()

@router.message(Command("start"))
async def start(message:types.Message):
    await message.answer("Привет я телеграмм бот!", reply_markup=inline_type_users)

@router.callback_query(lambda callback: callback.data == "bussines")
async def handle_user_type(callback_query: types.CallbackQuery):
    user_type = callback_query.data
    await callback_query.message.edit_text("Вы выбрали тип: Бизнес. Теперь выберите модель автомобиля.")
        # Получаем результат от асинхронной функции
    keyboard = await generate_car_buttons(choice_type="model")

    # Теперь передаем результат в метод answer
    await callback_query.message.answer("Выберите модель автомобиля:", reply_markup=keyboard)


@router.callback_query(lambda callback: callback.data.startswith("model_"))
async def handle_model(callback_query: types.CallbackQuery):
    model_id = callback_query.data.split("_")[1]
    model = await get_product_by_model(model_id)  # асинхронный запрос
    await callback_query.message.edit_text(f"Вы выбрали модель: {model.car_model}. Теперь выберите марку автомобиля.")
    keyboard = await generate_car_buttons("brand")
    await callback_query.message.answer("Выберите марку автомобиля:", reply_markup=keyboard)


@router.callback_query(lambda callback: callback.data.startswith("brand_"))
async def handle_brand(callback_query: types.CallbackQuery):
    brand_id = callback_query.data.split("_")[1]
    brand = await get_product_by_brand(brand_id)  # асинхронный запрос
    await callback_query.message.edit_text(f"Вы выбрали марку: {brand.car_brand}.")


@router.callback_query(lambda callback: callback.data == "no_models")
async def handle_no_models(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("К сожалению, нет доступных моделей.")

@router.callback_query(lambda callback: callback.data == "no_brands")
async def handle_no_brands(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("К сожалению, нет доступных марок.")

