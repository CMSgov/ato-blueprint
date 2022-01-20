from django.db.models import Count

from controls.enums.statements import StatementTypeEnum
from controls.models import ElementControl


# Get a count of the Statuses for the controls; Assessed, Ready for Assessment, ...
def get_controls_addressed_count(project):
  stat = (ElementControl.objects
      .filter(element_id=project.system.root_element)
      .values("status")
      .annotate(scount=Count("status"))
      .order_by()
  )

  # Get the Status allowed values
  es = ElementControl.Statuses.choices
  st = dict(es)
  statuses = {}

  # Add the counts to a dictionary keyed by the Status label; {"Assessed": 1, "Ready for assessment": 3,...}
  for els in stat:
      statuses[st[els["status"]]] = els["scount"]

  controls_addressed_count = 0
  if "Assessed" in statuses:
      controls_addressed_count +=  statuses["Assessed"]

  if "Ready for assessment" in statuses:
      controls_addressed_count +=  statuses["Ready for assessment"]

  return controls_addressed_count

def get_control_compliance_stats(project):
    # Get total number of controls assigned to the Project (based on baseline).
    total_controls_count = ElementControl.objects.filter(element_id=project.system.root_element).count()
    controls_addressed_count = get_controls_addressed_count(project)

    # Calculate approximate compliance as decimal representation of percent
    percent_compliant = 0
    if total_controls_count > 0:
        percent_compliant = controls_addressed_count/total_controls_count * 100

    return {
        "total_controls_count": total_controls_count,
        "controls_addressed_count": controls_addressed_count,
        "percent_compliant": percent_compliant
    }

# Get statement defining Security Sensitivity level if set
def get_security_sensitivity(project):
  security_sensitivity_smts = project.system.root_element.statements_consumed.filter(statement_type=StatementTypeEnum.SECURITY_SENSITIVITY_LEVEL.name)
  if len(security_sensitivity_smts) > 0:
      security_sensitivity = security_sensitivity_smts.first().body
  else:
      security_sensitivity = None

  return security_sensitivity
