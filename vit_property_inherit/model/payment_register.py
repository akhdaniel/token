from odoo import models
import logging
_logger = logging.getLogger(__name__)

class PaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        invoices = self.line_ids.move_id
        _logger.info("Invoices yang akan dibayar: %s", invoices.ids)

        res = super().action_create_payments()

        payments = self.line_ids.payment_id
        _logger.info("Payments dibuat: %s", payments.ids)

        for inv in invoices:
            order = self.env['vit.order_token'].sudo().search([
                ('sale_order_id', '=', inv.invoice_origin)
            ], limit=1)
            if order and order.status != 'confirmed':
                data_stage = self.env['vit.stage'].sudo().search([
                    ('model_id', '=', self.env['ir.model']._get_id('vit.order_token')),
                    ('name', '=', 'Confirmed')
                ], limit=1, order="sequence asc")
                order.write({'status': 'confirmed', 'stage_id': data_stage.id})
                tokens = order.property_unit_id.token_ids.filtered(
                    lambda t: t.token_state == 'reserved'
                )[:order.qty_token]
                tokens.write({'token_state': 'sold'})

        return res
