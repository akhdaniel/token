from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PropertyProfitShareWizard(models.TransientModel):
	_name = "vit.property_profit_share_wizard"
	_description = "Wizard Buat Profit Share Baru"

	rent_transaction_id = fields.Many2one(
		comodel_name="vit.rent_transaction",
		string="Rent Transaction",
		required=True,
		readonly=True
	)
	start_date = fields.Date(string="Start Date", required=True)
	end_date = fields.Date(string="End Date", required=True)
	property_unit_id = fields.Many2one("vit.property_unit", string="Property", readonly=True)
	total_profit_share_amount = fields.Float(string="Total Profit Share Amount",)

	def action_create_profit_share(self):
		for rec in self:
			if not rec.total_profit_share_amount:
				raise UserError(_("Total profit share amount must be set."))

			confirmed_orders = self.env['vit.order_token'].search([
				('property_unit_id', '=', rec.property_unit_id.id),
				('status', '=', 'confirmed'),
			])
			if not confirmed_orders:
				raise UserError(_("No confirmed investor orders found."))

			total_sold = sum(confirmed_orders.mapped('qty_token'))
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
				proportion = token_count / total_sold
				amount = proportion * rec.total_profit_share_amount

				new_header = self.env['vit.property_profit_share'].create({
					'name': self.env["ir.sequence"].next_by_code("vit.property_profit_share") or "Error Number!!!",
					'start_date': rec.start_date,
					'end_date': rec.end_date,
					'total_profit_share_amount': amount,   
					'property_unit_id': rec.property_unit_id.id,
					'investor_id': inv_id,
					'rent_transaction_id': self.rent_transaction_id.id,
					'property_unit_id': self.property_unit_id.id,
				})

				self.env['vit.property_profit_share_line'].create({
					'name': new_header.name,
					'token_count': token_count,
					'amount': amount,
					'profit_share_id': new_header.id,
				})
				new_header.stage_id = new_header._get_next_stage()
				new_headers.append(new_header.id)
		return True

