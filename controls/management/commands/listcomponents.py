# Usage:
#   python manage.py listcomponents --type <system_element | system>  (default type = system_element)
#
# Example:
#   python3 manage.py listcomponents --type system_element
#
# Example Docker:
#   docker exec -it govready-q-dev python3 manage.py listcomponents --type system_element
#   docker exec -it govready-q-dev python3 manage.py listcomponents --type system

import logging
import os.path
import sys
from collections import defaultdict
from pathlib import Path, PurePath

import fs
import fs.errors
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction
from django.db.utils import OperationalError
from django.utils.text import slugify

from controls.enums.remotes import RemoteTypeEnum
from controls.enums.statements import StatementTypeEnum
from controls.models import Element, ImportRecord, Statement, StatementRemote
from controls.oscal import *
from controls.views import ComponentImporter, OSCALComponentSerializer

logging.basicConfig()
import structlog
from structlog import get_logger
from structlog.stdlib import LoggerFactory

structlog.configure(logger_factory=LoggerFactory())
structlog.configure(processors=[structlog.processors.JSONRenderer()])
logger = get_logger()


class Command(BaseCommand):
    help = 'Generate list of component ids and component name'

    def add_arguments(self, parser):
        parser.add_argument('--type', metavar='type', nargs='?', required=False, type=str, default="system_element", help="Component (AKA element) type to export")
        parser.add_argument('--orderby', metavar='orderby', nargs='?', required=False, type=str, default="id", help="Order results by id or name")

    def handle(self, *args, **options):

        # Set up
        element_type = options['type']
        orderby = options['orderby']

        if orderby == "name":
            elements = Element.objects.filter(element_type=element_type).order_by('name')
        else:
            elements = Element.objects.filter(element_type=element_type).order_by('id')

        for e in elements:
            print(f"{e.id}\t{e.name}")
