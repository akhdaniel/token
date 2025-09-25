from odoo.tests.common import TransactionCase
from odoo.addons.vit_property_rent.tests.common import VitPropertyRentCommon

from odoo.exceptions import UserError
from odoo.tests import tagged

import logging
_logger = logging.getLogger(__name__)

@tagged('post_install', '-at_install')
class RentTypeTestCase(VitPropertyRentCommon):

	def test_vit_rent_type_count(cls):
		_logger.info(' -------------------- test record count -----------------------------------------')
		cls.assertEqual(
		    4,
		    len(cls.rent_types)
		)