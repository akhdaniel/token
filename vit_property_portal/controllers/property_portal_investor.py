from odoo import http
from odoo.http import request
from datetime import datetime
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

		token_awal = sum(order_recs.mapped('qty_token'))
		amount_awal = sum(order_recs.mapped('total_amount'))

		profit_share = request.env['vit.property_profit_share'].sudo().search([
			('investor_id', '=', partner)
		])
		all_properties = profit_share.mapped('property_unit_id')
		unique_property_ids = list(set(all_properties.ids))
		invested_properties = request.env['vit.property_unit'].sudo().browse(unique_property_ids)

		total_amount = sum(profit_share.profit_share_line_ids.mapped('amount'))
		token_count = sum(profit_share.profit_share_line_ids.mapped('token_count'))
		owned_property_count = len(order_recs.mapped('property_unit_id'))

		values = {
			'user': user,
			'user_balance_currency': amount_awal + total_amount,
			'current_account_value': amount_awal + total_amount,
			'total_rent_income': total_amount,
			'token_awal': token_awal,
			'token_count': token_count,
			'investasi_awal': amount_awal,
			'owned_property_count': owned_property_count,
			'invested_properties': profit_share,
			'breadcrumbs': [
				('Portofolio', False),   
			],
			'page_name': 'ikhtisar_aset',
		}
		return request.render('vit_property_portal.portal_asset_overview', values)

	# @http.route(['/investor/nilai_akun'], type='http', auth="user", website=True)
	# def investor_nilai_akun(self, **kw):
	# 	user = request.env.user
	# 	investor = user.partner_id

	# 	order_tokens = request.env['vit.order_token'].sudo().search([
	# 		('to_partner_id', '=', investor.id),
	# 		('status', '=', 'confirmed')
	# 	])

	# 	result_rows = []
	# 	for order in order_tokens:
	# 		profit_lines = request.env['vit.property_profit_share_line'].sudo().search([
	# 			('profit_share_id.investor_id', '=', investor.id),
	# 			('profit_share_id.property_unit_id', '=', order.property_unit_id.id)
	# 		])
	# 		total_profit = sum(profit_lines.mapped('amount'))
	# 		total_token_profit = sum(profit_lines.mapped('token_count'))

	# 		result_rows.append({
	# 			'property_name': order.property_unit_id.name,
	# 			'transaksi': order.name,
	# 			'token': order.qty_token,
	# 			'jumlah_investasi': order.total_amount,
	# 			'profit': total_profit,
	# 			'token_profit': total_token_profit,
	# 		})

	# 	total_investasi = sum(r['jumlah_investasi'] for r in result_rows)
	# 	total_profit    = sum(r['profit'] for r in result_rows)

	# 	summary = {
	# 		'total_token': sum(r['token'] for r in result_rows),
	# 		'total_investasi': sum(r['jumlah_investasi'] for r in result_rows),
	# 		'total_profit': sum(r['profit'] for r in result_rows),
	# 		'total_token_profit': sum(r['token_profit'] for r in result_rows),
	# 		'total_saldo': total_investasi + total_profit, 
	# 	}

	# 	sale_order_ids = order_tokens.mapped('sale_order_id').ids
	# 	token_product_ids = request.env['sale.order.line'].sudo().search([
	# 		('order_id', 'in', sale_order_ids),
	# 		('product_id.is_investment_token', '=', True),
	# 	]).mapped('product_id').ids
	# 	tokens = request.env['product.product'].sudo().search([
	# 		('id', 'in', token_product_ids),
	# 		('property_unit_id', 'in', order_tokens.mapped('property_unit_id').ids),
	# 		('token_state', 'in', ['reserved', 'sold']),
	# 	])
	# 	property_tokens_map = {}
	# 	for token in tokens:
	# 		prop = token.property_unit_id
	# 		if not prop:
	# 			continue

	# 		if prop.id not in property_tokens_map:
	# 			tokens_per_property = tokens.filtered(lambda t: t.property_unit_id.id == prop.id)
	# 			property_tokens_map[prop.id] = {
	# 				'property_id': prop.id,
	# 				'property_name': prop.name,
	# 				'tokens': [],
	# 				'total_token': len(tokens_per_property),
	# 			}
	# 		property_tokens_map[prop.id]['tokens'].append(token)

	# 	return request.render('vit_property_portal.nilai_akun_table',  
	# 		{
	# 			'rows': result_rows, 
	# 			'summary': summary,  
	# 			'currency': user.currency_id,
	# 			'property_tokens_map': property_tokens_map,
	# 			'breadcrumbs': [
	# 				('Portofolio', '/investor/ikhtisar'),
	# 				('Ikhtisar Nilai Akun', False),   
	# 			],
	# 			'page_name': 'nilai_akun',
	# 		}
	# 	)

	@http.route(['/investor/nilai_akun'], type='http', auth='user', website=True)
	def investor_nilai_akun(self, **kw):
		user = request.env.user
		investor = user.partner_id

		# 🔹 Ambil semua transaksi pembelian token investor
		order_tokens = request.env['vit.order_token'].sudo().search([
			('to_partner_id', '=', investor.id),
			('status', '=', 'confirmed')
		])

		if not order_tokens:
			return request.render('vit_property_portal.nilai_akun_table', {
				'rows': [],
				'summary': {},
				'currency': user.currency_id,
				'property_tokens_map': {},
				'breadcrumbs': [
					('Portofolio', '/investor/ikhtisar'),
					('Ikhtisar Nilai Akun', False),
				],
				'page_name': 'nilai_akun',
			})

		# ==============================
		# 🔹 Kelompokkan transaksi berdasarkan Property
		# ==============================
		property_data_map = {}

		for order in order_tokens:
			prop = order.property_unit_id
			if not prop:
				continue

			if prop.id not in property_data_map:
				property_data_map[prop.id] = {
					'property_name': prop.name,
					'property_id': prop.id,
					'transaksi': [],
					'total_token': 0,
					'total_investasi': 0,
					'total_profit': 0,
					'total_token_profit': 0,
				}

			property_data_map[prop.id]['transaksi'].append({
				'name': order.name,
				'token': order.qty_token,
				'jumlah_investasi': order.total_amount,
			})

			# Tambahkan transaksi
			# property_data_map[prop.id]['transaksi'].append(order.name)
			property_data_map[prop.id]['total_token'] += order.qty_token
			property_data_map[prop.id]['total_investasi'] += order.total_amount

		# ==============================
		# 🔹 Hitung Profit per Property
		# ==============================
		profit_lines = request.env['vit.property_profit_share_line'].sudo().search([
			('profit_share_id.investor_id', '=', investor.id),
			('profit_share_id.property_unit_id', 'in', list(property_data_map.keys())),
		])

		for line in profit_lines:
			prop_id = line.profit_share_id.property_unit_id.id
			if prop_id not in property_data_map:
				continue

			# Gunakan hanya profit yang relevan (end_date dan periode valid)
			if not line.end_date:
				continue

			property_data_map[prop_id]['total_profit'] += line.amount
			property_data_map[prop_id]['total_token_profit'] += line.token_count

		# ==============================
		# 🔹 Generate property_tokens_map
		# ==============================
		property_tokens_map = {}
		property_ids = list(property_data_map.keys())

		tokens = request.env['product.product'].sudo().search([
			('property_unit_id', 'in', property_ids),
			('token_state', '=', 'sold'),
			('token_owner_id', '=', investor.id),
		])

		for token in tokens:
			prop = token.property_unit_id
			if not prop:
				continue

			if prop.id not in property_tokens_map:
				property_tokens_map[prop.id] = {
					'property_id': prop.id,
					'property_name': prop.name,
					'tokens': [],
					'total_token': 0,
				}

			property_tokens_map[prop.id]['tokens'].append(token)
			property_tokens_map[prop.id]['total_token'] += 1

		# ==============================
		# 🔹 Konversi ke List & Hitung Summary
		# ==============================
		rows = list(property_data_map.values())

		total_investasi = sum(r['total_investasi'] for r in rows)
		total_profit = sum(r['total_profit'] for r in rows)
		total_token_awal = sum(r['total_token'] for r in rows)
		total_token_profit = sum(r['total_token_profit'] for r in rows)

		summary = {
			'total_investasi': total_investasi,
			'total_profit': total_profit,
			'total_token': total_token_awal,
			'total_token_profit': total_token_profit,
			'total_saldo': total_investasi + total_profit,
		}

		# ==============================
		# 🔹 Render ke Template
		# ==============================
		return request.render('vit_property_portal.nilai_akun_table', {
			'rows': rows,
			'summary': summary,
			'currency': user.currency_id,
			'property_tokens_map': property_tokens_map,
			'breadcrumbs': [
				('Portofolio', '/investor/ikhtisar'),
				('Ikhtisar Nilai Akun', False),
			],
			'page_name': 'nilai_akun',
		})

	@http.route(['/investor/payment_request'], type='http', auth="user", website=True, csrf=True)
	def portal_withdraw_request(self, **post):
		property_unit_id = post.get('property_unit_id')
		token_amount = post.get('token_amount')
		bank_account = post.get('bank_account')

		if not property_unit_id or not token_amount or not bank_account:
			return request.redirect('/my/home?error=missing_data')

		try:
			property_unit_id = int(property_unit_id)
			token_amount = int(token_amount)
			bank_id = int(bank_account)
		except ValueError:
			return request.redirect('/my/home?error=invalid_data')

		property_unit = request.env['vit.property_unit'].sudo().browse(property_unit_id)
		if not property_unit.exists():
			return request.redirect('/my/home?error=invalid_property')

		user = request.env.user
		partner = user.partner_id

		request_amount = property_unit.price_per_token * token_amount

		payment = request.env['vit.payment_request'].sudo().create({
			'investor_id': partner.id,
			'bank_id': bank_id,
			'token_amount': token_amount,
			'request_amount': request_amount,
			'request_date': datetime.now(),
		})

		return request.redirect('/my/home?success=withdraw_submitted')
