# -*- coding: utf-8 -*-
from odoo import http, api, models
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.web.controllers.main import content_disposition, ensure_db
import werkzeug.utils
import base64
import json

from captcha.image import ImageCaptcha
import random

def password_check(p):

    if len(p) < 10:
        return "Длина пароля не может быть меньше 10 символов"
    elif len(p) >25:
        return "Длина пароля не должна превышать 25 символов"

    elif len(p) >= 10 and len(p)<26:
        if p.isupper() or p.islower() or p.isdigit():
            return "Пароль соответствует требованиям"
        else:
            return "ok"

def random_captcha():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789'
    return ''.join(random.SystemRandom().choice(chars) for _ in range(6))




class Registration(http.Controller):

    def _check_user_profile_access(self, user_id):
        user_sudo = request.env['res.users'].sudo().browse(user_id)
        # User can access - no matter what - his own profile
        if user_sudo.id == request.env.user.id:
            return user_sudo
        return False
    
    

    @http.route(['/web/registration'], type='http', auth="public", website=True, sitemap=True, methods=['GET','POST'])
    def new_registration(self, **kw):

        error = ''
        ip_addr = request.httprequest.remote_addr
        

        # if request.httprequest.method == 'GET':
        #     request.env['reg.reg'].sudo()._set_recaptcha(ip_addr, captcha_text)
        
        if request.httprequest.method == 'POST':
            error = ''

            ip_addr = request.httprequest.remote_addr
            write_captcha_text = kw.get("captcha_text")
            name = kw.get("name")
            password = kw.get("password")
            confirm_password = kw.get("confirm_password")

            if password != confirm_password:
                error += "Пароли не совпадают \n"

            empl = request.env['hr.employee'].sudo().search([
                ('name', '=', name),
            ], limit=1)
            if len(empl) == 0:
                error += "Не найден сотрудник с указанным ФИО \n"
            else:
                email = None
                if empl.work_email:
                    email = empl.work_email
                elif empl.personal_email:
                    email = empl.personal_email
                if email == None:
                    error += "Не существует email, регистрация не возможна, обратитесь в службу поддержку \n"


            check_password = password_check(password)
            if check_password != 'ok':
                error += check_password + " \n"

            verify_code = request.env['reg.reg'].sudo()._verify_recaptcha(ip_addr, write_captcha_text)
            if not verify_code:
                error += "Не верно указан код с картинки \n"

            if error == '':
                return http.request.render(
                    'website_registration.registration_success', 
                    {
                        'name': empl.name,
                        'email': email,
                    },
                    )


        image = ImageCaptcha(width = 280, height = 90)
        captcha_text = random_captcha() 
        captcha = base64.b64encode(image.generate(captcha_text).getvalue())
        request.env['reg.reg'].sudo()._set_recaptcha(ip_addr, captcha_text)



        return http.request.render(
            'website_registration.registration_page', 
            {
                'captcha': captcha,
                'name': kw.get("name") or '',
                'password': kw.get("password") or '',
                'confirm_password': kw.get("confirm_password") or '',
                'error': error
            },
            )

    
    def check_user_param(self):

        error = ''

        print("++++++++++++", request.params)
        print("++++++++++++ remote_addr", request.httprequest.remote_addr)
        ip_addr = request.httprequest.remote_addr
        captcha_text = kw.get("captcha_text")
        name = kw.get("name")
        password = kw.get("password")

        empl = request.env['hr.employee'].sudo().search([
            ('name', '=', name),
        ], limit=1)
        if len(empl) == 0:
            error += "Не найден сотрудник с указанным ФИО /n"

        check_password = password_check(password)
        if check_password != 'ok':
            error += check_password + "/n"

        verify_code = request.env['reg.reg'].sudo()._verify_recaptcha(ip_addr, captcha_text)
        if not verify_code:
            error += "Не верно указан код с картинки /n"

        # request.params.append(('error', error))
        
        return http.local_redirect('/web/registration', query=request.params, keep_hash=True)



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

       
        
            
        

    