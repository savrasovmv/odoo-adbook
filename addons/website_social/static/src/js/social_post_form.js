odoo.define('website_social.PartnerSearch', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    var rpc = require('web.rpc');
    const ajax = require('web.ajax');
    var core = require('web.core');
    var QWeb = core.qweb;

    publicWidget.registry.PartnerSearch = publicWidget.Widget.extend({
        // template: 'website_adbook.wadbook_emploer_list',
        // xmlDependencies: ['/website_adbook/static/src/xml/wadbook_emploer_list.xml'],
        selector: '.website_social',
        events: {
            // 'click': '_onClick',
        },
        // init: function (parent, options) {
        //     this._super.apply(this, arguments);
        //     // $('.o_wslides_lesson_content_type').append(QWeb.render('website_adbook.wadbook_content' , {}))
        // },

        /**
         * @override
         */
        start: function () {
            var self = this;

            this.lastsearch = [];
            console.log("js_partner_m2o")


            $('input.js_partner_m2o').select2({
                // tags: true,
                tokenSeparators: [',', ' ', '_'],
                maximumInputLength: 35,
                minimumInputLength: 2,
                lastsearch: [],
                placeholder: 'Выберите сотрудника',
                allowClear: true,


                ajax: {
                    url: '/social/get_partner',
                    dataType: 'json',
                    data: function (term) {
                        console.log("js_partner_m2o term", term)

                        return {
                            query: term,
                            limit: 50,
                        };
                    },
                    results: function (data) {
                        var ret = [];
                        _.each(data, function (x) {
                            ret.push({
                                id: x.id,
                                text: x.name,
                                isNew: false,
                            });
                        });
                        self.lastsearch = ret;
                        return { results: ret };
                    }
                },
                // Take default tags from the input value
                initSelection: function (element, callback) {
                    var data = [];
                    _.each(element.data('init-value'), function (x) {
                        data.push({ id: x.id, text: x.name, isNew: false });
                    });
                    element.val('');
                    callback(data);
                },
            });



            return this._super.apply(this, arguments);
        }

    });


    return publicWidget.registry.PartnerSearch;



});