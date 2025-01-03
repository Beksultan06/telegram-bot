from django.urls import path, include

from business import views

urlpatterns = [
    path('categories/', views.ServiceCategoryListView.as_view(), name='service_categories'),
    path('categories/<int:category_id>/sub_categories/', views.ServiceSubCategoryListView.as_view(),
         name='service_categories'),
    path('categories/<int:category_id>/sub_categories/api/v2/', views.Api2ServiceSubCategoryListView.as_view(),
         name='v2_service_categories'),
    path('add_service_view/', views.ServiceViewLogCreate.as_view(), name='add_service_view'),
    path('add_service_view/api/v2/', views.Api2ServiceViewLogCreate.as_view(), name='add_service_view_v2'),
    path('api/v2/', views.Api2ServiceListView.as_view(), name='v2_service_list'),
    path('', views.ServiceListView.as_view(), name='service_list'),
]
