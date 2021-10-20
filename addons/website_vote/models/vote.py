from odoo import fields, models, api
from odoo import tools
import base64




class Vote(models.Model):
    _name = "vote.vote"
    _description = "Голосования"
    _order = "name"

    name = fields.Char(u'Наименование', required=True)
    date_start = fields.Date(string='Начало голосования')
    date_end = fields.Date(string='Окончание голосования')
    reg_date_start = fields.Date(string='Начало регистрации')
    reg_date_end = fields.Date(string='Окончание регистрации')

    is_reg = fields.Boolean(string='Регистрация', help="Если установлена, разрешает участникам регистрацию на сайте")

    type = fields.Selection([
        ('ideas', 'Идеи'),
        ('contest', 'Конкурс'),
    ], string='Тип')

    description = fields.Html(
        "Описание", translate=True, sanitize=False,  # TDE FIXME: find a way to authorize videos
        help="Описание Голосования, которое будет отображаться на странице голосования")

    conditions = fields.Html(
        "Условия", translate=True, sanitize=False,  # TDE FIXME: find a way to authorize videos
        help="Условия участия, которое будет отображаться на странице регистрации")

    description_votes = fields.Html(
        "Условия голосования", translate=True, sanitize=False,  # TDE FIXME: find a way to authorize videos
        help="Описание для голосующих, которое будет отображаться на странице голосования в период голосования")
    
    background_image = fields.Binary("Изображение")
    state = fields.Selection(selection=[
            ('draft', 'Черновик'), 
            ('reg', 'Регистрация'), 
            ('vote', 'Голосование'), 
            ('closed', 'Закрыто')
        ], string="Статус", default='draft', required=True,
    )

    user_id = fields.Many2one('res.users', string='Организатор', required=False, default=lambda self: self.env.user)

    numder_votes = fields.Integer(string='Кол-во голосов', help="Сколько раз можно проголосовать (выбрать несколько)", default=1)


    active = fields.Boolean(string='Активна', default=True)

    vote_vote_participant = fields.One2many('vote.vote_participant', 'vote_vote_id', string=u"Зарегистрированные Участники")
    vote_vote_voting = fields.One2many('vote.vote_voting', 'vote_vote_id', string=u"Участники голосования")


    def button_draft(self):
        for line in self:
            line.state = "draft"
    
    def button_reg(self):
        for line in self:
            line.state = "reg"

    def button_vote(self):
        for line in self:
            line.state = "vote"

    def button_closed(self):
        for line in self:
            line.state = "closed"

class VoteParticipant(models.Model):
    _name = "vote.vote_participant"
    _description = "Зарегистрированные Участники"
    _order = "name"

    name = fields.Char(u'Наименование', compute="_get_name")
    users_id = fields.Many2one("res.users", string="пользователь")
    employee_id = fields.Many2one("hr.employee", string="Сотрудник")

    vote_vote_id = fields.Many2one('vote.vote',
		ondelete='cascade', string=u"Голосования", required=True)
    
    text_idea = fields.Text(string='Текст идеи')
    file = fields.Binary('Файл', default=None)
    file_text = fields.Char(string='Подпись к файлу')
    description = fields.Text( "Описание", translate=True, sanitize=False)

    image_1920 = fields.Image("image_1920",compute="_get_default_image", store=True, readonly=True)
    image_128 = fields.Image("Image_128", max_width=128, max_height=128, compute='_get_default_image', store=True, readonly=True)
    # mimetype = fields.Char(
    #     compute="_compute_mimetype", string="Type", readonly=True, store=True
    # )

    @api.depends("users_id", "employee_id")
    def _get_name(self):
        for line in self:
            if line.users_id:
                line.name = line.users_id.name 
            if line.employee_id:
                line.name = line.employee_id.name 

    @api.depends("file")
    def _get_default_image(self):
        if self.file:
            self.image_128 = self.file
            self.image_1920 = self.file
    


class VoteVoting(models.Model):
    _name = "vote.vote_voting"
    _description = "Участники голосования"
    _order = "name"

    name = fields.Char(u'Наименование', compute="_get_name")
    users_id = fields.Many2one("res.users", string="пользователь")

    vote_vote_id = fields.Many2one('vote.vote',
		ondelete='cascade', string=u"Голосования", required=True)
    
    vote_vote_participant = fields.Many2one('vote.vote_participant', string=u"Зарегистрированные Участники")
   
    score = fields.Integer(string='Голос', default=1)



    @api.depends("users_id")
    def _get_name(self):
        if self.users_id:
            self.name = self.users_id.name 
    
    @api.model
    def create(self, vals):
        if 'file' in vals:
            vals['file_small'] = tools.image_resize_image_small(base64.b64encode(vals['file_small']))

        # print("==============", vals)  
        return super(VoteVoting, self).create(vals)

    

  