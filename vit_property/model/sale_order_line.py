#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class sale_order_line(models.Model):

	_name = "sale.order.line"
	_description = "sale.order.line"


	def action_reload_view(self):
		pass


	_inherit = "sale.order.line"


