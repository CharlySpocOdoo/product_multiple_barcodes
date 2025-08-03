from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductBarcode(models.Model):
    _name = 'product.barcode'
    _description = 'Códigos de Barras Adicionales del Producto'
    _order = 'sequence, id'
    _rec_name = 'barcode'
    
    # Campos básicos
    barcode = fields.Char(
        'Código de Barras', 
        required=True, 
        index=True,
        help='Código de barras adicional para el producto'
    )
    name = fields.Char(
        'Descripción', 
        help='Descripción opcional del código (ej: Código proveedor A, Código anterior, etc.)'
    )
    sequence = fields.Integer('Secuencia', default=10)
    active = fields.Boolean('Activo', default=True)
    
    # Relaciones híbridas - Solo una puede tener valor
    product_tmpl_id = fields.Many2one(
        'product.template', 
        string='Producto (Sin Variantes)', 
        ondelete='cascade',
        index=True,
        help='Para productos que no tienen variantes'
    )
    product_id = fields.Many2one(
        'product.product', 
        string='Variante de Producto', 
        ondelete='cascade',
        index=True,
        help='Para productos con variantes específicas'
    )
    
    # Campos computados para mostrar información
    product_name = fields.Char(
        'Nombre del Producto', 
        compute='_compute_product_info', 
        store=True
    )
    product_type = fields.Selection([
        ('template', 'Producto Sin Variantes'),
        ('variant', 'Variante de Producto')
    ], string='Tipo', compute='_compute_product_info', store=True)
    
    # Restricciones SQL
    _sql_constraints = [
        ('barcode_unique', 'unique(barcode)', 
         'El código de barras debe ser único en todo el sistema!'),
        ('check_product_relation', 
         'CHECK((product_tmpl_id IS NOT NULL AND product_id IS NULL) OR (product_tmpl_id IS NULL AND product_id IS NOT NULL))', 
         'El código debe estar asociado a un producto SIN variantes O a una variante específica, no ambos.'),
    ]
    
    @api.depends('product_tmpl_id', 'product_id')
    def _compute_product_info(self):
        """Calcular información del producto asociado"""
        for record in self:
            if record.product_tmpl_id:
                record.product_name = record.product_tmpl_id.name
                record.product_type = 'template'
            elif record.product_id:
                record.product_name = record.product_id.display_name
                record.product_type = 'variant'
            else:
                record.product_name = False
                record.product_type = False
    

	

    @api.constrains('barcode')
    def _check_barcode_format(self):
        """Validar formato y unicidad del código de barras"""
        for record in self:
            if record.barcode:
                # Limpiar espacios
                barcode_clean = record.barcode.strip()
                if not barcode_clean:
                    raise ValidationError("El código de barras no puede estar vacío.")
                
                # SOLO actualizar si es diferente (evita bucle infinito)
                if record.barcode != barcode_clean:
                    # Usar write directo sin disparar validaciones
                    record.write({'barcode': barcode_clean})
                
                # Verificar que no exista en códigos principales de product.template
                existing_template = self.env['product.template'].search([
                    ('barcode', '=', barcode_clean),
                    ('id', '!=', record.product_tmpl_id.id if record.product_tmpl_id else False)
                ])
                if existing_template:
                    raise ValidationError(
                        f"El código '{barcode_clean}' ya existe como código principal "
                        f"en el producto '{existing_template.name}'"
                    )
                
                # Verificar que no exista en códigos principales de product.product
                existing_product = self.env['product.product'].search([
                    ('barcode', '=', barcode_clean),
                    ('id', '!=', record.product_id.id if record.product_id else False)
                ])
                if existing_product:
                    raise ValidationError(
                        f"El código '{barcode_clean}' ya existe como código principal "
                        f"en la variante '{existing_product.display_name}'"
                    )
                
                # Verificar que no exista en otros códigos adicionales
                existing_barcode = self.env['product.barcode'].search([
                    ('barcode', '=', barcode_clean),
                    ('id', '!=', record.id)
                ])
                if existing_barcode:
                    raise ValidationError(
                        f"El código '{barcode_clean}' ya existe como código adicional "
                        f"en otro producto"
                    )


    
    @api.constrains('product_tmpl_id', 'product_id')
    def _check_product_assignment(self):
        """Validar que solo uno de los productos esté asignado"""
        for record in self:
            if not record.product_tmpl_id and not record.product_id:
                raise ValidationError("Debe asignar el código a un producto o variante.")
            if record.product_tmpl_id and record.product_id:
                raise ValidationError("No puede asignar el código a ambos: producto y variante.")
    
    def name_get(self):
        """Personalizar nombre mostrado en vistas"""
        result = []
        for record in self:
            name = record.barcode
            if record.name:
                name = f"{record.barcode} - {record.name}"
            result.append((record.id, name))
        return result
    
    @api.model
    def search_product_by_barcode(self, barcode):
        """Buscar cualquier producto por código de barras adicional"""
        if not barcode:
            return False
            
        barcode = barcode.strip()
        barcode_record = self.search([
            ('barcode', '=', barcode),
            ('active', '=', True)
        ], limit=1)
        
        if barcode_record:
            if barcode_record.product_tmpl_id:
                # Producto sin variantes - devolver la única variante
                return barcode_record.product_tmpl_id.product_variant_ids[0] if barcode_record.product_tmpl_id.product_variant_ids else False
            elif barcode_record.product_id:
                # Variante específica
                return barcode_record.product_id
        
        return False