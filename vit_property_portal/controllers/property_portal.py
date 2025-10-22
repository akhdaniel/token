from odoo import http, fields, _
from odoo.http import request
from odoo.exceptions import UserError
import json 
import logging
_logger = logging.getLogger(__name__)

class PropertyPortal(http.Controller):

	@http.route(['/properties'], type='http', auth='public', website=True)
	def list_properties(self, **kw):
		mode = kw.get('mode', 'all')
		domain = [('stage_name', '=', 'Publish')]

		if mode == 'sale':
			domain.append(('is_sale', '=', True))
		elif mode == 'rent':
			domain.append(('is_rent', '=', True))
		else:
			domain.append('|')
			domain.extend([
				('is_sale', '=', True),
				('is_rent', '=', True)
			])

		properties = request.env['vit.property_unit'].sudo().search(domain)
		return request.render('vit_property_portal.portal_property_list', {
			'properties': properties,
			'breadcrumbs': [
				('Properties', False),   
			],
			'page_name': 'list_properties',
			'mode': mode
		})

	@http.route(['/properties/<int:prop_id>'], type='http', auth='public', website=True)
	def property_detail(self, prop_id, **kw):
		prop = request.env['vit.property_unit'].sudo().browse(prop_id)
		# Ambil semua order token confirmed untuk property ini
		investors_orders = request.env['vit.order_token'].sudo().search([
			('property_unit_id', '=', prop_id),
			('status', '=', 'confirmed')
		])
		property_financial = request.env['vit.property_financial'].sudo().search([
			('name', '=', prop_id),
		])

		# Kelompokkan per investor
		investors_grouped = []
		total_token = 0
		for order in investors_orders:
			if not order.to_partner_id:
				continue
			found = False
			for i in investors_grouped:
				if i['partner'].id == order.to_partner_id.id:
					i['total_token'] += order.qty_token
					if order.date and (not i['last_date'] or order.date > i['last_date']):
						i['last_date'] = order.date
					found = True
					break
			if not found:
				investors_grouped.append({
					'partner': order.to_partner_id,
					'total_token': order.qty_token,
					'last_date': order.date
				})

		# Hitung total token
		total_token = sum(i['total_token'] for i in investors_grouped)

		# Urutkan berdasarkan total_token descending
		investors_sorted = sorted(investors_grouped, key=lambda x: x['total_token'], reverse=True)

		return request.render('vit_property_portal.portal_property_detail', {
			'property': prop,
			'investors': investors_sorted,
			'property_financial': property_financial,
			'total_token': total_token,
			'breadcrumbs': [
				('Properties', '/properties'),
				(prop.name, False),   
			],
			'page_name': 'property_detail',
		})

	@http.route(['/properties/<int:property_id>/buy_token'], type='http', auth="user", methods=['POST','GET'], website=True, csrf=True)
	def buy_token(self, property_id, **post):
		if request.httprequest.method == 'GET':
			return request.redirect('/properties')

		try:
			qty = int(post.get('qty_token', 0))
			property_id = int(post.get('property_id', property_id))
		except (ValueError, TypeError):
			raise UserError(_("Jumlah token tidak valid."))
		if qty <= 0:
			raise UserError(_("Jumlah token harus lebih dari 0."))

		user = request.env.user
		partner = user.partner_id

		Property = request.env['vit.property_unit'].sudo()
		prop = Property.browse(property_id)
		if not prop.exists():
			raise UserError(_("Property tidak ditemukan."))

		Product = request.env['product.product'].sudo()
		tokens = Product.search([
			('property_unit_id', '=', prop.id),
			('is_investment_token', '=', True),
			('token_state', '=', 'available')
		], order='token_code asc', limit=qty)

		if len(tokens) < qty:
			raise UserError(_("Token yang tersedia tidak mencukupi."))

		SaleOrder = request.env['sale.order'].sudo()
		SaleOrderLine = request.env['sale.order.line'].sudo()
		OrderToken = request.env['vit.order_token'].sudo()

		with request.env.cr.savepoint():
			tokens.sudo().write({'token_state': 'reserved'})

			sale_order = SaleOrder.create({
				'partner_id': partner.id,
				'origin': _('Property Token Purchase'),
			})

			SaleOrderLine.create([{
				'order_id': sale_order.id,
				'product_id': token.id,
				'product_uom_qty': 1,
				'price_unit': prop.price_per_token,
			} for token in tokens])

			sale_order.action_confirm()
			invoices = sale_order._create_invoices()
			invoices.write({'invoice_date': fields.Date.context_today(request.env.user)})
			invoices.action_post()

			data_stage = request.env["vit.stage"].sudo().search([('model_id', '=', request.env['ir.model']._get_id('vit.order_token')),('name','=','Reserved')], limit=1, order="sequence asc")
			order_token = OrderToken.create({
				'qty_token': qty,
				'total_amount': sale_order.amount_total,
				'property_unit_id': prop.id,
				'from_partner_id': prop.owner_id.id,
				'to_partner_id': partner.id,
				'sale_order_id': sale_order.id,
				'date': fields.Datetime.now(),
				'status': 'reserved',
				'stage_id': data_stage.id,
			})

		prop.write({'available_tokens': prop.available_tokens - qty})

		_logger.info("Order Token %s created, Sale Order %s, Invoice %s", order_token.id, sale_order.id, invoices.ids)

		return request.redirect('/my/invoices')
