from django.db import models
from django.conf import settings  # To use CustomUser
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


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


# Donation Model
class Donation(models.Model):
    donation_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    donation_type = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    donation_details = models.TextField()
    quantity = models.IntegerField(null=True, blank=True)
    date_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')])

    def __str__(self):
        return f"{self.donation_type} - {self.user.fullname}"


# Event Model
class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_type = models.CharField(max_length=100)
    event_date = models.DateField()
    description = models.TextField()
    location = models.CharField(max_length=255)
    event_status = models.CharField(max_length=50, choices=[('Upcoming', 'Upcoming'), ('Ongoing', 'Ongoing'), ('Completed', 'Completed')])
    sponsor_details = models.TextField()

    def __str__(self):
        return self.event_type


# Volunteer Model
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
    availability = models.BooleanField(default=True)
    assigned_task = models.TextField(null=True, blank=True)
    proof = models.FileField(upload_to='volunteer_proofs/', null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Approved', 'Approved')])

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


# Beneficiary Support Model
class BeneficiarySupport(models.Model):
    beneficiary_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    emergency_type = models.CharField(max_length=255)
    details = models.TextField()
    date = models.DateField(auto_now_add=True)
    response = models.TextField(null=True, blank=True)
    proof = models.FileField(upload_to='beneficiary_proofs/', null=True, blank=True)
    emergency_level = models.CharField(max_length=50, choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')])
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Resolved', 'Resolved')])

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


# Inventory Model
class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    total_quantity = models.IntegerField()
    allocated_quantity = models.IntegerField()
    beneficiary = models.ForeignKey(BeneficiarySupport, on_delete=models.CASCADE)

    def __str__(self):
        return f"Inventory - {self.donation.donation_type}"


# Field Data Model
class FieldData(models.Model):
    field_id = models.AutoField(primary_key=True)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    place = models.CharField(max_length=255)
    post = models.CharField(max_length=255)
    pin = models.CharField(max_length=10)
    district = models.CharField(max_length=255)
    email = models.EmailField()
    details = models.TextField()
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Reviewed', 'Reviewed')])
    proof = models.FileField(upload_to='field_data_proofs/', null=True, blank=True)

    def __str__(self):
        return self.full_name


# Payment Model
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


# Feedback Model
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
    role = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    dob = models.DateField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    place = models.CharField(max_length=100)
    post = models.CharField(max_length=100)
    pin = models.CharField(max_length=10)
    district = models.CharField(max_length=100)
    join_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active')

    def __str__(self):
        return f"{self.role} - {self.email}"



class ChatMessage(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"Message from {self.sender.fullname} to {self.receiver.fullname}"
    
    



