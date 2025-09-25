#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class currency(models.Model):

	_name = "res.currency"
	_description = "res.currency"


	def action_reload_view(self):
		pass


	_inherit = "res.currency"


