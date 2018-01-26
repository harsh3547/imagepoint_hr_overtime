# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from datetime import datetime, timedelta
from dateutil import relativedelta
from calendar import monthrange

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):

    	res_super = super(HrPayslip,self).get_worked_day_lines(contract_ids,date_from,date_to)

    	import pdb
    	#pdb.set_trace()

    	def was_on_leave_interval(employee_id, date_from, date_to):
            date_from = fields.Datetime.to_string(date_from)
            date_to = fields.Datetime.to_string(date_to)
            return self.env['hr.holidays'].search([
                ('state', '=', 'validate'),
                ('employee_id', '=', employee_id),
                ('type', '=', 'remove'),
                ('date_from', '<=', date_from),
                ('date_to', '>=', date_to)
            ], limit=1)

        res = []
        #fill only if the contract as a working schedule linked
        uom_day = self.env.ref('product.product_uom_day', raise_if_not_found=False)
        public_holiday_env=self.env['hr.holidays.public']
        for contract in self.env['hr.contract'].browse(contract_ids).filtered(lambda contract: contract.working_hours):
            uom_hour = contract.employee_id.resource_id.calendar_id.uom_id or self.env.ref('product.product_uom_hour', raise_if_not_found=False)
            interval_data = []
            holidays = self.env['hr.holidays']
            working_days = {
                 'name': _("Normal Working Days **"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            working_days_attendances = {
                 'name': _("Normal Working Days Attendance Total"),
                 'sequence': 5,
                 'code': 'WORKED',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            working_days_attendances_OT = {
                 'name': _("Normal Working Days OT Total"),
                 'sequence': 7,
                 'code': 'WORKED_OT',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            leaves = {}
            weekends_holiday = {
                'name':_("Weekend & Public Holidays **"),
                'sequence':3,
                'code':'HOLIDAY',
                'number_of_days':0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }
            weekends_holiday_OT = {
                'name':_("Weekend & Public Holidays OT Total"),
                'sequence':9,
                'code':'HOLIDAY_OT',
                'number_of_days':0.0,
                'number_of_hours': 0.0,
                'contract_id': contract.id,
            }

            day_from = fields.Datetime.from_string(date_from)
            day_to = fields.Datetime.from_string(date_to)
            nb_of_days = (day_to - day_from).days + 1

            # Gather all intervals and holidays
            for day in range(0, nb_of_days):
                start_dt=day_from + timedelta(days=day)
                is_public_holiday=public_holiday_env.is_public_holiday(selected_date=start_dt,employee_id=contract.employee_id.id)
                working_intervals_on_day = contract.working_hours.get_working_intervals_of_day(start_dt=start_dt)

                #print "------start_dt--",start_dt,type(start_dt)
                #print "---working intervals--",working_intervals_on_day
                attendance_intervals_on_day = self.env['hr.attendance'].get_attendance_intervals(selected_date=start_dt, employee_id=contract.employee_id.id)
                

                if not working_intervals_on_day or is_public_holiday:
                    weekends_holiday['number_of_days']+=1
                    weekends_holiday['number_of_hours']=uom_day._compute_quantity(weekends_holiday['number_of_days'], uom_hour)\
                         if uom_day and uom_hour\
                         else weekends_holiday['number_of_days'] * 10.0
                    
                    if attendance_intervals_on_day:
                        weekends_holiday_OT['number_of_days'] +=1
                        for rec_ot in attendance_intervals_on_day:
                            weekends_holiday_OT['number_of_hours'] += rec_ot[0].worked_hours
                    continue # continue because no need to include workings intervals in workings days if it is a public holiday and if no working_intervals then it is a weekend


                if attendance_intervals_on_day:
                    working_days_attendances['number_of_days'] +=1
                    att_for_the_day=0.0
                    for rec_att in attendance_intervals_on_day:
                        working_days_attendances['number_of_hours'] += rec_att[0].worked_hours
                        att_for_the_day += rec_att[0].worked_hours
                    working_hours_on_day = contract.working_hours.get_working_hours_of_date(start_dt=start_dt)
                    if att_for_the_day>working_hours_on_day:
                        working_days_attendances_OT['number_of_days'] +=1
                        working_days_attendances_OT['number_of_hours'] += (att_for_the_day - working_hours_on_day)

                for interval in working_intervals_on_day:
                    interval_data.append((interval, was_on_leave_interval(contract.employee_id.id, interval[0], interval[1])))

            # Extract information from previous data. A working interval is considered:
            # - as a leave if a hr.holiday completely covers the period
            # - as a working period instead
            for interval, holiday in interval_data:
                holidays |= holiday
                hours = (interval[1] - interval[0]).total_seconds() / 3600.0
                if holiday:
                    #if he was on leave, fill the leaves dict
                    if holiday.holiday_status_id.name in leaves:
                        leaves[holiday.holiday_status_id.name]['number_of_hours'] += hours
                    else:
                        leaves[holiday.holiday_status_id.name] = {
                            'name': holiday.holiday_status_id.name+" **",
                            'sequence': 11,
                            'code': holiday.holiday_status_id.name.upper().replace(' ','_'),
                            'number_of_days': 0.0,
                            'number_of_hours': hours,
                            'contract_id': contract.id,
                        }
                else:
                    #add the input vals to tmp (increment if existing)
                    working_days['number_of_hours'] += hours

            # Clean-up the results
            leaves = [value for key, value in leaves.items()]
            for data in [working_days] + leaves:
                data['number_of_days'] = uom_hour._compute_quantity(data['number_of_hours'], uom_day)\
                    if uom_day and uom_hour\
                    else data['number_of_hours'] / 10.0
                res.append(data)
            if weekends_holiday['number_of_hours']!=0.0:res.append(weekends_holiday)
            if working_days_attendances['number_of_hours']!=0.0:res.append(working_days_attendances)
            if working_days_attendances_OT['number_of_hours']!=0.0:res.append(working_days_attendances_OT)
            if weekends_holiday_OT['number_of_hours']!=0.0:res.append(weekends_holiday_OT)

        #print "-==-==========",res
        return res

    @api.model
    def get_inputs(self, contract_ids, date_from, date_to):
        
        res = super(HrPayslip,self).get_inputs(contract_ids,date_from,date_to)
        if isinstance(date_from, basestring):
            date_from = fields.Datetime.from_string(date_from)
        if isinstance(date_to, basestring):
            date_to = fields.Datetime.from_string(date_to)
        contracts = self.env['hr.contract'].browse(contract_ids)
        total_months=0
        total_days=0
        uom_day = self.env.ref('product.product_uom_day', raise_if_not_found=False)
        for contract in contracts:
            if contract.working_hours:
                uom_hour = contract.employee_id.resource_id.calendar_id.uom_id or self.env.ref('product.product_uom_hour', raise_if_not_found=False)
                if contract.schedule_pay=='monthly':
                    
                    days_in_month = 30
                    if contract.working_hours.days_per_month=='custom':
                        days_in_month = 'custom'
                    else:
                        days_in_month = contract.working_hours.days_per_month

                    for month in range(date_from.month,date_to.month+1):
                        total_months += 1
                        
                        if days_in_month=='custom':
                            total_days += monthrange(date_from.year, month)[1]
                        else:   
                            total_days += days_in_month

                    hour_per_day = uom_day._compute_quantity(1, uom_hour)\
                             if uom_day and uom_hour\
                             else 1 * 10.0
                    input_data = {
                        'name': "Hourly Salary "+str(contract.wage)+'x'+str(total_months)+'/'+str(total_days)+'/'+str(hour_per_day),
                        'code': 'HOURLY_SALARY',
                        'amount':contract.wage*total_months/(total_days*hour_per_day),
                        'contract_id': contract.id,
                    }
                    res += [input_data]
                    
        return res
