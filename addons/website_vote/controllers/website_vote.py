# -*- coding: utf-8 -*-
from odoo import http, api, models
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.web.controllers.main import content_disposition, ensure_db
import werkzeug.utils
import base64
import json

class WebsiteVote(http.Controller):

    def _check_user_profile_access(self, user_id):
        user_sudo = request.env['res.users'].sudo().browse(user_id)
        # User can access - no matter what - his own profile
        if user_sudo.id == request.env.user.id:
            return user_sudo
        return False
    
    

    @http.route(['/vote'], type='http', auth="user", website=True, sitemap=True)
    def my_page(self):
        # user = self._check_user_profile_access(request.env.user.id)
        # print('+++++++', user[0].name)
        # if not user:
        #     return request.redirect("/")

        # employer = request.env['hr.employee'].sudo().search([
        #     ('user_id', '=', user.id)
        # ])

        # if len(employer) == 0:
        #     return request.redirect("/")
        
        open_list = request.env['vote.vote'].search([
            ('state', '=', 'open')
        ])

        closed_list = request.env['vote.vote'].search([
            ('state', '=', 'closed')
        ])
        
        return http.request.render(
            'website_vote.vote_home', 
            {
                'open_list':open_list,
                'closed_list': closed_list,
            })
