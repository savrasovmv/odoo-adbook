from odoo import fields, models, api
from odoo import tools
from odoo.tools import html2plaintext
import base64


class BaseMultiSyncServer(models.Model):
    """Модель для подключения к внешнему серверу Odoo"""

    _name = "base.multi_sync_server"
    _description = "Сервер для синхронизации"

    name = fields.Char("Имя", required=True)
    server_url = fields.Char("URL", required=True, help="Например https://test.domain.ru")
    server_port = fields.Integer("Порт", required=True, default=8069)
    db_name = fields.Char("Имя БД", required=True)
    login = fields.Char("Имя пользователя", required=True)
    password = fields.Char("Пароль", required=True, password=True)
    obj_ids = fields.One2many(
        "base.multi_sync_obj", "server_id", "Объекты", ondelete="cascade"
    )


class BaseMultiSyncObj(models.Model):
    """Модель объекты синхронизации"""

    _name = "base.multi_sync_obj"
    _description = "Объекты синхронизации"
    _order = "sequence"

    name = fields.Char("Наименование", required=True)
    domain = fields.Char("Домен", required=True, default="[]")
    server_id = fields.Many2one(
        "base.multi_sync_server", "Сервер", ondelete="cascade", required=True
    )
    model_id = fields.Many2one("ir.model", "Объект для синхронизации")
    field_by_search = fields.Char("Поля для поиска соответствия", required=True, default="name")
    action = fields.Selection(
        [("Pull", "Pull"), ("Push", "Push"), ("PullPush", "PullPush")],
        "Тип сихронизации",
        required=True,
        default="Push",
    )
    sequence = fields.Integer("Порядок")
    active = fields.Boolean(default=True)
    sync_date = fields.Datetime("Последняя синхронизация")
    line_id = fields.One2many(
        "base.multi_sync_line", "obj_id", "IDs объектов синхронизации", ondelete="cascade"
    )
    ignore_ids = fields.One2many(
        "base.multi_sync_ignored", "obj_id", "Игнорируемые поля объектов"
    )

    @api.model
    def get_ids(self):
        model_obj = self.env[self.model_id.model]
        if self.sync_date:
            w_date = self.domain + [("write_date", ">=", self.sync_date)]
            c_date = self.domain + [("create_date", ">=", self.sync_date)]
        else:
            w_date = c_date = self.domain
        obj_rec = model_obj.search(w_date)
        obj_rec += model_obj.search(c_date)
        return obj_rec
        # result = [
        #     (
        #         r.get("write_date") or r.get("create_date"),
        #         r.get("id"),
        #         self.action,
        #     )
        #     for r in obj_rec.read(["create_date", "write_date"])
        # ]
        # return result


class BaseMultiSyncIgnored(models.Model):
    """Игнорируемые поля объектов"""

    _name = "base.multi_sync_ignored"
    _description = "Игнорируемые поля объекта"

    name = fields.Char("Имя поля", required=True)
    obj_id = fields.Many2one(
        "base.multi_sync_obj", "Объект", required=True, ondelete="cascade"
    )


class BaseMultiSyncLine(models.Model):
    """Строки Ids объектов синхронизации"""

    _name = "base.multi_sync_line"
    _description = "Синхронизированные объекты"

    name = fields.Datetime(
        "Дата", required=True, default=lambda self: fields.Datetime.now()
    )
    obj_id = fields.Many2one("base.multi_sync_obj", "Объект", ondelete="cascade")
    local_id = fields.Integer("Local ID", readonly=True)
    remote_id = fields.Integer("Remote ID", readonly=True)


class BaseMultiSyncLog(models.Model):
    """Результат синхронизации"""

    _name = "base.multi_sync_log"
    _description = "Результат синхронизации"
    _order = "date desc"
    

    name = fields.Char(
        "Наименование", required=True,
    )
    date = fields.Datetime(string='Дата')
    server_id = fields.Many2one(
        "base.multi_sync_server", "Сервер", required=True
    )
    result = fields.Text("Результат")