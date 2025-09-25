#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class investor(models.Model):

	_name = "res.partner"
	_description = "res.partner"


	def action_reload_view(self):
		pass



	_inherit = "res.partner"
	is_investor = fields.Boolean( string=_("Is Investor"), default=False)
	ktp_number = fields.Char( string=_("Ktp Number"))
	ktp_image = fields.Binary( string=_("Ktp Image"))
	selfie_ktp = fields.Binary( string=_("Selfie Ktp"))
	npwp_number = fields.Char( string=_("Npwp Number"))
	npwp_image = fields.Binary( string=_("Npwp Image"))
	bank_name = fields.Char( string=_("Bank Name"))
	bank_account_number = fields.Char( string=_("Bank Account Number"))
	bank_account_name = fields.Char( string=_("Bank Account Name"))
	total_investment = fields.Float( string=_("Total Investment"))
	total_tokens = fields.Integer( string=_("Total Tokens"))
	total_dividend_received = fields.Float( string=_("Total Dividend Received"))
	kyc_status = fields.Selection(selection=[('pending', 'Pending'),('approved', 'Approved'),('rejected', 'Rejected')],default='pending',  string=_("Kyc Status"))
	kyc_approved_date = fields.Datetime( string=_("Kyc Approved Date"))


