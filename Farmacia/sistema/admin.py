from django.contrib import admin
from .models import Usuario, Sucursal, Producto, Inventario, Cliente, Pedido, Venta, Transferencia, Entrega, Factura, Administrador, Empleado


# Personalización de los modelos en el admin


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'roles')
    list_filter = ('roles',)
    search_fields = ('username', 'email')
    list_editable = ('roles',)


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'telefono')
    search_fields = ('nombre', 'direccion')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'nombre', 'precio')
    search_fields = ('id_producto', 'nombre')
    list_filter = ('precio',)


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('sucursal', 'producto', 'cantidad')
    list_filter = ('sucursal', 'producto')
    search_fields = ('producto__nombre', 'sucursal__nombre')


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id_cliente', 'nombre_completo', 'telefono')
    search_fields = ('id_cliente', 'nombre')

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'telefono')
    search_fields = ('nombre', 'apellido', 'email')
    list_filter = ('nombre',)

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'email', 'telefono', 'sucursal')
    search_fields = ('nombre', 'apellido', 'email')
    list_filter = ('sucursal', 'nombre')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'sucursal_origen', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion', 'sucursal_origen', 'sucursal_destino')
    search_fields = ('cliente__nombre', 'estado')
    list_editable = ('estado',)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_total', 'fecha')
    list_filter = ('fecha', 'producto', 'pedido')
    search_fields = ('producto__nombre', 'pedido__cliente__nombre')


@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'sucursal_origen', 'sucursal_destino', 'cantidad', 'fecha')
    list_filter = ('sucursal_origen', 'sucursal_destino', 'producto', 'fecha')
    search_fields = ('producto__nombre', 'sucursal_origen__nombre', 'sucursal_destino__nombre')


@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'opcion', 'fecha_entrega')
    list_filter = ('opcion',)
    search_fields = ('pedido__cliente__nombre',)
    list_editable = ('opcion',)


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'cliente', 'fecha_emision', 'total')
    list_filter = ('fecha_emision',)
    search_fields = ('pedido__cliente__nombre', 'total')