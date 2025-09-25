from odoo.tests.common import TransactionCase
from odoo.addons.vit_property.tests.common import VitPropertyCommon

from odoo.exceptions import UserError
from odoo.tests import tagged

import logging
_logger = logging.getLogger(__name__)

@tagged('post_install', '-at_install')
class PropertyProfitShareTestCase(VitPropertyCommon):

	def test_vit_property_profit_share_count(cls):
		_logger.info(' -------------------- test record count -----------------------------------------')
		cls.assertEqual(
		    4,
		    len(cls.property_profit_shares)
		)