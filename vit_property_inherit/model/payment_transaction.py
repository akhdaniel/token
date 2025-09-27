from odoo import models
import logging
_logger = logging.getLogger(__name__)

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _set_done(self):
        res = super()._set_done()

        for tx in self:
            if tx.provider_code != 'xendit':
                continue

            invoice = self.env['account.move'].sudo().search([
                ('payment_reference', '=', tx.reference)
            ], limit=1)

            sale_order = self.env['sale.order'].sudo().search([
                ('name', '=', invoice.invoice_origin)
            ], limit=1)
            order = self.env['vit.order_token'].sudo().search([
                ('sale_order_id', '=', sale_order.id)
            ], limit=1)

            if order and order.status != 'confirmed':
                data_stage = self.env["vit.stage"].sudo().search([('model_id', '=', self.env['ir.model']._get_id('vit.order_token')),('name','=','Confirmed')], limit=1, order="sequence asc")
                order.write({'status': 'confirmed', 'stage_id': data_stage.id})
                tokens = order.property_unit_id.token_ids.filtered(
                    lambda t: t.token_state == 'reserved'
                )[:order.qty_token]
                tokens.write({'token_state': 'sold'})

        return res
