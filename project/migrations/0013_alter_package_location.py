# Generated by Django 3.2.5 on 2022-02-15 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0012_alter_package_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='location',
            field=models.CharField(choices=[('cms_aws', 'CMS AWS Commercial'), ('govcloud', 'CMS AWS GovCloud'), ('azure', 'Microsoft Azure'), ('other', 'Other')], help_text='Where the project is located', max_length=100, null=True),
        ),
    ]
