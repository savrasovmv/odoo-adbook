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

        participant = request.env['vote.vote_participant_item'].sudo().search([
            ('vote_vote_id', '=', vote_id),
            ('users_id', '=', request.env.user.id)
        ])

        if vote.state == 'closed':
            winner = request.env['vote.vote_participant_item'].sudo().search([
                ('vote_vote_id', '=', vote_id),
            ],limit=vote.numder_winner, order='score asc')
        else:
            winner = []


       
        return http.request.render(
            'website_vote.vote_page', 
            {
                'vote':vote,
                'participant': participant,
                'winner': winner
            })


    @http.route(['/vote/reg/<int:vote_id>'], type='http', auth="user", website=True, sitemap=True)
    def vote_reg_page(self, vote_id=False):
        """Регистрация участника"""

        if not vote_id:
            return request.redirect("/vote")

        user = request.env.user

        vote = request.env['vote.vote'].sudo().search([
            ('id', '=', vote_id)
        ], limit=1)

        if len(vote) == 0:
            return request.redirect("/vote")
       
        return http.request.render(
            'website_vote.vote_reg_page', 
            {
                'vote': vote,
                'user': user
            })


    @http.route("/vote/reg/file/<int:vote_id>", type="http", auth="user", website=True, csrf=True)
    def submit_vote(self, vote_id=False, **kw):
        
        return http.request.render(
            'website_vote.vote_reg_file_page', 
            {
                "description": kw.get("description"),
                "users_id": http.request.env.user.id,
                "vote_vote_id": vote_id,
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
            "description": kw.get("description"),
            "file_text": kw.get("file_text"),
            "users_id": http.request.env.user.id,
            "vote_vote_id": vote_id,
            "file": file,
            # "file_small": tools.image_resize_image_small(base64.b64encode(base64.b64encode(data))) if file else '',
        }
        new_vote_line = request.env["vote.vote_participant"].sudo().create(vals)
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


        
        return http.request.render(
            'website_vote.vote_home', 
            {
                'reg_list':reg_list,
                'vote_list': vote_list_search,
            })


    # Голосование
    @http.route(['/vote/voting/<int:vote_id>', '/vote/voting/<int:vote_id>/<int:participant_id>' ], type='http', auth="user", website=True, sitemap=True)
    def vote_voting(self, vote_id=False, participant_id=False):
        if not vote_id:
            return request.redirect("/vote")
        
        # vote = request.env['vote.vote'].sudo().search([
        #     ('id', '=', vote_id)
        # ], limit=1)
        if participant_id:
            participant = request.env['vote.vote_participant'].sudo().search([
                    ('vote_vote_id', '=', vote_id),
                    ('id', '=', participant_id),
                ], limit=1)
        else:
            participant = request.env['vote.vote_participant'].sudo().search([
                    ('vote_vote_id', '=', vote_id),
                ], limit=1)

       
        return http.request.render(
            # 'website_vote.vote_image_views', 
            'website_vote.voting_page', 
            {
                'vote_id':participant.vote_vote_id.id,
                'participant_id': participant.id,
                'vote_start': True if participant.vote_vote_id.state=='vote' else False,
                # 'list_ids': vote.vote_vote_participant.ids
            })

    @http.route(['/vote/participant/<int:participant_id>'], type='json', auth="user", website=True, sitemap=True)
    def vote_get_participant_image(self, participant_id=False):
        # import time
        # time.sleep(5) #задержка в течение 5 секунд
        # print("+++++++++++++++++vote_get_participant_image")
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
            'description': participant.description if participant.description else '',
        }

    @http.route(['/vote/json/voting/<int:participant_id>'], type='json', auth="user", website=True, sitemap=True)
    def vote_json_voting(self, vote_id=False, participant_id=False):
        """ Возвращает начальные данные в форму голосования"""
        # if not vote_id:
        #     return request.redirect("/vote")
       
        # vote = request.env['vote.vote'].sudo().search([
        #     ('id', '=', vote_id),
        # ], limit=1)


        # if not vote:
        #     return request.redirect("/vote")
        if not participant_id:
            return request.redirect("/vote")

        participant = request.env['vote.vote_participant'].sudo().search([
            ('id', '=', participant_id),
        ], limit=1)

        if not participant:
            return request.redirect("/vote")


        voting = request.env['vote.vote_voting'].sudo().search([
            ('vote_vote_id', '=', participant.vote_vote_id.id),
            ('users_id', '=', http.request.env.user.id),
        ])
        list_voting = []
        for line in voting:
            list_voting.append(line.vote_vote_participant_id.id)
       
        return {
            'list_id': participant.vote_vote_id.vote_vote_participant.ids,
            # 'participant_id': participant.id,
            # 'next_id': vote.vote_vote_participant.ids[1],
            # 'prev_id': vote.vote_vote_participant.ids[-1],
            'image_1920': participant.image_1920,
            'file_text': participant.file_text,
            'autor': participant.employee_id.name if participant.employee_id else participant.users_id.name,
            'title': participant.employee_id.job_title if participant.employee_id else '',
            'department': participant.employee_id.department_id.name if participant.employee_id.department_id else '',
            'description': participant.description if participant.description else '',
            'list_voting': list_voting,
            'max_voting': participant.vote_vote_id.numder_votes
        }


    @http.route(['/vote/voting_participant/<int:participant_id>'], type='json', auth="user", website=True, sitemap=True)
    def vote_json_voting_participant(self, participant_id=False):
        """ Принимает голос за кандидата"""
        if not participant_id:
            return {
                'result': 'error',
                'data': 'Не указан id участника'
            }
        
        participant = request.env['vote.vote_participant'].sudo().search([
            ('id', '=', participant_id),
        ], limit=1)

        if not participant:
            return {
                'result': 'error',
                'data': 'Нет такого участника'
            }

        voting = request.env['vote.vote_voting'].sudo().search([
            ('vote_vote_id', '=', participant.vote_vote_id.id),
            ('users_id', '=', http.request.env.user.id),
        ])

        # Проверка может ли голосовать
        if len(voting)>participant.vote_vote_id.numder_votes:
            return {
                'result': 'error',
                'data': 'Превышен лимит голосований'
            }
        
        vals = {
            "users_id": http.request.env.user.id,
            "vote_vote_id": participant.vote_vote_id.id,
            "vote_vote_participant_id": participant_id,
        }
        new_voting_line = request.env["vote.vote_voting"].sudo().create(vals)
       
        return {
            'result': 'success',
            'data': participant_id
        }