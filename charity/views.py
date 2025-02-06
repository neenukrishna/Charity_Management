from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import Donation,Event,Volunteer,BloodDonor, BeneficiarySupport, PalliativeCare, Inventory, Notification, FieldData, Feedback,Inventory, Notification, FieldData,Staff
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import ChatMessage, CustomUser
from django.contrib import messages

def home(request):
    return render(request, 'home.html')


@login_required
def user_home(request):
    return render(request, 'user_home.html')

@login_required
def profile(request):
    return render(request, 'profile.html')

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

# User Login View (Without Forms)
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect admin users to the custom admin dashboard
            if user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('user_home')
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'login.html')

# User Logout View
def user_logout(request):
    logout(request)
    return redirect('login')

# Helper function to check if a user is an admin (superuser)
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


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
def manage_events(request):
    events = Event.objects.all()  # Query all events
    return render(request, 'manage_events.html', {'events': events})

@login_required
@user_passes_test(is_admin)
def manage_volunteers(request):
    volunteers = Volunteer.objects.all()  # Query all volunteers
    return render(request, 'manage_volunteers.html', {'volunteers': volunteers})

@login_required
@user_passes_test(is_admin)
def manage_staff(request):
    staff_members = CustomUser.objects.filter(user_type='staff')  # Query only staff users
    return render(request, 'manage_staff.html', {'staff_members': staff_members})


# Manage Blood Donors
@login_required
@user_passes_test(is_admin)
def manage_blood_donors(request):
    donors = BloodDonor.objects.all()
    return render(request, 'manage_blood_donors.html', {'donors': donors})

# Manage Emergency Support
@login_required
@user_passes_test(is_admin)
def manage_emergency_support(request):
    emergency_requests = BeneficiarySupport.objects.all()
    return render(request, 'manage_emergency_support.html', {'emergency_requests': emergency_requests})

# Manage Palliative Care
@login_required
@user_passes_test(is_admin)
def manage_palliative_care(request):
    palliative_cases = PalliativeCare.objects.all()
    return render(request, 'manage_palliative_care.html', {'palliative_cases': palliative_cases})

# Manage Resources & Inventory
@login_required
@user_passes_test(is_admin)
def manage_inventory(request):
    inventory_items = Inventory.objects.all()
    return render(request, 'manage_inventory.html', {'inventory_items': inventory_items})

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
@login_required
@user_passes_test(is_admin)
def manage_inventory(request):
    inventory_items = Inventory.objects.all()
    return render(request, 'manage_inventory.html', {'inventory_items': inventory_items})

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




#ADD FUNCTIONS




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



@login_required
@user_passes_test(is_admin)
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



@login_required
@user_passes_test(is_admin)
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
        availability = request.POST.get('availability') == 'on'
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
            availability=availability,
            assigned_task=assigned_task,
            proof=proof,
            status=status
        )

        messages.success(request, "Volunteer added successfully!")
        return redirect('manage_volunteers')  # Redirect to manage volunteers page
    
    return render(request, 'add_volunteer.html')  # Render the form for GET request


@login_required
@user_passes_test(is_admin)
def add_event(request):
    if request.method == 'POST':
        # Get data from the form
        event_type = request.POST.get('event_type')
        event_date = request.POST.get('event_date')
        description = request.POST.get('description')
        location = request.POST.get('location')
        event_status = request.POST.get('event_status')
        sponsor_details = request.POST.get('sponsor_details')

        # Create the new event
        Event.objects.create(
            event_type=event_type,
            event_date=event_date,
            description=description,
            location=location,
            event_status=event_status,
            sponsor_details=sponsor_details
        )

        messages.success(request, "Event added successfully!")
        return redirect('manage_events')  # Redirect to manage events page
    
    return render(request, 'add_event.html')  # Render the form for GET request


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


@login_required
@user_passes_test(is_admin)
def add_staff(request):
    if request.method == 'POST':
        # Get data from the form
        role = request.POST.get('role')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        place = request.POST.get('place')
        post = request.POST.get('post')
        pin = request.POST.get('pin')
        district = request.POST.get('district')
        join_date = request.POST.get('join_date')
        status = request.POST.get('status')

        # Create the new staff record
        Staff.objects.create(
            role=role,
            email=email,
            phone=phone,
            dob=dob,
            gender=gender,
            place=place,
            post=post,
            pin=pin,
            district=district,
            join_date=join_date,
            status=status
        )

        messages.success(request, "Staff added successfully!")
        return redirect('manage_staff')  # Redirect to manage staff page
    
    return render(request, 'add_staff.html')  # Render the form for GET request



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
def view_events(request):
    """
    View to display events added by admin or staff.
    Only upcoming or ongoing events are shown.
    """
    events = Event.objects.filter(event_status__in=['Upcoming', 'Ongoing'])
    return render(request, 'view_events.html', {'events': events})

@login_required
def sponsor_event(request, event_id):
    """
    View to handle a user expressing sponsorship interest.
    For simplicity, this example simply shows a form to confirm sponsorship.
    In a real-world scenario, you might record additional sponsorship details.
    """
    event = get_object_or_404(Event, event_id=event_id)
    
    if request.method == 'POST':
        # Here, you could capture sponsorship details (e.g., amount) if needed.
        sponsorship_amount = request.POST.get('sponsorship_amount')
        # For now, we just display a success message.
        messages.success(request, f"You have expressed interest to sponsor the event '{event.event_type}'.")
        return redirect('view_events')
    
    return render(request, 'sponsor_event.html', {'event': event})



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
    
    return render(request, 'add_donation.html')




@login_required
def request_emergency_support(request):
    if request.method == 'POST':
        emergency_type = request.POST.get('emergency_type')
        details = request.POST.get('details')
        # You may also let the user choose an emergency level, but for now we set a default.
        emergency_level = request.POST.get('emergency_level', 'High')
        status = 'Pending'  # New requests start as Pending

        # Create the emergency support request
        BeneficiarySupport.objects.create(
            user=request.user,
            emergency_type=emergency_type,
            details=details,
            emergency_level=emergency_level,
            status=status
        )
        messages.success(request, "Your emergency support request has been submitted.")
        return redirect('user_home')
    
    return render(request, 'request_emergency_support.html')


def register_blood_donation(request):
    return render(request, 'register_blood_donation.html')


def submit_feedback(request):
    if request.method == "POST":
        # Process feedback form
        pass
    return render(request, 'submit_feedback.html')