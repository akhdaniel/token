from odoo import models, fields, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class rent_transaction(models.Model):
	_name = "vit.rent_transaction"
	_inherit = "vit.rent_transaction"

	property_profit_share_ids = fields.One2many(comodel_name="vit.property_profit_share",  inverse_name="rent_transaction_id", string="Profit Shares")
	property_profit_share_count = fields.Integer(compute="_compute_profit_share_count", string="Profit Share Count")

	@api.depends('property_profit_share_ids')
	def _compute_profit_share_count(self):
		for rec in self:
			rec.property_profit_share_count = len(rec.property_profit_share_ids)

	def action_open_profit_share_tree(self):
		self.ensure_one()
		return {
			'name': 'Property Profit Shares',
			'type': 'ir.actions.act_window',
			'view_mode': 'list,form',
			'res_model': 'vit.property_profit_share',
			'domain': [('rent_transaction_id', '=', self.id)],
			'context': dict(self.env.context, create=False)
		}
