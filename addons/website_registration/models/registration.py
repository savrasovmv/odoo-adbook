from odoo import fields, models, api
from odoo import tools
from odoo.tools import html2plaintext
import base64




class Registration(models.Model):
    _name = "reg.reg"
    _description = "Регистрации"
    _order = "name"

    name = fields.Char(u'IP адрес', required=True)
    date = fields.Datetime(string='Дата', required=True, default=fields.Datetime.now())
    captcha_text = fields.Char(u'Код captcha', required=True)
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
    def _set_recaptcha(self, ip_addr, captcha_text):
        self.sudo().create({
            'name': ip_addr,
            'captcha_text': captcha_text,
        })