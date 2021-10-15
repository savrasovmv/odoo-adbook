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

        participant = request.env['vote.vote_participant'].sudo().search([
            ('vote_vote_id', '=', vote_id),
            ('users_id', '=', request.env.user.id)
        ], limit=1)

       
        return http.request.render(
            'website_vote.vote_page', 
            {
                'vote':vote,
                'participant': participant
            })


    @http.route(['/vote/reg/<int:vote_id>'], type='http', auth="user", website=True, sitemap=True)
    def vote_reg_page(self, vote_id=False):
        if not vote_id:
            return request.redirect("/vote")
        # user = self._check_user_profile_access(request.env.user.id)
        user = request.env.user
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
            'website_vote.vote_reg_page', 
            {
                'vote':vote,
                'user': user
            })


    @http.route("/vote/submitted/<int:vote_id>", type="http", auth="user", website=True, csrf=True)
    def submit_vote(self, vote_id=False, **kw):
        print('++++++++++++', kw)
        data = False
        if kw.get("file"):
            for c_file in request.httprequest.files.getlist("file"):
                print('++++++++++++', c_file)

                data = c_file.read()
                file = c_file
            
        vals = {
            "file_text": kw.get("file_text"),
            "users_id": http.request.env.user.id,
            "vote_vote_id": vote_id,
            "file": base64.b64encode(data).decode("utf-8") if file else '',
            # "file": base64.b64encode(file) if file else '',
        }
        new_vote_line = request.env["vote.vote_participant"].sudo().create(vals)
        # new_ticket.message_subscribe(partner_ids=request.env.user.partner_id.ids)
        # if kw.get("attachment"):
        #     for c_file in request.httprequest.files.getlist("attachment"):
        #         data = c_file.read()
        #         if c_file.filename:
        #             request.env["ir.attachment"].sudo().create(
        #                 {
        #                     "name": c_file.filename,
        #                     "datas": base64.b64encode(data),
        #                     "res_model": "vote.vote_line",
        #                     "res_id": new_vote_line.id,
        #                 }
        #             )
        return werkzeug.utils.redirect("/vote/%s" % str(vote_id))



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