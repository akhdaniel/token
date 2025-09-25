#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class sale_order_line(models.Model):
	_name = "sale.order.line"
	_inherit = "sale.order.line"
