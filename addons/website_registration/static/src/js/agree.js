odoo.define('website_registration.Agree', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    
    publicWidget.registry.RegistrationAgree = publicWidget.Widget.extend({

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
            var checked = this.$el[0].checked;
            $('*.o_button_registration').each(function() {
                this.disabled = !this.disabled
            });
            
        },
    });

    return publicWidget.registry.RegistrationAgree;


});