# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Adbook синхронизация',
    "author": "Savrasov Mikhail <savrasovmv@tmenergo.ru> ",
    'version': '14',
    'category': 'HR',
    'sequence': 15,
    'summary': 'Синхронизация сотрудников с 1С и AD',
    'description': "Синхронизация сотрудников с 1С и AD",
    'external_dependencies': {'python': ['requests']},
    'depends': [
        'base',
        'hr_adbook',
    ],
    'data': [
        
        'views/settings_views.xml',
        'wizard/ad_sync_wizard_views.xml',
        'views/ad_group_views.xml',
        'views/ad_sync_log_views.xml',
        'views/cron_ad_group_sync_views.xml',
        'views/menu.xml',

        'security/ir.model.access.csv',

    ],

    'installable': True,
    'application': True,
    'auto_install': False
}