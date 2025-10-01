#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class order_token(models.Model):
	"""
	{
	"menu":0
	}
	"""

	_name = "vit.order_token"
	_description = "vit.order_token"


	def action_reload_view(self):
		pass


	_inherit = "vit.order_token"


	token_resell_id = fields.Many2one(comodel_name="vit.token_resell",  string=_("Token Resell"))
