from django.urls import path, include
from . import views

urlpatterns = [
    path(r'', include('django.contrib.auth.urls')),
    path(r'', views.index, name='index'),
    path(r'profile/', views.profile, name='profile'),
    path(r'training/', views.training, name='training'),
    path(r'walking/', views.walking, name='walking'),
    path(r'test/', views.test, name='test'),
    path(r'shop/', views.shop, name='shop'),
    path(r'price/', views.price, name='price'),
    path(r'order', views.order, name='order'),
    path(r'interesting/', views.interesting, name='interesting'),
    path(r'discounts/', views.discounts, name='discounts'),
    path(r'contacts/', views.contacts, name='contacts'),
    path(r'about_us/', views.about_us, name='about_us'),
    path(r'consultation/', views.consultation, name='consultation'),
    path(r'book_walking/', views.book_walking, name='book_walking'),
]
