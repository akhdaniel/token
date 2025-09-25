#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class rent_transaction(models.Model):
	_name = "vit.rent_transaction"
	_inherit = "vit.rent_transaction"

	stage_id = fields.Many2one(
		comodel_name="vit.stage",
		string="Stage",
		default=lambda self: self._get_first_stage(),
		copy=False,
		group_expand="_group_expand_states",
		domain=lambda self: [
			('model_id', '=', self.env['ir.model']._get_id('vit.rent_transaction'))
		],
	)
	end_date = fields.Date(compute="_compute_dates_amount", store=True)
	amount_total_rent = fields.Float(compute="_compute_dates_amount", store=True)
	rent_price_per_month = fields.Float(compute='_compute_rent_price', store=True)
	rent_type_id = fields.Many2one(comodel_name="vit.rent_type", related="property_unit_id.rent_type_id",  string=_("Rent Type"))

	@api.depends('property_unit_id.rental_price')
	def _compute_rent_price(self):
		for rec in self:
			rec.rent_price_per_month = rec.property_unit_id.rental_price
			
	@api.depends("start_date", "duration", "rent_type_id", "rent_price_per_month")
	def _compute_dates_amount(self):
		for rec in self:
			end_date = False
			if rec.start_date and rec.duration and rec.rent_type_id:
				# tentukan jumlah bulan / tahun
				name = (rec.rent_type_id.name or "").lower()
				if "month" in name:
					end_date = rec.start_date + relativedelta(months=rec.duration)
				elif "year" in name:
					end_date = rec.start_date + relativedelta(years=rec.duration)
			rec.end_date = end_date
			# total harga sewa
			rec.amount_total_rent = (rec.duration or 0) * (rec.rent_price_per_month or 0)

	@api.model_create_multi
	def create(self, vals):
		return super(rent_transaction, self).create(vals)

	def _get_first_stage(self):
		try:
			data_id = self.env["vit.stage"].sudo().search([('model_id', '=', self.env['ir.model']._get_id('vit.rent_transaction'))], limit=1, order="sequence asc")
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
		data_id = self.env["vit.stage"].sudo().search([('model_id', '=', self.env['ir.model']._get_id('vit.rent_transaction')),("sequence",">",current_stage_seq)], limit=1, order="sequence asc")
		if data_id:
			return data_id
		else:
			return self.stage_id

	def _get_previous_stage(self):
		current_stage_seq = self.stage_id.sequence
		data_id = self.env["vit.stage"].sudo().search([('model_id', '=', self.env['ir.model']._get_id('vit.rent_transaction')),("sequence","<",current_stage_seq)], limit=1, order="sequence desc")
		if data_id:
			return data_id
		else:
			return self.stage_id

	@api.model
	def _group_expand_states(self, stages, domain, order):
		return self.env['vit.stage'].search([('model_id', '=', self.env['ir.model']._get_id('vit.rent_transaction'))])

	def unlink(self):
		for me_id in self :
			if not me_id.stage_id.draft:
				raise UserError("Cannot delete non draft record!  Make sure that the Stage draft flag is checked.")
		return super(rent_transaction, self).unlink()
