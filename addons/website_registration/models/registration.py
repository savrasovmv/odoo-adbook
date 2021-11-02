from odoo import fields, models, api
from odoo import tools
from odoo.tools import html2plaintext
import base64

import random

def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for _ in range(20))


class Registration(models.Model):
    _name = "reg.reg"
    _description = "Регистрации"
    _order = "name"

    name = fields.Char(u'IP адрес', required=True)
    token = fields.Char(u'Токен', required=True)
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now())
    captcha_text = fields.Char(u'Код captcha', required=True)
    active = fields.Boolean(string='Активна?', default=True)

    @api.model
    def _verify_recaptcha(self, ip_addr, captcha_text, token):
        res = self.sudo().search([
            ('name', '=', ip_addr),
            ('captcha_text', '=', captcha_text),
            ('token', '=', token),
            ], limit=1, order='date asc')

        if len(res)>0:
            return True
        
        return False

    @api.model
    def _set_recaptcha(self, ip_addr, captcha_text):
        token = random_token()
        self.sudo().create({
            'name': ip_addr,
            'token': token,
            'captcha_text': captcha_text,
        })
        return token

class RegistrationActivation(models.Model):
    _name = "reg.activation"
    _description = "Активация регистрации."
    _order = "name"

    name = fields.Char(u'Токен', required=True)
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now())
    user_id = fields.Many2one('res.users', string='Пользователь', required=True)

    active = fields.Boolean(string='Активна?', default=True)

    @api.model
    def _verify_recaptcha(self, ip_addr, captcha_text):
        res = self.sudo().search([
            ('name', '=', ip_addr),
            ('captcha_text', '=', captcha_text),
            ], limit=1, order='date asc')

        if len(res)>0:
            return True
        
        return False

    @api.model
    def _set_token(self, user_id):
        token = random_token()
        self.sudo().create({
            'name': ip_addr,
            'captcha_text': captcha_text,
        })


class RegistrationСonditions(models.Model):
    _name = "reg.conditions"
    _description = "Соглашения"
    _order = "name asc"

    name = fields.Datetime(u'Дата начала', required=True)
    conditions = fields.Html(string='Условия', required=True)
    confidentiality = fields.Html(string='Конфиденциальность', required=True)

    @api.model
    def get_conditions(self):
        return self.sudo().search([], limit=1)

import ipaddress

class RegistrationAllowedIP(models.Model):
    _name = "reg.allowed_ip"
    _description = "Разрешенные IP для доступа к ресурсу без капчи"
    _order = "name asc"

    name = fields.Char(u'Наименование', required=True)
    networks = fields.Char(u'Подсеть', required=True)

    @api.model
    def get_allowed(self, ip):
        nets = self.sudo().search()
        for net in nets:
            an_address = ipaddress.ip_address(ip)
            a_network = ipaddress.ip_network(net.networks)
            if an_address in a_network:
                return True
        
        return False