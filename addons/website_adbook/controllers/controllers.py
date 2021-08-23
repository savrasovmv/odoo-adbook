# -*- coding: utf-8 -*-
# from odoo import http


# class WebsiteAdbook(http.Controller):
#     @http.route('/website_adbook/website_adbook/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_adbook/website_adbook/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_adbook.listing', {
#             'root': '/website_adbook/website_adbook',
#             'objects': http.request.env['website_adbook.website_adbook'].search([]),
#         })

#     @http.route('/website_adbook/website_adbook/objects/<model("website_adbook.website_adbook"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_adbook.object', {
#             'object': obj
#         })
