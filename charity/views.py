from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser,FieldData, Volunteer,Task,FieldAssignment,FieldArea,Notif
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Donation,Event,Volunteer,BloodDonor,Payment, BeneficiarySupport, PalliativeCare, Inventory,  FieldData, Feedback,Inventory, FieldData,Staff,Sponsorship,DonationProduct,Contact,PalliativePatient
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import ChatMessage, CustomUser
from decimal import Decimal
from django.contrib import messages
from django import forms
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.contrib.auth.models import User, Group
import razorpay
import uuid
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required






User = get_user_model()

# Helper function to check if a user is an admin (superuser)
def is_admin(user):
    return user.is_staff or user.is_superuser


#---------------------------------ADMIN USER DASHBOARD--------------------------------------------------------------------------------
def home(request):
    feedbacks = Feedback.objects.all().order_by('-date')[:5]  # Show recent 5 feedbacks
    return render(request, 'home.html', {'feedbacks': feedbacks})


def all_feedbacks(request):
    feedbacks = Feedback.objects.order_by('-date')
    return render(request, 'feedback/all_feedbacks.html', {'feedbacks': feedbacks})

@login_required
def user_home(request):
    return render(request, 'user_home.html')
@login_required
def account_dashboard(request):
    donations = Donation.objects.filter(user=request.user).order_by('-date_time')
    beneficiary_requests = BeneficiarySupport.objects.filter(user=request.user).order_by('-date')
    sponsorships = Sponsorship.objects.filter(user=request.user).select_related('event')
    notifications = Notif.objects.filter(user=request.user).order_by('-date_time')
    notifications.update(unread=False)

    context = {
        'donations': donations,
        'sponsorships': sponsorships,
        'beneficiary_requests': beneficiary_requests,
        'notifications': notifications,
    }
    return render(request, 'home/dashboard.html', context)


def notification_count(request):
    if request.user.is_authenticated:
        # For example, count only unread notifications:
        count = Notif.objects.filter(user=request.user, unread=True).count()
    else:
        count = 0
    return {'notification_count': count}

def contact_view(request):
    if request.method == 'POST':
        # Debug: print the POST data to the console
        print("Received POST data:", request.POST)
        
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message_text = request.POST.get('message', '').strip()

        # Check that all fields are provided
        if name and email and message_text:
            # Create the contact object
            contact = Contact.objects.create(name=name, email=email, message=message_text)
            print("Contact created:", contact)
            messages.success(request, 'Your message has been sent successfully.')
            return redirect('user_home')
        else:
            messages.error(request, 'Please fill out all fields.')
    
    return render(request, 'user_home.html')


def admin_contact_list(request):
    contacts = Contact.objects.all().order_by('-created_at')
    print("Total contacts:", contacts.count())  # Debug: log the number of contacts
    return render(request, 'feedback/contacts.html', {'contacts': contacts})


@login_required
def profile(request):
    return render(request, 'profile.html')

import json
from .models import Donation, BeneficiarySupport  # adjust as needed

# views.py
@login_required
def staff_dashboard(request):
    if not request.user.is_staff:
        return redirect('login')

    # Emergency Requests Data
    urgent_requests = BeneficiarySupport.objects.filter(emergency_level="High")
    new_emergency = urgent_requests.filter(status='Pending').count()
    pending_actions = urgent_requests.exclude(status='Completed').count()

    # Donations Data
    today = timezone.now().date()
    today_donations = Donation.objects.filter(donation_date__date=today).count()
    
    # Upcoming Events
    upcoming_event = Event.objects.filter(event_date__gte=today).order_by('event_date').first()

    # Donation Breakdown Chart Data
    donation_breakdown = Donation.objects.values('donation_type').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    donation_data = {
        'labels': [d['donation_type'] for d in donation_breakdown],
        'data': [float(d['total']) for d in donation_breakdown]
    }

    # Emergency Requests Distribution
    emergency_dist = BeneficiarySupport.objects.values('emergency_type').annotate(
        count=Count('id')
    )
    emergency_data = {
        'labels': [e['emergency_type'] for e in emergency_dist],
        'data': [e['count'] for e in emergency_dist]
    }

    context = {
        'new_emergency': new_emergency,
        'pending_actions': pending_actions,
        'today_donations': today_donations,
        'upcoming_event': upcoming_event,
        'donation_breakdown': json.dumps(donation_data),
        'emergency_distribution': json.dumps(emergency_data),
    }

    return render(request, 'staff_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Counts and totals
    total_beneficiaries = BeneficiarySupport.objects.count()
    total_volunteers = Volunteer.objects.count()
    total_donations = Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
    urgent_requests_count = BeneficiarySupport.objects.filter(emergency_level="High").count()
    urgent_requests = BeneficiarySupport.objects.filter(
        emergency_level="High",
        status="Pending"
    ).order_by('-date')[:5]
    # Donations by type
    donations_by_type = Donation.objects.values('donation_type').annotate(total=Sum('amount'))
    
    # Monthly activity data
    monthly_activity = {
        'labels': ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        'data': [30, 50, 40, 60, 70, 80],
    }
    
    context = {
        'total_beneficiaries': total_beneficiaries,
        'total_volunteers': total_volunteers,
        'total_donations': total_donations,
        'urgent_requests_count': urgent_requests_count,
        'urgent_requests': urgent_requests,
        'donations_by_category': donations_by_type,  # Consider renaming to donations_by_type
        'monthly_activity': monthly_activity,
    }
    return render(request, 'admin_dashboard.html', context)
#---------------------------------------------------REGISTER-LOGIN--------------------------------------------------------------------

# User Registration View (Without Forms)
def register(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        place = request.POST.get('place')
        post = request.POST.get('post')
        pin = request.POST.get('pin')
        district = request.POST.get('district')
        gender = request.POST.get('gender')
        user_type = request.POST.get('user_type')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            user = CustomUser.objects.create(
                fullname=fullname,
                email=email,
                phone=phone,
                dob=dob,
                place=place,
                post=post,
                pin=pin,
                district=district,
                gender=gender,
                user_type=user_type,
                username=username,
                password=make_password(password)  # Hash password
            )
            login(request, user)  # Auto-login after registration
            return redirect('home')
        else:
            messages.error(request, "Passwords do not match!")
    
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('username')  # Using email as username
        password = request.POST.get('password')

        # Check if the user is a staff member
        try:
            staff = Staff.objects.get(email=email, status="Active")
            if check_password(password, staff.password):  # Verify hashed password
                request.session['staff_id'] = staff.staff_id  # Store staff session
                request.session['staff_name'] = staff.full_name
                # Redirect based on role
                if staff.role == "Manager":
                    return redirect('staff_dashboard')
                elif staff.role == "Coordinator":
                    return redirect('coordinator_dashboard')
                else:
                    return redirect('staff_dashboard')
            else:
                messages.error(request, "Invalid email or password!")
        except Staff.DoesNotExist:
            # Not a staff member; handle non-staff login if needed
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')
                elif user.groups.filter(name='Volunteers').exists():
                    return redirect('volunteer_dashboard')
                else:
                    return redirect('user_home')
            else:
                messages.error(request, "Invalid username or password!")

    return render(request, 'login.html')





@login_required
@user_passes_test(is_admin)
def admin_change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = request.user  # the admin user who is logged in

        if not user.check_password(current_password):
            messages.error(request, "Your current password is incorrect!")
        elif new_password != confirm_password:
            messages.error(request, "New password and confirmation do not match!")
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Important: keeps the user logged in
            messages.success(request, "Password changed successfully!")
            return redirect('admin_dashboard')  # Update this to your admin dashboard URL name

    return render(request, 'admin_change_password.html')

# User Logout View
def user_logout(request):
    logout(request)
    return redirect('home')



@login_required
def user_profile(request):
    # Renders the user profile page.
    return render(request, 'userhome/user_profile.html', {'user': request.user})

@login_required
def user_update_profile(request):
    User = get_user_model()

    # Inline ModelForm for updating user details.
    class UserUpdateForm(forms.ModelForm):
        class Meta:
            model = User
            fields = [
                'fullname', 'username', 'email', 'phone', 'dob',
                'place', 'post', 'pin', 'district', 'gender'
            ]

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('user_profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'userhome/user_update_profile.html', {'form': form})


#---------------------------------MANAGE SECTION--------------------------------------------------------------------------------
@login_required
@user_passes_test(is_admin)
def manage_users(request):
    search_user_type = request.GET.get('user_type', '').strip()
    # Retrieve only donor and beneficiary users
    users = CustomUser.objects.filter(user_type__in=['donor', 'beneficiary'])
    
    # If a search term is provided, filter further by user_type
    if search_user_type:
        users = users.filter(user_type__icontains=search_user_type)
    
    return render(request, 'manage_users.html', {
        'users': users,
        'search_user_type': search_user_type
    })



def manage_donations(request):
    donations = Donation.objects.all()

    donation_type = request.GET.get('donation_type')
    details = request.GET.get('details')
    status = request.GET.get('status')

    if donation_type:
        donations = donations.filter(donation_type=donation_type)
    if details:
        donations = donations.filter(donation_details__icontains=details)
    if status:
        donations = donations.filter(status__icontains=status)

    context = {
        'donations': donations
    }
    return render(request, 'manage_donations.html', context)


# def is_admin_or_staff(user):
#     return user.is_authenticated and (user.is_staff or user.user_type == "staff")  # Ensure user_type exists

@login_required
@user_passes_test(is_admin)
def manage_staff(request):
    # Retrieve a role filter from GET parameters (if provided)
    role_filter = request.GET.get('role', '').strip()
    
    # Order by staff_id instead of id.
    staff_members = Staff.objects.all().order_by('-staff_id')
    
    # If a role filter is provided, filter by role (e.g., 'coordinator' or 'manager')
    if role_filter:
        staff_members = staff_members.filter(role__iexact=role_filter)
    
    context = {
        'staff_members': staff_members,
        'role_filter': role_filter
    }
    
    return render(request, 'manage_staff.html', context)




from django.db.models import Q

def manage_blood_donors(request):
    # Get search parameters from the request (defaulting to empty strings)
    search_blood_group = request.GET.get('blood_group', '').strip()
    search_address = request.GET.get('address', '').strip()

    # Start with all donors
    donors = BloodDonor.objects.all()

    # Filter by blood group if provided
    if search_blood_group:
        donors = donors.filter(blood_group__icontains=search_blood_group)
    
    # Filter by address (e.g., matching any part of place, post, or district)
    if search_address:
        donors = donors.filter(
            Q(place__icontains=search_address) |
            Q(post__icontains=search_address) |
            Q(district__icontains=search_address)
        )

    # Determine which dashboard URL to use
    if request.user.is_superuser:
        dashboard_url = 'admin_dashboard'
    else:
        dashboard_url = 'staff_dashboard'
    
    context = {
        'donors': donors,
        'dashboard_url': dashboard_url,
        'search_blood_group': search_blood_group,
        'search_address': search_address,
    }
    return render(request, 'manage_blood_donors.html', context)



def manage_palliative_care(request):
    palliative_cases = PalliativePatient.objects.all()
    return render(request, 'manage_palliative_care.html', {
        'palliative_cases': palliative_cases
    })

# Manage Resources & Inventory
# @login_required
# @user_passes_test(is_admin)

# Helper function: checks if user is a donor (customize as needed)

def is_donor(user):
    return user.user_type == "donor"

@login_required
def donor_notifications(request):
    if request.user.user_type != "donor":
        return redirect('user_home')
    
    # Retrieve notifications for the logged-in donor
    notifications = Notif.objects.filter(user=request.user).order_by('-date_time')
    
    # Mark all notifications as read
    notifications.update(unread=False)
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'donor_notifications.html', context)



# Helper: returns True if the user is a beneficiary.
def is_beneficiary(user):
    return user.is_authenticated and user.user_type == "beneficiary"


@login_required
def beneficiary_notifications(request):
    # Ensure that only users with a beneficiary user_type access this view
    if request.user.user_type != "beneficiary":
        return redirect('user_home')  # Or some error page / permission denied view

    # Get notifications for the currently logged-in beneficiary
    notifications = Notif.objects.filter(user=request.user).order_by('-date_time')
    context = {
        'notifications': notifications,
    }
    return render(request, 'notification/beneficiary_notification.html', context)


def is_manager(user):
    """
    Check if the logged-in user is a manager by matching the user's email
    with a Staff record that has the role 'Manager'.
    """
    return Staff.objects.filter(role__iexact="Manager", email=user.email).exists()

# @login_required
# @user_passes_test(is_manager)
# def manager_notifications(request):
#     """
#     Manager view: Display notifications for the logged-in manager.
#     """
#     notifications = Notification.objects.filter(user=request.user).order_by('-date_time')
#     print("Logged-in Manager ID:", request.user.id, "Email:", request.user.email)
#     print("Manager notifications count:", notifications.count())
#     return render(request, 'home/manager_notifications.html', {'notifications': notifications})

def is_coordinator(user):
    """
    Check if the logged-in user is a coordinator by matching the user's email
    with a Staff record that has the role 'Coordinator'.
    """
    return Staff.objects.filter(role__iexact="Coordinator", email=user.email).exists()

@login_required
@user_passes_test(is_admin)
def manage_field_data(request):
    # Get filter parameters from the request
    volunteer_name = request.GET.get('volunteer_name', '').strip()
    urgency_level = request.GET.get('urgency_level', '').strip()
    status = request.GET.get('status', '').strip()

    # Initial queryset
    field_data_entries = FieldData.objects.all()

    # Apply filters
    if volunteer_name:
        field_data_entries = field_data_entries.filter(volunteer__full_name__icontains=volunteer_name)
    if urgency_level:
        field_data_entries = field_data_entries.filter(urgency_level__icontains=urgency_level)
    if status:
        field_data_entries = field_data_entries.filter(status__icontains=status)

    context = {
        'field_data_entries': field_data_entries,
        'volunteer_name': volunteer_name,
        'urgency_level': urgency_level,
        'status': status,
    }
    return render(request, 'manage_field_data.html', context)


@login_required
@user_passes_test(is_admin)
def mark_field_solved(request, field_id):
    if request.method == 'POST':
        field_data = get_object_or_404(FieldData, field_id=field_id)
        field_data.status = 'Solved'
        field_data.save()
        messages.success(request, f'Successfully marked {field_data.full_name} as solved!')
    return redirect('manage_field_data')


# # Manage Notifications
# @login_required
# @user_passes_test(is_admin)
# def manage_notifications(request):
#     notifications = Notification.objects.all()
#     return render(request, 'manage_notifications.html', {'notifications': notifications})

# Manage Field Data Collection
@login_required
@user_passes_test(is_admin)
def manage_field_data(request):
    field_data_entries = FieldData.objects.all()
    return render(request, 'manage_field_data.html', {'field_data_entries': field_data_entries})





#--------------------------------------------ADD USER---------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def add_user(request):
    if request.method == 'POST':
        # Get the form data from the request
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        place = request.POST.get('place')
        post = request.POST.get('post')
        pin = request.POST.get('pin')
        district = request.POST.get('district')
        gender = request.POST.get('gender')
        user_type = request.POST.get('user_type')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check if the passwords match
        if password == confirm_password:
            # Create the user and hash the password
            user = CustomUser.objects.create(
                fullname=fullname,
                email=email,
                phone=phone,
                place=place,
                post=post,
                pin=pin,
                district=district,
                gender=gender,
                user_type=user_type,
                username=username,
                password=make_password(password)  # Hash the password before saving
            )
            return redirect('manage_users')  # Redirect to the manage users page
        else:
            # Show error message if passwords do not match
            error_message = "Passwords do not match!"
            return render(request, 'add_user.html', {'error_message': error_message})

    return render(request, 'add_user.html')  # Render the form if it's a GET request


#--------------------------------------------ADD DONATION---------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def add_donation(request):
    if request.method == 'POST':
        # Get data from the form
        donation_type = request.POST.get('donation_type')
        amount = request.POST.get('amount')
        donation_details = request.POST.get('donation_details')
        quantity = request.POST.get('quantity')
        status = request.POST.get('status')
        
        # Create the new donation
        donation = Donation.objects.create(
            user=request.user,  # Admin or logged-in user can add donations
            donation_type=donation_type,
            amount=amount,
            donation_details=donation_details,
            quantity=quantity,
            status=status
        )
        
        messages.success(request, "Donation added successfully!")
        return redirect('manage_donations')  # Redirect back to the manage donations page

    return render(request, 'add_donation.html') 




#--------------------------------------------ADD BLOOD DONOR---------------------------------------------------------------------------
def add_blood_donor(request):
    if request.method == 'POST':
        # Get data from the form
        full_name = request.POST.get('full_name')
        blood_group = request.POST.get('blood_group')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        place = request.POST.get('place')
        post = request.POST.get('post')
        pin = request.POST.get('pin')
        district = request.POST.get('district')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        
        # Create the new blood donor
        BloodDonor.objects.create(
            full_name=full_name,
            blood_group=blood_group,
            email=email,
            phone=phone,
            place=place,
            post=post,
            pin=pin,
            district=district,
            gender=gender,
            dob=dob
        )
        
        return redirect('manage_blood_donors')  # Redirect to manage blood donors page
    
    return render(request, 'add_blood_donor.html')  # Render the form if it's a GET request




#--------------------------------------------ADD EMERGENCY REQUEST---------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def add_emergency_request(request):
    if request.method == 'POST':
        # Get data from the form
        emergency_type = request.POST.get('emergency_type')
        details = request.POST.get('details')
        response = request.POST.get('response')
        emergency_level = request.POST.get('emergency_level')
        status = request.POST.get('status')
        proof = request.FILES.get('proof')  # Handle file upload
        
        # Create the new emergency request
        BeneficiarySupport.objects.create(
            user=request.user,  # Admin or logged-in user adding the request
            emergency_type=emergency_type,
            details=details,
            response=response,
            emergency_level=emergency_level,
            status=status,
            proof=proof
        )

        messages.success(request, "Emergency request added successfully!")
        return redirect('manage_emergency_support')  # Redirect to manage emergency requests page
    
    return render(request, 'add_emergency_request.html') 


#--------------------------------------------ADD PALLIATIVE CARE---------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def add_palliative_care(request):
    if request.method == 'POST':
        # Get data from the form
        user = request.user  # Admin or logged-in user adding the request
        volunteer_id = request.POST.get('volunteer_id')
        volunteer = Volunteer.objects.get(id=volunteer_id)
        date = request.POST.get('date')
        needs = request.POST.get('needs')
        status = request.POST.get('status')

        # Create the new palliative care case
        PalliativeCare.objects.create(
            user=user,
            volunteer=volunteer,
            date=date,
            needs=needs,
            status=status
        )

        messages.success(request, "Palliative Care case added successfully!")
        return redirect('manage_palliative_care')  # Redirect to manage palliative care cases page
    
    # Get all volunteers to show in the form
    volunteers = Volunteer.objects.all()
    return render(request, 'add_palliative_care.html', {'volunteers': volunteers})  # Render the form for GET request



#--------------------------------------------ADD VOLUNTEER---------------------------------------------------------------------------

def add_volunteer(request):
    if request.method == 'POST':
        # Get data from the form
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        place = request.POST.get('place')
        post = request.POST.get('post')
        pin = request.POST.get('pin')
        district = request.POST.get('district')
        availability_date = request.POST.get('availability_date')  # Correct field name
        volunteering_in = request.POST.get('volunteering_in')  # Add this field if needed
        assigned_task = request.POST.get('assigned_task')
        proof = request.FILES.get('proof')  # Handle file upload
        status = request.POST.get('status')

        # Create the new volunteer
        Volunteer.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            dob=dob,
            gender=gender,
            place=place,
            post=post,
            pin=pin,
            district=district,
            availability_date=availability_date,  # Correct field name
            volunteering_in=volunteering_in,
            assigned_task=assigned_task,
            proof=proof,
            status=status
        )

        messages.success(request, "Volunteer added successfully!")
        return redirect('manage_volunteers')  # Redirect to manage volunteers page
    
    return render(request, 'add_volunteer.html')  # Render the form for GET request



#--------------------------------------------INVENTORY---------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def add_inventory(request):
    if request.method == 'POST':
        # Get data from the form
        donation_id = request.POST.get('donation_id')
        total_quantity = request.POST.get('total_quantity')
        allocated_quantity = request.POST.get('allocated_quantity')
        beneficiary_id = request.POST.get('beneficiary_id')

        donation = Donation.objects.get(id=donation_id)
        beneficiary = BeneficiarySupport.objects.get(id=beneficiary_id)

        # Create the new inventory record
        Inventory.objects.create(
            donation=donation,
            total_quantity=total_quantity,
            allocated_quantity=allocated_quantity,
            beneficiary=beneficiary
        )

        messages.success(request, "Inventory record added successfully!")
        return redirect('manage_inventory')  # Redirect to manage inventory page
    
    # Get all donations and beneficiaries to display in the form
    donations = Donation.objects.all()
    beneficiaries = BeneficiarySupport.objects.all()
    return render(request, 'add_inventory.html', {'donations': donations, 'beneficiaries': beneficiaries})



#--------------------------------------------NOTIFICATION---------------------------------------------------------------------------

# @login_required
# @user_passes_test(is_admin)
# def add_notification(request):
#     if request.method == 'POST':
#         # Get data from the form
#         user_id = request.POST.get('user_id')
#         message = request.POST.get('message')

#         user = CustomUser.objects.get(id=user_id)

#         # Create the new notification
#         Notification.objects.create(
#             user=user,
#             message=message
#         )

#         messages.success(request, "Notification added successfully!")
#         return redirect('manage_notifications')  # Redirect to manage notifications page
    
#     # Get all users to display in the form
#     users = CustomUser.objects.all()
#     return render(request, 'add_notification.html', {'users': users})



#--------------------------------------------FIELD DATA---------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def add_field_data(request):
    if request.method == 'POST':
        # Get data from the form
        volunteer_id = request.POST.get('volunteer_id')
        full_name = request.POST.get('full_name')
        place = request.POST.get('place')
        post = request.POST.get('post')
        pin = request.POST.get('pin')
        district = request.POST.get('district')
        email = request.POST.get('email')
        details = request.POST.get('details')
        status = request.POST.get('status')
        proof = request.FILES.get('proof')  # Handle file upload

        volunteer = Volunteer.objects.get(id=volunteer_id)

        # Create the new field data record
        FieldData.objects.create(
            volunteer=volunteer,
            full_name=full_name,
            place=place,
            post=post,
            pin=pin,
            district=district,
            email=email,
            details=details,
            status=status,
            proof=proof
        )

        messages.success(request, "Field data added successfully!")
        return redirect('manage_field_data')  # Redirect to manage field data page
    
    # Get all volunteers to display in the form
    volunteers = Volunteer.objects.all()
    return render(request, 'add_field_data.html', {'volunteers': volunteers})


#--------------------------------------------SEND FEEDBACK REPLY---------------------------------------------------------------------------

@login_required
@user_passes_test(is_admin)
def manage_feedbacks(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'manage_feedbacks.html', {'feedbacks': feedbacks})




@login_required
@user_passes_test(is_admin)
def send_feedback_reply(request, feedback_id):
    feedback = get_object_or_404(Feedback, feedback_id=feedback_id)

    if request.method == 'POST':
        reply = request.POST.get('reply')
        feedback.reply = reply
        feedback.save()
        messages.success(request, "Reply sent successfully!")
        return redirect('manage_feedbacks')

    return redirect('manage_feedbacks')
 # Make sure this is the correct model
 
 
 #------------------------------------------ADD STAFF------------------------------------------

import string
import secrets
from django.contrib.auth.hashers import make_password


def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length))


