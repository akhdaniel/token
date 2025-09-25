/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PropertyFormWidget = publicWidget.Widget.extend({
    selector: '#property-form',
    events: {
        'submit': '_onSubmitForm',
        'change .sale-rent-switch': '_onSaleRentChange',
        'input .currency-input': '_onCurrencyInput',
        'input #cost_price_display': '_recalculatePricePerToken',
        'input #total_tokens': '_recalculatePricePerToken',
    },

    /**
     * @override
     */
    start() {
        this.saveBtn = this.$el.find('#save-btn');
        this.spinner = this.saveBtn.find('.spinner-border');
        this.alertContainer = $('#alert-container');
        this.salePriceGroup = this.$('#sale_price_group');
        this.rentPriceGroup = this.$('#rental_price_group');

        this.$('.currency-input').each((_, el) => {
            const raw = $(el).val().replace(/[^\d]/g, '');
            $(el).val(this._formatIDR(raw));
        });

        this._recalculatePricePerToken();

        return this._super(...arguments);
    },

    _onSaleRentChange(ev) {
        const $target = $(ev.currentTarget);

        if ($target.attr('id') === 'is_sale' && $target.is(':checked')) {
            this.$('#is_rent').prop('checked', false);
        } else if ($target.attr('id') === 'is_rent' && $target.is(':checked')) {
            this.$('#is_sale').prop('checked', false);
        }

        this.salePriceGroup.toggle(this.$('#is_sale').is(':checked'));
        this.rentPriceGroup.toggle(this.$('#is_rent').is(':checked'));
    },

    _onCurrencyInput(ev) {
        const display = ev.currentTarget;
        const raw = display.value.replace(/[^\d]/g, '');
        const hiddenId = display.id.replace('_display', '');
        this.$('#' + hiddenId).val(raw);
        display.value = this._formatIDR(raw);
    },

    _recalculatePricePerToken() {
        const costRaw = this.$('#cost_price').val() || 0;
        const totalTokens = parseInt(this.$('#total_tokens').val()) || 0;
        const perToken = totalTokens > 0 ? (parseFloat(costRaw) / totalTokens) : 0;
        this.$('#price_per_token').val(perToken);
        this.$('#price_per_token_display').val(this._formatIDR(perToken));
    },

    /**
     * Handles the form submission event.
     * @param {Event} ev
     */
    _onSubmitForm(ev) {
        ev.preventDefault();

        this.saveBtn.prop('disabled', true);
        this.spinner.removeClass('d-none');
        this.alertContainer.empty();

        const formData = new FormData(this.$el[0]);
        const data = Object.fromEntries(formData.entries());

        this._prepareData(data);
        this._callRpc(data);
    },

    /**
     * Prepares form data for the RPC call.
     * @param {Object} data
     */
    _prepareData(data) {
        data['is_sale'] = this.$el.find('#is_sale').is(':checked');
        data['is_rent'] = this.$el.find('#is_rent').is(':checked');

        ['sale_price', 'cost_price', 'rental_price', 'sale_price_target', 'expected_rental_yield'].forEach(key => {
            data[key] = parseFloat(data[key]) || 0;
        });

        ['total_tokens', 'available_tokens'].forEach(key => {
            data[key] = parseInt(data[key]) || 0;
        });
    },

    /**
     * Calls the RPC endpoint to save the property.
     * @param {Object} data
     */
    async _callRpc(data) {
        try {
            console.log("_callRpc", data);
            
            const result = await rpc('/api/property/save', { data });
            console.log("_callRpc result : ", result);
            
            this._handleRpcResult(result);
        } catch (error) {
            console.error("RPC Error:", error);
            this._showAlert('danger', 'An unexpected error occurred. Please try again.');
        } finally {
            this.isSaving = false; 
            this.saveBtn.prop('disabled', false);
            this.spinner.addClass('d-none');
        }
    },

    /**
     * Handles the result from the RPC call.
     * @param {Object} result
     */
    _handleRpcResult(result) {
        if (result.success) {
            console.log("_handleRpcResult : ", result);

            this._showAlert('success', result.message);
            this.$el.find('input[name="id"]').val(result.property_id);
        } else {
            this._showAlert('danger', result.message);
        }
    },

    /**
     * Displays an alert notification.
     * @param {string} type - 'success' or 'danger'
     * @param {string} message - The message to display.
     */
    _showAlert(type, message) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
            </div>
        `;
        this.alertContainer.html(alertHtml);
        setTimeout(() => {
            this.alertContainer.find('.alert').alert('close');
        }, 3000);
    },

    _resetButton() {
        this.saveBtn.prop('disabled', false);
        this.spinner.addClass('d-none');
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

});