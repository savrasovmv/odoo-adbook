
from odoo import fields, models, api
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError

import logging
_logger = logging.getLogger(__name__)



class ZupConnect(models.AbstractModel):
    _name = "zup.connect"
    _description = "Класс для работы с 1С:ЗУП"

    def zup_search(self, url_api=False, full_sync=False, date=False,search_filter=False, attributes=False):
        """ Подключется к ЗУП, ищит записи, 
            Параметры:
                full_sync - полная синхронизация, при установке ищит в журнале синхронизации, когда последний раз было обновление и добавляет в фильтр значение даты
                search_filter - строка поиска
                attributes - требуемые атрибуты
            Возвращает:
                total_entries - общее количество полученных записей
                data - данные
         """
        _logger.info("Подключение к ЗУП")

        ZUP_USER = self.env['ir.config_parameter'].sudo().get_param('zup_user')
        ZUP_PASSWORD = self.env['ir.config_parameter'].sudo().get_param('zup_password')
        ZUP_TIMEOUT = self.env['ir.config_parameter'].sudo().get_param('zup_timeout')

        if not ZUP_USER or not ZUP_PASSWORD:
            _logger.error("Нет учетных данных для доступ к API ЗУП. Проверьте настройки")
            raise "Нет учетных данных для доступ к API ЗУП. Проверьте настройки"
        
        try:
            response = requests.get(
                                url_api,
                                auth=HTTPBasicAuth(ZUP_USER, ZUP_PASSWORD),
                                timeout=int(ZUP_TIMEOUT)
                            )
            if response.status_code != 200:
                err = "Ошибка, Код ответа: %s" % response.status_code
                _logger.error(err)
                raise Exception(err)
     
        except Exception as error:
            _logger.error("Ошибка при выполнении подключения к ЗУП:" + str(error))
            raise Exception("Ошибка при выполнении подключения к ЗУП:" + str(error))

        res = response.json()

        total_entries = len(res['data'])
        data = res['data']
        #return total_entries, data
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




