# Generated by Django 2.0.2 on 2018-02-26 07:32

import uuid

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
from django_extensions.db.fields import (
    CreationDateTimeField,
    ModificationDateTimeField,
)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(
                    max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(
                    blank=True,
                    null=True,
                    verbose_name='last login')),
                ('is_superuser', models.BooleanField(
                    default=False,
                    help_text=(
                        'Designates that this user has all permissions'
                        ' without explicitly assigning them.'),
                    verbose_name='superuser status')),
                ('created', CreationDateTimeField(
                    auto_now_add=True, verbose_name='created')),
                ('modified', ModificationDateTimeField(
                    auto_now=True, verbose_name='modified')),
                ('id',
                 models.UUIDField(default=uuid.uuid4,
                                  editable=False,
                                  primary_key=True,
                                  serialize=False)),
                ('username', models.CharField(
                    error_messages={
                        'unique': 'A user with that username already exists.'
                    },
                    help_text=(
                        'Required. 150 characters or fewer.'
                        ' Letters, digits and @/./+/-/_ only.'),
                    max_length=150,
                    unique=True,
                    validators=[
                        django.contrib.auth.validators.
                        UnicodeUsernameValidator()
                    ],
                    verbose_name='username')),
                ('first_name', models.CharField(
                    blank=True,
                    max_length=30,
                    verbose_name='first name')),
                ('last_name', models.CharField(
                    blank=True,
                    max_length=30,
                    verbose_name='last name')),
                ('email', models.EmailField(
                    blank=True,
                    max_length=254,
                    verbose_name='email address')),
                ('is_staff', models.BooleanField(
                    default=False,
                    help_text=(
                        'Designates whether the user can'
                        ' log into this admin site.'),
                    verbose_name='staff status')),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text=(
                        'Designates whether this user should'
                        ' be treated as active.'
                        ' Unselect this instead of deleting accounts.'),
                    verbose_name='active')),
                ('date_joined', models.DateTimeField(
                    default=django.utils.timezone.now,
                    verbose_name='date joined')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('created', CreationDateTimeField(
                    auto_now_add=True, verbose_name='created')),
                ('modified', ModificationDateTimeField(
                    auto_now=True, verbose_name='modified')),
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClientPermission',
            fields=[
                ('created', CreationDateTimeField(
                    auto_now_add=True, verbose_name='created')),
                ('modified', ModificationDateTimeField(
                    auto_now=True, verbose_name='modified')),
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    editable=False,
                    primary_key=True,
                    serialize=False)),
                ('object_pk', models.CharField(
                    max_length=255, verbose_name='object ID')),
                ('client', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='clientpermission',
                    to='dhh_auth.Client')),
                ('content_type', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='contenttypes.ContentType')),
                ('permission', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='auth.Permission')),
                ('permitted_by', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='client',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to='dhh_auth.Client'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(
                blank=True,
                help_text=(
                    'The groups this user belongs to.'
                    ' A user will get all permissions granted'
                    ' to each of their groups.'),
                related_name='user_set',
                related_query_name='user',
                to='auth.Group',
                verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(
                blank=True,
                help_text='Specific permissions for this user.',
                related_name='user_set',
                related_query_name='user',
                to='auth.Permission',
                verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='clientpermission',
            unique_together={
                ('client', 'permission', 'content_type', 'object_pk'),
            },
        ),
    ]
