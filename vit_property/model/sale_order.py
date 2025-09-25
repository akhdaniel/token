#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class sale_order(models.Model):

	_name = "sale.order"
	_description = "sale.order"


	def action_reload_view(self):
		pass


	_inherit = "sale.order"


