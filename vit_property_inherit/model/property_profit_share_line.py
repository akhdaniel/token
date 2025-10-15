from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class property_profit_share_line(models.Model):
	_name = "vit.property_profit_share_line"
	_inherit = "vit.property_profit_share_line"

	start_date = fields.Datetime( string=_("Start Date"))
	end_date = fields.Datetime( string=_("End Date"))