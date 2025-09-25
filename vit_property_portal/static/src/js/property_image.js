/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PropertyImageManager = publicWidget.Widget.extend({
    selector: '#image-pane',
    events: {
        'click #btn-add-image': '_openModal',
        'submit #upload-image-form': '_onSubmit',
        'click .btn-delete': '_onDelete',
        'click .btn-edit': '_openEdit',
        'submit #edit-image-form': '_onUpdate',
    },

    start() {
        this.unitId = this.$('input[name="property_unit_id"]').val();
        this.alertContainer = $('#image-alert-container');
        return this._super(...arguments);
    },

    _openModal() {
        $('#uploadImageModal').modal('show');
    },

    async _onSubmit(ev) {
        ev.preventDefault();
        const form = ev.currentTarget;
        const spinner = $(form).find('.spinner-border');
        spinner.removeClass('d-none');

        try {
            const seq = form.sequence.value;
            const file = form.image.files[0];
            const base64 = await this._fileToBase64(file);

            const result = await rpc('/my/property/upload_image', {
                property_unit_id: this.unitId,
                sequence: seq,
                image: base64.split(',')[1], // remove prefix
            });

            spinner.addClass('d-none');

            if (result.error) {
                this._showAlert('danger', result.error);
            } else {
                $('#uploadImageModal').modal('hide');
                form.reset();
                this._showAlert('success', 'Image uploaded successfully');
                this._reloadTable();
            }
        } catch (err) {
            spinner.addClass('d-none');
            this._showAlert('danger', err.message);
        }
    },

    async _onDelete(ev) {
        const id = $(ev.currentTarget).closest('tr').data('id');
        if (!confirm('Delete this image?')) return;
        const result = await rpc('/my/property/delete_image', { image_id: id });
        if (result.error) {
            this._showAlert('danger', result.error);
        } else {
            this._showAlert('success', 'Image deleted');
            this._reloadTable();
        }
    },

    _openEdit(ev) {
        const tr = $(ev.currentTarget).closest('tr');
        const id = tr.data('id');
        const name = tr.find('td:nth-child(3)').text().trim();
        const seq = tr.find('td:first-child').text().trim();
        const imageSrc = tr.data('image');

        const modal = $('#editImageModal');
        modal.find('input[name="image_id"]').val(id);
        modal.find('input[name="name"]').val(name);
        modal.find('input[name="sequence"]').val(seq);
        modal.find('#edit-image-preview').attr('src', imageSrc);
        modal.modal('show');
    },

    async _onUpdate(ev) {
        ev.preventDefault();
        const form = ev.currentTarget;
        const id = form.image_id.value;
        const name = form.name.value;
        const seq = form.sequence.value;

        let imageBase64 = null;
        if (form.image.files.length > 0) {
            const file = form.image.files[0];
            const base64 = await this._fileToBase64(file);
            imageBase64 = base64.split(',')[1]; 
        }

        const result = await rpc('/my/property/update_image', {
            image_id: id,
            name: name,
            sequence: seq,
            image: imageBase64,
        });

        if (result.error) {
            this._showAlert('danger', result.error);
        } else {
            $('#editImageModal').modal('hide');
            this._showAlert('success', 'Image updated');
            this._reloadTable();
        }
    },

    async _reloadTable() {
        const rows = await rpc(`/my/property/image_list/${this.unitId}`);
        const tbody = this.$('#image-table tbody').empty();

        rows.forEach(r => {
            const imgTag = `<img src="data:image/png;base64,${r.image}" style="height:60px;">`;
            tbody.append(`<tr>
                                <td>${r.sequence}</td>
                                <td>${imgTag}</td>
                                <td>${r.name}</td>
                                <td>
                                    <button class="btn btn-sm btn-warning btn-edit" id="btn-edit">Edit</button>
                                    <button class="btn btn-sm btn-danger btn-delete" id="btn-delete">Delete</button>
                                </td>
                            </tr>`);
        });
    },

    _showAlert(type, msg) {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${msg}
            </div>
        `;
        this.alertContainer.html(alertHtml);
        setTimeout(() => {
            this.alertContainer.find('.alert').alert('close');
        }, 3000);
    },

    _fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    },
});
