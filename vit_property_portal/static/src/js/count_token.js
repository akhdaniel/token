/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.VitPropertyDetail = publicWidget.Widget.extend({
    // root di container besar
    selector: '.portal_property_detail_wrapper',

    start() {
        // ==== SLIDER TOKEN ====
        this.$years = this.$el.find('#years');
        const tokenWrapper = this.el.querySelector('.vit-token-wrapper');
        if (tokenWrapper) {
            this._price = parseFloat(tokenWrapper.dataset.pricePerToken || '0');
            this._range = tokenWrapper.querySelector('.vit-token-range');
            this._value = tokenWrapper.querySelector('.vit-token-value');
            this._total = tokenWrapper.querySelector('.vit-token-total');

            if (this._range && this._value && this._total) {
                this._updateDisplay(this._range.value);
                this._range.addEventListener('input', ev => {
                    this._updateDisplay(ev.target.value);
                });
            }
        }

        // ==== GANTI GAMBAR UTAMA ====
        // const mainImg = this.el.querySelector('#mainImage');
        // const thumbs  = this.el.querySelectorAll('.thumb-image');

        // thumbs.forEach(thumb => {
        //     thumb.addEventListener('click', () => {
        //         if (!mainImg) return;
        //         mainImg.src = thumb.dataset.full;

        //         // highlight thumbnail aktif
        //         thumbs.forEach(t => t.classList.remove('border', 'border-primary'));
        //         thumb.classList.add('border', 'border-primary');
        //     });
        // });

        this._updateSliderBackground();
        this.$years.on('input', () => this._updateSliderBackground());

        return this._super(...arguments);
    },

    _updateSliderBackground() {
        const slider = this.$years[0];
        if (!slider) return;
        const min = parseFloat(slider.min || 0);
        const max = parseFloat(slider.max || 100);
        const val = parseFloat(slider.value);
        const percent = ((val - min) * 100) / (max - min);
        slider.style.background = `linear-gradient(to right,
            #0d6efd 0%,
            #0d6efd ${percent}%,
            #6c757d ${percent}%,
            #6c757d 100%)`;
    },

    _updateDisplay(qty) {
        const n = parseInt(qty, 10) || 0;
        this._value.textContent = n;
        const amount = n * this._price;
        this._total.textContent = this._formatIDR(amount);
    },

    _formatIDR(amount) {
        try {
            return new Intl.NumberFormat('id-ID', {
                style: 'currency',
                currency: 'IDR',
                minimumFractionDigits: 0
            }).format(amount);
        } catch (_) {
            return 'Rp' + String(amount).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        }
    },
});
