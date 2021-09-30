from odoo import fields, models, api

class AdbookBuildWizard(models.TransientModel):
    _name = 'adbook.build_wizard'
    _description = 'Создание/обновления справочника контактов'

    result = fields.Char(string='Результат')


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
				'name': 'Message',
				'type': 'ir.actions.act_window',
				'view_type': 'form',
				'view_mode': 'form',
				'res_model': 'adbook.build_wizard',
				'target':'new',
				'context':{
							'default_result':self.result,
							} 
				}

    def adbook_build_wizard_action(self):
        #res = self.ad_sync_group_action()
        # self.result = self.env['adbook.build'].sudo().adbook_build()

        try:
            self.result = self.env['adbook.build'].sudo().adbook_build()
        except Exception as error:
            return self.return_result(error=error)
        
        return self.return_result()

    