from odoo import api, fields, models


class ResCountry(models.Model):
    _inherit = "res.country"

    # 1С
    name_in_zup = fields.Char(string='Нименование в ЗУП')
    