@login_required
def add_staff(request):
    if request.method == "POST":
        # Extract data from the POST request
        full_name = request.POST.get("fullname")
        role = request.POST.get("role")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        dob = request.POST.get("dob")
        gender = request.POST.get("gender")
        place = request.POST.get("place")
        post = request.POST.get("post")
        district = request.POST.get("district")
        pin = request.POST.get("pin")
        join_date = request.POST.get("join_date")
        status = request.POST.get("status")
        
        # Generate a random password automatically
        generated_password = generate_random_password(length=10)  # adjust length if needed
        hashed_password = make_password(generated_password)
        
        # Create and save the Staff instance
        staff = Staff(
            full_name=full_name,
            role=role,
            email=email,
            phone=phone,
            dob=dob,
            gender=gender,
            password=hashed_password,  # Store the hashed password
            place=place,
            post=post,
            district=district,
            pin=pin,
            join_date=join_date,
            status=status
        )
        staff.save()
        
        # Send an email with the generated password
        subject = "Your Staff Account Has Been Created"
        message = (
            f"Hello {full_name},\n\n"
            f"Your staff account has been created successfully.\n"
            f"Your login password is: {generated_password}\n\n"
            f"Please change your password after logging in for the first time.\n\n"
            f"Thank you."
        )
        from_email = settings.DEFAULT_FROM_EMAIL  # Make sure this is set in your settings.py
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)
        
        messages.success(request, "Staff added successfully. An email has been sent with login details.")
        return redirect("manage_staff")
    
    return render(request, "add_staff.html")


#--------------------------------------CHAT-------------------------------------------------------------------------
@login_required
def chat_view(request):
    # Get all messages between the logged-in user and admin
    admin = CustomUser.objects.filter(is_superuser=True).first()
    messages = ChatMessage.objects.filter(sender=request.user) | ChatMessage.objects.filter(receiver=request.user)
    messages = messages.order_by('timestamp')

    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text:
            ChatMessage.objects.create(sender=request.user, receiver=admin, message=message_text)
            return redirect('chat_view')

    return render(request, 'chat.html', {'messages': messages})


@login_required
@user_passes_test(is_admin)
def admin_chat_view(request):
    users = CustomUser.objects.exclude(is_superuser=True)  
    selected_user = None
    messages = None

    if 'user_id' in request.GET:
        selected_user = CustomUser.objects.get(id=request.GET['user_id'])
        messages = ChatMessage.objects.filter(sender=selected_user) | ChatMessage.objects.filter(receiver=selected_user)
        messages = messages.order_by('timestamp')

    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text and selected_user:
            ChatMessage.objects.create(sender=request.user, receiver=selected_user, message=message_text)
            return redirect(f"{request.path}?user_id={selected_user.id}")

    return render(request, 'admin_chat.html', {'users': users, 'messages': messages, 'selected_user': selected_user})


#---------------------------------------------------started user views ---------------------------------------------------------------------



@login_required
def make_donation(request):
    if request.method == 'POST':
        # Process the donation form data here.
        # For example, you could retrieve form data and create a Donation object.
        donation_type = request.POST.get('donation_type')
        amount = request.POST.get('amount')
        donation_details = request.POST.get('donation_details')
        
        
        messages.success(request, "Thank you for your donation!")
        return redirect('user_home')  
    
    return render(request, 'donation.html')





def register_blood_donation(request):
    return render(request, 'register_blood_donation.html')


@login_required
def submit_feedback(request):
    if request.method == "POST":
        rating = request.POST.get('rating')
        comments = request.POST.get('comments')

        if not rating or not comments:
            messages.error(request, "Please fill in all fields.")
            return redirect('submit_feedback')

        Feedback.objects.create(user=request.user, rating=rating, comments=comments)

        messages.success(request, "Feedback submitted successfully!")
        return redirect('user_home')  # Redirect to home or feedback page

    return render(request, 'feedback/submit_feedback.html')



#-------------------------------------staff section----------------------------------------------------------------------------------
def staff_dashboard(request):
    # Check if the staff member is logged in.
    if 'staff_id' not in request.session:
        return redirect("login")
    
    # Retrieve the staff member’s details.
    staff_member = Staff.objects.get(staff_id=request.session['staff_id'])
    
    return render(request, "staff_dashboard.html", {"staff_member": staff_member})