class ZupSync(models.AbstractModel):
    _name = 'zup.sync'
    _description = 'Синхронизация ЗУП'
    _inherit = ['zup.connect']
  

    def zup_sync_dep(self):
        """Загрузка информации по подразделениям из ЗУП"""
        date = datetime.today()
        URL_API = self.env['ir.config_parameter'].sudo().get_param('zup_url_get_dep_list')
        if not URL_API:
            raise "Не заполнен параметр zup_url_get_dep_list"

        try:
            res = self.zup_search(
                                    url_api=URL_API
                                )
        except Exception as error:
            self.create_ad_log(date=date,result=error, is_error=True)
            raise error

        if res:
            total_entries, data = res
        else:
            self.create_ad_log(date=date,result='Ошибка. Данные не получены', is_error=True)
            raise 'Ошибка. Данные не получены'
        
        if total_entries == 0:
            result = "Новых данных нет"
            self.create_ad_log(result=result)
            return result
        
        n = 0
        message_error = ''
        message_update = ''
        message_create = ''
        # Пример записи {'guid1C': 'e91bef40-1d5a-4942-80d4-e6febb61edb5', 'code': '49', 'name': 'Планово-экономический отдел', 'parentGuid1C': '493c1dd5-ba5b-11e9-94b3-00155d000c0e', 'managerGuid1C': ''}
        for line in data:
            if 'name' in line and 'guid1C' in line:
                name = line['name'] 
                guid_1c = line['guid1C']
                code_1c = line['code'] if 'code' in line else ''
                parent_guid_1c = line['parentGuid1C'] if 'parentGuid1C' in line else ''
                manager_guid_1c = line['managerGuid1C'] if 'managerGuid1C' in line else ''

                manager_id = self.env['hr.employee'].search([
                    ('guid_1c', '=', manager_guid_1c)
                ],limit=1).id

                parent_id = self.env['hr.department'].search([
                    ('guid_1c', '=', parent_guid_1c)
                ],limit=1).id

                record_search = self.env['hr.department'].search([
                    ('guid_1c', '=', guid_1c)
                ],limit=1)

                vals = {
                    'name': name,
                    'guid_1c': guid_1c,
                    'code_1c': code_1c,
                    'parent_id': parent_id,
                    'manager_id': manager_id,
                }

                if len(record_search)>0:
                    message_update += name + '\n'
                    record_search.write(vals)
                else:
                    n +=1
                    message_create += name + '\n'
                    record_search.create(vals)
            else:
                message_error += "Отсутствует Наименование или УИД 1С  в запси: %s \n" % line


        result ='Всего получено из ЗУП %s записей \n' % total_entries
        if not message_error == '':
            result = "\n Обновление прошло с предупреждениями: \n \n" + message_error
        else:
            result = "\n Обновление прошло успешно \n \n"

        if not message_create == '':
            result += "\n Создно %s новых Подразделений: \n" % n
            result += message_create

        if not message_update == '':
            result += "\n Обновлены Подразделения: \n" + message_update

        self.create_ad_log(result=result)

        return result


    def zup_sync_employer(self):
        """Загрузка информации по Сотрудникам из ЗУП"""
        date = datetime.today()
        URL_API = self.env['ir.config_parameter'].sudo().get_param('zup_url_get_empl_list')
        if not URL_API:
            raise "Не заполнен параметр zup_url_get_empl_list"

        try:
            res = self.zup_search(
                                    url_api=URL_API
                                )
        except Exception as error:
            self.create_ad_log(date=date,result=error, is_error=True)
            raise error

        if res:
            total_entries, data = res
        else:
            self.create_ad_log(date=date,result='Ошибка. Данные не получены', is_error=True)
            raise 'Ошибка. Данные не получены'
        
        if total_entries == 0:
            result = "Новых данных нет"
            self.create_ad_log(result=result)
            return result
        
        n = 0
        message_error = ''
        message_update = ''
        message_create = ''
        # Пример записи {
            # 'guid1C': 'd71e435e-8abe-11e2-bf2d-009c029f6565', 
            # 'number': '0001118', 
            # 'name': 'Иванов Иван Иванович',
            # 'employmentDate': '2013-03-12T00:00:00',
            # 'birthDate': '1987-05-28T00:00:00', 
            # 'gender': 'Мужской', 
            # 'citizenship': 'RU', 
            # 'eMail': '', 
            # 'employmentType': 'Основное место работы', 
            # 'departament': 'e9c52c32-d042-41f3-9f6f-85c6896ee423', 
            # 'position': 'Ведущий инженер'}
        for line in data:
            if 'name' in line and 'guid1C' in line and 'departament' in line and 'position' in line:
                name = line['name'] 
                guid_1c = line['guid1C']
                
                #Подразделение
                department_guid_1c = line['departament']
                department = self.env['hr.department'].search([
                    ('guid_1c', '=', department_guid_1c)
                ],limit=1)
                department_id = department.id 
                
                # Должность
                job_title = line['position']
                # Дата рождение
                birthday = None
                birthday_text = line['birthDate'] if 'birthDate' in line else ''
                if birthday_text != '':
                    birthday = datetime.strptime(birthday_text, '%Y-%m-%dT%H:%M:%S').date()

                # Дата принятия на работу
                service_start_date = None
                service_start_date_text = line['employmentDate'] if 'employmentDate' in line else ''
                if service_start_date_text != '':
                    service_start_date = datetime.strptime(service_start_date_text, '%Y-%m-%dT%H:%M:%S').date()

                # Пол
                gender = None
                gender_text = line['gender'] if 'gender' in line else ''
                if gender_text =='Мужской':
                    gender = 'male'
                if gender_text =='Женский':
                    gender = 'female'
                # Гражданство, страна
                country_id = None
                country_text = line['citizenship'] if 'citizenship' in line else ''
                if country_text != '':
                    country_id = self.env['res.country'].search([
                        ('code', '=', country_text)
                    ],limit=1).id
                # Личный адрес
                personal_email = line['eMail'] if 'eMail' in line else ''
                
                # Вид знятости
                employment_type_1c = line['employmentType'] if 'employmentType' in line else ''

                number_1c = line['number'] if 'number' in line else ''

                

                record_search = self.env['hr.employee'].search([
                    ('guid_1c', '=', guid_1c)
                ],limit=1)

                # Менеджер
                parent_id = None
                # Если Менеджер это есть текущий сотрудник, то нужно искать менеджера в вышестоящем подразделеии
                if record_search.id != department.manager_id.id:
                    parent_id = self.env['hr.employee'].search([
                        ('id', '=', department.manager_id.id)
                    ],limit=1).id
                else:
                    parent_id = self.env['hr.employee'].search([
                        ('id', '=', department.parent_id.manager_id.id)
                    ],limit=1).id


                vals = {
                    'name': name,
                    'guid_1c': guid_1c,
                    'department_id': department_id,
                    'job_title': job_title,
                    'birthday': birthday,
                    'service_start_date': service_start_date,
                    'gender': gender,
                    'country_id': country_id,
                    'personal_email': personal_email,
                    'employment_type_1c': employment_type_1c,
                    'number_1c': number_1c,
                    'parent_id': parent_id,
                }

                if len(record_search)>0:
                    message_update += name + '\n'
                    record_search.write(vals)
                else:
                    n +=1
                    message_create += name + '\n'
                    record_search.create(vals)
            else:
                message_error += "Отсутствует обязательное поле в запси: %s \n" % line


        result ='Всего получено из ЗУП %s записей \n' % total_entries
        if not message_error == '':
            result = "\n Обновление прошло с предупреждениями: \n \n" + message_error
        else:
            result = "\n Обновление прошло успешно \n \n"

        if not message_create == '':
            result += "\n Создно %s новых Сотрудников: \n" % n
            result += message_create

        if not message_update == '':
            result += "\n Обновлены Сотрудники: \n" + message_update

        self.create_ad_log(result=result)

        return result

        