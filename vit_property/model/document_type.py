#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class document_type(models.Model):
	"""
	{
	"data":[
	{"name":"Sertifikat Hak Atas Tanah / Bangunan", "code":"SHM"},
	{"name":"Izin Mendirikan Bangunan", "code":"IMB"},
	{"name":"Sertifikat Laik Fungsi", "code":"SLF"},
	{"name":"Surat Pemberitahuan Pajak Terutang Pajak Bumi Bangunan", "code":"SPPT PBB"}
	]
	}
	"""

	_name = "vit.document_type"
	_description = "vit.document_type"


	def action_reload_view(self):
		pass

	name = fields.Char( required=True, copy=False, string=_("Name"))
	code = fields.Char( string=_("Code"))


	def copy(self, default=None):
		default = dict(default or {})
		default.update({
			'name': self.name + ' (Copy)'
		})
		return super(document_type, self).copy(default)

