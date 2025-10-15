#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class property_unit(models.Model):
	"""
	{
	"menu":1,
	"sequence":10
	}
	"""

	_name = "vit.property_unit"
	_description = "vit.property_unit"


	def action_generate_token(self, ):
		pass


	@api.depends("total_tokens","cost_price")
	def _compute_price_per_token(self, ):
		"""
		{
		"@api.depends":["total_tokens","cost_price"]
		}
		"""
		for rec in self:
		    if rec.total_tokens and rec.total_tokens > 0:
		        rec.price_per_token = rec.cost_price / rec.total_tokens
		    else:
		        rec.price_per_token = 0.0


	def action_reload_view(self):
		pass

	name = fields.Char( required=True, copy=False, default="New", readonly=True, string="Property Name", related="product_template_id.name")
	address = fields.Text(string="Full Address")
	description = fields.Html(string="Property Description")
	total_tokens = fields.Integer(related="product_template_id.total_tokens",  string=_("Total Tokens"))
	available_tokens = fields.Integer( string=_("Available Tokens"))
	price_per_token = fields.Float(compute="_compute_price_per_token",  string=_("Price Per Token"))
	property_type = fields.Selection(selection=[('villa', 'Villa'),('apartemen', 'Apartment'),('house', 'House'),('office', 'Office'),('warehouse', 'Warehouse')],  string=_("Property Type"))
	cost_price = fields.Float(related="product_template_id.standard_price",  string=_("Cost Price"))
	sale_price = fields.Float(related="product_template_id.list_price",  string=_("Sale Price"))
	is_sale = fields.Boolean( string=_("Is Sale"))
	is_rent = fields.Boolean( string=_("Is Rent"))
	rental_price = fields.Float( string=_("Rental Price"))
	sale_price_target = fields.Float( string=_("Sale Price Target"))
	expected_rental_yield = fields.Float( string=_("Expected Rental Yield"))
	expected_capital_appreciation = fields.Float( string=_("Expected Capital Appreciation"))
	internal_rate_of_return = fields.Float( string=_("Internal Rate Of Return"))
	stage_is_draft = fields.Boolean(related="stage_id.draft", store=True,  string=_("Stage Is Draft"))
	stage_is_done = fields.Boolean(related="stage_id.done", store=True,  string=_("Stage Is Done"))
	allow_confirm = fields.Boolean(related="stage_id.allow_confirm", store=True,  string=_("Allow Confirm"))
	allow_cancel = fields.Boolean(related="stage_id.allow_cancel", store=True,  string=_("Allow Cancel"))
	stage_name = fields.Char(related="stage_id.name", store=True,  string=_("Stage Name"))
	bedroom_count = fields.Integer( string=_("Bedroom Count"))
	bathroom_count = fields.Integer( string=_("Bathroom Count"))
	property_size = fields.Float( string=_("Property Size"))
	longitude = fields.Float( string=_("Longitude"))
	latitude = fields.Float( string=_("Latitude"))


	@api.model_create_multi
	def create(self, vals):
		for val in vals:
			if not val.get("name", False) or val["name"] == "New":
				val["name"] = self.env["ir.sequence"].next_by_code("vit.property_unit") or "Error Number!!!"
		return super(property_unit, self).create(vals)

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
		return super(property_unit, self).unlink()

	def copy(self, default=None):
		default = dict(default or {})
		default.update({
			'name': self.name + ' (Copy)'
		})
		return super(property_unit, self).copy(default)

	product_template_id = fields.Many2one(comodel_name="product.template", readonly=True,  string=_("Product Template"))
	owner_id = fields.Many2one(comodel_name="res.partner",  string=_("Owner"))
	currency_id = fields.Many2one(comodel_name="res.currency",  string=_("Currency"), default=lambda self: self.env.company.currency_id.id)
	stage_id = fields.Many2one(comodel_name="vit.stage",  default=_get_first_stage, copy=False, group_expand="_group_expand_states",  string=_("Stage"))
	token_ids = fields.One2many(comodel_name="product.product",  inverse_name="property_unit_id",  string=_("Token"))
	property_unit_image_ids = fields.One2many(comodel_name="vit.property_unit_image",  inverse_name="property_unit_id",  string=_("Property Unit Image"))
	property_document_ids = fields.One2many(comodel_name="vit.property_document",  inverse_name="property_unit_id", string="Document")
	property_timeline_ids = fields.One2many(comodel_name="vit.property_timeline",  inverse_name="property_unit_id",  string=_("Property Timeline"))
