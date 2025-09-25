from odoo import http
from odoo.http import request
import base64

class PropertyImageController(http.Controller):

	@http.route('/my/property/upload_image', type='json', auth='user', methods=['POST'], csrf=True)
	def upload_image(self, property_unit_id, sequence, image):
		try:
			unit = request.env['vit.property_unit'].sudo().browse(int(property_unit_id))
			if not unit:
				return {'error': 'Property unit not found'}

			request.env['vit.property_unit_image'].sudo().create({
				'property_unit_id': unit.id,
				'sequence': int(sequence),
				'image': image,
			})
			return {'success': True}
		except Exception as e:
			return {'error': str(e)}

	@http.route('/my/property/image_list/<int:unit_id>', type='json', auth='user')
	def image_list(self, unit_id):
		imgs = request.env['vit.property_unit_image'].sudo().search([('property_unit_id','=',unit_id)], order="sequence asc")
		data = [{
			'id': i.id,
			'name': i.name,
			'sequence': i.sequence,
			'image': i.image,
		} for i in imgs]
		return data

	@http.route('/my/property/update_image', type='json', auth='user', methods=['POST'], csrf=True)
	def update_image(self, image_id, sequence=None, name=None, image=None):
		rec = request.env['vit.property_unit_image'].sudo().browse(int(image_id))
		if not rec.exists():
			return {'error': 'Image not found'}
			
		vals = {}
		if sequence is not None:
			vals['sequence'] = int(sequence)
		if name is not None:
			vals['name'] = name
		if image:  
			vals['image'] = image
		rec.write(vals)
		return {'success': True}

	@http.route('/my/property/delete_image', type='json', auth='user', methods=['POST'], csrf=True)
	def delete_image(self, image_id):
		rec = request.env['vit.property_unit_image'].sudo().browse(int(image_id))
		if not rec.exists():
			return {'error': 'Image not found'}
		rec.unlink()
		return {'success': True}
