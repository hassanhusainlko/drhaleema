from django.urls import path
from . import views

app_name = 'clinic'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('expertise/', views.ExpertiseView.as_view(), name='expertise'),
    path('testimonials/', views.TestimonialsView.as_view(), name='testimonials'),
    path('book/', views.BookingView.as_view(), name='book'),
    path('book/guest/', views.GuestBookingView.as_view(), name='book_guest'),
    path('book/confirm/<int:pk>/', views.BookingConfirmView.as_view(), name='book_confirm'),
    path('appointments/', views.MyAppointmentsView.as_view(), name='my_appointments'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment_detail'),
    path('appointments/<int:pk>/cancel/', views.AppointmentCancelView.as_view(), name='appointment_cancel'),
    path('ajax/slots/', views.ajax_slots, name='ajax_slots'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/appointments/', views.DashboardListView.as_view(), name='dashboard_list'),
    path('dashboard/appointments/<int:pk>/', views.DashboardDetailView.as_view(), name='dashboard_detail'),
    path('dashboard/appointments/<int:pk>/notes/', views.dashboard_notes, name='dashboard_notes'),
    path('dashboard/appointments/<int:pk>/status/', views.dashboard_status, name='dashboard_status'),
    path('dashboard/blocked-dates/', views.DashboardBlockedView.as_view(), name='dashboard_blocked'),
    path('dashboard/blocked-dates/<int:pk>/delete/', views.DashboardBlockedDeleteView.as_view(), name='dashboard_blocked_delete'),
]
