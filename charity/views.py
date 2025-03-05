from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser,FieldData, Volunteer
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Donation,Event,Volunteer,BloodDonor,Payment, BeneficiarySupport, PalliativeCare, Inventory, Notification, FieldData, Feedback,Inventory, Notification, FieldData,Staff,Sponsorship,DonationProduct,Contact
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




User = get_user_model()

# Helper function to check if a user is an admin (superuser)
def is_admin(user):
    return user.is_staff or user.is_superuser


#---------------------------------ADMIN USER DASHBOARD--------------------------------------------------------------------------------
def home(request):
    feedbacks = Feedback.objects.order_by('-date')[:6]
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
    feedbacks = Feedback.objects.filter(user=request.user).order_by('-date')
    context = {
        'donations': donations,
        'beneficiary_requests': beneficiary_requests,
        'feedbacks': feedbacks,
    }
    return render(request, 'home/dashboard.html', context)

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

def staff_dashboard(request):
    if 'staff_id' in request.session:
        return render(request, 'staff_dashboard.html', {'staff_name': request.session['staff_name']})
    return redirect('user_login')

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')



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
                return redirect('staff_dashboard')  # Redirect staff to dashboard
            else:
                messages.error(request, "Invalid email or password!")
        except Staff.DoesNotExist:
            # Not a staff member; check if it's a normal user (volunteer or other)
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_dashboard')
                elif user.groups.filter(name='Volunteers').exists():
                    # Redirect volunteer users to their dashboard
                    return redirect('volunteer_dashboard')
                else:
                    return redirect('user_home')
            else:
                messages.error(request, "Invalid username or password!")

    return render(request, 'login.html')

# User Logout View
def user_logout(request):
    logout(request)
    return redirect('login')


#---------------------------------MANAGE SECTION--------------------------------------------------------------------------------


@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = CustomUser.objects.all()
    return render(request, 'manage_users.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def manage_donations(request):
    donations = Donation.objects.all()
    return render(request, 'manage_donations.html', {'donations': donations})


@login_required
@user_passes_test(is_admin)
def manage_volunteers(request):
    volunteers = Volunteer.objects.all()  # Query all volunteers
    return render(request, 'manage_volunteers.html', {'volunteers': volunteers})

@login_required
@user_passes_test(is_admin)
def manage_staff(request):
    # Order by staff_id instead of id
    staff_members = Staff.objects.all().order_by('-staff_id')
    return render(request, 'manage_staff.html', {'staff_members': staff_members})

# Manage Blood Donors

def manage_blood_donors(request):
    donors = BloodDonor.objects.all()
    return render(request, 'manage_blood_donors.html', {'donors': donors})



# Manage Palliative Care
@login_required
@user_passes_test(is_admin)
def manage_palliative_care(request):
    palliative_cases = PalliativeCare.objects.all()
    return render(request, 'manage_palliative_care.html', {'palliative_cases': palliative_cases})

# Manage Resources & Inventory
# @login_required
# @user_passes_test(is_admin)



# Manage Notifications
@login_required
@user_passes_test(is_admin)
def manage_notifications(request):
    notifications = Notification.objects.all()
    return render(request, 'manage_notifications.html', {'notifications': notifications})

# Manage Field Data Collection
@login_required
@user_passes_test(is_admin)
def manage_field_data(request):
    field_data_entries = FieldData.objects.all()
    return render(request, 'manage_field_data.html', {'field_data_entries': field_data_entries})

# Manage Feedbacks
@login_required
@user_passes_test(is_admin)
def manage_feedbacks(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'manage_feedbacks.html', {'feedbacks': feedbacks})



# Manage Resources & Inventory
# @login_required
# @user_passes_test(is_admin)
# def manage_inventory(request):
#     inventory_items = Inventory.objects.all()
#     return render(request, 'manage_inventory.html', {'inventory_items': inventory_items})

# Manage Notifications
@login_required
@user_passes_test(is_admin)
def manage_notifications(request):
    notifications = Notification.objects.all()
    return render(request, 'manage_notifications.html', {'notifications': notifications})

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

@login_required
@user_passes_test(is_admin)
def add_notification(request):
    if request.method == 'POST':
        # Get data from the form
        user_id = request.POST.get('user_id')
        message = request.POST.get('message')

        user = CustomUser.objects.get(id=user_id)

        # Create the new notification
        Notification.objects.create(
            user=user,
            message=message
        )

        messages.success(request, "Notification added successfully!")
        return redirect('manage_notifications')  # Redirect to manage notifications page
    
    # Get all users to display in the form
    users = CustomUser.objects.all()
    return render(request, 'add_notification.html', {'users': users})



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
def manage_feedback(request):
    feedbacks = Feedback.objects.all()
    return render(request, 'manage_feedback.html', {'feedbacks': feedbacks})

@login_required
@user_passes_test(is_admin)
def send_feedback_reply(request, feedback_id):
    feedback = get_object_or_404(Feedback, feedback_id=feedback_id)

    if request.method == 'POST':
        reply = request.POST.get('reply')
        feedback.reply = reply
        feedback.save()
        messages.success(request, "Reply sent successfully!")
        return redirect('manage_feedback')

    return redirect('manage_feedback')
 # Make sure this is the correct model
 
 
 #------------------------------------------ADD STAFF------------------------------------------

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
        
        # Extract and compare passwords
        raw_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        # Validate that the passwords match
        if raw_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "add_staff.html")
        
        # Hash the raw password using Django's built-in function
        hashed_password = make_password(raw_password)
        
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
    users = CustomUser.objects.exclude(is_superuser=True)  # Get all users except admin
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
        # (You may need additional logic here, e.g., validations, saving to the database, etc.)
        
        messages.success(request, "Thank you for your donation!")
        return redirect('user_home')  # Or wherever you want to redirect after donation.
    
    return render(request, 'donation.html')




