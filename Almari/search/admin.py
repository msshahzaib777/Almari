from django.contrib import admin
from .models import product, fav, profile

admin.site.register(product)
admin.site.register(fav)
admin.site.register(profile)

# Register your models here.
