from django.conf import settings
from django.db import models
from datetime import datetime, timedelta


CONSULTATION_MODE_CHOICES = [
    ('clinic', 'Clinic Visit'),
    ('oncall', 'On-Call (Phone/Online)'),
]

PATIENT_TYPE_CHOICES = [
    ('new', 'New Patient'),
    ('followup', 'Follow-up'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

SLOT_DURATION_MAP = {
    'new': 25,
    'followup': 15,
}


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    condition = models.CharField(max_length=150, help_text='e.g. "PCOS Patient · Clinic Visit"')
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    avatar = models.CharField(max_length=10, default='👤', help_text='Emoji avatar')
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.name} — {self.condition}"

    def star_range(self):
        return range(self.rating)

    def empty_star_range(self):
        return range(5 - self.rating)


class Specialisation(models.Model):
    CATEGORY_CHOICES = [
        ('core', 'Core Specialisations'),
        ('womens', "Women's & Reproductive Health"),
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, help_text='Emoji icon')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='core')
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'order', 'id']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"


class BlockedDate(models.Model):
    date = models.DateField(unique=True)
    reason = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return str(self.date)


class Appointment(models.Model):
    # Patient identity — one path populated, other blank
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='appointments',
    )
    guest_name = models.CharField(max_length=100, blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)
    guest_email = models.EmailField(blank=True)

    # Scheduling
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveSmallIntegerField(editable=False)
    consultation_mode = models.CharField(max_length=10, choices=CONSULTATION_MODE_CHOICES)
    patient_type = models.CharField(max_length=10, choices=PATIENT_TYPE_CHOICES)

    # Workflow
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')

    # Clinical record
    consultation_notes = models.TextField(blank=True)
    prescription = models.TextField(blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        unique_together = [['appointment_date', 'appointment_time']]

    def save(self, *args, **kwargs):
        self.duration_minutes = SLOT_DURATION_MAP.get(self.patient_type, 15)
        super().save(*args, **kwargs)

    def end_time(self):
        dt = datetime.combine(self.appointment_date, self.appointment_time)
        return (dt + timedelta(minutes=self.duration_minutes)).time()

    def display_name(self):
        if self.patient:
            return self.patient.get_full_name() or self.patient.username
        return self.guest_name

    def display_phone(self):
        if self.patient:
            return self.patient.phone_number
        return self.guest_phone

    def __str__(self):
        return f"{self.display_name()} — {self.appointment_date} {self.appointment_time.strftime('%H:%M')}"
