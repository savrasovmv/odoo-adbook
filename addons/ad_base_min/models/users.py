# -*- coding: utf-8 -*-

from odoo import fields, models, api
import base64
import re


class AdOU(models.Model):
    _name = "ad.ou"
    _description = "Организационное подразделение AD"
    _order = "name"

    name = fields.Char(u'Наименование', required=True)
    active = fields.Boolean('Active', default=True)
    is_default = fields.Boolean(string='AD контейнер по умолчанию', help='Если установлено, новые пользователи не вошедшие не в одну группу будут создаваться тут')
    hr_department_id = fields.Many2one("hr.department", string="HR Подразделене")



class AdDepartment(models.Model):
    _name = "ad.department"
    _description = "Подразделения AD"
    _order = "name"

    name = fields.Char(u'Наименование', required=True)
    ou_id = fields.Many2one("ad.ou", string="Организационное подразделение AD")
    active = fields.Boolean('Active', default=True)



flags = [
    [0x0001, 'SCRIPT'],
    [0x0002, 'ACCOUNTDISABLE'],
    [0x0008, 'HOMEDIR_REQUIRED'],
    [0x0010, 'LOCKOUT'],
    [0x0020, 'PASSWD_NOTREQD'],
    [0x0040, 'PASSWD_CANT_CHANGE'],
    [0x0080, 'ENCRYPTED_TEXT_PWD_ALLOWED'],
    [0x0100, 'TEMP_DUPLICATE_ACCOUNT'],
    [0x0200, 'NORMAL_ACCOUNT'],
    [0x0800, 'INTERDOMAIN_TRUST_ACCOUNT'],
    [0x1000, 'WORKSTATION_TRUST_ACCOUNT'],
    [0x2000, 'SERVER_TRUST_ACCOUNT'],
    [0x10000, 'DONT_EXPIRE_PASSWORD'],
    [0x20000, 'MNS_LOGON_ACCOUNT'],
    [0x40000, 'SMARTCARD_REQUIRED'],
    [0x80000, 'TRUSTED_FOR_DELEGATION'],
    [0x100000, 'NOT_DELEGATED'],
    [0x200000, 'USE_DES_KEY_ONLY'],
    [0x400000, 'DONT_REQ_PREAUTH'],
    [0x800000, 'PASSWORD_EXPIRED'],
    [0x1000000, 'TRUSTED_TO_AUTH_FOR_DELEGATION'],
    [0x04000000, 'PARTIAL_SECRETS_ACCOUNT'],
  ]


class AdUsers(models.Model):
    _name = "ad.users"
    _description = "Пользователи AD"
    _order = "name"

    name = fields.Char(u'ФИО', required=True)
    employee_id = fields.Many2one("hr.employee", string="Сотрудник")

    active = fields.Boolean('Active', default=True)
    is_ldap = fields.Boolean('LDAP?', default=False)

    # organization_id = fields.Many2one("ad.organizacion", string="Организация", compute="_compute_organization", store=True)
    # company_id = fields.Many2one('res.company', string='Компания', compute="_compute_company", store=True)

    ou_id = fields.Many2one("ad.ou", string="Организационное подразделение AD")
    department_id = fields.Many2one("ad.department", string="Подразделение AD")
    title = fields.Char(u'Должность')

    ip_phone = fields.Char(u'Вн. номер')
    phone = fields.Char(u'Мобильный телефон 1')
    sec_phone = fields.Char(u'Мобильный телефон 2')

    email = fields.Char(u'E-mail')

    username = fields.Char(u'sAMAccountName')
    object_SID = fields.Char(u'AD objectSID')
    photo = fields.Binary('Фото', default=False)


    def get_employee_by_name(self):
        """Связывает пользователей АД с сотрудниками"""
        for user in self:
            empl = self.env['hr.employee'].search([
                ('name', '=', user.name),
                '|',
                ('active', '=', False), 
                ('active', '=', True)

            ], limit=1)


            if len(empl)>0:
                user.employee_id = empl[0].id
                employee = self.env['hr.employee'].browse(empl[0].id)
               
                if user.photo:
                    employee.image_1920 = user.photo
                else:
                    employee._default_image()

                employee.ad_users_id = user.id
                employee.mobile_phone = user.phone
                employee.mobile_phone2 = user.sec_phone
                employee.ip_phone = user.ip_phone
                employee.work_email = user.email

            else:
                user.employee_id = None

    
    def join_user_and_employee(self, full_sync=False):
        for user in self.search([]):
            if not user.employee_id or full_sync:
                user.get_employee_by_name()



    

    




    




