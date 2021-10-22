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
    
    def _get_emploee(self, users_id):
        empl = request.env['hr.employee'].sudo().search([
                ('user_id', '=', users_id),
            ], limit=1)

        if len(empl)>0:
            return empl.id
        else:
            return False
    


    @http.route(['/vote/<int:vote_id>'], type='http', auth="user", website=True, sitemap=True)
    def vote_page(self, vote_id=False):
        """Информация по конкурсу"""
        if not vote_id:
            return request.redirect("/vote")
        
        vote = request.env['vote.vote'].sudo().search([
            ('id', '=', vote_id)
        ], limit=1)

        participant_item = request.env['vote.vote_participant_item'].sudo().search([
            ('vote_vote_id', '=', vote_id),
            ('users_id', '=', request.env.user.id)
        ])

        if vote.state == 'closed':

            winner_item = request.env['vote.vote_participant_item'].sudo().search([
                ('vote_vote_id', '=', vote_id),
            ],limit=vote.numder_winner_item, order='score desc')

            winner_participant = request.env['vote.vote_participant'].sudo().search([
                ('vote_vote_id', '=', vote_id),
            ],limit=vote.numder_winner_participant, order='score desc')

        else:
            winner_item = []
            winner_participant = []


       
        return http.request.render(
            'website_vote.vote_page', 
            {
                'vote':vote,
                'participant_item': participant_item,
                'winner_item': winner_item,
                'winner_participant': winner_participant,
            })


    @http.route(['/vote/reg/<int:vote_id>'], type='http', auth="user", website=True, sitemap=True)
    def vote_reg_page(self, vote_id=False):
        """Регистрация участника. Начальная страница"""

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


    @http.route("/vote/reg/file/<int:vote_id>", type="http",  auth="user", website=True, csrf=True)
    def vote_reg_file_page(self, vote_id=False, **kw):
        """Регистрация участника. Страница загрузки файла"""

        if not vote_id:
            return request.redirect("/vote")
        vote = request.env['vote.vote'].sudo().search([
            ('id', '=', vote_id)
        ], limit=1)
        if len(vote) == 0:
            return request.redirect("/vote")
        
        participant_item = request.env['vote.vote_participant_item'].sudo().search([
            ('users_id', '=', http.request.env.user.id),
            ('vote_vote_id', '=', vote_id),

        ])

        finish = True
        if len(participant_item)<vote.numder_files:
            finish = False
        
        if finish:
            return request.redirect("/vote/%s" % str(vote_id))
        
        return http.request.render(
            'website_vote.vote_reg_file_page', 
            {
                "vote": vote,
                "description": kw.get("description"),
                "participant_item": participant_item,
                "finish": finish,
            })


    @http.route("/vote/reg/add_item/<int:vote_id>", type="http", auth="user", website=True, csrf=True)
    def submit_vote(self, vote_id=False, **kw):
        """Регистрация участника.Загрузка файла, создание участника и файла в модели"""

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

        participant = request.env['vote.vote_participant'].sudo().search([
            ('users_id', '=', http.request.env.user.id),
            ('vote_vote_id', '=', vote_id),
        ], limit=1)

        if len(participant) == 0:
            vals = {
                "description": kw.get("description"),
                "users_id": http.request.env.user.id,
                "employee_id": self._get_emploee(http.request.env.user.id),
                "vote_vote_id": vote_id,
            }
            participant = request.env["vote.vote_participant"].sudo().create(vals)
        

        vals = {
            "users_id": http.request.env.user.id,
            "employee_id": self._get_emploee(http.request.env.user.id),
            "vote_vote_id": vote_id,
            "file_text": kw.get("file_text"),
            "file": file,
            "participant_id": participant.id
        }

        new_participant_item = request.env["vote.vote_participant_item"].sudo().create(vals)

        return werkzeug.utils.redirect("/vote/reg/file/%s" % str(vote_id))



    @http.route(['/vote'], type='http', auth="user", website=True, sitemap=True)
    def vote_home(self):
        """ Домашняя страница голосований"""
        
        vote_reg_list = request.env['vote.vote'].sudo().search([
            ('state', '=', 'reg')
        ], limit=3, order='reg_date_start asc')

        vote_vote_list = request.env['vote.vote'].sudo().search([
            ('state', '=', 'vote')
        ], limit=3, order='date_start asc')

        vote_closed_list = request.env['vote.vote'].sudo().search([
            ('state', '=', 'closed')
        ], limit=3, order='date_start asc')
        
        return http.request.render(
            'website_vote.vote_home', 
            {
                'vote_reg_list': vote_reg_list,
                'vote_vote_list': vote_vote_list,
                'vote_closed_list': vote_closed_list,
            })


    # Процесс Голосования
    @http.route(['/vote/voting/<int:vote_id>', '/vote/voting/<int:vote_id>/<int:participant_item_id>' ], type='http', auth="user", website=True, sitemap=True)
    def vote_voting(self, vote_id=False, participant_item_id=False):
        """Просмотр работ участников"""
        if not vote_id:
            return request.redirect("/vote")
        
        # vote = request.env['vote.vote'].sudo().search([
        #     ('id', '=', vote_id)
        # ], limit=1)
        if participant_item_id:
            participant_item = request.env['vote.vote_participant_item'].sudo().search([
                    ('vote_vote_id', '=', vote_id),
                    ('id', '=', participant_item_id),
                ], limit=1)
        else:
            participant_item = request.env['vote.vote_participant_item'].sudo().search([
                    ('vote_vote_id', '=', vote_id),
                ], limit=1)

       
        return http.request.render(
            # 'website_vote.vote_image_views', 
            'website_vote.voting_page', 
            {
                'vote_id':participant_item.vote_vote_id.id,
                'participant_item_id': participant_item.id,
                'participant_id': participant_item.participant_id.id,
                'vote_start': True if participant_item.vote_vote_id.state=='vote' else False,
                # 'list_ids': vote.vote_vote_participant.ids
            })

    @http.route(['/vote/participant_item/<int:participant_item_id>'], type='json', auth="user", website=True, sitemap=True)
    def vote_get_participant_image(self, participant_item_id=False):
        """ Возвращает данные работы участника в форму просмотра и голосования"""
        
        if not participant_item_id:
            return request.redirect("/vote")
        
       
        participant_item = request.env['vote.vote_participant_item'].sudo().search([
            ('id', '=', participant_item_id),
        ], limit=1)


        if not participant_item:
            return request.redirect("/vote")
       
        return {
            'participant_id': participant_item.id,
            'image_1920': participant_item.image_1920,
            'file_text': participant_item.file_text,
            'autor': participant_item.employee_id.name if participant_item.employee_id else participant_item.users_id.name,
            'title': participant_item.employee_id.job_title if participant_item.employee_id else '',
            'department': participant_item.employee_id.department_id.name if participant_item.employee_id.department_id else '',
            'description': participant_item.participant_id.description if participant_item.participant_id.description else '',
        }

    @http.route(['/vote/json/voting/<int:participant_item_id>'], type='json', auth="user", website=True, sitemap=True)
    def vote_json_voting(self, vote_id=False, participant_item_id=False):
        """ Возвращает начальные данные в форму просмотра и голосования"""

        if not participant_item_id:
            return request.redirect("/vote")

        participant_item = request.env['vote.vote_participant_item'].sudo().search([
            ('id', '=', participant_item_id),
        ], limit=1)

        if not participant_item:
            return request.redirect("/vote")

        voting = request.env['vote.vote_voting'].sudo().search([
            ('vote_vote_id', '=', participant_item.vote_vote_id.id),
            ('users_id', '=', http.request.env.user.id),
        ])
        list_voting = []
        for line in voting:
            list_voting.append(line.vote_vote_participant_item_id.id)
       
        return {
            'list_id': participant_item.vote_vote_id.vote_vote_participant_item.ids,
            'image_1920': participant_item.image_1920,
            'file_text': participant_item.file_text,
            'autor': participant_item.employee_id.name if participant_item.employee_id else participant_item.users_id.name,
            'title': participant_item.employee_id.job_title if participant_item.employee_id else '',
            'department': participant_item.employee_id.department_id.name if participant_item.employee_id.department_id else '',
            'description': participant_item.participant_id.description if participant_item.participant_id else '',
            'list_voting': list_voting,
            'max_voting': participant_item.vote_vote_id.numder_votes
        }


    @http.route(['/vote/voting_participant_item/<int:participant_item_id>'], type='json', auth="user", website=True, sitemap=True)
    def vote_json_voting_participant(self, participant_item_id=False):
        """ Принимает голос за работу кандидата"""
        if not participant_item_id:
            return {
                'result': 'error',
                'data': 'Не указан id участника'
            }
        
        participant_item = request.env['vote.vote_participant_item'].sudo().search([
            ('id', '=', participant_item_id),
        ], limit=1)

        if not participant_item:
            return {
                'result': 'error',
                'data': 'Нет такого участника'
            }

        voting = request.env['vote.vote_voting'].sudo().search([
            ('vote_vote_id', '=', participant_item.vote_vote_id.id),
            ('users_id', '=', http.request.env.user.id),
        ])

        # Проверка может ли голосовать
        if len(voting)>participant_item.vote_vote_id.numder_votes:
            return {
                'result': 'error',
                'data': 'Превышен лимит голосований'
            }
        
        vals = {
            "users_id": http.request.env.user.id,
            "employee_id": self._get_emploee(http.request.env.user.id),
            "vote_vote_id": participant_item.vote_vote_id.id,
            "vote_vote_participant_item_id": participant_item_id,
            "vote_vote_participant_id": participant_item.participant_id.id,
        }
        new_voting_line = request.env["vote.vote_voting"].sudo().create(vals)
       
        return {
            'result': 'success',
            'data': participant_item_id
        }