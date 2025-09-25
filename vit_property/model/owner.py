#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class owner(models.Model):

	_name = "res.partner"
	_description = "res.partner"


	def action_reload_view(self):
		pass


	_inherit = "res.partner"
	is_owner = fields.Boolean( string=_("Is Owner"))


