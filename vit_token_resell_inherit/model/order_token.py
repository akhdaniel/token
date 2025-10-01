#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class order_token(models.Model):
	_name = "vit.order_token"
	_inherit = "vit.order_token"
