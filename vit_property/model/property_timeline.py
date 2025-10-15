#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class property_timeline(models.Model):

	_name = "vit.property_timeline"
	_description = "vit.property_timeline"


	def action_reload_view(self):
		pass

	name = fields.Char( required=True, copy=False, string=_("Name"))
	description = fields.Text( string=_("Description"))
	timeline_date = fields.Datetime( string=_("Timeline Date"))
	status = fields.Selection(selection=[('plan','Plan'),('ongoing','Ongoing'),('done','Done')],  string=_("Status"))


	def copy(self, default=None):
		default = dict(default or {})
		default.update({
			'name': self.name + ' (Copy)'
		})
		return super(property_timeline, self).copy(default)

	property_unit_id = fields.Many2one(comodel_name="vit.property_unit",  string=_("Property Unit"))
