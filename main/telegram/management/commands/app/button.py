from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from product.models import Product
from asgiref.sync import sync_to_async
from aiogram import types

inline_type_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Бизнес", callback_data="bussines")],
    [InlineKeyboardButton(text='Клиент', callback_data='cklient')]
])

@sync_to_async
def get_product_by_model_async(model_id):
    return list(Product.objects.filter(car_model_id=model_id))

@sync_to_async
def get_product_by_brand_async(brand_id):
    return Product.objects.filter(car_brand_id=brand_id).first()

@sync_to_async
def get_car_models():
    return list(Product.objects.values('car_model', 'car_model__title').distinct())

@sync_to_async
def get_car_brands():
    return list(Product.objects.values('car_brand', 'car_brand__title').distinct())

async def generate_car_buttons(choice_type="model"):
    keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=[])
    if choice_type == "model":
        car_models = await get_car_models()
        if car_models:
            for product in car_models:
                model_name = product.get('car_model__title', 'Unknown Model')
                model_id = product.get('car_model', None)

                if model_id:
                    keyboard.inline_keyboard.append([types.InlineKeyboardButton(text=model_name, callback_data=f"model_{model_id}")])
                else:
                    print(f"Model ID not found for product: {product}")
        else:
            keyboard.inline_keyboard.append([types.InlineKeyboardButton(text="Нет категорий моделей", callback_data="no_models")])
    elif choice_type == "brand":
        car_brands = await get_car_brands()

        if car_brands:
            for product in car_brands:
                brand_name = product.get('car_brand__title', 'Unknown Brand')
                brand_id = product.get('car_brand', None)

                if brand_id:
                    keyboard.inline_keyboard.append([types.InlineKeyboardButton(text=brand_name, callback_data=f"brand_{brand_id}")])
                else:
                    print(f"Brand ID not found for product: {product}")
        else:
            keyboard.inline_keyboard.append([types.InlineKeyboardButton(text="Нет категорий марок", callback_data="no_brands")])

    return keyboard
