from django.db import models
from django.conf import settings  # To use CustomUser
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Sum
from decimal import Decimal



# Custom User Model
class CustomUser(AbstractUser):
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    dob = models.DateField(null=True, blank=True)
    place = models.CharField(max_length=255)
    post = models.CharField(max_length=255)
    pin = models.CharField(max_length=10)
    district = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    user_type = models.CharField(max_length=20, choices=[('donor', 'Donor'), ('beneficiary', 'Beneficiary')])

    def __str__(self):
        return self.fullname
    
    
#----------------------------------------------------------Donation----------------------------------------------------------------

# --- Donation model for donation records (if needed) ---

# Donation type and status choices
DONATION_TYPE_CHOICES = (
    ('monetary', 'Monetary'),
    ('medical', 'Medical Expenses'),
    ('meals', 'Nourish the Needy'),
    ('grocery', 'Essential Grocery Assistance'),
    ('home', 'Comprehensive Home Care'),
    ('other', 'Other Donations'),
)

STATUS_CHOICES = (
    ('Pending', 'Pending'),
    ('Paid', 'Paid'),
    ('Failed', 'Failed'),
)

class Donation(models.Model):
    donation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    donation_type = models.CharField(
        max_length=100,
        choices=DONATION_TYPE_CHOICES,
        help_text="Select the type of donation."
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Enter the amount for monetary donations or the estimated value for in-kind donations."
    )
    donation_details = models.TextField(help_text="Enter the donation details.")
    quantity = models.IntegerField(
        null=True, blank=True,
        help_text="Enter the quantity (for non-monetary donations)."
    )
    date_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Pending',
        help_text="Donation status."
    )

    def __str__(self):
        return f"{self.get_donation_type_display()} - {self.user.username}"

    def clean(self):
        if self.donation_type == 'monetary':
            if self.amount is None:
                raise ValidationError("Amount is required for monetary donations.")
            if self.quantity:
                raise ValidationError("Quantity should not be provided for monetary donations.")
        else:
            if self.quantity is None:
                raise ValidationError("Quantity is required for non-monetary donations.")

    class Meta:
        ordering = ['-date_time']

class DonationProduct(models.Model):
    CATEGORY_CHOICES = (
        ('medical', 'Medical Expenses'),
        ('meals', 'Nourish the Needy'),
        ('grocery', 'Essential Grocery Assistance'),
        ('home', 'Comprehensive Home Care'),
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    donation_amount = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='donation_products/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name
    
class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_type = models.CharField(max_length=100)
    event_date = models.DateField()
    description = models.TextField()
    location = models.CharField(max_length=255)
    event_status = models.CharField(
        max_length=50,
        choices=[('Upcoming', 'Upcoming'), ('Ongoing', 'Ongoing'), ('Completed', 'Completed')]
    )
    target_budget = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Enter the target budget amount for sponsorship",
        default=0.00
    )
    sponsor_details = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.event_type

    @property
    def collected_amount(self):
        """Returns the total sponsorship amount collected for this event."""
        total = self.sponsorships.aggregate(total=Sum('sponsorship_amount'))['total']
        return total if total is not None else Decimal('0.00')

    @property
    def remaining_amount(self):
        """Returns the remaining amount needed to meet the target budget."""
        remaining = self.target_budget - self.collected_amount
        return remaining if remaining > 0 else Decimal('0.00')

    @property
    def is_budget_met(self):
        """Returns True if the collected sponsorships meet or exceed the target budget."""
        return self.collected_amount >= self.target_budget

class Sponsorship(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sponsorships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sponsorship_amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} sponsored {self.event.event_type} with {self.sponsorship_amount}"
    

