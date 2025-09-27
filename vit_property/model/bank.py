#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class bank(models.Model):

	_name = "res.partner.bank"
	_description = "res.partner.bank"


	def action_reload_view(self):
		pass


	_inherit = "res.partner.bank"