# @login_required
# def request_emergency_support(request):
#     if request.method == 'POST':
#         emergency_type = request.POST.get('emergency_type')
#         details = request.POST.get('details')
#         # You may also let the user choose an emergency level, but for now we set a default.
#         emergency_level = request.POST.get('emergency_level', 'High')
#         status = 'Pending'  # New requests start as Pending

#         # Create the emergency support request
#         BeneficiarySupport.objects.create(
#             user=request.user,
#             emergency_type=emergency_type,
#             details=details,
#             emergency_level=emergency_level,
#             status=status
#         )
#         messages.success(request, "Your emergency support request has been submitted.")
#         return redirect('user_home')
    
#     return render(request, 'request_emergency_support.html')


def register_blood_donation(request):
    return render(request, 'register_blood_donation.html')


def submit_feedback(request):
    if request.method == "POST":
        # Process feedback form
        pass
    return render(request, 'submit_feedback.html')



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

# Update Profile View
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
        # Update additional fields as needed...
        staff_member.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('staff/staff_profile')
    return render(request, 'staff/update_staff.html', {'staff_member': staff_member})

# Change Password View
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
        if new_password != confirm_password:
            messages.error(request, "New password and confirm password do not match.")
            return redirect('change_password_staff')
        if not check_password(old_password, staff_member.password):
            messages.error(request, "Old password is incorrect.")
            return redirect('change_password_staff')
        staff_member.password = make_password(new_password)
        staff_member.save()
        messages.success(request, "Password changed successfully!")
        return redirect('staff_profile')
    return render(request, 'staff/change_password_staff.html', {'staff_member': staff_member})


def staff_events(request):
    # Check for your custom session key
    if 'staff_id' not in request.session:
        return redirect("login")
    
    events = Event.objects.all()  # Or filter as needed
    return render(request, 'manage_events.html', {'events': events})


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

def counselling(request):
    return render(request, 'home/counseling.html')

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

# Only staff (admin) users can manage volunteers.
@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_volunteers(request):
    volunteers = Volunteer.objects.all()  # List all applications
    return render(request, 'manage_volunteers.html', {'volunteers': volunteers})

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


# charity/views.py
def assigned_tasks(request):
    # Retrieve tasks for the volunteer here.
    # For now, we use a simple placeholder.
    return render(request, 'home/assigned_tasks.html')

# def profile(request):
#     return render(request, 'profile.html')

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

def change_password(request):
    return render(request, 'home/change_password.html')

def view_events(request):
    return render(request, 'view_events.html')


# Inline ModelForm for FieldData
class FieldDataForm(forms.ModelForm):
    class Meta:
        model = FieldData
        # We exclude the volunteer field since it will be set automatically
        fields = ['full_name', 'place', 'post', 'pin', 'district', 'email', 'details', 'proof']

def field_data_collection(request):
    if request.method == 'POST':
        form = FieldDataForm(request.POST, request.FILES)
        if form.is_valid():
            field_data = form.save(commit=False)
            # Associate the field data with the logged-in volunteer
            try:
                # This assumes the logged-in user's email corresponds to a Volunteer record
                volunteer_instance = Volunteer.objects.get(email=request.user.email)
            except Volunteer.DoesNotExist:
                messages.error(request, "Volunteer profile not found. Please contact support.")
                return redirect('volunteer_dashboard')
            field_data.volunteer = volunteer_instance
            # Set default status
            field_data.status = 'Pending'
            # Optionally assign priority based on content in 'details'
            details_lower = field_data.details.lower()
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
        form = FieldDataForm()
    return render(request, 'home/field_data_collection.html', {'form': form})

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
    return render(request, 'manage_events.html', {'events': events})

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
            return redirect('staff_events')
    
    return render(request, 'add_event.html')

@login_required
def view_events(request):
    """
    Display events to users. Only Upcoming or Ongoing events are shown.
    """
    events = Event.objects.filter(event_status__in=['Upcoming', 'Ongoing'])
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

