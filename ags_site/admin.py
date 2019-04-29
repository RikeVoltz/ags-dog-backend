from django.contrib import admin

from ags_site.models import Walker, WalkingZone, WalkingDate, ShopProduct, ShopProductCategory

admin.site.register(Walker)
admin.site.register(WalkingZone)
admin.site.register(WalkingDate)
admin.site.register(ShopProduct)
admin.site.register(ShopProductCategory)
