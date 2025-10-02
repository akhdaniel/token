#-*- coding: utf-8 -*-

{
	"name": "Property",
	"version": "1.0",
	"depends": [
		"base",
		"account",
		"sale_management"
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
		"view/investor.xml",
		"view/product_template.xml",
		"view/sale_order.xml",
		"view/property_unit.xml",
		"report/property_unit.xml",
		"data/sequence_property_unit.xml",
		"view/owner.xml",
		"view/property_profit_share.xml",
		"report/property_profit_share.xml",
		"data/sequence_property_profit_share.xml",
		"view/property_profit_share_line.xml",
		"report/property_profit_share_line.xml",
		"view/account_move.xml",
		"view/sale_order_line.xml",
		"view/token.xml",
		"view/order_token.xml",
		"report/order_token.xml",
		"data/sequence_order_token.xml",
		"view/property_token_move.xml",
		"report/property_token_move.xml",
		"view/stage.xml",
		"view/currency.xml",
		"view/property_unit_image.xml",
		"report/property_unit_image.xml",
		"view/owner_users.xml",
		"view/payment_request.xml",
		"report/payment_request.xml",
		"data/sequence_payment_request.xml",
		"view/bank.xml",
		"view/document_type.xml",
		"report/document_type.xml",
		"data/vit.document_type.csv",
		"view/property_document.xml",
		"report/property_document.xml",
		"view/token_owner.xml"
	],
	"installable": True,
	"auto_install": False,
	"application": True,
	"odooVersion": 18,
	"menus": [
		"Properties"
	]
}