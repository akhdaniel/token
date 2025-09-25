#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class order_token(models.Model):
	_name = "vit.order_token"
	_inherit = "vit.order_token"

	stage_id = fields.Many2one(
		comodel_name="vit.stage",
		string="Stage",
		default=lambda self: self._get_first_stage(),
		copy=False,
		group_expand="_group_expand_states",
		domain=lambda self: [
			('model_id', '=', self.env['ir.model']._get_id('vit.order_token'))
		],
	)
	order_token_line_ids = fields.One2many(related="sale_order_id.order_line", string="Order Token Lines", readonly=True, store=False)

	@api.model_create_multi
	def create(self, vals):
		return super(order_token, self).create(vals)

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
		return super(order_token, self).unlink()
