import pymysql

class ConexionDB:
    def __init__(self, host, user, password, db):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.conexion = None
        self.port=57432

    def conectar(self):
        if self.conexion is None or not self.conexion.open:
            self.conexion = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                cursorclass=pymysql.cursors.Cursor, 
                port=self.port
            )
        return self.conexion

    def obtener_cursor(self):
        return self.conectar().cursor()