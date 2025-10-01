# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
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
