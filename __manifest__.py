{
    'name': 'Multiple Barcodes for Products',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Múltiples códigos de barras por producto - Perfecto para cosméticos y productos con variantes',
    'description': """
	Multiple Barcodes for Products - Versión Híbrida
	================================================

	Este módulo permite gestionar múltiples códigos de barras tanto para:
		* Productos únicos (sin variantes) - ej: Bronceador
		* Productos con variantes (colores, tallas, etc.) - ej: Labiales con diferentes colores

	Características principales:
		* Códigos de barras únicos en todo el sistema
		* Búsqueda automática en POS, Inventario, Ventas y Compras
		* Interfaz intuitiva para gestionar códigos adicionales
		* Compatible con lectores USB/Bluetooth
		* Activar/desactivar códigos específicos
		* Descripciones opcionales para cada código

	Casos de uso ideales:
		* Cosméticos y maquillaje
		* Productos con códigos de diferentes proveedores
		* Migración de sistemas (códigos antiguos vs nuevos)
		* Productos con códigos por unidad vs por caja
    """,
    'author': 'Charly boy',
    'website': 'https://www.rosadelima.mx',
    'depends': ['product', 'stock', 'point_of_sale', 'sale', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}