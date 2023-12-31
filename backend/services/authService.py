from backend import db
from backend.errors.exceptions import (
    UsuarioNotFoundError,
    CuentaExistenteError,
    PasswordInvalidaError,
)
from backend.models.cliente import Cliente
from backend.models.usuario import Usuario
from backend.utils.passwordService import PasswordService


class AuthService:
    @staticmethod
    def registrar_usuario(
        username,
        password,
        email,
    ):
        """
        Registra un nuevo usuario y crea un cliente asociado.
        :param username: Nombre de usuario.
        :param password: Contraseña.
        :param email: Correo electrónico.
        :return: Mensaje indicando el éxito de la operación.
        """

        if PasswordService.validar_formato_password(password) is False:
            raise PasswordInvalidaError()

        # Verificar si el nombre de usuario o correo electrónico ya existen
        email_existente = Usuario.query.filter_by(email=email).first()

        if email_existente:
            raise CuentaExistenteError("Correo electrónico ya registrado.")

        usuario_existente = Usuario.query.filter_by(username=username).first()

        if usuario_existente:
            raise CuentaExistenteError("Nombre de usuario ya registrado.")

        # Hash de la contraseña antes de almacenarla en la base de datos
        # password = PasswordService.hash_password(password)

        # Crea un nuevo usuario
        nuevo_usuario = Usuario(
            username=username,
            password=password,
            email=email,
        )
        # Crea un nuevo cliente asociado al usuario y por defecto con el mismo nombre de usuario
        nuevo_cliente = Cliente(nombre=username)
        nuevo_cliente.usuario = nuevo_usuario

        db.session.add(nuevo_usuario)
        db.session.add(nuevo_cliente)
        db.session.commit()

        return nuevo_cliente.to_dict()

    @staticmethod
    def login(
        email,
        password,
    ):
        """
        Inicia sesión y retorna el usuario.
        :param email: Correo electrónico del usuario.
        :param password: Contraseña del usuario.
        :return: Usuario que inició sesión.
        """
        usuario = Usuario.query.filter_by(email=email).first()

        # if usuario is None or check_password_hash(usuario.password, password):
        #     raise UsuarioNotFoundError(
        #         "Nombre de usuario o contraseña incorrectos."
        #     )

        if not usuario or usuario.password != password:
            raise UsuarioNotFoundError(
                "Nombre de usuario o contraseña incorrectos."
            )

        cliente = usuario.cliente
        empleado = usuario.empleado

        user_data = {}
        if cliente:
            user_data = cliente.to_dict()

        if empleado:
            user_data = empleado.to_dict()

        return user_data

    @staticmethod
    def eliminar_cuenta(
        email,
        password,
    ):
        """
        Elimina la cuenta de un usuario y el cliente asociado.
        :param password: Contraseña del usuario.
        :param email: Correo electrónico del usuario.
        :return: Mensaje indicando el éxito de la operación.
        """

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario or usuario.password != password:
            raise UsuarioNotFoundError(
                "Email de usuario o contraseña incorrectos."
            )

        # Busca el cliente asociado
        cliente = usuario.cliente
        if not cliente:
            raise UsuarioNotFoundError(
                "El usuario no tiene un cliente asociado."
            )
        # Eliminar cliente asociado
        db.session.delete(cliente)

        # Eliminar usuario
        db.session.delete(usuario)
        db.session.commit()
