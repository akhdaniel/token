#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class product_template(models.Model):

	_name = "product.template"
	_description = "product.template"


	def action_reload_view(self):
		pass


	_inherit = "product.template"
	is_property = fields.Boolean( string=_("Is Property"))
	total_tokens = fields.Integer( string=_("Total Tokens"))


