from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.management.commands.app.db import get_all_car_brands, get_car_models_by_brand

inline_type_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Бизнес", callback_data="bussines")],
    [InlineKeyboardButton(text='Клиент', callback_data='cklient')]
])

async def generate_car_buttons(choice_type="brand", brand_id=None):
    keyboard = InlineKeyboardMarkup(row_width=1, inline_keyboard=[])
    if choice_type == "brand":
        car_brands = await get_all_car_brands()
        if car_brands:
            for brand in car_brands:
                keyboard.inline_keyboard.append(
                    [InlineKeyboardButton(text=brand['title'], callback_data=f"brand_{brand['id']}")]
                )
        else:
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton(text="Нет доступных марок", callback_data="no_brands")]
            )
    elif choice_type == "model" and brand_id:
        car_models = await get_car_models_by_brand(brand_id)
        if car_models:
            for model in car_models:
                keyboard.inline_keyboard.append(
                    [InlineKeyboardButton(text=model['title'], callback_data=f"model_{model['id']}")]
                )
        else:
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton(text="Нет доступных моделей", callback_data="no_models")]
            )
    return keyboard