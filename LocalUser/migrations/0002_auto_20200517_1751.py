

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LocalUser', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='localuser',
            name='profile_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='LocalUser.UserProfile', unique=True),
        ),
    ]
