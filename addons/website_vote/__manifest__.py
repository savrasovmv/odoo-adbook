# -*- coding: utf-8 -*-
{
    'name': "Голосование wibsite",

    'summary': """
        Голосование wibsite""",

    'description': """
        Голосование wibsite
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
                'base',
                'website',
                'hr'
                ],

    # always loaded
    'data': [
        'views/assets.xml',
        # 'views/assets_voting.xml',
        'views/vote_views.xml',
        'views/vote_participant_views.xml',
        'views/vote_participant_item_views.xml',
        'views/vote_voiting_views.xml',
        'views/menu.xml',
        'views/website_vote_templates.xml',
        'views/website_vote_reg_page_templates.xml',
        'views/website_vote_voting_templates.xml',
        'security/security.xml',
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
