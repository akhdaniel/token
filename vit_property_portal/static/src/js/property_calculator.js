/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.VitPropertyDropdown = publicWidget.Widget.extend({
    selector: '#property_id',      

    start() {
        this.$property    = this.$el.find('#property_id');
        this._loadProperties();
        return this._super(...arguments);
    },

    _loadProperties() {
        $.ajax({
            url: '/list_properties',
            type: 'GET',
            contentType: 'application/json',
            dataType: 'json',
            success: (result) => {
                this._display(result);
            },
            error: (err) => {
                console.error('Error fetching properties:', err);
            },
        });
    },

    _display(result) {
        result.result.forEach((p) => {
            this.$el.append(`<option value="${p.id}">${p.name}</option>`);
        });
    },
});
