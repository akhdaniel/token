# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class PropertyProfitShare(models.Model):
	_inherit = "vit.property_profit_share"

	rent_transaction_id = fields.Many2one(
		comodel_name="vit.rent_transaction",
		string="Rent Transaction",
		help="Transaksi sewa yang terkait dengan profit sharing ini"
	)
	total_profit_share_amount = fields.Float(compute="_compute_amount_to_share")

	@api.depends('rent_transaction_id')
	def _compute_amount_to_share(self):
		for rec in self:
			rec.total_profit_share_amount = rec.rent_transaction_id.rent_price_per_month
			rec.property_unit_id = rec.rent_transaction_id.property_unit_id
