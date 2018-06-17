from django.contrib import admin
from .models import Profile, Doctor, appointment


class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender','profileFilled','bdate', 'photo']

class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user','organization','specialization','rating','phoneNumber','address']

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doc','scheduled_date','scheduled_time','status']


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Doctor, DoctorAdmin)
admin.site.register(appointment, AppointmentAdmin)
