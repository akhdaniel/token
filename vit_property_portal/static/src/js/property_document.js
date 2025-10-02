/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";
import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.PropertyDocumentManager = publicWidget.Widget.extend({
    selector: '#document-pane',
    events: {
        'click #btn-add-document': '_openModal',
        'submit #upload-document-form': '_onSubmit',
        'click .btn-delete-doc': '_onDelete',
        'click .btn-edit-doc': '_openEdit',
        'submit #edit-document-form': '_onUpdate',
    },

    start() {
        this.unitId = this.$('input[name="property_unit_id"]').val();
        this.alertContainer = $('#document-alert-container');
        return this._super(...arguments);
    },

    _openModal() {
        $('#uploadDocumentModal').modal('show');
    },

    async _onSubmit(ev) {
        ev.preventDefault();
        const form = ev.currentTarget;
        const spinner = $(form).find('.spinner-border');
        spinner.removeClass('d-none');

        try {
            const file = form.document_file.files[0];
            const base64 = await this._fileToBase64(file);

            const result = await rpc('/property/upload_document', {
                property_unit_id: this.unitId,
                document_type_id: form.document_type_id.value,
                issue_date: form.issue_date.value,
                date_expiry: form.date_expiry.value,
                file_name: file.name,
                document_file: base64.split(',')[1], 
            });

            spinner.addClass('d-none');

            if (result.error) {
                this._showAlert('danger', result.error);
            } else {
                $('#uploadDocumentModal').modal('hide');
                form.reset();
                this._showAlert('success', 'Document uploaded successfully');
                this._reloadTable();
            }
        } catch (err) {
            spinner.addClass('d-none');
            this._showAlert('danger', err.message);
        }
    },

    async _onDelete(ev) {
        const id = $(ev.currentTarget).closest('tr').data('id');
        if (!confirm('Delete this document?')) return;
        const result = await rpc('/property/delete_document', { document_id: id });
        if (result.error) {
            this._showAlert('danger', result.error);
        } else {
            this._showAlert('success', 'Document deleted');
            this._reloadTable();
        }
    },

    async _reloadTable() {
        const rows = await rpc(`/property/document_list/${this.unitId}`);
        const tbody = this.$('#document-table tbody').empty();

        if (rows.length === 0) {
            tbody.append(`<tr><td colspan="6" class="text-center text-muted">Belum ada dokumen</td></tr>`); 
            return;
        }

        rows.forEach(r => {
            let previewHtml = '<span>File</span>';
            if (r.mimetype.includes('image')) {
                previewHtml = `<img src="${r.file_url}?image_zoom=0&amp;width=50&amp;height=50" class="img-thumbnail" alt="Preview"/>`;
            } else if (r.mimetype.includes('pdf')) {
                previewHtml = `<i class="fa fa-file-pdf-o fa-2x text-danger" title="PDF File"></i>`;
            } else {
                previewHtml = `<i class="fa fa-file-o fa-2x text-muted" title="Document File"></i>`;
            }

            const downloadLink = `<a href="${r.file_url}?download=false">${r.file_name}</a>`;
            tbody.append(`<tr data-id="${r.id}"
                                data-type-id="${r.document_type_id}"
                                data-name="${r.document_type}"
                                data-issue="${r.issue_date || ''}"
                                data-expiry="${r.date_expiry || ''}"
                                data-file="${r.file_name}"
                                data-url="${r.file_url}"
                                data-mimetype="${r.mimetype}"> <td>${r.document_type}</td>
                                <td class="text-center">${previewHtml}</td> <td>${downloadLink}</td>
                                <td>${r.issue_date || ''}</td>
                                <td>${r.date_expiry || ''}</td>
                                <td>
                                    <button class="btn btn-sm btn-warning btn-edit-doc">Edit</button>
                                    <button class="btn btn-sm btn-danger btn-delete-doc">Delete</button>
                                </td>
                            </tr>`);
        });
    },

    _openEdit(ev) {
        const tr = $(ev.currentTarget).closest('tr');
        const id = tr.data('id');
        const typeId = tr.data('type-id');
        const issue = tr.data('issue');
        const expiry = tr.data('expiry');
        const fileName = tr.data('file');
        const fileUrl = tr.data('url');
        const mimetype = tr.data('mimetype'); 

        const modal = $('#editDocumentModal');
        modal.find('input[name="document_id"]').val(id);
        modal.find('select[name="document_type_id"]').val(typeId);
        modal.find('input[name="issue_date"]').val(issue);
        modal.find('input[name="date_expiry"]').val(expiry);

        const preview = modal.find('#doc-preview').empty();

        if (mimetype.includes('pdf')) {
            preview.html(`<embed src="${fileUrl}" type="application/pdf" width="100%" height="400px"/>`);
        } else if (mimetype.includes('image')) {
            preview.html(`<img src="${fileUrl}" class="img-fluid rounded" style="max-height:300px;"/>`);
        } else {
            preview.html(`<a href="${fileUrl}?download=true" target="_blank">${fileName}</a>`);
        }

        modal.modal('show');
    },

    async _onUpdate(ev) {
        ev.preventDefault();
        const form = ev.currentTarget;
        const id = form.document_id.value;
        const typeId = form.document_type_id.value;
        const issue = form.issue_date.value;
        const expiry = form.date_expiry.value;

        let fileBase64 = null;
        let fileName = null;
        if (form.document_file.files.length > 0) {
            const file = form.document_file.files[0];
            fileName = file.name;
            const base64 = await this._fileToBase64(file);
            fileBase64 = base64.split(',')[1];
        }

        const result = await rpc('/property/update_document', {
            document_id: id,
            document_type_id: typeId,
            issue_date: issue,
            date_expiry: expiry,
            file_name: fileName,
            document_file: fileBase64,
        });

        if (result.error) {
            this._showAlert('danger', result.error);
        } else {
            $('#editDocumentModal').modal('hide');
            this._showAlert('success', 'Document updated');
            this._reloadTable();
        }
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
