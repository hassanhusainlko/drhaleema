from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, FormView, ListView, TemplateView, View

from .forms import (
    AppointmentForm, GuestAppointmentForm,
    ConsultationNotesForm, AppointmentStatusForm, BlockedDateForm,
)
from .models import Appointment, BlockedDate, Specialisation, Testimonial, STATUS_CHOICES
from .utils import get_available_slots


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

class HomeView(TemplateView):
    template_name = 'clinic/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['testimonials'] = Testimonial.objects.filter(is_active=True)
        ctx['core_specs'] = Specialisation.objects.filter(
            is_active=True, category='core'
        )
        return ctx


class AboutView(TemplateView):
    template_name = 'clinic/about.html'


class TestimonialsView(TemplateView):
    template_name = 'clinic/testimonials.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['testimonials'] = Testimonial.objects.filter(is_active=True).order_by('order')
        return ctx


class ExpertiseView(TemplateView):
    template_name = 'clinic/expertise.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['core_specs'] = Specialisation.objects.filter(
            is_active=True, category='core'
        )
        ctx['womens_specs'] = Specialisation.objects.filter(
            is_active=True, category='womens'
        )
        return ctx


# ---------------------------------------------------------------------------
# Booking — logged-in patients
# ---------------------------------------------------------------------------

class BookingView(LoginRequiredMixin, FormView):
    form_class = AppointmentForm
    template_name = 'clinic/book.html'

    def form_valid(self, form):
        appt = form.save(commit=False)
        appt.patient = self.request.user
        try:
            appt.save()
        except IntegrityError:
            messages.error(self.request, 'Sorry, that slot was just taken. Please select another time.')
            return self.form_invalid(form)
        messages.success(self.request, 'Your appointment has been booked!')
        return redirect('clinic:book_confirm', pk=appt.pk)


# ---------------------------------------------------------------------------
# Booking — guest patients
# ---------------------------------------------------------------------------

class GuestBookingView(FormView):
    form_class = GuestAppointmentForm
    template_name = 'clinic/book_guest.html'

    def form_valid(self, form):
        appt = form.save(commit=False)
        appt.patient = None
        try:
            appt.save()
        except IntegrityError:
            messages.error(self.request, 'Sorry, that slot was just taken. Please select another time.')
            return self.form_invalid(form)
        # Store session token so this browser can view confirmation
        self.request.session[f'guest_token_{appt.pk}'] = True
        return redirect('clinic:book_confirm', pk=appt.pk)


# ---------------------------------------------------------------------------
# Booking confirmation
# ---------------------------------------------------------------------------