@login_required
def other_donations(request):
    return render(request, 'donation/other_donations.html')

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
        return redirect('grocery_kit_donation')
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
        return redirect('medical_expenses_donation')
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
        return redirect('nourish_the_needy_donation')
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
        return redirect('comprehensive_home_care_donation')
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
            # Use 'quantity' if present; otherwise, use 'total_quantity' (or 0 if not available).
            quantity = item.get('quantity')
            if quantity is None:
                quantity = item.get('total_quantity', 0)
            clean_cart[key] = {
                'name': name,
                'price': price,
                'quantity': quantity
            }
    # Replace the original cart with the clean cart.
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
        # For non-monetary donations, create an Inventory record.
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
        'organization_name': 'Charitable Trust Name',
        'organization_address': '123 Charity Street, City, State, ZIP',
        'organization_phone': '123-456-7890',
        'organization_email': 'info@charity.org',
        'organization_website': 'www.charity.org',
        'receipt_number': receipt_number,
        'donation_date': donation_date,
        'amount_donated': total,
        'donation_method': 'Razorpay',
        'donor_name': billing.get('full_name'),
        'donor_address': billing.get('address'),
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
            'organization_name': 'Charitable Trust Name',
            'organization_address': '123 Charity Street, City, State, ZIP',
            'organization_phone': '123-456-7890',
            'organization_email': 'info@charity.org',
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
# A simple test for admin/staff users.
def is_admin(user):
    return user.is_staff
from datetime import date


@login_required
def submit_request(request):
    if request.method == 'POST':
        donation_category = request.POST.get('donation_category')
        details = request.POST.get('details')
        emergency_level = request.POST.get('emergency_level')
        proof = request.FILES.get('proof')

        # Check if "on_behalf" checkbox is checked.
        on_behalf = request.POST.get('on_behalf')
        if on_behalf:
            # When submitting on someone else's behalf, use form values.
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
            # When not on behalf, use the logged-in user's details from the CustomUser model.
            beneficiary_name = request.user.fullname or request.user.username
            beneficiary_email = request.user.email
            beneficiary_phone = request.user.phone
            gender = request.user.gender

            # Compute age from dob if available.
            if request.user.dob:
                today = date.today()
                age = today.year - request.user.dob.year - ((today.month, today.day) < (request.user.dob.month, request.user.dob.day))
            else:
                age = None

            # Use address details from the user profile.
            address = request.user.place  # If you have a separate street address field, use it here.
            place = request.user.place
            post = request.user.post
            pin = request.user.pin
            district = request.user.district
            relationship = ""  # No relationship is needed in this case.

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
                custom_other_donation=custom_other_donation
            )
            messages.success(request, "Your request has been submitted.")
            return redirect('request_list')
        else:
            error = "Please fill in all the required fields."
            return render(request, 'beneficary/submit_request.html', {'error': error})
    return render(request, 'beneficary/submit_request.html')
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

@user_passes_test(is_admin)
def manage_emergency_support(request):
    # Another admin view for managing emergency support requests.
    emergency_requests = BeneficiarySupport.objects.all()
    # Pass the context variable as 'requests' so the template can iterate correctly.
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




@login_required
@user_passes_test(is_admin)
def urgent_requests(request):
    urgent_reqs = BeneficiarySupport.objects.filter(emergency_level="High")
    return render(request, 'beneficary/urgent_requests.html', {'requests': urgent_reqs})

# ----------------------------
# Inventory & Allocation Functions
# ----------------------------

from django.db.models import Sum, Count,Q
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
        # For money-based categories, we can calculate allocated amounts from beneficiary requests.
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
def beneficiary_requests_by_category(request, category):
    # For money-based types, category might be like 'medical', etc.
    # For other, category is the sub-category (i.e., the value in Inventory.item_name).
    # Adjust filtering logic as needed.
    requests_qs = BeneficiarySupport.objects.filter(emergency_type__iexact=category, status='Pending')
    context = {
        'donation_category': category,
        'requests': requests_qs,
    }
    return render(request, 'beneficary/beneficiary_requests_by_category.html', context)
@login_required
@user_passes_test(is_admin)
def allocate_beneficiary_request(request, pk):
    # Allocate a single beneficiary request.
    req_obj = get_object_or_404(BeneficiarySupport, pk=pk)
    if request.method == 'POST':
        # Get the allocation amount from the form.
        allocation_amount = request.POST.get('allocation_amount')
        if allocation_amount:
            try:
                allocation_amount = float(allocation_amount)
            except ValueError:
                messages.error(request, "Please enter a valid amount.")
                return redirect('allocate_beneficiary_request', pk=pk)
            req_obj.allocation_amount = allocation_amount
            req_obj.status = 'Resolved'
            req_obj.save()
            messages.success(request, "Beneficiary request allocated successfully.")
            # Redirect back to the list for the same category.
            return redirect('allocate_by_category', d_type=req_obj.emergency_type)
        else:
            messages.error(request, "Please enter an allocation amount.")
    context = {
        'request_obj': req_obj
    }
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
    beneficiaries = BeneficiarySupport.objects.filter(status='Pending')
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









