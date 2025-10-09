#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class property_unit(models.Model):
	_name = "vit.property_unit"
	_inherit = "vit.property_unit"

	stage_id = fields.Many2one(
		comodel_name="vit.stage",
		string="Stage",
		default=lambda self: self._get_first_stage(),
		copy=False,
		group_expand="_group_expand_states",
		domain=lambda self: [
			('model_id', '=', self.env['ir.model']._get_id('vit.property_unit'))
		],
	)
	token_initial_ids = fields.One2many(comodel_name="product.product", inverse_name="property_unit_id", domain=[("token_type", "=", "token_initial")], string="Token Initial")
	token_reward_ids = fields.One2many(comodel_name="product.product", inverse_name="property_unit_id", domain=[("token_type", "=", "token_reward")], string="Token Reward")
	available_tokens = fields.Integer(compute="_compute_available_tokens", store=True )
	can_generate_token = fields.Boolean(string="Can Generate Token", default=True)

	# @api.depends("token_ids")
	# def _compute_can_generate_token(self):
	# 	for rec in self:
	# 		rec.can_generate_token = not bool(rec.token_ids)

	@api.depends('token_ids.token_state')
	def _compute_available_tokens(self):
		for rec in self:
			rec.available_tokens = len(
				rec.token_ids.filtered(lambda t: t.token_state == 'available')
			)

	@api.model_create_multi
	def create(self, vals):
		for val in vals:
			if not val.get('available_tokens') and val.get('total_tokens'):
				val['available_tokens'] = val['total_tokens']
			elif not val.get('available_tokens') and val.get('product_template_id'):
				product = self.env['product.template'].browse(val['product_template_id'])
				if product and product.total_tokens:
					val['available_tokens'] = product.total_tokens
			return super(property_unit, self).create(vals)

	def _get_first_stage(self):
		try:
			data_id = self.env["vit.stage"].sudo().search([('model_id', '=', self.env['ir.model']._get_id(self._name))], limit=1, order="sequence asc")
			if data_id:
				return data_id
		except KeyError:
			return False

	def action_confirm(self):
		if not self.property_unit_image_ids:
			raise UserError("Cannot confirm record without image!  Please upload image.")
			
		if not self.property_document_ids:
			raise UserError("Cannot confirm record without document!  Please upload document.")

		stage = self._get_next_stage()
		self.stage_id=stage
		if self.stage_id.execute_enter and hasattr(self, self.stage_id.execute_enter) and callable(getattr(self, self.stage_id.execute_enter)):
			eval(f"self.{self.stage_id.execute_enter}()")

	def action_cancel(self):
		stage = self._get_previous_stage()
		self.stage_id=stage

	def _get_next_stage(self):
		current_stage_seq = self.stage_id.sequence
		data_id = self.env["vit.stage"].sudo().search([('model_id', '=', self.env['ir.model']._get_id(self._name)),("sequence",">",current_stage_seq)], limit=1, order="sequence asc")
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
		return super(property_unit, self).unlink()

	def action_generate_token(self, ):
		Product = self.env["product.product"].sudo()
		vals_list = []
		for i in range(self.total_tokens):
			vals_list.append({
				"name": f"{self.name} - Token {i+1}",
				"list_price": self.price_per_token,
				"taxes_id": [(6, 0, [])],
				"supplier_taxes_id": [(6, 0, [])],
				"type": "service",
				"token_state": "available",
				"token_type": "token_initial",
				"is_investment_token": True,
				"property_unit_id": self.id,
				"token_owner_id": self.owner_id.id,
				"token_code": f"{self.id}-{i+1:03d}",
			})
		Product.create(vals_list)
		self.available_tokens = len(vals_list)
		self.can_generate_token = False 
		return {
			"type": "ir.actions.client",
			"tag": "reload",
		}