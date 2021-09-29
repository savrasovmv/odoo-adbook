# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Settings(models.TransientModel):
    _inherit = 'res.config.settings'

    # LDAP
    ldap_host = fields.Char(u'LDAP host')
    ldap_port = fields.Char(u'Ldap port', default='636')
    ldap_ssl = fields.Boolean(u'SSL?', default=True)
    ldap_user = fields.Char(u'Пользователь ldap', default='')
    ldap_password = fields.Char(u'Пароль ldap', default='')
    ldap_search_base = fields.Char(u'search_base', default='')
    ldap_search_filter = fields.Char(u'ldap_search_filter', default='(|(objectClass=user)(objectClass=user))')
    ldap_search_group_filter = fields.Char(u'ldap_search_group_filter', default='(objectClass=group)')
    ldap_connect_timeout = fields.Integer(u'LDAP timeout, сек', default=30)

    # ЗУП
    zup_user = fields.Char(u'Пользователь ЗУП', default='')
    zup_password = fields.Char(u'Пароль ЗУП', default='')
    zup_timeout = fields.Integer(u'Timeout, сек', default=10)
    zup_url_get_empl_list = fields.Char(u'Список сотрудников', default='', help='URL API позвращает полный список работающих сотрудников на текущий момент')
    zup_url_get_dep_list = fields.Char(u'Список подразделений', default='', help='URL API позвращает полный список подразделений организации')
    zup_url_get_passport_list = fields.Char(u'Список документов УЛ и адресов', default='', help='URL API позвращает полный список документов УЛ и адресов сотрудников')

    zup_url_get_recruitment_doc_list = fields.Char(u'Список документов Прием на работу', default='', help='URL API позвращает полный список документов Прием на работу сотрудников')
    zup_url_get_termination_doc_list = fields.Char(u'Список документов Увольнения', default='', help='URL API позвращает полный список документов Увольнения сотрудников')
    zup_url_get_vacation_doc_list = fields.Char(u'Список документов Отпуска', default='', help='URL API позвращает полный список документов Отпуска сотрудников')
    zup_url_get_trip_doc_list = fields.Char(u'Список документов Командировки', default='', help='URL API позвращает полный список документов Командировки сотрудников')
    zup_url_get_sick_leave_doc_list = fields.Char(u'Список документов Больничные', default='', help='URL API позвращает полный список документов Больничные сотрудников')
    zup_url_get_transfer_doc_list = fields.Char(u'Список документов Переводы сотрудников', default='', help='URL API позвращает полный список документов Переводы сотрудников')
    zup_url_get_multi_transfer_doc_list = fields.Char(u'Список документов Переводы сотрудников (группа)', default='', help='URL API позвращает полный список документов Переводы сотрудников групповой документ')

    
    @api.model
    def get_values(self):
        res = super(Settings, self).get_values()
        conf = self.env['ir.config_parameter']
        res.update({
                'ldap_host': conf.get_param('ldap_host'),
                'ldap_port': conf.get_param('ldap_port'),
                'ldap_ssl': conf.get_param('ldap_ssl'),
                'ldap_user': conf.get_param('ldap_user'),
                'ldap_password': conf.get_param('ldap_password'),
                'ldap_search_base': conf.get_param('ldap_search_base'),
                'ldap_search_filter': conf.get_param('ldap_search_filter'),
                'ldap_search_group_filter': conf.get_param('ldap_search_group_filter'),
                'ldap_connect_timeout': conf.get_param('ldap_connect_timeout'),

                'zup_user': conf.get_param('zup_user'),
                'zup_password': conf.get_param('zup_password'),
                'zup_timeout': conf.get_param('zup_timeout'),
                'zup_url_get_empl_list': conf.get_param('zup_url_get_empl_list'),
                'zup_url_get_dep_list': conf.get_param('zup_url_get_dep_list'),
                'zup_url_get_passport_list': conf.get_param('zup_url_get_passport_list'),

                'zup_url_get_recruitment_doc_list': conf.get_param('zup_url_get_recruitment_doc_list'),
                'zup_url_get_termination_doc_list': conf.get_param('zup_url_get_termination_doc_list'),
                'zup_url_get_vacation_doc_list': conf.get_param('zup_url_get_vacation_doc_list'),
                'zup_url_get_trip_doc_list': conf.get_param('zup_url_get_trip_doc_list'),
                'zup_url_get_sick_leave_doc_list': conf.get_param('zup_url_get_sick_leave_doc_list'),
                'zup_url_get_transfer_doc_list': conf.get_param('zup_url_get_transfer_doc_list'),
                'zup_url_get_multi_transfer_doc_list': conf.get_param('zup_url_get_multi_transfer_doc_list'),
                
        })
        return res


    def set_values(self):
        super(Settings, self).set_values()
        conf = self.env['ir.config_parameter']
        conf.set_param('ldap_host', str(self.ldap_host))
        conf.set_param('ldap_port', str(self.ldap_port))
        conf.set_param('ldap_ssl', self.ldap_ssl)
        conf.set_param('ldap_user', str(self.ldap_user))
        conf.set_param('ldap_password', str(self.ldap_password))
        conf.set_param('ldap_search_base', str(self.ldap_search_base))
        conf.set_param('ldap_search_filter', str(self.ldap_search_filter))
        conf.set_param('ldap_search_group_filter', str(self.ldap_search_group_filter))
        conf.set_param('ldap_connect_timeout', int(self.ldap_connect_timeout))

        conf.set_param('zup_user', str(self.zup_user))
        conf.set_param('zup_password', str(self.zup_password))
        conf.set_param('zup_timeout', int(self.zup_timeout))
        conf.set_param('zup_url_get_empl_list', str(self.zup_url_get_empl_list))
        conf.set_param('zup_url_get_dep_list', str(self.zup_url_get_dep_list))
        conf.set_param('zup_url_get_passport_list', str(self.zup_url_get_passport_list))

        conf.set_param('zup_url_get_recruitment_doc_list', str(self.zup_url_get_recruitment_doc_list))
        conf.set_param('zup_url_get_termination_doc_list', str(self.zup_url_get_termination_doc_list))
        conf.set_param('zup_url_get_vacation_doc_list', str(self.zup_url_get_vacation_doc_list))
        conf.set_param('zup_url_get_trip_doc_list', str(self.zup_url_get_trip_doc_list))
        conf.set_param('zup_url_get_sick_leave_doc_list', str(self.zup_url_get_sick_leave_doc_list))
        conf.set_param('zup_url_get_transfer_doc_list', str(self.zup_url_get_transfer_doc_list))
        conf.set_param('zup_url_get_multi_transfer_doc_list', str(self.zup_url_get_multi_transfer_doc_list))