class BookingConfirmView(DetailView):
    model = Appointment
    template_name = 'clinic/book_confirm.html'
    context_object_name = 'appointment'

    def dispatch(self, request, *args, **kwargs):
        appt = get_object_or_404(Appointment, pk=kwargs['pk'])
        if appt.patient:
            if not request.user.is_authenticated or request.user != appt.patient:
                messages.error(request, 'You do not have access to this page.')
                return redirect('clinic:home')
        else:
            if not request.session.get(f'guest_token_{appt.pk}'):
                messages.error(request, 'You do not have access to this page.')
                return redirect('clinic:home')
        return super().dispatch(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# AJAX: available slots
# ---------------------------------------------------------------------------

def ajax_slots(request):
    date_str = request.GET.get('date', '')
    patient_type = request.GET.get('patient_type', '')
    try:
        appt_date = date.fromisoformat(date_str)
    except ValueError:
        return JsonResponse({'slots': []})
    slots = get_available_slots(appt_date, patient_type)
    return JsonResponse({'slots': [t.strftime('%H:%M') for t in slots]})


# ---------------------------------------------------------------------------
# Patient: my appointments
# ---------------------------------------------------------------------------

class MyAppointmentsView(LoginRequiredMixin, ListView):
    template_name = 'clinic/my_appointments.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return self.request.user.appointments.order_by('-appointment_date', '-appointment_time')


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = 'clinic/appointment_detail.html'
    context_object_name = 'appointment'

    def dispatch(self, request, *args, **kwargs):
        appt = get_object_or_404(Appointment, pk=kwargs['pk'])
        if not request.user.is_staff and appt.patient != request.user:
            messages.error(request, 'You do not have access to this appointment.')
            return redirect('clinic:my_appointments')
        return super().dispatch(request, *args, **kwargs)


class AppointmentCancelView(LoginRequiredMixin, View):
    def post(self, request, pk):
        appt = get_object_or_404(Appointment, pk=pk)
        if appt.patient != request.user and not request.user.is_staff:
            messages.error(request, 'You cannot cancel this appointment.')
            return redirect('clinic:my_appointments')
        if appt.status in ('completed', 'cancelled'):
            messages.warning(request, 'This appointment cannot be cancelled.')
        else:
            appt.status = 'cancelled'
            appt.save()
            messages.success(request, 'Appointment cancelled successfully.')
        return redirect('clinic:my_appointments')


# ---------------------------------------------------------------------------
# Staff dashboard
# ---------------------------------------------------------------------------

class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'clinic/dashboard/overview.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = date.today()
        ctx['today'] = today
        ctx['today_appointments'] = Appointment.objects.filter(
            appointment_date=today
        ).exclude(status='cancelled').order_by('appointment_time')
        ctx['pending_count'] = Appointment.objects.filter(status='pending').count()
        ctx['confirmed_count'] = Appointment.objects.filter(status='confirmed').count()
        ctx['total_today'] = Appointment.objects.filter(appointment_date=today).exclude(status='cancelled').count()
        return ctx


class DashboardListView(StaffRequiredMixin, ListView):
    model = Appointment
    template_name = 'clinic/dashboard/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 20

    def get_queryset(self):
        qs = Appointment.objects.all()
        status = self.request.GET.get('status')
        appt_date = self.request.GET.get('date')
        mode = self.request.GET.get('mode')
        if status:
            qs = qs.filter(status=status)
        if appt_date:
            try:
                qs = qs.filter(appointment_date=date.fromisoformat(appt_date))
            except ValueError:
                pass
        if mode:
            qs = qs.filter(consultation_mode=mode)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = STATUS_CHOICES
        ctx['filter_status'] = self.request.GET.get('status', '')
        ctx['filter_date'] = self.request.GET.get('date', '')
        ctx['filter_mode'] = self.request.GET.get('mode', '')
        return ctx


class DashboardDetailView(StaffRequiredMixin, DetailView):
    model = Appointment
    template_name = 'clinic/dashboard/appointment_detail.html'
    context_object_name = 'appointment'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['notes_form'] = ConsultationNotesForm(instance=self.object)
        ctx['status_form'] = AppointmentStatusForm(initial={'status': self.object.status})
        return ctx


def dashboard_notes(request, pk):
    if not (request.user.is_authenticated and request.user.is_staff):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    appt = get_object_or_404(Appointment, pk=pk)
    form = ConsultationNotesForm(request.POST, instance=appt)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid data', 'errors': form.errors}, status=400)


def dashboard_status(request, pk):
    if not (request.user.is_authenticated and request.user.is_staff):
        return JsonResponse({'error': 'Forbidden'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    appt = get_object_or_404(Appointment, pk=pk)
    form = AppointmentStatusForm(request.POST)
    if form.is_valid():
        appt.status = form.cleaned_data['status']
        appt.save()
        return JsonResponse({'success': True, 'status': appt.status, 'status_display': appt.get_status_display()})
    return JsonResponse({'error': 'Invalid data'}, status=400)


class DashboardBlockedView(StaffRequiredMixin, View):
    template_name = 'clinic/dashboard/blocked_dates.html'

    def get(self, request):
        from django.shortcuts import render
        blocked = BlockedDate.objects.filter(date__gte=date.today()).order_by('date')
        form = BlockedDateForm()
        return render(request, self.template_name, {'blocked_dates': blocked, 'form': form})

    def post(self, request):
        from django.shortcuts import render
        form = BlockedDateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Date blocked successfully.')
            return redirect('clinic:dashboard_blocked')
        blocked = BlockedDate.objects.filter(date__gte=date.today()).order_by('date')
        return render(request, self.template_name, {'blocked_dates': blocked, 'form': form})


class DashboardBlockedDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        blocked = get_object_or_404(BlockedDate, pk=pk)
        blocked.delete()
        messages.success(request, 'Date unblocked.')
        return redirect('clinic:dashboard_blocked')
