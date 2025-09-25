#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class stage(models.Model):

	_name = "vit.stage"
	_description = "vit.stage"

	_order = "sequence asc"

	def action_reload_view(self):
		pass

	name = fields.Char( required=True, copy=False, string=_("Name"))
	sequence = fields.Integer( string=_("Sequence"))
	done = fields.Boolean( string=_("Done"))
	draft = fields.Boolean( string=_("Draft"))
	fold = fields.Boolean( string=_("Fold"))
	on_progress = fields.Boolean( string=_("On Progress"))
	active = fields.Boolean( string=_("Active"))
	execute_enter = fields.Char( string=_("Execute Enter"))
	allow_confirm = fields.Boolean( string=_("Allow Confirm"))
	allow_cancel = fields.Boolean( string=_("Allow Cancel"))
	confirmation = fields.Char( string=_("Confirmation"))


	def copy(self, default=None):
		default = dict(default or {})
		default.update({
			'name': self.name + ' (Copy)'
		})
		return super(stage, self).copy(default)

	model_id = fields.Many2one(comodel_name="ir.model", string="Related Model", help="The module this stage belongs to.")
