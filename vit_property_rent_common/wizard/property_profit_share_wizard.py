from odoo import models, fields, api, _
from odoo.exceptions import UserError
import math
import logging
_logger = logging.getLogger(__name__)

class PropertyProfitShareWizard(models.TransientModel):
	_name = "vit.property_profit_share_wizard"
	_description = "Wizard Buat Profit Share Baru"

	rent_transaction_id = fields.Many2one(
		comodel_name="vit.rent_transaction",
		string="Rent Transaction",
		required=True,
		readonly=True
	)
	start_date = fields.Datetime(string="Start Date", required=True)
	end_date = fields.Datetime(string="End Date", required=True)
	property_unit_id = fields.Many2one("vit.property_unit", string="Property", readonly=True)
	total_profit_share_amount = fields.Float(readonly=True, string="Total Profit Share Amount",)

	def action_create_profit_share(self):
		for rec in self:
			if not rec.total_profit_share_amount:
				raise UserError(_("Total profit share amount must be set."))

			if rec.start_date < rec.rent_transaction_id.start_date:
				raise UserError(_("Rental period has not started."))

			confirmed_orders = self.env['vit.order_token'].search([
				('property_unit_id', '=', rec.property_unit_id.id),
				('status', '=', 'confirmed'),
				('create_date', '<=', rec.end_date),
			])
			if not confirmed_orders:
				raise UserError(_("No confirmed investor orders found."))

			total_sold = sum(confirmed_orders.mapped('qty_token'))
			total_token = rec.property_unit_id.total_tokens
			if total_sold <= 0:
				raise UserError(_("Total sold tokens must be greater than zero."))

			investor_map = {}
			for order in confirmed_orders:
				partner = order.to_partner_id
				if not partner:
					continue
				investor_map.setdefault(partner.id, 0)
				investor_map[partner.id] += order.qty_token

			new_headers = []
			for inv_id, token_count in investor_map.items():
				proportion = token_count / total_token
				amount = proportion * rec.total_profit_share_amount

				existing_header = self.env['vit.property_profit_share'].search([
					('investor_id', '=', inv_id),
					('property_unit_id', '=', rec.property_unit_id.id),
					('rent_transaction_id', '=', rec.rent_transaction_id.id),
				], limit=1)

				if existing_header:
					header = existing_header
					existing_line = self.env['vit.property_profit_share_line'].search([
						('profit_share_id', '=', header.id),
						('start_date', '=', rec.start_date),
						('end_date', '=', rec.end_date),
					], limit=1)
					if existing_line:
						raise UserError(_("Profit share for this period already exists for investor %s.") % header.investor_id.name)

					header.write({
						'total_revenue': header.total_revenue + amount,
					})
				else:
					header = self.env['vit.property_profit_share'].create({
						'name': self.env["ir.sequence"].next_by_code("vit.property_profit_share") or "Error Number!!!",
						'start_date': self.rent_transaction_id.start_date,
						'end_date': self.rent_transaction_id.end_date,
						'total_profit_share_amount': rec.total_profit_share_amount,   
						'total_revenue': amount,   
						'property_unit_id': rec.property_unit_id.id,
						'investor_id': inv_id,
						'rent_transaction_id': rec.rent_transaction_id.id,
					})

				token_reward_count = int(amount // rec.property_unit_id.price_per_token)
				self.env['vit.property_profit_share_line'].create({
					'name': f"{header.name} - {rec.start_date.strftime('%B %Y')}",
					'start_date': rec.start_date,
					'end_date': rec.end_date,
					'token_count': token_reward_count,
					'amount': amount,
					'profit_share_id': header.id,
				})

				if token_reward_count > 0:
					existing_tokens = self.env["product.product"].search_count([
						("property_unit_id", "=", rec.property_unit_id.id),
						("token_type", "=", "token_reward")
					])
					start_index = existing_tokens + 1
					Product = self.env["product.product"].sudo()
					vals_list = []
					for i in range(token_reward_count):
						seq = start_index + i
						vals_list.append({
							"name": f"{rec.property_unit_id.name} - Token {seq}",
							"list_price": rec.property_unit_id.price_per_token,
							"taxes_id": [(6, 0, [])],
							"supplier_taxes_id": [(6, 0, [])],
							"type": "service",
							"token_state": "sold",
							"token_type": "token_reward",
							"is_investment_token": True,
							"property_unit_id": rec.property_unit_id.id,
							"token_owner_id": inv_id,
							"token_code": f"{rec.property_unit_id.id}-{seq:03d}",
						})
					Product.create(vals_list)

				partner = self.env['res.partner'].browse(inv_id)
				partner.write({
					'total_tokens': partner.total_tokens + token_reward_count,
					'total_dividend_received': partner.total_dividend_received + amount,
				})

				header.stage_id = header._get_next_stage()
				new_headers.append(header.id)

		return True