from datetime import date

from django import forms

from .models import Appointment, BlockedDate, CONSULTATION_MODE_CHOICES, PATIENT_TYPE_CHOICES, STATUS_CHOICES
from .utils import get_available_slots


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_time', 'consultation_mode', 'patient_type']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.Select(),
            'consultation_mode': forms.RadioSelect(),
            'patient_type': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['appointment_date'].label = 'Appointment Date'
        self.fields['appointment_time'].label = 'Available Time Slot'
        self.fields['consultation_mode'].label = 'Consultation Type'
        self.fields['patient_type'].label = 'Are you a new or returning patient?'
        # Time choices start empty; populated via AJAX
        self.fields['appointment_time'].choices = [('', 'Select a date and patient type first')]

    def clean(self):
        cleaned = super().clean()
        appt_date = cleaned.get('appointment_date')
        appt_time = cleaned.get('appointment_time')
        patient_type = cleaned.get('patient_type')

        if appt_date and appt_date < date.today():
            self.add_error('appointment_date', 'Please select a future date.')

        if appt_date and patient_type and appt_time:
            available = get_available_slots(appt_date, patient_type)
            if appt_time not in available:
                self.add_error('appointment_time', 'That slot is no longer available. Please select another time.')

        return cleaned


class GuestAppointmentForm(AppointmentForm):
    guest_name = forms.CharField(max_length=100, required=True, label='Your Full Name')
    guest_phone = forms.CharField(max_length=20, required=True, label='Phone Number')
    guest_email = forms.EmailField(required=False, label='Email Address (optional)')

    class Meta(AppointmentForm.Meta):
        fields = AppointmentForm.Meta.fields + ['guest_name', 'guest_phone', 'guest_email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Move guest fields to the top of the form order
        field_order = ['guest_name', 'guest_phone', 'guest_email'] + AppointmentForm.Meta.fields
        self.order_fields(field_order)


class ConsultationNotesForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['consultation_notes', 'prescription']
        widgets = {
            'consultation_notes': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Consultation notes...'}),
            'prescription': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Prescription details...'}),
        }
        labels = {
            'consultation_notes': 'Consultation Notes',
            'prescription': 'Prescription',
        }


class AppointmentStatusForm(forms.Form):
    status = forms.ChoiceField(choices=STATUS_CHOICES)


class BlockedDateForm(forms.ModelForm):
    class Meta:
        model = BlockedDate
        fields = ['date', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.TextInput(attrs={'placeholder': 'e.g. Public holiday, Leave'}),
        }

    def clean_date(self):
        d = self.cleaned_data.get('date')
        if d and d < date.today():
            raise forms.ValidationError('Cannot block a past date.')
        return d
