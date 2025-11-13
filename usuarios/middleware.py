from django.contrib.auth import get_user_model
from usuarios.models import Rol, Administrador

Usuario = get_user_model()


class CrearAdminMiddleware:
    """
    Middleware que crea un usuario administrador automáticamente
    al iniciar la aplicación.
    """
    _admin_creado = False

    def __init__(self, get_response):
        self.get_response = get_response
        # Crear admin al inicializar el middleware (primera request)
        if not CrearAdminMiddleware._admin_creado:
            self._crear_admin()
            CrearAdminMiddleware._admin_creado = True

    def __call__(self, request):
        response = self.get_response(request)
        return response

    @staticmethod
    def _crear_admin():
        """Crea el usuario administrador si no existe"""
        try:
            if Usuario.objects.filter(is_superuser=True).exists():
                return

            # Crear o obtener el rol de administrador
            rol_admin, _ = Rol.objects.get_or_create(
                nombre='Administrador'
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

            print("✓ Usuario administrador creado exitosamente")
            print("  Email: admin@sales365.com")
            print("  Contraseña: admin123")
        except Exception as e:  # pylint: disable=broad-except
            if 'duplicate key value' not in str(e):
                print(f"Error al crear usuario administrador: {e}")
