# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'UIT Base module',
    'version': '1',
    'category': 'SM',
    'sequence': 15,
    'summary': 'Общий модуль',
    'description': "Общие объекты/модели",
    'depends': [
        # 'base_setup',
        'base',
        'web',
        # 'website'
    ],
    'data': [
        
        'views/organizacion_views.xml',
        'views/branch_views.xml',
        'views/department_views.xml',
        'views/employer_views.xml',
        'views/ad_sync_wizard_view.xml',
        'views/settings_view.xml',
        'views/ad_menu.xml',
        'views/templates_head.xml',
        'views/templates_list.xml',
        'views/templates_list_search.xml',
        'views/templates.xml',
        
        'security/ir.model.access.csv',

    ],

    'js': [
        #'static/src/js/adbook.js',
    ],

    'css': [
        'static/src/css/uit_base.css',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}