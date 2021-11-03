# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    
    auth_signup_template_ad_user_id = fields.Many2one('res.users', string='Шаблон прав для пользователей с учетной записью в AD',
                                                   config_parameter='base.template_ad_user_id')

    def open_template_ad_user(self):
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_res_users")
        action['res_id'] = literal_eval(self.env['ir.config_parameter'].sudo().get_param('base.template_ad_user_id', 'False'))
        action['views'] = [[self.env.ref('base.view_users_form').id, 'form']]
        return action
