#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class payment_request(models.Model):
	"""
	{
	"sequence":4
	}
	"""

	_name = "vit.payment_request"
	_description = "vit.payment_request"


	def action_reload_view(self):
		pass

	name = fields.Char( required=True, copy=False, default="New", readonly=True,  string=_("Name"))
	token_amount = fields.Integer(readonly=True,  string=_("Token Amount"))
	request_amount = fields.Float(readonly=True,  string=_("Request Amount"))
	request_date = fields.Datetime( string=_("Request Date"))
	stage_is_draft = fields.Boolean(related="stage_id.draft", store=True,  string=_("Stage Is Draft"))
	stage_is_done = fields.Boolean(related="stage_id.done", store=True,  string=_("Stage Is Done"))
	allow_confirm = fields.Boolean(related="stage_id.allow_confirm", store=True,  string=_("Allow Confirm"))
	allow_cancel = fields.Boolean(related="stage_id.allow_cancel", store=True,  string=_("Allow Cancel"))
	stage_name = fields.Char(related="stage_id.name", store=True,  string=_("Stage Name"))


	@api.model_create_multi
	def create(self, vals):
		for val in vals:
			if not val.get("name", False) or val["name"] == "New":
				val["name"] = self.env["ir.sequence"].next_by_code("vit.payment_request") or "Error Number!!!"
		return super(payment_request, self).create(vals)

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
		return super(payment_request, self).unlink()

	def copy(self, default=None):
		default = dict(default or {})
		default.update({
			'name': self.name + ' (Copy)'
		})
		return super(payment_request, self).copy(default)

	stage_id = fields.Many2one(comodel_name="vit.stage",  default=_get_first_stage, copy=False, group_expand="_group_expand_states",  string=_("Stage"))
	investor_id = fields.Many2one(comodel_name="res.partner", readonly=True,  string=_("Investor"))
	bank_id = fields.Many2one(comodel_name="res.partner.bank", readonly=True,  string=_("Bank"))
