#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class model(models.Model):
	"""
	{
	"menu":0
	}
	"""

	_name = "ir.model"
	_description = "ir.model"


	def action_reload_view(self):
		pass


	_inherit = "ir.model"


