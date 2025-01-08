from django.urls import path
from .views import HomeView, RoomView, join_room, create_room

urlpatterns = [
    path("", HomeView , name="login"),
    path('user/', join_room, name = 'user'),
    path('create-room/', create_room, name='admin'),
    path("<str:room_name>/<str:username>/", RoomView, name= "room"),
]

