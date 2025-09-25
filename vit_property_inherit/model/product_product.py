#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class product_product(models.Model):
	_name = "product.product"
	_inherit = "product.product"

	_order = "token_code asc" 
