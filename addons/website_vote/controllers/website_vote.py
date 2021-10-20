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
        data = False
        file = ""
        if kw.get("file"):
            for c_file in request.httprequest.files.getlist("file"):
                data = c_file.read()
        if data:
            binary = base64.b64encode(data).decode("utf-8")
            mimetype = guess_mimetype(data)
            if mimetype.startswith("image/"):
                file = binary
            else:
                return werkzeug.utils.redirect("/vote/%s" % str(vote_id))

        vals = {
            "file_text": kw.get("file_text"),
            "users_id": http.request.env.user.id,
            "vote_vote_id": vote_id,
            "file": file,
            # "file_small": tools.image_resize_image_small(base64.b64encode(base64.b64encode(data))) if file else '',
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


    # Голосование
    @http.route(['/vote/voting/<int:vote_id>'], type='http', auth="user", website=True, sitemap=True)
    def vote_voting(self, vote_id=False):
        if not vote_id:
            return request.redirect("/vote")
        
        vote = request.env['vote.vote'].sudo().search([
            ('id', '=', vote_id)
        ], limit=1)

        participant = request.env['vote.vote_participant'].sudo().search([
            ('vote_vote_id', '=', vote.id),
        ], limit=1)



       
        return http.request.render(
            # 'website_vote.vote_image_views', 
            'website_vote.voting_page', 
            {
                'vote':vote,
                'participant': participant,
                'list_ids': vote.vote_vote_participant.ids
            })

    @http.route(['/vote/participant/<int:participant_id>'], type='json', auth="user", website=True, sitemap=True)
    def vote_get_participant_image(self, participant_id=False):
        print("+++++++++++++++++vote_get_participant_image")
        if not participant_id:
            return request.redirect("/vote")
        
       
        participant = request.env['vote.vote_participant'].sudo().search([
            ('id', '=', participant_id),
        ], limit=1)


        if not participant:
            return request.redirect("/vote")
       
        return {
            'participant_id': participant.id,
            'image_1920': participant.image_1920,
            'file_text': participant.file_text,
            'autor': participant.employee_id.name if participant.employee_id else participant.users_id.name,
            'title': participant.employee_id.job_title if participant.employee_id else '',
            'department': participant.employee_id.department_id.name if participant.employee_id.department_id else '',
            'description': participant.description,
        }

    @http.route(['/vote/json/voting/<int:vote_id>'], type='json', auth="user", website=True, sitemap=True)
    def vote_json_voting(self, vote_id=False):
        if not vote_id:
            return request.redirect("/vote")
        
       
        vote = request.env['vote.vote'].sudo().search([
            ('id', '=', vote_id),
        ], limit=1)


        if not vote:
            return request.redirect("/vote")

        participant = request.env['vote.vote_participant'].sudo().search([
            ('vote_vote_id', '=', vote_id),
        ], limit=1)

        if not participant:
            return request.redirect("/vote")
       
        return {
            'list_id': vote.vote_vote_participant.ids,
            'next_id': vote.vote_vote_participant.ids[1],
            'prev_id': vote.vote_vote_participant.ids[-1],
            'image_1920': participant.image_1920,
            'file_text': participant.file_text,
            'autor': participant.employee_id.name if participant.employee_id else participant.users_id.name,
            'title': participant.employee_id.job_title if participant.employee_id else '',
            'department': participant.employee_id.department_id.name if participant.employee_id.department_id else '',
            'description': participant.description,
        }