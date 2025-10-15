#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class property_financial(models.Model):

	_name = "vit.property_financial"
	_description = "vit.property_financial"


	def action_reload_view(self):
		pass

	total_investment = fields.Float( string=_("Total Investment"))
	property_upgrade = fields.Float( string=_("Property Upgrade"))
	notaris_fee = fields.Float( string=_("Notaris Fee"))
	platform_fee = fields.Float( string=_("Platform Fee"))


	def copy(self, default=None):
		default = dict(default or {})
		default.update({
			'name': self.name + ' (Copy)'
		})
		return super(property_financial, self).copy(default)

	name = fields.Many2one(comodel_name="vit.property_unit",  required=True, copy=False, string=_("Name"))
