from django.urls import path, include

from info import views
from info.views import AndroidVersionControlAPIView, IOSVersionControlAPIView

urlpatterns = [
    path('promocodes/', views.PromotionalCodesAndDiscountListView.as_view(), name='promocodes'),
    path('promocodes/<int:pk>/', views.PromotionalCodesAndDiscounDetailView.as_view(), name='promocode_detail'),
    path('regions/', views.RegionListView.as_view(), name='regions'),
    path('banners/', views.BannerListView.as_view(), name='banners'),
    path('banners/<int:pk>/', views.BannerDetailView.as_view(), name='banner_detail'),
    path('support_and_faq/', views.SupportFAQView.as_view(), name='support_and_faq'),
    path('about_app/', views.AboutAppView.as_view(), name='about_app'),
    path('ad_page/', views.AdPageView.as_view(), name='ad_page'),

    # Контроль версии через админку
    path('android/', AndroidVersionControlAPIView.as_view()),
    path('ios/', IOSVersionControlAPIView.as_view()),

]
