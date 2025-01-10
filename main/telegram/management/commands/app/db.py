from asgiref.sync import sync_to_async
from product.models import Product, ProductImage
from car.models import CarBrand, CarModel

@sync_to_async
def get_car_brand_title(brand_id):
    brand = CarBrand.objects.filter(id=brand_id).first()
    return brand.title if brand else "Unknown Brand"

@sync_to_async
def get_car_model_title(model_id):
    model = CarModel.objects.filter(id=model_id).first()
    return model.title if model else "Unknown Model"

@sync_to_async
def get_car_models_by_brand(brand_id):
    return list(CarModel.objects.filter(brand_id=brand_id).values('id', 'title'))

@sync_to_async
def get_all_car_brands():
    return list(CarBrand.objects.values('id', 'title'))

@sync_to_async
def create_product(price, description, car_model, car_brand):
    product = Product.objects.create(
        title=f"Товар для {car_brand.title} {car_model.title}",
        description=description,
        price=price,
        car_model=car_model,
        car_brand=car_brand,
        shop_price=price,
    )
    return product

@sync_to_async
def create_product_image(product, file_path, is_main):
    return ProductImage.objects.create(
        product=product,
        image=file_path,
        is_main=is_main
    )