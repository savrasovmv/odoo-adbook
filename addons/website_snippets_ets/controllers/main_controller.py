# -*- coding: utf-8 -*-
from odoo import http, api, models,tools
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.web.controllers.main import content_disposition, ensure_db
from odoo.tools.mimetypes import guess_mimetype
import werkzeug.utils
import base64
import json
from odoo.tools import html2plaintext
from datetime import datetime

class WebsiteVideoWidget(http.Controller):

    @http.route(['/web/birthday/'], type='json', auth="user", website=True, sitemap=True)
    def get_birthday(self):
        """Возвращает сотрудников у которых ДР"""
        date = datetime.today()

        employers = http.request.env['hr.employee'].sudo().search([
                            ('is_fired', '=', False),
                            ('birthday_day', '=', date.day),
                            ('birthday_month', '=', date.month),
                            ('active', '=', True),
                        ], order="name")

        employer_list = []
        for line in employers:
            employer_list.append({
                'name': line.name,
                'job_title': line.job_title,
                'photo': line.image_128,
            })


        return  {
            'employer_list':  employer_list,
            # 'employer_list':  json.dumps(employer_list) if employer_list else False ,
        }
        
        