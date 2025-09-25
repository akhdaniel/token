from odoo import http
from odoo.http import request

class OauthController(http.Controller):

	@http.route('/choose-role', type='http', auth='user', website=True)
	def choose_role(self, **kw):
		return request.render('vit_oauth_portal.choose_role_template', {})

	@http.route(['/choose-role/submit'], type='http', auth='user', methods=['POST'], website=True, csrf=True)
	def choose_role_submit(self, **post):
		role = post.get('role')
		if role not in ('owner', 'investor'):
			return request.redirect('/choose-role')

		user = request.env.user.sudo()
		partner = user.partner_id

		is_owner = role == 'owner'
		is_investor = role == 'investor'

		partner.sudo().write({
			'is_owner': is_owner,
			'is_investor': is_investor,
		})

		return request.redirect('/my/home')
