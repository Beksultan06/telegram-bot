from django.urls import path, include

from business import views
from business.views import ServiceViewLogsByCategory

urlpatterns = [
    path('tariffs/', views.TariffListView.as_view(), name='tariff_list'),
    path('create/', views.BusinessCreateView.as_view(), name='business_create'),
    path('create/api/2/', views.Api2BusinessCreateView.as_view(), name='business_create_api'),
    path('profile/', views.BusinessDetailView.as_view(), name='business_update'),
    path('profile/activate/', views.BusinessActivateView.as_view(), name='business_activate'),
    path('profile/deactivate/', views.BusinessDeactivateView.as_view(), name='business_deactivate'),
    path('my_services/', views.BusinessServiceListCreateView.as_view(), name='my_services'),
    path('my_services/<int:pk>/', views.BusinessServiceDetailView.as_view()),
    path('change_tariff/', views.ChangeTariffView.as_view()),
    path('update_car_brands/', views.BusinessCarBrandsUpdateView.as_view(), name='update_car_brands'),
    path('my_car_brands/', views.MyCarBrandsListView.as_view(), name='my_business_car_brands'),
    path('car_brands/', views.BusinessCarBrandsListView.as_view(), name='business_car_brands'),
    path('update_common_parts/', views.BusinessCommonPartsUpdateView.as_view(), name='update_common_parts'),
    path('common_parts/', views.BusinessCommonPartsListView.as_view(), name='common_parts'),
    path('purchase_request_types/', views.BusinessPurchaseRequestTypesView.as_view(), name='purchase_request_types'),
    path('add_balance/', views.PayboxOrderCreateView.as_view(), name='add_balance'),
    path('paybox_result/', views.PayboxTransactionResultView.as_view(), name='paybox_result'),
    path('statics_by_car_brand/', views.StaticsCarBrandView.as_view(), name='statics_by_car_brand'),
    path('statics_by_services/', views.StaticsServiceView.as_view(), name='statics_by_services'),
    path('service-view-logs-by-category/', ServiceViewLogsByCategory.as_view(), name='service-view-logs-by-category'),
]
