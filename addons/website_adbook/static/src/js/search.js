odoo.define('website_adbook.WadbookSearch', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    var rpc = require('web.rpc');
    const ajax = require('web.ajax');
    var core = require('web.core');
    var QWeb = core.qweb;
    
    publicWidget.registry.WadbookSearch = publicWidget.Widget.extend({
        template: 'website_adbook.wadbook_emploer_list',
        xmlDependencies: ['/website_adbook/static/src/xml/wadbook_emploer_list.xml'],
        selector: '.oe_wadbook_search_button',
        events: {
            'click': '_onClick',
        },
        init: function (parent, options) {
            this._super.apply(this, arguments);
            // $('.o_wslides_lesson_content_type').append(QWeb.render('website_adbook.wadbook_content' , {}))
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         */
         _onClick: function (event) {
            event.preventDefault();
            // console.log("+++++++++++++++++++++++++++this", this);
            var self = this.$el[0]
            var id = self.id;
            // var serch_text = $('.o_search_text').value;
            var serch_text = document.querySelector('.o_search_text').value;

            console.log("+++++++++++++++++++++++++++this", serch_text);
            
            if (serch_text != '') {
                ajax.jsonRpc('/wadbook/search_employer/' + serch_text, 'call', {})
                .then(function(json_data) { 
                    // console.log(json_data); 
                    var $content = $(QWeb.render('website_adbook.wadbook_emploer_list' , json_data))
                    $('.o_wslides_lesson_content_type').html($content) 
                });
            }
        },
    });

    return publicWidget.registry.WadbookSearch;

    

});