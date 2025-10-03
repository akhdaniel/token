from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from math import ceil
import json 
import logging
_logger = logging.getLogger(__name__)

class PropertyPortalOwner(CustomerPortal):

	@http.route(['/owner/properties'], type='http', auth="user", website=True, csrf=True)
	def get_all_properties(self, **kw):
		user = request.env.user
		partner = user.partner_id
		Property = request.env['vit.property_unit'].sudo()
		properties = Property.search([('owner_id','=',partner.id)])
		return request.render('vit_property_portal.property_portal_property_list', {
			'property_units': properties,
			'breadcrumbs': [
				('Properties', False),   
			],
			'page_name': 'list_properties',
		})

	@http.route('/owner/property/new', type='http', auth="user", website=True)
	def create_properties(self, **kw):
		if not request.env.user.partner_id.is_owner:
			return request.redirect('/my/home')

		rent_types = request.env['vit.rent_type'].sudo().search([])

		values = self._prepare_portal_layout_values()
		values.update({
			'breadcrumbs': [
				('Properties', '/owner/properties'),
				('New', False),   
			],
			'property_unit': None,
			'rent_types': rent_types,
			'page_name': 'property_unit_new',
		})
		return request.render("vit_property_portal.portal_my_property_unit_form", values)

	@http.route(['/my/property/<int:property_id>'], type='http', auth="user", website=True)
	def my_property_unit(self, property_id, page=1, **kw):
		property_unit = request.env['vit.property_unit'].sudo().browse(property_id)
		if property_unit.owner_id != request.env.user.partner_id:
			return request.redirect('/my/home')

		page = int(kw.get('page', page))
		page_size = 40  
		token_ids = property_unit.token_initial_ids
		total = len(token_ids)
		page_count = ceil(total / page_size)
		start = (page - 1) * page_size
		end = start + page_size
		tokens_page = token_ids[start:end]

		rent_types = request.env['vit.rent_type'].sudo().search([])

		values = self._prepare_portal_layout_values()
		values.update({
			'property_unit': property_unit,
			'tokens_page': tokens_page,
			'page': page,
			'page_count': page_count,
			'page_size': page_size,
			'rent_types': rent_types,
			'breadcrumbs': [
				('Properties', '/owner/properties'),
				(property_unit.name, False),   
			],
			'page_name': 'property_unit_detail',
		})
		return request.render("vit_property_portal.portal_my_property_unit_form", values)

	@http.route('/my/property/<int:property_id>/tokens', type='json', auth="user", website=True)
	def my_property_tokens(self, property_id, **kw):
		property_unit = request.env['vit.property_unit'].sudo().browse(property_id)
		if property_unit.owner_id != request.env.user.partner_id:
			return {'error': 'not_allowed'}

		page = int(kw.get('page', 1))
		page_size = 40
		token_ids = property_unit.token_inital_ids
		total = len(token_ids)
		page_count = max(1, (total + page_size - 1) // page_size)
		start, end = (page - 1) * page_size, page * page_size
		tokens_page = token_ids[start:end]

		html = request.env['ir.qweb']._render(
			'vit_property_portal.portal_my_property_list_token', {
				'tokens_page': tokens_page,
				'page': page,
				'page_size': page_size,
				'page_count': page_count,
				'property_unit': property_unit,
			}
		)
		return {'html': html}

	@http.route('/api/property/save', type='json', auth="user", website=True, methods=['POST'])
	def save_property_unit(self, **kw):
		try:
			user = request.env.user
			partner = user.partner_id
			form_data = kw.get('data', {})

			if not partner.is_owner:
				return {'success': False, 'message': 'You are not authorized to perform this action.'}

			if not form_data.get('name'):
				raise UserError(_("Property Name is a required field."))

			cost_price = float(form_data.get('cost_price') or 0)
			total_tokens = int(form_data.get('total_tokens') or 0)
			price_per_token = cost_price / total_tokens if total_tokens > 0 else 0.0

			data_stage = request.env["vit.stage"].sudo().search([('model_id', '=', request.env['ir.model']._get_id('vit.property_unit'))], limit=1, order="sequence asc")
			property_id = form_data.get('id')
			if property_id:
				property_unit = request.env['vit.property_unit'].sudo().browse(int(property_id))
				if not property_unit.exists():
					return {'success': False, 'message': 'Property not found.'}
				if property_unit.owner_id != partner:
					return {'success': False, 'message': 'Not allowed to edit this property.'}

				product_template = property_unit.product_template_id
				product_template.sudo().write({
					'name': form_data.get('name'),
					'type': 'service',
					'list_price': form_data.get('sale_price'),
					'standard_price': cost_price,
					'total_tokens': total_tokens,
					'taxes_id': [(6, 0, [])],
					'is_property': True,
				})

				property_unit.sudo().write({
					'address': form_data.get('address'),
					'description': form_data.get('description'),
					'total_tokens': total_tokens,
					'available_tokens': form_data.get('available_tokens'),
					'property_type': form_data.get('property_type'),
					'is_sale': form_data.get('is_sale'),
					'is_rent': form_data.get('is_rent'),
					'rental_price': form_data.get('rental_price'),
					'cost_price': cost_price,
					'sale_price_target': form_data.get('sale_price_target'),
					'expected_rental_yield': form_data.get('expected_rental_yield'),
					'owner_id': partner.id,
					'currency_id': user.company_id.currency_id.id,
					'price_per_token': price_per_token,
					'rent_type_id': form_data.get('rent_type_id'),
					'stage_id': data_stage.id,
				})

				return {
					'success': True,
					'message': 'Property updated successfully!',
					'property_id': property_unit.id
				}

			product_template = request.env['product.template'].sudo().create({
				'name': form_data.get('name'),
				'type': 'service',
				'list_price': form_data.get('sale_price'),
				'standard_price': cost_price,
				'total_tokens': total_tokens,
				'taxes_id': [(6, 0, [])],
				'is_property': True,
			})

			property_unit = request.env['vit.property_unit'].sudo().search(
				[('product_template_id', '=', product_template.id)],
				limit=1
			)
			if not property_unit:
				raise UserError(_("Property unit record was not generated automatically."))

			property_unit.sudo().write({
				'address': form_data.get('address'),
				'description': form_data.get('description'),
				'total_tokens': total_tokens,
				'available_tokens': form_data.get('available_tokens'),
				'property_type': form_data.get('property_type'),
				'is_sale': form_data.get('is_sale'),
				'is_rent': form_data.get('is_rent'),
				'rental_price': form_data.get('rental_price'),
				'cost_price': cost_price,
				'sale_price_target': form_data.get('sale_price_target'),
				'expected_rental_yield': form_data.get('expected_rental_yield'),
				'owner_id': partner.id,
				'currency_id': user.company_id.currency_id.id,
				'price_per_token': price_per_token,
				'rent_type_id': form_data.get('rent_type_id'),
				'stage_id': data_stage.id,
			})

			return {
				'success': True,
				'message': 'Property has been saved successfully!',
				'property_id': property_unit.id
			}

		except UserError as e:
			return {'success': False, 'message': str(e)}
		except Exception as e:
			_logger.error("Error creating/updating property: %s", e)
			return {'success': False, 'message': 'An error occurred while saving the property.'}

	@http.route('/my/property/<int:property_id>/generate_tokens', type='json', auth='user', methods=['POST'], csrf=True)
	def generate_tokens(self, property_id):
		property_unit = request.env['vit.property_unit'].browse(property_id).sudo()
		if not property_unit.exists():
			return {'error': 'Property tidak ditemukan'}
		
		property_unit.action_generate_token()
		
		page = 1
		page_size = 40
		token_ids = property_unit.token_ids
		total = len(token_ids)
		page_count = max(1, (total + page_size - 1) // page_size)
		start, end = (page - 1) * page_size, page * page_size
		tokens_page = token_ids[start:end]

		html = request.env['ir.qweb']._render('vit_property_portal.portal_my_property_list_token_table',
			{
				'tokens_page': tokens_page, 
				'page': page,
				'page_size': page_size,
				'page_count': page_count,
				'property_unit': property_unit,
			}
		)
		return {'html': html}


	@http.route('/my/property/delete/<model("vit.property_unit"):property_unit>', type='http', auth="user", website=True, methods=['POST'], csrf=False)
	def my_property_unit_delete(self, property_unit):
		if property_unit.owner_id == request.env.user.partner_id:
			property_unit.unlink()
		return request.redirect('/my/properties')

	