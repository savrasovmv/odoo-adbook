# -*- coding: utf-8 -*-
from odoo import http, api, models
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.web.controllers.main import content_disposition, ensure_db
import werkzeug.utils
import base64
import json
from odoo.tools import html2plaintext

class WebsiteVote(http.Controller):

    def _check_user_profile_access(self, user_id):
        user_sudo = request.env['res.users'].sudo().browse(user_id)
        # User can access - no matter what - his own profile
        if user_sudo.id == request.env.user.id:
            return user_sudo
        return False
    
    

    @http.route(['/vote'], type='http', auth="user", website=True, sitemap=True)
    def vote_home(self):
        # user = self._check_user_profile_access(request.env.user.id)
        # print('+++++++', user[0].name)
        # if not user:
        #     return request.redirect("/")

        # employer = request.env['hr.employee'].sudo().search([
        #     ('user_id', '=', user.id)
        # ])

        # if len(employer) == 0:
        #     return request.redirect("/")
        
        reg_list_search = request.env['vote.vote'].sudo().search([
            ('state', '=', 'reg')
        ], limit=3, order='reg_date_start asc')

        reg_list = []
        for line in reg_list_search:
            reg_list.append(
                {
                    'id': line.id,
                    'name': line.name,
                    'description':html2plaintext(line.description).replace('\n', ' ')[:200] + '...',
                    'background_image': line.background_image
                }
            )
        
        vote_list_search = request.env['vote.vote'].sudo().search([
            ('state', '=', 'vote')
        ], limit=3, order='date_start asc')
        
        print('+++++++++', reg_list)
        return http.request.render(
            'website_vote.vote_home', 
            {
                'reg_list':reg_list,
                'vote_list': vote_list_search,
            })


    @http.route(['/vote/<int:vote_id>'], type='http', auth="user", website=True, sitemap=True)
    def vote_page(self, vote_id=False):
        if not vote_id:
            return request.redirect("/vote")
        # user = self._check_user_profile_access(request.env.user.id)
        # print('+++++++', user[0].name)
        # if not user:
        #     return request.redirect("/")

        # employer = request.env['hr.employee'].sudo().search([
        #     ('user_id', '=', user.id)
        # ])

        # if len(employer) == 0:
        #     return request.redirect("/")
        
        vote = request.env['vote.vote'].sudo().search([
            ('id', '=', vote_id)
        ], limit=1)

       
        return http.request.render(
            'website_vote.vote_page', 
            {
                'vote':vote,
            })
