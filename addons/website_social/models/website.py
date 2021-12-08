# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.addons.http_routing.models.ir_http import url_for


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def get_default_social_count(self):
        self.social_count = self.env['social.social'].search_count(self.website_domain())

    social_count = fields.Integer(readonly=True, default=get_default_social_count)

    def get_suggested_controllers(self):
        suggested_controllers = super(Website, self).get_suggested_controllers()
        suggested_controllers.append((_('Social'), url_for('/social'), 'website_social'))
        return suggested_controllers
