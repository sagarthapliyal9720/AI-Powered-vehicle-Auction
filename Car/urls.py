from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    
    path('',views.Home,name="home"),
    path('register/',views.register_view,name="register"),
    path('Login/',views.login_view,name="login_view"),
    path('carlist/',views.Car_list,name="car_list"),
    path('car/<int:id>/', views.car_detail, name="car_detail"),
    path('logout/',views.logout_view,name="logout"),
    path('car/<int:id>/bid/', views.bid_car, name="bid_car"),
    path('addcar/',views.add_car,name="addcar"),
    path('my-bidding/', views.my_bidding, name='my_bidding'),
    path('my-listings/', views.my_listings, name='my_listings'),

    path('ai',views.Find_price,name="Find_price")


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)