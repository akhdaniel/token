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

	# def unlink(self):
	# 	for me_id in self :
	# 		if not me_id.stage_id.draft:
	# 			raise UserError("Cannot delete non draft record!  Make sure that the Stage draft flag is checked.")
	# 	return super(property_profit_share, self).unlink()


	def action_confirm(self):
		"""Hitung dan buat detail profit share per investor"""
		for rec in self:
			if not rec.total_profit_share_amount:
				raise UserError(_("Total profit share amount must be set."))

			# 1) Cari token terjual untuk property ini
			sold_tokens = self.env['product.product'].search([
				('property_unit_id', '=', rec.property_unit_id.id),
				# ('token_state', '=', 'sold')
			])

			if not sold_tokens:
				raise UserError(_("No sold tokens found for this property."))

			total_sold = len(sold_tokens)

			# 2) Hitung kepemilikan token per investor
			confirmed_orders = self.env['vit.order_token'].search([
				('property_unit_id', '=', rec.property_unit_id.id),
				('status', '=', 'confirmed'),
				('to_partner_id', '=', rec.investor_id.id),
			])

			if not confirmed_orders:
				raise UserError(_("No confirmed investor orders found."))

			# Map investor -> total token yg dimiliki
			investor_map = {}
			for order in confirmed_orders:
				if not order.to_partner_id:
					continue
				investor_map.setdefault(order.to_partner_id.id, 0)
				investor_map[order.to_partner_id.id] += order.qty_token

			# 3) Buat detail profit share per investor
			line_vals = []
			for inv_id, token_count in investor_map.items():
				proportion = token_count / total_sold
				amount = proportion * rec.total_profit_share_amount
				line_vals.append({
					'name': rec.name,
					'token_count': amount / rec.property_unit_id.price_per_token,
					'amount': amount,
					'profit_share_id': rec.id,
				})

			# hapus detail lama (opsional)
			rec.profit_share_line_ids.unlink()
			self.env['vit.property_profit_share_line'].create(line_vals)

			# 4) Pindahkan ke stage berikut (menggunakan logic stage bawaan)
			next_stage = rec._get_next_stage()
			rec.stage_id = next_stage
			if rec.stage_id.execute_enter and \
			   hasattr(rec, rec.stage_id.execute_enter) and \
			   callable(getattr(rec, rec.stage_id.execute_enter)):
				eval(f"rec.{rec.stage_id.execute_enter}()")
