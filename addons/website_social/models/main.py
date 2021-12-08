from odoo import fields, models, api
from odoo import tools
from odoo.tools import html2plaintext
import base64




class Social(models.Model):
    _name = "social.social"
    _description = "Сообщества"
    _inherit = ['mail.thread', 'image.mixin', 'website.seo.metadata', 'website.multi.mixin']
    _order = "name"

    name = fields.Char(u'Наименование', required=True)
    subtitle = fields.Char('Подзаголовок', translate=True)

    description = fields.Html(
        "Описание", translate=True, sanitize=False,  # TDE FIXME: find a way to authorize videos
        help="Описание Сообщества, которое будет отображаться на странице Сообщества")

    social_post_count = fields.Integer("Посты", compute='_compute_social_post_count')

    # background_image = fields.Binary("Изображение")

    # state = fields.Selection(selection=[
    #         ('draft', 'Черновик'), 
    #         ('opened', 'Открыто'), 
    #         ('closed', 'Закрыто')
    #     ], string="Статус", default='draft', required=True,
    # )

    user_id = fields.Many2one('res.users', string='Автор', required=False, default=lambda self: self.env.user)

    active = fields.Boolean(string='Активна', default=True)

    social_post_ids = fields.One2many('social.post', 'social_id', 'Посты сообщества')


    @api.depends('social_post_ids')
    def _compute_social_post_count(self):
        for record in self:
            record.social_post_count = len(record.social_post_ids)



            

class SocialPost(models.Model):
    _name = "social.post"
    _description = "Сообщества. Посты"
    _inherit = ['mail.thread', 'website.seo.metadata', 'website.published.multi.mixin', 'website.cover_properties.mixin']
    _order = 'id DESC'

    name = fields.Char(u'Заголовок', required=True, translate=True, default='')
    subtitle = fields.Char('Подзаголовок', translate=True)
    author_id = fields.Many2one('res.partner', 'Автор', default=lambda self: self.env.user.partner_id)
    author_avatar = fields.Binary(related='author_id.image_128', string="Avatar", readonly=False)
    author_name = fields.Char(related='author_id.display_name', string="Автор ФИО", readonly=False, store=True)
    active = fields.Boolean('Активно', default=True)
    content = fields.Html("Контент", required=True)
    
    partner_id = fields.Many2one('res.partner', string='Для кого')

    social_comments_ids = fields.One2many('social.comments', 'social_post_id', string=u"Комментарии к посту")
    social_comments_count = fields.Integer("Кол-во комментариев", compute='_compute_social_comments_count')


    social_id = fields.Many2one('social.social', ondelete='cascade', string=u"Сообщество", required=True)

    @api.depends("users_id")
    def _get_name(self):
        for line in self:
            if line.users_id:
                line.name = line.users_id.name 

    @api.depends('social_comments_ids')
    def _compute_social_comments_count(self):
        for record in self:
            record.social_comments_count = len(record.social_comments_ids)
           
                


class SocialComments(models.Model):
    _name = "social.comments"
    _description = "Сообщества. Комментарии к постам"
    _order = "name"


    name = fields.Char(related='author_id.display_name', string="Наименование", readonly=False, store=True)
    author_id = fields.Many2one('res.partner', 'Автор', default=lambda self: self.env.user.partner_id)
    author_avatar = fields.Binary(related='author_id.image_128', string="Avatar", readonly=False)
    author_name = fields.Char(related='author_id.display_name', string="Автор ФИО", readonly=False, store=True)
    active = fields.Boolean('Активно', default=True)
    content = fields.Html("Контент", required=True)
    parent_id = fields.Many2one('social.comments', string='Комментарий', ondelete='cascade', readonly=True, index=True)



    social_post_id = fields.Many2one('social.post', ondelete='cascade', string=u"Пост", required=True)
    social_id = fields.Many2one('social.social', ondelete='cascade', string=u"Сообщество", required=True)
    



    