#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class stage(models.Model):
	"""
	{
	"menu":0
	}
	"""

	_name = "vit.stage"
	_description = "vit.stage"


	def action_reload_view(self):
		pass


	_inherit = "vit.stage"


