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
def get_products_and_images_by_model(model_id):
    # Получаем товары с основными и дополнительными изображениями
    products = Product.objects.filter(car_model_id=model_id).values(
        'id', 'title', 'description', 'price', 'car_brand__title', 'car_model__title'
    )
    
    # Для каждого товара получаем связанные изображения
    result = []
    for product in products:
        images = list(ProductImage.objects.filter(product_id=product['id']).values_list('image', flat=True))
        result.append({**product, 'images': images})
    
    return result

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
        products = await get_products_and_images_by_model(model_id)
        print(f"Полученные товары для модели {model_id}: {products}")

        if products:
            for product in products:
                # Формируем текст описания товара
                message_text = (
                    f"Бренд: {product['car_brand__title']}\n"
                    f"Модель: {product['car_model__title']}\n"
                    f"Товар: {product['title']}\n"
                    f"Описание: {product['description']}\n"
                    f"Цена: {product['price']} руб.\n"
                )
                print(f"Текст сообщения: {message_text}")
                
                # Проверяем изображения
                if product['images']:
                    main_image_path = os.path.join(settings.MEDIA_ROOT, product['images'][0])
                    print(f"Путь к основному изображению: {main_image_path}")
                    
                    # Отправляем основное изображение с описанием
                    if os.path.exists(main_image_path):
                        try:
                            main_photo = FSInputFile(main_image_path)
                            await callback_query.message.answer_photo(photo=main_photo, caption=message_text)
                        except Exception as e:
                            print(f"Ошибка при отправке основного изображения: {e}")
                            await callback_query.message.answer(message_text)
                    else:
                        print(f"Основное изображение не найдено: {main_image_path}")
                        await callback_query.message.answer(message_text)

                    # Отправляем остальные изображения отдельно
                    for image_path in product['images'][1:]:
                        additional_image_path = os.path.join(settings.MEDIA_ROOT, image_path)
                        print(f"Путь к дополнительному изображению: {additional_image_path}")
                        
                        if os.path.exists(additional_image_path):
                            try:
                                additional_photo = FSInputFile(additional_image_path)
                                await callback_query.message.answer_photo(photo=additional_photo)
                            except Exception as e:
                                print(f"Ошибка при отправке дополнительного изображения: {e}")
                                continue
                        else:
                            print(f"Дополнительное изображение не найдено: {additional_image_path}")
                else:
                    # Если изображения отсутствуют, отправляем только текст
                    await callback_query.message.answer(message_text)
        else:
            await callback_query.message.answer("К сожалению, нет доступных товаров для этой модели.")
    except Exception as e:
        print(f"Ошибка при обработке модели {model_id}: {e}")
        await callback_query.message.answer("Произошла ошибка при обработке вашей заявки. Попробуйте позже.")
