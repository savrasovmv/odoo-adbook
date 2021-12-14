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


MAX_POST_PAGE = 5
MAX_POST_COMMENT = 3



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


    @http.route(['/social/<int:social_id>',
                '/social/<int:social_id>/page/<int:page>',
                '/social/<int:social_id>/post/<int:post_id>',
                ], type='http', auth="user", website=True, sitemap=True)
    def social_social(self, social_id=None, page=1, post_id=None, search=None, is_post=False, **opt):
        """Страница Сообщества с постами
            is_post - признак что это страница поста
        
        """

        if not social_id:
            return request.render("website_social.404")

        Social = request.env['social.social']
        social = Social.search([
            ('id', '=', social_id)
        ], limit=1, order="create_date asc, id asc")

        post_list = []
        like_list = []
        comment_list = []
        page_count = 1

        if len(social)>0:
            offset = (page - 1) * MAX_POST_PAGE
            if social.social_post_count>0 and MAX_POST_PAGE>0:
                page_count = social.social_post_count//MAX_POST_PAGE
                if (social.social_post_count % MAX_POST_PAGE)>0:
                    page_count += 1 

            if post_id:
                # Если это страница поста
                post_list = request.env['social.post'].search([
                    ('social_id', '=', social_id),
                    ('id', '=', post_id),
                ], limit=1)
                max_comment = None
                page_count = 0
                is_post = True
            else:
                # Если это страница сообщества
                post_list = request.env['social.post'].search([
                    ('social_id', '=', social_id),
                ], limit=MAX_POST_PAGE, offset=offset)
                max_comment = MAX_POST_COMMENT

            likes = request.env['social.post_like'].search([
                ('social_post_id', 'in', post_list.ids),
                ('create_uid', '=', request.env.user.id),
            ])

            like_list = [s.social_post_id.id for s in likes]

            for post in post_list:
                com = request.env['social.comments'].search([
                    ('social_post_id', '=', post.id),
                ], limit=max_comment)

                if len(com)>0:
                    comment_list += com




            
        values = {
            'social': social,
            "post_list": post_list,
            "page": page,
            "page_count": page_count,
            "like_list": like_list,
            "comment_list": comment_list,
            "is_post": is_post,

            


        }

        values['social_url'] = QueryURL('', ['social', ], social=social, search=search)
        
        
        return request.render("website_social.social_index", values)



    @http.route(['/social/post/form/<int:social_id>/<int:post_id>',
                '/social/post/form/<int:social_id>'
                ], type='http', auth="user", website=True, sitemap=True)
    def social_post_form(self, social_id=None, post_id=None):
        """Страница Формы поста"""

        if not social_id:
            return request.render("website_social.404")

        Social = request.env['social.social']
        social = Social.search([
            ('id', '=', social_id)
        ], limit=1, order="create_date asc, id asc")

        
        if not social:
            return request.render("website_social.404")

        values = {
            'social': social,
            
        }
       
        return request.render("website_social.social_post_form", values)



    @http.route("/social/create/post/<int:social_id>", type="http", auth="user", website=True, csrf=True)
    def social_create_post(self, social_id=False, **kw):
        """Создания поста в сообществе, из данных формы"""

        if not social_id:
            return request.render("website_social.404")

        Social = request.env['social.social']
        social = Social.search([
            ('id', '=', social_id)
        ], limit=1, order="create_date asc, id asc")

        
        if not social:
            return request.render("website_social.404")

        

        vals = {
            "social_id": social_id,
            "name": kw.get("name"),
            "content": kw.get("content"),
            "partner_id": int(kw.get("partner_id")) if kw.get("partner_id") else False,
        }
        post = request.env["social.post"].create(vals)
        

  
        return werkzeug.utils.redirect("/social/%s" % str(social_id))


    
    @http.route("/social/post/like/<int:post_id>", type="json", auth="user", website=True, csrf=True)
    def social_post_like(self, post_id=False, **kw):
        """Лайк поста"""

        if not post_id:
            return {
                'result': 'error',
                'data': 'Не верный ID поста'
            }

        Post = request.env['social.post']
        post = Post.search([
            ('id', '=', int(post_id))
        ], limit=1, order="create_date asc, id asc")

        
        if not post:
            return {
                'result': 'error',
                'data': 'Не верный ID поста'
            }

                
        like = request.env["social.post_like"].create({'social_post_id': post.id })

        if like:
            return {
                'result': 'success',
            }

        return {
                'result': 'error',
                'data': 'Ошибка создания лайка'
            } 



    @http.route("/social/post/comment/create/<int:post_id>", type="json", auth="user", website=True, csrf=True)
    def social_post_comment_create(self, post_id=False, content=False, **kw):
        """Новый комментарий"""


        if not post_id or not content:
            return {
                'result': 'error',
                'data': 'Не верный ID поста или нет контента'
            }

        Post = request.env['social.post']
        post = Post.search([
            ('id', '=', int(post_id))
        ], limit=1, order="create_date asc, id asc")

        
        if not post:
            return {
                'result': 'error',
                'data': 'Не верный ID поста'
            }

        vals = {
            "social_post_id": post.id,
            "social_id": post.social_id.id,
            "content": content,

        }

        comment = request.env["social.comments"].create(vals)
        # comment = True

        if comment:
            return {
                'result': 'success',
            }

        return {
                'result': 'error',
                'data': 'Ошибка создания комментария'
            } 


    

    @http.route('/social/get_partner', type='http', auth="user", methods=['GET'], website=True, sitemap=False)
    def social_partner_read(self, query='', limit=25, **post):
        data = request.env['res.partner'].search_read(
            domain=[('name', '=ilike', (query or '') + "%")],
            fields=['id', 'name'],
            limit=int(limit),
        )
        return json.dumps(data)

        
        