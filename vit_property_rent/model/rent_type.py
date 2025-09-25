#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class rent_type(models.Model):

	_name = "vit.rent_type"
	_description = "vit.rent_type"


	def action_reload_view(self):
		pass

	name = fields.Char( required=True, copy=False, string=_("Name"))
	period = fields.Integer( string=_("Period"))
	date = fields.Date( string=_("Date"))


	def copy(self, default=None):
		default = dict(default or {})
		default.update({
			'name': self.name + ' (Copy)'
		})
		return super(rent_type, self).copy(default)

