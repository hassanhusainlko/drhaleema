from django.contrib import admin
from django.utils.html import format_html

from .models import Appointment, BlockedDate, Specialisation, Testimonial


# ── Appointment bulk actions ──────────────────────────────────────────────────

@admin.action(description='✅  Mark selected as Confirmed')
def mark_confirmed(modeladmin, request, queryset):
    queryset.update(status='confirmed')


@admin.action(description='✔️  Mark selected as Completed')
def mark_completed(modeladmin, request, queryset):
    queryset.update(status='completed')


@admin.action(description='❌  Mark selected as Cancelled')
def mark_cancelled(modeladmin, request, queryset):
    queryset.update(status='cancelled')


# ── Appointment admin ─────────────────────────────────────────────────────────

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display  = (
        'display_name', 'appointment_date', 'appointment_time',
        'consultation_mode', 'patient_type', 'coloured_status', 'created_at',
    )
    list_filter   = ('status', 'consultation_mode', 'patient_type', 'appointment_date')
    search_fields = (
        'patient__username', 'patient__first_name', 'patient__last_name',
        'guest_name', 'guest_phone',
    )
    date_hierarchy   = 'appointment_date'
    readonly_fields  = ('duration_minutes', 'created_at', 'updated_at')
    save_on_top      = True
    ordering         = ('-appointment_date', '-appointment_time')
    actions          = [mark_confirmed, mark_completed, mark_cancelled]

    fieldsets = (
        ('Patient', {
            'fields': ('patient', 'guest_name', 'guest_phone', 'guest_email'),
        }),
        ('Scheduling', {
            'fields': (
                'appointment_date', 'appointment_time', 'duration_minutes',
                'consultation_mode', 'patient_type',
            ),
        }),
        ('Status', {
            'fields': ('status',),
        }),
        ('Clinical Notes', {
            'fields': ('consultation_notes', 'prescription'),
            'classes': ('wide',),
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Status')
    def coloured_status(self, obj):
        colours = {
            'pending':   ('#b45309', '#fef3c7'),
            'confirmed': ('#1e40af', '#dbeafe'),
            'completed': ('#166534', '#dcfce7'),
            'cancelled': ('#991b1b', '#fee2e2'),
        }
        fg, bg = colours.get(obj.status, ('#374151', '#f3f4f6'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;'
            'border-radius:12px;font-size:0.82rem;font-weight:600;">{}</span>',
            bg, fg, obj.get_status_display(),
        )


# ── Blocked date admin ────────────────────────────────────────────────────────

@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ('date', 'reason')
    ordering     = ('date',)


# ── Testimonial admin ─────────────────────────────────────────────────────────

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display  = ('name', 'condition', 'star_display', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter   = ('is_active', 'rating')
    search_fields = ('name', 'condition', 'text')
    ordering      = ('order',)

    @admin.display(description='Rating')
    def star_display(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)


# ── Specialisation admin ──────────────────────────────────────────────────────

@admin.register(Specialisation)
class SpecialisationAdmin(admin.ModelAdmin):
    list_display  = ('icon', 'title', 'category', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter   = ('category', 'is_active')
    ordering      = ('category', 'order')
