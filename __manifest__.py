# -*- coding: utf-8 -*-
{
    'name': "Imagepoint HR Overtime",

    'summary': """
        HR Overtime feature""",

    'description': """
        Overtime of employees is calculated according to the attendance and payroll structure
    """,

    'author': "harsh jain",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Payroll',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr_payroll','hr_attendance','hr_holidays','hr_public_holidays'],

    'data': ['views/resource_calendar_view.xml',
            'views/hr_contract_view.xml',
            'views/hr_holidays_view.xml',]

    
}