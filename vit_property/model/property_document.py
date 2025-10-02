#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class property_document(models.Model):

	_name = "vit.property_document"
	_description = "vit.property_document"


	def action_reload_view(self):
		pass

	document_file = fields.Binary( string=_("Document File"))
	file_name = fields.Char( string=_("File Name"))
	date_expiry = fields.Date( string=_("Date Expiry"))
	issue_date = fields.Date( string=_("Issue Date"))


	def copy(self, default=None):
		default = dict(default or {})
		default.update({
			'name': self.name + ' (Copy)'
		})
		return super(property_document, self).copy(default)

	name = fields.Many2one(comodel_name="vit.document_type",  required=True, copy=False, string=_("Name"))
	property_unit_id = fields.Many2one(comodel_name="vit.property_unit",  string=_("Property Unit"))
