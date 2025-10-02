#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class document_type(models.Model):

	_name = "vit.document_type"
	_inherit = "vit.document_type"
