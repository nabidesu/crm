from django.contrib import admin


# Register your models here.
from .models import *


admin.site.register(Customer)
admin.site.register(Reviews)
admin.site.register(Status)
admin.site.register(StaffProfile)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customerEmail', 'noOfDays', 'chargeperDay',
                    'activityStatus', 'tokenNumber', 'email_verified')
    readonly_fields = ('tokenNumber',)
    fields = ('customerEmail', 'noOfDays', 'chargeperDay', 'activityStatus',
              'tokenNumber', 'email_verified', 'responseAlert', 'adminUserID')
