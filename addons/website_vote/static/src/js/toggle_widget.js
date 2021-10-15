odoo.define('website_vote.Agree', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    var rpc = require('web.rpc');
    const ajax = require('web.ajax');
    var core = require('web.core');
    var QWeb = core.qweb;
    
    publicWidget.registry.WadbookMenu = publicWidget.Widget.extend({
        // template: 'website_adbook.wadbook_emploer_list',
        // xmlDependencies: ['/website_adbook/static/src/xml/wadbook_emploer_list.xml'],
        selector: '.oe_agree',
        events: {
            'click ': '_onClick',
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
         _onClick: function () {
            // console.log("+++++++++++++++++++++++++++this", this);
            console.log(this);
            var checked = this.$el[0].checked;
            $('*.oe_vote_reg').each(function() {
                console.log(this);
                    // if (checked) {
                    //     $(this).addClass('vote_agree');
                    // } else {
                    //     $(this).removeClass('vote_agree');
                    // }
                    this.disabled = !this.disabled
                    
                });
            // var self = this.$el[0]
            // var id = self.id;
            // var isrecords = self.attributes['isrecords'].value;
            // $('*.o_adbook_menu').each(function() {
            //     $(this).removeClass('active');
            // });
            // $(self).addClass('active')
            
            // if (self.classList.contains('o-active')) {
            //     $(self).removeClass('o-active')
            //     $('*#o_dep_parent_id_'+id).each(function() {
            //         $(this).removeClass('dep-sub-menu-show');
            //     });
            // } else {
            //     $(self).addClass('o-active')
            //     $('*#o_dep_parent_id_'+id).each(function() {
            //         $(this).addClass('dep-sub-menu-show');
            //     });
            // }
            
            // if (isrecords == 'True') {
            //     ajax.jsonRpc('/wadbook/get_employer/'+id, 'call', {})
            //     .then(function(json_data) { 
            //         // console.log(json_data); 
            //         var $content = $(QWeb.render('website_adbook.wadbook_emploer_list' , json_data))
            //         $('.o_wslides_lesson_content_type').html($content) 
            //         // return;
            //     });
            // }

                // self.view.$el.append(QWeb.render('view_cart_detail_template' , {'product_details': json_data}))                
                // $ ("# ViewCartModal"). modal (); // Отображение модального 
                 
            // var res = rpc.query({
            //     model: 'adbook.employer',
            //     method: 'search_read',
            //     args: [['branch_id', '=', id], []]
            //     /* args: args */
            // }).then(function (products) {
            //     console.log(products); });
            
        },
    });

    return publicWidget.registry.WadbookMenu;


});