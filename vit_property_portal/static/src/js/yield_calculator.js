/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.VitPropertySimulasiImbalHasil = publicWidget.Widget.extend({
    selector: '.simulasi-wrapper',

    start() {
        this.$property    = this.$el.find('#property_id');
        this.$invest      = this.$el.find('#monthly_invest');
        this.$years       = this.$el.find('#years');
        this.$yearsValue  = this.$el.find('#years_value');
        this.$investType  = this.$el.find('input[name="invest_type"]');
        
        this.$totalInvest = this.$el.find('#total_invest');
        this.$totalReturn = this.$el.find('#total_return');
        this.$totalAsset  = this.$el.find('#total_asset');
        this.$tokens      = this.$el.find('#tokens');
        this.$tokenQty    = this.$el.find('#token_qty');
        
        this.$yearsValue2  = this.$el.find('#years_value2');
        this.$yearsValue3  = this.$el.find('#years_value3');
        this.$totalReturn2 = this.$el.find('#total_return2');
        this.$tokens2      = this.$el.find('#tokens2');
        // Warna progress awal
        this._updateSliderBackground();
        this.$years.on('input', () => this._updateSliderBackground());

        // Format input nominal tanpa “Rp”
        this.$invest.on('input', (e) => this._formatInvestInput(e));

        // Perhitungan awal & event
        this._compute();
        this.$property.on('change', () => this._compute());
        this.$years.on('input', () => {
            this.$yearsValue.text(this.$years.val());
            this.$yearsValue2.text(this.$years.val());
            this.$yearsValue3.text(this.$years.val());
            this._compute();
        });
        this.$investType.on('change', () => this._compute());

        return this._super(...arguments);
    },

    _formatInvestInput(e) {
        let raw = e.target.value.replace(/\D/g, '');   // hanya angka
        if (!raw) {
            e.target.value = '';
            this._compute();
            return;
        }
        e.target.value = new Intl.NumberFormat('id-ID', {
            style: 'decimal',
            minimumFractionDigits: 0
        }).format(parseInt(raw, 10));
        this._compute();
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

    _compute() {
        const propertyId = this.$property.val();
        const invest = parseInt((this.$invest.val() || '0').replace(/\D/g,''), 10);
        const years  = parseInt(this.$years.val() || 1, 10);
        const investType = this.$el.find('input[name="invest_type"]:checked').val();

        if (!propertyId || invest <= 0) {
            this._display(0,0,0,0);
            return;
        }

        $.ajax({
            url: '/yield_calculator',
            type: 'POST',
            contentType: 'application/json',
            dataType: 'json',
            data: JSON.stringify({
                property_id: propertyId,
                invest_type: investType,
                monthly_invest: invest,
                years: years,
                auto_reinvest: false,
            }),
            success: (result) => this._display(result),
            error: () => this._display(0,0,0,0),
        });
    },

    _display(result) {
        let total_invest = 0, total_return = 0, total_asset = 0, tokens = 0;
        if (result && result.result) {
            total_invest = result.result.total_invest || 0;
            total_return = result.result.total_rental_income || 0;
            total_asset  = result.result.total_asset || 0;
            tokens       = result.result.token_qty || 0;
        }
        console.log(total_invest, total_return, total_asset, tokens);
        
        this.$totalInvest.text(this._formatIDR(total_invest));
        this.$totalReturn.text(this._formatIDR(total_return));
        this.$totalAsset.text(this._formatIDR(total_asset));
        this.$tokens.text(tokens);
        this.$totalReturn2.text(this._formatIDR(total_return));
        this.$tokens2.text(tokens);
        this.$tokenQty.val(tokens);
    },

    _formatIDR(amount) {
        return new Intl.NumberFormat('id-ID', {
            style: 'currency',
            currency: 'IDR',
            minimumFractionDigits: 0
        }).format(amount);
    },
});
