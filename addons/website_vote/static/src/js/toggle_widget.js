odoo.define('website_vote.Agree', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    // var rpc = require('web.rpc');
    // const ajax = require('web.ajax');
    // var core = require('web.core');
    // var QWeb = core.qweb;
    
    publicWidget.registry.VoteAgree = publicWidget.Widget.extend({

        selector: '.oe_agree',

        events: {
            'click ': '_onClick',
        },

        init: function (parent, options) {
            this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         */
        _onClick: function () {
            console.log(this);
            var checked = this.$el[0].checked;
            $('*.oe_vote_reg').each(function() {
                this.disabled = !this.disabled
            });
            
        },
    });

    return publicWidget.registry.VoteAgree;


});