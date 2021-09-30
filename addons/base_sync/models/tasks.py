# -*- coding: utf-8 -*-

from odoo import fields, models, api
from ldap3 import Server, Connection, SUBTREE, MODIFY_REPLACE, LEVEL


class SyncTasks(models.Model):
    _name = "sync.tasks"
    _description = "Задачи синхронизации"
    _order = "name"

    name = fields.Char(u'Наименование', required=True)
    date = fields.Datetime(string='Дата')
    obj_create = fields.Char(u'Модель')
    obj_create_name = fields.Char(u'Имя модели')
    obj_create_id = fields.Char(u'Id записи')
    is_completed = fields.Boolean(string='Выполнена?')
    