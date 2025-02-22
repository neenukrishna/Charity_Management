from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render

# from django.contrib.auth.decorators import login_required, user_passes_test

admin.site.site_header = "Charity Management Admin"
admin.site.site_title = "Charity Admin Panel"
admin.site.index_title = "Welcome to the Charity Management System"

class CustomUserAdmin(UserAdmin):
    # model = CustomUser
    list_display = ('fullname', 'email', 'phone', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('fullname', 'email', 'phone')
    ordering = ('fullname',)
    fieldsets = (
        ("Personal Info", {'fields': ('fullname', 'email', 'phone', 'dob', 'place', 'post', 'pin', 'district', 'gender')}),
        ("Account Details", {'fields': ('username', 'password', 'user_type', 'is_staff', 'is_active')}),
        ("Permissions", {'fields': ('groups', 'user_permissions')}),
    )
    

# Customizing other models in admin
class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'donation_type', 'amount', 'status', 'date_time')
    list_filter = ('status', 'donation_type')
    search_fields = ('user__fullname', 'donation_type')

class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'event_date', 'location', 'event_status')
    list_filter = ('event_status',)
    search_fields = ('event_type', 'location')

class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'status')
    list_filter = ('status',)
    search_fields = ('full_name', 'email')




def is_admin(user):
    # Replace this with your actual admin test logic.
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def sponsorship_details(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    sponsorships = event.sponsorships.all()  # Using the related_name from the ForeignKey.
    context = {
        'event': event,
        'sponsorships': sponsorships,
    }
    return render(request, 'sponsorship_details.html', context)




from django.contrib import admin
from .models import CustomUser
from .models import Donation
from .models import Event
from .models import Volunteer
from .models import BloodDonor
from .models import BeneficiarySupport
from .models import PalliativeCare
from .models import Inventory
from .models import Payment
from .models import FieldData
from .models import Notification
from .models import Feedback
from .models import Staff


admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(CustomUser)
admin.site.register(Donation)
admin.site.register(Event)
admin.site.register(Volunteer)
admin.site.register(BloodDonor)
admin.site.register(FieldData)
admin.site.register(Feedback)
admin.site.register(Inventory)
admin.site.register(PalliativeCare)
admin.site.register(Notification)
admin.site.register(Payment)
admin.site.register(BeneficiarySupport)
admin.site.register(Staff)


def admin_only(user):
    return user.is_superuser

admin.site.login = login_required(user_passes_test(admin_only)(admin.site.login))