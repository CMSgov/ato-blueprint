# Generated by Django 3.0.11 on 2021-01-12 05:12

import uuid

import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('controls', '0035_importrecord_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalStatement',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('sid', models.CharField(blank=True, help_text='Statement identifier such as OSCAL formatted Control ID', max_length=100, null=True)),
                ('sid_class', models.CharField(blank=True, help_text="Statement identifier 'class' such as 'NIST_SP-800-53_rev4' or other OSCAL catalog name Control ID.", max_length=200, null=True)),
                ('pid', models.CharField(blank=True, help_text="Statement part identifier such as 'h' or 'h.1' or other part key", max_length=20, null=True)),
                ('body', models.TextField(blank=True, help_text='The statement itself', null=True)),
                ('statement_type', models.CharField(blank=True, help_text='Statement type.', max_length=150, null=True)),
                ('remarks', models.TextField(blank=True, help_text='Remarks about the statement.', null=True)),
                ('status', models.CharField(blank=True, help_text='The status of the statement.', max_length=100, null=True)),
                ('version', models.CharField(blank=True, help_text='Optional version number.', max_length=20, null=True)),
                ('created', models.DateTimeField(blank=True, db_index=True, editable=False)),
                ('updated', models.DateTimeField(blank=True, db_index=True, editable=False)),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='A UUID (a unique identifier) for this Statement.')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('consumer_element', models.ForeignKey(blank=True, db_constraint=False, help_text='The element the statement is about.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='controls.Element')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('import_record', models.ForeignKey(blank=True, db_constraint=False, help_text='The Import Record which created this Statement.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='controls.ImportRecord')),
                ('parent', models.ForeignKey(blank=True, db_constraint=False, help_text='Parent statement', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='controls.Statement')),
                ('producer_element', models.ForeignKey(blank=True, db_constraint=False, help_text='The element producing this statement.', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='controls.Element')),
                ('prototype', models.ForeignKey(blank=True, db_constraint=False, help_text='Prototype statement', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='controls.Statement')),
            ],
            options={
                'verbose_name': 'historical statement',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
