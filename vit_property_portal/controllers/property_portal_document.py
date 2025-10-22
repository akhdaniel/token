from odoo import http
from odoo.http import request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import base64, tempfile, os, json
import logging
_logger = logging.getLogger(__name__)

class PropertyPortalDocument(http.Controller):

	@http.route('/property/upload_document', type='json', auth="user")
	def upload_document(self, property_unit_id, document_type_id, issue_date, date_expiry, file_name, document_file):
		try:
			doc = request.env['vit.property_document'].sudo().create({
				'property_unit_id': int(property_unit_id),
				'name': int(document_type_id),
				'issue_date': issue_date or False,
				'date_expiry': date_expiry or False,
				'file_name': file_name,
				'document_file': document_file,
			})
			return {'id': doc.id}
		except Exception as e:
			return {'error': str(e)}

	@http.route('/property/delete_document', type='json', auth="user")
	def delete_document(self, document_id):
		try:
			doc = request.env['vit.property_document'].sudo().browse(int(document_id))
			if doc.exists():
				doc.unlink()
			return {'success': True}
		except Exception as e:
			return {'error': str(e)}

	@http.route('/property/document_list/<int:unit_id>', type='json', auth="user")
	def document_list(self, unit_id):
		docs = request.env['vit.property_document'].sudo().search([('property_unit_id', '=', unit_id)])
		res = []
		for d in docs:
			attachment = request.env['ir.attachment'].sudo().search([
				('res_model', '=', 'vit.property_document'),
				('res_id', '=', d.id),
				('res_field', '=', 'document_file')
			], limit=1)
			file_url = f"/web/content/vit.property_document/{d.id}/document_file"
			res.append({
				'id': d.id,
				'document_type': d.name.name,
				'document_type_id': d.name.id,
				'file_name': d.file_name,
				'file_url': file_url, 
				'mimetype': attachment.mimetype if attachment else 'application/octet-stream', 
				'issue_date': d.issue_date and str(d.issue_date) or '',
				'date_expiry': d.date_expiry and str(d.date_expiry) or '',
			})
		return res

	@http.route('/property/update_document', type='json', auth="user")
	def update_document(self, document_id, document_type_id, issue_date=None, date_expiry=None, file_name=None, document_file=None):
		try:
			doc = request.env['vit.property_document'].sudo().browse(int(document_id))
			if not doc.exists():
				return {'error': 'Document not found'}

			vals = {
				'name': int(document_type_id),
				'issue_date': issue_date or False,
				'date_expiry': date_expiry or False,
			}
			if file_name and document_file:
				vals.update({
					'file_name': file_name,
					'document_file': document_file,
				})

			doc.write(vals)
			return {'success': True}
		except Exception as e:
			return {'error': str(e)}

	@http.route('/property/upload_document_to_drive', type='json', auth="user")
	def upload_document_to_drive(self, property_unit_id, document_type_id, issue_date, date_expiry, file_name, document_file):
		try:
			creds_data = request.env['ir.config_parameter'].sudo().get_param('google_drive_credentials_json')
			if not creds_data:
				return {'error': 'Google Drive belum dikonfigurasi. Silakan hubungkan dulu.'}

			creds = Credentials.from_authorized_user_info(json.loads(creds_data))
			service = build('drive', 'v3', credentials=creds)

			# Ambil data properti
			property_unit = request.env['vit.property_unit'].sudo().browse(int(property_unit_id))

			# === [1] Buat folder Google Drive jika belum ada ===
			if not property_unit.google_drive_folder_id:
				folder_metadata = {
					'name': f"Property_{property_unit.name}",
					'mimeType': 'application/vnd.google-apps.folder',
				}
				folder = service.files().create(body=folder_metadata, fields='id, webViewLink').execute()

				property_unit.write({
					'google_drive_folder_id': folder['id'],
					'google_drive_folder_link': folder['webViewLink'],
				})

			# === [2] Simpan file sementara ===
			temp_path = tempfile.mktemp(suffix=os.path.splitext(file_name)[1])
			with open(temp_path, 'wb') as f:
				f.write(base64.b64decode(document_file))

			# === [3] Upload file ke folder milik unit ===
			file_metadata = {
				'name': file_name,
				'parents': [property_unit.google_drive_folder_id],
			}
			media = MediaFileUpload(temp_path, resumable=True)
			uploaded = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()

			os.remove(temp_path)

			# === [4] Simpan dokumen di database (tanpa link Drive) ===
			doc = request.env['vit.property_document'].sudo().create({
				'property_unit_id': property_unit.id,
				'name': int(document_type_id),
				'issue_date': issue_date or False,
				'date_expiry': date_expiry or False,
				'file_name': file_name,
				'document_file': document_file,
			})

			return {
				'success': True,
				'message': 'Dokumen berhasil diunggah ke folder Google Drive unit ini.',
				'folder_link': property_unit.google_drive_folder_link
			}

		except Exception as e:
			return {'error': str(e)}
