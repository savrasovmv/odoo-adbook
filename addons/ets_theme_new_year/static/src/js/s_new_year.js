odoo.define('website_snippets_ets.Birthday', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    // var rpc = require('web.rpc');
    const ajax = require('web.ajax');
    var core = require('web.core');
    var QWeb = core.qweb;
    
    publicWidget.registry.Birthday = publicWidget.Widget.extend({
        template: 'website_snippets_ets.birthday_list',
        xmlDependencies: ['/website_snippets_ets/static/src/xml/birthday_list.xml'],
        selector: '.o_birthday_snippets',
        disabledInEditableMode: false,
        init: function (parent, options) {
            this._super.apply(this, arguments);
            // $('.o_wslides_lesson_content_type').append(QWeb.render('website_adbook.wadbook_content' , {}))
        },
        start: function () {
            var self = this;
            ajax.jsonRpc('/web/birthday/', 'call', {})
            .then(function(json_data) { 
                // console.log(json_data); 
                console.log("+++++++++++json_data", json_data)
                
                var $content = $(QWeb.render('website_snippets_ets.birthday_list' , json_data))
                $('.o_birthday_snippets').html($content) 
            });
        }, 
        
    });

    return publicWidget.registry.Birthday;


});