# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Модуль синхронизации с AD и 1С:ЗУП',
    "author": "Savrasov Mikhail <savrasovmv@tmenergo.ru> ",
    'version': '14',
    'category': 'HR',
    'sequence': 15,
    'summary': 'Синхронизация сотрудников с 1С и AD',
    'description': "Загружает информацию из 1С:ЗУП используя рзработанное api: сотрудники, подрзделения, документы: удостоверения личности, адреса, прием на работу, увольнение, отпуска, командировки, больничные. \n Згружает информацию из AD: пользователей, группы. Создет и изменяется пользователей AD, в соответствии с изменениями сотрудников 1С:ЗУП. ",
    'external_dependencies': {'python': ['requests']},
    'depends': [
        'base',
        'hr_adbook',
    ],
    'data': [
        
        'views/settings_views.xml',
        'wizard/sync_wizard_views.xml',
        'views/sync_log_views.xml',
        'cron/cron_ad_group_sync_views.xml',
        'views/menu.xml',

        'security/ir.model.access.csv',

    ],

    'installable': True,
    'application': True,
    'auto_install': False
}