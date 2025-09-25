#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class product_product(models.Model):
	"""
	{
	"menu":0
	}
	"""

	_name = "product.product"
	_description = "product.product"


	def action_reload_view(self):
		pass


	_inherit = "product.product"
	is_investment_token = fields.Boolean( string=_("Is Investment Token"))
	token_code = fields.Char( string=_("Token Code"))
	token_state = fields.Selection(selection=[("available", "Available"),("reserved", "Reserved"),("sold", "Sold")],default="available",  string=_("Token State"))


	property_unit_id = fields.Many2one(comodel_name="vit.property_unit",  string=_("Property Unit"))
