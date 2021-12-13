odoo.define('website_social.Like', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    var rpc = require('web.rpc');
    const ajax = require('web.ajax');
    var core = require('web.core');
    var QWeb = core.qweb;

    publicWidget.registry.Like = publicWidget.Widget.extend({
        // template: 'website_adbook.wadbook_emploer_list',
        // xmlDependencies: ['/website_adbook/static/src/xml/wadbook_emploer_list.xml'],
        selector: '.o_social_post',
        events: {
            'click .o_post_like_button': '_onClickLike',
            'click .o_post_comment_send_button': '_onClickSendComment',
        },

        init: function (parent, options) {
            this._super.apply(this, arguments);
            // $('.o_wslides_lesson_content_type').append(QWeb.render('website_adbook.wadbook_content' , {}))
        },

        _onClickLike: function () {
            var postId = this.$el[0].attributes.postId.value;
            console.log("_onClickLike", this.postId)
            console.log("this", this)
            var self = this;
            // var postId = this.postId;

            if (postId) {
                // $('.load').css('display', 'block');

                ajax.jsonRpc('/social/post/like/' + postId, 'call', {})
                    .then(function (json_data) {
                        if (json_data['result'] == 'success') {
                            // self.listVoting.push(json_data['data'])
                            console.log("ok")
                            var elem = $(`.a_post_like_${postId}`);
                            var el_count = $(`.like_count_${postId}`);
                            el_count.html('+1');
                            if (elem.hasClass('o_post_like_button')) {
                                elem.removeClass('o_post_like_button');
                            }
                            elem.addClass('post-like');

                        } else {
                            alert(json_data['data'])
                        }
                        // $('.load').css('display', 'none')

                    });

            }
        },


        _onClickSendComment: function () {
            var postId = this.$el[0].attributes.postId.value;
            console.log("_onClickSendComment", this.postId)
            console.log("this", this)

            var comment = $(`.p_comment_${postId}`).val();
            console.log("comment", comment)

            if (comment.length == 0) {
                alert("Комментарий не должен быть пустым")
                return
            }

            var self = this;
            // var postId = this.postId;
            // var content = "lkjlkjk"
            if (postId) {
                // $('.load').css('display', 'block');

                ajax.jsonRpc('/social/post/comment/create/' + postId, 'call', { 'content': comment })
                    .then(function (json_data) {
                        if (json_data['result'] == 'success') {
                            // self.listVoting.push(json_data['data'])
                            console.log("ok")
                            // var elem = $(`.a_post_like_${postId}`);
                            // var el_count = $(`.like_count_${postId}`);
                            // el_count.html('+1');
                            // if (elem.hasClass('o_post_like_button')) {
                            //     elem.removeClass('o_post_like_button');
                            // }
                            // elem.addClass('post-like');
                            location.reload();

                        } else {
                            alert(json_data['data'])
                        }
                        // $('.load').css('display', 'none')

                    });

            }
        },

    });


    return publicWidget.registry.Like;



});