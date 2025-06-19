from flask import Flask, jsonify, request
from conexion import ConexionDB  
from flask_cors import CORS
import hashlib


app = Flask(__name__)
CORS(app)

# Configuración
app.config['MYSQL_HOST'] = 'shuttle.proxy.rlwy.net'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'jQxRvwPOTCjethKdlqEYRxipeeibgJUq'
app.config['MYSQL_DB'] = 'VENTAS'

# Instancia de conexión
db = ConexionDB(
    app.config['MYSQL_HOST'],
    app.config['MYSQL_USER'],
    app.config['MYSQL_PASSWORD'],
    app.config['MYSQL_DB']
)


@app.route('/')
def index():
    return 'Hola Mundo'


@app.route('/usuario', methods=['GET'])
def listar_usuarios():
    try:
        cursor = db.obtener_cursor()
        cursor.execute("SELECT idemp, usuario, clave, estado FROM USUARIO")
        datos = cursor.fetchall()
        usuarios = [{'idemp': row[0], 'usuario': row[1], 'clave': row[2], 'estado': row[3]} for row in datos]
        return jsonify({'usuarios': usuarios, 'mensaje': "Usuarios listados.", 'exito': True})
    except Exception as ex:
        print(f"Error al listar usuarios: {ex}")
        return jsonify({'mensaje': "Error al obtener usuarios", 'exito': False})


@app.route('/usuario/<int:id>', methods=['GET'])
def listar_usuario_por_id(id):
    try:
        usuario = leer_usuario_bd_by_id(id)
        if usuario:
            return jsonify(usuario)
        else:
            return jsonify({'mensaje': "Usuario no encontrado", 'exito': False}), 404
    except Exception as ex:
        return jsonify({'mensaje': "Error al obtener el usuario", 'exito': False})

#-------------------

@app.route('/usuario', methods=['POST'])
def registrar_usuario():
    if (request.json['idemp'] and request.json['usuario'] and request.json['clave'] and request.json['estado'] ):
        try:
            usuario = leer_usuario_bd_by_id(request.json['idemp'])
            if usuario != None:
                return jsonify({'mensaje': "Código ya existe, no se puede duplicar.", 'exito': False})
            else:
                cursor = db.obtener_cursor()
                sql = """INSERT INTO USUARIO (idemp, usuario, clave, estado) 
                VALUES ('{0}', '{1}', '{2}', '{3}')""".format(request.json['idemp'], request.json['usuario'],hashlib.sha1(request.json['clave'].encode('utf-8')).hexdigest(), request.json['estado'])
                cursor.execute(sql)
                db.conexion.commit()  # Confirma la acción de inserción.
                return jsonify({'mensaje': "Usuario registrado.", 'exito': True})
        except Exception as ex:
            print(f"Error al registrar usuario: {ex}")
            return jsonify({'mensaje': 'error', 'exito': False})
    else:
        return jsonify({'mensaje': "Parámetros inválidos...", 'exito': False})


def leer_usuario_bd_by_id(id):
    try:
        cursor = db.obtener_cursor()
        cursor.execute("SELECT idemp, usuario, clave, estado FROM USUARIO WHERE idemp = %s", (id,))
        datos = cursor.fetchone()
        if datos != None:
            usuario = {'idemp': datos[0], 'usuario': datos[1], 'clave': datos[2], 'estado': datos[3]}
            return usuario
        else:
            return None
    except Exception as ex:
        raise ex

@app.route('/usuario/<id>', methods=['PUT'])
def actualizar_usuario(id):
    if (request.json['usuario'] and request.json['clave'] and request.json['estado'] is not None):
        try:
            usuario = leer_usuario_bd_by_id(id)
            if usuario != None:
                cursor = db.obtener_cursor()
                sql = """UPDATE USUARIO SET usuario = '{0}', clave = '{1}' , estado = '{2}' 
                WHERE idemp = '{3}'""".format(request.json['usuario'], hashlib.sha1(request.json['clave'].encode('utf-8')).hexdigest(), request.json['estado'], id)
                cursor.execute(sql)
                db.conexion.commit()  # Confirma la acción de actualización.
                return jsonify({'mensaje': "Usuario actualizado.", 'exito': True})
            else:
                return jsonify({'mensaje': "Usuario no encontrado.", 'exito': False})
        except Exception as ex:
            return jsonify({'mensaje': "Error", 'exito': False})
    else: 
        return jsonify({'mensaje': "Parámetros inválidos...", 'exito': False})


@app.route('/usuario/<id>', methods=['DELETE'])
def eliminar_usuario(id):
    try:
        usuario = leer_usuario_bd_by_id(id)
        if usuario != None:
            cursor = db.obtener_cursor()
            sql = "DELETE FROM USUARIO WHERE idemp = '{0}'".format(id)
            cursor.execute(sql)
            db.conexion.commit()  # Confirma la acción de eliminación.
            return jsonify({'mensaje': "Usuario eliminado.", 'exito': True})
        else:
            return jsonify({'mensaje': "Usuario no encontrado.", 'exito': False})
    except Exception as ex:
        return jsonify({'mensaje': "Error", 'exito': False})


@app.route('/usuario/login', methods=['POST'])
def autenticar_usuario():
    if (request.json['usuario'] and request.json['password']):
        try:
            cursor = db.obtener_cursor()
            # sql = "SELECT  nombre, usuario FROM usuario WHERE usuario = '{0}' and password='{1}'".format(request.json['usuario'], request.json['password'])
            sql = "SELECT  idemp, usuario, clave FROM USUARIO WHERE usuario = '{0}'".format(request.json['usuario'])
            cursor.execute(sql)
            datos = cursor.fetchone()
            if datos is None:
                return jsonify({'mensaje': 'Usuario no encontrado', 'exito': False}), 404

            clave_hash = hashlib.sha1(request.json['password'].encode('utf-8')).hexdigest()
            if clave_hash == datos[2]:
                return jsonify({
                    'mensaje': 'Login exitoso',
                    'exito': True,
                    'usuario': {
                        'idemp': datos[0],
                        'usuario': datos[1],
                    }
                })
            else:
                return jsonify({'mensaje': 'Contraseña incorrecta', 'exito': False}), 401
            
        except Exception as ex:
            return jsonify({'mensaje': ex, 'exito': False})
    else:
        return jsonify({'mensaje': "Parámetros inválidos...", 'exito': False})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)