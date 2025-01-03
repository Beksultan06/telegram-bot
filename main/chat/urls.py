from django.urls import path

from chat import views

urlpatterns = [
    path('<int:chat_room>/', views.MessageCreateListView.as_view(), name='message_view'),
]

