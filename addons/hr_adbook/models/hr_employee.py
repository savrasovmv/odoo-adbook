from dateutil.relativedelta import relativedelta
from datetime import timedelta
from math import fabs

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # 1С
    guid_1c = fields.Char(string='guid1C', readonly=True, groups="base.group_erp_manager, base.group_system")
    employment_type_1c = fields.Char(string='Вид занятости', readonly=True)
    number_1c = fields.Char(string='Номер в 1С', readonly=True)

    # Возраст
    age = fields.Integer(string="Возраст", compute="_compute_age")
    
    # Доп Телефоны
    mobile_phone2 = fields.Char(string='Мобильный телефон 2')
    ip_phone = fields.Char(string='Внутренний номер')

    @api.depends("birthday")
    def _compute_age(self):
        for record in self:
            age = 0
            if record.birthday:
                age = relativedelta(fields.Date.today(), record.birthday).years
            record.age = age


    # Даты приема и увольнения
    service_start_date = fields.Date(
        string="Дата приема",
        groups="hr.group_hr_user",
        tracking=True,
        help=(
            "Дата с которой сотрудник устроен на работу (первый рабочий день) и исполняет обязанности по должности"
            
        ),
    )
    service_termination_date = fields.Date(
        string="Дата увольнения",
        groups="hr.group_hr_user",
        tracking=True,
        help=(
            "Дата увольнения сотрудника - последний рабочий день"
        ),
    )
    service_duration = fields.Integer(
        string="Отработано в днях",
        groups="hr.group_hr_user",
        readonly=True,
        compute="_compute_service_duration",
        help="Отработано дней в должности",
    )
    service_duration_years = fields.Integer(
        string="Отработано, лет",
        groups="hr.group_hr_user",
        readonly=True,
        compute="_compute_service_duration_display",
    )
    service_duration_months = fields.Integer(
        string="Отработано, мес",
        groups="hr.group_hr_user",
        readonly=True,
        compute="_compute_service_duration_display",
    )
    service_duration_days = fields.Integer(
        string="Отработано, дней",
        groups="hr.group_hr_user",
        readonly=True,
        compute="_compute_service_duration_display",
    )




    @api.depends("service_start_date", "service_termination_date")
    def _compute_service_duration(self):
        for record in self:
            service_until = record.service_termination_date or fields.Date.today()
            if record.service_start_date and service_until > record.service_start_date:
                service_since = record.service_start_date
                service_duration = fabs(
                    (service_until - service_since) / timedelta(days=1)
                )
                record.service_duration = int(service_duration)
            else:
                record.service_duration = 0

    @api.depends("service_start_date", "service_termination_date")
    def _compute_service_duration_display(self):
        for record in self:
            service_until = record.service_termination_date or fields.Date.today()
            if record.service_start_date and service_until > record.service_start_date:
                service_duration = relativedelta(
                    service_until, record.service_start_date
                )
                record.service_duration_years = service_duration.years
                record.service_duration_months = service_duration.months
                record.service_duration_days = service_duration.days
            else:
                record.service_duration_years = 0
                record.service_duration_months = 0
                record.service_duration_days = 0
    

    # NOTE: Support odoo/odoo@90731ad170c503cdfe89a9998fa1d1e2a5035c86
    def _get_date_start_work(self):
        return self.service_start_date or super()._get_date_start_work()