# Profile Display View
def staff_profile(request):
    staff_id = request.session.get('staff_id')
    if not staff_id:
        messages.error(request, "You must be logged in to view your profile.")
        return redirect('user_login')
    staff_member = get_object_or_404(Staff, pk=staff_id)
    return render(request, 'staff/staff_profile.html', {'staff_member': staff_member})


def update_profile(request):
    staff_id = request.session.get('staff_id')
    if not staff_id:
        messages.error(request, "You must be logged in to update your profile.")
        return redirect('user_login')
    staff_member = get_object_or_404(Staff, pk=staff_id)
    if request.method == "POST":
        staff_member.full_name = request.POST.get('full_name')
        staff_member.email = request.POST.get('email')
        staff_member.phone = request.POST.get('phone')
        staff_member.dob = request.POST.get('dob')  # You might need to parse this date.
        staff_member.gender = request.POST.get('gender')
        staff_member.place = request.POST.get('place')
        staff_member.post = request.POST.get('post')
        staff_member.district = request.POST.get('district')
        staff_member.pin = request.POST.get('pin')
        staff_member.status = request.POST.get('status')
        # Update additional fields as needed...
        staff_member.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('staff_profile')
    return render(request, 'staff/update_staff.html', {'staff_member': staff_member})


import logging
logger = logging.getLogger(__name__)
def change_password(request):
    staff_id = request.session.get('staff_id')
    if not staff_id:
        messages.error(request, "You must be logged in to change your password.")
        return redirect('user_login')
        
    staff_member = get_object_or_404(Staff, pk=staff_id)
    
    if request.method == "POST":
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Debug output
        logger.debug("Old password entered: %s", old_password)
        logger.debug("Stored hashed password: %s", staff_member.password)
        logger.debug("check_password returns: %s", check_password(old_password, staff_member.password))
        
        if new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
            return redirect('change_password_staff')
        
        if not check_password(old_password, staff_member.password):
            messages.error(request, "Old password is incorrect.")
            return redirect('change_password_staff')
        
        # Update password
        staff_member.password = make_password(new_password)
        staff_member.save()
        
        # If your staff model is integrated with Django's auth system, update the session auth hash:
        # update_session_auth_hash(request, staff_member)
        
        messages.success(request, "Password changed successfully!")
        return redirect('staff_profile')
    
    return render(request, 'staff/change_password_staff.html', {'staff_member': staff_member})


def is_manager(user):
    # Replace 'Managers' with the exact name of your manager group
    return user.is_staff or user.groups.filter(name='Managers').exists()


def staff_manage_events(request):
 # Restrict access to staff only
    
    # Search functionality
    event_type = request.GET.get('event_type', '')
    location = request.GET.get('location', '')
    status = request.GET.get('status', '')

    events = Event.objects.all()

    if event_type:
        events = events.filter(event_type__icontains=event_type)
    if location:
        events = events.filter(location__icontains=location)
    if status:
        events = events.filter(event_status=status)

    return render(request, 'staff/staff_manage_events.html', {'events': events})





def staff_manage_volunteers(request):

    # Retrieve search parameters from GET request.
    query = request.GET.get('q', '')
    availability = request.GET.get('availability', '')
    program = request.GET.get('program', '')
    status = request.GET.get('status', '')

    # Start with all volunteers.
    volunteers = Volunteer.objects.all()

    # Filter volunteers based on search parameters.
    if query:
        volunteers = volunteers.filter(place__icontains=query)
    if availability:
        volunteers = volunteers.filter(availability_date=availability)
    if program:
        volunteers = volunteers.filter(volunteering_in__icontains=program)
    if status:
        volunteers = volunteers.filter(status=status)

    context = {
        'volunteers': volunteers,
        'query': query,
        'availability': availability,
        'program': program,
        'status': status,
    }

    # Render the staff template (e.g., 'staff_manage_volunteers.html').
    return render(request, 'staff/staff_manage_volunteers.html', context)



def staff_manage_blood_donors(request):
    # Restrict access to staff users only.
  # You may redirect to an error page or staff dashboard as needed.

    # Retrieve search parameters from GET request.
    search_blood_group = request.GET.get('blood_group', '')
    search_address = request.GET.get('address', '')

    # Start with all blood donors.
    donors = BloodDonor.objects.all()

    # Filter by blood group if provided.
    if search_blood_group:
        donors = donors.filter(blood_group__icontains=search_blood_group)
    
    # Filter by address (or place) if provided.
    if search_address:
        donors = donors.filter(place__icontains=search_address)

    # Pass the filtered donors and search parameters to the template context.
    context = {
        'donors': donors,
        'search_blood_group': search_blood_group,
        'search_address': search_address,
    }
    
    # Render the staff view template (adjust the template name as needed).
    return render(request, 'staff/staff_manage_blood_donors.html', context)



def staff_manage_donations(request):
    # Restrict access to staff users only.
   # Alternatively, you can raise a 403 error.

    # Retrieve search parameters from GET request.
    donation_type = request.GET.get('donation_type', '')
    details = request.GET.get('details', '')
    status = request.GET.get('status', '')

    # Start with all donations.
    donations = Donation.objects.all()

    # Filter donations by donation type if provided.
    if donation_type:
        donations = donations.filter(donation_type=donation_type)

    # Filter donations by details (using case-insensitive containment).
    if details:
        donations = donations.filter(donation_details__icontains=details)

    # Filter donations by status if provided.
    if status:
        donations = donations.filter(status__icontains=status)

    context = {
        'donations': donations,
    }

    # Render the staff donation management template.
    return render(request, 'staff/staff_manage_donations.html', context)


def staff_manage_palliative_cases(request):
    # Restrict access to staff users only.
   # Alternatively, you can raise a 403 error or redirect elsewhere.

    # Retrieve all palliative care registrations from the database.
    palliative_cases = PalliativePatient.objects.all()

    # Optional: Add filtering based on GET parameters if needed.
    # For example, you might filter by patient name, date, etc.
    # search_query = request.GET.get('search', '')
    # if search_query:
    #     palliative_cases = palliative_cases.filter(patientName__icontains=search_query)

    context = {
        'palliative_cases': palliative_cases,
    }
    
    return render(request, 'staff/staff_manage_palliative_cases.html', context)


def staff_urgent_requests(request):
    # Restrict access to staff users only.
   # Alternatively, return a 403 Forbidden response.

    # Retrieve filter parameters from the GET request.
    assistance_type = request.GET.get('assistance_type', '')
    # We no longer get emergency_level from GET since we want urgent requests only
    payment_method = request.GET.get('payment_method', '')
    status = request.GET.get('status', '')

    # Start with urgent requests only (emergency_level is "High")
    requests_qs = BeneficiarySupport.objects.filter(emergency_level="High")

    # Apply additional filters.
    if assistance_type:
        requests_qs = requests_qs.filter(emergency_type__icontains=assistance_type)
    
    if payment_method:
        requests_qs = requests_qs.filter(disbursement_method__icontains=payment_method)
    
    if status:
        requests_qs = requests_qs.filter(status__icontains=status)
    
    # Order by date descending (most recent first)
    requests_qs = requests_qs.order_by('-date')

    context = {
        'requests': requests_qs,
    }
    
    return render(request, 'staff/staff_urgent_requests.html', context)



def staff_manage_emergency_support(request):
    # Restrict access to staff users only.
     # Or return a 403 Forbidden response

    # Retrieve filter parameters from the GET request.
    emergency_type = request.GET.get('emergency_type', '')
    emergency_level = request.GET.get('emergency_level', '')
    payment_method = request.GET.get('payment_method', '')
    status = request.GET.get('status', '')

    # Start with all beneficiary support requests.
    qs = BeneficiarySupport.objects.all()

    # Apply filters based on provided search criteria.
    if emergency_type:
        qs = qs.filter(emergency_type__icontains=emergency_type)
    if emergency_level:
        qs = qs.filter(emergency_level=emergency_level)
    if payment_method:
        qs = qs.filter(disbursement_method=payment_method)
    if status:
        qs = qs.filter(status__icontains=status)

    # Order by date descending so that the most recent requests appear first.
    qs = qs.order_by('-date')

    context = {
        'requests': qs,
    }

    # Render the staff template (adjust the template path as needed).
    return render(request, 'staff/staff_manage_emergency_support.html', context)


# Staff user check function
def is_staff(user):
    return user.is_authenticated and user.is_staff



def staff_manage_inventory(request):
    # Define money-based donation types
    money_based_types = ['monetary', 'medical', 'meals', 'grocery', 'home']
    donation_type_choices = dict(Donation._meta.get_field('donation_type').choices)
    
    money_summary = {}
    for d_type in money_based_types:
        donations = Donation.objects.filter(donation_type=d_type, status='Paid')
        total_amount = donations.aggregate(total=Sum('amount'))['total'] or 0
        entries_count = donations.count()
        allocated_sum = BeneficiarySupport.objects.filter(
            emergency_type__iexact=d_type, completion_status='Resolved'
        ).aggregate(total_allocated=Sum('allocation_amount'))['total_allocated'] or 0
        available_amount = total_amount - allocated_sum
        
        money_summary[d_type] = {
            'donation_type_display': donation_type_choices.get(d_type, d_type),
            'total_amount': total_amount,
            'allocated_amount': allocated_sum,
            'available_amount': available_amount,
            'entries_count': entries_count,
        }

    # In-Kind (Other) Donations Summary
    qs = Inventory.objects.filter(donation__donation_type='other')
    others_grouped = qs.values('item_name').annotate(
        total_quantity=Sum('quantity'),
        allocated_quantity=Sum('quantity', filter=Q(allocated=True)),
        entries_count=Count('id')
    )
    
    others_summary = []
    for entry in others_grouped:
        total_quantity = entry['total_quantity'] or 0
        allocated_quantity = entry['allocated_quantity'] or 0
        available_quantity = total_quantity - allocated_quantity
        others_summary.append({
            'sub_category': entry['item_name'],
            'total_quantity': total_quantity,
            'allocated_quantity': allocated_quantity,
            'available_quantity': available_quantity,
            'entries_count': entry['entries_count'],
        })

    # Detailed Inventory Listing
    inventory_items = Inventory.objects.select_related('donation', 'allocated_to')
    
    context = {
        'money_summary': money_summary,
        'others_summary': others_summary,
        'inventory_items': inventory_items,
    }

    return render(request, 'staff/staff_manage_inventory.html', context)

from datetime import timedelta



# @login_required
# def staff_manage_notifications(request):
#     # Restrict access to staff users only.
#     if not request.user.is_staff:
#         return redirect('login')
    
#     # Define a time threshold (e.g., last 1 hour)
#     time_threshold = timezone.now() - timedelta(hours=1)
    
#     # Count new donations created in the last hour
#     new_donations_count = Donation.objects.filter(date_time__gte=time_threshold).count()
    
#     # Count new urgent requests created in the last hour.
#     new_requests_count = BeneficiarySupport.objects.filter(date__gte=time_threshold).count()
    
#     # Prepare notifications messages (if count > 0)
#     notifications = []
#     if new_donations_count:
#         notifications.append(f"{new_donations_count} new donation(s) received.")
#     if new_requests_count:
#         notifications.append(f"{new_requests_count} new urgent request(s) received.")
    
#     context = {
#         'notifications': notifications
#     }
    
#     return render(request, 'staff/manager_notifications.html', context)


@staff_member_required
def staff_donation_details(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'staff/donation_details.html', {'donation': donation})






#-------------------------------------home services------------------------------------------------------------------------------


def hospital_without_hunger(request):
    return render(request, 'home/meal.html')

def grocery_assistance(request):
    return render(request, 'home/grocery.html')

def cancer_patient(request):
    return render(request, 'home/cancer_patient.html')

def beneficary_aid(request):
    return render(request, 'home/beneficiary_aid.html')

def palliative_program(request):
    return render(request, 'home/palliative_program.html')


def palliative_register(request):
    if request.method == 'POST':
        # Get form data from request.POST
        patientName = request.POST.get('patientName')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        contactNumber = request.POST.get('contactNumber')
        email = request.POST.get('email')
        medicalCondition = request.POST.get('medicalCondition')
        physicianName = request.POST.get('physicianName')
        additionalDetails = request.POST.get('additionalDetails')

        # (Optional) Save to DB if you have a PalliativePatient model
        patient = PalliativePatient(
            patientName=patientName,
            age=age,
            gender=gender,
            address=address,
            contactNumber=contactNumber,
            email=email,
            medicalCondition=medicalCondition,
            additionalDetails=additionalDetails
        )
        patient.save()

        # 1) Construct the email message
        subject = "Palliative Care Registration Confirmation"
        message = (
            f"Dear {patientName},\n\n"
            "Thank you for registering for our Palliative Care program.\n"
            "We have received your details and will contact you soon.\n\n"
            "Regards,\n"
            "AKG Charitable Society"
        )
        from_email = "your_gmail_username@gmail.com"  # or your EMAIL_HOST_USER
        recipient_list = [email] if email else []

        # 2) Send the email (only if email is provided)
        if recipient_list:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        # 3) Redirect to a success page (or return a success response)
        return redirect('palliative_register_success')

    # If GET request, just render the form page
    return render(request, 'home/palliative_patient.html')


@login_required
def palliative_patient_detail(request, patient_id):
    patient = get_object_or_404(PalliativePatient, id=patient_id)
    return render(request, 'home/palliative_patient_detail.html', {
        'patient': patient,
    })




def assign_volunteer(request, patient_id):
    patient = get_object_or_404(PalliativePatient, id=patient_id)
    if request.method == 'POST':
        volunteer_id = request.POST.get('volunteer_id')
        if volunteer_id:
            # Use the primary key field 'volunteer_id'
            volunteer = get_object_or_404(Volunteer, volunteer_id=volunteer_id)
            patient.volunteer = volunteer
            messages.success(request, f"Volunteer {volunteer.full_name} has been assigned to {patient.patientName}.")
        else:
            patient.volunteer = None
            messages.error(request, "Please select a volunteer.")
        patient.save()
        return redirect('manage_palliative_care')
    
    # Filter volunteers to include only those registered for "Palliative Care Program"
    volunteers = Volunteer.objects.filter(volunteering_in="Palliative Care Program")
    return render(request, 'home/palliative_assign.html', {
        'patient': patient,
        'volunteers': volunteers
    })

    
