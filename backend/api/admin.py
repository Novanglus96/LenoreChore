from django.contrib import admin
from .models import Area, Chore, HistoryItem, Option

# Register your models here.

admin.site.register(Area)
admin.site.register(Chore)
admin.site.register(HistoryItem)
admin.site.register(Option)
