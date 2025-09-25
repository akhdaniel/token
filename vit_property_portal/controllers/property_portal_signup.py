from odoo import http
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
import logging
_logger = logging.getLogger(__name__)

class AuthSignupOwnerInvestor(AuthSignupHome):

	@http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
	def web_auth_signup(self, *args, **kw):
		qcontext = self.get_auth_signup_qcontext()
		if 'is_owner' in qcontext and qcontext['is_owner']:
			qcontext['is_owner'] = True
		if 'is_investor' in qcontext and qcontext['is_investor']:
			qcontext['is_investor'] = True
		return super().web_auth_signup(*args, **kw)

	def get_auth_signup_qcontext(self):
		qcontext = super().get_auth_signup_qcontext()
		role = request.params.get('role_type')
		qcontext['is_owner'] = role == 'is_owner'
		qcontext['is_investor'] = role == 'is_investor'
		return qcontext


	def _prepare_signup_values(self, qcontext):
		values = super()._prepare_signup_values(qcontext)
		return values

	def do_signup(self, qcontext):
		if qcontext.get('is_owner') and qcontext.get('is_investor'):
			raise UserError(_("You cannot be both an Owner and an Investor."))

		super().do_signup(qcontext)

		values = self._prepare_signup_values(qcontext)
		user = request.env['res.users'].sudo().search([('login', '=', values.get('login'))], limit=1)
		portal_group = request.env.ref('base.group_portal').sudo()
		
		if user:
			user.write({'groups_id': [(4, portal_group.id)]})

			if qcontext.get('is_owner'):
				user.partner_id.is_owner = True
			elif qcontext.get('is_investor'):
				user.partner_id.is_investor = True

		request.env.cr.commit()