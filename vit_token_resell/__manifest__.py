#-*- coding: utf-8 -*-

{
	"name": "Token Resell",
	"version": "1.0",
	"depends": [
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
		"view/token_resell.xml",
		"report/token_resell.xml",
		"data/sequence_token_resell.xml",
		"view/property_unit.xml",
		"view/investor.xml",
		"view/stage.xml",
		"view/order_token.xml"
	],
	"installable": True,
	"auto_install": False,
	"application": True,
	"odooVersion": 18
}