# @login_required
# def assigned_tasks_view(request):
#     # Retrieve the Volunteer instance linked to the current user
#     volunteer = get_object_or_404(Volunteer, user=request.user)
#     # Query all tasks/patients assigned to this volunteer
#     tasks = PalliativePatient.objects.filter(volunteer=volunteer)
#     return render(request, 'home/assigned_task.html', {
#         'tasks': tasks,
#         'volunteer': volunteer,
#     })

@login_required
def assigned_tasks_view(request):
    """Retrieve all tasks assigned to a volunteer (both general tasks & palliative care)."""
    
    volunteer = get_object_or_404(Volunteer, user=request.user)
    
    # Query all tasks assigned to this volunteer
    task_assignments = Task.objects.filter(volunteer=volunteer)
    # Query all palliative care assignments linked to this volunteer
    palliative_tasks = PalliativePatient.objects.filter(volunteer=volunteer)
    
    general_tasks = []
    for task in task_assignments:
        general_tasks.append({
            'id': task.id,  # Include the task id for URL reverse lookup
            'volunteer': volunteer.full_name,
            'title': f"Task: {task.task_description}",
            'task_description': task.task_description,
            'location': task.location,
            'district': task.district,
            'materials': task.materials if hasattr(task, 'materials') else "N/A",
            'instructions': task.instructions if hasattr(task, 'instructions') else "N/A",
            'status': task.status if hasattr(task, 'status') else "Pending",
            'priority': task.priority if hasattr(task, 'priority') else "Low",
            'assigned_by': 'Coordinator',
            'deadline': task.due_date,
            'assigned_at': task.assigned_at,
            'type': 'Task',
        })
    
    palliative_list = []
    for ptask in palliative_tasks:
        palliative_list.append({
            'patient_id': ptask.id,
            'patient': ptask,
            'title': f"Palliative Care for {ptask.patientName}",
            'description': f"Caring for {ptask.patientName} at {ptask.address}",
            'assigned_by': 'Healthcare Coordinator',
            'deadline': ptask.created_at,
            'assigned_at': ptask.created_at,
            'type': 'Palliative',
            'status': ptask.status,  # Include status here
        })
    
    context = {
        'general_tasks': general_tasks,
        'palliative_tasks': palliative_list,
        'volunteer': volunteer,
    }
    
    return render(request, 'home/assigned_task.html', context)

@login_required
def complete_palliative_case(request, case_id):
    """
    View to mark a palliative care case as completed.
    Only the volunteer assigned to the case may mark it as complete.
    """
    volunteer = get_object_or_404(Volunteer, user=request.user)
    palliative_case = get_object_or_404(PalliativePatient, id=case_id, volunteer=volunteer)
    
    if request.method == "POST":
        palliative_case.status = "Completed"
        palliative_case.save()
        messages.success(request, "Palliative care case marked as completed.")
    return redirect('assigned_tasks_view')


@login_required
def complete_task(request, task_id):
    """
    View to mark a task as completed. Only the volunteer assigned to the task may mark it as complete.
    """
    volunteer = get_object_or_404(Volunteer, user=request.user)
    task = get_object_or_404(Task, id=task_id, volunteer=volunteer)
    
    if request.method == "POST":
        task.status = "Completed"
        task.save()
        messages.success(request, "Task marked as completed.")
    return redirect('assigned_tasks_view')

def volunteer_detail(request, volunteer_id):
    # If primary key is volunteer_id, use volunteer_id=volunteer_id or pk=volunteer_id
    volunteer = get_object_or_404(Volunteer, volunteer_id=volunteer_id)
    return render(request, 'home/volunteer_detail.html', {'volunteer': volunteer})


def palliative_register_success(request):
    return render(request, 'home/palliative_success.html')

def counselling(request):
    return render(request, 'home/counseling.html')

def councontact(request):
    return render(request, 'home/counscontact.html')

#----------------------------------volunteer------------------------------------------

def volunteer(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')  # Expecting YYYY-MM-DD format
        gender = request.POST.get('gender')
        place = request.POST.get('place')
        post = request.POST.get('post')
        pin = request.POST.get('pin')
        district = request.POST.get('district')
        availability_date = request.POST.get('availability_date')
        volunteering_in = request.POST.get('volunteering_in')  # Capture program choice
        proof = request.FILES.get('proof')

        # Create Volunteer instance with status "Pending"
        volunteer_instance = Volunteer.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            dob=dob,
            gender=gender,
            place=place,
            post=post,
            pin=pin,
            district=district,
            availability_date=availability_date if availability_date else timezone.now().date(),
            volunteering_in=volunteering_in,  # Save the selected program
            status='Pending'
        )
        if proof:
            volunteer_instance.proof = proof
            volunteer_instance.save()

        messages.success(request, "Your volunteer application has been submitted successfully!")
        return redirect('volunteer_thankyou')
    
    return render(request, 'home/volunteer.html')

def volunteer_thankyou(request):
    return render(request, 'home/volunteer_thankyou.html')


