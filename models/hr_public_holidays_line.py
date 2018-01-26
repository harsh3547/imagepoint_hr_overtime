# -*- coding: utf-8 -*-

from odoo import api, fields, models

class HrPublicHolidaysLine(models.Model):
    _inherit = 'hr.holidays.public.line'

    year_id = fields.Many2one(
        'hr.holidays.public',
        'Calendar Year',
        required=True, ondelete='cascade'
    )