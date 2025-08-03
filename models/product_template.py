from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    # Relación con códigos adicionales (solo para productos SIN variantes)
    additional_barcode_ids = fields.One2many(
        'product.barcode', 
        'product_tmpl_id', 
        string='Códigos de Barras Adicionales',
        help='Códigos de barras alternativos para este producto (solo para productos sin variantes)'
    )
    
    additional_barcode_count = fields.Integer(
        'Códigos Adicionales', 
        compute='_compute_barcode_count'
    )
    
    @api.depends('additional_barcode_ids.active')
    def _compute_barcode_count(self):
        """Contar códigos adicionales activos"""
        for record in self:
            record.additional_barcode_count = len(record.additional_barcode_ids.filtered('active'))
    
    @api.model
    def search_by_any_barcode(self, barcode):
        """Buscar producto por código principal o adicional"""
        if not barcode:
            return self.env['product.template']
            
        barcode = barcode.strip()
        
        # Buscar por código principal
        product = self.search([('barcode', '=', barcode)], limit=1)
        if product:
            return product
            
        # Buscar por códigos adicionales
        barcode_obj = self.env['product.barcode'].search([
            ('barcode', '=', barcode), 
            ('active', '=', True),
            ('product_tmpl_id', '!=', False)
        ], limit=1)
        
        if barcode_obj:
            return barcode_obj.product_tmpl_id
            
        return self.env['product.template']
    
    def get_all_barcodes(self):
        """Obtener todos los códigos de barras del producto"""
        self.ensure_one()
        barcodes = []
        
        # Código principal (solo si no tiene variantes múltiples)
        if self.barcode and len(self.product_variant_ids) <= 1:
            barcodes.append(self.barcode)
            
        # Códigos adicionales activos
        additional_barcodes = self.additional_barcode_ids.filtered('active').mapped('barcode')
        barcodes.extend(additional_barcodes)
        
        return list(set(barcodes))  # Eliminar duplicados