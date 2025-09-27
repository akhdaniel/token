# -*- coding: utf-8 -*-
{
    "name": "Property & Rent – Common",
    "version": "1.0",
    "depends": [
        "vit_property",       
        "vit_property_rent"    
    ],
    "author": "Your Company",
    "category": "Utility",
    "license": "OPL-1",
    "data": [
        "security/ir.model.access.csv",
        "wizard/property_profit_share_wizard.xml",
        "view/profit_share_rent_rel.xml",
        "view/rent_transaction.xml",
    ],
    "installable": True,
    "application": True,
    "odooVersion": 18,
}
