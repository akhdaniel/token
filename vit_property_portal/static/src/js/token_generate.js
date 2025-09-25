/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.VitTokenGenerator = publicWidget.Widget.extend({
    selector: '#token-table-wrapper',

    start() {
        this.propertyId = this.$el.data('property-id');
        this.$button = this.$el.find('#btn-generate-token');
        this.$spinner = this.$button.find('.spinner-border');
        this._bindGenerate();
        return this._super(...arguments);
    },

    _bindGenerate() {
        this.$button.off('click').on('click', ev => {
            ev.preventDefault();
            this._generateTokens();
        });
    },

    async _generateTokens() {
        try {
            this.$spinner.removeClass('d-none');          
            this.$button.prop('disabled', true);          
            const result = await rpc(`/my/property/${this.propertyId}/generate_tokens`,{});
            if (result.error) {
                console.error(result.error);
            } else if (result.html) {
                this.$el.find('tbody').replaceWith(result.html);
            }
        } catch (err) {
            console.error('Generate token error:', err);
        } finally {
            this.$spinner.addClass('d-none');             
            this.$button.prop('disabled', false);       
        }
    },
});

export default publicWidget.registry.VitTokenGenerator;
