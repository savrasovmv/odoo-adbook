# -*- coding: utf-8 -*-
from odoo import http, api
from odoo.http import request
from odoo.addons.website.controllers.main import Website
import werkzeug.utils
import base64

class AdBook(http.Controller):
    
    

    @http.route(['/adbook/search'], type='http', auth='public', csrf=False, methods=['POST'])
    def search(self, search_text='', excel='', **kw):
        print("++++ route SEARCH", excel)

        #Экспорт контактов в эксель
        if excel == 'export':
            file_name = http.request.env['ad.users'].sudo()._export_adbook()
            f = open(file_name,"rb").read()
            response = request.make_response(f,
                                        headers=[('Content-Type', 'application/vnd.ms-excel'),
                                                ('Content-Disposition', 'attachment;filename=ETS Contacts.xlsx;')],
                                        )
            return response


        if search_text == '':
            return werkzeug.utils.redirect('/adbook')

        branch_list = http.request.env['ad.branch'].sudo().search([
                                ('active', '=', True),
                                ('is_view_adbook', '=', True),
                            ], order="sequence desc")
                
        employer_list = http.request.env['ad.users'].sudo().search([
                            ('search_text', 'ilike', search_text),
                            ('active', '=', True),
                            ('is_view_adbook', '=', True),
                            ('branch_id', 'in', branch_list.ids),
                        ], order="sequence desc, name asc")

        # employer_list = http.request.env['ad.users'].sudo().search([
        #                     '|','|',
        #                     ('name', 'ilike', search_text),
        #                     ('ip_phone', 'ilike', search_text),
        #                     ('email', 'ilike', search_text),
        #                     '&',
        #                     ('active', '=', True),
        #                     ('is_view_adbook', '=', True),
        #                     ('branch_id', 'in', branch_list.ids),
        #                 ], order="sequence desc, name asc")
        
            
        return http.request.render('website_adbook.index', {
            'search': True,
            'search_text': search_text,
            'current_branch_id': '',
            'branch_list':  branch_list,
            'employer_list':  employer_list,
        })


       
        
            
        

    @http.route(['/adbook','/adbook/<int:branch_id>'], auth='public')
    def index(self, branch_id=False, **kw):
        print("++++ route INDEX")
        branch_list = http.request.env['ad.branch'].sudo().search([
                                ('active', '=', True),
                                ('is_view_adbook', '=', True),
                            ], order="sequence desc")
        if not branch_list:
            return "Нет ниодного подразделения для отображения в справочнике. Установите хотя бы для одного объекта Подразделения AD 'Отображать в справочнике контктов'"

        if branch_id in branch_list.ids:
            branch_id = http.request.env['ad.branch'].sudo().browse(branch_id)
        
        if branch_list and not branch_id:
            branch_id = branch_list[0]

        if branch_id:
            department_list_id = http.request.env['ad.users'].sudo().read_group([ 
                                                        ('branch_id', '=', branch_id.id),
                                                        ('active', '=', True),
                                                        ('is_view_adbook', '=', True),
                                                    ], 
                                                        fields=['department_id'], 
                                                        groupby=['department_id']
                                                    )
            department_ids = []
            
            for data in department_list_id:
                d_id, obj = data['department_id']
                department_ids.append(d_id)
           
            department_list = http.request.env['ad.department'].sudo().search([ 
                                                        ('id', 'in', department_ids),
                                                        ('active', '=', True),
                                                        ('is_view_adbook', '=', True),
                                                    ], 
                                                        order="sequence desc"
                                                    )
            employer_list = http.request.env['ad.users'].sudo().search([
                                ('branch_id', '=', branch_id.id),
                                ('active', '=', True),
                                ('is_view_adbook', '=', True),
                            ], order="sequence desc")
        else:
            employer_list = []
            branch_list = []
            department_list = []
            branch_id = ''
            
        return http.request.render('website_adbook.index', {
            'search': False,
            'current_branch_id': branch_id,
            'branch_list':  branch_list,
            'department_list':  department_list,
            'employer_list':  employer_list,
        })




# class Website(Website):

#     @http.route(auth='public')
#     def index(self, **kw):
#         super(Website, self).index(**kw)
#         return "Hello, world"