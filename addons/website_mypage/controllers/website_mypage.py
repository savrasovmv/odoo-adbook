# -*- coding: utf-8 -*-
from odoo import http, api, models
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.web.controllers.main import content_disposition, ensure_db
import werkzeug.utils
import base64
import json

class MyPage(http.Controller):

    def _check_user_profile_access(self, user_id):
        user_sudo = request.env['res.users'].sudo().browse(user_id)
        # User can access - no matter what - his own profile
        if user_sudo.id == request.env.user.id:
            return user_sudo
        return False
    
    

    @http.route(['/mypage'], type='http', auth="user", website=True, sitemap=True)
    def my_page(self):
        user = self._check_user_profile_access(request.env.user.id)
        print('+++++++', user[0].name)
        if not user:
            return request.redirect("/")

        employer = request.env['hr.employee'].sudo().search([
            ('user_id', '=', user.id)
        ])

        if len(employer) == 0:
            return request.redirect("/")
        
        vacation_doc = request.env['hr.vacation_doc'].sudo().search([
            ('employee_id', '=', employer.id)
        ])

        sick_leave_doc = request.env['hr.sick_leave_doc'].sudo().search([
            ('employee_id', '=', employer.id)
        ])

        trip_doc = request.env['hr.trip_doc'].sudo().search([
            ('employee_id', '=', employer.id)
        ])

        transfer_doc = request.env['hr.transfer_doc'].sudo().search([
            ('employee_id', '=', employer.id)
        ])

        print('===============', employer.image_1920)
        return http.request.render(
            'website_mypage.mypage_home', 
            {
                'user':user[0],
                'employer': employer,
                'photo': employer.image_1920,
                'vacation_doc': vacation_doc if len(vacation_doc)>0 else [],
                'sick_leave_doc': sick_leave_doc if len(sick_leave_doc)>0 else [],
                'trip_doc': trip_doc if len(trip_doc)>0 else [],
                'transfer_doc': transfer_doc if len(transfer_doc)>0 else [],

            
            })


#     @http.route(['/mypage/vacation'], type='http', auth="user", website=True)
#     def download_pdf(self):
        
#         pdf, _ = request.env['ir.actions.report']._get_report_from_name('website_mypage.report_vacation').sudo()._render_qweb_pdf([1])
#         pdf_http_headers = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)),
#                             ('Content-Disposition', content_disposition('%s - Invoice.pdf' % ('Заявление')))]
#         return request.make_response(pdf, headers=pdf_http_headers)




# class ParticularReport(models.AbstractModel):
#     _name = 'report.website_mypage.report_vacation'

#     def _get_report_values(self, docids, data=None):
#         # get the report action back as we will need its data
#         report = self.env['ir.actions.report']._get_report_from_name('module.report_name')
#         # get the records selected for this rendering of the report
#         # obj = self.env[report.model].browse(docids)
#         # return a custom rendering context
#         return {
#             'lines': docids
#         }

       
        
            
        

    