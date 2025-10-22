/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.TokenResellPriceAutofill = publicWidget.Widget.extend({
    selector: '.modal-resell',

    events: {
        'submit .resell-property-form': '_onSubmitResellForm',
    },

    start() {
        this._setupModalPriceAutofill();
        this.alertContainer = $('#alert-container');
        return this._super(...arguments);
    },

    _setupModalPriceAutofill() {
        document.querySelectorAll("button[data-bs-target^='#resellPropertyModal']").forEach((btn) => {
            btn.addEventListener("click", () => {
                const price = btn.getAttribute("data-price");
                const modalId = btn.getAttribute("data-bs-target");
                const modal = document.querySelector(modalId);
                if (!modal || !price) return;

                const displayInput = modal.querySelector("input[name='price_per_token_display']");
                const hiddenInput = modal.querySelector("input[name='price_per_token']");

                let raw = price.replace(/[^\d.,]/g, '');
                if (raw.includes(',')) {
                    raw = raw.replace(/\./g, '').replace(',', '.');
                }
                const numericValue = parseFloat(raw) || 0;
                displayInput.value = this._formatIDR(numericValue);
                hiddenInput.value = numericValue;
            });
        });

        document.querySelectorAll(".currency-input").forEach((el) => {
            el.addEventListener("input", (ev) => {
                let val = ev.target.value.replace(/[^\d]/g, '');
                if (val.includes(',')) {
                    val = val.replace(/\./g, '').replace(',', '.');
                }
                const numeric = parseFloat(val) || 0;
                const modal = ev.target.closest('.modal');
                const hidden = modal.querySelector('#price_per_token');
                hidden.value = numeric;
                ev.target.value = this._formatIDR(numeric);
            });
        });
    },

    /**
     * Handle form submission via RPC
     */
    async _onSubmitResellForm(ev) {
        ev.preventDefault();

        const form = ev.currentTarget;
        const property_id = form.dataset.propertyId;
        const qty_token = form.querySelector("input[name='qty_token']").value;
        const price_per_token = form.querySelector("input[name='price_per_token']").value;

        try {
            const result = await rpc("/token/resell/submit", {
                property_id: parseInt(property_id),
                qty_token: parseInt(qty_token),
                price_per_token: parseFloat(price_per_token),
            });

            if (result.success) {
                this._showAlert("success", result.message);
                $(form).closest(".modal").modal("hide");
            } else {
                this._showAlert("danger", result.message || "Gagal mengajukan resell token.");
            }
        } catch (error) {
            console.error("RPC Error:", error);
            this._showAlert("danger", "Terjadi kesalahan saat mengirim data resell.");
        }
    },

    _formatIDR(amount) {
        const num = parseFloat(String(amount).replace(/[^\d.-]/g, '')) || 0;
        try {
            return new Intl.NumberFormat('id-ID', {
                style: 'currency',
                currency: 'IDR',
                minimumFractionDigits: 0
            }).format(num);
        } catch (_) {
            return 'Rp' + num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
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
