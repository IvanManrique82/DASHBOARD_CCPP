import streamlit as st
import bcrypt  # Añadir bcrypt para manejar el cifrado de contraseñas

# Función para verificar la contraseña cifrada
def verificar_contraseña(contraseña, hash_contraseña):
    # Asegurarse de que el hash esté en formato de bytes
    if isinstance(hash_contraseña, str):
        hash_contraseña = hash_contraseña.encode('utf-8')
    
    # Comparar la contraseña ingresada con el hash
    return bcrypt.checkpw(contraseña.encode('utf-8'), hash_contraseña)

def login(usuarios):
    st.sidebar.title("Iniciar Sesión")
    user = st.sidebar.text_input("Usuario", key="user_input")
    password = st.sidebar.text_input("Contraseña", type="password", key="password_input")

    # Verificar que el archivo tenga la columna HASH_CONTRASEÑA
    if 'HASH_CONTRASEÑA' not in usuarios.columns:
        st.sidebar.error("El archivo de usuarios no tiene la columna 'HASH_CONTRASEÑA'.")
        return None, False

    # Botón de inicio de sesión
    if st.sidebar.button("Iniciar Sesión"):
        for _, row in usuarios.iterrows():
            try:
                # Verificar la contraseña cifrada
                if user == row['USUARIO'] and verificar_contraseña(password, row['HASH_CONTRASEÑA']):
                    st.sidebar.success(f"Bienvenido, {user}")
                    
                    # Verificar si es un administrador
                    if row['NOMBRE DE COLABORADOR'] == "Ivan Manrique" or row['NOMBRE DE COLABORADOR'] == "SUPER ADMIN":
                        return "Todos", True  # Administradores ven todos los colaboradores
                    
                    # Otros colaboradores solo ven sus propios datos
                    return row['NOMBRE DE COLABORADOR'], False
            
            except Exception as e:
                st.sidebar.error(f"Error en la autenticación: {e}")
                return None, False
        
        st.sidebar.error("Usuario o contraseña incorrectos")
    
    return None, False
