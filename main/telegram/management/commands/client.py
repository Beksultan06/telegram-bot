from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.input_file import FSInputFile
from asgiref.sync import sync_to_async
from car.models import CarBrand, CarModel
from product.models import Product, ProductImage
from django.db.models import OuterRef, Subquery
import os
from django.conf import settings

router = Router()

@sync_to_async
def get_all_car_brands():
    return list(CarBrand.objects.values('id', 'title'))

@sync_to_async
def get_car_models_by_brand(brand_id):
    return list(CarModel.objects.filter(brand_id=brand_id).values('id', 'title'))

@sync_to_async
def get_products_by_model(model_id):
    # Получаем основное изображение каждого продукта
    main_image_subquery = ProductImage.objects.filter(
        product=OuterRef('pk'), is_main=True
    ).values('image')[:1]

    # Формируем данные о продуктах с их основным изображением
    return list(Product.objects.filter(car_model_id=model_id).annotate(
        main_image=Subquery(main_image_subquery)
    ).values(
        'title', 'description', 'price', 'car_brand__title', 'car_model__title', 'main_image'
    ))

@router.message(Command(commands=["start"]))
async def start(message: types.Message):
    brands = await get_all_car_brands()
    if brands:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=brand['title'], callback_data=f"brand_{brand['id']}")]
            for brand in brands
        ])
        await message.answer(
            "Привет! Я бот, в котором вы можете купить машину.\nВыберите бренд:",
            reply_markup=keyboard
        )
    else:
        await message.answer("К сожалению, нет доступных брендов.")

@router.callback_query(F.data.startswith("brand_"))
async def select_brand(callback_query: types.CallbackQuery):
    brand_id = int(callback_query.data.split("_")[1])
    models = await get_car_models_by_brand(brand_id)
    if models:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=model['title'], callback_data=f"model_{model['id']}")]
            for model in models
        ])
        await callback_query.message.answer("Выберите модель:", reply_markup=keyboard)
    else:
        await callback_query.message.answer("К сожалению, нет доступных моделей для этого бренда.")

@router.callback_query(F.data.startswith("model_"))
async def select_model(callback_query: types.CallbackQuery):
    model_id = int(callback_query.data.split("_")[1])
    try:
        products = await get_products_by_model(model_id)
        print(f"Полученные товары для модели {model_id}: {products}")

        if products:
            for product in products:
                image_path = os.path.join(settings.MEDIA_ROOT, product['main_image'])
                print(f"Путь к изображению: {image_path}")

                message_text = (
                    f"Бренд: {product['car_brand__title']}\n"
                    f"Модель: {product['car_model__title']}\n"
                    f"Товар: {product['title']}\n"
                    f"Описание: {product['description']}\n"
                    f"Цена: {product['price']} руб.\n"
                )
                print(f"Текст сообщения: {message_text}")

                try:
                    if os.path.exists(image_path):
                        photo = FSInputFile(image_path)
                        await callback_query.message.answer_photo(photo=photo, caption=message_text)
                    else:
                        print(f"Файл не найден: {image_path}")
                        await callback_query.message.answer(message_text)
                except Exception as e:
                    print(f"Ошибка при отправке сообщения: {e}")
                    await callback_query.message.answer(message_text)
        else:
            await callback_query.message.answer("К сожалению, нет доступных товаров для этой модели.")
    except Exception as e:
        print(f"Ошибка при обработке модели {model_id}: {e}")
        await callback_query.message.answer("Произошла ошибка при обработке вашей заявки. Попробуйте позже.")
