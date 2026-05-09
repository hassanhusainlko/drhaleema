from datetime import date, time, datetime, timedelta

from .models import Appointment, BlockedDate

OPD_SESSIONS = [
    (time(10, 0), time(14, 0)),    # Morning: 10:00 AM – 2:00 PM
    (time(14, 30), time(18, 30)),  # Evening: 2:30 PM – 6:30 PM
]

SLOT_DURATION_MAP = {
    'new': 25,
    'followup': 15,
}


def _time_to_minutes(t):
    return t.hour * 60 + t.minute


def _minutes_to_time(m):
    return time(m // 60, m % 60)


def get_available_slots(appt_date, patient_type):
    """
    Return list of available start times (datetime.time) for the given date
    and patient_type ('new' or 'followup').
    """
    if appt_date < date.today():
        return []

    if BlockedDate.objects.filter(date=appt_date).exists():
        return []

    duration = SLOT_DURATION_MAP.get(patient_type, 15)

    existing = Appointment.objects.filter(
        appointment_date=appt_date,
    ).exclude(status='cancelled').values_list('appointment_time', 'duration_minutes')

    booked_intervals = [
        (_time_to_minutes(t), _time_to_minutes(t) + d)
        for t, d in existing
    ]

    available = []
    for session_start, session_end in OPD_SESSIONS:
        cursor = _time_to_minutes(session_start)
        end = _time_to_minutes(session_end)
        while cursor + duration <= end:
            slot_end = cursor + duration
            overlaps = any(
                cursor < b_end and slot_end > b_start
                for b_start, b_end in booked_intervals
            )
            if not overlaps:
                available.append(_minutes_to_time(cursor))
            cursor += duration

    return available
