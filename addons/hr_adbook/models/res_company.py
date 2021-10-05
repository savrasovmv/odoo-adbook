from odoo import api, fields, models


class ResCountry(models.Model):
    _inherit = "res.company"

    # 1С
    domain_name = fields.Char(string='Имя домена')
    