from odoo import http
from odoo.http import request
import json

class PropertyWebsite(http.Controller): 

	@http.route('/list_properties', type='http', auth='public', methods=['GET'], csrf=False, website=True)
	def list_properties(self):
		props = request.env['vit.property_unit'].sudo().search([('stage_name','=','Published')])
		data = [
			{'id': p.id, 'name': p.name, 'price_per_token': p.price_per_token}
			for p in props
		]
		return request.make_response(
            json.dumps({'result': data}),
            headers=[('Content-Type', 'application/json')]
        )

	@http.route('/yield_calculator', type='json', auth='public', methods=['POST'], csrf=False)
	def yield_calculator(self):
		params = request.httprequest.get_json(force=True)   
		property_id    = int(params.get('property_id'))
		invest_type    = params.get('invest_type')
		monthly_invest = float(params.get('monthly_invest', 0))
		years          = int(params.get('years', 1))
		auto_reinvest  = bool(params.get('auto_reinvest', False))

		prop = request.env['vit.property_unit'].sudo().browse(int(property_id))
		token_price = prop.price_per_token
		annual_yield = prop.expected_rental_yield / 100.0
		months = years * 12

		total_invest = 0.0
		total_rental_income = 0.0
		token_qty = 0

		if invest_type == 'once':
			# hitung token integer
			token_qty = int(monthly_invest // token_price)
			total_invest = token_qty * token_price
			total_rental_income = token_qty * token_price * annual_yield * years
		else:
			for m in range(months):
				# token tambahan setiap bulan
				new_token = int(monthly_invest // token_price)
				total_invest += new_token * token_price
				token_qty += new_token
				if auto_reinvest:
					# rental yield per bulan → beli token bulat
					rental = token_qty * token_price * (annual_yield/12)
					reinvest_token = int(rental // token_price)
					token_qty += reinvest_token
					total_rental_income += reinvest_token * token_price
				else:
					total_rental_income += token_qty * token_price * (annual_yield/12)

		total_asset = total_invest + total_rental_income

		return {
			'token_price': token_price,
			'token_qty': token_qty,              
			'total_invest': total_invest,      
			'total_rental_income': total_rental_income,
			'total_asset': total_asset,
		}