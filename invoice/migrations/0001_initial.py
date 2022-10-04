#Developer : SURENDRA 
#date : 2-Oct-2022

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('LocalUser', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(default='000', max_length=2000, null=True)),
                ('invoice_file', models.FileField(upload_to='invoices/')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='LocalUser.UserProfile')),
            ],
        ),
    ]