class Volunteer(models.Model):
    volunteer_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    place = models.CharField(max_length=255)
    post = models.CharField(max_length=255)
    pin = models.CharField(max_length=10)
    district = models.CharField(max_length=255)
    availability_date = models.DateField(default=timezone.now)
    
    VOLUNTEERING_CHOICES = [
        ('HWH', 'Hospital Without Hunger'),
        ('EGA', 'Essential Grocery Assistance'),
        ('CHC', 'Comprehensive Home Care'),
        ('BAS', 'Beneficiary Aid & Support'),
        ('PCP', 'Palliative Care Program'),
        ('GC', 'Guidance & Counseling'),
        ('OTH', 'Others'),
    ]
    volunteering_in = models.CharField(max_length=20, choices=VOLUNTEERING_CHOICES, default='OTH')
    assigned_task = models.TextField(null=True, blank=True)
    proof = models.FileField(upload_to='volunteer_proofs/', null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.full_name


# Blood Donor Model
class BloodDonor(models.Model):
    donor_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255)
    blood_group = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    place = models.CharField(max_length=255)
    post = models.CharField(max_length=255)
    pin = models.CharField(max_length=10)
    district = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    dob = models.DateField()

    def __str__(self):
        return f"{self.full_name} ({self.blood_group})"

class BeneficiarySupport(models.Model):
    beneficiary_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Beneficiary details
    beneficiary_name = models.CharField(max_length=255, blank=True, null=True)
    beneficiary_email = models.EmailField(blank=True, null=True)
    beneficiary_phone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    place = models.CharField(max_length=255, blank=True, null=True)
    post = models.CharField(max_length=255, blank=True, null=True)
    pin = models.CharField(max_length=10, blank=True, null=True)
    district = models.CharField(max_length=255, blank=True, null=True)
    relationship = models.CharField(max_length=255, blank=True, null=True)
    
    # Request details
    emergency_type = models.CharField(max_length=255)
    details = models.TextField()
    date = models.DateField(auto_now_add=True)
    response = models.TextField(null=True, blank=True)
    proof = models.FileField(upload_to='beneficiary_proofs/', null=True, blank=True)
    emergency_level = models.CharField(
        max_length=50, 
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')]
    )
    status = models.CharField(
        max_length=50, 
        choices=[('Pending', 'Pending'), ('Resolved', 'Resolved')],
        default='Pending'
    )
    
    # Additional Assistance Details
    other_donation_type = models.CharField(max_length=255, blank=True, null=True)
    custom_other_donation = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.emergency_type
    
# Palliative Care Model
class PalliativeCare(models.Model):
    palliative_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    date = models.DateField()
    needs = models.TextField()
    status = models.CharField(max_length=50, choices=[('Ongoing', 'Ongoing'), ('Completed', 'Completed')])

    def __str__(self):
        return f"Palliative Care - {self.user.fullname}"


class Inventory(models.Model):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    item_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    allocated = models.BooleanField(default=False)
    allocated_to = models.ForeignKey(BeneficiarySupport, null=True, blank=True, on_delete=models.SET_NULL)
    date_received = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_name} ({self.quantity})"
    
    

class FieldData(models.Model):
    field_id = models.AutoField(primary_key=True)
    volunteer = models.ForeignKey('Volunteer', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    post = models.CharField(max_length=255)
    pin = models.CharField(max_length=10)
    district = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    details = models.TextField()
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Reviewed', 'Reviewed')])
    proof = models.FileField(upload_to='field_data_proofs/', null=True, blank=True)
    # New field for priority
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Low')

    def __str__(self):
        return self.full_name

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Completed', 'Completed')])

    def __str__(self):
        return f"Payment - {self.donation.donation_type}"

# Notification Model
class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comments = models.TextField()
    reply = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Feedback - {self.user.fullname}"
    
class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    dob = models.DateField()
    gender = models.CharField(
        max_length=10, 
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    )
    place = models.CharField(max_length=100)
    post = models.CharField(max_length=100)
    pin = models.CharField(max_length=10)
    district = models.CharField(max_length=100)
    join_date = models.DateField()
    password = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20, 
        choices=[('Active', 'Active'), ('Inactive', 'Inactive')], 
        default='Active'
    )

    def __str__(self):
        return f"{self.role} - {self.email}"  # Removed the trailing comma




class ChatMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"Message from {self.sender.fullname} to {self.receiver.fullname}"
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
    
    
    

    
    



