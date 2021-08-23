odoo.define("toggle_widget", function (require) {
    "use strict";

    var basic_fields = require("web.basic_fields");

    var Toggle = basic_fields.BooleanToggle.extend({
        _onClick: function (event) {
            var self = this;
            this._super(event);
            var node = event.view.$(".custom-control-input");

            if (this.value) {
                node.show();
            } else {
                node.hide();
            }
        },
    });

    fieldRegistry.add("toggle", Toggle);

    return {
        toggle: toggle,
    };
});
