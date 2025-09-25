#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class property_unit_image(models.Model):
	_inherit = "vit.property_unit_image"

	@api.model_create_multi
	def create(self, vals):
		for val in vals:
			if not val.get("name", False) or val["name"] == "New":
				unit = self.env["vit.property_unit"].browse(val["property_unit_id"])
				seq = val.get("sequence", 0)
				val["name"] = f"{unit.name} - {seq}"
		return super(property_unit_image, self).create(vals)