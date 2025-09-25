#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class property_unit_image(models.Model):

	_name = "vit.property_unit_image"
	_description = "vit.property_unit_image"

	_order = "sequence asc"

	def action_reload_view(self):
		pass

	name = fields.Char( required=True, copy=False, default="New",  string=_("Name"))
	sequence = fields.Integer( string=_("Sequence"))
	image = fields.Binary( string=_("Image"))


	def copy(self, default=None):
		default = dict(default or {})
		default.update({
			'name': self.name + ' (Copy)'
		})
		return super(property_unit_image, self).copy(default)

	property_unit_id = fields.Many2one(comodel_name="vit.property_unit",  string=_("Property Unit"))
