from odoo import fields, models, api
from datetime import datetime

class AdbookBuild(models.AbstractModel):
    _name = 'adbook.build'
    _description = 'Создание/обновления справочника контактов'

    def adbook_build(self, full_sync=False):
        date_update = datetime.now()
        
        # ПОДРЗДЕЛЕНИЯ
        # ad_branch_list = self.env['ad.branch'].sudo().search([
        #                         ('active', '=', True),
        #                         ('is_view_adbook', '=', True),
        #                     ])

        # for ad_branch in ad_branch_list:
        #     search_branch = self.env['adbook.branch'].sudo().search([
        #                         ('ad_branch_id', '=', ad_branch.id),
        #                     ])
        #     if len(search_branch)>0:
        #         search_branch.write({
        #             'name': ad_branch.name,
        #             'ad_branch_id': ad_branch.id,
        #             'date_update': date_update,

        #         })
        #     else:
        #         self.env['adbook.branch'].sudo().create({
        #             'name': ad_branch.name,
        #             'adbook_name': ad_branch.name,
        #             'ad_branch_id': ad_branch.id,
        #             'date_update': date_update,

        #         })
        # # Удаляем записи которые небыли обновлены
        # self.env['adbook.branch'].sudo().search([
        #                         ('date_update', '<', date_update),
        #                         ('ad_branch_id', '!=', ''),
        #                     ]).unlink()
        ad_branch_list = self.env['ad.branch'].sudo().search([
                                ('active', '=', True),
                                ('is_view_adbook', '=', True),
                            ])
        for ad_branch in ad_branch_list:
            search_dep = self.env['adbook.department'].sudo().search([
                            ('ad_branch_id', '=', ad_branch.id),
                        ],limit=1)
            
            if len(search_dep)>0:
                dep_id = search_dep
                dep_vals = {
                    'name': ad_branch.name,
                    'company_id': ad_branch.company_id.id,
                    'ad_branch_id': ad_branch.id,
                    'date_update': date_update,
                }
                search_dep.write(dep_vals)
            else:
                dep_vals = {
                    'name': ad_branch.name,
                    'adbook_name': ad_branch.name,
                    'company_id': ad_branch.company_id.id,
                    'ad_branch_id': ad_branch.id,
                    'date_update': date_update,
                }
                dep_id = self.env['adbook.department'].sudo().create(dep_vals)
      


        # СОТРУДНИКИ

        ad_users_list = self.env['ad.users'].sudo().search([
                                ('active', '=', True),
                                ('is_view_adbook', '=', True),
                                ('branch_id', 'in', ad_branch_list.ids),
                            ])
        adbook_emloyer = self.env['adbook.employer'].sudo()
        for user in ad_users_list:
            search_emloyer = adbook_emloyer.search([
                                ('ad_users_id', '=', user.id),
                            ])
            hr_vals = {}

            if user.employee_id:
                hr_employer = user.employee_id
                hr_vals = {
                    'hr_employee_id': hr_employer.id,
                    'title': hr_employer.job_title,
                }

                # Добавить поиск по документам Отпус и прочее
            
            branch_id = self.env['adbook.branch'].sudo().search([
                                ('ad_branch_id', '=', user.branch_id.id),
                            ], limit=1).id

            ad_vals = {
                'name': user.name,
                'branch_id': branch_id,
                'title': user.title,
                'ip_phone': user.ip_phone,
                'phone': user.phone,
                'sec_phone': user.sec_phone,
                'email': user.email,
                'photo': user.photo,
                'ad_users_id': user.id,
                'date_update': date_update,
            }

            vals = {**ad_vals, **hr_vals}
            if search_emloyer:
                search_emloyer.write(vals)
            else:
                search_emloyer.create(vals)


        # Удаляем записи которые небыли обновлены
        adbook_emloyer.search([
                                ('date_update', '<', date_update),
                                ('ad_users_id', '!=', ''),
                            ]).unlink()

        
        print('----------Создание подразделений в сотрудниках')
        adbook_emloyer_list = adbook_emloyer.search([])
        department_list_ids = [] # Список актуальных записей, родителей которых нужно обновить
        for employer in adbook_emloyer_list:
            if employer.hr_employee_id:
                if employer.hr_employee_id.department_id:
                    search_dep = self.env['adbook.department'].sudo().search([
                                    ('hr_department_id', '=', employer.hr_employee_id.department_id.id),
                                ],limit=1)
                    
                    if len(search_dep)>0:
                        dep_id = search_dep
                        dep_vals = {
                            'name': employer.hr_employee_id.department_id.name,
                            'hr_department_id': employer.hr_employee_id.department_id.id,
                            'branch_id': employer.branch_id.id,
                            'date_update': date_update,

                        }
                        search_dep.write(dep_vals)
                    else:
                        dep_vals = {
                            'name': employer.hr_employee_id.department_id.name,
                            'adbook_name': employer.hr_employee_id.department_id.name,
                            'hr_department_id': employer.hr_employee_id.department_id.id,
                            'branch_id': employer.branch_id.id,
                            'date_update': date_update,

                        }
                        dep_id = self.env['adbook.department'].sudo().create(dep_vals)
                    
                    employer.department_id = dep_id.id
                    department_list_ids.append(dep_id.id)
                else:
                    search_dep = self.env['adbook.department'].sudo().search([
                                ('is_default', '=', True),
                            ],limit=1)
                    if len(search_dep)>0:
                        employer.department_id = search_dep.id

            elif employer.ad_users_id:
                print('employer', employer.name)
                search_dep = []
                if employer.ad_users_id.department_id:
                    search_dep = self.env['adbook.department'].sudo().search([
                                    ('ad_department_id', '=', employer.ad_users_id.department_id.id),
                                ],limit=1)
                
                    
                    if len(search_dep)>0:
                        dep_id = search_dep
                        dep_vals = {
                            'name': employer.ad_users_id.department_id.name,
                            'ad_department_id': employer.ad_users_id.department_id.id,
                            'branch_id': employer.branch_id.id,
                            'date_update': date_update,

                        }
                        
                        search_dep.write(dep_vals)
                    else:
                        dep_vals = {
                            'name': employer.ad_users_id.department_id.name,
                            'adbook_name': employer.ad_users_id.department_id.name,
                            'ad_department_id': employer.ad_users_id.department_id.id,
                            'branch_id': employer.branch_id.id,
                            'date_update': date_update,

                        }
                        print(dep_vals)
                        dep_id = self.env['adbook.department'].sudo().create(dep_vals)
                    
                    employer.department_id = dep_id.id
                    # department_list_ids.append(dep_id.id)
                else:
                    search_dep = self.env['adbook.department'].sudo().search([
                                ('is_default', '=', True),
                            ],limit=1)
                    if len(search_dep)>0:
                        employer.department_id = search_dep.id


        print('----------Обновляем родителей')
        
        # Обновляем родителей
        # dep_list = self.env['adbook.department'].sudo().browse(hr_department_list_ids)
        dep_list = self.env['adbook.department'].sudo().search([
                                    ('id', 'in', department_list_ids),
                                ])
        print(department_list_ids)
        print(dep_list)
        for dep in dep_list:
            print(dep.name)

            if not dep.hr_department_id:
                break

            hr_parent_id = dep.hr_department_id.parent_id
            i = 1
            while hr_parent_id:
                if i==1:
                    current_dep = dep
                
                print(str(i)+" - " + hr_parent_id.name)
                if hr_parent_id.is_view_adbook:
                    search_dep = self.env['adbook.department'].sudo().search([
                                    ('hr_department_id', '=', hr_parent_id.id),
                                ],limit=1)
                    
                    if len(search_dep)>0:
                        dep_id = search_dep
                        dep_vals = {
                            'name': hr_parent_id.name,
                            'hr_department_id': hr_parent_id.id,
                            'branch_id': dep.branch_id.id,
                            'date_update': date_update,

                        }
                        search_dep.write(dep_vals)
                        print('Обновил ', dep_id)

                    else:
                        dep_vals = {
                            'name': hr_parent_id.name,
                            'adbook_name': hr_parent_id.name,
                            'hr_department_id': hr_parent_id.id,
                            'branch_id': dep.branch_id.id,
                            'date_update': date_update,

                        }
                        dep_id = self.env['adbook.department'].sudo().create(dep_vals)
                        print('             Создал ', dep_id)
                    
                    
                    current_dep.parent_id = dep_id.id
                    hr_parent_id = hr_parent_id.parent_id
                    i+=1
                    current_dep = dep_id
                else:
                    break


        # Удаляем записи которые небыли обновлены
        self.env['adbook.department'].sudo().search([
                                ('date_update', '<', date_update),
                                '|',
                                ('hr_department_id', '!=', ''),
                                ('ad_department_id', '!=', ''),
                            ]).unlink()

        
        
        # НАЗНАЧЕНИЯ УРОВНЯ ОТДЕЛАМ
        dep_list = self.env['adbook.department'].sudo().search([])
        for dep in dep_list:
            level = 0
            dep_parent = dep.parent_id
            while dep_parent:
                level += 1
                dep_parent = dep_parent.parent_id

            dep.level = level

        
        return True