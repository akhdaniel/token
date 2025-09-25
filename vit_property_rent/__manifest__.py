#-*- coding: utf-8 -*-

{
	"name": "Property Rent",
	"version": "1.0",
	"depends": [
		"base",
		"vit_property",
		"vit_stage"
	],
	"author": "Akhmad Daniel Sembiring",
	"category": "Utility",
	"website": "http://vitraining.com",
	"images": [
		"static/description/images/main_screenshot.jpg"
	],
	"price": "100",
	"license": "OPL-1",
	"currency": "USD",
	"summary": "",
	"description": "",
	"data": [
		"security/groups.xml",
		"security/ir.model.access.csv",
		"view/menu.xml",
		"view/customer.xml",
		"view/property_unit.xml",
		"view/rent_transaction.xml",
		"report/rent_transaction.xml",
		"data/sequence_rent_transaction.xml",
		"view/stage.xml",
		"view/rent_type.xml",
		"report/rent_type.xml"
	],
	"installable": True,
	"auto_install": False,
	"application": True,
	"odooVersion": 18
}