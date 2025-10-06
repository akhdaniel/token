#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class property_profit_share_line(models.Model):
	"""
	{
	"menu":0
	}
	"""

	_name = "vit.property_profit_share_line"
	_description = "vit.property_profit_share_line"


	def action_reload_view(self):
		pass

	name = fields.Char( required=True, copy=False, string=_("Name"))
	amount = fields.Float( string=_("Amount"))
	token_count = fields.Integer( string=_("Token Count"))


	def copy(self, default=None):
		default = dict(default or {})
		default.update({
			'name': self.name + ' (Copy)'
		})
		return super(property_profit_share_line, self).copy(default)

	profit_share_id = fields.Many2one(comodel_name="vit.property_profit_share", string="Profit Share Allocation", required=True)
