#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class property_unit(models.Model):
	_name = "vit.property_unit"
	_inherit = "vit.property_unit"
