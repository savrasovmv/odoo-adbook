
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
        _logger.info("Получены данные из ЗУП, в кол-ве: %s" % total_entries)
        #return total_entries, data
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




class ZupSyncDep(models.AbstractModel):
    _name = 'zup.sync_dep'
    _description = 'Синхронизация подразделений ЗУП'
    _inherit = ['zup.connect']
  

    def zup_sync_dep(self):
        """Загрузка информации по подразделениям из ЗУП"""
        date = datetime.today()
        URL_API = self.env['ir.config_parameter'].sudo().get_param('zup_url_get_dep_list')
        if not URL_API:
            raise Exception("Не заполнен параметр zup_url_get_dep_list")

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
            raise Exception('Ошибка. Данные не получены')
        
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

class ZupSyncEmployer(models.AbstractModel):
    _name = 'zup.sync_employer'
    _description = 'Синхронизация сотрудников ЗУП'
    _inherit = ['zup.connect']

    def zup_sync_employer(self):
        """Загрузка информации по Сотрудникам из ЗУП"""
        date = datetime.today()
        URL_API = self.env['ir.config_parameter'].sudo().get_param('zup_url_get_empl_list')
        if not URL_API:
            raise Exception("Не заполнен параметр zup_url_get_empl_list")

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
            raise Exception('Ошибка. Данные не получены')
        
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