@login_required
@user_passes_test(is_admin)
def manage_volunteers(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    availability = request.GET.get('availability', '')
    program = request.GET.get('program', '')

    volunteers = Volunteer.objects.all()

    if query:
        volunteers = volunteers.filter(
            Q(place__icontains=query) |
            Q(post__icontains=query) |
            Q(district__icontains=query)
        )
    if availability:
        volunteers = volunteers.filter(availability_date=availability)
    if program:
        volunteers = volunteers.filter(volunteering_in__icontains=program)
    if status:
        volunteers = volunteers.filter(status__icontains=status)

    context = {
        'volunteers': volunteers,
        'dashboard_url': 'admin_dashboard',
        'query': query,
        'status': status,
        'availability': availability,
        'program': program,
    }
    return render(request, 'manage_volunteers.html', context)


@login_required
@user_passes_test(is_admin)
def manage_events(request):
    # Retrieve and clean filter parameters
    event_type = request.GET.get('event_type', '').strip()
    location = request.GET.get('location', '').strip()
    status = request.GET.get('status', '').strip()

    # Debugging outputs
    print(f"Event Type: '{event_type}', Location: '{location}', Status: '{status}'")

    # Base queryset
    events = Event.objects.all()

    # Apply filters if present
    if event_type:
        events = events.filter(event_type__icontains=event_type)
    if location:
        events = events.filter(location__icontains=location)
    if status:
        events = events.filter(event_status__iexact=status)

    context = {
        'events': events,
        'dashboard_url': 'admin_dashboard',
        'request': request,
    }
    return render(request, 'manage_events.html', context)



@login_required
@user_passes_test(is_admin)
def update_event(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    
    if request.method == 'POST':
        event.event_type = request.POST.get('event_type', event.event_type)
        event.event_date = request.POST.get('event_date', event.event_date)
        event.description = request.POST.get('description', event.description)
        event.location = request.POST.get('location', event.location)
        event.event_status = request.POST.get('event_status', event.event_status)
        event.target_budget = request.POST.get('target_budget', event.target_budget)
        # Process other fields as needed...
        
        event.save()
        messages.success(request, 'Event updated successfully.')
        return redirect('manage_events')
    
    return render(request, 'update_events.html', {'event': event})

@login_required
@user_passes_test(is_admin)
def delete_event(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    event.delete()
    messages.success(request, 'Event deleted successfully.')
    return redirect('manage_events')



# Approve a volunteer: create a user account, send email credentials, and mark as approved.


@login_required
@user_passes_test(lambda u: u.is_staff)
def approve_volunteer(request, volunteer_id):
    volunteer_instance = get_object_or_404(Volunteer, pk=volunteer_id)
    
    if volunteer_instance.status != 'Approved':
        username = volunteer_instance.email.split('@')[0]
        random_password = get_random_string(length=8)
        
        user = User.objects.create_user(
            username=username, 
            email=volunteer_instance.email, 
            password=random_password
        )
        
        volunteer_group, created = Group.objects.get_or_create(name='Volunteers')
        user.groups.add(volunteer_group)
        
        volunteer_instance.user = user
        volunteer_instance.status = 'Approved'
        volunteer_instance.save()
        
        subject = "Volunteer Account Approved"
        message = (
            f"Hello {volunteer_instance.full_name},\n\n"
            f"Your volunteer application has been approved.\n"
            f"Your login credentials are:\n"
            f"Username: {username}\n"
            f"Password: {random_password}\n\n"
            "Please log in to your dashboard at [YOUR_LOGIN_URL].\n\n"
            "Thank you for joining our team!"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [volunteer_instance.email])
        
        messages.success(request, f"{volunteer_instance.full_name} has been approved and an email has been sent with login details.")
    else:
        messages.info(request, "This volunteer has already been approved.")
    
    return redirect('manage_volunteers')

# Volunteer dashboard – accessible only to users in the 'Volunteers' group.
@login_required
def volunteer_dashboard(request):
    if not request.user.groups.filter(name='Volunteers').exists():
        messages.error(request, "You do not have permission to access the volunteer dashboard.")
        return redirect('home')
    return render(request, 'home/volunteer_dashboard.html')


def profile(request):
    try:
        # Assuming the Volunteer record is linked to the user's email
        volunteer = Volunteer.objects.get(email=request.user.email)
    except Volunteer.DoesNotExist:
        messages.error(request, "Volunteer profile not found.")
        return redirect('volunteer_dashboard')  # Fallback if profile not found

    context = {
        'volunteer': volunteer,
    }
    return render(request, 'home/volunteer_profile.html', context)


from datetime import datetime

@login_required
def edit_volunteer_profile(request):
    try:
        # Fetch the volunteer using the logged-in user's email
        volunteer = Volunteer.objects.get(email=request.user.email)
    except Volunteer.DoesNotExist:
        messages.error(request, "Volunteer profile not found.")
        return redirect('volunteer_dashboard')

    if request.method == "POST":
        # Get form data from POST request
        volunteer.full_name = request.POST.get('full_name')
        volunteer.dob = request.POST.get('dob')
        volunteer.gender = request.POST.get('gender')
        volunteer.phone = request.POST.get('phone')
        volunteer.place = request.POST.get('place')
        volunteer.post = request.POST.get('post')
        volunteer.pin = request.POST.get('pin')
        volunteer.district = request.POST.get('district')

        # Handle availability date
        availability = request.POST.get('availability')
        if availability:
            try:
                volunteer.availability = datetime.strptime(availability, '%Y-%m-%d').date()
            except ValueError:
                volunteer.availability = None  # Handle invalid date
        
        # Handle file upload for proof
        if request.FILES.get('proof'):
            volunteer.proof = request.FILES.get('proof')
        
        # Save the updated volunteer data
        volunteer.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    context = {'volunteer': volunteer}
    return render(request, 'home/edit_volunteer_profile.html', context)



def change_password(request):
    return render(request, 'home/change_password.html')



def volunteer_view_events(request):
    # Fetch upcoming events only (where event date is in the future)
    today = date.today()
    events = Event.objects.filter(event_date__gte=today).order_by('event_date')  # Orders by upcoming events first
    
    context = {'events': events}
    return render(request, 'home/volunteer-events.html', context)


# Inline ModelForm for FieldData
class FieldDataForm(forms.ModelForm):
    class Meta:
        model = FieldData
        # We exclude the volunteer field since it will be set automatically
        fields = ['full_name', 'place', 'post', 'pin', 'district', 'email', 'details', 'proof']

def field_data_collection(request):
    if request.method == 'POST':
        # Retrieve POST data manually (using .get() with a default)
        full_name = request.POST.get('full_name', '')
        age = request.POST.get('age')  # You may need to cast to int if needed
        gender = request.POST.get('gender', '')
        phone = request.POST.get('phone', '')
        place = request.POST.get('place', '')
        post_office = request.POST.get('post', '')
        pin = request.POST.get('pin', '')
        district = request.POST.get('district', '')
        email = request.POST.get('email', '')
        details = request.POST.get('details', '')
        medical_conditions = request.POST.get('medical_conditions', '')
        family_size = request.POST.get('family_size')
        urgency_level = request.POST.get('urgency_level', '')
        additional_info = request.POST.get('additional_info', '')
        
        # Optionally convert age and family_size to integers if provided
        try:
            age = int(age) if age else None
        except ValueError:
            age = None
        try:
            family_size = int(family_size) if family_size else None
        except ValueError:
            family_size = None

        # Handle file upload for proof
        proof = request.FILES.get('proof')

        # Associate the field data with the logged-in volunteer
        try:
            volunteer_instance = Volunteer.objects.get(email=request.user.email)
        except Volunteer.DoesNotExist:
            messages.error(request, "Volunteer profile not found. Please contact support.")
            return redirect('volunteer_dashboard')

        # Create a new FieldData instance
        field_data = FieldData(
            volunteer=volunteer_instance,
            full_name=full_name,
            age=age,
            gender=gender,
            phone=phone,
            place=place,
            post=post_office,
            pin=pin,
            district=district,
            email=email,
            details=details,
            medical_conditions=medical_conditions,
            family_size=family_size,
            urgency_level=urgency_level,
            additional_info=additional_info,
            proof=proof,
            status='Pending'  # default status
        )
        
        # Optionally assign priority based on content in 'details'
        details_lower = details.lower()
        if "urgent" in details_lower:
            field_data.priority = 'High'
        elif "important" in details_lower:
            field_data.priority = 'Medium'
        else:
            field_data.priority = 'Low'

        field_data.save()
        messages.success(request, "Field data submitted successfully!")
        return redirect('field_data_collection')
    else:
        # For GET, simply render the template; if you need to pass an empty dictionary for the form fields, you can.
        return render(request, 'home/field_data_collection.html')
# #--------------------------------------------------------------------------------------------------


def blood_donation(request):
    if request.method == 'POST':
        # Retrieve form data from POST request
        full_name   = request.POST.get('full_name')
        blood_group = request.POST.get('blood_group')
        email       = request.POST.get('email')
        phone       = request.POST.get('phone')
        place       = request.POST.get('place')
        post        = request.POST.get('post')
        pin         = request.POST.get('pin')
        district    = request.POST.get('district')
        gender      = request.POST.get('gender')
        dob         = request.POST.get('dob')

        try:
            # Create a new BloodDonor record in the database
            BloodDonor.objects.create(
                full_name=full_name,
                blood_group=blood_group,
                email=email,
                phone=phone,
                place=place,
                post=post,
                pin=pin,
                district=district,
                gender=gender,
                dob=dob
            )
            messages.success(request, "Thank you for registering as a blood donor!")
            # Redirect to the same page (or to a thank-you page) after successful submission
            return redirect('blood_donation')
        except Exception as e:
            # Optionally log the error and show an error message to the user
            messages.error(request, f"An error occurred while processing your registration: {e}")

    # For GET requests, simply render the blood donation form template
    return render(request, 'home/blood_donor.html')


#--------------------------------DONATIONS----------------------------------


@login_required
def blood_donor(request):
    if request.method == 'POST':
        # Process blood donor registration details here.
        messages.success(request, "Thank you for registering as a blood donor!")
        return redirect('user_home')
    return render(request, 'blood_donor.html')



#-----------------------------------------event------------------------------
@login_required
@user_passes_test(is_admin)
def manage_events(request):
    events = Event.objects.all()  # Query all events
    context = {
        'events': events,
        'dashboard_url': 'admin_dashboard'
    }
    return render(request, 'manage_events.html', context)

def add_event(request):
    if request.method == 'POST':
        # Get data from the form
        event_type = request.POST.get('event_type')
        event_date = request.POST.get('event_date')
        description = request.POST.get('description')
        location = request.POST.get('location')
        event_status = request.POST.get('event_status')
        sponsor_details = request.POST.get('sponsor_details')
        target_budget = request.POST.get('target_budget')
        
        # Create the new event (converting target_budget to Decimal if provided)
        Event.objects.create(
            event_type=event_type,
            event_date=event_date,
            description=description,
            location=location,
            event_status=event_status,
            sponsor_details=sponsor_details,
            target_budget=Decimal(target_budget) if target_budget else Decimal('0.00')
        )

        messages.success(request, "Event added successfully!")
        
        # Conditionally redirect based on the user role:
        if request.user.is_superuser:
            return redirect('manage_events')
        else:
            return redirect('staff_manage_events')
    
    return render(request, 'add_event.html')

@login_required
def view_events(request):
    """
    Display events to users. Only Upcoming or Ongoing events are shown.
    For Upcoming events, the event_date must be today or in the future.
    """
    today = timezone.now().date()
    events = Event.objects.filter(
        Q(event_status="Ongoing") |
        Q(event_status="Upcoming", event_date__gte=today)
    )
    return render(request, 'view_events.html', {'events': events})

@login_required
def sponsor_event(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)

    # Prevent sponsorship if the event's budget is already met.
    if event.is_budget_met:
        messages.error(request, "Sponsorship for this event is already complete. Thank you for your interest!")
        return redirect('view_events')

    if request.method == 'POST':
        try:
            sponsorship_amount = Decimal(request.POST.get('sponsorship_amount'))
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid sponsorship amount.")
            return redirect('sponsor_event', event_id=event.event_id)

        # Check if the sponsorship amount exceeds the remaining budget.
        if sponsorship_amount > event.remaining_amount:
            messages.error(request, f"The amount exceeds the remaining budget of {event.remaining_amount}.")
            return redirect('sponsor_event', event_id=event.event_id)

        # Create a sponsorship record.
        Sponsorship.objects.create(
            event=event,
            user=request.user,
            sponsorship_amount=sponsorship_amount,
        )
        messages.success(request, f"Thank you for sponsoring {event.event_type}!")
        return redirect('view_events')

    context = {
        'event': event,
        'remaining_amount': event.remaining_amount,
        'target_budget': event.target_budget,
        'collected_amount': event.collected_amount,
    }
    return render(request, 'sponsor_event.html', context)



def is_admin_or_staff(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin_or_staff)
def sponsorship_details(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    sponsorships = event.sponsorships.all()
    return render(request, 'sponsorship_details.html', {'event': event, 'sponsorships': sponsorships})





#--------------------donation full-----------------------------------------

@login_required
def monetary_donation(request):
    description = ("Monetary donations help us provide direct financial assistance to those in need. "
                   "Your contributions support medical expenses, food aid, and emergency relief efforts.")
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        donation_details = request.POST.get('donation_details')
        
        try:
            amount_val = float(amount)
        except (ValueError, TypeError):
            messages.error(request, "Please enter a valid amount.")
            return redirect('monetary_donation')
        
        # Save donation details in session for later use
        request.session['monetary_donation_details'] = {
            'amount': amount_val,
            'donation_details': donation_details,
        }
        request.session.modified = True
        
        # Create a Razorpay order (amount in paise)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order_amount = int(amount_val * 100)
        order_currency = "INR"
        order_receipt = f"monetary_{uuid.uuid4().hex[:8]}"
        razorpay_order = client.order.create({
            'amount': order_amount,
            'currency': order_currency,
            'receipt': order_receipt,
            'payment_capture': 1,
        })
        
        request.session['monetary_razorpay_order'] = razorpay_order
        request.session.modified = True
        
        context = {
            'amount': amount_val,
            'razorpay_order': razorpay_order,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        }
        return render(request, 'donation/monetary_payment.html', context)
    
    return render(request, 'donation/monetory_donation.html', {'description': description})

@login_required
def monetary_receipt(request):
    donation_details = request.session.get('monetary_donation_details', {})
    razorpay_order = request.session.get('monetary_razorpay_order', {})
    
    if not donation_details or not razorpay_order:
        messages.error(request, "Donation details missing.")
        return redirect('monetary_donation')
    
    amount_val = donation_details.get('amount')
    donation_details_text = donation_details.get('donation_details')
    
    # Create the donation record with status Paid
    donation = Donation.objects.create(
        user=request.user,
        donation_type='monetary',
        amount=amount_val,
        donation_details=donation_details_text,
        quantity=None,
        status='Paid'
    )
    
    # Create a Payment record
    Payment.objects.create(
        donation=donation,
        method='Razorpay',
        status='Completed'
    )
    
    # Clear session donation data
    request.session.pop('monetary_donation_details', None)
    request.session.pop('monetary_razorpay_order', None)
    request.session.modified = True
    
    receipt_number = f"RCPT-{uuid.uuid4().hex[:8].upper()}"
    donation_date = timezone.now()
    
    context = {
        'organization_name': 'Charitable Trust Name',
        'organization_address': '123 Charity Street, City, State, ZIP',
        'organization_phone': '123-456-7890',
        'organization_email': 'info@charity.org',
        'organization_website': 'www.charity.org',
        'receipt_number': receipt_number,
        'donation_date': donation_date,
        'amount_donated': amount_val,
        'donation_method': 'Razorpay',
        'donor_name': request.user.username,
        'donor_address': '',  
        'donor_contact': '',
    }
    
    return render(request, 'donation/monetary_receipt.html', context)

def donation_category(request):
    categories = [
        {'slug': 'medical', 'name': 'Medical Expenses', 'description': 'Support medical care for those in need.'},
        {'slug': 'meals', 'name': 'Nourish the Needy', 'description': 'Provide meals to the underprivileged.'},
        {'slug': 'grocery', 'name': 'Essential Grocery Assistance', 'description': 'Offer grocery kits to families.'},
        {'slug': 'home', 'name': 'Comprehensive Home Care', 'description': 'Help with essential home care supplies.'},
    ]
    return render(request, 'donation_category.html', {'categories': categories})

@login_required
def donation_products(request, category):
    products = DonationProduct.objects.filter(category=category)
    category_titles = {
        'medical': 'Medical Expenses',
        'meals': 'Nourish the Needy',
        'grocery': 'Essential Grocery Assistance',
        'home': 'Comprehensive Home Care',
    }
    title = category_titles.get(category, 'Donations')
    return render(request, 'donation/donation_products.html', {
        'products': products,
        'title': title,
        'category': category
    })

# Dedicated donation pages
@login_required
def grocery_kit_donation(request):
    return render(request, 'donation/grocery_donation.html')

@login_required
def medical_expenses_donation(request):
    return render(request, 'donation/medical_expenses.html')

@login_required
def nourish_the_needy_donation(request):
    return render(request, 'donation/nourish_the_needy.html')

@login_required
def comprehensive_home_care_donation(request):
    return render(request, 'donation/comprehensive_home_care.html')

def other_donations(request):
    # Get the category from GET parameters or default to one, if needed.
    category = request.GET.get('category', None)
    products = DonationProduct.objects.none()
    if category:
        products = DonationProduct.objects.filter(category=category)
    context = {
        'products': products,
    }
    return render(request, 'donation/other_donations.html', context)
# ----------------------------
# Cart & Checkout Functions
# ----------------------------

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        item_name = request.POST.get('name')
        try:
            price = float(request.POST.get('price', 0))
        except ValueError:
            messages.error(request, "Invalid price.")
            return redirect('donation_category')
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        key = item_name.replace(' ', '_').lower()
        if key in cart:
            cart[key]['quantity'] += quantity
        else:
            cart[key] = {
                'name': item_name,
                'price': price,
                'quantity': quantity,
            }
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, f'"{item_name}" has been added to your cart!')
        return redirect('view_cart')
    return redirect('donation_category')

@login_required
def add_to_cart_grocery(request):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        key = 'grocery_kit'
        if key in cart:
            cart[key]['quantity'] += quantity
        else:
            cart[key] = {
                'name': 'Grocery Kit to a Patient',
                'price': 1000,
                'quantity': quantity,
                'image': '/media/groceryimg.jpeg',
            }
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, '"Grocery Kit to a Patient" has been added to your cart!')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'cart': cart})   
    return redirect('donation_category')

@login_required
def add_to_cart_medical(request):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        key = 'medical_expenses'
        if key in cart:
            cart[key]['quantity'] += quantity
        else:
            cart[key] = {
                'name': 'Medical Expenses',
                'price': 5000,
                'quantity': quantity,
                'image': '/media/medical_expenses.jpeg',
            }
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, '"Medical Expenses" donation has been added to your cart!')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'cart': cart})   
    return redirect('donation_category')

@login_required
def add_to_cart_needy(request):
    if request.method == 'POST':
        try:
            donation_amount = float(request.POST.get('donation_amount', 30))
        except ValueError:
            donation_amount = 30.0
        cart = request.session.get('cart', {})
        key = 'nourish_needy'
        if key in cart:
            cart[key]['price'] += donation_amount
            cart[key]['quantity'] += 1
        else:
            cart[key] = {
                'name': 'Nourish the Needy Donation',
                'price': donation_amount,
                'quantity': 1,
                'image': '/media/nourish_needy.jpeg',
            }
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, '"Nourish the Needy Donation" has been added to your cart!')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'cart': cart})   
    return redirect('donation_category')


@login_required
def add_to_cart_homecare(request):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        key = 'comprehensive_home_care'
        if key in cart:
            cart[key]['quantity'] += quantity
        else:
            cart[key] = {
                'name': 'Comprehensive Home Care',
                'price': 3000,
                'quantity': quantity,
                'image': '/media/comprehensive_home_care.jpeg',
            }
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, '"Comprehensive Home Care" donation has been added to your cart!')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart': cart})
    return redirect('donation_category')

@login_required
def add_to_cart_other(request):
    if request.method == 'POST':
        donation_type = request.POST.get('donation_type')
        if donation_type == 'Other':
            donation_type = request.POST.get('other_donation', 'Other')
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1
        
        cart = request.session.get('cart', {})
        key = f"other_{donation_type.replace(' ', '_').lower()}"
        if key in cart:
            cart[key]['quantity'] += quantity
        else:
            cart[key] = {
                'name': donation_type,
                'price': 0,
                'quantity': quantity,
                'image': '/media/other_default.jpeg',
            }
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, f'"{donation_type}" donation has been added to your cart!')
        return redirect('other_donations')
    return redirect('donation_category')

@login_required
def view_cart(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    for key, item in cart.items():
        item['subtotal'] = item['price'] * item['quantity']
    return render(request, 'donation/cart.html', {'cart': cart, 'total': total})

@login_required
def remove_from_cart(request, key):
    cart = request.session.get('cart', {})
    if key in cart:
        del cart[key]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, f"{key.replace('_', ' ').title()} has been removed from your cart.")
    else:
        messages.error(request, "Item not found in cart.")
    return redirect('view_cart')

@login_required
def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                item_key = key.replace('quantity_', '')
                try:
                    new_quantity = int(value)
                    if new_quantity > 0:
                        if item_key in cart:
                            cart[item_key]['quantity'] = new_quantity
                    else:
                        if item_key in cart:
                            del cart[item_key]
                except ValueError:
                    continue
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Cart updated successfully!")
    return redirect('view_cart')

@login_required
def clear_cart(request):
    request.session['cart'] = {}
    request.session.modified = True
    messages.success(request, "Cart cleared!")
    return redirect('view_cart')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty!")
        return redirect('view_cart')
    
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    donation_type_mapping = {
        'medical_expenses': 'medical',
        'nourish_needy': 'meals',
        'comprehensive_home_care': 'home',
        'grocery_kit': 'grocery',
    }
    
    # If no payment is required (total < 1)
    if total < 1:
        for key, item in cart.items():
            donation_type = donation_type_mapping.get(key, 'other') if key in donation_type_mapping else 'other'
            donation = Donation.objects.create(
                user=request.user,
                donation_type=donation_type,
                amount=item['price'] * item['quantity'],
                donation_details=item['name'],
                quantity=item['quantity'],
                status='Paid'
            )
            if donation.donation_type != 'monetary':
                Inventory.objects.create(
                    donation=donation,
                    item_name=item['name'],
                    quantity=item['quantity']
                )
        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, "Donation recorded successfully (no payment required).")
        return redirect('receipt')
    
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order_amount = int(total * 100)
    order_currency = "INR"
    order_receipt = f"receipt_{uuid.uuid4().hex[:8]}"
    razorpay_order = client.order.create({
        'amount': order_amount,
        'currency': order_currency,
        'receipt': order_receipt,
        'payment_capture': 1
    })
    
    billing = {
        'full_name': request.user.get_full_name() or '',
        'email': request.user.email or '',
    }
    request.session['billing'] = billing
    request.session.modified = True

    context = {
        'billing': billing,
        'cart': cart,
        'total': total,
        'razorpay_order': razorpay_order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'donation/payment.html', context)

