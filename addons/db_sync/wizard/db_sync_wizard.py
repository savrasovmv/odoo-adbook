import logging
import threading
import time
from xmlrpc.client import ServerProxy
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.tools import format_datetime

_logger = logging.getLogger(__name__)


class RPCProxyOne(object):
    def __init__(self, server, ressource):
        """Class to store one RPC proxy server."""
        self.server = server
        local_url = "%s:%d/xmlrpc/2/common" % (
            server.server_url,
            server.server_port,
        )
        rpc = ServerProxy(local_url)
        self.uid = rpc.login(server.db_name, server.login, server.password)
        local_url = "%s:%d/xmlrpc/2/object" % (
            server.server_url,
            server.server_port,
        )
        self.rpc = ServerProxy(local_url)
        self.ressource = ressource

    def __getattr__(self, name):
        return lambda *args, **kwargs: self.rpc.execute(
            self.server.db_name,
            self.uid,
            self.server.password,
            self.ressource,
            name,
            *args
        )


class RPCProxy(object):
    """Class to store RPC proxy server."""

    def __init__(self, server):
        self.server = server

    def get(self, ressource):
        return RPCProxyOne(self.server, ressource)



class DbSyncWizard(models.TransientModel):
    """Форма действия синхронизации"""

    _name = "db.sync_wizard"
    _description = "Форма действия синхронизации"

    @api.depends("server")
    def _compute_report_vals(self):
        self.report_total = 0
        self.report_create = 0
        self.report_write = 0

    server_id = fields.Many2one(
        "db.sync_server", "Сервер", required=True
    )

    user_id = fields.Many2one(
        "res.users", "Отправить результат", default=lambda self: self.env.user
    )

    result = fields.Text(string='Результат')

    
    def get_remote_id_by_local_id(self, sync_model_id, obj_id):
        """Ищит была ли ранее синхронизация, возвращает id запись удаленной базы"""
        s = self.env['db.sync_obj'].search([
            ('sync_model_id', '=', sync_model_id.id),
            ('local_id', '=', obj_id.id),
        ], limit=1)

        if len(s)>0:
            return s.remote_id
        return False

    
    
    def sync_obj(self, sync_model_id, obj_id):
        """Синхронизация конкретных объектов модели"""

        _logger.debug("Синхронизация объекта %s",  obj_id)
        pool_dist = RPCProxy(self.server_id)
        s_obj = self.get_remote_id_by_local_id(sync_model_id, obj_id)
        if s_obj:
            pass
        else:
            vals ={
                'name': obj_id.name
            }
            list_field_by_search = sync_model_id.field_by_search.split(' ')
            domain = []
            for field in list_field_by_search:
                domain.append((field, '=', obj_id[field]))

            remote_obj = pool_dist.get(sync_model_id.model_id.model).search(domain, limit=1)
            print('remote_obj', remote_obj)
            if remote_obj:
                new_id = remote_obj[0]
                _logger.debug("Обновление объекта %s в удаленной БД с id= %s" % (obj_id, new_id))
                pool_dist.get(sync_model_id.model_id.model).write([new_id], vals)
                
            else:
                _logger.debug("Создание нового объекта %s в удаленной БД " % (obj_id, ))
                new_id = pool_dist.get(sync_model_id.model_id.model).create(vals)
                _logger.debug("Создан новый объекта %s в удаленной БД с id = %s" % (obj_id, new_id))


        print("++++++++++sync_obj_line")
        # remote_id 
        # if 
        pass





    def sync_model(self, sync_model_id):
        """Синхронизация модели. Выборка объектов для синхронизации, запус синхронизации записей"""
        
        _logger.debug("Синхронизация модели. Выборка объектов для синхронизации, запус синхронизации записей")

        pool_dist = RPCProxy(self.server_id)
        module = pool_dist.get("ir.module.module")
        model_obj = sync_model_id.model_id.model
        module_id = module.search(
            [("name", "ilike", "db_sync"), ("state", "=", "installed")]
        )
        if not module_id and (sync_model_id.action == "Pull" or sync_model_id.action == "PullPush"):
            raise ValidationError(
                _(
                    """Для синхронизации объектов с типом/
                          Pull или PullPush /
                          необходимо установить модуль синхронизации/
                          на удаленный сервер"""
                )
            )
        
        for obj_id in sync_model_id.get_sync_obj_ids():
            self.sync_obj(sync_model_id, obj_id)





    def start_sync(self):
        """Начало синхронизации. Выборка моделей для синхронизации и их синхронизация"""

        _logger.debug("Начало синхронизации. Выборка моделей для синхронизации и их синхронизация")

        for sync_model_id in self.server_id.sync_model_ids:
            _logger.debug("Начало синхронизации модели  %s", sync_model_id.name)
            self.sync_model(sync_model_id)


        self.create_log()


    def create_log(self):
        if self.user_id:
            log = self.env["db.sync_log"]
            
            log.create(
                {
                    "name": "Отчет о синхронизации",
                    "date": fields.Datetime.now(),
                    "server_id": self.server_id.id,
                    "result": self.result,
                }
            )


    def start_sync_action(self):
        """События Wizard начать синхронизацию"""

        _logger.debug("События Wizard начать синхронизацию")

        threaded_sync = threading.Thread(
            target=self.start_sync()
        )
        threaded_sync.run()
        id2 = self.env.ref("db_sync.db_sync_finish_wizard").id
        return {
            "binding_view_types": "form",
            "view_mode": "form",
            "res_model": "db.sync_wizard",
            "views": [(id2, "form")],
            "view_id": False,
            "type": "ir.actions.act_window",
            "target": "new",
        }