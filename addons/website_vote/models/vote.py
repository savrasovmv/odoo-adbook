from odoo import fields, models, api
from odoo import tools
from odoo.tools import html2plaintext
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

    is_reg = fields.Boolean(string='Регистрация на сайте', help="Если установлена, разрешает участникам регистрацию на сайте")

    type = fields.Selection([
        ('ideas', 'Идеи'),
        ('contest', 'Конкурс'),
    ], string='Тип')

    description = fields.Html(
        "Описание", translate=True, sanitize=False,  # TDE FIXME: find a way to authorize videos
        help="Описание Голосования, которое будет отображаться на странице голосования")


    description_text = fields.Text(
        "Описание", translate=True, sanitize=False,  # TDE FIXME: find a way to authorize videos
        help="Описание Голосования в текстовом формате, которое будет отображаться на главной странице голосования",
        compute="get_description_text"
        )

    conditions = fields.Html(
        "Условия", translate=True, sanitize=False,  # TDE FIXME: find a way to authorize videos
        help="Условия участия, которое будет отображаться на странице регистрации")

    description_votes = fields.Html(
        "Условия голосования", translate=True, sanitize=False,  # TDE FIXME: find a way to authorize videos
        help="Описание для голосующих, которое будет отображаться на странице голосования в период голосования")

    description_winner_item = fields.Html(
        "Подпись к победившим работам ", translate=True, sanitize=False,  # TDE FIXME: find a way to authorize videos
        help="Подпись к победившим работам, которое будет отображаться над блоком списка победивших работ",
        default="<h5>Лучшие работы</h5>"
        )
    description_winner_participant = fields.Html(
        "Подпись к победившим участникам ", translate=True, sanitize=False,  # TDE FIXME: find a way to authorize videos
        help="Подпись к победившим участникам, которое будет отображаться над блоком списка победивших участников",
        default="<h5>Лучшие участники</h5>"
        )
    
    background_image = fields.Binary("Изображение")
    state = fields.Selection(selection=[
            ('draft', 'Черновик'), 
            ('reg', 'Регистрация'), 
            ('vote', 'Голосование'), 
            ('closed', 'Закрыто')
        ], string="Статус", default='draft', required=True,
    )

    user_id = fields.Many2one('res.users', string='Организатор', required=False, default=lambda self: self.env.user)

    numder_votes = fields.Integer(string='Кол-во голосов', help="Сколько раз можно проголосовать (выбрать несколько) голосующему", default=1)

    numder_winner = fields.Integer(string='Итого победителей', help="Сколько участников будут награждены", readonly=True, compute='_get_winner', store=True)
    numder_winner_item = fields.Integer(string='Лучшая работа', help="Сколько участников будут награждены за лучшую работу", default=1)
    numder_winner_participant = fields.Integer(string='Лучший участник', help="Сколько участников будут награждены за сумму голосов по всем работам", default=1)

    numder_files = fields.Integer(string='Кол-во работ', help="Количество работ участника", default=1)




    active = fields.Boolean(string='Активна', default=True)

    vote_vote_participant = fields.One2many('vote.vote_participant', 'vote_vote_id', string=u"Участники")
    vote_vote_participant_item = fields.One2many('vote.vote_participant_item', 'vote_vote_id', string=u"Работы Участников")
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

    @api.depends("numder_winner_item", "numder_winner_participant")
    def _get_winner(self):
        for line in self:
            line.numder_winner = line.numder_winner_item + line.numder_winner_participant

    @api.depends("conditions")
    def get_description_text(self):
        for line in self:
            line.description_text = html2plaintext(line.description).replace('\n', ' ')[:200] + '...'

    



            