class ZupSyncPassport(models.AbstractModel):
    _name = 'zup.sync_passport'
    _description = 'Синхронизация документов УЛ и адресов ЗУП'
    _inherit = ['zup.connect']

    def zup_sync_passport(self):
        """Загрузка информации по удостоверениям личности и адресам Сотрудников из ЗУП
            Пример ответа:
            {'dataType': 'identityDocumentList', 
		'discription': '', 
		'data': [
					{'employeeGuid1C': 'c3c66a3c-17c2-11e0-86c5-00155d003102', 
					'documentType': 'Паспорт гражданина РФ', 
					'country': '', 
					'series': '71 11', 
					'number': '860325', 
					'issuedBy': 'Территориальным пунктом УФМС России по Тюменской обл. в Нижнетавдинском районе', 
					'departamentCode': '720-016', 
					'issueDate': '2011-05-31T00:00:00', 
					'validUntil': '0001-01-01T00:00:00', 
					'birthPlace': '0,Комсомолец,Комсомольский,Кустанайская,Россия', 
					'registrationAddress': {
											'value': '626020, Тюменская обл, Нижнетавдинский р-н, Нижняя Тавда с, Ульянова ул, дом № 12', 
											'comment': '', 
											'type': 'Адрес', 
											'Country': 'РОССИЯ', 
											'addressType': 'Административно-территориальный', 
											'CountryCode': '643', 
											'ZIPcode': '626020', 
											'area': 'Тюменская', 
											'areaType': 'обл', 
											'city': '', 
											'cityType': '', 
											'street': 'Ульянова', 
											'streetType': 'ул', 
											'id': '', 
											'areaCode': '', 
											'areaId': '', 
											'district': 'Нижнетавдинский', 
											'districtType': 'р-н', 
											'districtId': '', 
											'munDistrict': '', 
											'munDistrictType': '', 
											'munDistrictId': '', 
											'cityId': '', 
											'settlement': '', 
											'settlementType': '', 
											'settlementId': '', 
											'cityDistrict': '', 
											'cityDistrictType': '', 
											'cityDistrictId': '', 
											'territory': '', 
											'territoryType': '', 
											'territoryId': '', 
											'locality': 'Нижняя Тавда', 
											'localityType': 'с', 
											'localityId': '', 
											'streetId': '', 
											'houseType': 'Дом', 
											'houseNumber': '12', 
											'houseId': '', 
											'buildings': [], 
											'apartments': [{
															'type': 'Квартира', 
															'number': '69'
															}],
											'codeKLADR': '', 
											'oktmo': '', 
											'okato': '', 
											'asInDocument': '', 
											'ifnsFLCode': '', 
											'ifnsULCode': '', 
											'ifnsFLAreaCode': '', 
											'ifnsULAreaCode': ''}, 
					'residenceAddress': ''
				}, ]
		}

        
        """
        date = datetime.today()
        URL_API = self.env['ir.config_parameter'].sudo().get_param('zup_url_get_passport_list')
        if not URL_API:
            raise Exception("Не заполнен параметр zup_url_get_passport_list")

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
            raise Exception('Ошибка. Данные не получены')
        
        if total_entries == 0:
            result = "Новых данных нет"
            self.create_ad_log(result=result)
            return result
        
        n = 0
        message_error = ''
        message_update = ''
        message_create = ''
        
        for line in data:
            # print(line)
            if 'employeeGuid1C' in line:
                guid_1c = line['employeeGuid1C'] # Идентификатор сотрудника
                
                record_search = self.env['hr.employee'].search([
                    ('guid_1c', '=', guid_1c)
                ],limit=1)
                if len(record_search) == 0:
                    message_error += "не найден сотрудник с gud1c %s \n" % guid_1c
                    continue # Переход к следующей записи
                
                passport_type = line['documentType'] 
                passport_country = line['country'] 
                if passport_country == '':
                    passport_country = record_search.country_id.name
                passport_series = line['series'] 
                passport_number = line['number'] 
                passport_issued_by = line['issuedBy'] 
                passport_department_code = line['departamentCode'] 

                # Дата выдачи
                passport_date_issue = None
                passport_date_issue_text = line['issueDate']
                if passport_date_issue_text != '' and passport_date_issue_text != '0001-01-01T00:00:00':
                    passport_date_issue = datetime.strptime(passport_date_issue_text, '%Y-%m-%dT%H:%M:%S').date()
                
                # Срок действия
                passport_date_validity = None
                passport_date_validity_text = line['validUntil'] 
                if passport_date_validity_text != '' and passport_date_validity_text != '0001-01-01T00:00:00':
                    passport_date_validity = datetime.strptime(passport_date_validity_text, '%Y-%m-%dT%H:%M:%S').date()
                
                # Место рождения
                passport_place_birth = line['birthPlace'] 

                vals = {
                    'passport_type': passport_type,
                    'passport_country': passport_country,
                    'passport_series': passport_series,
                    'passport_number': passport_number,
                    'passport_issued_by': passport_issued_by,
                    'passport_department_code': passport_department_code,
                    'passport_date_issue': passport_date_issue,
                    'passport_date_validity': passport_date_validity,
                    'passport_place_birth': passport_place_birth,
                }



                
                reg_adr = line['registrationAddress'] 
                fact_adr = line['residenceAddress'] 

                adr_list_param = [
                    {'name':'full', 'key':'value'},
                    {'name':'zipcode', 'key':'ZIPcode'},
                    {'name':'area_type', 'key':'areaType'},
                    {'name':'area', 'key':'area'},
                    {'name':'district_type', 'key':'districtType'},
                    {'name':'district', 'key':'district'},
                    {'name':'city_type', 'key':'cityType'},
                    {'name':'city', 'key':'city'},
                    {'name':'locality_type', 'key':'localityType'},
                    {'name':'locality', 'key':'locality'},
                    {'name':'mun_district_type', 'key':'munDistrictType'},
                    {'name':'mun_district', 'key':'munDistrict'},
                    {'name':'settlement_type', 'key':'settlementType'},
                    {'name':'settlement', 'key':'settlement'},
                    {'name':'city_district_type', 'key':'cityDistrictType'},
                    {'name':'city_district', 'key':'cityDistrict'},
                    {'name':'territory_type', 'key':'territoryType'},
                    {'name':'territory', 'key':'territory'},
                    {'name':'street_type', 'key':'streetType'},
                    {'name':'street', 'key':'street'},
                    {'name':'house_type', 'key':'houseType'},
                    {'name':'house', 'key':'houseNumber'},
                    {'name':'stead', 'key':'stead'},
                ]
                    # {'buildings_type':''},
                    # {'buildings':''},
                    # {'apartments_type':''},
                    # {'apartments':''},

                if len(reg_adr) > 0:

                    for param in adr_list_param:
                        vals['ra_%s' % param['name']] = reg_adr[param['key']] if param['key'] in reg_adr else ''
                    
                    buildings_text = reg_adr['buildings'] if 'buildings' in reg_adr else ''
                    if len(buildings_text) > 0:
                        vals['ra_buildings_type'] = buildings_text[0]['type']
                        vals['ra_buildings'] = buildings_text[0]['number']
                    
                    apartments_text = reg_adr['apartments'] if 'apartments' in reg_adr else ''
                    if len(apartments_text) > 0:
                        vals['ra_apartments_type'] = apartments_text[0]['type']
                        vals['ra_apartments'] = apartments_text[0]['number']
                    
                
                if len(fact_adr) > 0:

                    for param in adr_list_param:
                        vals['fa_%s' % param['name']] = fact_adr[param['key']] if param['key'] in fact_adr else ''

                    buildings_text = fact_adr['buildings'] if 'buildings' in fact_adr else ''
                    if len(buildings_text) > 0:
                        vals['fa_buildings_type'] = buildings_text[0]['type']
                        vals['fa_buildings'] = buildings_text[0]['number']
                    
                    apartments_text = fact_adr['apartments'] if 'apartments' in fact_adr else ''
                    if len(apartments_text) > 0:
                        vals['fa_apartments_type'] = apartments_text[0]['type']
                        vals['fa_apartments'] = apartments_text[0]['number']


                print(guid_1c) 
                print(vals) 
                message_update += record_search.name + '\n'
                record_search.write(vals)
                
            else:
                message_error += "Отсутствует обязательное поле в запси: %s \n" % line


        result ='Всего получено из ЗУП %s записей \n' % total_entries
        if not message_error == '':
            result = "\n Обновление прошло с предупреждениями: \n \n" + message_error
        else:
            result = "\n Обновление прошло успешно \n \n"

        _logger.info(result)

        if not message_update == '':
            result += "\n Обновлены Документы УЛ и адреса сотрудников: \n" + message_update

        self.create_ad_log(result=result)

        return result

        