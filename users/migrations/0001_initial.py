# Generated by Django 5.1.1 on 2024-10-29 05:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dob', models.DateField(blank=True, null=True)),
                ('profile_photo', models.ImageField(default='profile_pics/male_default.jpg', upload_to='profile_pics')),
                ('first_name', models.CharField(blank=True, max_length=100, null=True)),
                ('last_name', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('age', models.PositiveIntegerField(default=0, editable=False)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Male', max_length=10)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('place', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('pin', models.IntegerField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('education', models.CharField(blank=True, default='Degree', max_length=100)),
                ('job', models.CharField(blank=True, max_length=100, null=True)),
                ('religion', models.CharField(blank=True, choices=[('Hinduism', 'Hinduism'), ('Islam', 'Islam'), ('Christianity', 'Christianity'), ('Buddhism', 'Buddhism'), ('Sikhism', 'Sikhism'), ('Judaism', 'Judaism'), ('Atheism', 'Atheism'), ('Other', 'Other')], max_length=100, null=True)),
                ('caste', models.CharField(blank=True, max_length=100, null=True)),
                ('about_me', models.CharField(blank=True, max_length=500, null=True)),
                ('family_background', models.CharField(choices=[('Lower', 'Lower'), ('Middle', 'Middle'), ('Upper', 'Upper')], default='Middle', max_length=10)),
                ('father_name', models.CharField(blank=True, max_length=100, null=True)),
                ('mother_name', models.CharField(blank=True, max_length=100, null=True)),
                ('siblings_no', models.IntegerField(blank=True, null=True)),
                ('father_job', models.CharField(blank=True, max_length=100, null=True)),
                ('mother_job', models.CharField(blank=True, max_length=100, null=True)),
                ('preferred_age_min', models.IntegerField(default=18)),
                ('preferred_age_max', models.IntegerField(default=35)),
                ('preferred_religion', models.CharField(blank=True, choices=[('Hinduism', 'Hinduism'), ('Islam', 'Islam'), ('Christianity', 'Christianity'), ('Buddhism', 'Buddhism'), ('Sikhism', 'Sikhism'), ('Judaism', 'Judaism'), ('Atheism', 'Atheism'), ('Other', 'Other')], max_length=100, null=True)),
                ('preferred_caste', models.CharField(blank=True, max_length=100, null=True)),
                ('preferred_job', models.CharField(blank=True, max_length=100, null=True)),
                ('preferred_family_background', models.CharField(choices=[('Lower', 'Lower'), ('Middle', 'Middle'), ('Upper', 'Upper')], default='Middle', max_length=10)),
                ('facebook_id', models.CharField(blank=True, max_length=200, null=True)),
                ('instagram_id', models.CharField(blank=True, max_length=200, null=True)),
                ('twitter_id', models.CharField(blank=True, max_length=200, null=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('needs_verification', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('notification_type', models.CharField(choices=[('interest_request', 'Interest Request'), ('message', 'Message'), ('general', 'General')], default='general', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_notifications', to='users.profile')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_notifications', to='users.profile')),
            ],
        ),
        migrations.CreateModel(
            name='InterestRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_accepted', models.BooleanField(default=False)),
                ('is_declined', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_interest_requests', to='users.profile')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_interest_requests', to='users.profile')),
            ],
        ),
        migrations.CreateModel(
            name='ProfileImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='additional_images/')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_images', to='users.profile')),
            ],
        ),
    ]
