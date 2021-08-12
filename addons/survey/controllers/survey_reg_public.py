# -*- coding: utf-8 -*-

import datetime
import json
import werkzeug

from dateutil.relativedelta import relativedelta
from werkzeug.exceptions import NotFound

from odoo import fields, http
from odoo.http import request
from odoo.tools import is_html_empty

from email_validator import EmailSyntaxError, EmailUndeliverableError, validate_email


class RegPublicUser(http.Controller):
    def _fetch_from_token(self, survey_token):
        """ Check that given survey_token matches a survey 'access_token'.
        Unlike the regular survey controller, user trying to access the survey must have full access rights! """
        return request.env['survey.survey'].sudo().search([('access_token', '=', survey_token)])

    def _fetch_from_session_code(self, session_code):
        """ Matches a survey against a passed session_code.
        We force the session_state to be reachable (ready / in_progress) to avoid people
        using this route to access other (private) surveys.
        We limit to sessions opened within the last 7 days to avoid potential abuses. """
        if session_code:
            matching_survey = request.env['survey.survey'].sudo().search([
                ('state', '=', 'open'),
                ('session_state', 'in', ['ready', 'in_progress']),
                ('session_start_time', '>', fields.Datetime.now() - relativedelta(days=7)),
                ('session_code', '=', session_code),
            ], limit=1)
            if matching_survey:
                return matching_survey

        return False

    # ------------------------------------------------------------
    # SURVEY SESSION MANAGEMENT
    # ------------------------------------------------------------

    @http.route('/survey/reg/<string:survey_token>', type='http', auth='public', website=True, methods=['POST'])
    def survey_reg(self, survey_token, fio=False, email=False, **kw):

        if not fio or not email:
            return request.render("survey.survey_reg_public_verify", {'email': "", "error": True, "text_error": "Не указано ФИО или e-mail"})
        try:
            validate_email(email)
        except Exception as error:
            return request.render("survey.survey_reg_public_verify", {'email': email, "error": True, "text_error": str(error)})    
        

        partner_info = {
            'name': fio,
            'email': email,
        }

        sudo_partner = request.env["res.partner"].sudo()
        partner = sudo_partner.search([('email', '=', email)], limit=1)
        partner_id = False
        if len(partner) == 0:
            partner = sudo_partner.create(partner_info)


        survey = self._fetch_from_token(survey_token)
        # MAIL_CATCHALL_DOMAIN = request.env['ir.config_parameter'].sudo().get_param('mail.catchall.domain')

        email_from = request.env['ir.config_parameter'].sudo().get_param('survey_reg_email')

        if not email_from:
            return request.render("survey.survey_reg_public_error", {})

        template = request.env.ref('survey.mail_template_public_user_input_invite', raise_if_not_found=False)

        sudo_invite = request.env["survey.invite"].sudo().create({
                                        'partner_ids': [partner.id,], 
                                        'email_from': email_from, 
                                        'survey_id': survey.id,
                                        'template_id': template.id,
                                        #'author_id': 45,
                                        })
        # print("++++sudo_invite", sudo_invite)
        #sudo_invite[0]._compute_subject()
        sudo_invite.sudo().action_invite()
        
        return request.render("survey.survey_reg_public_verify", {'email': email, "error": False})
        #return request.redirect('/survey/start/%s?email=%s&partner_id=%s' % (survey_token, email, partner[0].id))
        #return request.render("survey.survey_confirm_registration", {'survey_token': survey_token, 'name': fio, 'email': email, 'partner': partner})
        #return request.redirect('/survey/start/%s?email=%s' % (survey_token, email))
    


    # ------------------------------------------------------------
    # QUICK ACCESS SURVEY ROUTES
    # ------------------------------------------------------------

    # @http.route('/survey/reg/check_code/<string:code>', type='json', auth='public', website=True)
    # def survey_check_session_code(self, code):
    #     """ Проверяет введенный код с кодом отправленным в письме"""
    #     print("+++++++ survey_check_session_code", code)
    #     survey = self._fetch_from_session_code(code)
    #     if survey:
    #         return {"survey_url": "/survey/start/%s" % survey.access_token}

    #     return {"error": "survey_wrong"}

   