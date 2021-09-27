from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.department"

    # 1С
    guid_1c = fields.Char(string='guid1C', readonly=True, groups="base.group_erp_manager, base.group_system")
    code_1c = fields.Char(string='Код 1С', readonly=True, groups="base.group_erp_manager, base.group_system")

    # Показывать в справочнике контактов
    is_view_adbook = fields.Boolean(string='Отоброжать в справочнике сотрудников', default=True)
