import streamlit as st
import plotly.express as px
from data_manager import load_data, load_usuarios
from auth import login
import pandas as pd

# Cargar los datos
data = load_data("clientes.xlsx")
usuarios = load_usuarios("usuarios_actualizado.xlsx")

# Función para eliminar duplicados con sufijo "0F"
def filtrar_cups_repetidos(cups):
    cups_unicos = {c[:-2] if c.endswith("0F") else c for c in cups}
    return list(cups_unicos)

# Función para obtener el último tipo de contrato y comercializadora
def obtener_ultimo_contrato(df, cups_seleccionados):
    df_filtrado = df[df['CUPS'].isin(cups_seleccionados)]
    ultimo_tipo_contrato = df_filtrado['TIPO CONTRATO'].iloc[-1] if not df_filtrado.empty else None
    ultima_comercializadora = df_filtrado['COMPAÑÍA'].iloc[-1] if not df_filtrado.empty else None
    return ultimo_tipo_contrato, ultima_comercializadora

# Función para actualizar las comisiones seleccionadas por los CUPS y meses
def actualizar_comisiones_seleccionadas(data, cups_seleccionados, meses_seleccionados, columna_comisiones):
    df_filtrado = data[(data['CUPS'].isin(cups_seleccionados)) & (data['MES'].isin(meses_seleccionados))]
    total_comisiones = df_filtrado[columna_comisiones].sum() if not df_filtrado.empty else 0
    return total_comisiones

# Verificación de autenticación
if "user" not in st.session_state:
    colaborador, is_admin = login(usuarios)
    if colaborador:
        st.session_state["user"] = colaborador
        st.session_state["is_admin"] = is_admin
else:
    colaborador = st.session_state["user"]
    is_admin = st.session_state["is_admin"]

# Agregar botón de deslogueo
if st.sidebar.button("Cerrar sesión"):
    st.session_state.pop("user", None)
    st.session_state.pop("is_admin", None)
    st.experimental_rerun()  # Refresca la aplicación para volver al estado de login

# Definir la columna de comisiones según el tipo de usuario
columna_comisiones = 'Comision IVAN' if is_admin else 'Comision'

# --- Aplicar filtros iniciales ---
filtered_data = data.copy()

# Filtrar contratos por usuario (solo admin ve todos los contratos)
if not is_admin:
    filtered_data = filtered_data[filtered_data['COLABORADOR'] == colaborador]

# Conversión de la columna de comisiones a numérico, ignorando errores
filtered_data[columna_comisiones] = pd.to_numeric(filtered_data[columna_comisiones], errors='coerce')
filtered_data[columna_comisiones] = filtered_data[columna_comisiones].fillna(0)

