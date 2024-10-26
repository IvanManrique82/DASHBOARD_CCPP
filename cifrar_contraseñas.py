import bcrypt
import pandas as pd

# Cargar usuarios
usuarios = pd.read_excel("usuarios.xlsx")

# Función para encriptar una contraseña
def encriptar_contraseña(contraseña):
    # Ciframos la contraseña y la convertimos a string con decode('utf-8')
    return bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Crear una nueva columna con las contraseñas encriptadas
usuarios['HASH_CONTRASEÑA'] = usuarios['CONTRASEÑA'].apply(encriptar_contraseña)

# Guardar el archivo Excel con las contraseñas cifradas
usuarios.to_excel("usuarios_actualizado.xlsx", index=False)

print("El archivo 'usuarios_actualizado.xlsx' se ha generado con contraseñas cifradas.")
