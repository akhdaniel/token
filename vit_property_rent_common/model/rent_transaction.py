from odoo import models, fields, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class rent_transaction(models.Model):
	_name = "vit.rent_transaction"
	_inherit = "vit.rent_transaction"
