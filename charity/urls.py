# from django.contrib import admin
# from .admin import admin_site
from django.urls import path
from . import views
from .views import user_home,profile
from .views import admin_dashboard, manage_users, manage_events, manage_volunteers, manage_staff,hospital_without_hunger,volunteer,volunteer_thankyou
from .views import register, user_login, user_logout
from .views import admin_dashboard
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views



urlpatterns = [
    
    #ADMIN URLS
    path('', views.home, name='home'),  
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-donations/', views.manage_donations, name='manage_donations'),
    path('manage-events/', views.manage_events, name='manage_events'),
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
    path('add-inventory/', views.add_inventory, name='add_inventory'),
    path('add-notification/', views.add_notification, name='add_notification'),
    path('add-field-data/', views.add_field_data, name='add_field_data'),
    path('send-feedback-reply/<int:feedback_id>/', views.send_feedback_reply, name='send_feedback_reply'),
    path('add-staff/', views.add_staff, name='add_staff'), 
    path('chat/', views.chat_view, name='chat_view'),
    path('admin-chat/', views.admin_chat_view, name='manage_chat'),
    
    
    #USER URLS
    path('user-home/', views.user_home, name='user_home'),
    path('profile/', views.profile, name='profile'),
    path('donation/', views.make_donation, name='make_donation'),
    path('request-emergency-support/', views.request_emergency_support, name='request_emergency_support'),
    path('register-blood-donation/', views.register_blood_donation, name='register_blood_donation'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    
    #STAFF URLS
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/profile-staff/', views.staff_profile, name='staff_profile'),
    path('staff/update-staff/', views.update_profile, name='update_profile'),
    path('staff/change-password-staff/', views.change_password, name='change_password'),
    path('staff/<int:staff_id>/', views.staff_profile, name='staff_profile'),
    
    
    #HOME PAGE U
    path('meal/', views.hospital_without_hunger, name='hospital_without_hunger'),
    path('grocery/', views.grocery_assistance, name='grocery_assistance'),
    path('cancer_patient/', views.cancer_patient, name='cancer_patient'),
    path('beneficary_aid/', views.beneficary_aid, name='beneficary_aid'),
    path('palliative_program/',views.palliative_program,name='palliative_program'),
    path('counseling/',views.counselling,name='counseling'),
    path('blood-donor/', views.blood_donation, name='blood_donation'),

    
    path('volunteer/', views.volunteer, name='volunteer'),
    path('volunteer/thank-you/', views.volunteer_thankyou, name='volunteer_thankyou'),
    path('manage-volunteers/approve/<int:volunteer_id>/', views.approve_volunteer, name='approve_volunteer'),
    path('volunteer_dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('manage-volunteers/', views.manage_volunteers, name='manage_volunteers'),
    path('add-volunteer/', views.add_volunteer, name='add_volunteer'), 
    path('assigned_tasks/', views.assigned_tasks, name='assigned_tasks'),
    path('volunteer_profile/', views.profile, name='profile'),
    path('change_password/', auth_views.PasswordChangeView.as_view(
         template_name='home/change_password.html',
         success_url='/change_password_done/'
    ), name='change_password'),
    path('change_password_done/', auth_views.PasswordChangeDoneView.as_view(
         template_name='home/change_password_done.html'
    ), name='change_password_done'),    path('view_events/', views.view_events, name='view_events'),
    path('field_data_collection/', views.field_data_collection, name='field_data_collection'),
    


    
    
    
    # path('donation-category/', views.donation_categories, name='donation_categories'),
    # path('donation/monetory-donation/', views.monetary_donation, name='monetary_donation'),
    # path('donation/monetary-submit/', views.submit_monetary_donation, name='submit_monetary_donation'),
    
    #EVENT URLS
    path('manage-events/', views.manage_events, name='manage_events'),
    path('add-event/', views.add_event, name='add_event'),
    path('view-events/', views.view_events, name='view_events'),
    path('sponsor-event/<int:event_id>/', views.sponsor_event, name='sponsor_event'),
    path('sponsorship-details/<int:event_id>/', views.sponsorship_details, name='sponsorship_details'),
    path('staff-events/', views.staff_events, name='staff_events'),
    
    
    
    
    
    
    #donations
    path('donation/monetory_donation/', views.monetary_donation, name='monetary_donation'),
    path('donation/monetary_submit/', views.submit_monetary_donation, name='submit_monetary_donation'),
    
    
    path('donation/blood_donor/', views.blood_donor, name='blood_donor'),
    path('donation-category/', views.donation_category, name='donation_category'),
    path('donation/products/<str:category>/', views.donation_products, name='donation_products'),
    path('donation/grocery-donation/', views.grocery_kit_donation, name='grocery_kit_donation'),
    path('donation/medical-expenses/', views.medical_expenses_donation, name='medical_expenses_donation'),
    
    # Cart Management
    path('donation/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('donation/add-to-cart-grocery/', views.add_to_cart_grocery, name='add_to_cart_grocery'),
    path('donation/add-to-cart-medical/', views.add_to_cart_medical, name='add_to_cart_medical'),
    path('donation/cart/', views.view_cart, name='view_cart'),
    path('donation/remove/<str:key>/', views.remove_from_cart, name='remove_from_cart'),
    path('donation/update-cart/', views.update_cart, name='update_cart'),
    path('donation/clear-cart/', views.clear_cart, name='clear_cart'),
    
    # Checkout
    path('donation/checkout/', views.checkout, name='checkout'),

    
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

