

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=300)),
                ('company_razorpay', models.CharField(default='RAZORPAY', max_length=300)),
                ('address', models.TextField(max_length=1000)),
                ('gst', models.CharField(max_length=15)),
                ('employees', models.IntegerField()),
                ('disabled', models.BooleanField(default=False)),
                ('allotted', models.FloatField()),
                ('hourly_rate', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=300)),
                ('last_name', models.CharField(max_length=300)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('regular', models.BooleanField(default=False)),
                ('company_name', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='LocalUser.Company')),
            ],
        ),
        migrations.CreateModel(
            name='LocalUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('date_of_birth', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('profile_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='LocalUser.UserProfile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GmailAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gmail_id', models.CharField(max_length=500)),
                ('user_profile_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LocalUser.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='ForgotPasswordTokens',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.BigIntegerField()),
                ('localuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
