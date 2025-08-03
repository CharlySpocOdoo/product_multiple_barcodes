from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    # Relación con códigos adicionales (para variantes específicas)
    additional_barcode_ids = fields.One2many(
        'product.barcode', 
        'product_id', 
        string='Códigos de Barras Adicionales de esta Variante'
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
            return self.env['product.product']
            
        barcode = barcode.strip()
        
        # Buscar por código principal en product.product
        product = self.search([('barcode', '=', barcode)], limit=1)
        if product:
            return product
            
        # Buscar por código principal en product.template (productos sin variantes)
        template = self.env['product.template'].search([('barcode', '=', barcode)], limit=1)
        if template and len(template.product_variant_ids) == 1:
            return template.product_variant_ids[0]
            
        # Buscar por códigos adicionales de variantes
        barcode_obj = self.env['product.barcode'].search([
            ('barcode', '=', barcode), 
            ('active', '=', True),
            ('product_id', '!=', False)
        ], limit=1)
        
        if barcode_obj:
            return barcode_obj.product_id
            
        # Buscar por códigos adicionales de plantillas (productos sin variantes)
        barcode_obj = self.env['product.barcode'].search([
            ('barcode', '=', barcode), 
            ('active', '=', True),
            ('product_tmpl_id', '!=', False)
        ], limit=1)
        
        if barcode_obj and barcode_obj.product_tmpl_id.product_variant_ids:
            return barcode_obj.product_tmpl_id.product_variant_ids[0]
            
        return self.env['product.product']
    
    def get_all_barcodes(self):
        """Obtener todos los códigos de barras de la variante"""
        self.ensure_one()
        barcodes = []
        
        # Código principal de la variante
        if self.barcode:
            barcodes.append(self.barcode)
        
        # Código principal de la plantilla (solo si es producto sin variantes)
        if self.product_tmpl_id.barcode and len(self.product_tmpl_id.product_variant_ids) == 1:
            barcodes.append(self.product_tmpl_id.barcode)
            
        # Códigos adicionales de la variante
        variant_barcodes = self.additional_barcode_ids.filtered('active').mapped('barcode')
        barcodes.extend(variant_barcodes)
        
        # Códigos adicionales de la plantilla (solo si es producto sin variantes)
        if len(self.product_tmpl_id.product_variant_ids) == 1:
            template_barcodes = self.product_tmpl_id.additional_barcode_ids.filtered('active').mapped('barcode')
            barcodes.extend(template_barcodes)
        
        return list(set(barcodes))  # Eliminar duplicados
