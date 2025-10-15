/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.TokenResellPriceAutofill = publicWidget.Widget.extend({
    selector: '.modal-resell',  // gunakan body agar event global
    events: {},

    /**
     * @override
     */
    start() {
        // Jalankan setelah halaman siap
        this._setupModalPriceAutofill();
        return this._super(...arguments);
    },

    /**
     * Mengisi otomatis harga token ketika modal dibuka.
     */
    _setupModalPriceAutofill() {
        // Tangkap semua tombol dengan data-bs-target ke modal resell
        document.querySelectorAll("button[data-bs-target^='#resellPropertyModal']").forEach((btn) => {
            btn.addEventListener("click", () => {
                const price = btn.getAttribute("data-price");
                const modalId = btn.getAttribute("data-bs-target");
                const modal = document.querySelector(modalId);
                if (!modal) return;

                // cari input di dalam modal dan isi dengan value
                const input = modal.querySelector("input[name='price_per_token']");
                if (input && price) {
                    input.value = price;
                }
            });
        });
    },
});
