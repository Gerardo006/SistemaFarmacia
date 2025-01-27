from enum import Enum
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class EstadoPedido(Enum):
    PENDIENTE = 'pendiente'
    ENVIADO = 'enviado'
    COMPLETADO = 'completado'

class EstadoEntrega(Enum):
    RETIRO_SUCURSAL = 'retiro_sucursal'
    ENVIO_A_SUCURSAL = 'envio_a_sucursal'

class Roles(Enum):
    ADMINISTRADOR = 'admin'
    EMPLEADO = 'empleado'
    CLIENTE = 'cliente'




class Persona(models.Model):
    """
    Clase abstracta para definir atributos comunes entre Administradores y Empleados.
    """
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField()

    class Meta:
        abstract = True

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def __str__(self):
        return self.nombre_completo()

class Administrador(Persona):
    """
    Modelo que hereda de Persona, específico para administradores.
    """
    nivel_acceso = models.CharField(max_length=50, default="Administrador General")  # Ejemplo de campo exclusivo

    def __str__(self):
        return f"Administrador: {self.nombre_completo()}"

class Empleado(Persona):
    """
    Modelo que hereda de Persona, específico para empleados.
    """
    sucursal = models.OneToOneField('Sucursal', on_delete=models.CASCADE, related_name="empleados")
    

    def __str__(self):
        return f"Empleado: {self.nombre_completo()} en {self.sucursal.nombre}"

# ------------------------------------------------------------
# AUTENTICACIÓN DE USUARIOS Y ROLES
# ------------------------------------------------------------
class Usuario(AbstractUser):
    roles = models.CharField(max_length=20, choices=[(tag.name, tag.value) for tag in Roles],
                             default=Roles.CLIENTE.name)
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # Cambiar el related_name
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",  # Cambiar el related_name
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return f"{self.username} ({self.roles})"


# ------------------------------------------------------------
# MODELOS BASE
# ------------------------------------------------------------
class Sucursal(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    id_producto = models.CharField(
        max_length=4, unique=True, editable=False, null=True, blank=True
    )
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    def save(self, *args, **kwargs):
        if not self.id_producto:
            ultimo_id = Producto.objects.all().count()+1
            self.id_producto = f'P{ultimo_id:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.id_producto})"


class Inventario(models.Model):
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE, related_name='inventarios')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='inventarios')
    cantidad = models.PositiveIntegerField()

    class Meta:
        unique_together = ('sucursal', 'producto')

    def __str__(self):
        return f"{self.producto.nombre} - {self.sucursal.nombre}: {self.cantidad} en stock"


# ------------------------------------------------------------
# MODELOS DE VENTA Y PEDIDOS
# ------------------------------------------------------------
class Cliente(Persona):
    id_cliente = models.CharField(
    max_length=4, unique=True, editable=False, null=True, blank=True
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Generar el ID si no existe
        if not self.id_cliente:
            ultimo_id = Cliente.objects.count() + 1
            self.id_cliente = f'C{ultimo_id:04d}'  # Ejemplo: C0001, C0002, etc.
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cliente: {self.id_cliente} - {self.nombre_completo()}"





class Pedido(models.Model):
    estado = models.CharField(max_length=20, choices=[(tag.name, tag.value) for tag in EstadoPedido],
    default=EstadoPedido.PENDIENTE.name)


    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    sucursal_origen = models.ForeignKey(
        Sucursal, on_delete=models.CASCADE, related_name='pedidos_origen'
    )
    sucursal_destino = models.ForeignKey(
        Sucursal, on_delete=models.CASCADE, related_name='pedidos_destino', null=True, blank=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} de {self.cliente.nombre_completo()} - Estado: {self.estado}"


class Venta(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='ventas')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='ventas')
    cantidad = models.PositiveIntegerField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calcular precio total
        self.precio_total = self.cantidad * self.producto.precio

        # Validar inventario de la sucursal
        inventario = Inventario.objects.get(
            sucursal=self.pedido.sucursal_origen, producto=self.producto
        )
        if inventario.cantidad < self.cantidad:
            raise ValueError(f"Stock insuficiente para {self.producto.nombre}")

        # Reducir cantidad
        inventario.cantidad -= self.cantidad
        inventario.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Venta de {self.cantidad}x {self.producto.nombre}"


# ------------------------------------------------------------
# TRANSFERENCIAS ENTRE SUCURSALES
# ------------------------------------------------------------
class Transferencia(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='transferencias')
    sucursal_origen = models.ForeignKey(
        Sucursal, on_delete=models.CASCADE, related_name='transferencias_origen'
    )
    sucursal_destino = models.ForeignKey(
        Sucursal, on_delete=models.CASCADE, related_name='transferencias_destino'
    )
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Reducir stock de la sucursal origen
        inventario_origen = Inventario.objects.get(
            sucursal=self.sucursal_origen, producto=self.producto
        )
        if inventario_origen.cantidad < self.cantidad:
            raise ValueError(f"No hay suficiente stock en {self.sucursal_origen.nombre}")

        inventario_origen.cantidad -= self.cantidad
        inventario_origen.save()

        # Aumentar stock en la sucursal destino
        inventario_destino, created = Inventario.objects.get_or_create(
            sucursal=self.sucursal_destino, producto=self.producto, defaults={'cantidad': 0}
        )
        inventario_destino.cantidad += self.cantidad
        inventario_destino.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transferencia de {self.cantidad}x {self.producto.nombre}"


# ------------------------------------------------------------
# OPCIONES DE ENTREGA
# ------------------------------------------------------------
class Entrega(models.Model):
    opcion=models.CharField(max_length=20, choices=[(tag.name, tag.value) for tag in EstadoEntrega],
    default=EstadoEntrega.RETIRO_SUCURSAL.name)

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='entrega')
    fecha_entrega = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Entrega: {self.opcion} para Pedido {self.pedido.id}"

#------------------------------------------------------------
# MODELOS DE FACTURACIÓN
# ------------------------------------------------------------
class Factura(models.Model):
    pedido = models.OneToOneField(
        Pedido, on_delete=models.CASCADE, related_name='factura'
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name='facturas'
    )
    fecha_emision = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        """
        Al guardar una factura, calcular el total automáticamente
        basado en las ventas asociadas al pedido.
        """
        ventas = self.pedido.ventas.all()
        self.total = sum(venta.precio_total for venta in ventas)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Factura {self.id} - Pedido {self.pedido.id} - Total: ${self.total}"