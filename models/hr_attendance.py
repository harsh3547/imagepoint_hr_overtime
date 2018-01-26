# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
import pytz
from datetime import timedelta

from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class HrAttendance(models.Model):
	_inherit = "hr.attendance"

	def get_attendance_intervals(self,selected_date, employee_id):
		"""
		Returns the attendance intervals for the employee for the selected_date
		:param selected_date: datetime object or string
		:param employee_id: ID of the employee
		:return: list of tuples of datetime intervals in local timezone 
		"""
  		
  		# the selected_date is just a date , but attendance intervals in databse are in UTC with date and time .
  		# so if attendance is 2017-11-30 00:00:00 entered in erp , it will become , 2017-11-29 21:00:00 in database if tz=QATAR , therefore the need for start_dt , end_dt
  		# but returning dattimes in local timezone instead of UTC coz , returned values need again to be compared with date.
		
		if isinstance(selected_date, basestring):
			selected_date = fields.Datetime.from_string(selected_date)
		tz_info = fields.Datetime.context_timestamp(self, selected_date).tzinfo
		start_date = selected_date.replace(hour=0, minute=0, second=0,tzinfo=tz_info).astimezone(pytz.UTC).replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
		end_dt = selected_date.replace(hour=23, minute=59, second=59,tzinfo=tz_info).astimezone(pytz.UTC).replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
		res = self.search(args=[('check_in','>=',start_date),('check_out','<=',end_dt),('employee_id','=',employee_id)],order='create_date desc')
		result=[]
		
		for rec in res:
			check_in=fields.Datetime.from_string(rec.check_in).replace(tzinfo=pytz.UTC).astimezone(tz_info).replace(tzinfo=None)
			check_out=fields.Datetime.from_string(rec.check_out).replace(tzinfo=pytz.UTC).astimezone(tz_info).replace(tzinfo=None)
			if check_in.date()==selected_date.date():
				result.append((rec,check_in,check_out))

		#print "attendance intervals ---",result
		return result

