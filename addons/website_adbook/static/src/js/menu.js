odoo.define('website_adbook.WadbookMenu', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    var rpc = require('web.rpc');
    const ajax = require('web.ajax');
    var core = require('web.core');
    var QWeb = core.qweb;
    
    publicWidget.registry.WadbookMenu = publicWidget.Widget.extend({
        template: 'website_adbook.wadbook_emploer_list',
        xmlDependencies: ['/website_adbook/static/src/xml/wadbook_emploer_list.xml'],
        selector: '.o_adbook_menu',
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
            // alert($(ev.target).attr('id'));
            var self = this.$el[0]
            var id = self.id;
            var isrecords = self.attributes['isrecords'].value;
            $('*.o_adbook_menu').each(function() {
                $(this).removeClass('active');
            });
            $(self).addClass('active')
            
            if (self.classList.contains('o-active')) {
                $(self).removeClass('o-active')
                $('*#o_dep_parent_id_'+id).each(function() {
                    $(this).removeClass('dep-sub-menu-show');
                });
            } else {
                $(self).addClass('o-active')
                $('*#o_dep_parent_id_'+id).each(function() {
                    $(this).addClass('dep-sub-menu-show');
                });
            }
            
            if (isrecords == 'True') {
                ajax.jsonRpc('/wadbook/get_employer/'+id, 'call', {})
                .then(function(json_data) { 
                    // console.log(json_data); 
                    var $content = $(QWeb.render('website_adbook.wadbook_emploer_list' , json_data))
                    $('.o_wslides_lesson_content_type').html($content) 
                    // return;
                });
            }

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

    // console.log("this");
    // var Widget = require('web.Widget');

    // var Counter = Widget.extend({
    //     template: 'wadbook_left_panel',
    //     events: {
    //         'click .o_adbook_menu': '_onClick',
    //         'click button': '_onClick',
    //     },
    //     init: function (parent, value) {
    //         this._super(parent);
    //         // this.count = value;
    //     },
    //     _onClick: function () {
    //         // this.count++;
    //         // this.$('.val').text(this.count);
    //         console.log("this+++++++++++++++++");

    //     },
    // });

    // var Widget = require('web.Widget');
    // var MenuAdbook = Widget.extend({
    //     // template: 'WidgetOneTemplate', // fill with the template name that will be rendered by odoo
    //     template: 'website_adbook.wadbook_left_panel',
    //     selector: '.o_adbook_menu',
    //     events: { // list of event, like jquery event
    //         'click .o_adbook_menu': 'menu_action',
    //     },
    //     /**
    //      * @override
    //      * @param {$.Element} params.questionsEl The element containing the actual questions
    //      *   to be able to hide / show them based on the page number
    //      */
    //     init: function (parent, params) {
    //         this._super.apply(this, arguments);
    //     },

    //     /**
    //      * @override
    //      */
    //     start: function () {
    //         var self = this;
    //         return this._super.apply(this, arguments).then(function () {
    //         });
    //     },
        
    //     /**
    //      * @private
    //      * @param {MouseEvent} event
    //      */
    //     menu_action: function(event){
    //         var self = this;
    //         var $target = $(event.currentTarget);
    //         this.$('o_adbook_menu_item').removeClass('dep-sub-menu-show');
    //         this.$('o_adbook_menu_item').addClass('dep-sub-menu-show');
    //         console.log("this");
    //     },
        
    // });

    // return Widget.registry.MenuAdbook;

});