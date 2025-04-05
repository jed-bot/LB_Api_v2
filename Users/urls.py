from django.urls import path
from .views import get_users  # Import the function from views
from . import views  # Import the views module
urlpatterns = [

    path('get-users/', get_users, name='get_users'),  # Define the route
    path('register/', views.register_user, name='register_user'),
    path('login/',views.log_in_user, name = 'log_in_user'),
    path('reset_password/',views.reset_password, name ='reset_password' ),
    path('delete_account/',views.delete_account, name = 'delete_account'),
    path('classify/', views.classify, name='classify'),
    path('edit_profile/',views.edit_profile, name = 'edit_profile')
]

