from odoo import fields, models, api
from ldap3 import Server, Connection, SUBTREE, MODIFY_REPLACE, LEVEL
import json
import base64
import re

from openpyxl import Workbook
import os, fnmatch
from openpyxl.styles import Alignment, Border, Side, PatternFill, Font

# class AdbookBranch(models.Model):
#     _name = "adbook.branch"
#     _description = "Подразделения"
#     _order = "sequence"

#     name = fields.Char(u'Наименование в AD', required=True)
#     adbook_name  = fields.Char(u'Наименование')
#     ad_branch_id = fields.Many2one("ad.branch", string="Подразделение AD")
#     company_id = fields.Many2one('res.company', string='Компания')
#     sequence = fields.Integer(string=u"Сортировка", help="Сортировка", default=10)
#     date_update = fields.Datetime(string='Обновлено')


class AdbookDepartment(models.Model):
    _name = "adbook.department"
    _description = "Управления/отделы"
    _order = "name"
    # _parent_store = True
    # _parent_name = "parent_id" 
    # parent_path = fields.Char(index=True)

    name = fields.Char(u'Наименование (1С)', required=True, default="Другие")
    adbook_name = fields.Char(u'Наименование в справочнике')
    hr_department_id = fields.Many2one("hr.department", string="HR управления/отделы")
    ad_department_id = fields.Many2one("ad.department", string="AD управления/отделы")
    ad_branch_id = fields.Many2one("ad.branch", string="AD подразделения")
    
    # company_id = fields.Many2one('res.company', string='Компания', compute="_get_company", store=True)
    company_id = fields.Many2one('res.company', string='Компания')
    branch_id = fields.Many2one("adbook.department", string="Подразделение(осн)")
    # branch_id = fields.Many2one("adbook.branch", string="Подразделение")
    parent_id = fields.Many2one("adbook.department", string="Родитель")
    sequence = fields.Integer(string=u"Сортировка", help="Сортировка", default=10)  
    date_update = fields.Datetime(string='Обновлено')
    is_default = fields.Boolean(string='По умолчанию для пустых', help="Для сотрудников у которых не задан отдел, будет помещен в этот отдел")
    is_records = fields.Boolean(string='Есть записи', help="Если установлено, значит в этом подразделение есть сотрудники")
    level = fields.Integer(string='Уровень')
   
    child_ids = fields.One2many('adbook.department', 'parent_id', string='Дочернии подразделения')
    employer_ids = fields.One2many('adbook.employer', 'department_id', string='Сотрудники подразделения')

    is_show_full = fields.Boolean(string='Показать все поля', help="Если установлено, значит подразделение установленно в ручную", default=False, store=False)

    # parent_left = fields.Integer('Left Parent', index=True)
    # parent_right = fields.Integer('Right Parent', index=True)

    @api.model
    def create(self, vals):
        if not 'name' in vals or vals['name'] == '':
            vals['name'] = 'Другое'
            
        return super(AdbookDepartment, self).create(vals)


    # @api.depends("branch_id.company_id")
    # def _get_company(self):
    #     for dep in self:
    #         dep.company_id = dep.branch_id.company_id.id


class AdbookEmployer(models.Model):
    _name = "adbook.employer"
    _description = "Сотрудники"
    _order = "name"

    name = fields.Char(u'ФИО', required=True)
    hr_employee_id = fields.Many2one("hr.employee", string="Сотрудник HR")
    ad_users_id = fields.Many2one("ad.users", string="Пользователь AD")
    company_id = fields.Many2one('res.company', string='Компания', compute="_get_company", store=True)

    branch_id = fields.Many2one("adbook.department", string="Подразделение")
    department_id = fields.Many2one("adbook.department", string="Управление/отдел")
    title = fields.Char(u'Должность')
    ip_phone = fields.Char(u'Вн. номер')
    phone = fields.Char(u'Мобильный телефон 1')
    sec_phone = fields.Char(u'Мобильный телефон 2')

    email = fields.Char(u'E-mail')
    photo = fields.Binary('Фото', default=None)

    # is_fired = fields.Boolean(string='Уволен', default=False)
    # fired_date = fields.Date(string='Дата увольнения')

    # is_vacation = fields.Boolean(string='Отпуск')
    # vacation_start_date = fields.Date(string='Дата начала отпуска')
    # vacation_end_date = fields.Date(string='Дата окончания отпуска')

    # is_btrip = fields.Boolean(string='Командировка')
    # btrip_start_date = fields.Date(string='Дата начала командировки')
    # btrip_end_date = fields.Date(string='Дата окончания командировки')

    service_status = fields.Selection([
        ('work', 'На работе'),
        ('vacation', 'Отпуск'),
        ('trip', 'Командировка'),
        ('sick_leave', 'Больничный'),
    ], string='Статус', readonly=True, default='work')

    service_status_start_date = fields.Date(string='Начало', readonly=True)
    service_status_end_date = fields.Date(string='Окончание', readonly=True)
    

    search_text = fields.Char(u'Поисковое поле', compute="_get_search_text", store=True, index=True)

    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer(string=u"Сортировка", help="Сортировка", default=10)
    date_update = fields.Datetime(string='Обновлено')
    is_view_adbook = fields.Boolean(string='Отоброжать в справочнике контактов', default=True)

    is_manual = fields.Boolean(string='Ручная корректировка', help="Если установлено, значит подразделение установленно в ручную", default=False)




    @api.depends("branch_id.company_id")
    def _get_company(self):
        for emp in self:
            emp.company_id = emp.branch_id.company_id.id

    @api.depends("name", "ip_phone", "phone","sec_phone", "email")
    def _get_search_text(self):
        for user in self:
            if user:
                ip_phone = re.sub('\D', '', user.ip_phone) if user.ip_phone else ''
                phone = re.sub('\D', '', user.phone) if user.phone else ''
                sec_phone = re.sub('\D', '', user.sec_phone) if user.sec_phone else ''
                email = user.email if user.email else ''
                user.search_text = str(user.name) + " " + str(ip_phone) + " " + str(phone)  + " " + str(sec_phone) + " " + str(email)