#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class account_move(models.Model):

	_name = "account.move"
	_description = "account.move"


	def action_reload_view(self):
		pass


	_inherit = "account.move"


