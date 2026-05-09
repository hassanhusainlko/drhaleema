from django.db import migrations


SPECIALISATIONS = [
    # Core
    ('core', '🫀', 'Liver & Digestive Health',
     'Liver diseases, digestive disorders, and Chronic Kidney Disease (CKD)', 1),
    ('core', '🌬️', 'Respiratory & Allergy',
     'Comprehensive management of rhinitis and sinusitis', 2),
    ('core', '🦴', 'Pain Management',
     'Specialised treatment for arthritis and sciatica', 3),
    ('core', '✨', 'Dermatology & Aesthetics',
     'Vitiligo, persistent hair & skin issues, and weight management', 4),
    ('core', '🧠', 'Mental Wellness',
     'Compassionate care for anxiety and depression', 5),
    # Women's
    ('womens', '⚖️', 'Hormonal Health',
     'PCOD/PCOS, hormonal imbalance, and menstrual disorders', 1),
    ('womens', '🌸', 'Reproductive Care',
     'Clinical management of infertility and uterine fibroids', 2),
    ('womens', '🔒', 'Sexual Wellness',
     'Confidential consultations for sexual health concerns', 3),
]

TESTIMONIALS = [
    ('Sana R.', 'PCOS Patient · Clinic Visit', '👩',
     'I had been struggling with PCOS for years with no real improvement. After just two months of '
     'treatment with Dr. Haleema, my cycles regulated and my symptoms reduced significantly. '
     'The natural approach made such a difference — no harsh side effects.', 5, 1),
    ('Usman K.', 'Liver Disease · On-Call Consultation', '👨',
     'My father has been suffering from chronic liver issues for a long time. Dr. Haleema\'s herbal '
     'treatment and dietary plan brought noticeable improvement within weeks. She explains everything '
     'clearly and is genuinely caring towards her patients.', 5, 2),
    ('Ayesha M.', 'Sinusitis · Clinic Visit', '👩',
     'I came to Dr. Haleema for severe sinusitis that had been bothering me for over a year. '
     'The Unani treatment she prescribed cleared it up better than anything else I had tried. '
     'Very professional and thorough in her assessment.', 5, 3),
    ('Tariq B.', 'Arthritis · On-Call Consultation', '👴',
     'The online consultation was incredibly convenient. Dr. Haleema was attentive and prescribed '
     'a treatment plan for my arthritis that has reduced my joint pain substantially. '
     'I highly recommend her to anyone looking for a natural approach.', 5, 4),
    ('Mariam F.', 'Anxiety & Wellness · Clinic Visit', '👩',
     'I was dealing with anxiety and stress for a long time. Dr. Haleema\'s holistic approach — '
     'combining herbal medicine with lifestyle advice — helped me feel balanced again. '
     'She listens patiently and never rushes the consultation.', 5, 5),
]


def seed_data(apps, schema_editor):
    Specialisation = apps.get_model('clinic', 'Specialisation')
    Testimonial = apps.get_model('clinic', 'Testimonial')

    for category, icon, title, description, order in SPECIALISATIONS:
        Specialisation.objects.create(
            category=category,
            icon=icon,
            title=title,
            description=description,
            order=order,
            is_active=True,
        )

    for name, condition, avatar, text, rating, order in TESTIMONIALS:
        Testimonial.objects.create(
            name=name,
            condition=condition,
            avatar=avatar,
            text=text,
            rating=rating,
            order=order,
            is_active=True,
        )


def remove_data(apps, schema_editor):
    apps.get_model('clinic', 'Specialisation').objects.all().delete()
    apps.get_model('clinic', 'Testimonial').objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0002_add_testimonial_specialisation'),
    ]

    operations = [
        migrations.RunPython(seed_data, remove_data),
    ]
