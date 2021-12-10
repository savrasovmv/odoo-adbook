# -*- coding: utf-8 -*-
{
    'name': "Сообщества wibsite",

    'summary': """
        Сообщества wibsite""",

    'description': """
        Сообщества wibsite
    """,

    "author": "Savrasov Mikhail <savrasovmv@tmenergo.ru> ",
    "website": "https://github.com/savrasovmv/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website/Website',
    'version': '0.1',
    'external_dependencies': {
        'python': [
             
            ]},

    # any module necessary for this one to work correctly
    'depends': [
                'base',
                'base_automation',
                'website',
                ],

    # always loaded
    'data': [
        'views/social_social_views.xml',
        'views/website_social.xml',
        'views/website_social_social.xml',
        'views/website_social_post_form.xml',
        'views/social_post_mail_templates.xml',
        'views/menu.xml',
        'views/assets.xml',
        'security/ir.model.access.csv',

        'data/base_automation.xml'

    ],
    
    'js': [
        #'static/src/js/toggle_widget.js',
        # 'static/src/js/disabled_copy.js',
    ],

    'css': [
        # 'static/src/scss/adbook.scss',
    ],
}
