
from apps import views
from django.urls import path
from knox import views as knox_views
from .views import *
urlpatterns=[
    #Authentication
   path('register/', RegisterAPI.as_view(), name='register'),
   path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),


    #Crud Operation


    path('create/', views.create_items, name='create-items'),
    path('all/', views.all_items, name='all_items'),
    path('item/update/<int:pk>/', views.update_items, name='update-items'),
    path('item/<int:pk>/delete/', views.delete_items, name='delete-items'),
    path("file/",views.uploadImage, name="uploadImage")

   
]



