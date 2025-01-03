from django.urls import path

from car import views


urlpatterns = [
    path('engines/', views.EngineListView.as_view(), name='car_engines'),
    path('transmissions/', views.TransmissionListView.as_view(), name='car_transmissions'),
    path('drives/', views.DrivesListView.as_view(), name='car_drives'),
    path('categories/', views.CarCategoryListView.as_view(), name='car_categories'),
    path('brands/', views.CarBrandListView.as_view(), name='car_brands'),
    path('models/', views.CarModelListView.as_view(), name='car_models'),
    path('bodies/', views.CarBodyListView.as_view(), name='car_bodies'),
    path('my_cars/', views.CarListView.as_view(), name='car_list'),
    path('create/', views.CarCreateView.as_view(), name='car_create'),
    path('<int:pk>/', views.CarDetailView.as_view(), name='car_update'),
    path('<int:car_id>/oil_change/', views.OilChangeListCreateView.as_view(), name='oil_change_list_create'),
    path('<int:car_id>/oil_change/<int:pk>/', views.OilChangeDeleteView.as_view(), name='oil_change_delete'),
    path('<int:car_id>/consumables/', views.ConsumablesListCreateView.as_view(), name='consumables_list_create'),
    path('<int:car_id>/consumables/<int:pk>/', views.ConsumablesDeleteView.as_view(), name='consumables_delete'),

    path('part_category/', views.PartCategoryListView.as_view(), name='part_category_list'),
    path('parts/', views.PartListView.as_view(), name='parts'),
    path('common_parts/', views.CommonPartListView.as_view(), name='common_parts'),
    path('part_manufacturer_countires/', views.PartManufacturerCountryListView.as_view(), name='part_manufacturer_countires'),
]
