/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.VitPropertyDetail = publicWidget.Widget.extend({
    selector: '.portal_property_detail_wrapper',

    start() {
        // --- TOKEN CALCULATION (sudah ada) ---
        const tokenWrapper = this.el.querySelector('.vit-token-wrapper');
        if (tokenWrapper) {
            this._price = parseFloat(tokenWrapper.dataset.pricePerToken || '0');
            this._numberInput = tokenWrapper.querySelector('.vit-token-input');
            this._total = tokenWrapper.querySelector('.vit-token-total');
            this._quickBtns = tokenWrapper.querySelectorAll('.quick-btn');

            this._numberInput.addEventListener('input', ev => this._updateTotal(ev.target.value));
            this._quickBtns.forEach(btn => {
                const val = parseInt(btn.dataset.value, 10);
                if (val > parseInt(this._numberInput.max)) btn.disabled = true;
                btn.addEventListener('click', () => {
                    this._numberInput.value = val;
                    this._updateTotal(val);
                });
            });
            this._updateTotal(this._numberInput.value);
        }

        // --- IMAGE GALLERY ---
        const mainImg = this.el.querySelector('#mainImage');
        const thumbs = Array.from(this.el.querySelectorAll('.thumb-image'));
        const container = this.el.querySelector('.thumb-container');
        const prevBtn = this.el.querySelector('.thumb-nav.prev');
        const nextBtn = this.el.querySelector('.thumb-nav.next');

        if (mainImg && thumbs.length) {
            thumbs.forEach(thumb => {
                thumb.addEventListener('click', () => {
                    const newSrc = thumb.getAttribute('src');
                    if (mainImg.src !== newSrc) {
                        mainImg.classList.remove('fade-active');
                        setTimeout(() => {
                            mainImg.src = newSrc;
                            mainImg.classList.add('fade-active');
                        }, 150);
                    }
                    thumbs.forEach(t => t.classList.remove('active'));
                    thumb.classList.add('active');
                });
            });

            // Navigasi scroll thumbnail
            let scrollPos = 0;
            const scrollStep = 120;

            prevBtn?.addEventListener('click', () => {
                scrollPos = Math.max(scrollPos - scrollStep, 0);
                container.scrollTo({ left: scrollPos, behavior: 'smooth' });
            });

            nextBtn?.addEventListener('click', () => {
                scrollPos = Math.min(scrollPos + scrollStep, container.scrollWidth);
                container.scrollTo({ left: scrollPos, behavior: 'smooth' });
            });
        }

        return this._super(...arguments);
    },

    _updateTotal(qty) {
        const n = parseInt(qty, 10) || 0;
        const total = n * this._price;
        this._total.textContent = this._formatIDR(total);
    },

    _formatIDR(amount) {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(amount);
    },
});