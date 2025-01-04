from aiogram import types, Router
from aiogram.filters import Command
from telegram.management.commands.app.button import generate_car_buttons, get_car_brand_title, get_car_model_title,\
get_car_models_by_brand, inline_type_users

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    """Обработчик команды /start."""
    await message.answer("Привет, я телеграм-бот! Выберите тип пользователя:", reply_markup=inline_type_users)

@router.callback_query(lambda callback: callback.data == "bussines")
async def handle_user_type(callback_query: types.CallbackQuery):
    """Обработчик выбора типа пользователя."""
    await callback_query.message.edit_text("Вы выбрали тип: Бизнес. Теперь выберите марку автомобиля.")
    keyboard = await generate_car_buttons(choice_type="brand")
    await callback_query.message.answer("Выберите марку автомобиля:", reply_markup=keyboard)

@router.callback_query(lambda callback: callback.data.startswith("brand_"))
async def handle_brand(callback_query: types.CallbackQuery):
    """Обработчик выбора марки."""
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
async def handle_model(callback_query: types.CallbackQuery):
    """Обработчик выбора модели."""
    model_id = int(callback_query.data.split("_")[1])
    model_title = await get_car_model_title(model_id)

    if model_title != "Unknown Model":
        await callback_query.message.edit_text(f"Вы выбрали модель: {model_title}.")
    else:
        await callback_query.message.edit_text("Ошибка: Модель не найдена.")


@router.callback_query(lambda callback: callback.data == "no_models")
async def handle_no_models(callback_query: types.CallbackQuery):
    """Обработчик, если нет моделей."""
    await callback_query.message.edit_text("К сожалению, нет доступных моделей.")


@router.callback_query(lambda callback: callback.data == "no_brands")
async def handle_no_brands(callback_query: types.CallbackQuery):
    """Обработчик, если нет марок."""
    await callback_query.message.edit_text("К сожалению, нет доступных марок.")