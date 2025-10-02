from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class PropertyPortalInvestor(http.Controller):
	@http.route(['/investor/ikhtisar'], type='http', auth="user", website=True)
	def ikhtisar_aset(self, **kw):
		user = request.env.user
		partner = user.partner_id.id
		order_recs = request.env['vit.order_token'].sudo().search([
			('status', '=', 'confirmed'),
			('to_partner_id', '=', partner)
		])

		# token & amount
		token_awal = sum(order_recs.mapped('qty_token'))
		amount_awal = sum(order_recs.mapped('total_amount'))

		# profit share
		profit_share = request.env['vit.property_profit_share'].sudo().search([
			('investor_id', '=', partner)
		])
		total_amount = sum(profit_share.profit_share_line_ids.mapped('amount'))
		token_count = sum(profit_share.profit_share_line_ids.mapped('token_count'))

		owned_property_count = len(order_recs.mapped('property_unit_id'))
		invested_properties = profit_share.mapped('property_unit_id')

		values = {
			'user': user,
			'user_balance_currency': amount_awal + total_amount,
			'current_account_value': amount_awal + total_amount,
			'total_rent_income': total_amount,
			'token_awal': token_awal,
			'token_count': token_count,
			'investasi_awal': amount_awal,
			'owned_property_count': owned_property_count,
			'invested_properties': invested_properties,
			'breadcrumbs': [
				('Portofolio', False),   
			],
			'page_name': 'ikhtisar_aset',
		}
		return request.render('vit_property_portal.portal_asset_overview', values)

	@http.route(['/investor/nilai_akun'], type='http', auth="user", website=True)
	def investor_nilai_akun(self, **kw):
		user = request.env.user
		investor = user.partner_id

		order_tokens = request.env['vit.order_token'].sudo().search([
			('to_partner_id', '=', investor.id),
			('status', '=', 'confirmed')
		])

		result_rows = []
		for order in order_tokens:
			profit_lines = request.env['vit.property_profit_share_line'].sudo().search([
				('profit_share_id.investor_id', '=', investor.id),
				('profit_share_id.property_unit_id', '=', order.property_unit_id.id)
			])
			total_profit = sum(profit_lines.mapped('amount'))
			total_token_profit = sum(profit_lines.mapped('token_count'))

			result_rows.append({
				'property_name': order.property_unit_id.name,
				'transaksi': order.name,
				'token': order.qty_token,
				'jumlah_investasi': order.total_amount,
				'profit': total_profit,
				'token_profit': total_token_profit,
			})

		total_investasi = sum(r['jumlah_investasi'] for r in result_rows)
		total_profit    = sum(r['profit'] for r in result_rows)

		summary = {
			'total_token': sum(r['token'] for r in result_rows),
			'total_investasi': sum(r['jumlah_investasi'] for r in result_rows),
			'total_profit': sum(r['profit'] for r in result_rows),
			'total_token_profit': sum(r['token_profit'] for r in result_rows),
			'total_saldo': total_investasi + total_profit, 
		}

		sale_order_ids = order_tokens.mapped('sale_order_id').ids
		token_product_ids = request.env['sale.order.line'].sudo().search([
			('order_id', 'in', sale_order_ids),
			('product_id.is_investment_token', '=', True),
		]).mapped('product_id').ids
		tokens = request.env['product.product'].sudo().search([
			('id', 'in', token_product_ids),
			('property_unit_id', 'in', order_tokens.mapped('property_unit_id').ids),
			('token_state', 'in', ['reserved', 'sold']),
		])
		property_tokens_map = {}
		for token in tokens:
			prop = token.property_unit_id
			if not prop:
				continue

			if prop.id not in property_tokens_map:
				# inisialisasi
				tokens_per_property = tokens.filtered(lambda t: t.property_unit_id.id == prop.id)
				property_tokens_map[prop.id] = {
					'property_id': prop.id,
					'property_name': prop.name,
					'tokens': [],
					'total_token': len(tokens_per_property),
				}

			# tambahkan token
			property_tokens_map[prop.id]['tokens'].append(token)

		return request.render('vit_property_portal.nilai_akun_table',  
			{
				'rows': result_rows, 
				'summary': summary,  
				'currency': user.currency_id,
				'property_tokens_map': property_tokens_map,
				'breadcrumbs': [
					('Portofolio', '/investor/ikhtisar'),
					('Ikhtisar Nilai Akun', False),   
				],
				'page_name': 'nilai_akun',
			}
		)

	@http.route(['/investor/payment_request'], type='http', auth="user", website=True, csrf=True)
	def portal_withdraw_request(self, **post):
		token_amount = post.get('token_amount')
		bank_account = post.get('bank_account')
		if not token_amount or not bank_account:
			return request.redirect('/my/home?error=missing_data')

		try:
			token_amount = int(token_amount)
			bank_id = int(bank_account)
		except ValueError:
			return request.redirect('/my/home?error=invalid_data')

		user = request.env.user
		partner = user.partner_id
		request_amount = token_amount

		payment = request.env['vit.payment_request'].sudo().create({
			'investor_id': partner.id,
			'bank_id': bank_id,
			'token_amount': token_amount,
			'request_amount': request_amount,
		})

		return request.redirect('/my/home?success=withdraw_submitted')
