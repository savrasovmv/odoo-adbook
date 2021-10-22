odoo.define('website_vote.Voting', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    // var rpc = require('web.rpc');
    const ajax = require('web.ajax');
    // var core = require('web.core');
    // var QWeb = core.qweb;
    
    publicWidget.registry.Voting = publicWidget.Widget.extend({
        // template: 'website_adbook.wadbook_emploer_list',
        // xmlDependencies: ['/website_adbook/static/src/xml/wadbook_emploer_list.xml'],
        selector: '.o_voting_main',
        events: {
            'click .o_voting_next': '_onClickNext',
            'click .o_voting_prev': '_onClickPrev',
            'click .o_voting_button': '_onClickVoting',
            'keydown': '_onKeydown',

        },
        init: function (parent, options) {
            this._super.apply(this, arguments);
            // $('.o_wslides_lesson_content_type').append(QWeb.render('website_adbook.wadbook_content' , {}))
        },

        _replaceContent: function (json_data) {
            $('.o_voting_image').css('backgroundImage', 'url(data:image/png;base64,'+ json_data['image_1920'] +' )'); 
            $('.o_voting_file_text').html(json_data['file_text'])
            $('.o_voting_autor').html(json_data['autor'])
            $('.o_voting_title').html(json_data['title'])
            $('.o_voting_department').html(json_data['department'])
            $('.o_voting_description').html(json_data['description'].replace(/\n/g, '<br/>'))
        },

        _replaceVotingButton: function (self) {
            if (!self.allowedVoting) {
                $('.voting_button').css('display', 'none');
                if (self.listVoting.includes(self.participantItemId)) {
                    $('.voting_button_finish').css('display', 'block');
                } else {
                    $('.voting_button_finish').css('display', 'none');
                }
            } else {
                if (self.listVoting.includes(self.participantItemId)) {
                    $('.voting_button').css('display', 'none');
                    $('.voting_button_finish').css('display', 'block');
                } else {
                    $('.voting_button').css('display', 'block');
                    $('.voting_button_finish').css('display', 'none');
                }

            }
            
        },

        _setNexPrevId: function (self) {
            self.index = self.listId.indexOf(parseInt(self.participantItemId))
            
            if (self.index == 0) {
                self.nextId = self.listId[self.index+1]
                self.prevId = self.listId[self.listId.length-1]
            } else {
                if (self.index == self.listId.length-1) {
                    self.nextId = self.listId[0] 
                } else {
                    self.nextId = self.listId[self.index+1]
                }
                
                self.prevId = self.listId[self.index-1]
                
            }

            
        },



        start: function () {
            // this._super.apply(this, arguments);
            var self = this;
            console.log("---------------")
            console.log(this)
            var voteId = this.$el[0].attributes.voteId.value;
            var participantItemId = this.$el[0].attributes.participantItemId.value;

            return this._super.apply(this, arguments).then(function () {
                
                $(document).keydown(function(event){
                    var keycode = (event.keyCode ? event.keyCode : event.which);
                    if(keycode == '39' | keycode == '38' | keycode == '13' | keycode == '32' | keycode == '9'){
                        self._onClickNext()
                    }
                    if(keycode == '37' | keycode == '40'){
                        self._onClickPrev()
                    }
                });
                
                if (participantItemId) {
                    $('.load').css('display', 'block');

                    self.voteId = voteId
                    self.participantItemId = participantItemId
                    // this._replaceContent(voteId)
                    ajax.jsonRpc('/vote/json/voting/'+participantItemId, 'call', {})
                    .then(function(json_data) { 
                            // console.log(json_data);
                            self._replaceContent(json_data) 
                            self.nextId = 0
                            self.prevId = 0
                            self.index = 0
                            self.listId = json_data['list_id']
                            self.amount = self.listId.length
                            
                            self.listVoting = json_data['list_voting']
                            self.maxVoting = json_data['max_voting']
                            self.allowedVoting = false
                            if (self.listVoting.length<self.maxVoting) {
                                self.allowedVoting = true
                            }

                            self._setNexPrevId(self)
                            $('.o_voting_count').html('1 из ' + self.amount)
                            self._replaceVotingButton(self)
                            $('.load').css('display', 'none')

                            // console.log(self.listVoting)
                            // console.log(self.maxVoting)
                            // console.log(self.allowedVoting)
                            // console.log(self.participantItemId)
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
                $('.load').css('display', 'block');

                ajax.jsonRpc('/vote/participant_item/'+nextId, 'call', {})
                .then(function(json_data) { 
                        // $('.o_voting_image').css('backgroundImage', 'url(data:image/png;base64,'+ json_data['image_1920'] +' )'); 
                        // $('.o_voting_file_text').html(json_data['file_text'])

                        self._replaceContent(json_data)
                        self.participantItemId = self.nextId

                        self._setNexPrevId(self)


                        // if (self.index == self.listId.length-1) {
                        //     // self.nextId = self.listId[0]
                        //     // self.prevId = self.listId[self.index-1]
                        //     self.index = 0
                        // } else {
                        //     self.index = self.index + 1
                        // }
                        
                        // if (self.index == 0) {
                        //     self.nextId = self.listId[self.index+1]
                        //     self.prevId = self.listId[self.listId.length-1]
                        // } else {
                        //     if (self.index == self.listId.length-1) {
                        //         self.nextId = self.listId[0] 
                        //     } else {
                        //         self.nextId = self.listId[self.index+1]
                        //     }
                            
                        //     self.prevId = self.listId[self.index-1]
                            
                        // } 
                        $('.o_voting_count').html(self.index+1+' из ' + self.amount)
                        self._replaceVotingButton(self)
                        $('.load').css('display', 'none')
                        
                        // self.index = self.index + 1

                });
                

            }
        },

         _onClickPrev: function () {
            var self = this;
            var prevId = this.prevId;
            if (prevId) {
                $('.load').css('display', 'block');

                ajax.jsonRpc('/vote/participant_item/'+prevId, 'call', {})
                .then(function(json_data) { 

                        self._replaceContent(json_data)
                        self.participantItemId = self.prevId
                        self._setNexPrevId(self)

                        // if (self.index == 0) {
                        //     self.index = self.listId.length-1
                        // } else {
                        //     self.index = self.index - 1
                        // }
                        
                        // if (self.index == 0) {
                        //     self.nextId = self.listId[self.index+1]
                        //     self.prevId = self.listId[self.listId.length-1]
                        // } else {
                        //     if (self.index == self.listId.length-1) {
                        //         self.nextId = self.listId[0] 
                        //     } else {
                        //         self.nextId = self.listId[self.index+1]
                        //     }
                            
                        //     self.prevId = self.listId[self.index-1]
                            
                        // } 
                        $('.o_voting_count').html(self.index+1+' из ' + self.amount)
                        self._replaceVotingButton(self)
                        $('.load').css('display', 'none')

                });

            }
        },
        _onClickVoting: function () {
            var self = this;
            var voteId = this.voteId;
            var participantItemId = this.participantItemId

            if (voteId) {
                $('.load').css('display', 'block');

                ajax.jsonRpc('/vote/voting_participant_item/'+participantItemId, 'call', {})
                .then(function(json_data) { 
                    if (json_data['result'] == 'success') {
                        self.listVoting.push(json_data['data'])
                        console.log(self.listVoting)
                        if (self.listVoting.length<self.maxVoting) {
                            self.allowedVoting = true
                        } else {
                            self.allowedVoting = false
                        }
                        self._replaceVotingButton(self)


                    } else {
                        alert(json_data['data'])
                    }
                    $('.load').css('display', 'none')

                });

            }
        },

        /**
         * Called when typing something on the composer of this thread window.
         *
         * @private
         * @param {KeyboardEvent} ev 
        
         */
        _onKeydown: function (ev) {
            console.log('++++++++++++++++')
            var self = this;
            ev.stopPropagation(); // to prevent jquery's blockUI to cancel event
            // ENTER key (avoid requiring jquery ui for external livechat)
            if (ev.which === 39) {
                self._onClickNext()
            }
        },
        
    });

    return publicWidget.registry.Voting;


});