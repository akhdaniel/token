/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.VitTokenPagination = publicWidget.Widget.extend({
    selector: '#token-table-wrapper',

    start() {
        this.propertyId = this.$el.data('property-id');
        this._bindLinks();
        return this._super(...arguments);
    },

    _bindLinks() {
        this.$el.off('click', '.token-page');
        this.$el.on('click', '.token-page', ev => {
            ev.preventDefault();
            const page = $(ev.currentTarget).data('page');
            this._loadPage(page);
        });
    },

    async _loadPage(page) {
        try {
            const result = await rpc(`/my/property/${this.propertyId}/tokens`, {
                page: page
            });
            if (result.html) {
                this.$el.html(result.html); 
                this._bindLinks(); 
            }
        } catch (err) {
            console.error('Error fetching token pagination:', err);
        }
    },
});
