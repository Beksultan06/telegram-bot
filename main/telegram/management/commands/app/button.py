from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async
from car.models import CarBrand, CarModel

inline_type_users = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Бизнес", callback_data="bussines")],
    [InlineKeyboardButton(text='Клиент', callback_data='cklient')]
])


@sync_to_async
def get_car_brand_title(brand_id):
    """Получить название марки по ID."""
    brand = CarBrand.objects.filter(id=brand_id).first()
    return brand.title if brand else "Unknown Brand"

@sync_to_async
def get_car_model_title(model_id):
    """Получить название модели по ID."""
    model = CarModel.objects.filter(id=model_id).first()
    return model.title if model else "Unknown Model"

@sync_to_async
def get_car_models_by_brand(brand_id):
    """Получить модели по ID марки."""
    return list(CarModel.objects.filter(brand_id=brand_id).values('id', 'title'))

@sync_to_async
def get_all_car_brands():
    """Получить все марки машин."""
    return list(CarBrand.objects.values('id', 'title'))

async def generate_car_buttons(choice_type="brand", brand_id=None):
    """
    Генерация кнопок для выбора марок или моделей.
    :param choice_type: Тип данных — 'brand' или 'model'.
    :param brand_id: ID марки (для фильтрации моделей).
    """
    keyboard = InlineKeyboardMarkup(row_width=1, inline_keyboard=[])

    if choice_type == "brand":
        # Получаем все марки
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
        # Получаем модели для выбранной марки
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
