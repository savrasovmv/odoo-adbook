from odoo import fields, models, api
from ldap3 import Server, Connection, SUBTREE, MODIFY_REPLACE, LEVEL
import json
import base64
from io import StringIO
import csv
from datetime import datetime


def get_date(date_text):
    """Возвращает форматированную дату если она не пуста, т.е не равна 0001-01-01T00:00:00"""
    date = False
    print('date_text=',date_text)

    if date_text != '0001-01-01T00:00:00' and date_text !='':
        print('date_text=',date_text)
        date = datetime.strptime(date_text, '%d.%m.%Y %H:%M:%S').date()
    print(date_text, date)
    return date

class HrImportCSV(models.TransientModel):
    _name = 'hr.import_csv'
    _description = "Wizard Загрузка данных из csv"

    result = fields.Text(string='Результат')
    type = fields.Selection([
        ('department', 'Подразделения'),
        ('employee', 'Сотрудники')
    ], string='Тип загрузки')

    file = fields.Binary(u'Импортировать файл')

    department_id = fields.Many2one("hr.department", string="Подразделение", help="Подразделение в котором будут создаваться записи")

    def return_result(self, error=False):
        """Возвращает ошибку или результат выполнения действия"""

        if error:
            notification = {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': ('Прерванно'),
                    'message': error,
                    'type':'warning',  #types: success,warning,danger,info
                    'sticky': False,  #True/False will display for few seconds if false
                },
            }
            return notification
        else:
            return {
				'name': 'Wizard',
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'hr.import_csv',
				'target':'new',
				'context':{
							'default_result':self.result,
							} 
				}


    def import_department(self, line):
        """Импорт подразделения. line = [Наименование, guid, parent_guid]"""
        
        if len(line) != 3:
            return False

        name = line[0]
        guid = line[1]
        parent_guid = line[2]

        dep = self.env['hr.department'].search([
            ('guid_1c', '=', guid),
            '|',
            ('active', '=', True),
            ('active', '=', False),

        ], limit=1)

        parent_dep = False

        if parent_guid == '00000000-0000-0000-0000-000000000000':
            parent_dep = self.department_id
        else:
            parent_dep = self.env['hr.department'].search([
                ('guid_1c', '=', parent_guid),
                '|',
                ('active', '=', True),
                ('active', '=', False),
            ])

        if not parent_guid or len(parent_guid) == 0:
            parent_guid = self.department_id


        vals = {
            'name': name,
            'guid_1c': guid,
            'parent_id': parent_dep.id if len(parent_dep)>0 else False,
            'active': True
        }

        if len(dep)>0:
            dep.write(vals)
        else:
            self.env['hr.department'].create(vals)


    def import_employee(self, line):
        """Импорт сотрудников. line = [guid, department_guid, ФИО, Должность, Подразделение(наименование), Пол, ДатаРождение, ДатаПриема, ВидЗнятости]"""
        
        if len(line) != 9:
            return False

        guid = line[0]
        department_guid = line[1]
        name = line[2]
        job_title = line[3]
        department_name = line[4]
        gender = 'male' if line[5]=='Мужской' else 'female'
        birthday = line[6]
        service_start_date = line[7]
        employment_type_1c = line[8]

        print("Создание/Обновление: ", name)

        empl = self.env['hr.employee'].search([
            ('guid_1c', '=', guid),
            '|',
            ('active', '=', True),
            ('active', '=', False),
        ])

        dep = self.env['hr.department'].search([
            ('guid_1c', '=', department_guid),
            '|',
            ('active', '=', True),
            ('active', '=', False),
        ])

        vals = {
            'guid_1c': guid,
            'department_id': dep.id if len(dep)>0 else self.department_id.id,
            'name': name,
            'job_title': job_title,
            'gender': gender,
            'birthday': get_date(birthday),
            'service_start_date': get_date(service_start_date),
            'employment_type_1c': employment_type_1c,
            'active': True
        }

        if len(empl)>0:
            empl.write(vals)
        else:
            self.env['hr.employee'].create(vals)



    def import_file_wizard_action(self):

        if not self.file:
            return self.return_result(error="Не выбран файл")
        if not self.type:
            return self.return_result(error="Не выбран тип импортируемой информации")
        if not self.department_id:
            return self.return_result(error="Не выбрано подразделение по умолчанию")

        tmp_file_name = '/tmp/hr_import.csv'
        file_content = base64.b64decode(self.file) 
        file_string = file_content.decode('Windows-1251') 
        data_file_p = open(tmp_file_name,'w')

        data_file_p.write(file_string)
        with open(tmp_file_name) as File:
            reader = csv.reader(File, delimiter=';', quotechar=';',
                                quoting=csv.QUOTE_MINIMAL)
            if self.type == 'department':
                i = 0
                for row in reader:
                    i+=1
                    if i==1: continue # Пропуск первой строки
                    self.import_department(row)
                # Второй проходд для выставления родителей
                i = 0
                for row in reader:
                    i+=1
                    if i==1: continue
                    self.import_department(row)
            
            if self.type == 'employee':
                print("+++++ type == 'employee'")
                i = 0
                for row in reader:
                    i+=1
                    if i==1: continue
                    print(row)
                    self.import_employee(row)
            
       
        self.result = True
                
        return self.return_result()
