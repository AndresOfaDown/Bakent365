from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from usuarios.models import Rol, Administrador, Cliente

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Inicializa los datos básicos: roles y usuarios de prueba'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🔧 Iniciando configuración de datos...'))
        
        # 1. Crear roles
        self.stdout.write('\n📋 Creando roles...')
        rol_admin, created = Rol.objects.get_or_create(
            nombre='Administrador',
            defaults={'nombre': 'Administrador'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Rol "Administrador" creado'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Rol "Administrador" ya existe'))

        rol_cliente, created = Rol.objects.get_or_create(
            nombre='Cliente',
            defaults={'nombre': 'Cliente'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Rol "Cliente" creado'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Rol "Cliente" ya existe'))

        # 2. Crear usuario administrador
        self.stdout.write('\n👤 Creando usuario administrador...')
        if not Usuario.objects.filter(email='admin@sales365.com').exists():
            try:
                usuario_admin = Usuario.objects.create_superuser(
                    email='admin@sales365.com',
                    password='admin123',
                    nombre='Administrador Sistema',
                    telefono='12345678',
                    estado=1
                )
                usuario_admin.rol = rol_admin
                usuario_admin.save()

                Administrador.objects.get_or_create(administrador=usuario_admin)

                self.stdout.write(self.style.SUCCESS('  ✓ Usuario administrador creado'))
                self.stdout.write(self.style.SUCCESS('    Email: admin@sales365.com'))
                self.stdout.write(self.style.SUCCESS('    Contraseña: admin123'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error al crear administrador: {e}'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Usuario administrador ya existe'))

        # 3. Crear usuario cliente
        self.stdout.write('\n👤 Creando usuario cliente...')
        if not Usuario.objects.filter(email='cliente@sales365.com').exists():
            try:
                usuario_cliente = Usuario.objects.create_user(
                    email='cliente@sales365.com',
                    password='cliente123',
                    nombre='Cliente Demo',
                    telefono='87654321',
                    estado=1
                )
                usuario_cliente.rol = rol_cliente
                usuario_cliente.save()

                Cliente.objects.get_or_create(cliente=usuario_cliente)

                self.stdout.write(self.style.SUCCESS('  ✓ Usuario cliente creado'))
                self.stdout.write(self.style.SUCCESS('    Email: cliente@sales365.com'))
                self.stdout.write(self.style.SUCCESS('    Contraseña: cliente123'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error al crear cliente: {e}'))
        else:
            self.stdout.write(self.style.WARNING('  ⚠ Usuario cliente ya existe'))

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✅ Configuración completada'))
        self.stdout.write('='*50)
        self.stdout.write(self.style.SUCCESS('\n📝 Credenciales de prueba:'))
        self.stdout.write(self.style.SUCCESS('\n  ADMINISTRADOR:'))
        self.stdout.write(self.style.SUCCESS('    Email: admin@sales365.com'))
        self.stdout.write(self.style.SUCCESS('    Password: admin123'))
        self.stdout.write(self.style.SUCCESS('\n  CLIENTE:'))
        self.stdout.write(self.style.SUCCESS('    Email: cliente@sales365.com'))
        self.stdout.write(self.style.SUCCESS('    Password: cliente123'))
        self.stdout.write('\n')
