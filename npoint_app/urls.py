from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("my_account/", views.my_account, name = 'my_account'),
    path("account/token/regenerate/", views.regenerate_token, name="regenerate_token"),
    path('main/', views.main, name='main'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('register/', views.register_page, name='register'),
    path('json_viewer/<str:username>/<slug:title_slug>/<int:json_id>/', views.json_viewer, name='json_viewer'),
    # path('json_viewer/', views.json_viewer, name='json_viewer'),
    path("json_form/", views.json_form, name='json_form'),
    path('my_json_form', views.my_json_form, name='my_json_form'),
    path("edit_json_form/<slug:title_slug>/<int:json_id>/", views.edit_json_form, name='edit_json_form'),
    path("my_json_form/<int:json_id>/delete", views.delete_json_form, name='delete_json_form'),
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('docs/', views.docs, name='docs'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path("terms_of_service/", views.terms_of_service, name='terms_of_service'),
    path('error-404/', views.handler404, name='handler404'),
    path('reset_password/', views.password_setting, name='password_setting'),
    
    
    path("base/", views.base, name='base'),
]





