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



class BaseMultiSyncWizard(models.TransientModel):
    """Форма действия синхронизации"""

    _name = "base.multi_sync_wizard"
    _description = "Форма действия синхронизации"

    @api.depends("server")
    def _compute_report_vals(self):
        self.report_total = 0
        self.report_create = 0
        self.report_write = 0

    server_id = fields.Many2one(
        "base.multi_sync_server", "Сервер", required=True
    )

    user_id = fields.Many2one(
        "res.users", "Отправить результат", default=lambda self: self.env.user
    )

    result = fields.Text(string='Результат')

    
    def get_sync_obj_line_by_id(self, obj_id, obj_line_id):
        """Ищит была ли ранее синхронизация, возвращает id запись удаленной базы"""
        s = self.env['base.multi_sync_line'].search([
            ('obj_id', '=', obj_id),
            ('local_id', '=', obj_line_id),
        ], limit=1).id
        return s

    def sync_obj_line(self, obj_line):
        pass





    def sync_obj(self, obj):
        pool_dist = RPCProxy(self.server_id)
        module = pool_dist.get("ir.module.module")
        model_obj = obj.model_id.model
        module_id = module.search(
            [("name", "ilike", "base_multi_sync"), ("state", "=", "installed")]
        )
        if not module_id and (obj.action == "Pull" or obj.action == "PullPush"):
            raise ValidationError(
                _(
                    """Для синхронизации объектов с типом/
                          Pull или PullPush /
                          необходимо установить модуль синхронизации/
                          на удаленный сервер"""
                )
            )

        for obj_line in obj.get_ids():
            self.sync_obj_line(obj_line)



    def start_sync(self):

        for obj in self.server_id.obj_ids:
            _logger.debug("Начало синхронизации  %s", obj.name)
            self.sync_obj(obj)


        self.create_log()


    def create_log(self):
        if self.user_id:
            log = self.env["base.multi_sync_log"]
            
            log.create(
                {
                    "name": "Отчет о синхронизации",
                    "date": fields.Datetime.now(),
                    "server_id": self.server_id.id,
                    "result": self.result,
                }
            )


    def start_sync_action(self):
        threaded_sync = threading.Thread(
            target=self.start_sync()
        )
        threaded_sync.run()
        id2 = self.env.ref("base_multi_sync.base_multi_sync_finish_wizard").id
        return {
            "binding_view_types": "form",
            "view_mode": "form",
            "res_model": "base.synchro",
            "views": [(id2, "form")],
            "view_id": False,
            "type": "ir.actions.act_window",
            "target": "new",
        }