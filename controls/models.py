import json
import os
import uuid
from copy import deepcopy
from pathlib import Path

import auto_prefetch
from django.db import models, transaction
from django.db.models import Count
from django.utils.functional import cached_property
from guardian.shortcuts import assign_perm, get_perms_for_model
from jsonfield import JSONField
from natsort import natsorted
from simple_history.models import HistoricalRecords

import tools.diff_match_patch.python3 as dmp_module
from controls.enums.components import ComponentStateEnum, ComponentTypeEnum
from controls.enums.remotes import RemoteTypeEnum
from controls.enums.statements import StatementTypeEnum
from controls.oscal import Catalog, CatalogData
from siteapp.model_mixins.tags import TagModelMixin

BASELINE_PATH = os.path.join(os.path.dirname(__file__), "data", "baselines")
ORGPARAM_PATH = os.path.join(
    os.path.dirname(__file__), "data", "org_defined_parameters"
)


class ImportRecord(models.Model):
    name = models.CharField(
        max_length=100,
        help_text="File name of the import",
        unique=False,
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=True,
        help_text="Unique identifier for this Import Record.",
    )

    def get_components_statements(self):
        components = Element.objects.filter(import_record=self)
        component_statements = {}

        for component in components:
            component_statements[component] = Statement.objects.filter(
                producer_element=component
            )

        return component_statements


STATEMENT_SYNCHED = "synched"
STATEMENT_NOT_SYNCHED = "not_synched"
STATEMENT_ORPHANED = "orphaned"


class SystemException(Exception):
    """Class for raising custom exceptions with Systems"""

    pass


