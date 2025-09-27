#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class property_profit_share(models.Model):
	_name = "vit.property_profit_share"
	_inherit = "vit.property_profit_share"

	stage_id = fields.Many2one(
		comodel_name="vit.stage",
		string="Stage",
		default=lambda self: self._get_first_stage(),
		copy=False,
		group_expand="_group_expand_states",
		domain=lambda self: [
			('model_id', '=', self.env['ir.model']._get_id('vit.property_profit_share'))
		],
	)
	
	@api.model_create_multi
	def create(self, vals):
		return super(property_profit_share, self).create(vals)

	def _get_first_stage(self):
		try:
			data_id = self.env["vit.stage"].sudo().search([('model_id', '=', self.env['ir.model']._get_id(self._name))], limit=1, order="sequence asc")
			if data_id:
				return data_id
		except KeyError:
			return False

	def action_confirm(self):
		stage = self._get_next_stage()
		self.stage_id=stage
		if self.stage_id.execute_enter and hasattr(self, self.stage_id.execute_enter) and callable(getattr(self, self.stage_id.execute_enter)):
			eval(f"self.{self.stage_id.execute_enter}()")

	def action_cancel(self):
		stage = self._get_previous_stage()
		self.stage_id=stage

	def _get_next_stage(self):
		current_stage_seq = self.stage_id.sequence
		data_id = self.env["vit.stage"].sudo().search([
			('model_id', '=', self.env['ir.model']._get_id(self._name)),
			("sequence",">",current_stage_seq)
		], limit=1, order="sequence asc")
		if data_id:
			return data_id
		else:
			return self.stage_id

	def _get_previous_stage(self):
		current_stage_seq = self.stage_id.sequence
		data_id = self.env["vit.stage"].sudo().search([('model_id', '=', self.env['ir.model']._get_id(self._name)),("sequence","<",current_stage_seq)], limit=1, order="sequence desc")
		if data_id:
			return data_id
		else:
			return self.stage_id

	@api.model
	def _group_expand_states(self, stages, domain, order):
		return self.env['vit.stage'].search([('model_id', '=', self.env['ir.model']._get_id(self._name))])

	def unlink(self):
		for me_id in self :
			if not me_id.stage_id.draft:
				raise UserError("Cannot delete non draft record!  Make sure that the Stage draft flag is checked.")
		return super(property_profit_share, self).unlink()

	def action_confirm(self):
		pass

	# def action_confirm(self):
	# 	for rec in self:
	# 		if not rec.total_profit_share_amount:
	# 			raise UserError(_("Total profit share amount must be set."))

	# 		confirmed_orders = self.env['vit.order_token'].search([
	# 			('property_unit_id', '=', rec.property_unit_id.id),
	# 			('status', '=', 'confirmed'),
	# 		])
	# 		if not confirmed_orders:
	# 			raise UserError(_("No confirmed investor orders found."))

	# 		total_sold = sum(confirmed_orders.mapped('qty_token'))
	# 		if total_sold <= 0:
	# 			raise UserError(_("Total sold tokens must be greater than zero."))

	# 		investor_map = {}
	# 		for order in confirmed_orders:
	# 			partner = order.to_partner_id
	# 			if not partner:
	# 				continue
	# 			investor_map.setdefault(partner.id, 0)
	# 			investor_map[partner.id] += order.qty_token

	# 		new_headers = []
	# 		for inv_id, token_count in investor_map.items():
	# 			proportion = token_count / total_sold
	# 			amount = proportion * rec.total_profit_share_amount

	# 			new_header = self.env['vit.property_profit_share'].create({
	# 				'name': f"{rec.name} - {self.env['res.partner'].browse(inv_id).name}",
	# 				'start_date': rec.start_date,
	# 				'end_date': rec.end_date,
	# 				'total_revenue': rec.total_revenue,
	# 				'total_profit_share_amount': amount,   
	# 				'property_unit_id': rec.property_unit_id.id,
	# 				'investor_id': inv_id,
	# 				'rent_transaction_id': self.rent_transaction_id.id,
	# 				'property_unit_id': self.property_unit_id.id,
	# 				'stage_id': rec.stage_id.id,  
	# 			})

	# 			self.env['vit.property_profit_share_line'].create({
	# 				'name': new_header.name,
	# 				'token_count': token_count,
	# 				'amount': amount,
	# 				'profit_share_id': new_header.id,
	# 			})
	# 			new_headers.append(new_header.id)

	# 		rec.stage_id = rec._get_next_stage()

	# 	return True
