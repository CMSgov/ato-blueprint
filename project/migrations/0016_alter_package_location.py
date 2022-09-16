# Generated by Django 3.2.5 on 2022-02-28 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0015_alter_package_impact_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='location',
            field=models.CharField(choices=[('cms_aws', 'CMS AWS Commercial East-West'), ('govcloud', 'CMS AWS GovCloud'), ('azure', 'Microsoft Azure'), ('other', 'Other')], default=None, help_text='Where the project is located', max_length=100, null=True),
        ),
    ]