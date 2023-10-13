from django.urls import path
from . import views

urlpatterns=[
    
    #resiter and login
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name="logout"),
    path('register/', views.registerPage, name="register"),
    


    #home and room
    path('',views.home, name="HOME"),
    path('room/<str:pk>/',views.room, name="room"),
    path('profile/<str:pk>',views.userProfile,name='user-profile'),
    #CURD
    path('create-room/',views.createRoom, name="create-room"),
    path('update-room/<str:pk>',views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>',views.deleteRoom,name='delete-room'),
    # path('topic/<str')


    path('delete-message/<str:pk>',views.deleteMessage,name='delete-message'),


    path('update-user/',views.updateUser,name='update-user'),

    # mobile
    path('topics/',views.topicPage,name='topics'),
    path('activity/',views.activityPage,name='activity'),
]