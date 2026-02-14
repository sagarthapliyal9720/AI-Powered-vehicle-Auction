from django.contrib import admin

# Register your models here.
from .models import Car,Bid,Watchlist
admin.site.register(Car)
admin.site.register(Bid)
admin.site.register(Watchlist)
