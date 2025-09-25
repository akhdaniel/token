from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website

class WebsiteHomeRedirect(Website):
	@http.route('/', type='http', auth='public', website=True)
	def index(self, **kw):
		if request.env.user and request.env.user.id and not request.env.user._is_public():
			user = request.env.user
			if user.partner_id.is_owner or user.partner_id.is_investor:
				return request.redirect('/my/home')
			return request.redirect('/choose-role')
		return super().index(**kw)
