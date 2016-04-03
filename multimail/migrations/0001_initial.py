from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('verif_key', models.CharField(max_length=40)),
                ('verified_at', models.DateTimeField(null=True, default=None, blank=True)),
                ('remote_addr', models.IPAddressField(null=True, blank=True)),
                ('remote_host', models.CharField(null=True, blank=True, max_length=255)),
                ('is_primary', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]