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
    path('admin-change-password/',views.admin_change_password,name='admin_change_password'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-donations/', views.manage_donations, name='manage_donations'),
    path('manage-events/', views.manage_events, name='manage_events'),
    path('update-events/<int:event_id>/', views.update_event, name='update_event'),
    path('delete-events/<int:event_id>/', views.delete_event, name='delete_event'),
    path('manage-staff/', views.manage_staff, name='manage_staff'),
    path('manage-blood-donors/', views.manage_blood_donors, name='manage_blood_donors'),
    path('manage-emergency-support/', views.manage_emergency_support, name='manage_emergency_support'),
    path('manage-palliative-care/', views.manage_palliative_care, name='manage_palliative_care'),
    path('manage-field-data/', views.manage_field_data, name='manage_field_data'),
    path('mark-solved/<int:field_id>/', views.mark_field_solved, name='mark_field_solved'),
    path('manage-feedbacks/', views.manage_feedbacks, name='manage_feedbacks'),
    path('manage-inventory/', views.manage_inventory, name='manage_inventory'),
    path('add-donation/', views.add_donation, name='add_donation'),
    path('add-emergency-request/', views.add_emergency_request, name='add_emergency_request'),
    path('add-inventory/', views.add_inventory, name='add_inventory'),
    path('add-field-data/', views.add_field_data, name='add_field_data'),
    path('send-feedback-reply/<int:feedback_id>/', views.send_feedback_reply, name='send_feedback_reply'),
    path('add-staff/', views.add_staff, name='add_staff'), 
   
    
    
    #USER URLS
    path('user-home/', views.user_home, name='user_home'),
    path('profile/', views.profile, name='profile'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('user-update-profile/', views.user_update_profile, name='user_update_profile'),
    path('user-password-change/', auth_views.PasswordChangeView.as_view(template_name='userhome/user_password_change.html'), name='password_change'),
    path('user-password-change-done/', auth_views.PasswordChangeDoneView.as_view(template_name='userhome/user_password_change_done.html'), name='password_change_done'),
    path('donation/', views.make_donation, name='make_donation'),
    path('register-blood-donation/', views.register_blood_donation, name='register_blood_donation'),
    path('donor-notifications/', views.donor_notifications, name='donor_notifications'),
    path('beneficiary-notification/', views.beneficiary_notifications, name='beneficiary_notifications'),
    path('beneficiary-requests/<str:d_type>/', views.beneficiary_requests_by_category, name='beneficiary_requests_by_category'),

    
    #STAFF URLS
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/profile-staff/', views.staff_profile, name='staff_profile'),
    path('update-staff/', views.update_profile, name='update_profile'),
    path('staff/change-password-staff/', views.change_password, name='change_password'),
    path('staff/<int:staff_id>/', views.staff_profile, name='staff_profile'),
    path('staff-manage-blood-donors/', views.staff_manage_blood_donors, name='staff_manage_blood_donors'),
    path('staff-manage-donations/', views.staff_manage_donations, name='staff_manage_donations'),
    path('staff-manage-palliative-cases/', views.staff_manage_palliative_cases, name='staff_manage_palliative_cases'),
    path('staff-urgent-requests/', views.staff_urgent_requests, name='staff_urgent_requests'),
    path('staff-manage-emergency-support/', views.staff_manage_emergency_support, name='staff_manage_emergency_support'),
    path('staff/manage-inventory/', views.staff_manage_inventory, name='staff_manage_inventory'),
    path('manage-events/', views.manage_events, name='manage_events'),
    path('add-event/', views.add_event, name='add_event'),
    path('view-events/', views.view_events, name='view_events'),
    path('sponsor-event/<int:event_id>/', views.sponsor_event, name='sponsor_event'),
    path('sponsorship-details/<int:event_id>/', views.sponsorship_details, name='sponsorship_details'),
    path('staff-manage-events/', views.staff_manage_events, name='staff_manage_events'),
    path('staff-dashboard/donation-details/<int:donation_id>/', views.staff_donation_details, name='staff_donation_details'),
    
    
    
    #HOME PAGE URLS
    path('meal/', views.hospital_without_hunger, name='hospital_without_hunger'),
    path('grocery/', views.grocery_assistance, name='grocery_assistance'),
    path('cancer_patient/', views.cancer_patient, name='cancer_patient'),
    path('beneficary_aid/', views.beneficary_aid, name='beneficary_aid'),
    path('palliative_program/',views.palliative_program,name='palliative_program'),
    path('palliative-patient/', views.palliative_register, name='palliative_register'),
    path('palliative-success/', views.palliative_register_success, name='palliative_register_success'),
    path('palliative-assign/<int:patient_id>/', views.assign_volunteer, name='assign_volunteer'),
    path('volunteer-detail/<int:volunteer_id>/', views.volunteer_detail, name='volunteer_detail'),
    path('counseling/',views.counselling,name='counseling'),
    path('councontact/', views.councontact, name='councontact'),
    path('blood-donor/', views.blood_donation, name='blood_donation'),

    #VOLUNTEER URLS
    path('volunteer/', views.volunteer, name='volunteer'),
    path('volunteer/thank-you/', views.volunteer_thankyou, name='volunteer_thankyou'),
    path('manage-volunteers/approve/<int:volunteer_id>/', views.approve_volunteer, name='approve_volunteer'),
    path('volunteer_dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),
    path('manage-volunteers/', views.manage_volunteers, name='manage_volunteers'),
    path('staff/volunteers/', views.staff_manage_volunteers, name='staff_manage_volunteers'),
    path('add-volunteer/', views.add_volunteer, name='add_volunteer'), 
    path('assigned-task/', views.assigned_tasks_view, name='assigned_tasks_view'),
    path('complete_task/<int:task_id>/', views.complete_task, name='complete_task'),
    path('complete_palliative_case/<int:case_id>/', views.complete_palliative_case, name='complete_palliative_case'),
    path('palliative-patient/<int:patient_id>/', views.palliative_patient_detail, name='palliative_patient_detail'),
    path('volunteer_profile/', views.profile, name='profile'),
    path('change_password/', auth_views.PasswordChangeView.as_view(
         template_name='home/change_password.html',
         success_url='/change_password_done/'
    ), name='change_password'),
    path('change_password_done/', auth_views.PasswordChangeDoneView.as_view(
         template_name='home/change_password_done.html'
    ), name='change_password_done'),    path('view_events/', views.view_events, name='view_events'),
    path('field_data_collection/', views.field_data_collection, name='field_data_collection'),
    path('edit-volunteer-profile/', views.edit_volunteer_profile, name='edit_volunteer_profile'),
    path('volunteer-events/', views.volunteer_view_events, name='volunteer_view_events'),
    path('assign-field/<int:volunteer_id>/', views.assign_field_to_volunteer, name='assign_field_to_volunteer'),


    #DONATION URLS
    path('donation/monetary/', views.monetary_donation, name='monetary_donation'),
    path('donation/monetary-receipt/', views.monetary_receipt, name='monetary_receipt'),
    path('donation/blood_donor/', views.blood_donor, name='blood_donor'),
    path('donation-category/', views.donation_category, name='donation_category'),
    path('donation/products/<str:category>/', views.donation_products, name='donation_products'),
    path('donation/grocery-donation/', views.grocery_kit_donation, name='grocery_kit_donation'),
    path('donation/medical-expenses/', views.medical_expenses_donation, name='medical_expenses_donation'),
    path('donation/nourish-the-needy/', views.nourish_the_needy_donation, name='nourish_the_needy_donation'),
    path('donation/add-to-cart-needy/', views.add_to_cart_needy, name='add_to_cart_needy'),
    path('donation/comprehensive-home-care/', views.comprehensive_home_care_donation, name='comprehensive_home_care_donation'),
    path('donation/add-to-cart-homecare/', views.add_to_cart_homecare, name='add_to_cart_homecare'),
    path('donation/other-donations/', views.other_donations, name='other_donations'),
    path('donation/add-to-cart-other/', views.add_to_cart_other, name='add_to_cart_other'),
    path('donation/goods-checkout/', views.goods_checkout, name='goods_checkout'),
    path('donor/<int:user_id>/', views.donor_detail, name='donor_detail'),

    
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
    path('donation/receipt/', views.receipt, name='receipt'),
    
    

    
    
    path('submit-request/', views.submit_request, name='submit_request'),
    path('thank-you/', views.thank_you, name='thank_you'),

    path('request-list/', views.request_list, name='request_list'),
    path('admin-request-list/', views.admin_request_list, name='admin_request_list'),
    path('approve-request/<int:beneficiary_id>/', views.approve_request, name='approve_request'),
    path('reject-request/<int:beneficiary_id>/', views.reject_request, name='reject_request'),
    path('update-request/<int:pk>/', views.update_request, name='update_request'),
    path('monetary/payment-success/', views.payment_success, name='payment_success'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    
    
    path('all/', views.all_feedbacks, name='all_feedbacks'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),

    path('home/dashboard/', views.account_dashboard, name='account_dashboard'),
    path('user-home/', views.contact_view, name='user_home'),
    path('contacts/', views.admin_contact_list, name='admin_contact_list'),
    
    
    path('urgent-requests/', views.urgent_requests, name='urgent_requests'),
    path('inventory-allocate/<str:d_type>/', views.beneficiary_requests_by_category, name='allocate_by_category'),
    path('allocate-beneficiary-request/<int:pk>/', views.allocate_beneficiary_request, name='allocate_beneficiary_request'),

    path('donation-category/', views.donation_category, name='donation_category'),
    
    
    
    #coordinator
    
    path('coordinator-dashboard/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('coordinator-profile/', views.coordinator_profile, name='coordinator_profile'),
    path('coordinator_manage_events/', views.coordinator_manage_events, name='coordinator_manage_events'),
    path('add-eventscord/',views.add_eventscord, name='add_eventscord'),
    path('coordinator-update-event/<int:event_id>/', views.coordinator_update_event, name='coordinator_update_event'),
    path('coordinator-delete-event/<int:event_id>/', views.coordinator_delete_event, name='coordinator_delete_event'),

    path('coordinator-manage-volunteers/', views.coordinator_manage_volunteers, name='coordinator_manage_volunteers'),
    path('coordinator-manage-tasks/', views.coordinator_manage_tasks, name='coordinator_manage_tasks'),
    path('coordinator-manage-palliative/', views.coordinator_manage_palliative, name='coordinator_manage_palliative'),
    path('edit-profile/', views.edit_coordinator_profile, name='edit_coordinator_profile'),
    path('change-password/', views.change_coordinator_password, name='change_coordinator_password'),
    path('assigned_tasks_coordinator/', views.view_assigned_tasks_coordinator, name='view_assigned_tasks_coordinator'),
    path('tasks/<int:task_id>/complete/', views.mark_task_complete, name='mark_task_complete'),

    
    path('assign-field/<int:volunteer_id>/', views.assign_field_to_volunteer, name='assign_field_to_volunteer'),
    path('assignment-success/', views.assignment_success, name='assignment_success'),
    path('assign-field/', views.search_volunteers, name='search_volunteers'),
    path('my-assignments/', views.view_assigned_fields, name='view_assigned_fields'),
    path('mark-assignment-completed/<int:assignment_id>/', views.mark_assignment_completed, name='mark_assignment_completed'),

    path('view_field_assignments_coordinator/', views.view_field_assignments_coordinator, name='view_field_assignments_coordinator'),
    path('requests/all/', views.view_all_requests, name='view_all_requests'),
    
    
    path('notifs/', views.manage_notifs, name='manage_notifs'),
    path('notifs/<str:group>/', views.group_notifs, name='group_notifs'),
    path('volunteer-notifications/', views.volunteer_notifs, name='volunteer_notifs'),


    #REPORT URL
    path('reports/beneficiary-support/',views.beneficiary_support_report, name='beneficiary_support_report'),
    path('reports/monthly-report-form/', views.monthly_report, name='monthly_report'),


    
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

