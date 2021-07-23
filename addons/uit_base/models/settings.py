# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Settings(models.TransientModel):
    _inherit = 'res.config.settings'

    ldap_host = fields.Char(u'LDAP host')
    ldap_port = fields.Char(u'Ldap port', default='636')
    ldap_ssl = fields.Boolean(u'SSL?', default=True)
    ldap_user = fields.Char(u'Пользователь ldap', default='')
    ldap_password = fields.Char(u'Пароль ldap', default='')
    ldap_search_base = fields.Char(u'search_base', default='')
    ldap_search_filter = fields.Char(u'ldap_search_filter', default='(|(objectClass=user)(objectClass=user))')
    ldap_search_group_filter = fields.Char(u'ldap_search_group_filter', default='(objectClass=group)')

    
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
