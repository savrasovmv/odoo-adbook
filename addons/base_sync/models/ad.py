# -*- coding: utf-8 -*-

from odoo import fields, models, api
from ldap3 import Server, Connection, SUBTREE, MODIFY_REPLACE, LEVEL
from datetime import datetime
import base64


class AdConnect(models.AbstractModel):
    _name = "ad.connect"
    _description = "Класс для работы с AD"

    def ldap_search(self, full_sync=False, date=False, search_filter=False, attributes=False):
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

        # Если дату не определим то делаем полную синхронизацию
        if not full_sync and not date:
            sl = self.env['sync.log'].search([
                                                    ('obj', '=', self.__class__.__name__),
                                                    ('is_error', '=', False),
                                                ], 
                                                limit=1, 
                                                order='date desc'
                                                )
            if sl:
                date = sl.date if sl.date else False
        
        if date:
            search_filter =  "(&"+ search_filter + "(whenChanged>=" + date.strftime('%Y%m%d%H%M')  + "00.0Z))" #секунды обнулил

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
        self.env['sync.log'].sudo().create({
                    'date': date, 
                    'obj': self.__class__.__name__, 
                    'name': self.__class__._description, 
                    'is_error': is_error,
                    'result': result
                    })




class AdSyncGroup(models.AbstractModel):
    _name = "ad.sync_group"
    _description = "Синхронизация Групп AD"
    _inherit = ['ad.connect']


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
            g_search = self.env['ad.group'].search([
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
                self.env['ad.group'].create(vals)
        

        result ='Всего получено из АД %s записей \n' % total_entries
        if not message_error == '':
            result += "\n Обновление прошло с предупреждениями: \n \n" + message_error
        else:
            result += "\n Обновление прошло успешно \n \n"
        if not message_create == '':
            result += "\n Создны новые группы: \n" + message_create
        if not message_update == '':
            result += "\n Обновлены группы: \n" + message_update

        #self.env['sync.log'].sudo().create({'name': 'Группы AD', 'is_error': False, 'result': result})
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


class AdSyncUsers(models.AbstractModel):
    _name = 'ad.sync_users'
    _description = 'Пользователи AD'
    _inherit = ['ad.connect']

    # Синхронизация пользователей
    def ad_sync_users(self, full_sync=False):
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


        n = 0
        message_error = ''
        message_branch = ''
        message_department = ''
        message_user_update = ''
        message_user_create = ''
        for user in data:

            user_name = user['cn'].value
            

            if len(user_name) == 0:
                message_error += "Не указано CN поля для записи %s, пропускаю \n" % str(user) 
                break
            n += 1
            #if n>5: break
            #print(user)
            #Search Branch
            distinguishedName = user['distinguishedName'].value
            if user['distinguishedName'].value:
                branch_name = distinguishedName.split(',OU=')[1]
                #print("Branch = ", branch_name)
                branch_search = self.env['ad.branch'].search([('ad_name', '=', branch_name)],limit=1)
                if not branch_search:
                    branch_id = self.env['ad.branch'].create({
                                                'name': branch_name, 
                                                'ad_name': branch_name, 
                                                'adbook_name': branch_name, 
                                            }).id
                    message_branch += branch_name +"\n"
                else:
                    branch_id = branch_search.id
            else:
                message_error += "Для %s не задан branch. \n" % user_name
                branch_id = None

            #Search Department
            if user['department'].value:
                department_name = user['department'].value
                if len(department_name)>0:
                    #print("department_name = ", department_name)
                    department_search = self.env['ad.department'].search([('name', '=', department_name)],limit=1)
                    if not department_search:
                        department_id = self.env['ad.department'].create({
                                                    'name': department_name, 
                                                }).id
                        message_department += department_name +"\n"
                    else:
                        department_id = department_search.id
                else:
                    message_error += "Для %s не задан department. \n" % user_name
                    department_id = None
            else:
                message_error += "Для %s не задан department. \n" % user_name
                department_id = None



            #Photo
            if user['thumbnailPhoto'].value:
                thumbnailPhoto = base64.b64encode(user['thumbnailPhoto'].value).decode("utf-8")
            else:
                thumbnailPhoto = None

            #Search users
            user_search = self.env['ad.users'].search([
                                        ('object_SID', '=', user['objectSID']),
                                        '|',
                                        ('active', '=', False), 
                                        ('active', '=', True)
                                    ],limit=1)



            # 514 отключенный пользователь
            uic = int(user['userAccountControl'].value or '514')
            active = True
            # Если пользователь отключен, ACCOUNTDISABLE	0x0002	2
            if uic | 2 == uic:
                active = False 
            
            vals = {
                    'name': user_name,
                    'branch_id': branch_id,
                    'department_id': department_id,
                    'title': user['title'].value,
                    'ip_phone': user['ipPhone'].value,
                    'phone': user['mobile'].value,
                    'sec_phone': user['homePhone'].value,
                    'email': user['mail'].value,
                    'username': user['sAMAccountName'].value,
                    'object_SID': user['objectSID'].value,
                    'distinguished_name': user['distinguishedName'].value,
                    'user_account_control': user['userAccountControl'].value,
                    'photo': thumbnailPhoto,
                    'active': active,
                    'is_ldap': True,
                    # 'photo': base64.b64decode(user['thumbnailPhoto'].value)

                }
            if len(user_search)>0 :
                #print('Обновление ', user_search.name)
                message_user_update += user_name + '\n'
                user_search.write(vals)
            else:
                #print('Создание  ', user_name)
                message_user_create += user_name + '\n'
                self.env['ad.users'].create(vals)
            #print(vals)
        # if res:
        #     emp = c.response[0]
        #     print(emp)
        #     atr = emp['attributes']
        #     dn = emp['dn']
        #     print(atr)
        #     department = atr['department']
            # self.name = atr['cn']
            # self.department = atr['department']
            # self.title = atr['title']
            # self.ou = dn.split(',OU=')[1]
            # self.ip_phone = atr['ipPhone']

        result ='Всего получено из АД %s записей \n' % total_entries
        if not message_error == '':
            result = "\n Обновление прошло с предупреждениями: \n \n" + message_error
        else:
            result = "\n Обновление прошло успешно \n \n"
        if not message_branch == '':
            result = "\n Добавлены филиалы, необходимо назначить имена: \n" + message_branch
        if not message_department == '':
            result = "\n Добавлены управления/отделы AD: \n" + message_department
        if not message_user_create == '':
            result += "\n Создны новые пользователи AD: \n" + message_user_create
        if not message_user_update == '':
            result += "\n Обновлены пользователи AD: \n" + message_user_update
        #print("result sync: ", result)

        self.create_ad_log(result=result)

        return result
       



    

