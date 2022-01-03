# Generated by Django 3.2.5 on 2021-08-28 00:23

import json
import os.path

from django.db import migrations, models

from controls.models import Element, Statement
from controls.oscal import CatalogData


def load_catalog_data_800_171_fixed(apps, schema_editor):
    """Load control catalog data into database for 800-171 fix"""

    # Load the default control catalogs and baselines
    CATALOG_PATH = os.path.join(os.path.dirname(__file__),'..','data','catalogs')
    BASELINE_PATH = os.path.join(os.path.dirname(__file__),'..','data','baselines')

    # TODO: Check directory exists
    catalog_files = [file for file in os.listdir(CATALOG_PATH) if file.startswith('NIST_SP-800-171_rev1_catalog')]
    # Load catalog and baseline data into database records from source files if data records do not exist in database
    for cf in catalog_files:
        catalog_key = cf.replace("_catalog.json", "")
        with open(os.path.join(CATALOG_PATH,cf), 'r') as json_file:
            catalog_json = json.load(json_file)
        baseline_filename = cf.replace("_catalog.json", "_baselines.json")
        if os.path.isfile(os.path.join(BASELINE_PATH, baseline_filename)):
            with open(os.path.join(BASELINE_PATH, baseline_filename), 'r') as json_file:
                baselines_json = json.load(json_file)
        else:
            baselines_json = {}

        catalog, created = CatalogData.objects.get_or_create(
                catalog_key=catalog_key
            )
        if created:
            print(f"{catalog_key} record created into database")
        else:
            catalog.catalog_json = catalog_json
            catalog.baselines_json = baselines_json
            catalog.save()
            print(f"{catalog_key} record updated in database")

def update_smt_800_171(apps, schema_editor):
    """Update sid statements that point to 800-171 catalog"""

    catalog_key = 'NIST_SP-800-171_rev1'
    smts =  Statement.objects.filter(sid_class=catalog_key, sid__icontains='3.').only('sid')
    # update sid
    for smt in smts:
        # double check control starts with '3.'
        if smt.sid.startswith('3.'):
            smt.sid = 'c' + smt.sid
            smt.save()

def reverse_func(apps, schema_editor):
    """Reverse update sid statements that point to 800-171 catalog"""

    catalog_key = 'NIST_SP-800-171_rev1'
    smts =  Statement.objects.filter(sid_class=catalog_key, sid__icontains='3.').only('sid')
    # update sid
    for smt in smts:
        # double check control starts with '3.'
        if smt.sid.startswith('c3.'):
            smt.sid = smt.sid.replace('c3.', '3.')
            smt.save()

    # No reverse for catalog_json, leave as is


class Migration(migrations.Migration):

    dependencies = [
        ('controls', '0060_auto_20210816_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalstatement',
            name='change_log',
            field=models.JSONField(blank=True, help_text='JSON object representing changes to the statement', null=True),
        ),
        migrations.AddField(
            model_name='statement',
            name='change_log',
            field=models.JSONField(blank=True, help_text='JSON object representing changes to the statement', null=True),
        ),
         migrations.RunPython(load_catalog_data_800_171_fixed, reverse_func),
         migrations.RunPython(update_smt_800_171, reverse_func)
    ]
