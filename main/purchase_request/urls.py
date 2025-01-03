from django.urls import path, include

from purchase_request import views, business_views

business_patterns = [
    path('all_requests/', business_views.PurchaseRequestForBusinessListView.as_view(), name='business_requests'),
    path('all_requests/api/v2/', business_views.Api2PurchaseRequestForBusinessListView.as_view(),
         name='v2_business_requests'),
    path('car_models/api/v2/', business_views.Api2BusinessCarModelListView.as_view(),
         name='v2_business_car_brans_car_models'),
    path('accepted_requests/', business_views.AcceptedPurchaseRequestForBusinessListView.as_view(),
         name='accepted_requests'),
    path('accepted_requests/delete_all/', business_views.DeleteAllAcceptedPurchaseRequestForBusinessView.as_view(),
         name='delete_all_accepted_requests'),
    path('request/is_viewed/', business_views.Api2PurchaseRequestIsViewedView.as_view(), name='request_is_viewed'),
    path('request/detail/<int:pk>/', business_views.Api2PurchaseRequestForBusinessDetailView.as_view(),
         name='request_detail'),
    path('offer/create/', business_views.OfferCreateView.as_view(), name='offer_create'),

    path('offer/<int:pk>/', business_views.OfferDetailView.as_view(), name='offer_detail'),
    path('offer/differences/', business_views.OfferDifferenceListView.as_view(), name='offer_differences'),
    path('offer/availabilities/', business_views.OfferAvailabilityListView.as_view(), name='offer_availabilities'),
    path('offer/conditions/', business_views.OfferConditionsListView.as_view(), name='offer_conditions'),
]

user_patterns = [
    path('request_types/', views.PurchaseRequestTypeListView.as_view(), name='purchase_request_types'),
    path('create/', views.PurchaseRequestCreateView.as_view(), name='purchase_request_create'),
    path('create/vip/', views.VipPurchaseRequestCreateView.as_view(), name='vip_purchase_request_create'),
    path('my_requests/', views.PurchaseRequestListView.as_view(), name='my_purchase_requests'),
    path('my_requests/<int:pk>/', views.PurchaseRequestDetailView.as_view(), name='my_purchase_request_detail'),
    path('my_requests/<int:pk>/update/', views.PurchaseRequestUpdateView.as_view(), name='my_purchase_request_update'),
    path('my_requests/off/<int:pk>/', views.PurchaseRequestOffView.as_view(), name='my_purchase_request_off'),
    path('my_requests/off_all/', views.PurchaseRequestAllOffView.as_view(), name='my_purchase_request_off_all'),
    path('accepted_offers/', views.AcceptedOffersListView.as_view(), name='accepted_offers'),
    path('accepted_offers/delete_all/', views.AcceptedOffersDeleteAllView.as_view(), name='accepted_offers_delete_all'),
    path('accepted_offers/<int:pk>/delete/', views.AcceptedOffersDeleteView.as_view(), name='accepted_offers_delete'),
]

urlpatterns = [
    path('user/', include(user_patterns)),
    path('business/', include(business_patterns)),
]
