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
                'website',
                'auth_password_policy',
                'auth_password_policy_signup',
                'auth_password_policy_portal',
                'auth_signup',

                ],

    # always loaded
    'data': [
        # 'views/mail_auth_signup_templates.xml',
        'views/res_config_settings_views.xml',
        'views/registration_allowed_ip_views.xml',
        'views/registration_conditions_views.xml',
        'views/website_registration_templates.xml',
        'views/website_registration_step1_templates.xml',
        'views/website_registration_step2_templates.xml',
        'views/res_menu.xml',
        'views/assets.xml',
        'security/ir.model.access.csv',

    ],
    
    'js': [
        #'static/src/js/toggle_widget.js',
        # 'static/src/js/disabled_copy.js',
    ],

    'css': [
        # 'static/src/scss/adbook.scss',
    ],
}
