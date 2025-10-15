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
	end_date = fields.Datetime(compute="_compute_dates_amount", store=True)
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
				name = (rec.rent_type_id.name or "").lower()
				if "month" in name:
					end_date = rec.start_date + relativedelta(months=rec.duration)
				elif "year" in name:
					end_date = rec.start_date + relativedelta(years=rec.duration)
			rec.end_date = end_date
			rec.transaction_date = rec.start_date
			rec.amount_total_rent = (rec.duration or 0) * (rec.rent_price_per_month or 0)

	@api.onchange("property_unit_id")
	def _onchange_property_unit_id(self, ):
		self.rent_price_per_month = self.property_unit_id.rental_price
		self.rent_type_id = self.property_unit_id.rent_type_id

		active_rent = self.env["vit.rent_transaction"].search([
			("property_unit_id", "=", self.property_unit_id.id),
			("end_date", ">=", fields.Datetime.now()),  
		], limit=1)

		if active_rent:
			raise UserError(_(
				"Properti ini masih dalam masa sewa!\n"
				"Transaksi aktif: %s\nPeriode: %s → %s"
			) % (
				active_rent.name,
				active_rent.start_date.strftime("%d-%m-%Y") if active_rent.start_date else "-",
				active_rent.end_date.strftime("%d-%m-%Y") if active_rent.end_date else "-"
			))

	@api.model_create_multi
	def create(self, vals):
		for val in vals:
			start_date = val.get("start_date")
			duration = val.get("duration")

			rent_type = None
			rent_type_id = val.get("rent_type_id")
			property_unit_id = val.get("property_unit_id")
			if not rent_type_id and property_unit_id:
				rent_type = self.env["vit.property_unit"].browse(property_unit_id).rent_type_id
				rent_type_id = rent_type.id if rent_type else None
			elif rent_type_id:
				rent_type = self.env["vit.rent_type"].browse(rent_type_id)

			if start_date and duration and rent_type:
				name = (rent_type.name or "").lower()
				start_dt = fields.Datetime.from_string(start_date)
				if "month" in name:
					val["end_date"] = start_dt + relativedelta(months=duration)
				elif "year" in name:
					val["end_date"] = start_dt + relativedelta(years=duration)

			if property_unit_id and start_date and val.get("end_date"):
				overlapping = self.env["vit.rent_transaction"].search([
					("property_unit_id", "=", property_unit_id),
					("end_date", ">=", start_date),
					("start_date", "<=", val["end_date"]),
				], limit=1)
				if overlapping:
					raise UserError(_(
						"Property unit ini masih dalam masa sewa!\n"
						"Transaksi aktif: %s\nPeriode: %s → %s"
					) % (
						overlapping.name,
						overlapping.start_date.strftime("%d-%m-%Y"),
						overlapping.end_date.strftime("%d-%m-%Y")
					))
			
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
