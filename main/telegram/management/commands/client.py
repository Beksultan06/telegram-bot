from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from car.models import CarBrand, CarModel
from product.models import Product

router = Router()

# Асинхронные функции для работы с базой данных
@sync_to_async
def get_all_car_brands():
    return list(CarBrand.objects.values('id', 'title'))

@sync_to_async
def get_car_models_by_brand(brand_id):
    return list(CarModel.objects.filter(brand_id=brand_id).values('id', 'title'))

@sync_to_async
def get_products_by_model(model_id):
    return list(Product.objects.filter(car_model_id=model_id).values(
        'title', 'description', 'price', 'car_brand__title', 'car_model__title'
    ))

# Обработчик команды /start
@router.message(Command("start"))
async def start(message: types.Message):
    brands = await get_all_car_brands()
    if brands:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=brand['title'], callback_data=f"brand_{brand['id']}")
            ] for brand in brands
        ])
        await message.answer("Привет! Я бот, в котором вы можете купить машину.\nВыберите бренд:", reply_markup=keyboard)
    else:
        await message.answer("К сожалению, нет доступных брендов.")

# Обработчик выбора бренда
@router.callback_query(lambda c: c.data.startswith("brand_"))
async def select_brand(callback_query: types.CallbackQuery):
    brand_id = int(callback_query.data.split("_")[1])
    models = await get_car_models_by_brand(brand_id)
    if models:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=model['title'], callback_data=f"model_{model['id']}")
            ] for model in models
        ])
        await callback_query.message.answer("Выберите модель:", reply_markup=keyboard)
    else:
        await callback_query.message.answer("К сожалению, нет доступных моделей для этого бренда.")

# Обработчик выбора модели
@router.callback_query(lambda c: c.data.startswith("model_"))
async def select_model(callback_query: types.CallbackQuery):
    model_id = int(callback_query.data.split("_")[1])
    try:
        products = await get_products_by_model(model_id)

        print(f"Полученные товары для модели {model_id}: {products}")  # Логирование товаров

        if products:
            for product in products:
                # Формируем текст сообщения
                message_text = (
                    f"Товар: {product['title']}\n"
                    f"Описание: {product['description']}\n"
                    f"Цена: {product['price']} руб.\n"
                    f"Бренд: {product['car_brand__title']}\n"
                    f"Модель: {product['car_model__title']}\n"
                )

                print(f"Текст сообщения: {message_text}")  # Логирование текста сообщения

                try:
                    await callback_query.message.answer(message_text)
                except Exception as e:
                    print(f"Ошибка при отправке сообщения: {e}\nСообщение: {message_text}")

        else:
            await callback_query.message.answer("К сожалению, нет доступных товаров для этой модели.")

    except Exception as e:
        print(f"Ошибка при обработке модели {model_id}: {e}")
