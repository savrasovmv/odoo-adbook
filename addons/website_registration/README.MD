

Для работы модуля 


Добавьте пользователя (шаблон), задать любое имя, выставить необходимые права. Сохранить, запомнить id

В Настройках - Системные параметры, добавить параметр
base.template_ad_user_id указать id шаблона для пользователя из AD

Теперь при создании пользователя при регистрации, если у него в сотруднике указана ссылка на пользователя AD 
будет создаваться из шаблона пользователя


ШАБЛОНЫ ПИСЕМ

Настройки - Технические - Шаблоны

найти запись  Регистрация, новый пользователь set_password_email запомнить ID

Настройки - Технические - Внешние Идентификаторы

Для записи auth_signup.set_password_email изменить ID из шаблона

