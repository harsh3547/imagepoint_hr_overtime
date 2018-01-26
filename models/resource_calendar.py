# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    days_per_month = fields.Selection(string='Working Days per month (salary calculations) *',
							    	selection=[('custom','Actual Days in that particular month'),(31,31),(30,30),(29,29),(28,28),(27,27),(26,26),(25,25),(24,24),(23,23),(22,22),(21,21),(20,20)],
							    	default='custom')


