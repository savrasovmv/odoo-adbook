# -*- coding: utf-8 -*-
{
    'name': "Дополнительные блоки для website",

    'summary': """
        Snippets website""",

    'description': """
        Добавляет блоки для вебсайта:
        birthday
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
             
            ]},

    # any module necessary for this one to work correctly
    'depends': [
                'website',
                'hr'
                ],

    # always loaded
    'data': [
        'views/assets.xml',
        # 'views/assets_voting.xml',
        'views/s_birthday.xml',
        'views/snippets.xml',

    ],
    
    'js': [
        #'static/src/js/toggle_widget.js',
        # 'static/src/js/disabled_copy.js',
    ],

    'css': [
        # 'static/src/scss/adbook.scss',
    ],
    'qweb': [
        'static/src/xml/birthday_list.xml',
    ],
}
