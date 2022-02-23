# Generated by Django 3.2.5 on 2021-07-26 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("controls", "0054_merge_0052_auto_20210521_1422_0053_auto_20210701_1133"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalstatement",
            name="source",
            field=models.CharField(
                blank=True,
                help_text="Statement source such as '../../../nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json'.",
                max_length=200,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="statement",
            name="source",
            field=models.CharField(
                blank=True,
                help_text="Statement source such as '../../../nist.gov/SP800-53/rev4/json/NIST_SP-800-53_rev4_catalog.json'.",
                max_length=200,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="historicalstatement",
            name="statement_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("CONTROL_IMPLEMENTATION", "control_implementation"),
                    ("CONTROL_IMPLEMENTATION_LEGACY", "control_implementation_legacy"),
                    (
                        "CONTROL_IMPLEMENTATION_PROTOTYPE",
                        "control_implementation_prototype",
                    ),
                    ("ASSESSMENT_RESULT", "assessment_result"),
                    ("POAM", "POAM"),
                    ("SECURITY_SENSITIVITY_LEVEL", "security_sensitivity_level"),
                    ("SECURITY_IMPACT_LEVEL", "security_impact_level"),
                ],
                help_text="Statement type.",
                max_length=150,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="statement",
            name="statement_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("CONTROL_IMPLEMENTATION", "control_implementation"),
                    ("CONTROL_IMPLEMENTATION_LEGACY", "control_implementation_legacy"),
                    (
                        "CONTROL_IMPLEMENTATION_PROTOTYPE",
                        "control_implementation_prototype",
                    ),
                    ("ASSESSMENT_RESULT", "assessment_result"),
                    ("POAM", "POAM"),
                    ("SECURITY_SENSITIVITY_LEVEL", "security_sensitivity_level"),
                    ("SECURITY_IMPACT_LEVEL", "security_impact_level"),
                ],
                help_text="Statement type.",
                max_length=150,
                null=True,
            ),
        ),
    ]
