# -*- coding: utf-8 -*-
from odoo import http, api, models
from odoo.http import request
from odoo.addons.website.controllers.main import Website
from odoo.addons.web.controllers.main import content_disposition, ensure_db
import werkzeug.utils
import base64
import json
import logging
_logger = logging.getLogger(__name__)

from captcha.image import ImageCaptcha
import random

def password_check(p):
    """Проверка пароля на сложность"""
    if len(p) < 10:
        return "Длина пароля не может быть меньше 10 символов"
    elif len(p) >25:
        return "Длина пароля не должна превышать 25 символов"

    elif len(p) >= 10 and len(p)<26:
        if p.isupper() or p.islower() or p.isdigit():
            return "Пароль не соответствует требованиям"
        else:
            return "ok"

def random_captcha():
    """Генерация текста для капчи"""
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789'
    return ''.join(random.SystemRandom().choice(chars) for _ in range(6))

def get_email_cipher(email):
    """Зашифровать email: use***@domain.com"""
    e = email[:3] + "***@" + email.split("@")[-1]
    return e or email




class Registration(http.Controller):

    def _check_user_profile_access(self, user_id):
        user_sudo = request.env['res.users'].sudo().browse(user_id)
        # User can access - no matter what - his own profile
        if user_sudo.id == request.env.user.id:
            return user_sudo
        return False
    
    # @http.route(['/web/registrationtest'], type='http', auth="public", website=True, sitemap=True, methods=['GET'])
    # def test_registration(self, **kw):

    #     error = ''
    #     empl = request.env['hr.employee'].sudo().search([
    #         ('name', '=', 'Саврасов Михаил Владимирович'),
    #     ], limit=1)
    #     if len(empl) == 0:
    #         error += "Не найден сотрудник с указанным ФИО \n"
    #     else:
    #         email = None
    #         if empl.work_email:
    #             email = empl.work_email
    #         elif empl.personal_email:
    #             email = empl.personal_email
    #         if email == None:
    #             error += "Не существует email, регистрация не возможна, обратитесь в службу поддержку \n"
    #         else:
    #             email = get_email_cipher(email)
            
    #     if error=='':
    #         empl.reg_create_user()

    #         return http.request.render(
    #             'website_registration.registration_success', 
    #             {
    #                 'name': empl.name,
    #                 'email': email,
    #             },
    #             )
    #     else:
    #         return http.request.render(
    #             'website_registration.registration_success', 
    #             {
    #                 'name': empl.name,
    #                 'email': "Ошибка создания пользователя с " + email,
    #             },
    #             )


    @http.route(['/web/registration/step1'], type='http', auth="public", website=True, sitemap=True, methods=['GET','POST'])
    def new_registration_step1(self, **kw):

        _logger.debug("new_registration_step1")
        error = ''
        email_cipher = ''

        ip_addr = request.httprequest.remote_addr
        
        if request.httprequest.method == 'POST':
            error = ''
            # request.httprequest.environ['HTTP_X_REAL_IP']
            ip_addr = request.httprequest.remote_addr
            write_captcha_text = kw.get("captcha_text") or ''
            name = kw.get("name") or ''
            token = kw.get("token") or ''
            _logger.debug("Регистрация, шаг 1 ФИО = %s" % (name))

            if len(token)==0 or len(write_captcha_text)==0 or len(name)==0:
                _logger.debug("Отсутствует обязательное поле token = %s write_captcha_text = %s name = %s" % (token, write_captcha_text, name))

                return http.local_redirect('/web/registration/step1')
            
            # if len(str(write_captcha_text))!=6 or len(name)==0: 
            #     return http.local_redirect('/web/registration/step1')


            empl = request.env['hr.employee'].sudo().search([
                ('name', 'ilike', name),
                ('is_fired', '=', False),
            ], limit=1)

            if len(empl) == 0 or empl.name.lower()!=name.lower():
                error += "Не найден сотрудник с указанным ФИО \n"
            else:
                if empl.user_id:
                    error += "Пользователь с таким ФИО уже зарегистрирован. Если вы забыли пароль, выполните его сброс на странице авторизации"
                email = empl.get_registration_email()
                
                if not email:
                    error += "Не существует email, регистрация не возможна, обратитесь в службу поддержку \n"
                else:
                    email_cipher = get_email_cipher(email)

            verify_code = request.env['reg.reg'].sudo()._verify_recaptcha(ip_addr, write_captcha_text, token)
            if not verify_code:
                error += "Не верно указан код с картинки \n"

            if error == '':
                return http.request.render(
                    'website_registration.registration_page_step2', 
                    {
                        'name': empl.name,
                        'email_cipher': email_cipher,
                        'token': token,
                        'write_captcha_text': write_captcha_text,
                    },
                    )

        _logger.debug("error = %s" % (error))

        image = ImageCaptcha(width = 280, height = 90)
        captcha_text = random_captcha() 
        captcha = base64.b64encode(image.generate(captcha_text).getvalue())
        token = request.env['reg.reg'].sudo()._set_recaptcha(ip_addr, captcha_text)

        return http.request.render(
            'website_registration.registration_page_step1', 
            {
                'captcha': captcha,
                'name': kw.get("name") or '',
                'token': token or '',
                'password': kw.get("password") or '',
                'confirm_password': kw.get("confirm_password") or '',
                'error': error
            },
            )


    @http.route(['/web/registration/step2'], type='http', auth="public", website=True, sitemap=True, methods=['POST'])
    def new_registration_step2(self, **kw):
        _logger.debug("new_registration_step1")

        
        error = ''
        ip_addr = request.httprequest.remote_addr
        
        if request.httprequest.method == 'POST':
            error = ''
            email_cipher = ''
            # request.httprequest.environ['HTTP_X_REAL_IP']
            ip_addr = request.httprequest.remote_addr
            write_captcha_text = kw.get("write_captcha_text") or ''
            name = kw.get("name") or ''
            token = kw.get("token") or ''
            write_email = kw.get("email") or ''

            _logger.debug("Регистрация, шаг 2 ФИО = %s" % (name))


            if len(token)==0 or len(write_captcha_text)==0 or len(name)==0 or len(write_email)==0:
                _logger.debug("Отсутствует обязательное поле token = %s write_captcha_text = %s name = %s write_email= %s" % (token, write_captcha_text, name, write_email))

                return http.local_redirect('/web/registration/step1')
            
            empl = request.env['hr.employee'].sudo().search([
                ('name', '=', name),
            ], limit=1)

            if len(empl) == 0:
                error += "Не найден сотрудник с указанным ФИО \n"
            else:
                email = empl.get_registration_email()
                if not email:
                    error += "Не существует email, регистрация не возможна, обратитесь в службу поддержку \n"
                elif write_email.lower()!=email.lower():
                    _logger.debug("Не верно указан email write_email= %s email=%s" % (write_email, email))

                    error += "Не верно указан email \n"
                    email_cipher = get_email_cipher(email)


            verify_code = request.env['reg.reg'].sudo()._verify_recaptcha(ip_addr, write_captcha_text, token)
            if not verify_code:
                error += "Не верно указан код с картинки \n"

            if error == '':
                try:
                    empl.reg_create_user()
                    return http.request.render(
                        'website_registration.registration_success', 
                        {
                            'name': empl.name,
                            'email': email,
                        },
                        )
                except Exception as e:
                    _logger.warning("Ошибка при создании пользователя %s  %s" % ( email, str(e)))

                

        _logger.debug("error = %s" % (error))

        return http.request.render(
                    'website_registration.registration_page_step2', 
                    {
                        'name': empl.name,
                        'email_cipher': email_cipher,
                        'token': token,
                        'write_captcha_text': write_captcha_text,
                        'error': error,
                        
                    },
                    )

    # @http.route(['/web/registration'], type='http', auth="public", website=True, sitemap=True, methods=['GET','POST'])
    # def new_registration1(self, **kw):

    #     error = ''
    #     ip_addr = request.httprequest.remote_addr
        
    #     if request.httprequest.method == 'POST':
    #         error = ''
    #         # request.httprequest.environ['HTTP_X_REAL_IP']
    #         ip_addr = request.httprequest.remote_addr
    #         write_captcha_text = kw.get("captcha_text")
    #         name = kw.get("name")
    #         password = kw.get("password")
    #         confirm_password = kw.get("confirm_password")

    #         if password != confirm_password:
    #             error += "Пароли не совпадают \n"

    #         empl = request.env['hr.employee'].sudo().search([
    #             ('name', '=', name),
    #         ], limit=1)
    #         if len(empl) == 0:
    #             error += "Не найден сотрудник с указанным ФИО \n"
    #         else:
    #             email = None
    #             if empl.work_email:
    #                 email = empl.work_email
    #             elif empl.personal_email:
    #                 email = empl.personal_email
    #             if email == None:
    #                 error += "Не существует email, регистрация не возможна, обратитесь в службу поддержку \n"
    #             else:
    #                 email = email_cipher(email)


    #         check_password = password_check(password)
    #         if check_password != 'ok':
    #             error += check_password + " \n"

    #         verify_code = request.env['reg.reg'].sudo()._verify_recaptcha(ip_addr, write_captcha_text)
    #         if not verify_code:
    #             error += "Не верно указан код с картинки \n"

    #         if error == '':
    #             return http.request.render(
    #                 'website_registration.registration_success', 
    #                 {
    #                     'name': empl.name,
    #                     'email': email,
    #                 },
    #                 )


    #     image = ImageCaptcha(width = 280, height = 90)
    #     captcha_text = random_captcha() 
    #     captcha = base64.b64encode(image.generate(captcha_text).getvalue())
    #     request.env['reg.reg'].sudo()._set_recaptcha(ip_addr, captcha_text)



    #     return http.request.render(
    #         'website_registration.registration_page', 
    #         {
    #             'captcha': captcha,
    #             'name': kw.get("name") or '',
    #             'password': kw.get("password") or '',
    #             'confirm_password': kw.get("confirm_password") or '',
    #             'error': error
    #         },
    #         )

    
    # def check_user_param(self):

    #     error = ''

    #     print("++++++++++++", request.params)
    #     print("++++++++++++ remote_addr", request.httprequest.remote_addr)
    #     ip_addr = request.httprequest.remote_addr
    #     captcha_text = kw.get("captcha_text")
    #     name = kw.get("name")
    #     password = kw.get("password")

    #     empl = request.env['hr.employee'].sudo().search([
    #         ('name', '=', name),
    #     ], limit=1)
    #     if len(empl) == 0:
    #         error += "Не найден сотрудник с указанным ФИО /n"

    #     check_password = password_check(password)
    #     if check_password != 'ok':
    #         error += check_password + "/n"

    #     verify_code = request.env['reg.reg'].sudo()._verify_recaptcha(ip_addr, captcha_text)
    #     if not verify_code:
    #         error += "Не верно указан код с картинки /n"

    #     # request.params.append(('error', error))
        
    #     return http.local_redirect('/web/registration', query=request.params, keep_hash=True)


    @http.route(['/web/registration/conditions'], type='http', auth="public", website=True, sitemap=True)
    def registration_conditions(self):

        cond = request.env['reg.conditions'].sudo().get_conditions()

        return http.request.render(
            'website_registration.registration_conditions', 
            {
                'data': cond,
            },
            )
    
    @http.route(['/web/registration/confidentiality'], type='http', auth="public", website=True, sitemap=True)
    def registration_confidentiality(self):

        cond = request.env['reg.conditions'].sudo().get_conditions()
        return http.request.render(
            'website_registration.registration_confidentiality', 
            {
                'data': cond,
            },
            )



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

       
        
            
        

    