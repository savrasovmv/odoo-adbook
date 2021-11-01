# -*- coding: utf-8 -*-
{
    'name': "Регистрация на портале",

    'summary': """
        Регистрация на портале""",

    'description': """
        Регистрация на портале.
        Для рботы модуля установить pip3 install captcha
    """,

    "author": "Savrasov Mikhail <savrasovmv@tmenergo.ru> ",
    "website": "https://github.com/savrasovmv/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'external_dependencies': {
        'python': [
             'captcha'
            ]},

    # any module necessary for this one to work correctly
    'depends': [
                'base',
                'ad_base',
                'website'
                ],

    # always loaded
    'data': [
        'views/website_registration_templates.xml',
        # 'views/res_menu.xml',
        # 'views/assets.xml',

    ],
    
    'js': [
        #'static/src/js/toggle_widget.js',
        # 'static/src/js/disabled_copy.js',
    ],

    'css': [
        # 'static/src/scss/adbook.scss',
    ],
}
