# -*- coding: utf-8 -*-
{
    'name': "Справочник контактов adbook wibsite",

    'summary': """
        Справочник контактов adbook wibsite""",

    'description': """
        Справочник контактов adbook wibsite
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
            'openpyxl', 
            ]},

    # any module necessary for this one to work correctly
    'depends': [
                'base',
                'ad_base',
                'website'
                ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates_head.xml',
        'views/templates_list_search.xml',
        'views/templates_list.xml',
        'views/templates.xml',
    ],
    
    'js': [
        #'static/src/js/toggle_widget.js',
        # 'static/src/js/disabled_copy.js',
    ],

    'css': [
        'static/src/css/adbook.css',
    ],
}
