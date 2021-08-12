# -*- coding: utf-8 -*-

from odoo import fields, models, api
from ldap3 import Server, Connection, SUBTREE, MODIFY_REPLACE, LEVEL


class AdGroup(models.Model):
    _name = "ad.group"
    _description = "Группы AD"
    _order = "name"

    name = fields.Char(u'Наименование', required=True, readonly=True)

    distinguished_name = fields.Char(u'AD distinguishedName', readonly=True)
    account_name = fields.Char(u'sAMAccountName', readonly=True)
    object_SID = fields.Char(u'AD objectSID', readonly=True)
    is_ldap = fields.Boolean('LDAP?', default=False, readonly=True)

    active = fields.Boolean('Active', default=True)
    is_managed = fields.Boolean('Управляемая', default=False, help="Включите, для управления вхождения сотрудника в эту группу в форме Сотрудника")



class AdSyncLog(models.Model):
    _name = "ad.sync_log"
    _description = "Журнал синхронизаций AD"
    _order = "name"

    name = fields.Char(u'Объект', readonly=True)
    result = fields.Text(string='Результат', readonly=True)
    is_error = fields.Boolean(string='С ошибкой')
    

