#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class product_template(models.Model):
	_name = "product.template"
	_inherit = "product.template"

	total_tokens = fields.Integer( string=_("Total Tokens"))

	@api.model_create_multi
	def create(self, vals_list):
		products = super().create(vals_list)
		for product, vals in zip(products, vals_list):
			if vals.get('is_property'):
				self.env['vit.property_unit'].create({
					'product_template_id': product.id,
					'name': product.name,
					'currency_id': product.currency_id.id,
					'sale_price': product.list_price,
					'cost_price': product.standard_price,
				})
		return products