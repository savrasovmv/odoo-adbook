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
        """Главная страница Сообществ"""

        Social = request.env['social.social']
        social_list = Social.search(request.website.website_domain(), order="create_date asc, id asc")

        # print("+++++++request.website.website_domain()", request.website.website_domain())
        print("+++++++socials image_128", social_list[0].image_128)

        values = {
            'social_list': social_list,
            "search": search,
        }

        values['social_url'] = QueryURL('', ['social', ], social=social, search=search)
        
        return request.render("website_social.index", values)


    @http.route(['/social/<int:social_id>'], type='http', auth="user", website=True, sitemap=True)
    def social_social(self, social_id=None, page=1, search=None, **opt):
        """Страница Сообщества с постами"""

        if not social_id:
            return request.render("website_social.404")

        Social = request.env['social.social']
        social = Social.search([
            ('id', '=', social_id)
        ], limit=1, order="create_date asc, id asc")

        post_list = []

        if len(social)>0:
            post_list = social.social_post_ids

        values = {
            'social': social,
            "post_list": post_list,
        }

        values['social_url'] = QueryURL('', ['social', ], social=social, search=search)

        import hashlib
        field = 'image_1920'
        size=None
        record = social
        sudo_record = social
        sha = hashlib.sha512(str(getattr(sudo_record, '__last_update')).encode('utf-8')).hexdigest()[:7]
        size = '' if size is None else '/%s' % size
        url =  '/web/image/%s/%s/%s%s?unique=%s' % (record._name, record.id, field, size, sha)
        print("+++++++ URL", url)
        
        return request.render("website_social.social_index", values)

        
        