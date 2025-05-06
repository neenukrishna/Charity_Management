from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render
from .models import Donation, DonationProduct,Inventory

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


class DonationAdmin(admin.ModelAdmin):
    list_display = (
        'donation_id',
        'user',
        'donor_email',
        'donation_type',
        'amount',
        'quantity',
        'donation_details',
        'date_time',
        'status'
    )
    list_filter = ('donation_type', 'status', 'date_time')
    search_fields = ('user__username', 'user__email', 'donation_details')

    def donor_email(self, obj):
        return obj.user.email
    donor_email.short_description = 'Donor Email'

# admin.site.register(Donation, DonationAdmin)


class DonationProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'donation_amount')
    list_filter = ('category',)
    search_fields = ('name', 'description')



admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('inventory_id', 'donation', 'total_quantity', 'allocated_quantity', 'available_quantity', 'beneficiary')


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('feedback_id', 'user', 'rating', 'short_comments', 'reply', 'date')
    list_filter = ('date', 'rating')
    search_fields = ('user__fullname', 'comments', 'reply')
    ordering = ('-date',)
    # Make everything except reply read-only so that admin can only modify the reply
    readonly_fields = ('feedback_id', 'user', 'rating', 'comments', 'date')
    
    def short_comments(self, obj):
        # Show the first 50 characters of comments
        return obj.comments[:50] + ('...' if len(obj.comments) > 50 else '')
    short_comments.short_description = 'Comments'


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')


from .models import Contact
from django.contrib import admin
from .models import CustomUser
from .models import Donation
from .models import Event
from .models import Volunteer
from .models import BloodDonor
from .models import BeneficiarySupport
from .models import Inventory
from .models import Payment
from .models import FieldData
# from .models import Notification
from .models import Feedback
from .models import Staff


admin.site.register(CustomUser, CustomUserAdmin)
# admin.site.register(CustomUser)
admin.site.register(Donation,DonationAdmin)
admin.site.register(DonationProduct, DonationProductAdmin)

admin.site.register(Event)
admin.site.register(Volunteer)
admin.site.register(BloodDonor)
admin.site.register(FieldData)
admin.site.register(Feedback,FeedbackAdmin)
# admin.site.register(Inventory,InventoryAdmin)
# admin.site.register(Notification)
admin.site.register(Payment)
# admin.site.register(BeneficiarySupport)
admin.site.register(Staff)
admin.site.register(Contact)
@admin.register(BeneficiarySupport)
class BeneficiarySupportAdmin(admin.ModelAdmin):
    list_display = (
        'beneficiary_id',
        'user',
        'beneficiary_name',
        'emergency_type',
        'emergency_level',
        'disbursement_method',  # use the actual field name
        'date',
        'status',
    )
    list_filter = ('status', 'emergency_level', 'date', 'disbursement_method')  # use the actual field
    search_fields = (
        'beneficiary_name', 
        'user__username', 
        'beneficiary_email', 
        'beneficiary_phone',
        'other_donation_type',
        'custom_other_donation',
        'disbursement_method',  # if needed for search
        'bank_name',             # optional: to search by bank name if required
    )

    
from .models import PalliativePatient

@admin.register(PalliativePatient)
class PalliativePatientAdmin(admin.ModelAdmin):
    list_display = (
        'patientName',
        'age',
        'gender',
        'contactNumber',
        'created_at',
    )
    search_fields = ('patientName', 'contactNumber')

def admin_only(user):
    return user.is_superuser

admin.site.login = login_required(user_passes_test(admin_only)(admin.site.login))