# Si el usuario está autenticado
if colaborador:

    # --- Barra lateral para filtros ---
    with st.sidebar:
        clientes_unicos = ['Todos'] + list(filtered_data['CLIENTE'].unique())
        search_query = st.selectbox("Buscar por CLIENTE, CIF/DNI o CUPS", options=clientes_unicos)

        tipo_contrato = st.selectbox("Tipo de Contrato", ["Todos"] + list(filtered_data['TIPO CONTRATO'].unique()))
        mes = st.selectbox("Mes", ["Todos"] + list(filtered_data['MES'].unique()))
        estado = st.selectbox("Estado", ["Todos"] + list(filtered_data['ESTADO'].unique()))

    # --- Aplicar filtros adicionales ---
    if search_query != "Todos":
        filtered_data = filtered_data[filtered_data['CLIENTE'] == search_query]

    if tipo_contrato != "Todos":
        filtered_data = filtered_data[filtered_data['TIPO CONTRATO'] == tipo_contrato]

    if mes != "Todos":
        filtered_data = filtered_data[filtered_data['MES'] == mes]

    if estado != "Todos":
        filtered_data = filtered_data[filtered_data['ESTADO'] == estado]

    # --- Mostrar detalles del cliente ---
    if search_query != "Todos" and not filtered_data.empty:
        cliente_seleccionado = filtered_data.iloc[0]
        cups = filtrar_cups_repetidos(list(filtered_data['CUPS'].unique()))

        # Obtener el último tipo de contrato y comercializadora para los CUPS seleccionados
        ultimo_tipo_contrato, ultima_comercializadora = obtener_ultimo_contrato(filtered_data, cups)

        with st.expander(f"Detalles de {cliente_seleccionado['CLIENTE']}", expanded=True):
            st.write(f"**Nombre del Cliente**: {cliente_seleccionado['CLIENTE']}")
            st.write(f"**CIF/DNI**: {cliente_seleccionado['CIF/DNI']}")
            st.write(f"**Tipo de Contrato**: {ultimo_tipo_contrato}")
            st.write(f"**Comercializadora**: {ultima_comercializadora}")
            st.write(f"**Estado**: {cliente_seleccionado['ESTADO']}")
            st.write(f"**Comisión Total**: € {filtered_data[columna_comisiones].sum():,.2f}")
            st.write("**CUPS Asociados**:")

            # Mostrar CUPS con checkboxes
            cups_seleccionados = []
            for c in cups:
                if st.checkbox(c):
                    cups_seleccionados.append(c)

            # Si hay CUPS seleccionados, mostrar los meses en que se ha cobrado
            if cups_seleccionados:
                meses_cobrados = list(filtered_data[filtered_data['CUPS'].isin(cups_seleccionados)]['MES'].unique())
                meses_seleccionados = st.multiselect("Selecciona los meses para ver la comisión", meses_cobrados)

                # Mostrar comisión acumulada de los CUPS y meses seleccionados
                if meses_seleccionados:
                    comision_seleccionada = actualizar_comisiones_seleccionadas(filtered_data, cups_seleccionados, meses_seleccionados, columna_comisiones)
                    st.write(f"Comisión seleccionada: € {comision_seleccionada:.2f}")
                else:
                    st.write("Por favor selecciona al menos un mes para ver la comisión.")

    # --- Tarjetas de resumen ---
    st.markdown("<h2 style='color: #34a0eb;'>📊 Resumen de Contratos</h2>", unsafe_allow_html=True)

    total_comisiones = filtered_data[columna_comisiones].sum()
    num_contratos = len(filtered_data)
    
    # Calcular número de contratos activos (Activado/Cargado)
    contratos_activos = filtered_data[filtered_data['ESTADO'].isin(['Activado', 'Cargado'])].shape[0]
    
    # Calcular número de bajas en la columna "TIPO CONTRATO"
    num_bajas = filtered_data[filtered_data['TIPO CONTRATO'] == 'Baja'].shape[0]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Comisiones Totales", f"€ {total_comisiones:,.2f}")
    with col2:
        st.metric("Contratos Activos/Cargado", contratos_activos)
    with col3:
        st.metric("Total Bajas", num_bajas)

    # --- Gráficos de comisiones por mes ---
    if 'MES' in filtered_data.columns and columna_comisiones in filtered_data.columns:
        comisiones_mes = filtered_data.groupby('MES')[columna_comisiones].sum().reset_index()
        fig_comisiones = px.bar(comisiones_mes, x='MES', y=columna_comisiones, title='Comisiones por Mes',
                                color='MES', text=columna_comisiones,
                                color_discrete_sequence=px.colors.sequential.Teal,
                                labels={columna_comisiones: 'Comisión (€)'})
        fig_comisiones.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig_comisiones.update_xaxes(categoryorder='array', categoryarray=["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                   "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
        st.plotly_chart(fig_comisiones, use_container_width=True)

    # --- Gráfico de contratos por comercializadora ---
    if 'COMPAÑÍA' in filtered_data.columns:
        contratos_por_compania = filtered_data['COMPAÑÍA'].value_counts().reset_index()
        contratos_por_compania.columns = ['COMPAÑÍA', 'TOTAL CONTRATOS']

        if not contratos_por_compania.empty:
            fig_barras = px.bar(
                contratos_por_compania, 
                x='TOTAL CONTRATOS', 
                y='COMPAÑÍA', 
                orientation='h',  
                title='Distribución de Contratos por Comercializadora',
                text='TOTAL CONTRATOS',  
                color='COMPAÑÍA',  
                color_discrete_sequence=px.colors.sequential.Teal
            )
            fig_barras.update_layout(
                xaxis_title="Total de Contratos", 
                yaxis_title="Comercializadora", 
                showlegend=False
            )
            fig_barras.update_traces(texttemplate='%{x}', textposition='outside')
            st.plotly_chart(fig_barras, use_container_width=True)
        else:
            st.warning("No hay suficientes datos para mostrar el gráfico de comercializadoras.")
    else:
        st.error("La columna 'COMPAÑÍA' no se encuentra en los datos.")

    # --- Mostrar tabla de datos filtrados ---
    st.markdown("<h2 style='color: #34a0eb;'>📋 Tabla de Contratos</h2>", unsafe_allow_html=True)

    # Mostrar solo las columnas correspondientes al usuario (ocultar "Comision IVAN" y "Factura IVAN" si no es admin)
    if is_admin:
        st.dataframe(filtered_data)
    else:
        st.dataframe(filtered_data.drop(columns=['Comision IVAN', 'Factura IVAN'], errors='ignore'))

    # --- Botón para descargar los datos filtrados como CSV ---
    st.download_button(
        label="Descargar datos como CSV",
        data=filtered_data.drop(columns=['Comision IVAN', 'Factura IVAN'], errors='ignore').to_csv(index=False).encode('utf-8'),
        file_name="datos_filtrados.csv",
        mime="text/csv"
    )
