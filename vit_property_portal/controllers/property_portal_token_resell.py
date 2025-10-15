# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.http import request, Response
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class TokenResellController(http.Controller):

	@http.route('/token/resell/submit', type='json', auth="user", methods=['POST'], csrf=True)
	def token_resell_submit(self, property_id, qty_token, price_per_token, **kwargs):
		user = request.env.user
		investor = user.partner_id

		if not investor:
			return {'success': False, 'message': _("Investor tidak ditemukan")}

		try:
			data_stage = request.env["vit.stage"].sudo().search([('model_id', '=', request.env['ir.model']._get_id('vit.token_resell'))], limit=1, order="sequence asc")
			resell = request.env['vit.token_resell'].sudo().create({
				'investor_id': investor.id,
				'property_unit_id': int(property_id),
				'qty_token': int(qty_token),
				'price_per_token': float(price_per_token),
				'stage_id': data_stage.id
			})

			return {
				'success': True,
				'message': _("Resell token berhasil diajukan"),
				'resell_id': resell.id,
			}
		except Exception as e:
			_logger.error("Gagal resell token: %s", str(e))
			return {'success': False, 'message': _("Gagal resell token: %s") % str(e)}

	@http.route('/marketplace', type='http', auth="public", website=True)
	def token_resell_marketplace(self, **kwargs):
		try:
			resell_tokens = request.env['vit.token_resell'].sudo().search([], order="create_date desc")
			return request.render('vit_property_portal.portal_token_resell', {
				'resell_tokens': resell_tokens,
				'breadcrumbs': [
					('Marketplace', False),   
				],
				'page_name': 'marketplace',
			})

		except Exception as e:
			_logger.error("Gagal load marketplace token resell: %s", str(e))
			return request.not_found()

	@http.route('/marketplace/property/<int:resell_id>', type='http', auth="public", website=True)
	def token_resell_detail(self, resell_id, **kwargs):
		resell = request.env['vit.token_resell'].sudo().browse(resell_id)
		if not resell.exists():
			return request.not_found()
		
		return request.render('vit_property_portal.portal_token_resell_detail', {
			'resell': resell,
			'property': resell.property_unit_id,
			'breadcrumbs': [
				('Marketplace', '/marketplace'),
				(resell.property_unit_id.name, False)
			],
		})

	@http.route('/token/resell/buy', type='http', auth="user", methods=['POST'], website=True, csrf=True)
	def token_resell_buy(self, resell_id, **post):
		user = request.env.user
		buyer = user.partner_id

		if request.httprequest.method == 'GET':
			return request.redirect('/properties')


		try:
			qty_token = int(post.get('qty_token', 0))
			resell_id = int(post.get('resell_id', resell_id))

		except (ValueError, TypeError):
			raise UserError(_("Jumlah token tidak valid."))
		if qty_token <= 0:
			raise UserError(_("Jumlah token harus lebih dari 0."))

		resell = request.env['vit.token_resell'].sudo().browse(resell_id)
		Property = request.env['vit.property_unit'].sudo()
		Product = request.env['product.product'].sudo()
		prop = Property.browse(resell.property_unit_id.id)
		tokens = Product.search([
			('property_unit_id', '=', prop.id),
			('is_investment_token', '=', True),
			('token_type', '=', 'token_initial'),
			('token_owner_id', '=', resell.investor_id.id),
		], order='token_code asc', limit=qty_token)
		SaleOrder = request.env['sale.order'].sudo()
		SaleOrderLine = request.env['sale.order.line'].sudo()
		OrderToken = request.env['vit.order_token'].sudo()
		if not resell.exists():
			return {'success': False, 'message': _("Token resell tidak ditemukan")}
		if qty_token > resell.qty_token:
			return {'success': False, 'message': _("Jumlah token melebihi stok yang tersedia")}

		# Buat record pembelian
		with request.env.cr.savepoint():
			tokens.sudo().write({'token_state': 'reserved'})
			sale_order = SaleOrder.create({
				'partner_id': buyer.id,
				'origin': f"Resell Token {resell.name} Purchase",
			})
			SaleOrderLine.create([{
				'order_id': sale_order.id,
				'product_id': token.id,
				'product_uom_qty': 1,
				'price_unit': prop.price_per_token,
			} for token in tokens])
			# Konfirmasi order
			sale_order.action_confirm()
			invoices = sale_order._create_invoices()
			invoices.write({'invoice_date': fields.Date.context_today(request.env.user)})
			invoices.action_post()
			data_stage = request.env["vit.stage"].sudo().search([('model_id', '=', request.env['ir.model']._get_id('vit.order_token')),('name','=','Reserved')], limit=1, order="sequence asc")
			order_token = OrderToken.create({
				'qty_token': qty_token,
				'total_amount': sale_order.amount_total,
				'property_unit_id': prop.id,
				'from_partner_id': resell.investor_id.id,
				'to_partner_id': buyer.id,
				'sale_order_id': sale_order.id,
				'date': fields.Datetime.now(),
				'status': 'reserved',
				'stage_id': data_stage.id,
				'token_resell_id': resell.id,
			})
			
		_logger.info("Order Token %s created, Sale Order %s, Invoice %s", order_token.id, sale_order.id, invoices.ids)
		return request.redirect('/my/invoices')
		


