# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ActiveDirectory базовый модуль (минимальный функционал)',
    'version': '1',
    'category': 'SM',
    "author": "Savrasov Mikhail <savrasovmv@tmenergo.ru> ",
    "website": "https://github.com/savrasovmv/",
    'sequence': 15,
    'summary': 'Базовый модуль для ActiveDirectory (минимальный функционал) для портала',
    'description': "Пользователей из ActiveDirectory, минимальный набор полей, необходим при синхронизации БД с IT службой и последующем обновлением справочника контактов. Является клоном it_ad_base с урезанным функционалом, содержит только данные",
    'depends': [
        'base',
    ],
    'data': [
        
        # 'views/ad_organizacion_views.xml',
        'views/ad_ou_views.xml',
        'views/ad_department_views.xml',
        'views/ad_users_views.xml',
        'views/menu.xml',
        
        'security/ad_security.xml',
        'security/ir.model.access.csv',

    ],

    'js': [
        #'static/src/js/toggle_widget.js',
        # 'static/src/js/disabled_copy.js',
    ],

    'css': [
        'static/src/css/uit_base.css',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}