class Statement(auto_prefetch.Model):
    sid = models.CharField(
        max_length=100,
        help_text="Statement identifier such as OSCAL formatted Control ID",
        unique=False,
        blank=True,
        null=True,
    )
    sid_class = models.CharField(
        max_length=200,
        help_text="Statement identifier 'class' such as 'NIST_SP-800-53_rev4' or other OSCAL \
            catalog name Control ID.",
        unique=False,
        blank=True,
        null=True,
    )
    source = models.CharField(
        max_length=200,
        help_text="Statement source such as '../../../nist.gov/SP800-53/rev4/json/\
            NIST_SP-800-53_rev4_catalog.json'.",
        unique=False,
        blank=True,
        null=True,
    )
    pid = models.CharField(
        max_length=20,
        help_text="Statement part identifier such as 'h' or 'h.1' or other part key",
        unique=False,
        blank=True,
        null=True,
    )
    body = models.TextField(
        help_text="The statement itself", unique=False, blank=True, null=True
    )
    statement_type = models.CharField(
        max_length=150,
        help_text="Statement type.",
        unique=False,
        blank=True,
        null=True,
        choices=StatementTypeEnum.choices(),
    )
    remarks = models.TextField(
        help_text="Remarks about the statement.", unique=False, blank=True, null=True
    )
    status = models.CharField(
        max_length=100,
        help_text="The status of the statement.",
        unique=False,
        blank=True,
        null=True,
    )
    version = models.CharField(
        max_length=20,
        help_text="Optional version number.",
        unique=False,
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    parent = auto_prefetch.ForeignKey(
        "self",
        help_text="Parent statement",
        related_name="children",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    prototype = auto_prefetch.ForeignKey(
        "self",
        help_text="Prototype statement",
        related_name="instances",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    producer_element = auto_prefetch.ForeignKey(
        "Element",
        related_name="statements_produced",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="The element producing this statement.",
    )
    consumer_element = auto_prefetch.ForeignKey(
        "Element",
        related_name="statements_consumed",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="The element the statement is about.",
    )
    mentioned_elements = models.ManyToManyField(
        "Element",
        related_name="statements_mentioning",
        blank=True,
        help_text="All elements mentioned in a statement; elements with a first degree \
            relationship to the statement.",
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text="A UUID (a unique identifier) for this Statement.",
    )
    import_record = auto_prefetch.ForeignKey(
        ImportRecord,
        related_name="import_record_statements",
        on_delete=models.CASCADE,
        unique=False,
        blank=True,
        null=True,
        help_text="The Import Record which created this Statement.",
    )
    change_log = models.JSONField(
        blank=True,
        null=True,
        help_text="JSON object representing changes to the statement",
    )
    inheritance = models.ForeignKey(
        "Inheritance",
        related_name="statements",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    history = HistoricalRecords(cascade_delete_history=True)

    class Meta:
        indexes = [
            models.Index(fields=["producer_element"], name="producer_element_idx"),
        ]
        permissions = [
            (
                "can_grant_smt_owner_permission",
                "Grant a user statement owner permission",
            ),
        ]
        ordering = ["producer_element__name", "sid"]

    def __str__(self):
        return "'%s %s %s %s %s'" % (
            self.statement_type,
            self.sid,
            self.pid,
            self.sid_class,
            self.id,
        )

    def __repr__(self):
        # For debugging.
        return "'%s %s %s %s %s'" % (
            self.statement_type,
            self.sid,
            self.pid,
            self.sid_class,
            self.id,
        )

    @cached_property
    def producer_element_name(self):
        return self.producer_element.name

    @property
    def catalog_control(self):
        """Return the control content from the catalog"""

        # Get instance of the control catalog
        catalog = Catalog.GetInstance(catalog_key=self.sid_class)
        # Look up control by ID
        return catalog.get_control_by_id(self.sid)

    @cached_property
    def catalog_control_as_dict(self):
        """Return the control content from the catalog"""

        # Get instance of the control catalog
        catalog = Catalog.GetInstance(catalog_key=self.sid_class)
        # Look up control by ID
        catalog_control_dict = catalog.get_flattened_control_as_dict(
            self.catalog_control
        )
        return catalog_control_dict

    @cached_property
    def control_title(self):
        """Return the control title"""

        return self.catalog_control_as_dict["title"]

    def create_prototype(self):
        """
        Creates a prototype statement from an existing statement and prototype object
        """

        if self.prototype is not None:
            # Prototype already exists for statement
            return self.prototype

        prototype = deepcopy(self)
        prototype.statement_type = (
            StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name
        )
        prototype.consumer_element_id = None
        prototype.id = None
        prototype.save()
        # Set prototype attribute on the instances to newly created prototype
        self.prototype = prototype
        self.save()
        return self.prototype

    def create_system_control_smt_from_component_prototype_smt(
        self, consumer_element_id
    ):
        """
        Creates a control_implementation statement instance for a system's root_element from
        an existing control implementation prototype statement
        """

        # Check statement is a prototype
        if (
            self.statement_type
            != StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name
        ):
            return None

        # Return if statement already has instance associated with consumer_element
        if self.instances.filter(consumer_element__id=consumer_element_id).exists():
            return self.prototype

        instance = deepcopy(self)
        instance.statement_type = StatementTypeEnum.CONTROL_IMPLEMENTATION.name
        instance.consumer_element_id = consumer_element_id
        instance.id = None
        # Set prototype attribute to newly created instance
        instance.prototype = self
        instance.save()
        return instance

    @property
    def prototype_synched(self):
        """
        Returns one of STATEMENT_SYNCHED, STATEMENT_NOT_SYNCHED, STATEMENT_ORPHANED for
        control_implementations
        """

        if self.statement_type == StatementTypeEnum.CONTROL_IMPLEMENTATION.name:
            if self.prototype:
                if self.body == self.prototype.body:
                    return STATEMENT_SYNCHED
                else:
                    return STATEMENT_NOT_SYNCHED
            else:
                return STATEMENT_ORPHANED
        else:
            return STATEMENT_NOT_SYNCHED

    @property
    def diff_prototype_main(self):
        """
        Generate a diff of statement of type `control_implementation` and its prototype
        """

        if self.statement_type != StatementTypeEnum.CONTROL_IMPLEMENTATION.name:
            return None
        if self.prototype is None:
            return None
        dmp = dmp_module.diff_match_patch()
        diff = dmp.diff_main(self.prototype.body, self.body)
        return diff

    @property
    def diff_prototype_prettyHtml(self):
        """
        Generate a diff of statement of type `control_implementation` and its prototype
        """

        if self.statement_type != StatementTypeEnum.CONTROL_IMPLEMENTATION.name:
            return None
        if self.prototype is None:
            return None
        dmp = dmp_module.diff_match_patch()
        diff = dmp.diff_main(self.prototype.body, self.body)
        return dmp.diff_prettyHtml(diff)

    @staticmethod
    def _statement_id_from_control(control_id, part_id):
        if part_id:
            return f"{control_id}_smt.{part_id}"
        else:
            return f"{control_id}_smt"

    @property
    def oscal_statement_id(self):
        return Statement._statement_id_from_control(self.sid, self.pid)

    def change_log_add_entry(self, change):
        if not isinstance(change, dict):
            return False
        dictionary_copy = change.copy()
        self.change_log["change_log"]["changes"].append(dictionary_copy)
        self.save()
        return True


class StatementRemote(auto_prefetch.Model):
    statement = models.ForeignKey(
        Statement,
        related_name="remotes",
        unique=False,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="Descendent or cloned Statement.",
    )
    remote_statement = models.ForeignKey(
        Statement,
        related_name="descendents",
        unique=False,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Remote or parent Statement.",
    )
    remote_type = models.CharField(
        max_length=80,
        help_text="Remote type.",
        unique=False,
        blank=True,
        null=True,
        choices=RemoteTypeEnum.choices(),
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        help_text="A UUID (a unique identifier) for this Statement.",
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    import_record = auto_prefetch.ForeignKey(
        ImportRecord,
        related_name="import_record_statement_remotes",
        on_delete=models.CASCADE,
        unique=False,
        blank=True,
        null=True,
        help_text="The Import Record which created this record.",
    )


class Inheritance(models.Model):
    name = models.CharField(max_length=120, unique=True, blank=False, null=False)
    description = models.TextField(unique=False, blank=True, null=True)
    responsibility = models.TextField(unique=False, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        # For debugging.
        return f"{self.name} - {self.id}"


class Element(auto_prefetch.Model, TagModelMixin):
    name = models.CharField(
        max_length=250,
        help_text="Common name or acronym of the element",
        unique=True,
        blank=False,
        null=False,
    )
    full_name = models.CharField(
        max_length=250,
        help_text="Full name of the element",
        unique=False,
        blank=True,
        null=True,
    )
    description = models.TextField(
        default="Description needed",
        help_text="Description of the Element",
        unique=False,
        blank=False,
        null=False,
    )
    element_type = models.CharField(
        max_length=150, help_text="Component type", unique=False, blank=True, null=True
    )
    roles = models.ManyToManyField(
        "ElementRole",
        related_name="elements",
        blank=True,
        help_text="Roles assigned to the Element",
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    oscal_version = models.CharField(
        default="1.0.0",
        max_length=20,
        help_text="OSCAL version number.",
        unique=False,
        blank=True,
        null=True,
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=True,
        help_text="A UUID (a unique identifier) for this Element.",
    )
    import_record = auto_prefetch.ForeignKey(
        ImportRecord,
        related_name="import_record_elements",
        on_delete=models.CASCADE,
        unique=False,
        blank=True,
        null=True,
        help_text="The Import Record which created this Element.",
    )
    component_type = models.CharField(
        default="software",
        max_length=50,
        help_text="OSCAL Component Type.",
        unique=False,
        blank=True,
        null=True,
        choices=ComponentTypeEnum.choices(),
    )
    component_state = models.CharField(
        default="operational",
        max_length=50,
        help_text="OSCAL Component State.",
        unique=False,
        blank=True,
        null=True,
        choices=ComponentStateEnum.choices(),
    )

    def __str__(self):
        return "'%s id=%d'" % (self.name, self.id)

    def __repr__(self):
        # For debugging.
        return "'%s id=%d'" % (self.name, self.id)

    def assign_owner_permissions(self, user):
        try:
            permissions = get_perms_for_model(Element)
            for perm in permissions:
                assign_perm(perm.codename, user, self)
            return True
        except Exception:
            return False

    def assign_edit_permissions(self, user):
        try:
            permissions = ["view_element", "change_element", "add_element"]
            for perm in permissions:
                assign_perm(perm, user, self)
            return True
        except Exception:
            return False

    @transaction.atomic
    def remove_element_control(self, oscal_ctl_id, oscal_catalog_key):
        """Remove a selected control from a system.root_element"""

        try:
            if ElementControl.objects.filter(
                element=self,
                oscal_ctl_id=oscal_ctl_id,
                oscal_catalog_key=oscal_catalog_key,
            ).exists():
                ElementControl.objects.get(
                    element=self,
                    oscal_ctl_id=oscal_ctl_id,
                    oscal_catalog_key=oscal_catalog_key,
                ).delete()
            result = True
        except Exception:
            result = False

        return result

    @transaction.atomic
    def assign_baseline_controls(self, user, baselines_key, baseline_name):
        """
        Assign set of controls from baseline to system.root_element
        """

        selected_controls_cur = self.controls.all()
        selected_controls_ids_cur = set(
            [
                f"{sc.oscal_ctl_id}=+={sc.oscal_catalog_key}"
                for sc in selected_controls_cur
            ]
        )

        changed_controls = {"add": [], "remove": [], "no_change": []}

        # Does user have edit permissions on system?
        can_assign_controls = user.has_perm("change_element", self)
        if can_assign_controls:
            bs = Baselines()
            controls = bs.get_baseline_controls(baselines_key, baseline_name)
            for oscal_ctl_id in controls:
                if f"{oscal_ctl_id}=+={baselines_key}" in selected_controls_ids_cur:
                    # Control already in selected, just append to 'no_change' list
                    changed_controls["no_change"].append(
                        f"{oscal_ctl_id}=+={baselines_key}"
                    )
                    next
                else:
                    ec = ElementControl(
                        element=self,
                        oscal_ctl_id=oscal_ctl_id,
                        oscal_catalog_key=baselines_key,
                    )
                    ec.save()
                    changed_controls["add"].append(f"{oscal_ctl_id}=+={baselines_key}")
            selected_controls_ids_new = set(
                [f"{oscal_ctl_id}=+={baselines_key}" for oscal_ctl_id in controls]
            )
            for scc in selected_controls_ids_cur:
                if scc not in selected_controls_ids_new:
                    oscal_ctl_id_rm, catalog_key_rm = scc.split("=+=")
                    remove_result = self.remove_element_control(
                        oscal_ctl_id_rm, catalog_key_rm
                    )
                    if remove_result:
                        changed_controls["remove"].append(scc)
            return True
        else:
            return False

    def statements(self, statement_type):
        """
        Return on the statements of statement_type produced by this element
        """

        smts = Statement.objects.filter(
            producer_element=self, statement_type=statement_type
        )
        return smts

    def consuming_systems(self):
        """
        Return list of systems for which Element is producer_element of statement of
        type control_implementation
        """

        root_element_ids = set(
            filter(
                None,
                [
                    ce["consumer_element"]
                    for ce in Statement.objects.filter(producer_element=self)
                    .values("consumer_element")
                    .distinct()
                ],
            )
        )
        systems = System.objects.filter(
            pk__in=Element.objects.filter(pk__in=root_element_ids).values_list(
                "system", flat=True
            )
        )

        systems_with_projects = []
        for s in systems:
            if s.projects.exists():
                systems_with_projects.append(s)
        systems_with_projects.sort(key=lambda x: x.root_element.name)
        return systems_with_projects

    @property
    def get_control_impl_smts_prototype_count(self):
        """
        Return count of statements with this element as producer_element
        """

        smt_count = Statement.objects.filter(
            producer_element=self,
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name,
        ).count()

        return smt_count

    @transaction.atomic
    def copy(self, name=None):
        """
        Return a copy of an existing system element as a new element with duplicate
        control_implementation_prototype statements
        """

        if self.element_type == "system":
            raise SystemException("Copying an entire system is not permitted.")

        e_copy = deepcopy(self)
        e_copy.id = None
        if name is not None:
            e_copy.name = name
        else:
            e_copy.name = self.name + " copy"
        e_copy.save()
        # Copy prototype statements from existing element
        for smt in self.statements(
            StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name
        ):
            smt_copy = deepcopy(smt)
            smt_copy.producer_element = e_copy
            smt_copy.consumer_element_id = None
            smt_copy.id = None
            smt_copy.save()
        return e_copy

    @property
    def selected_controls_oscal_ctl_ids(self):
        """Return array of selected controls oscal ids"""
        # oscal_ids = self.controls.all()
        oscal_ctl_ids = [control.oscal_ctl_id for control in self.controls.all()]
        # Sort
        oscal_ctl_ids = natsorted(oscal_ctl_ids, key=str.casefold)

        return oscal_ctl_ids


class ElementControl(auto_prefetch.Model):
    class Statuses(models.IntegerChoices):
        NEEDSWORK = 2, "Pending"
        READY = 3, "Implemented"
        ASSESSED = 4, "Assessed"
        CHANGES = 5, "Changes requested"

    element = auto_prefetch.ForeignKey(
        Element,
        related_name="controls",
        on_delete=models.CASCADE,
        help_text="The Element (e.g., System, Component, Host) to which controls are associated.",
    )
    oscal_ctl_id = models.CharField(
        max_length=20,
        help_text="OSCAL formatted Control ID (e.g., au-2.3)",
        blank=True,
        null=True,
    )
    oscal_catalog_key = models.CharField(
        max_length=100,
        help_text="Catalog key from which catalog file can be derived (e.g., \
            'NIST_SP-800-53_rev4')",
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    smts_updated = models.DateTimeField(
        auto_now=False,
        db_index=True,
        help_text="Store date of most recent statement update",
        blank=True,
        null=True,
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=True,
        help_text="A UUID (a unique identifier) for this ElementControl.",
    )
    status = models.IntegerField(default=Statuses.NEEDSWORK, choices=Statuses.choices)

    class Meta:
        unique_together = [("element", "oscal_ctl_id", "oscal_catalog_key")]

    def __str__(self):
        return "'%s id=%d'" % (self.oscal_ctl_id, self.id)

    def __repr__(self):
        # For debugging.
        return "'%s id=%d'" % (self.oscal_ctl_id, self.id)

    def get_flattened_oscal_control_as_dict(self):
        cg = Catalog.GetInstance(catalog_key=self.oscal_catalog_key)
        return cg.get_flattened_control_as_dict(cg.get_control_by_id(self.oscal_ctl_id))

    def get_status(self):
        return self.Statuses(self.status).label


class ElementRole(auto_prefetch.Model):
    role = models.CharField(
        max_length=250,
        help_text="Common name or acronym of the role",
        unique=True,
        blank=False,
        null=False,
    )
    description = models.CharField(
        max_length=255,
        help_text="Brief description of the Element",
        unique=False,
        blank=False,
        null=False,
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return "'%s id=%d'" % (self.role, self.id)

    def __repr__(self):
        # For debugging.
        return "'%s id=%d'" % (self.role, self.id)


class System(auto_prefetch.Model):
    root_element = auto_prefetch.ForeignKey(
        Element,
        related_name="system",
        on_delete=models.CASCADE,
        help_text="The Element that is this System. Element must be type [Application,\
             General Support System]",
    )
    fisma_id = models.CharField(
        max_length=40,
        help_text="The FISMA Id of the system",
        unique=False,
        blank=True,
        null=True,
    )

    def __str__(self):
        return "'System %s id=%d'" % (self.root_element.name, self.id)

    def __repr__(self):
        # For debugging.
        return "'System %s id=%d'" % (self.root_element.name, self.id)

    def assign_owner_permissions(self, user):
        try:
            permissions = get_perms_for_model(System)
            for perm in permissions:
                assign_perm(perm.codename, user, self)
            return True
        except Exception:
            return False

    def assign_edit_permissions(self, user):
        try:
            permissions = ["view_system", "change_system", "add_system"]
            for perm in permissions:
                assign_perm(perm, user, self)
            return True
        except Exception:
            return False

    def add_control(self, catalog_key, control_id):
        """
        Add ElementControl (e.g., selected control) to a system
        """

        control = ElementControl(
            element=self.root_element,
            oscal_catalog_key=catalog_key,
            oscal_ctl_id=control_id,
        )
        control.save()
        return control

    def remove_control(self, control_id):
        """Remove ElementControl (e.g., selected control) from a system"""
        control = ElementControl.objects.get(pk=control_id)

        # Delete Control Statements
        self.root_element.statements_consumed.filter(
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name,
            sid_class=control.oscal_catalog_key,
            sid=control.oscal_ctl_id,
        ).delete()
        control.delete()
        return control

    @transaction.atomic
    def set_security_sensitivity_level(self, security_sensitivity_level):
        """
        Assign Security Sensitivty level to system
        """

        smt = Statement.objects.create(
            statement_type=StatementTypeEnum.SECURITY_SENSITIVITY_LEVEL.name,
            producer_element=self.root_element,
            consumer_element=self.root_element,
            body=security_sensitivity_level,
        )
        return security_sensitivity_level, smt

    @property
    def get_security_sensitivity_level(self):
        """Assign Security Sensitivty level to system"""

        smt, created = Statement.objects.get_or_create(
            statement_type=StatementTypeEnum.SECURITY_SENSITIVITY_LEVEL.name,
            producer_element=self.root_element,
            consumer_element=self.root_element,
        )
        security_sensitivity_level = smt.body
        return security_sensitivity_level

    @transaction.atomic
    def set_security_impact_level(self, security_impact_level):
        """
        Assign one or more of the System Security impact levels (e.g. confidentiality,
        integrity, availability)
        """

        security_objective_smt = self.root_element.statements_consumed.filter(
            statement_type=StatementTypeEnum.SECURITY_IMPACT_LEVEL.name
        )
        if security_objective_smt.exists():
            security_objective_smt.update(body=security_impact_level)
        else:
            # Set the security_impact_level smt for element; should only have 1 statement
            security_objective_smt, created = Statement.objects.get_or_create(
                statement_type=StatementTypeEnum.SECURITY_IMPACT_LEVEL.name,
                producer_element=self.root_element,
                consumer_element=self.root_element,
                body=security_impact_level,
            )
        return security_impact_level, security_objective_smt

    @property
    def get_security_impact_level(self):
        """
        Get one or more of the System Security impact levels (e.g. confidentiality,
        integrity, availability)
        """

        # Get the security_impact_level smt for element; should only have 1 statement
        try:
            smt = Statement.objects.get(
                statement_type=StatementTypeEnum.SECURITY_IMPACT_LEVEL.name,
                producer_element=self.root_element,
                consumer_element=self.root_element,
            )
            security_impact_level = eval(smt.body)  # Evaluate string of dictionary
            return security_impact_level
        except Statement.DoesNotExist:
            return {}

    @property
    def smts_common_controls_as_dict(self):
        common_controls = self.root_element.common_controls.all()
        smts_as_dict = {}
        for cc in common_controls:
            if cc.common_control.oscal_ctl_id in smts_as_dict:
                smts_as_dict[cc.common_control.oscal_ctl_id].append(cc)
            else:
                smts_as_dict[cc.common_control.oscal_ctl_id] = [cc]
        return smts_as_dict

    @property
    def smts_control_implementation_as_dict(self):
        smts = self.root_element.statements_consumed.filter(
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name
        ).order_by("pid")
        smts_as_dict = {}
        for smt in smts:
            if smt.sid in smts_as_dict:
                smts_as_dict[smt.sid]["control_impl_smts"].append(smt)
            else:
                smts_as_dict[smt.sid] = {
                    "control_impl_smts": [smt],
                    "common_controls": [],
                    "combined_smt": "",
                }
        return smts_as_dict

    @cached_property
    def control_implementation_as_dict(self):
        pid_current = None

        # Fetch all selected controls
        elm = self.root_element
        selected_controls = elm.controls.all().values("oscal_ctl_id", "uuid")
        # Get the smts_control_implementations ordered by part, e.g. pid
        smts = elm.statements_consumed.filter(
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name
        ).order_by("pid")

        smts_as_dict = {}

        # Retrieve all of the existing statements
        for smt in smts:
            if smt.sid in smts_as_dict:
                smts_as_dict[smt.sid]["control_impl_smts"].append(smt)
            else:

                try:
                    elementcontrol = self.root_element.controls.get(
                        oscal_ctl_id=smt.sid, oscal_catalog_key=smt.sid_class
                    )
                    smts_as_dict[smt.sid] = {
                        "control_impl_smts": [smt],
                        "common_controls": [],
                        "combined_smt": "",
                        "elementcontrol_uuid": elementcontrol.uuid,
                        "combined_smt_uuid": uuid.uuid4(),
                    }
                except ElementControl.DoesNotExist:
                    # Handle case where Element control does not exist
                    elementcontrol = None
                    smts_as_dict[smt.sid] = {
                        "control_impl_smts": [smt],
                        "common_controls": [],
                        "combined_smt": "",
                        "elementcontrol_uuid": None,
                        "combined_smt_uuid": uuid.uuid4(),
                    }

            # Build combined statement

            # Define status options
            impl_statuses = [
                "Not implemented",
                "Planned",
                "Partially implemented",
                "Implemented",
                "Unknown",
            ]
            status_str = ""
            for status in impl_statuses:
                if (smt.status is not None) and (smt.status.lower() == status.lower()):
                    status_str += f"[x] {status} "
                else:
                    status_str += f'<span style="color: #888;">[ ] {status}</span> '

            if smt.pid != "" and smt.pid != pid_current:
                smts_as_dict[smt.sid]["combined_smt"] += f"{smt.pid}.\n"
                pid_current = smt.pid

            if smt.producer_element:
                smt_formatted = smt.body.replace("\n", "<br/>")
                # TODO: Clean up special characters
                smt_formatted = smt_formatted.replace("\u2019", "'").replace(
                    "\u2022", "<li>"
                )
                smts_as_dict[smt.sid][
                    "combined_smt"
                ] += f"<i>{smt.producer_element.name}</i><br/>{status_str}<br/><br/>\
                    {smt_formatted}<br/><br/>"

        # Populate any controls from assigned baseline that do not have statements
        for ec in selected_controls:
            if ec.get("oscal_ctl_id") not in smts_as_dict:
                smts_as_dict[ec.get("oscal_ctl_id")] = {
                    "control_impl_smts": [],
                    "common_controls": [],
                    "combined_smt": "",
                    "elementcontrol_uuid": ec.get("ec.uuid"),
                    "combined_smt_uuid": uuid.uuid4(),
                }

        # Return the dictionary
        return smts_as_dict

    @cached_property
    def controls_status_count(self):
        """Retrieve counts of control status"""

        status_list = [
            "Not Implemented",
            "Planned",
            "Partially Implemented",
            "Implemented",
            "Unknown",
        ]
        status_stats = {status: 0 for status in status_list}
        # Fetch all selected controls
        elm = self.root_element

        counts = (
            Statement.objects.filter(
                statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name,
                status__in=status_list,
            )
            .filter(consumer_element_id=elm.id)
            .values("status")
            .order_by("status")
            .annotate(count=Count("status"))
        )
        status_stats.update({r["status"]: r["count"] for r in counts})

        # TODO add index on statement status
        # Get overall controls addressed (e.g., covered)
        status_stats["Addressed"] = (
            elm.statements_consumed.filter(
                statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name
            )
            .values("sid")
            .distinct()
            .count()
        )
        return status_stats

    @cached_property
    def poam_status_count(self):
        """Retrieve counts of poam status"""

        # Temporarily hard code status list
        status_list = ["Open", "Closed", "In Progress"]
        # TODO
        # Get a unique filter of status list and gather on that...
        status_stats = {status: 0 for status in status_list}
        # Fetch all system POA&Ms
        counts = (
            Statement.objects.filter(
                statement_type="POAM",
                consumer_element=self.root_element,
                status__in=status_list,
            )
            .values("status")
            .order_by("status")
            .annotate(count=Count("status"))
        )
        status_stats.update({r["status"]: r["count"] for r in counts})
        # TODO add index on statement status
        return status_stats

    # @property (See below for creation of property from method)
    def get_producer_elements(self):
        smts = self.root_element.statements_consumed.all()
        components = set()
        for smt in smts:
            if smt.producer_element:
                components.add(smt.producer_element)
        components = list(components)
        components.sort(key=lambda component: component.name)
        return components

    producer_elements = cached_property(get_producer_elements)

    def get_producer_elements_control_impl_smts_dict(self):
        smts = self.root_element.statements_consumed.filter(
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name
        )
        components_smts = {}
        for smt in smts:
            if smt.producer_element:
                # components.add(smt.producer_element)
                if smt.producer_element in components_smts:
                    components_smts[smt.producer_element].append(smt)
                else:
                    components_smts[smt.producer_element] = [smt]
        return components_smts

    producer_elements_control_impl_smts_dict = cached_property(
        get_producer_elements_control_impl_smts_dict
    )

    def get_producer_elements_control_impl_smts_status_dict(self):
        components_smts = self.producer_elements_control_impl_smts_dict
        components_smts_status = {}
        for component in components_smts.keys():
            cmpt_smts_status = {}
            for smt in components_smts[component]:
                if smt.status in cmpt_smts_status:
                    cmpt_smts_status[smt.status] += 1
                else:
                    cmpt_smts_status[smt.status] = 1
            components_smts_status[component] = cmpt_smts_status
        return components_smts_status

    producer_elements_control_impl_smts_status_dict = cached_property(
        get_producer_elements_control_impl_smts_status_dict
    )

    def set_component_control_status(self, element, status):
        """
        Batch update status of system control implementation statements for a specific element.
        """

        self.root_element.statements_consumed.filter(
            producer_element=element,
            statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name,
        ).update(status=status)
        return True


class CommonControlProvider(models.Model):
    name = models.CharField(
        max_length=150, help_text="Name of the CommonControlProvider", unique=False
    )
    description = models.CharField(
        max_length=255,
        help_text="Brief description of the CommonControlProvider",
        unique=False,
    )

    def __str__(self):
        return self.name


class CommonControl(auto_prefetch.Model):
    name = models.CharField(
        max_length=150,
        help_text="Name of the CommonControl",
        unique=False,
        blank=True,
        null=True,
    )
    description = models.CharField(
        max_length=255,
        help_text="Brief description of the CommonControlProvider",
        unique=False,
    )
    oscal_ctl_id = models.CharField(
        max_length=20,
        help_text="OSCAL formatted Control ID (e.g., au-2.3)",
        blank=True,
        null=True,
    )
    legacy_imp_smt = models.TextField(
        help_text="Legacy large implementation statement",
        unique=False,
        blank=True,
        null=True,
    )
    common_control_provider = auto_prefetch.ForeignKey(
        CommonControlProvider, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name


class ElementCommonControl(auto_prefetch.Model):
    element = auto_prefetch.ForeignKey(
        Element,
        related_name="common_controls",
        on_delete=models.CASCADE,
        help_text="The Element (e.g., System, Component, Host) to which common controls are \
            associated.",
    )
    common_control = auto_prefetch.ForeignKey(
        CommonControl,
        related_name="element_common_control",
        on_delete=models.CASCADE,
        help_text="The Common Control for this association.",
    )
    oscal_ctl_id = models.CharField(
        max_length=20,
        help_text="OSCAL formatted Control ID (e.g., au-2.3)",
        blank=True,
        null=True,
    )
    oscal_catalog_key = models.CharField(
        max_length=100,
        help_text="Catalog key from which catalog file can be derived (e.g., \
            'NIST_SP-800-53_rev4')",
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        unique_together = [
            ("element", "common_control", "oscal_ctl_id", "oscal_catalog_key")
        ]

    def __str__(self):
        return f"{self.element} {self.common_control} {self.oscal_ctl_id} id={self.id}"

    def __repr__(self):
        # For debugging.
        return f"{self.element} {self.common_control} {self.oscal_ctl_id} id={self.id}"


class Baselines(object):
    """Represent list of baselines"""

    def __init__(self):

        self.file_path = BASELINE_PATH
        self.baselines_keys = self._list_keys()

    def _list_keys(self):
        # TODO: only return keys for records that have baselines?
        return list(
            CatalogData.objects.order_by("catalog_key")
            .values_list("catalog_key", flat=True)
            .distinct()
        )

    def _load_json(self, baselines_key):
        """Read baseline file - JSON"""

        catalog_record = CatalogData.objects.get(catalog_key=baselines_key)
        baselines = catalog_record.baselines_json
        if baselines:
            return baselines
        else:
            return False

    def get_baseline_controls(self, baselines_key, baseline_name):
        """
        Return baseline's control OSCAL control ids given baselines key and baseline name
        """

        if baselines_key in self.baselines_keys:
            data = self._load_json(baselines_key)
        else:
            print("Requested baselines_key not found in baselines_key data file")
            return False
        if baseline_name in data.keys():
            return data[baseline_name]["controls"]
        else:
            print("Requested baseline name not found in baselines_key data file")
            return False


class OrgParams(object):
    """
    Represent list of organizational defined parameters. Temporary
    class to work with default org params.
    """

    _singleton = None

    def __new__(cls):
        if cls._singleton is None:
            cls._singleton = super(OrgParams, cls).__new__(cls)
            cls._singleton.init()

        return cls._singleton

    def init(self):
        self.cache = {}

        path = Path(ORGPARAM_PATH)
        for f in path.glob("*.json"):
            name, values = self.load_param_file(f)
            if name in self.cache:
                raise Exception(
                    f"Duplicate default organizational parameters name {name} from {f}"
                )
            self.cache[name] = values

    def load_param_file(self, path):
        with path.open("r") as json_file:
            data = json.load(json_file)
            if "name" in data and "values" in data:
                return (data["name"], data["values"])
            else:
                raise Exception(
                    "Invalid organizational parameters file {}".format(path)
                )

    def get_names(self):
        return self.cache.keys()

    def get_params(self, name):
        return self.cache.get(name, {})


class Poam(models.Model):
    statement = models.OneToOneField(
        Statement,
        related_name="poam",
        unique=False,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="The Poam details for this statement. Statement must be type Poam.",
    )
    poam_id = models.IntegerField(
        unique=False,
        blank=True,
        null=True,
        help_text="The sequential ID for the information system.",
    )
    controls = models.CharField(
        max_length=254,
        unique=False,
        blank=True,
        null=True,
        help_text="Comma delimited list of security controls affected by the weakness identified.",
    )
    weakness_name = models.CharField(
        max_length=254,
        unique=False,
        blank=True,
        null=True,
        help_text="Name for the identified weakness that provides a general idea of the \
            weakness.",
    )
    # weakness_description is found in the Statement.body
    weakness_detection_source = models.CharField(
        max_length=180,
        unique=False,
        blank=True,
        null=True,
        help_text=" Name of organization, vulnerability scanner, or other entity that first \
            identified the weakness.",
    )
    weakness_source_identifier = models.CharField(
        max_length=180,
        unique=False,
        blank=True,
        null=True,
        help_text="ID or reference provided by the detection source identifying the weakness.",
    )
    # asset_identifier is the Statement.producer_element
    remediation_plan = models.TextField(
        unique=False,
        blank=True,
        null=True,
        help_text="A high-level summary of the actions required to remediate the plan.",
    )
    scheduled_completion_date = models.DateTimeField(
        db_index=True,
        unique=False,
        blank=True,
        null=True,
        help_text="Planned completion date of all milestones.",
    )
    milestones = models.TextField(
        unique=False,
        blank=True,
        null=True,
        help_text="One or more milestones that identify specific actions to correct the \
            weakness with an associated completion date.",
    )
    milestone_changes = models.TextField(
        unique=False, blank=True, null=True, help_text="List of changes to milestones."
    )
    risk_rating_original = models.CharField(
        max_length=50,
        unique=False,
        blank=True,
        null=True,
        help_text="The initial risk rating of the weakness.",
    )
    risk_rating_adjusted = models.CharField(
        max_length=50,
        unique=False,
        blank=True,
        null=True,
        help_text="The current or modified risk rating of the weakness.",
    )
    poam_group = models.CharField(
        max_length=50,
        unique=False,
        blank=True,
        null=True,
        help_text="A name to collect related POA&Ms together.",
    )

    def __str__(self):
        return "<Poam %s id=%d>" % (self.statement, self.id)

    def __repr__(self):
        # For debugging.
        return "<Poam %s id=%d>" % (self.statement, self.id)

    def get_next_poam_id(self, system):
        """Count total number of POAMS and return next linear id"""
        return Statement.objects.filter(
            statement_type="POAM", consumer_element=system.root_element
        ).count()


class Deployment(auto_prefetch.Model):
    name = models.CharField(
        max_length=250,
        help_text="Name of the deployment",
        unique=False,
        blank=False,
        null=False,
    )
    description = models.CharField(
        max_length=255,
        help_text="Brief description of the deployment",
        unique=False,
        blank=False,
        null=False,
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=True,
        help_text="A UUID (a unique identifier) for the deployment.",
    )
    system = auto_prefetch.ForeignKey(
        "System",
        related_name="deployments",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="The system associated with the deployment",
    )
    inventory_items = JSONField(
        blank=True,
        null=True,
        help_text="JSON object representing the inventory items in a deployment.",
    )
    history = HistoricalRecords(cascade_delete_history=True)

    def __str__(self):
        return "'%s id=%d'" % (self.name, self.id)

    def __repr__(self):
        # For debugging.
        return "'%s id=%d'" % (self.name, self.id)

    def get_absolute_url(self):
        return "/systems/%d/deployments" % (self.system.id)


class SystemAssessmentResult(auto_prefetch.Model):
    name = models.CharField(
        max_length=250,
        help_text="Name of the system assessment result",
        unique=False,
        blank=False,
        null=False,
    )
    description = models.CharField(
        max_length=255,
        help_text="Brief description of the system assessment result",
        unique=False,
        blank=True,
        null=True,
    )
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=True,
        help_text="A UUID (a unique identifier) for the system assessment result.",
    )
    system = auto_prefetch.ForeignKey(
        "System",
        related_name="system_assessment_result",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="The system associated with the system assessment result",
    )
    deployment = auto_prefetch.ForeignKey(
        Deployment,
        related_name="assessment_results",
        unique=False,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The deployment associated with the assessment result.",
    )
    assessment_results = JSONField(
        blank=True,
        null=True,
        help_text="JSON object representing the system assessment results associated \
            with a deployment.",
    )
    history = HistoricalRecords(cascade_delete_history=True)

    def __str__(self):
        return "<SystemAssesmentResult %s id=%d>" % (self.system, self.id)

    def __repr__(self):
        # For debugging.
        return "<SystemAssesmentResult %s id=%d>" % (self.system, self.id)
