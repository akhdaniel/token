#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class investor(models.Model):
	"""
	{
	"menu":0
	}
	"""

	_name = "res.partner"
	_description = "res.partner"


	def action_reload_view(self):
		pass


	_inherit = "res.partner"


