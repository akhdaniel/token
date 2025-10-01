/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.TokenResellWidget = publicWidget.Widget.extend({
    selector: '.resell-property-form',
    events: {
        'submit': '_onSubmitForm',
    },

    /**
     * @override
     */
    start() {
        this.alertContainer = $('#alert-container');
        return this._super(...arguments);
    },

    /**
     * Handles the resell form submission.
     * @param {Event} ev
     */
    async _onSubmitForm(ev) {
        ev.preventDefault();

        const form = ev.currentTarget;
        const propertyId = form.dataset.propertyId;
        const qtyToken = form.querySelector("input[name='qty_token']").value;
        const pricePerToken = form.querySelector("input[name='price_per_token']").value;

        if (!qtyToken || !pricePerToken) {
            this._showAlert('danger', "Mohon isi jumlah token dan harga per token");
            return;
        }

        try {
            const result = await rpc('/token/resell/submit', {
                property_id: parseInt(propertyId),
                qty_token: parseInt(qtyToken),
                price_per_token: parseFloat(pricePerToken),
            });

            if (result.success) {
                const modalEl = $(form).closest(".modal");
                if (modalEl.length) {
                    modalEl.modal('hide');
                }

                this._showAlert('success', result.message);
                // setTimeout(() => {
                //     location.reload();
                // }, 1500);
            } else {
                this._showAlert('danger', result.message || "Gagal melakukan resell token.");
            }
        } catch (error) {
            console.error("RPC Error:", error);
            this._showAlert('danger', "Terjadi kesalahan server. Silakan coba lagi.");
        }
    },

    /**
     * Displays an alert notification inside alert-container.
     * @param {string} type - 'success' or 'danger'
     * @param {string} message - The message to display.
     */
    _showAlert(type, message) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        this.alertContainer.html(alertHtml);
        setTimeout(() => {
            this.alertContainer.find('.alert').alert('close');
        }, 3000);
    },

});
