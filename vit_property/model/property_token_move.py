#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class property_token_move(models.Model):

	_name = "vit.property_token_move"
	_description = "vit.property_token_move"


	def action_reload_view(self):
		pass

	name = fields.Char( required=True, copy=False, string=_("Name"))
	reference = fields.Char( string=_("Reference"))
	date = fields.Datetime( string=_("Date"))


	def copy(self, default=None):
		default = dict(default or {})
		default.update({
			'name': self.name + ' (Copy)'
		})
		return super(property_token_move, self).copy(default)

	token_id = fields.Many2one(comodel_name="sale.order.line",  string=_("Token"))
	from_partner_id = fields.Many2one(comodel_name="res.partner",  string=_("From Partner"))
	to_partner_id = fields.Many2one(comodel_name="res.partner",  string=_("To Partner"))
	account_move_id = fields.Many2one(comodel_name="account.move",  string=_("Account Move"))
	order_token_id = fields.Many2one(comodel_name="vit.order_token",  string=_("Order Token"))
