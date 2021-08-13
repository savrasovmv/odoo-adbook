# -*- coding: utf-8 -*-

from odoo import fields, models, api
from ldap3 import Server, Connection, SUBTREE, MODIFY_REPLACE, LEVEL
from datetime import datetime

class AdConnect(models.AbstractModel):
    _name = "ad.connect"
    _description = "Класс для работы с AD"

    def ldap_search(self, full_sync=False, date=False,search_filter=False, attributes=False):
        """ Подключется к АД, ищит записи, 
            Параметры:
                full_sync - полная синхронизация, при установке ищит в журнале синхронизации, когда последний раз было обновление и добавляет в фильтр значение даты
                search_filter - строка поиска
                attributes - требуемые атрибуты
            Возвращает:
                total_entries - общее количество полученных записей
                data - данные
         """
         #     #Подключение к серверу AD
        LDAP_HOST = self.env['ir.config_parameter'].sudo().get_param('ldap_host')
        LDAP_PORT = self.env['ir.config_parameter'].sudo().get_param('ldap_port')
        LDAP_USER = self.env['ir.config_parameter'].sudo().get_param('ldap_user')
        LDAP_PASS = self.env['ir.config_parameter'].sudo().get_param('ldap_password')
        LDAP_SSL = self.env['ir.config_parameter'].sudo().get_param('ldap_ssl')
        LDAP_SEARCH_BASE = self.env['ir.config_parameter'].sudo().get_param('ldap_search_base')
        # LDAP_SEARCH_FILTER = self.env['ir.config_parameter'].sudo().get_param('ldap_search_filter')
        # LDAP_SEARCH_GROUP_FILTER = self.env['ir.config_parameter'].sudo().get_param('ldap_search_group_filter')
        if not search_filter:
            raise "Не заполнен параметр search_filter"

        if LDAP_HOST and LDAP_PORT and LDAP_USER and LDAP_PASS and LDAP_SSL and LDAP_SEARCH_BASE:
            pass
        else:
            raise "Нет учетных данных для подключения. Настройки-Синхронизация"
        try:
            ldap_server = Server(host=LDAP_HOST, port=int(LDAP_PORT), use_ssl=LDAP_SSL, get_info='ALL', connect_timeout=10)
            c = Connection(ldap_server, user=LDAP_USER, password=LDAP_PASS, auto_bind=True)
        except Exception as e:
            raise 'Невозможно соединиться с AD. Ошибка: ' + str(e)
        
        # search_filter = "(&(|(objectClass=user)(objectClass=contact))(whenChanged>=" + today + "))"
        #                   '(|(objectClass=user)(objectClass=contact))'

        if not full_sync:
            sl = self.env['ad.sync_log'].search([
                                                    ('obj', '=', self.__class__.__name__),
                                                    ('is_error', '=', False),
                                                ], 
                                                limit=1, 
                                                order='date desc'
                                                )
            if sl:
                search_filter =  "(&"+ search_filter + "(whenChanged>=" + sl.date.strftime('%Y%m%d%H%M')  + "00.0Z))" #секунды обнулил

        total_entries = 0

        # Постраничный поиск
        res = c.search(
                        search_base=LDAP_SEARCH_BASE,
                        search_filter=search_filter,
                        search_scope=SUBTREE,
                        attributes=attributes,
                        paged_size = 500
                    )
        
        total_entries += len(c.response)
        cookie = c.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        data = c.entries
        page = 1
        while cookie:
            res = c.search(
                            search_base=LDAP_SEARCH_BASE,
                            search_filter=search_filter,
                            search_scope=SUBTREE,
                            attributes=attributes,
                            paged_size = 500,
                            paged_cookie = cookie
                        )
            total_entries += len(c.response)
            cookie = c.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
            data += c.entries
        
        return total_entries, data


    def create_ad_log(self, date=False, is_error=False, result=''):
        """Создает запись в журнале синхронизации с AD"""
        if not date:
            date = datetime.today()
        self.env['ad.sync_log'].sudo().create({
                    'date': date, 
                    'obj': self.__class__.__name__, 
                    'name': self.__class__._description, 
                    'is_error': is_error,
                    'result': result
                    })