class VoteParticipant(models.Model):
    _name = "vote.vote_participant"
    _description = "Зарегистрированные Участники"
    _order = "name"

    name = fields.Char(u'Наименование', compute="_get_name", stote=True)
    users_id = fields.Many2one("res.users", string="Пользователь")
    employee_id = fields.Many2one("hr.employee", string="Сотрудник")

    vote_vote_id = fields.Many2one('vote.vote',
		ondelete='cascade', string=u"Голосования", required=True)
    
    
    description = fields.Text( "Описание", translate=True, sanitize=False)
    number_item = fields.Integer(string='Число работ', compute='get_item', store=True)

    score = fields.Integer(string='Набранно голосов', compute='get_score', store=True)

    vote_vote_participant_item = fields.One2many('vote.vote_participant_item', 'participant_id', string=u"Работы Участников")


    # mimetype = fields.Char(
    #     compute="_compute_mimetype", string="Type", readonly=True, store=True
    # )

    @api.model
    def create(self, vals):
        if vals['employee_id'] == '' or vals['employee_id'] == False :
            empl = self.env['hr.employee'].sudo().search([
                ('user_id', '=', vals['users_id']),
            ], limit=1)
            if len(empl)>0:
                vals['employee_id'] = empl.id
            
        return super(VoteParticipant, self).create(vals)

    @api.depends("users_id", "employee_id")
    def _get_name(self):
        for line in self:
            if line.users_id:
                line.name = line.users_id.name 
            if line.employee_id:
                line.name = line.employee_id.name 

    @api.depends("vote_vote_id.vote_vote_voting")
    def get_score(self):
        for participant in self:
            voting_list = self.env['vote.vote_voting'].search([('vote_vote_participant_id', '=', participant.id)])
            participant.score = sum(line['score'] for line in voting_list)

    @api.depends("vote_vote_participant_item")
    def get_item(self):
        for participant in self:
            # item = self.env['vote.vote_participant_item'].search([('participant_id', '=', participant.id)])
            participant.number_item = len(participant.vote_vote_participant_item)
            


class VoteParticipantItem(models.Model):
    _name = "vote.vote_participant_item"
    _description = "Работы Участников"
    _order = "name"


    name = fields.Char(u'Наименование', compute="_get_name", store=True)
    employee_id = fields.Many2one("hr.employee", string="Сотрудник")

    users_id = fields.Many2one("res.users", string="Пользователь")
    vote_vote_id = fields.Many2one('vote.vote', ondelete='cascade', string=u"Голосования", required=True)

    participant_id = fields.Many2one("vote.vote_participant", ondelete='cascade', string="Участник")
                #    domain="[('id', 'in', vote_vote_id.vote_vote_participant.ids)]")
    # participant_list

    
    file = fields.Binary('Файл', default=None)
    file_text = fields.Char(string='Подпись к файлу')

    image_1920 = fields.Image("image_1920",compute="_get_default_image", store=True, readonly=True)
    image_128 = fields.Image("Image_128", max_width=128, max_height=128, compute='_get_default_image', store=True, readonly=True)

    score = fields.Integer(string='Набранно голосов', compute='get_score', store=True)

    vote_vote_voting = fields.One2many('vote.vote_voting', 'vote_vote_participant_item_id', string=u"Участники голосования")

    

    @api.model
    def create(self, vals):
        if vals['employee_id'] == '' or vals['employee_id'] == False :
            empl = self.env['hr.employee'].sudo().search([
                ('user_id', '=', vals['users_id']),
            ], limit=1)
            if len(empl)>0:
                vals['employee_id'] = empl.id
        return super(VoteParticipantItem, self).create(vals)


    @api.depends("file_text", "employee_id")
    def _get_name(self):
        for line in self:
            if line.file_text:
                line.name = str(line.employee_id.name) + " (" + str(line.file_text) + ")" 
            else:
                line.name = line.employee_id.name + "(без имени)"

    @api.depends("file")
    def _get_default_image(self):
        if self.file:
            self.image_128 = self.file
            self.image_1920 = self.file

    @api.depends("vote_vote_id.vote_vote_voting")
    def get_score(self):
        for item in self:
            voting_list = self.env['vote.vote_voting'].search([('vote_vote_participant_item_id', '=', item.id)])
            item.score = sum(line['score'] for line in voting_list)


    


class VoteVoting(models.Model):
    _name = "vote.vote_voting"
    _description = "Участники голосования"
    _order = "name"


    name = fields.Char(u'Наименование', compute="_get_name", store=True)
    users_id = fields.Many2one("res.users", string="Пользователь")
    employee_id = fields.Many2one("hr.employee", string="Сотрудник")


    vote_vote_id = fields.Many2one('vote.vote',
		ondelete='cascade', string=u"Голосования", required=True)
    
    vote_vote_participant_id = fields.Many2one('vote.vote_participant', string=u"Участник",)
                                                # search="[('vote_vote_id', '=', vote_vote_id)]")
    vote_vote_participant_item_id = fields.Many2one('vote.vote_participant_item', ondelete='cascade', string=u"Работа Участника")
   
    score = fields.Integer(string='Голос', default=1)



    @api.depends("users_id")
    def _get_name(self):
        for line in self:
            if line.users_id:
                line.name = line.users_id.name 
    
    @api.model
    def create(self, vals):
        if vals['employee_id'] == '' or vals['employee_id'] == False :
            empl = self.env['hr.employee'].sudo().search([
                ('user_id', '=', vals['users_id']),
            ], limit=1)
            if len(empl)>0:
                vals['employee_id'] = empl.id
        return super(VoteVoting, self).create(vals)

    

  