@login_required
def receipt(request):
    billing = request.session.get('billing', {})
    cart = request.session.get('cart', {})

    # Build a new clean cart dictionary that only contains expected keys.
    clean_cart = {}
    for key, item in cart.items():
        if isinstance(item, dict):
            name = item.get('name')
            price = item.get('price')
            quantity = item.get('quantity') or item.get('total_quantity', 0)
            clean_cart[key] = {
                'name': name,
                'price': price,
                'quantity': quantity
            }
    cart = clean_cart

    total = sum(item['price'] * item['quantity'] for item in cart.values())
    
    receipt_number = f"RCPT-{uuid.uuid4().hex[:8].upper()}"
    donation_date = timezone.now()
    donation_type_mapping = {
        'medical_expenses': 'medical',
        'nourish_needy': 'meals',
        'comprehensive_home_care': 'home',
        'grocery_kit': 'grocery',
    }
    
    # Create Donation and Inventory records from the clean cart.
    for key, item in cart.items():
        donation_type = donation_type_mapping.get(key, 'other') if key in donation_type_mapping else 'other'
        donation = Donation.objects.create(
            user=request.user,
            donation_type=donation_type,
            amount=item['price'] * item['quantity'],
            donation_details=item['name'],
            quantity=item['quantity'],
            status='Paid'
        )
        if donation.donation_type != 'monetary':
            Inventory.objects.create(
                donation=donation,
                item_name=item['name'],
                quantity=item['quantity']
            )
    
    # Clear session data.
    request.session['cart'] = {}
    request.session['billing'] = {}
    request.session.modified = True
    
    context = {
        'organization_name': 'AKG Charitable Society',
        'organization_address': 'Kakkodi, Kozhikode, Kerala, 673611',
        'organization_phone': '7907447256',
        'organization_email': 'akgcharitable@gmail.com',
        'organization_website': 'www.charity.org',
        'receipt_number': receipt_number,
        'donation_date': donation_date,
        'amount_donated': total,
        'donation_method': 'Razorpay',
        # Use billing data if available; otherwise, fall back to the logged-in user's details.
        'donor_name': billing.get('fullname', request.user.fullname),
        'donor_email': billing.get('email', request.user.email),
        
        'donor_contact': billing.get('phone'),
    }
    
    
    
    return render(request, 'donation/receipt.html', context)


@login_required
def payment_success(request):
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        }

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed!")
            return redirect('monetary_donation')

        billing = request.session.get('billing', {})
        cart = request.session.get('cart', {})
        total = sum(item['price'] * item['quantity'] for item in cart.values())
        
        if total > 0:
            monetary_donation = Donation.objects.create(
                user=request.user,
                donation_type='monetary',
                amount=total,
                donation_details="Donation payment via Razorpay",
                quantity=1,
                status='Paid'
            )
            donation_date = monetary_donation.date_time
            Payment.objects.create(
                donation=monetary_donation,
                method='Razorpay',
                status='Completed'
            )
        else:
            donation_date = timezone.now()
        
        donation_type_mapping = {
            'medical_expenses': 'medical',
            'nourish_needy': 'meals',
            'comprehensive_home_care': 'home',
            'grocery_kit': 'grocery',
        }
        for key, item in cart.items():
            donation_type = donation_type_mapping.get(key, 'other') if key in donation_type_mapping else 'other'
            donation = Donation.objects.create(
                user=request.user,
                donation_type=donation_type,
                amount=item['price'] * item['quantity'],
                donation_details=item['name'],
                quantity=item['quantity'],
                status='Paid'
            )
            if donation.donation_type != 'monetary':
                Inventory.objects.create(
                    donation=donation,
                    item_name=item['name'],
                    quantity=item['quantity']
                )
                
        request.session['cart'] = {}
        request.session['billing'] = {}
        request.session.modified = True

        receipt_number = f"RCPT-{uuid.uuid4().hex[:8].upper()}"
        context = {
            'organization_name': 'AKG Charitable Scoeity',
            'organization_address': 'Kakkodi, Kozhikode, Kerala, 673611',
            'organization_phone': '123-456-7890',
            'organization_email': 'akgcharitable@gmail.com',
            'organization_website': 'www.charity.org',
            'receipt_number': receipt_number,
            'donation_date': donation_date,
            'amount_donated': total,
            'donation_method': 'Razorpay',
            'donor_name': billing.get('full_name'),
            'donor_address': billing.get('address'),
            'donor_contact': billing.get('phone'),
        }

        messages.success(request, "Payment successful and donation recorded!")
        return render(request, 'donation/receipt.html', context)
    
    return redirect('monetary_donation')

# ----------------------------
# Beneficiary Request Functions
# ----------------------------
# Manage Emergency Support
# A simple test for admin/staff users.admin

from datetime import date



@login_required
def submit_request(request):
    if request.method == 'POST':
        donation_category = request.POST.get('donation_category')
        details = request.POST.get('details')
        emergency_level = request.POST.get('emergency_level')
        proof = request.FILES.get('proof')
        
        # Capture disbursement method
        disbursement_method = request.POST.get('disbursement_method')
        
        # If bank transfer is selected, capture additional bank details.
                # If bank transfer is selected, capture additional bank details.
        if disbursement_method == 'bank_transfer':  # Use 'bank_transfer' to match the form option
                account_holder = request.POST.get('account_holder')
                bank_name = request.POST.get('bank_name')
                account_number = request.POST.get('account_number')
                ifsc_code = request.POST.get('ifsc_code')
        else:
                account_holder = bank_name = account_number = ifsc_code = None

        
        # Check if "on_behalf" checkbox is checked.
        on_behalf = request.POST.get('on_behalf')
        if on_behalf:
            beneficiary_name = request.POST.get('beneficiary_name')
            beneficiary_email = request.POST.get('beneficiary_email')
            beneficiary_phone = request.POST.get('beneficiary_phone')
            gender = request.POST.get('gender')
            age = request.POST.get('age')
            address = request.POST.get('address')
            place = request.POST.get('place')
            post = request.POST.get('post')
            pin = request.POST.get('pin')
            district = request.POST.get('district')
            relationship = request.POST.get('relationship')
        else:
            beneficiary_name = request.user.fullname or request.user.username
            beneficiary_email = request.user.email
            beneficiary_phone = request.user.phone
            gender = request.user.gender
            if request.user.dob:
                today = date.today()
                age = today.year - request.user.dob.year - ((today.month, today.day) < (request.user.dob.month, request.user.dob.day))
            else:
                age = None
            address = request.user.place
            place = request.user.place
            post = request.user.post
            pin = request.user.pin
            district = request.user.district
            relationship = ""
        
        other_donation_type = request.POST.get('other_donation_type')
        custom_other_donation = request.POST.get('custom_other_donation')
        
        if donation_category and details and emergency_level:
            BeneficiarySupport.objects.create(
                user=request.user,
                emergency_type=donation_category,
                details=details,
                emergency_level=emergency_level,
                proof=proof,
                status='Pending',
                beneficiary_name=beneficiary_name,
                beneficiary_email=beneficiary_email,
                beneficiary_phone=beneficiary_phone,
                gender=gender,
                age=age if age and str(age).isdigit() else None,
                address=address,
                place=place,
                post=post,
                pin=pin,
                district=district,
                relationship=relationship,
                other_donation_type=other_donation_type,
                custom_other_donation=custom_other_donation,
                disbursement_method=disbursement_method,
                account_holder=account_holder,
                bank_name=bank_name,
                account_number=account_number,
                ifsc_code=ifsc_code
            )
            messages.success(request, "Your request has been submitted.")
            return redirect('thank_you')
        else:
            error = "Please fill in all the required fields."
            return render(request, 'beneficary/submit_request.html', {'error': error})
    return render(request, 'beneficary/submit_request.html')


@login_required
def thank_you(request):
    # Render a page that informs the beneficiary that they'll be contacted soon.
    return render(request, 'beneficary/thank_you.html')


@login_required
def approve_request(request, beneficiary_id):
    req = get_object_or_404(BeneficiarySupport, beneficiary_id=beneficiary_id)
    req.approval_status = 'Approved'
    req.status = 'Approved'
    req.save()

    subject = "Your Request has been Approved"
    message = f"Dear {req.beneficiary_name},\n\nYour request has been approved."
    recipient_list = [req.beneficiary_email]

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
        messages.success(request, "Request approved and email sent.")
    except Exception as e:
        print(f"Error: {e}")  # Prints the exact error
        messages.error(request, f"Email sending failed: {e}")

    return redirect('manage_emergency_support')
