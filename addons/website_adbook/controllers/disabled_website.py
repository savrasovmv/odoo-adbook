# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website

logger = logging.getLogger(__name__)

# class WebsiteDisabled(Website):
#     @http.route(type ='http', auth="none", website=True)
#     def index(self, **kw):
#         if not request.uid:
#             return http.local_redirect('/web/login', query=request.params, keep_hash=True)
# class WebsiteDisabled(Website):
#     @http.route(['/<string:name>'], type='http', auth="none", website=True)
#     def index(self, **kw):
#         # if not request.uid:
#         return http.local_redirect('/web/login', query=request.params, keep_hash=True)