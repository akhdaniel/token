/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.VitTokenResellDetail = publicWidget.Widget.extend({
    selector: '.portal_property_detail_wrapper',

    start() {
        this._initTokenForm();
        return this._super(...arguments);
    },

    _initTokenForm() {
        const wrapper = this.el.querySelector('.vit-token-wrapper');
        if (!wrapper) return;

        this._price = parseFloat(wrapper.dataset.pricePerToken || 0);
        this._input = wrapper.querySelector('.vit-token-input');
        this._total = wrapper.querySelector('.vit-token-total');

        // Quick select buttons
        wrapper.querySelectorAll('.quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const value = parseInt(btn.dataset.value, 10);
                this._input.value = value;
                this._updateTotal(value);
            });
        });

        // On manual input
        this._input.addEventListener('input', e => {
            const qty = parseInt(e.target.value, 10) || 0;
            this._updateTotal(qty);
        });

        // Initialize
        this._updateTotal(1);
    },

    _updateTotal(qty) {
        const total = qty * this._price;
        this._total.textContent = this._formatIDR(total);
    },

    _formatIDR(amount) {
        return new Intl.NumberFormat("id-ID", {
            style: "currency",
            currency: "IDR",
            minimumFractionDigits: 0,
        }).format(amount);
    },
});
