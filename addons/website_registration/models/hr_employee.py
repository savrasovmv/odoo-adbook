from odoo import fields, models, api, _


from ast import literal_eval
import logging

_logger = logging.getLogger(__name__)

VALIDATION_KARMA_GAIN = 3

class HrEmployee(models.Model):
    """Добавляет возможность создания партнера и пользователя из сотрудника"""
    _inherit = "hr.employee"


    @api.model
    def reg_create_user(self):
        self.ensure_one()

        email = self.get_registration_email()
        if not email:
            err = "Нет электронного адреса"
            _logger.warning("Ошибка при создании пользователя  %s, ОШИБКА: %s" % (self.name, err))
            raise ValueError(str(err))
        if self.user_id:
            err = "Пользователь уже зарегистрирован"
            _logger.warning("Ошибка при создании пользователя  %s, ОШИБКА: %s" % (self.name, err))
            raise ValueError(str(err))

        mobile = self.mobile_phone if self.mobile_phone else ''
        mobile += ' ' + self.mobile_phone2 if self.mobile_phone2 else ''

        _logger.debug("Создание партнера для %s" % self.name)

        partner_vals = {
            'name': self.name,
            'parent_id': self.company_id.partner_id.id,
            'company_id': self.company_id.id,
            'company_type': 'person',
            'email': email,
            'function': self.job_title,
            'phone': self.ip_phone,
            'mobile': mobile,
            'employee': True,
            'image_1920': self.image_1920,
        }

        part_search = self.env['res.partner'].search([
            ('name', '=', self.name),
            ('email', '=', email)
        ], limit=1)
        

        if len(part_search)>0:
            part_search.write(partner_vals)
            new_partner = part_search
        else:
            new_partner = self.env['res.partner'].create(partner_vals)

        _logger.debug("Создание пользователя для %s" % email)
        user_vals = {
            'login': email,
            'partner_id': new_partner.id,
            'active': True,
            'karma': VALIDATION_KARMA_GAIN,
        }

        user_search = self.env['res.users'].search([
            ('login', '=', email)
        ], limit=1)
        if len(user_search)>0:
            user_search.write(user_vals)
            new_user = user_search
        else:
            # Если сотрудник связан с пользователем AD
            if self.users_id:
                template_user_id = literal_eval(self.env['ir.config_parameter'].sudo().get_param('base.template_ad_user_id', 'False'))
            else:
                template_user_id = literal_eval(self.env['ir.config_parameter'].sudo().get_param('base.template_portal_user_id', 'False'))
            
            template_user = self.env['res.users'].browse(template_user_id)
            if not template_user.exists():
                raise ValueError(_('Signup: invalid template user'))
            

            # create a copy of the template user (attached to a specific partner_id if given)
            try:
                with self.env.cr.savepoint():
                    new_user =  template_user.with_context(no_reset_password=True, create_user=True).copy(user_vals)
                    new_user.with_context(create_user=True).action_reset_password()
                    _logger.debug("Пользователь создан  %s" % (email))

            except Exception as e:
                # copy may failed if asked login is not available.
                _logger.warning("Ошибка при создании пользователя  %s, ОШИБКА: %s" % (email, str(e)))
                raise ValueError(str(e))
                # new_user = self.env['res.users'].create(user_vals)
        
        if new_user:
            self.user_id = new_user.id

    @api.model
    def set_users_default_karma(self):
        """Устанавливает всем пользователям карму 3 для отключения предупреждения о валидации почты"""
        users = self.env['res.users'].sudo().search([('karma', '=', 0)])
        for user in users:
            user.karma = VALIDATION_KARMA_GAIN




    # @api.model
    # def write(self, values):
    #     result = super(HrEmployee, self).write(values)
    #     self._reassign_user_id_partner(values)
    #     return result

    