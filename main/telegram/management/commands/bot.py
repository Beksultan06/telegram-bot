from aiogram import types, Router
from aiogram.filters import Command
from product.models import Product
from telegram.management.commands.app.button import generate_car_buttons, get_product_by_brand_async, get_product_by_model_async, inline_type_users
from asgiref.sync import sync_to_async

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет, я телеграмм бот!", reply_markup=inline_type_users)

@router.callback_query(lambda callback: callback.data == "bussines")
async def handle_user_type(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Вы выбрали тип: Бизнес. Теперь выберите модель автомобиля.")
    keyboard = await generate_car_buttons(choice_type="model")
    await callback_query.message.answer("Выберите модель автомобиля:", reply_markup=keyboard)

@router.callback_query(lambda callback: callback.data.startswith("model_"))
async def handle_model(callback_query: types.CallbackQuery):
    model_id = callback_query.data.split("_")[1]
    model = await get_product_by_model_async(model_id)
    if isinstance(model, list) and model:
        model = model[0]
    if model:
        car_model_title = await get_car_model_title_async(model)
        await callback_query.message.edit_text(f"Вы выбрали модель: {car_model_title}. Теперь выберите марку автомобиля.")
        keyboard = await generate_car_buttons(choice_type="brand")
        await callback_query.message.answer("Выберите марку автомобиля:", reply_markup=keyboard)
    else:
        await callback_query.message.edit_text("Ошибка: Модель не найдена.")

@sync_to_async
def get_car_model_title_async(model):
    return model.car_model.title if model.car_model else 'Unknown Model'

@router.callback_query(lambda callback: callback.data.startswith("brand_"))
async def handle_brand(callback_query: types.CallbackQuery):
    brand_id = callback_query.data.split("_")[1]
    brand = await get_product_by_brand_async(brand_id)
    if brand:
        await callback_query.message.edit_text(f"Вы выбрали марку: {brand.car_brand}.")
    else:
        await callback_query.message.edit_text("Ошибка: Марка не найдена.")

@router.callback_query(lambda callback: callback.data == "no_models")
async def handle_no_models(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("К сожалению, нет доступных моделей.")

@router.callback_query(lambda callback: callback.data == "no_brands")
async def handle_no_brands(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("К сожалению, нет доступных марок.")
