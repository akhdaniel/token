#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class property_unit(models.Model):
	"""
	{
	"menu":0
	}
	"""

	_name = "vit.property_unit"
	_description = "vit.property_unit"


	def action_reload_view(self):
		pass


	_inherit = "vit.property_unit"


	rent_type_id = fields.Many2one(comodel_name="vit.rent_type",  string=_("Rent Type"))
