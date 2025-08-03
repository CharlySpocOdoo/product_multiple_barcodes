from odoo import models, api

class PosSession(models.Model):
    _inherit = 'pos.session'
    
    @api.model
    def search_product_by_barcode(self, barcode):
        """Buscar producto en POS por cualquier código de barras"""
        product = self.env['product.product'].search_by_any_barcode(barcode)
        return product