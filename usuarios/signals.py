from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Rol, Administrador

Usuario = get_user_model()


@receiver(post_migrate)
def crear_usuario_admin(sender, **kwargs):
    """
    Crea un usuario administrador automáticamente después de las migraciones.
    Se ejecuta solo si no existe ya un superusuario.
    """
    if sender.name == 'usuarios':
        # Verificar si ya existe un superusuario
        if Usuario.objects.filter(is_superuser=True).exists():
            return

        # Crear o obtener el rol de administrador
        rol_admin, _ = Rol.objects.get_or_create(
            nombre='Administrador',
            defaults={'nombre': 'Administrador'}
        )

        # Crear el usuario administrador
        try:
            usuario_admin = Usuario.objects.create_superuser(
                email='admin@sales365.com',
                password='admin123',
                nombre='Administrador',
            )

            # Asignar el rol de administrador
            usuario_admin.rol = rol_admin
            usuario_admin.save()

            # Crear la relación en la tabla Administrador
            Administrador.objects.get_or_create(administrador=usuario_admin)

            print("✓ Usuario administrador creado exitosamente")
            print("  Email: admin@sales365.com")
            print("  Contraseña: admin123")
        except Exception as e:  # pylint: disable=broad-except
            print(f"Error al crear usuario administrador: {e}")

