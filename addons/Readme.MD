ЗАвисимости
openpyxl

sudo su - odoo -s /bin/bash

user@mint:~/pro$ sudo chmod ugo=rwx -R odoo-test/
user@mint:~/pro$ sudo chown user:user -R odoo-test/\*


Создать пустой проект
======================
./odoo-bin scaffold nameAddons /addons-path/
или
odoo scaffold nameAddons /addons-path/


Logger
=======
import logging
_logger = logging.getLogger(__name__)

В функциях
        _logger.debug("IT IS DEBUG")
    	_logger.info("IT IS INFO")
    	_logger.error("IT IS Error")
    	_logger.warning("IT IS warn")
    	_logger.critical("IT IS Critical")


Tree цвета
===========
<tree decoration-danger="count_sync_field == 0">
decoration-bf - shows the line in BOLD
decoration-it - shows the line in ITALICS
decoration-danger - shows the line in LIGHT RED
decoration-info - shows the line in LIGHT BLUE
decoration-muted - shows the line in LIGHT GRAY
decoration-primary - shows the line in LIGHT PURPLE
decoration-success - shows the line in LIGHT GREEN
decoration-warning - shows the line in LIGHT BROWN
