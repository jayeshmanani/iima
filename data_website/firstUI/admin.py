from django.contrib import admin
from firstUI.models import Country
from firstUI.models import FinanceData
# Register your models here.

admin.site.register(Country)
admin.site.register(FinanceData)



# from this website -> https://medium.com/analytics-vidhya/create-a-fullstack-app-with-django-graphql-and-vuejs-727a0cf41820

# from django.contrib import admin
# from .models import *
# class CityAdmin(admin.ModelAdmin):
#     fields = (‘city_name’,)
# class TitleAdmin(admin.ModelAdmin):
#     fields = (‘title_name’,)
# class EmployeeAdmin(admin.ModelAdmin):
#     fields = (‘employee_name’, ‘employee_city’, ‘employee_title’,)
# admin.site.register(City, CityAdmin)
# admin.site.register(Title, TitleAdmin)
# admin.site.register(Employee, EmployeeAdmin)
