#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class rent_transaction(models.Model):
	"""
	{
	"menu":0
	}
	"""

	_name = "vit.rent_transaction"
	_description = "vit.rent_transaction"


	@api.onchange("property_unit_id")
	def _onchange_property_unit_id(self, ):
		"""
		{
		"@api.onchange":"property_unit_id"
		}
		"""
		self.rent_price_per_month = self.property_unit_id.rental_price
		self.rent_type_id = self.property_unit_id.rent_type_id


	def action_reload_view(self):
		pass

	name = fields.Char( required=True, copy=False, default="New", readonly=True,  string=_("Name"))
	start_date = fields.Date(required=True,  string=_("Start Date"))
	duration = fields.Integer(required=True,  string=_("Duration"))
	end_date = fields.Date( string=_("End Date"))
	rent_price_per_month = fields.Float(readonly=True,  string=_("Rent Price Per Month"))
	amount_total_rent = fields.Float(readonly=True,  string=_("Amount Total Rent"))
	transaction_date = fields.Datetime( string=_("Transaction Date"))
	stage_is_draft = fields.Boolean(related="stage_id.draft", store=True,  string=_("Stage Is Draft"))
	stage_is_done = fields.Boolean(related="stage_id.done", store=True,  string=_("Stage Is Done"))
	allow_confirm = fields.Boolean(related="stage_id.allow_confirm", store=True,  string=_("Allow Confirm"))
	allow_cancel = fields.Boolean(related="stage_id.allow_cancel", store=True,  string=_("Allow Cancel"))
	stage_name = fields.Char(related="stage_id.name", store=True,  string=_("Stage Name"))


	@api.model_create_multi
	def create(self, vals):
		for val in vals:
			if not val.get("name", False) or val["name"] == "New":
				val["name"] = self.env["ir.sequence"].next_by_code("vit.rent_transaction") or "Error Number!!!"
		return super(rent_transaction, self).create(vals)

	def _get_first_stage(self):
		try:
			data_id = self.env["vit.stage"].sudo().search([], limit=1, order="sequence asc")
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
		data_id = self.env["vit.stage"].sudo().search([("sequence",">",current_stage_seq)], limit=1, order="sequence asc")
		if data_id:
			return data_id
		else:
			return self.stage_id

	def _get_previous_stage(self):
		current_stage_seq = self.stage_id.sequence
		data_id = self.env["vit.stage"].sudo().search([("sequence","<",current_stage_seq)], limit=1, order="sequence desc")
		if data_id:
			return data_id
		else:
			return self.stage_id

	@api.model
	def _group_expand_states(self, stages, domain, order):
		return self.env['vit.stage'].search([])

	def unlink(self):
		for me_id in self :
			if not me_id.stage_id.draft:
				raise UserError("Cannot delete non draft record!  Make sure that the Stage draft flag is checked.")
		return super(rent_transaction, self).unlink()

	def copy(self, default=None):
		default = dict(default or {})
		default.update({
			'name': self.name + ' (Copy)'
		})
		return super(rent_transaction, self).copy(default)

	property_unit_id = fields.Many2one(comodel_name="vit.property_unit", required=True,  string=_("Property Unit"))
	customer_id = fields.Many2one(comodel_name="res.partner", required=True,  string=_("Customer"))
	stage_id = fields.Many2one(comodel_name="vit.stage",  default=_get_first_stage, copy=False, group_expand="_group_expand_states",  string=_("Stage"))
	rent_type_id = fields.Many2one(comodel_name="vit.rent_type", related="property_unit_id.rent_type_id", readonly=True,  string=_("Rent Type"))
