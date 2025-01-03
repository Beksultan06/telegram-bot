from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from product.models import Product
from asgiref.sync import sync_to_async

inline_type_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Бизнес", callback_data="bussines")],
    [InlineKeyboardButton(text='Клиент', callback_data='cklient')]
])

@sync_to_async
def get_car_models():
    return list(Product.objects.select_related('car_model').values('car_model__title').distinct())

@sync_to_async
def get_car_brands():
    return list(Product.objects.select_related('car_brand').values('car_brand__title').distinct())

@sync_to_async
def get_product_by_model(model_id):
    return Product.objects.get(car_model_id=model_id)

@sync_to_async
def get_product_by_brand(brand_id):
    return Product.objects.get(car_brand_id=brand_id)

async def generate_car_buttons(choice_type="model"):
    keyboard = InlineKeyboardMarkup(row_width=1, inline_keyboard=[])

    if choice_type == "model":
        # Получаем уникальные модели автомобилей асинхронно
        car_models = await get_car_models()

        if car_models:
            for product in car_models:
                model_name = product['car_model__title']
                keyboard.inline_keyboard.append([InlineKeyboardButton(text=model_name, callback_data=f"model_{model_name}")])
        else:
            keyboard.inline_keyboard.append([InlineKeyboardButton(text="Нет категорий моделей", callback_data="no_models")])

    elif choice_type == "brand":
        # Получаем уникальные бренды автомобилей асинхронно
        car_brands = await get_car_brands()

        if car_brands:
            for product in car_brands:
                brand_name = product['car_brand__title']
                keyboard.inline_keyboard.append([InlineKeyboardButton(text=brand_name, callback_data=f"brand_{brand_name}")])
        else:
            keyboard.inline_keyboard.append([InlineKeyboardButton(text="Нет категорий марок", callback_data="no_brands")])

    return keyboard