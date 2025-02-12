# Generated by Django 5.1.4 on 2025-02-12 12:44

import api.models
import django.db.models.deletion
import django.utils.timezone
import multiselectfield.db.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Income',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Enter the transaction amount.', max_digits=10, verbose_name='Amount')),
                ('category', models.CharField(help_text='Specify the category of the transaction', max_length=50, verbose_name='Category')),
                ('date', models.DateField(blank=True, help_text='The date of the transaction.', null=True, verbose_name='Transaction Date')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('source', models.CharField(help_text='The source of the income, e.g., salary, investment, etc.', max_length=100, verbose_name='Income Source')),
            ],
            options={
                'verbose_name': 'Income',
                'verbose_name_plural': 'Incomes',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True, verbose_name='Email Address')),
                ('full_name', models.CharField(blank=True, max_length=150)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', api.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='Budget', max_length=255, null=True)),
                ('category', models.CharField(choices=[('Meal', 'Meal'), ('Supplies', 'Supplies'), ('Hotel', 'Hotel'), ('Fuel & Energy', 'Fuel & Energy'), ('Transportation', 'Transportation'), ('Communication & Subscriptions', 'Communication & Subscriptions'), ('Entertainment', 'Entertainment'), ('Training', 'Training'), ('Healthcare', 'Healthcare'), ('Other', 'Other')], default='Other', help_text='Select the category of the receipt.', max_length=50, verbose_name='Category')),
                ('filter_categories', multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('Meal', 'Meal'), ('Supplies', 'Supplies'), ('Hotel', 'Hotel'), ('Fuel & Energy', 'Fuel & Energy'), ('Transportation', 'Transportation'), ('Communication & Subscriptions', 'Communication & Subscriptions'), ('Entertainment', 'Entertainment'), ('Training', 'Training'), ('Healthcare', 'Healthcare'), ('Other', 'Other')], max_length=118)),
                ('limit_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('current_spending', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Budget',
                'verbose_name_plural': 'Budgets',
            },
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, help_text='Enter the transaction amount.', max_digits=10, verbose_name='Amount')),
                ('date', models.DateField(blank=True, help_text='The date of the transaction.', null=True, verbose_name='Transaction Date')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('category', models.CharField(choices=[('Meal', 'Meal'), ('Supplies', 'Supplies'), ('Hotel', 'Hotel'), ('Fuel & Energy', 'Fuel & Energy'), ('Transportation', 'Transportation'), ('Communication & Subscriptions', 'Communication & Subscriptions'), ('Entertainment', 'Entertainment'), ('Training', 'Training'), ('Healthcare', 'Healthcare'), ('Other', 'Other')], default='Other', help_text='Select the category of the expense.', max_length=50, verbose_name='Category')),
                ('vendor', models.CharField(blank=True, help_text='The vendor or merchant associated with the expense.', max_length=100, null=True, verbose_name='Vendor')),
                ('payment_method', models.CharField(blank=True, help_text='Payment method used for the expense, e.g., credit card, cash.', max_length=50, null=True, verbose_name='Payment Method')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Expense',
                'verbose_name_plural': 'Expenses',
            },
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField(blank=True, max_length=500, null=True, verbose_name='Image URL')),
                ('merchant', models.CharField(blank=True, max_length=100, null=True, verbose_name='Merchant')),
                ('total_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Total')),
                ('uploaded_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('parsed_items', models.JSONField(blank=True, null=True, verbose_name='Parsed Items')),
                ('transaction_date', models.DateTimeField(blank=True, null=True, verbose_name='Transaction Date')),
                ('receipt_category', models.CharField(choices=[('Meal', 'Meal'), ('Supplies', 'Supplies'), ('Hotel', 'Hotel'), ('Fuel & Energy', 'Fuel & Energy'), ('Transportation', 'Transportation'), ('Communication & Subscriptions', 'Communication & Subscriptions'), ('Entertainment', 'Entertainment'), ('Training', 'Training'), ('Healthcare', 'Healthcare'), ('Other', 'Other')], default='Other', help_text='Select the category of the receipt.', max_length=50, verbose_name='Category')),
                ('budget', models.ManyToManyField(related_name='receipts', to='api.budget')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receipts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
