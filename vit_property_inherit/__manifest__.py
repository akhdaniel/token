#-*- coding: utf-8 -*-

{
	"name": "Property Inherited",
	"version": "1.0",
	"depends": [
		"base",
		"account",
		"sale_management",
		"vit_property"
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
		"security/ir.model.access.csv",
		"security/portal_access.xml",
		"view/investor.xml",
		"view/token.xml",
		#"view/sale_order.xml",
		"view/property_unit.xml",
		"view/owner.xml",
		"view/property_profit_share.xml",
		#"data/sequence_property_profit_share.xml",
		#"view/property_profit_share_line.xml",
		#"view/account_move.xml",
		#"view/sale_order_line.xml",
		"view/product_product.xml",
		"view/product_template.xml",
		"view/order_token.xml",
		#"data/sequence_order_token.xml",
		#"view/property_token_move.xml",
		#"view/stage.xml"
	],
	"installable": True,
	"auto_install": False,
	"application": True,
	"odooVersion": 18,
	# "menus": [
	# 	"Properties",
	# 	"Order Token",
	# 	"Token Ledger",
	# 	"Profit Share"
	# ]
}