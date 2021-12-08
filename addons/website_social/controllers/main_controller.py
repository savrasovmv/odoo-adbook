# -*- coding: utf-8 -*-
from odoo import http, api, models,tools
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.web.controllers.main import content_disposition, ensure_db
from odoo.addons.website.controllers.main import QueryURL

from odoo.tools.mimetypes import guess_mimetype
import werkzeug.utils
import base64
import json
from odoo.tools import html2plaintext
from datetime import datetime

class WebsiteSocial(http.Controller):

    @http.route(['/social/'], type='http', auth="user", website=True, sitemap=True)
    def social(self, social=None, page=1, search=None, **opt):
        """Возвращает сотрудников у которых ДР"""

        Social = request.env['social.social']
        socials = Social.search(request.website.website_domain(), order="create_date asc, id asc")

        # print("+++++++request.website.website_domain()", request.website.website_domain())
        # print("+++++++socials", socials)

        values = {
            'socials': socials,
            "search": search,
        }

        values['social_url'] = QueryURL('', ['social', ], social=social, search=search)
        
        return request.render("website_social.index", values)

        
        