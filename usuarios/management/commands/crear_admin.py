from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from usuarios.models import Rol, Administrador

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Crea un usuario administrador automáticamente si no existe'

    def handle(self, *args, **options):
        # Verificar si ya existe un superusuario
        if Usuario.objects.filter(is_superuser=True).exists():
            msg = 'Ya existe un usuario administrador'
            self.stdout.write(self.style.WARNING(msg))
            return

        try:
            # Crear o obtener el rol de administrador
            rol_admin, created = Rol.objects.get_or_create(
                nombre='Administrador',
                defaults={'nombre': 'Administrador'}
            )

            # Crear el usuario administrador
            usuario_admin = Usuario.objects.create_superuser(
                email='admin@sales365.com',
                password='admin123',
                nombre='Administrador',
            )

            # Asignar el rol de administrador
            usuario_admin.rol = rol_admin
            usuario_admin.save()

            # Crear la relación en la tabla Administrador
            Administrador.objects.get_or_create(
                administrador=usuario_admin
            )

            msg1 = '✓ Usuario administrador creado exitosamente'
            self.stdout.write(self.style.SUCCESS(msg1))
            msg2 = '  Email: admin@sales365.com'
            self.stdout.write(self.style.SUCCESS(msg2))
            msg3 = '  Contraseña: admin123'
            self.stdout.write(self.style.SUCCESS(msg3))
        except Exception as e:
            msg_error = f'Error al crear usuario administrador: {e}'
            self.stdout.write(self.style.ERROR(msg_error))