class AdGroup(models.Model):
    _name = "ad.group"
    _description = "Группы AD"
    _order = "name"
    _inherit = ['ad.connect']

    name = fields.Char(u'Наименование', required=True, readonly=True)

    distinguished_name = fields.Char(u'AD distinguishedName', readonly=True)
    account_name = fields.Char(u'sAMAccountName', readonly=True)
    object_SID = fields.Char(u'AD objectSID', readonly=True)
    is_ldap = fields.Boolean('LDAP?', default=False, readonly=True)

    active = fields.Boolean('Active', default=True)
    is_managed = fields.Boolean('Управляемая', default=False, help="Включите, для управления вхождения сотрудника в эту группу в форме Сотрудника")

     # Синхронизация групп
    def ad_sync_group(self, full_sync=False):
        date = datetime.today()
        LDAP_SEARCH_GROUP_FILTER = self.env['ir.config_parameter'].sudo().get_param('ldap_search_group_filter')
        if not LDAP_SEARCH_GROUP_FILTER:
            raise 'Не заполнен параметр ldap_search_group_filter'

        attributes = ['cn', 'distinguishedName', 'whenChanged', 'objectSID', 'sAMAccountName']
        
        try:
            res = self.ldap_search(
                                    search_filter=LDAP_SEARCH_GROUP_FILTER,
                                    attributes=attributes,
                                    full_sync=full_sync
                                )
                                
        except Exception as error:
            raise error
        
        if res:
            total_entries, data = res
        else:
            raise 'Ошибка. Данные не получены'
        
        if total_entries == 0:
            result = "Новых данных нет"
            self.create_ad_log(result=result)
            return result

        n = 0
        message_error = ''
        message_update = ''
        message_create = ''
        for group in data:

            group_name = group['cn'].value

            if len(group_name) == 0:
                message_error += "Не указано CN поля для записи %s, пропускаю \n" % str(group) 
                break

            #Search Group
            g_search = self.search([
                                        ('object_SID', '=', group['objectSID']),
                                        '|',
                                        ('active', '=', False), 
                                        ('active', '=', True)
                                    ],limit=1)

            
            vals = {
                    'name': group_name,
                    'account_name': group['sAMAccountName'].value,
                    'object_SID': group['objectSID'].value,
                    'distinguished_name': group['distinguishedName'].value,
                    'active': True,
                    'is_ldap': True,
                }
            if len(g_search)>0 :
                message_update += group_name + '\n'
                g_search.write(vals)
            else:
                message_create += group_name + '\n'
                self.create(vals)
        

        result ='Всего получено из АД %s записей \n' % total_entries
        if not message_error == '':
            result = "\n Обновление прошло с предупреждениями: \n \n" + message_error
        else:
            result = "\n Обновление прошло успешно \n \n"
        if not message_create == '':
            result += "\n Создны новые группы: \n" + message_create
        if not message_update == '':
            result += "\n Обновлены группы: \n" + message_update

        #self.env['ad.sync_log'].sudo().create({'name': 'Группы AD', 'is_error': False, 'result': result})
        self.create_ad_log(date=date, result=result)

        return result



flags = [
    [0x0001, 'SCRIPT'],
    [0x0002, 'ACCOUNTDISABLE'],
    [0x0008, 'HOMEDIR_REQUIRED'],
    [0x0010, 'LOCKOUT'],
    [0x0020, 'PASSWD_NOTREQD'],
    [0x0040, 'PASSWD_CANT_CHANGE'],
    [0x0080, 'ENCRYPTED_TEXT_PWD_ALLOWED'],
    [0x0100, 'TEMP_DUPLICATE_ACCOUNT'],
    [0x0200, 'NORMAL_ACCOUNT'],
    [0x0800, 'INTERDOMAIN_TRUST_ACCOUNT'],
    [0x1000, 'WORKSTATION_TRUST_ACCOUNT'],
    [0x2000, 'SERVER_TRUST_ACCOUNT'],
    [0x10000, 'DONT_EXPIRE_PASSWORD'],
    [0x20000, 'MNS_LOGON_ACCOUNT'],
    [0x40000, 'SMARTCARD_REQUIRED'],
    [0x80000, 'TRUSTED_FOR_DELEGATION'],
    [0x100000, 'NOT_DELEGATED'],
    [0x200000, 'USE_DES_KEY_ONLY'],
    [0x400000, 'DONT_REQ_PREAUTH'],
    [0x800000, 'PASSWORD_EXPIRED'],
    [0x1000000, 'TRUSTED_TO_AUTH_FOR_DELEGATION'],
    [0x04000000, 'PARTIAL_SECRETS_ACCOUNT'],
  ]


class AdEmployer(models.AbstractModel):
    _name = 'ad.employer'
    _description = 'Сотрудники AD'
    _inherit = ['ad.connect']

    # Синхронизация сотрудников
    def ad_sync_employe(self, full_sync=False):
        LDAP_SEARCH_FILTER = self.env['ir.config_parameter'].sudo().get_param('ldap_search_filter')
        if not LDAP_SEARCH_FILTER:
            raise 'Не заполнен параметр ldap_search_group_filter'

        attributes = ['cn', 'title', 'ipPhone', 'mobile', 'mail', 'department', 'sn', 'memberof', 'distinguishedName', 'homePhone', 'whenChanged', 'objectSID', 'sAMAccountName', 'thumbnailPhoto', 'userAccountControl']
        
        try:
            res = self.ldap_search(
                                    search_filter=LDAP_SEARCH_FILTER,
                                    attributes=attributes,
                                    full_sync=full_sync
                                )
        except Exception as error:
            raise error
        
        if res:
            total_entries, data = res
        else:
            raise 'Ошибка. Данные не получены'
        
        if total_entries == 0:
            result = "Новых данных нет"
            self.create_ad_log(result=result)
            return result

        result = "ok"
        self.create_ad_log(result=result)

        return result
       



    