@login_required
def reject_request(request, beneficiary_id):
    req = get_object_or_404(BeneficiarySupport, beneficiary_id=beneficiary_id)
    req.approval_status = 'Rejected'
    req.status = 'Rejected'
    req.save()
    
    # Send an email to the beneficiary
    subject = "Your Request has been Rejected"
    message = (
        f"Dear {req.beneficiary_name},\n\n"
        "We regret to inform you that your request for beneficiary support has been rejected. "
        "Please feel free to contact us for more information.\n\n"
        "Thank you."
    )
    recipient_list = [req.beneficiary_email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    
    messages.error(request, "Request rejected and email sent to the beneficiary.")
    return redirect('manage_emergency_support')

@login_required
def request_list(request):
    # List only the requests submitted by the logged-in user.
    requests = BeneficiarySupport.objects.filter(user=request.user)
    return render(request, 'beneficary/request_list.html', {'requests': requests})

@user_passes_test(is_admin)
def admin_request_list(request):
    # Admin view: list all requests.
    requests = BeneficiarySupport.objects.all()
    return render(request, 'beneficary/admin_request_list.html', {'requests': requests})
from django.db.models import Q

@user_passes_test(is_admin)
def manage_emergency_support(request):
    # Get filter parameters from the request
    emergency_type = request.GET.get('emergency_type')
    emergency_level = request.GET.get('emergency_level')
    payment_method = request.GET.get('payment_method')
    status = request.GET.get('status')

    # Base queryset
    emergency_requests = BeneficiarySupport.objects.all()

    # Apply filters if provided
    if emergency_type:
        emergency_requests = emergency_requests.filter(emergency_type__icontains=emergency_type)
    if emergency_level:
        emergency_requests = emergency_requests.filter(emergency_level=emergency_level)
    if payment_method:
        emergency_requests = emergency_requests.filter(disbursement_method=payment_method)
    if status:
        emergency_requests = emergency_requests.filter(status=status)

    return render(request, 'manage_emergency_support.html', {'requests': emergency_requests})

@user_passes_test(is_admin)
def update_request(request, pk):
    beneficiary_request = get_object_or_404(BeneficiarySupport, pk=pk)
    if request.method == 'POST':
        response_text = request.POST.get('response')
        status_value = request.POST.get('status')
        beneficiary_request.response = response_text
        beneficiary_request.status = status_value
        beneficiary_request.save()
        messages.success(request, "Request updated successfully.")
        return redirect('manage_emergency_support')
    return render(request, 'beneficary/update_request.html', {'request_obj': beneficiary_request})


from django.db.models import Q

@login_required
@user_passes_test(is_admin)
def urgent_requests(request):
    urgent_reqs = BeneficiarySupport.objects.filter(emergency_level="High")

    # Fetch search parameters
    assistance_type = request.GET.get('assistance_type')
    emergency_level = request.GET.get('emergency_level')
    payment_method = request.GET.get('payment_method')
    status = request.GET.get('status')

    # Apply filters based on provided search criteria
    if assistance_type:
        urgent_reqs = urgent_reqs.filter(emergency_type__icontains=assistance_type)
    if emergency_level:
        urgent_reqs = urgent_reqs.filter(emergency_level__icontains=emergency_level)
    if payment_method:
        urgent_reqs = urgent_reqs.filter(disbursement_method__icontains=payment_method)
    if status:
        urgent_reqs = urgent_reqs.filter(status__icontains=status)

    return render(request, 'beneficary/urgent_requests.html', {'requests': urgent_reqs})



# ----------------------------
# Inventory & Allocation Functions
# ----------------------------
from django.db.models import Sum, Count, Q




@login_required
@user_passes_test(is_admin)
def manage_inventory(request):
    # Define your donation types.
    # Money-based: all except 'other'
    money_based_types = ['monetary', 'medical', 'meals', 'grocery', 'home']
    donation_type_choices = dict(Donation._meta.get_field('donation_type').choices)
    
    money_summary = {}
    for d_type in money_based_types:
        donations = Donation.objects.filter(donation_type=d_type, status='Paid')
        total_amount = donations.aggregate(total=Sum('amount'))['total'] or 0
        entries_count = donations.count()
        # Calculate allocated amounts from beneficiary requests using completion_status
        allocated_sum = BeneficiarySupport.objects.filter(
            emergency_type__iexact=d_type, status='Resolved'
        ).aggregate(total_allocated=Sum('allocation_amount'))['total_allocated'] or 0

        available_amount = total_amount - allocated_sum
        
        money_summary[d_type] = {
            'donation_type_display': donation_type_choices.get(d_type, d_type),
            'total_amount': total_amount,
            'allocated_amount': allocated_sum,
            'available_amount': available_amount,
            'entries_count': entries_count,
        }
    
    # For "other" donations (in-kind), group by the sub-category.
    # We assume that for "other" donations, Inventory.item_name stores the specific sub-category.
    qs = Inventory.objects.filter(donation__donation_type='other')
    others_grouped = qs.values('item_name').annotate(
        total_quantity=Sum('quantity'),
        allocated_quantity=Sum('quantity', filter=Q(allocated=True)),
        entries_count=Count('id')
    )
    others_summary = []
    for entry in others_grouped:
        total_quantity = entry['total_quantity'] or 0
        allocated_quantity = entry['allocated_quantity'] or 0
        available_quantity = total_quantity - allocated_quantity
        others_summary.append({
            'sub_category': entry['item_name'],
            'total_quantity': total_quantity,
            'allocated_quantity': allocated_quantity,
            'available_quantity': available_quantity,
            'entries_count': entry['entries_count'],
        })
    
    # (Optionally) Fetch detailed inventory items.
    inventory_items = Inventory.objects.select_related('donation', 'allocated_to')
    
    context = {
        'money_summary': money_summary,
        'others_summary': others_summary,
        'inventory_items': inventory_items,
    }
    return render(request, 'beneficary/manage_inventory_summary.html', context)


@login_required
@user_passes_test(is_admin)
def beneficiary_requests_by_category(request, d_type):
    # Retrieve only approved requests in the given category that are still pending allocation.
    requests_qs = BeneficiarySupport.objects.filter(
        emergency_type__iexact=d_type,
        approval_status="Approved",  # Only approved requests
        status="approved"             # Excludes allocated (Resolved) ones
    )
    context = {
        'donation_category': d_type,
        'requests': requests_qs,
    }
    return render(request, 'beneficary/beneficiary_requests_by_category.html', context)

@login_required
@user_passes_test(is_admin)
def allocate_beneficiary_request(request, pk):
    req_obj = get_object_or_404(BeneficiarySupport, pk=pk)
    if request.method == 'POST':
        allocation_amount = request.POST.get('allocation_amount')
        if allocation_amount:
            try:
                allocation_amount = float(allocation_amount)
            except ValueError:
                messages.error(request, "Please enter a valid amount.")
                return redirect('allocate_beneficiary_request', pk=pk)
            req_obj.allocation_amount = allocation_amount
            # Update the correct field:
            req_obj.completion_status = "Resolved"
            req_obj.save()
            messages.success(request, "Beneficiary request allocated and marked as resolved.")
            return redirect('beneficiary_requests_by_category', d_type=req_obj.emergency_type)
        else:
            messages.error(request, "Please enter an allocation amount.")
    context = {'request_obj': req_obj}
    return render(request, 'beneficary/allocate_beneficiary_request.html', context)


@user_passes_test(lambda u: u.is_staff)
def inventory_list(request):
    inventory_items = Inventory.objects.all()
    return render(request, 'inventory_list.html', {'inventory_items': inventory_items})

@user_passes_test(lambda u: u.is_staff)
def update_inventory(request, pk):
    inventory_item = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        beneficiary_id = request.POST.get('beneficiary_id')
        if beneficiary_id:
            beneficiary = get_object_or_404(BeneficiarySupport, pk=beneficiary_id)
            inventory_item.allocated_to = beneficiary
            inventory_item.allocated = True
            inventory_item.save()
            messages.success(request, "Inventory allocated successfully.")
        else:
            messages.error(request, "Please select a beneficiary.")
        return redirect('inventory_list')
    # Only list beneficiaries that are approved and pending allocation
    beneficiaries = BeneficiarySupport.objects.filter(
        approval_status='Approved', 
        completion_status='Pending'
    )
    return render(request, 'inventory/update_inventory.html', {'inventory_item': inventory_item, 'beneficiaries': beneficiaries})


#-----------------------------------




@login_required
def goods_checkout(request):
    """
    Finalizes non-monetary (goods/in-kind) donations from the session cart.
    This view should display a summary of items and, on confirmation,
    create Donation records for each item.
    """
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty!")
        return redirect('view_cart')
    
    # You can filter the cart items by donation_type if needed.
    # Here, we assume all non-monetary items have a donation_type other than 'monetary'
    goods_items = {k: v for k, v in cart.items() if k not in ['monetary', 'grocery_kit']}

    if request.method == 'POST':
        # Optionally, retrieve additional donor details from the POST data.
        # For now, we'll just use the current user.
        for key, item in goods_items.items():
            # Determine the donation type based on the key or item data.
            # For example, if key is "medical_expenses", set donation_type accordingly.
            # You might store the actual donation type in the session item.
            donation_type = item.get('donation_type', 'other')  # default to 'other'
            # Create a Donation record.
            Donation.objects.create(
                user=request.user,
                donation_type=donation_type,
                donation_details=item.get('name', 'Goods Donation'),
                quantity=item.get('quantity'),
                # For goods donations, you might not require an amount.
                amount=item.get('price') if item.get('price') > 0 else None,
                status='Pending'
            )
        # Clear the session cart after finalization.
        request.session['cart'] = {}
        request.session.modified = True
        messages.success(request, "Thank you for your donation!")
        return redirect('user_home')
    
    # For GET requests, show a summary for confirmation.
    total_quantity = sum(item.get('quantity', 0) for item in goods_items.values())
    context = {
        'goods_items': goods_items,
        'total_quantity': total_quantity,
    }
    return render(request, 'donation/goods_checkout.html', context)


@login_required
def donor_detail(request, user_id):
    donor = get_object_or_404(User, pk=user_id)
    return render(request, 'donation/donor_detail.html', {'donor': donor})



#-------------------------------coordinator Dashboard-------------------------------------------------------

@login_required
def coordinator_dashboard(request):
    # Get the volunteer related to the logged-in user, if available
    user_volunteer = getattr(request.user, 'volunteer', None)
    
    # Get the search query from GET parameters
    search_query = request.GET.get('q', '')
    
    # Fetch all volunteers that have a valid volunteer_id (i.e. primary key)
    volunteers = Volunteer.objects.filter(volunteer_id__isnull=False)
    if search_query:
        volunteers = volunteers.filter(
            Q(district__icontains=search_query) |
            Q(place__icontains=search_query) |
            Q(post__icontains=search_query)
        )
    
    context = {
        'volunteer': user_volunteer,
        'search_query': search_query,
        'volunteers': volunteers,
    }
    return render(request, 'coordinator/coordinator_dashboard.html', context)
from django.http import HttpResponse

@login_required
def coordinator_profile(request):
    # Retrieve the staff_id from the session, set during login
    staff_id = request.session.get('staff_id')
    if not staff_id:
        return HttpResponse("Access Denied: Staff not logged in", status=403)
    
    try:
        staff = Staff.objects.get(staff_id=staff_id, role="Coordinator")
    except Staff.DoesNotExist:
        return HttpResponse("Access Denied: No Coordinator Found", status=403)
    
    return render(request, 'coordinator/coordinator_profile.html', {'staff': staff})


from django.contrib.auth import update_session_auth_hash

@login_required
def edit_coordinator_profile(request):
    staff_id = request.session.get('staff_id')
    if not staff_id:
        return HttpResponse("Access Denied", status=403)

    staff = Staff.objects.get(staff_id=staff_id)

    if request.method == "POST":
        staff.full_name = request.POST.get("full_name")
        staff.email = request.POST.get("email")
        staff.phone = request.POST.get("phone")
        staff.place = request.POST.get("place")
        staff.post = request.POST.get("post")
        staff.pin = request.POST.get("pin")
        staff.district = request.POST.get("district")
        staff.gender = request.POST.get("gender")

        staff.save()
        return redirect('coordinator_profile')  # Redirect back to profile page

    return render(request, 'coordinator/edit_profile.html', {'staff': staff})


@login_required
def change_coordinator_password(request):
    staff_id = request.session.get('staff_id')
    if not staff_id:
        return HttpResponse("Access Denied", status=403)

    staff = Staff.objects.get(staff_id=staff_id)

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not staff.user.check_password(old_password):
            return HttpResponse("Incorrect old password", status=400)

        if new_password != confirm_password:
            return HttpResponse("Passwords do not match", status=400)

        staff.user.password = make_password(new_password)
        staff.user.save()

        update_session_auth_hash(request, staff.user)  # Keep the user logged in

        return redirect('coordinator_profile')

    return render(request, 'coordinator/change_password.html')


def is_coordinator(user):
    """Check if the logged-in user is a coordinator."""
    staff = Staff.objects.filter(user=user, role__iexact='coordinator').first()
    return staff is not None

@login_required
def coordinator_manage_events(request):
    staff_id = request.session.get('staff_id')
    if not staff_id:
        return redirect('login')

    # Retrieve the staff record
    try:
        staff = Staff.objects.get(staff_id=staff_id)
    except Staff.DoesNotExist:
        return redirect('login')

    # Verify the staff role is "Coordinator"
    if staff.role.lower() != 'coordinator':
        return redirect('login')

    # Retrieve search parameters from GET request.
    event_type = request.GET.get('event_type', '')
    location = request.GET.get('location', '')
    status = request.GET.get('status', '')

    events = Event.objects.all()
    if event_type:
        events = events.filter(event_type__icontains=event_type)
    if location:
        events = events.filter(location__icontains=location)
    if status:
        events = events.filter(event_status=status)

    return render(request, 'coordinator/coordinator_manage_events.html', {'events': events})

@login_required
def coordinator_update_event(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    
    if request.method == 'POST':
        event.event_type = request.POST.get('event_type', event.event_type)
        event.event_date = request.POST.get('event_date', event.event_date)
        event.description = request.POST.get('description', event.description)
        event.location = request.POST.get('location', event.location)
        event.event_status = request.POST.get('event_status', event.event_status)
        event.target_budget = request.POST.get('target_budget', event.target_budget)
        # Process other fields as needed...
        
        event.save()
        messages.success(request, 'Event updated successfully.')
        return redirect('coordinator_manage_events')
    
    return render(request, 'coordinator/coordinator_update_event.html', {'event': event})

@login_required
def coordinator_delete_event(request, event_id):
    # Retrieve staff using session variable
    staff_id = request.session.get('staff_id')
    if not staff_id:
        return redirect('login')

    try:
        staff = Staff.objects.get(staff_id=staff_id)
    except Staff.DoesNotExist:
        return redirect('login')

    event = get_object_or_404(Event, event_id=event_id)

    # Ensure only the assigned coordinator can delete the event
    if event.coordinator != staff:
        messages.error(request, "You do not have permission to delete this event.")
        return redirect('coordinator_manage_events')

    event.delete()
    messages.success(request, 'Event deleted successfully.')
    return redirect('coordinator_manage_events')


@login_required
def coordinator_manage_volunteers(request):
    # Use session-based check instead of group-based check.
    if not request.session.get('staff_id'):
        return redirect('login')
    
    # Retrieve search parameters from GET request.
    query = request.GET.get('q', '')
    availability = request.GET.get('availability', '')
    program = request.GET.get('program', '')
    status = request.GET.get('status', '')
    
    # Start with all volunteers.
    volunteers = Volunteer.objects.all()
    
    # Filter volunteers based on search parameters.
    if query:
        volunteers = volunteers.filter(place__icontains=query)
    if availability:
        volunteers = volunteers.filter(availability_date=availability)
    if program:
        volunteers = volunteers.filter(volunteering_in__icontains=program)
    if status:
        volunteers = volunteers.filter(status=status)
    
    context = {
        'volunteers': volunteers,
        'query': query,
        'availability': availability,
        'program': program,
        'status': status,
    }
    
    # Render the coordinator template.
    return render(request, 'coordinator/coordinator_manage_volunteers.html', context)



@login_required
def coordinator_manage_palliative(request):
    # Retrieve all palliative care records from the database.
    palliative_cases = PalliativePatient.objects.all()
    return render(request, 'coordinator/coordinator_manage_palliative.html', {'palliative_cases': palliative_cases})

@login_required
def coordinator_manage_tasks(request):
    # Fetch all tasks ordered by assignment date (latest first)
    tasks = Task.objects.all().order_by('-assigned_at')
    
    # Get the selected program type from GET parameters (for volunteer filtering)
    selected_program = request.GET.get('program_type')
    volunteering_choices = Volunteer.VOLUNTEERING_CHOICES
    
    # Filter volunteers based on the selected program type, if provided
    if selected_program:
        volunteers = Volunteer.objects.filter(volunteering_in__iexact=selected_program)
    else:
        volunteers = Volunteer.objects.all()
    
    if request.method == 'POST':
        # Retrieve form data
        volunteer_id = request.POST.get('volunteer')
        task_description = request.POST.get('task_description')
        location = request.POST.get('location')
        district = request.POST.get('district')
        due_date = request.POST.get('due_date')
        materials = request.POST.get('materials', '')
        instructions = request.POST.get('instructions', '')
        status = request.POST.get('status', 'Assigned')
        priority = request.POST.get('priority', 'Medium')
        
        # Validate volunteer exists
        try:
            volunteer = Volunteer.objects.get(volunteer_id=volunteer_id)
        except Volunteer.DoesNotExist:
            messages.error(request, "Selected volunteer does not exist.")
            return redirect('coordinator_manage_tasks')
        
        # Check if the volunteer is available on the given due date
        if not volunteer.is_available_on(due_date):
            messages.error(request, "Volunteer is not available on the selected due date due to an existing assignment.")
            return redirect('coordinator_manage_tasks')
        
        # Create the new task if available
        Task.objects.create(
            volunteer=volunteer,
            task_description=task_description,
            location=location,
            district=district,
            due_date=due_date,
            materials=materials,
            instructions=instructions,
            status=status,
            priority=priority,
            assigned_at=timezone.now()
        )
        
        messages.success(request, "Task assigned successfully!")
        return redirect('coordinator_manage_tasks')
    
    context = {
        'tasks': tasks,
        'volunteers': volunteers,
        'volunteering_choices': volunteering_choices,
        'selected_program': selected_program,
    }
    return render(request, 'coordinator/coordinator_manage_tasks.html', context)


@login_required
def view_assigned_tasks_coordinator(request):
    # Fetch all assigned tasks and order them
    assigned_tasks = Task.objects.select_related('volunteer').order_by('-assigned_at')

    context = {
        'assigned_tasks': assigned_tasks
    }
    return render(request, 'coordinator/assigned_tasks_coordinator.html', context)


from django.views.decorators.http import require_POST

@login_required
@require_POST
def mark_task_complete(request, task_id):
    # Ensure that the task belongs to the logged-in volunteer.
    # Adjust the check below if you have a different permission model.
    task = get_object_or_404(Task, id=task_id, volunteer=request.user.volunteer)
    task.status = 'Completed'
    task.save()
    return JsonResponse({'status': 'success', 'new_status': task.status})

from django import forms


def search_volunteers(request):
    """Search volunteers by district, place, or post."""
    search_query = request.GET.get('q', '')
    volunteers = Volunteer.objects.all()
    if search_query:
        volunteers = volunteers.filter(
            Q(district__icontains=search_query) |
            Q(place__icontains=search_query) |
            Q(post__icontains=search_query)
        )
    context = {
        'volunteers': volunteers,
        'search_query': search_query,
    }
    return render(request, 'fielddata/volunteer_search.html', context)




def assign_field_to_volunteer(request, volunteer_id):
    """Show assignment form for a selected volunteer and process submission."""
    volunteer = get_object_or_404(Volunteer, pk=volunteer_id)
    
    if request.method == 'POST':
        responsibilities = request.POST.get('responsibilities')
        location = request.POST.get('location')
        completion_date_str = request.POST.get('completion_date')
        
        if not responsibilities or not location or not completion_date_str:
            messages.error(request, "All fields are required.")
        else:
            try:
                completion_date = datetime.strptime(completion_date_str, '%Y-%m-%d').date()
                FieldAssignment.objects.create(
                    volunteer=volunteer,
                    responsibilities=responsibilities,
                    location=location,
                    completion_date=completion_date
                )
                messages.success(request, "Field assignment created successfully.")
                return redirect('assignment_success')
            except ValueError:
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
    
    context = {
        'volunteer': volunteer,
    }
    return render(request, 'fielddata/assign_field_to_volunteer.html', context)

def assignment_success(request):
    return render(request, 'fielddata/assignment_success.html')
@login_required
def view_field_assignments_coordinator(request):
    """Display all assigned field areas with updated status."""
    assignments = FieldAssignment.objects.select_related('volunteer').order_by('-assigned_at')

    context = {
        'assignments': assignments,
    }
    return render(request, 'fielddata/view_field_assignments_coordinator.html', context)

@login_required
def mark_assignment_completed(request, assignment_id):
    """Update the status of the field assignment to completed."""
    assignment = get_object_or_404(FieldAssignment, id=assignment_id, volunteer=request.user.volunteer)

    if request.method == 'POST':
        if assignment.status != 'completed':
            assignment.status = 'completed'
            assignment.completion_date = now().date()  # Set completion date
            assignment.save()
            return JsonResponse({
                'success': True,
                'message': 'Assignment marked as completed!',
                'completed_date': assignment.completion_date.strftime('%b %d, %Y')
            })
        return JsonResponse({'success': False, 'message': 'Assignment is already completed!'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required
def view_assigned_fields(request):
    """
    Allows a volunteer (logged in user) to see their assigned field areas.
    """
    try:
        # Assuming each user has one volunteer profile linked via the OneToOneField 'user'
        volunteer = request.user.volunteer
    except AttributeError:
        messages.error(request, "No volunteer profile found for your account.")
        return redirect('home')  # Or another appropriate page

    # Get all assignments for this volunteer, most recent first
    assignments = FieldAssignment.objects.filter(volunteer=volunteer).order_by('-assigned_at')
    context = {
        'volunteer': volunteer,
        'assignments': assignments,
    }
    return render(request, 'fielddata/view_assigned_fields.html', context)


@login_required
def view_all_requests(request):
    requests = BeneficiarySupport.objects.all()  # or filter as needed
    return render(request, 'view_all_requests.html', {'requests': requests})



from itertools import groupby

@login_required
@user_passes_test(is_admin)
def manage_notifs(request):
    if request.method == 'POST':
        recipient = request.POST.get('user')
        message = request.POST.get('message')

        if message:
            # Use one timestamp for a group send
            timestamp = timezone.now()

            if recipient == "all":
                users = CustomUser.objects.all()
            elif recipient == "donors":
                users = CustomUser.objects.filter(user_type="donor")
            elif recipient == "beneficiaries":
                users = CustomUser.objects.filter(user_type="beneficiary")
            elif recipient == "volunteers":
                volunteer_user_ids = Volunteer.objects.exclude(user__isnull=True).values_list('user', flat=True)
                users = CustomUser.objects.filter(id__in=volunteer_user_ids)
            else:
                users = CustomUser.objects.none()

            notifs_to_create = [
                Notif(user=user, message=message, date_time=timestamp)
                for user in users
            ]
            Notif.objects.bulk_create(notifs_to_create)
            return redirect('manage_notifs')

    # Order notifications by user_type and then by date descending
    notifs = Notif.objects.select_related('user').order_by('user__user_type', '-date_time')
    
    # Group notifications by (user_type, message, date_time)
    grouped_notifs = []
    for key, group in groupby(notifs, key=lambda n: (n.user.user_type, n.message, n.date_time)):
        grouped_notifs.append(next(group))
    
    return render(request, 'manage_notifs.html', {
        'notifs': grouped_notifs,
    })

@login_required
@user_passes_test(is_admin)
def group_notifs(request, group):
    if group == 'donors':
        users = CustomUser.objects.filter(user_type='donor')
    elif group == 'beneficiaries':
        users = CustomUser.objects.filter(user_type='beneficiary')
    elif group == 'volunteers':
        volunteer_user_ids = Volunteer.objects.exclude(user__isnull=True).values_list('user', flat=True)
        users = CustomUser.objects.filter(id__in=volunteer_user_ids)
    else:
        users = CustomUser.objects.none()

    notifs = Notif.objects.filter(user__in=users).order_by('-date_time')
    return render(request, 'group_notifs.html', {
        'group': group,
        'notifs': notifs,
    })




@login_required
def volunteer_notifs(request):
    """Volunteers view their own notifications"""
    volunteer = get_object_or_404(Volunteer, user=request.user)
    notifs = Notif.objects.filter(user=volunteer.user).order_by('-date_time')

    return render(request, 'volunteer_notifs.html', {
        'notifs': notifs,
    })

#------------------------------------report-----------------------------------

# views.py
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Q
from .models import Donation, BeneficiarySupport
from datetime import datetime, timedelta
import io
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def monthly_report(request):
    if request.method == 'POST':
        # Get selected month and year from form
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        
        # Calculate date range
        selected_date = datetime(year, month, 1)
        next_month = selected_date.replace(day=28) + timedelta(days=4)
        last_day = next_month - timedelta(days=next_month.day)
        start_date = selected_date.date()
        end_date = last_day.date()

        # Get donations for the selected month
        donations = Donation.objects.filter(
            date_time__date__range=(start_date, end_date),
            status='Paid'
        )

        # Prepare report data for each category
        categories = ['monetary', 'medical', 'meals', 'grocery', 'home']
        report_data = []
        for category in categories:
            total = donations.filter(donation_type=category).aggregate(Sum('amount'))['amount__sum'] or 0
            allocated = BeneficiarySupport.objects.filter(
                emergency_type=category,
                status='Resolved',
                date__range=(start_date, end_date)
            ).aggregate(Sum('allocation_amount'))['allocation_amount__sum'] or 0
            report_data.append({
                'category': category,
                'total': total,
                'allocated': allocated,
                'remaining': total - allocated
            })

        # Define table_data list for the PDF table
        table_data = [
            ['Category', 'Total Donations', 'Allocated', 'Remaining']
        ]
        for item in report_data:
            table_data.append([
                item['category'].title(),
                f"₹{item['total']:,.2f}",
                f"₹{item['allocated']:,.2f}",
                f"₹{item['remaining']:,.2f}"
            ])

        # Calculate totals for summary section
        total_donations = sum(item['total'] for item in report_data)
        total_allocated = sum(item['allocated'] for item in report_data)
        total_remaining = total_donations - total_allocated

        # Generate chart and save to a BytesIO buffer with a white background
        plt.figure(figsize=(8, 3.5), dpi=100, facecolor='white')
        chart_categories = [item['category'].title() for item in report_data]
        totals = [float(item['total']) for item in report_data]
        allocated_values = [float(item['allocated']) for item in report_data]
        x = range(len(chart_categories))
        width = 0.35
        plt.bar(x, totals, width, label='Total Donations')
        plt.bar([i + width for i in x], allocated_values, width, label='Allocated')
        plt.title('Donations vs Allocations')
        plt.xticks([i + width/2 for i in x], chart_categories)
        plt.legend()
        chart_buffer = io.BytesIO()
        plt.savefig(chart_buffer, format='png', bbox_inches='tight')
        plt.close()
        chart_buffer.seek(0)

        # Create PDF buffer and build document
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch,
            topMargin=0.3*inch,
            bottomMargin=0.5*inch
        )
        
        styles = getSampleStyleSheet()
        elements = []

        # Custom Styles for header, title, etc.
        header_style = ParagraphStyle(
            name='Header',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=1
        )
        
        title_style = ParagraphStyle(
            name='Title',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=1,
            spaceAfter=12,
            textColor=colors.navy
        )

        # Header Section without logo
        header_data = [
            [
                Paragraph(
                    "<b>AKG Charitable Society</b><br/>"
                    "Kakkodi, Kozhikode, Kerala, 673611<br/>"
                    "Email: akgcharitable@gmail.com<br/>"
                    "Registration Number: KKD/CA/1698/2014<br/>"
                    "Phone: 7907447256",
                    header_style
                )
            ]
        ]
        header_table = Table(header_data, colWidths=[6*inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10)
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.2*inch))

        # Title and Period Section
        elements.append(Paragraph("MONTHLY DONATION REPORT", title_style))
        elements.append(Paragraph(
            f"<b>Period:</b> {selected_date.strftime('%B %Y')}",
            ParagraphStyle(name='Date', parent=styles['Normal'], fontSize=12, alignment=1)
        ))
        elements.append(Spacer(1, 0.3*inch))

        # Main Table displaying donation details
        # Removed grid lines to eliminate the small rectangle around cells.
        table = Table(table_data, colWidths=[1.5*inch, 1.8*inch, 1.8*inch, 1.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            # Removed the GRID line below:
            # ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

        # Add the chart image to the PDF
        elements.append(Image(chart_buffer, width=6*inch, height=2.5*inch))
        elements.append(Spacer(1, 0.2*inch))

        # Summary Section with key totals
        summary_style = ParagraphStyle(
            name='Summary',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.darkblue
        )
        summary_text = f"""
        <b>Total Donations:</b> ₹{total_donations:,.2f}<br/>
        <b>Total Allocated:</b> ₹{total_allocated:,.2f}<br/>
        <b>Total Remaining Balance:</b> ₹{total_remaining:,.2f}
        """
        elements.append(Paragraph(summary_text, summary_style))
        elements.append(Spacer(1, 0.2*inch))

        # Footer Section with generation time and signature placeholder
        footer = Paragraph(
            "Generated on: " + datetime.now().strftime("%d-%m-%Y %H:%M") + 
            " | Authorized Signature: ___________________________",
            ParagraphStyle(name='Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
        )
        elements.append(footer)

        # Build the PDF document
        doc.build(elements)
        buffer.seek(0)

        return FileResponse(buffer, as_attachment=True, filename=f"donation_report_{selected_date.strftime('%Y_%m')}.pdf")

    # GET request - show month selection form
    current_year = datetime.now().year
    years = range(current_year - 1, current_year + 10)
    return render(request, 'reports/monthly_report_form.html', {
        'years': years,
        'months': [
            (1, 'January'), (2, 'February'), (3, 'March'),
            (4, 'April'), (5, 'May'), (6, 'June'),
            (7, 'July'), (8, 'August'), (9, 'September'),
            (10, 'October'), (11, 'November'), (12, 'December')
        ]
    })
    
# from .models import Complaint

# def volunteer_send_complaint(request):
#     if request.method == "POST":
#         message_text = request.POST.get('message', '').strip()
#         if message_text:
#             Complaint.objects.create(
#                 sender=request.user,
#                 message=message_text
#             )
#             messages.success(request, "Your complaint has been submitted.")
#             return redirect('volunteer_complaint_list')
#         else:
#             messages.error(request, "Please enter your complaint message.")
#     return render(request, 'complaints/volunteer_complaint_form.html')

# def volunteer_complaint_list(request):
#     # Show only complaints from the current volunteer or admin
#     if request.user.is_staff:  # Admin can see all complaints
#         complaints = Complaint.objects.all().order_by('-created_at')
#     else:
#         complaints = Complaint.objects.filter(sender=request.user).order_by('-created_at')
#     return render(request, 'complaints/volunteer_complaint_list.html', {'complaints': complaints})


# def staff_send_complaint(request):
#     if request.method == "POST":
#         message_text = request.POST.get('message', '').strip()
#         if message_text:
#             Complaint.objects.create(
#                 sender=request.user,
#                 message=message_text
#             )
#             messages.success(request, "Your complaint has been submitted.")
#             return redirect('staff_complaint_list')
#         else:
#             messages.error(request, "Please enter your complaint message.")
#     return render(request, 'complaints/staff_complaint_form.html')

# def staff_complaint_list(request):
#     # Staff can only see their own complaints or all complaints if they are admin
#     if request.user.is_staff:  # Admin can see all complaints
#         complaints = Complaint.objects.all().order_by('-created_at')
#     else:
#         complaints = Complaint.objects.filter(sender=request.user).order_by('-created_at')
#     return render(request, 'complaints/staff_complaint_list.html', {'complaints': complaints})

# def admin_complaint_list(request):
#     # Admin sees all complaints (from both volunteers and staff)
#     complaints = Complaint.objects.all().order_by('-created_at')
#     return render(request, 'complaints/admin_complaint_list.html', {'complaints': complaints})

# def admin_reply_complaint(request, complaint_id):
#     complaint = get_object_or_404(Complaint, pk=complaint_id)
#     if request.method == "POST":
#         reply_text = request.POST.get('reply', '').strip()
#         if reply_text:
#             complaint.reply = reply_text
#             complaint.replied_at = timezone.now()
#             complaint.save()
#             messages.success(request, "Reply has been sent.")
#             return redirect('admin_complaint_list')
#         else:
#             messages.error(request, "Please enter a reply.")
#     return render(request, 'complaints/admin_complaint_reply.html', {'complaint': complaint})