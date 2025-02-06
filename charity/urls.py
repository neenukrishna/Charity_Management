# from django.contrib import admin
# from .admin import admin_site
from django.urls import path
from . import views
from .views import user_home,profile
from .views import admin_dashboard, manage_users, manage_events, manage_volunteers, manage_staff  
from .views import register, user_login, user_logout
from .views import admin_dashboard


urlpatterns = [
    path('', views.home, name='home'),  
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-donations/', views.manage_donations, name='manage_donations'),
    path('manage-events/', views.manage_events, name='manage_events'),
    path('manage-volunteers/', views.manage_volunteers, name='manage_volunteers'),
    path('manage-staff/', views.manage_staff, name='manage_staff'),
    path('manage-blood-donors/', views.manage_blood_donors, name='manage_blood_donors'),
    path('manage-emergency-support/', views.manage_emergency_support, name='manage_emergency_support'),
    path('manage-palliative-care/', views.manage_palliative_care, name='manage_palliative_care'),
    path('manage-inventory/', views.manage_inventory, name='manage_inventory'),
    path('manage-notifications/', views.manage_notifications, name='manage_notifications'),
    path('manage-field-data/', views.manage_field_data, name='manage_field_data'),
    path('manage-feedbacks/', views.manage_feedbacks, name='manage_feedbacks'),
    path('manage-inventory/', views.manage_inventory, name='manage_inventory'),
    path('manage-notifications/', views.manage_notifications, name='manage_notifications'),
    path('manage-field-data/', views.manage_field_data, name='manage_field_data'),
    path('add-user/', views.add_user, name='add_user'),
    path('add-donation/', views.add_donation, name='add_donation'),
    path('add-blood-donor/', views.add_blood_donor, name='add_blood_donor'),
    path('add-emergency-request/', views.add_emergency_request, name='add_emergency_request'),
    path('add-palliative-care/', views.add_palliative_care, name='add_palliative_care'),
    path('add-volunteer/', views.add_volunteer, name='add_volunteer'), 
    path('add-event/', views.add_event, name='add_event'),
    path('add-inventory/', views.add_inventory, name='add_inventory'),
    path('add-notification/', views.add_notification, name='add_notification'),
    path('add-field-data/', views.add_field_data, name='add_field_data'),
    path('send-feedback-reply/<int:feedback_id>/', views.send_feedback_reply, name='send_feedback_reply'),
    path('add-staff/', views.add_staff, name='add_staff'), 
    path('chat/', views.chat_view, name='chat_view'),
    path('admin-chat/', views.admin_chat_view, name='manage_chat'),
    
    path('user-home/', views.user_home, name='user_home'),
    path('profile/', views.profile, name='profile'),
    path('view-events/', views.view_events, name='view_events'),
    path('sponsor-event/<int:event_id>/', views.sponsor_event, name='sponsor_event'),
    path('add-donation/', views.make_donation, name='make_donation'),
    path('request-emergency-support/', views.request_emergency_support, name='request_emergency_support'),
    path('register-blood-donation/', views.register_blood_donation, name='register_blood_donation'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback')

    
]


