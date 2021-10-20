odoo.define('website_vote.Voting', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    var rpc = require('web.rpc');
    const ajax = require('web.ajax');
    var core = require('web.core');
    var QWeb = core.qweb;
    
    publicWidget.registry.Voting = publicWidget.Widget.extend({
        // template: 'website_adbook.wadbook_emploer_list',
        // xmlDependencies: ['/website_adbook/static/src/xml/wadbook_emploer_list.xml'],
        selector: '.o_voting_main',
        events: {
            'click .o_voting_next': '_onClickNext',
            'click .o_voting_prev': '_onClickPrev',
        },
        init: function (parent, options) {
            this._super.apply(this, arguments);
            // $('.o_wslides_lesson_content_type').append(QWeb.render('website_adbook.wadbook_content' , {}))
        },

        _replaceContent: function (voteId) {
            ajax.jsonRpc('/vote/json/voting/'+voteId, 'call', {})
                .then(function(json_data) { 
                        console.log(json_data); 
                        // console.log(json_data['image_1920']); 
                        // var $content = $(QWeb.render('website_adbook.wadbook_emploer_list' , json_data))
                        $('.o_voting_image').css('backgroundImage', 'url(data:image/png;base64,'+ json_data['image_1920'] +' )'); 
                        $('.o_voting_file_text').html(json_data['file_text'])
                        this.nextId = json_data['next_id']
                        // this.attr('prevId',json_data['prev_id'])

                        // return;
                });

        },

        start: function () {
            // this._super.apply(this, arguments);
            var self = this;
            console.log("---------------")
            console.log(this)
            var voteId = this.$el[0].attributes.voteId.value;

            return this._super.apply(this, arguments).then(function () {
                
                if (voteId) {
                    self.voteId = voteId
                    // this._replaceContent(voteId)
                    ajax.jsonRpc('/vote/json/voting/'+voteId, 'call', {})
                    .then(function(json_data) { 
                            console.log(json_data); 
                            // console.log(json_data['image_1920']); 
                            // var $content = $(QWeb.render('website_adbook.wadbook_emploer_list' , json_data))
                            $('.o_voting_image').css('backgroundImage', 'url(data:image/png;base64,'+ json_data['image_1920'] +' )'); 
                            $('.o_voting_file_text').html(json_data['file_text'])
                            self.nextId = json_data['next_id']
                            self.prevId = json_data['prev_id']
                            self.listId = json_data['list_id']
                            self.index = 0
                            // this.attr('prevId',json_data['prev_id'])

                            // return;
                    });
                }

            })


            // $('.o_wslides_lesson_content_type').append(QWeb.render('website_adbook.wadbook_content' , {}))
        },



        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------
        /**
         * @private
         */
        _onClickNext: function () {
            var self = this;
            var nextId = this.nextId;
            if (nextId) {
                ajax.jsonRpc('/vote/participant/'+nextId, 'call', {})
                .then(function(json_data) { 
                        $('.o_voting_image').css('backgroundImage', 'url(data:image/png;base64,'+ json_data['image_1920'] +' )'); 
                        if (self.index == self.listId.length-1) {
                            // self.nextId = self.listId[0]
                            // self.prevtId = self.listId[self.index-1]
                            self.index = 0
                        } else {
                            self.index = self.index + 1
                        }
                        
                        if (self.index == 0) {
                            self.nextId = self.listId[self.index+1]
                            self.prevtId = self.listId[self.listId.length-1]
                        } else {
                            if (self.index == self.listId.length-1) {
                                self.nextId = self.listId[0] 
                            } else {
                                self.nextId = self.listId[self.index+1]
                            }
                            
                            self.prevtId = self.listId[self.index-1]
                            
                        } 
                        // self.index = self.index + 1

                });
            }
        },

         _onClickPrev: function () {
            var self = this;
            var prevtId = this.prevtId;
            if (prevtId) {
                ajax.jsonRpc('/vote/participant/'+prevtId, 'call', {})
                .then(function(json_data) { 
                        $('.o_voting_image').css('backgroundImage', 'url(data:image/png;base64,'+ json_data['image_1920'] +' )'); 
                        if (self.index == 0) {
                            self.index = self.listId.length-1
                        } else {
                            self.index = self.index - 1
                        }
                        
                        if (self.index == 0) {
                            self.nextId = self.listId[self.index+1]
                            self.prevtId = self.listId[self.listId.length-1]
                        } else {
                            if (self.index == self.listId.length-1) {
                                self.nextId = self.listId[0] 
                            } else {
                                self.nextId = self.listId[self.index+1]
                            }
                            
                            self.prevtId = self.listId[self.index-1]
                            
                        } 
                });
            }
        },
        /**
         * @private
         */
         _onClick: function () {
            // console.log("+++++++++++++++++++++++++++this", this);
            console.log(this);
            // var checked = this.$el[0].checked;
            // $('*.oe_vote_reg').each(function() {
            //     console.log(this);
            //         // if (checked) {
            //         //     $(this).addClass('vote_agree');
            //         // } else {
            //         //     $(this).removeClass('vote_agree');
            //         // }
            //         this.disabled = !this.disabled
                    
            //     });
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

    return publicWidget.registry.Voting;


});