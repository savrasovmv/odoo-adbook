# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Settings(models.TransientModel):
    _inherit = 'res.config.settings'

    survey_reg_email = fields.Char(u'E-mail для отправки сообщения при регистрации', help="С этого адреса будут отправляться сообщения при запросе ФИО и email в форме регистрации", default='')
      
    @api.model
    def get_values(self):
        res = super(Settings, self).get_values()
        conf = self.env['ir.config_parameter']
        res.update({
                'survey_reg_email': conf.get_param('survey_reg_email'),
        })
        return res


    def set_values(self):
        super(Settings, self).set_values()
        conf = self.env['ir.config_parameter']
        conf.set_param('survey_reg_email', self.survey_reg_email)

