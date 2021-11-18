from odoo import fields, models, api
from odoo import tools
from odoo.tools import html2plaintext
import base64


class DbSyncServer(models.Model):
    """Модель настройка для подключения к внешнему серверу Odoo"""

    _name = "db.sync_server"
    _description = "Сервер для синхронизации"

    name = fields.Char("Имя", required=True)
    server_url = fields.Char("URL", required=True, help="Например https://test.domain.ru")
    server_port = fields.Integer("Порт", required=True, default=8069)
    db_name = fields.Char("Имя БД", required=True)
    login = fields.Char("Имя пользователя", required=True)
    password = fields.Char("Пароль", required=True, password=True)
    sync_model_ids = fields.One2many(
        "db.sync_model", "server_id", "Модели", ondelete="cascade"
    )


class DbSyncModel(models.Model):
    """Модели БД для синхронизации"""

    _name = "db.sync_model"
    _description = "Модели синхронизации"
    _order = "sequence"

    name = fields.Char("Наименование", required=True)
    domain = fields.Char("Домен", required=True, default=[])
    server_id = fields.Many2one(
        "db.sync_server", "Сервер", ondelete="cascade", required=True
    )
    model_id = fields.Many2one("ir.model", "Модель БД")
    field_by_search = fields.Char("Поля для поиска соответствия", required=True, default="name", help="Поля разделенные пробелами по которым будет идти поиск в начальной синхронизации")
    action = fields.Selection(
        [("Pull", "Pull"), ("Push", "Push"), ("PullPush", "PullPush")],
        "Тип сихронизации",
        required=True,
        default="Push",
    )
    sequence = fields.Integer("Порядок")
    active = fields.Boolean(default=True)
    sync_date = fields.Datetime("Последняя синхронизация")
    field_ids = fields.One2many(
        "db.sync_model_field", "sync_model_id", "IDs полей модели", ondelete="cascade"
    )
    obj_ids = fields.One2many(
        "db.sync_obj", "sync_model_id", "IDs объектов синхронизации", ondelete="cascade"
    )
    field_ignored_ids = fields.One2many(
        "db.sync_model_field_ignored", "sync_model_id", "Игнорируемые поля объектов"
    )

    # @api.model
    def action_set_field_ids(self):
        self.field_ids.unlink()
        fields = self.env['ir.model.fields'].search([
            ('model_id', '=', self.model_id.id)
        ])

        for f in fields:
            vals = {
                'model_field_id': f.id,
                'sync_model_id': self.id,
            }
            self.field_ids.create(vals)

    @api.model
    def get_sync_obj_ids(self, action=None):
        print("++++++++get_ids")
        domain = eval(self.domain)
        model_obj = self.env[self.model_id.model]
        if self.sync_date:
            w_date = domain + [("write_date", ">=", self.sync_date)]
            c_date = domain + [("create_date", ">=", self.sync_date)]
        else:
            w_date = c_date = domain
        
        obj_rec = model_obj.search(w_date)
        # obj_rec = model_obj.search(self.domain)

        obj_rec += model_obj.search(c_date)

        obj_rec = list(set(obj_rec)) #Удаляем дубликаты из списка

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

class DbSyncModelField(models.Model):
    """Поля Модели БД для синхронизации"""

    _name = "db.sync_model_field"
    _description = "Поля Модели синхронизации"
    _order = "name"

    name = fields.Char("Наименование", related="model_field_id.name")
    model_field_id = fields.Many2one("ir.model.fields", "Поля модели БД")
    ttype = fields.Selection(string='Тип', related="model_field_id.ttype")
    field_description = fields.Char(string='Описание поля', related="model_field_id.field_description")
    relation = fields.Char(string='Связь с моделью', related="model_field_id.relation")
    is_sync = fields.Boolean(string='Синхронизовать', default=False)

    sync_model_id = fields.Many2one("db.sync_model", "Модель синхронизации", required=True, ondelete="cascade")




class DbSyncModelFieldIgnored(models.Model):
    """Игнорируемые поля объектов"""

    _name = "db.sync_model_field_ignored"
    _description = "Игнорируемые поля объекта"

    name = fields.Char("Имя поля", required=True)
    sync_model_id = fields.Many2one(
        "db.sync_model", "Модель синхронизации", required=True, ondelete="cascade"
    )


class DbSyncObj(models.Model):
    """Строки Ids объектов синхронизации"""

    _name = "db.sync_obj"
    _description = "Синхронизированные объекты"

    name = fields.Datetime(
        "Дата", required=True, default=lambda self: fields.Datetime.now()
    )
    model_id = fields.Many2one("ir.model", "Модели БД", related="sync_model_id.model_id")
    sync_model_id = fields.Many2one("db.sync_model", "Модель синхронизации", required=True, ondelete="cascade")
    local_id = fields.Integer("Local ID", readonly=True)
    remote_id = fields.Integer("Remote ID", readonly=True)

    def get_remote_id_by_local_id(self, sync_model_id, local_id):
        """Ищит была ли ранее синхронизация, возвращает id запись удаленной базы"""
        
        s = self.search([
            ('sync_model_id', '=', sync_model_id),
            ('local_id', '=', local_id),
        ], limit=1)
       
        if len(s)>0:
            return s.remote_id
        
        return False

        



class DbSyncLog(models.Model):
    """Результат синхронизации"""

    _name = "db.sync_log"
    _description = "Результат синхронизации"
    _order = "date desc"
    

    name = fields.Char(
        "Наименование", required=True,
    )
    date = fields.Datetime(string='Дата')
    server_id = fields.Many2one(
        "db.sync_server", "Сервер", required=True
    )
    result = fields.Text("Результат")