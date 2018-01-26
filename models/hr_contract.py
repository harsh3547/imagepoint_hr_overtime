# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp


class HrContract(models.Model):
	_inherit = 'hr.contract'

	normal_ot_rate = fields.Float(string='Normal Day OT Rate',digits=dp.get_precision('Product Price'),default=1.25)
	holiday_ot_rate = fields.Float(string='Holiday Day OT Rate',digits=dp.get_precision('Product Price'),default=1.50)
