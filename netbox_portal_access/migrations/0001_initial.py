
# Generated barebones initial migration
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Portal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vendor_id', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=100)),
                ('base_url', models.URLField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('vendor_ct', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ('name',),
                'unique_together': {('vendor_ct', 'vendor_id', 'name')},
            },
        ),
        migrations.CreateModel(
            name='VendorRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('PORTAL_ADMIN', 'Portal Admin'), ('READ_ONLY', 'Read Only'), ('TICKETING', 'Ticketing'), ('ORDERING', 'Ordering'), ('LOA_APPROVER', 'LOA Approver'), ('BILLING', 'Billing'), ('REPORTS', 'Reports')], max_length=20)),
                ('description', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('portal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='netbox_portal_access.portal')),
            ],
            options={
                'ordering': ('portal', 'name'),
                'unique_together': {('portal', 'name')},
            },
        ),
        migrations.CreateModel(
            name='AccessAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_id', models.PositiveIntegerField(blank=True, null=True)),
                ('account_identifier', models.CharField(blank=True, max_length=100)),
                ('username_on_portal', models.CharField(blank=True, max_length=150)),
                ('active', models.BooleanField(default=True)),
                ('mfa_type', models.CharField(blank=True, max_length=50)),
                ('sso_provider', models.CharField(blank=True, max_length=50)),
                ('last_verified', models.DateField(blank=True, null=True)),
                ('expires_on', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('contact_ct', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype')),
                ('portal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='netbox_portal_access.portal')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assignments', to='netbox_portal_access.vendorrole')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='portal_access', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-active', 'portal', 'role'),
            },
        ),
        migrations.AddIndex(
            model_name='accessassignment',
            index=models.Index(fields=['active', 'last_verified', 'expires_on'], name='netbox_port_active__be8f9f_idx'),
        ),
        migrations.AddConstraint(
            model_name='accessassignment',
            constraint=models.CheckConstraint(check=models.Q(('user__isnull', False)) | models.Q(('contact_id__isnull', False)), name='assignment_has_subject'),
        ),
    ]
