# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 09:35:09 2022

@author: Camila
"""

import pandas as pd
import streamlit as st
#import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
#import base64

st.set_page_config(layout = 'wide')


########### TITULO ##################
st.markdown("<h1 style ='text-align: center; color:#3366CC;'>Accidentes de tránsito en Guatemala 🚗🚑🏍️ </h1>", unsafe_allow_html =True)


###### BASES DE DATOS ##########
def load_data(url):
    df =pd.read_csv(url)
    
    return df

fl = load_data("Bases/fl.csv")
ht = load_data("Bases/ht.csv")
vi = load_data("Bases/vi.csv")
dicc= load_data('Bases/diccionario_accidentes_transito.csv')
dicc2= load_data('Bases/geo3.csv')

############# PESTAÑAS ###################

st.markdown(
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">',
    unsafe_allow_html=True,
)
st.sidebar.title('Menú Principal')


indicador = st.sidebar.selectbox('Indicador', ['','Indicadores',
                                               'Descripción'], key='1',
                            format_func=lambda x: 'Seleccione una opción' if x == '' else x)

if indicador == 'Descripción':

#################################### Mapa     
    p3 = vi[['fecha', 'mupio_ocu', 'tipo_veh']]
    x3 = dicc.loc[dicc['Variable'] == 'tipo_veh'][['Codigo', 'Valor']].rename(columns={'Codigo': 'tipo_veh', 'Valor':'tipo_vehiculo'})
    p3 = pd.merge(p3, x3, how='left', on='tipo_veh')
    x3 = dicc.loc[dicc['Variable'] == 'mupio_ocu'][['Codigo', 'Valor']].rename(columns={'Codigo': 'mupio_ocu', 'Valor':'municipio'})
    p3 = pd.merge(p3, x3, how='left', on='mupio_ocu')
    p3["municipio"]=p3["municipio"].str.rstrip()
    x3 = dicc2[['name','lat','lon']].rename(columns={'name':'municipio'})
    pg3 = pd.merge(p3, x3, how='left', on='municipio')
    pg3 = pg3.drop(6).reset_index().drop('index', axis=1)
    pg3['fecha'] = pd.to_datetime(pg3['fecha'], dayfirst= False) #convertir los datos de la columna fecha en formato fecha
    pg3['fecha'] = pg3['fecha'].dt.year
    pg3= pg3.dropna()
    
    
    st.markdown("<h3 style ='text-align: center;color: black;'>Accidentes de transito en los municipios de Guatemala</h3>"
                ,unsafe_allow_html =True)
    year = st.slider("Año en que ocurrió el suceso",int(pg3["fecha"].min()),int(pg3["fecha"].max()))
    st.map(pg3[pg3['fecha']== year][["lat","lon"]])





###################TOP 5 VEHICULOS MAYOR ACCIDENTADOS###########################3
    c1,c2=st.columns((1,1))
    c1.markdown("<h3 style ='text-align: center; color:Black;'> Top 5 Vehiculos Mayor Accidentales</h3>", unsafe_allow_html =True)
    p2 = vi[['fecha', 'tipo_veh']]
    x2 = dicc.loc[dicc['Variable'] == 'tipo_veh'][['Codigo', 'Valor']].rename(columns={'Codigo': 'tipo_veh', 'Valor':'tipo'})
    p2 = pd.merge(p2, x2, how='left', on='tipo_veh')
    p2 = p2.loc[p2['tipo_veh'] != 99]
    p22 = p2.groupby(['tipo'])[['tipo_veh']].count().reset_index().rename(columns={'hora_ocu': 'hora', 'tipo_veh':'cantidad'}).sort_values('cantidad', ascending=False)
    p22 = p22.head(5).reset_index().drop('index', axis=1)
    
    fig2 = px.bar(p22, x='tipo', y='cantidad',width =850, height=450, color='tipo')
    fig2.update_layout(xaxis_title="<b>Tipo de vehiculo<b>",
                      yaxis_title="<b>Numero de accidentes<b>",
                      template = 'simple_white',
                      plot_bgcolor='rgba(0,0,0,0)'
                      )
    c1.plotly_chart(fig2)
    
####
    c2.markdown("<h3 style ='text-align: center; color:Black;'> Evolución anual de los 5 vehiculos más accidentados</h3>", unsafe_allow_html =True)
    p23 = p2.loc[p2['tipo'].isin(list(p22['tipo'].unique()))].reset_index().drop('index', axis=1)
    p23['fecha'] = pd.to_datetime(p23['fecha'], dayfirst= False) #convertir los datos de la columna fecha en formato fecha
    p23['fecha'] = p23['fecha'].dt.year
    p23 = p23.groupby(['fecha','tipo'])[['tipo_veh']].count().reset_index().rename(columns={'tipo_veh':'cantidad'}).sort_values('fecha', ascending=True)
    p23.head(5)
    fig22 = px.line(p23, x='fecha', y='cantidad', 
                    color='tipo',
                    width =900, height=450
                    )
    
    fig22.update_layout(
        template = 'simple_white',
        plot_bgcolor='rgba(0,0,0,0)',
        title_x = 0.5,
        legend_title = 'Tipo de vehículo:',
        xaxis_title = '<b>Año<b>',
        yaxis_title = '<b>Cantidad de accidentes<b>',
    )
    
    c2.plotly_chart(fig22)
   
###################### ACCIDENTES POR COLOR ##########################    
    c3, c4 = st.columns((1,1))
    
    c3.markdown("<h3 style ='text-align: center; color:Black;'> Accidentes de los vehículos según el color</h3>", unsafe_allow_html =True)

    p4= vi[['color_veh', 'hora_ocu']]
    p4= p4.groupby('color_veh')[['hora_ocu']].count().reset_index().rename(columns={'hora_ocu': 'cantidad'}).sort_values('cantidad', ascending= False)
     
    x1 = dicc.loc[dicc['Variable'] == 'color_veh'][['Codigo', 'Valor']].rename(columns={'Codigo': 'color_veh', 'Valor':'color'})
    x1['color'] = x1['color'].replace(['Ignorado'], 'Sin dato')
    p4 = pd.merge(p4, x1, how='left', on='color_veh')
    colores= ['gray', 'black','red', 'white', 'gray', 'blue','green', 'Corinth', 'yellow','beige', 'light blue', 'brown', 'orange','gray', 'purple','Turquoise','pink']
   
    fig4 = px.bar(p4, x ='color', y ='cantidad', width =1000, height=450)
    
    fig4.update_layout(
        template = 'plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        title_x=0.5)
    
    c3.plotly_chart(fig4)
    
############ ACCIDENTES VEHICULOS NEGROS POR HORA#################################
    
    c4.markdown("<h3 style ='text-align: center; color:Black;'> Accidentes de los vehículos negros según la hora del día</h3>", unsafe_allow_html =True)
    p44 = vi.loc[vi['color_veh'] == 5][['color_veh','hora_ocu']]
    p44 = p44.groupby('hora_ocu')[['color_veh']].count().reset_index().rename(columns={'hora_ocu': 'hora', 'color_veh':'cantidad_negro'}).sort_values('hora')
    p44 = p44.loc[p44['hora'] != 99]
    
    fig44 = px.bar(p44, x ='hora', y ='cantidad_negro', width =900, height=450, color= 'hora')
    

    fig44.update_layout(
        template = 'plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        title_x=0.5)
    
    c4.plotly_chart(fig44)
    
    
#################### EBRIOS POR DEPARTAMENTO ###############################    
#######PARETO TOP DEPARTAMENTOS ###################
    c5, c6 = st.columns((1,1))
    
    c5.markdown("<h3 style ='text-align: center; color:Black;'> Gráfico Pareto de Ebrios por departamento </h3>", unsafe_allow_html =True)
    
    p5=vi[['mes_ocu','depto_ocu','estado_con']]
    x5 = dicc.loc[dicc['Variable'] == 'depto_ocu'][['Codigo', 'Valor']].rename(columns={'Codigo': 'depto_ocu', 'Valor':'tipo'})
    x55 = dicc.loc[dicc['Variable'] == 'estado_con'][['Codigo', 'Valor']].rename(columns={'Codigo': 'estado_con', 'Valor':'tipo'})
    
    p5= pd.merge(p5, x5, how='left', on='depto_ocu')
    p5=pd.merge(p5,x55, how='left', on='estado_con').rename(columns={'tipo_x':'depto','tipo_y':'estado'}).drop(['depto_ocu', 'estado_con'], axis=1)
    
    p55= p5[p5['estado']=='Ebrio'].groupby(['depto'])[['estado']].count().reset_index().rename(columns={'estado':'cantidad_ebrios'}).sort_values('cantidad_ebrios', ascending= False)
    
    p55_c = p55.head()
    
    
    
    p555 = p5.loc[(p5['depto' ].isin(list(p55_c['depto'].unique()))) & (p5['estado']== 'Ebrio')]
    
############# GRAFICA PARETO##########################3    
    
    pareto = p55[['depto', 'cantidad_ebrios']]
    pareto['frec'] = pareto.apply(lambda x: round(x['cantidad_ebrios']/pareto['cantidad_ebrios'].sum() * 100,2), axis = 1)
    pareto = pareto.sort_values('frec', ascending = False)
    pareto['frec_acum'] = pareto['frec'].cumsum()
    
    # Create figure with secondary y-axis GRAFICAR PARETO
    fig5 = make_subplots(specs=[[{"secondary_y": True}]])
    
    
    fig5.add_trace(
        go.Bar(x=pareto['depto'].astype('str'), y=pareto['frec'], name='Frecuencia', marker_color= px.colors.qualitative.Pastel2[0]),
        secondary_y=False,
    )
    
    fig5.add_trace(
        go.Scatter(x=pareto['depto'], y=pareto['frec_acum'], name="Frecuencia Acumulada"),
        secondary_y=True,
    )
    
    
    # Set y-axes titles
    fig5.update_yaxes(title_text="<b>Frecuencia ebrios %</b>", secondary_y=False)
    fig5.update_yaxes(title_text="<b>Frecuencia Acumulada %</b>", secondary_y=True)
    
    fig5.update_layout(
        template = 'plotly_white',
        plot_bgcolor='rgba(0,0,0,0)',
        title_x=0.5,
        width =900, 
        height=450,)
    c5.plotly_chart(fig5)
    
####################  personas involucradas en eventos de transito en estado de embriaguez por mes y los 5 departamentos ###########
    
    c6.markdown("<h3 style ='text-align: center; color:Black;'> Cantidad de personas involucradas en eventos de transito en estado de embriaguez por mes y por departamento </h3>", unsafe_allow_html =True)
    
    p5e=p555.groupby(['mes_ocu', 'depto'])[['estado']].count().reset_index().rename(columns={'estado': 'cantidad_ebrios'})
    
    fig5e = px.line(p5e, x='mes_ocu',y='cantidad_ebrios', color ='depto',width =900, height=450)
    
    fig5e.update_layout(
        xaxis_title = 'Mes',
        yaxis_title = 'Cantidad de personas',
        template = 'simple_white',
        plot_bgcolor='rgba(0,0,0,0)',
        title_x = 0.5)
    
    
    c6.plotly_chart(fig5e)

############################### FALLECIDOS Y LESIONADOS ##################

    c10,c11= st.columns((1,1))
    
    c10.markdown("<h3 style ='text-align: center; color:gray24;'> Lesionados de acuerdo al tipo de sexo </h3>", unsafe_allow_html =True)
    p5 = fl[['ano_ocu', 'fall_les','sexo_per']]
    x5 = dicc.loc[dicc['Variable'] == 'fall_les'][['Codigo', 'Valor']].rename(columns={'Codigo': 'fall_les', 'Valor':'tipo'})
    p5 = pd.merge(p5, x5, how='left', on='fall_les')
    x53 = dicc.loc[dicc['Variable'] == 'sexo_per'][['Codigo', 'Valor']].rename(columns={'Codigo': 'sexo_per', 'Valor':'tipo'})
    p53 = pd.merge(p5, x53, how='left', on='sexo_per')
    p53 = p53.rename(columns={'tipo_x': 'tipo', 'tipo_y':'sexo'})
    p57lh= p53[p53["tipo"]== 'Lesionado']
    p58lh= p57lh[p57lh["sexo"]== 'Hombre']
    p58lh = p58lh.groupby(['ano_ocu','sexo']).agg({'tipo':'count'}).rename(columns={'tipo':'Cantidad'}) # no aplicarmos reset
    p57lm= p53[p53["tipo"]== 'Lesionado']
    p58lm= p57lm[p57lm["sexo"]== 'Mujer']
    p58lm = p58lm.groupby(['ano_ocu','sexo']).agg({'tipo':'count'}).rename(columns={'tipo':'Cantidad'}) # no aplicarmos reset
    xy= pd.merge(p58lh,p58lm, how= "outer",on='ano_ocu').reset_index().rename(columns={"Cantidad_x":"Hombre",'Cantidad_y':'Mujer'})
    
    fig5 = px.bar(xy, x = 'ano_ocu', y=['Hombre','Mujer'], barmode= 'group',width=900, height =450)
    
    # agregar detalles a la gráfica
    fig5.update_layout(
        xaxis_title = 'Año',
        yaxis_title = 'Número de Accidentes',
        template = 'simple_white',
        plot_bgcolor='rgba(0,0,0,0)',
        title_x = 0.5)
    
    c10.plotly_chart(fig5)    

    c11.markdown("<h3 style ='text-align: center; color: Black;'>Fallecidos de acuerdo al tipo de sexo </h3>", unsafe_allow_html =True)
    p57fh= p53[p53["tipo"]== 'Fallecido']
    p58fh= p57fh[p57fh["sexo"]== 'Hombre']
    p58fh = p58fh.groupby(['ano_ocu','sexo']).agg({'tipo':'count'}).rename(columns={'tipo':'Cantidad'}) # no aplicarmos reset
    p57fm= p53[p53["tipo"]== 'Fallecido']
    p58fm= p57fm[p57fm["sexo"]== 'Mujer']
    p58fm = p58fm.groupby(['ano_ocu','sexo']).agg({'tipo':'count'}).rename(columns={'tipo':'Cantidad'}) # no aplicarmos reset
    xy1= pd.merge(p58fh,p58fm, how= "left",on='ano_ocu').reset_index().rename(columns={"Cantidad_x":"Hombre",'Cantidad_y':'Mujer'})
    
    
    fig51 = px.bar(xy1, x = 'ano_ocu', y=['Hombre','Mujer'], barmode= 'group',width=900, height =450 )
    
    #agregar detalles a la gráfica
    fig51.update_layout(
        xaxis_title = 'Año',
        yaxis_title = 'Número de Accidentes',
        template = 'simple_white',
        plot_bgcolor='rgba(0,0,0,0)',
        title_x = 0.5)
    
    c11.plotly_chart(fig51)

################################¿Cómo se comporta el número de fallecidos, ebrios y colisiones según el mes?################
    st.markdown("<h3 style ='text-align: center; color:Black;'> Evolución por mes de fallecidos, ebrio y colisiones </h3>", unsafe_allow_html =True)
    fl9=fl[fl['fall_les']==1].groupby(['mes_ocu'])[['fall_les']].count().reset_index().rename(columns={'fall_les': 'cantidad fallecidos'})
    vi9= vi[vi['estado_con']==2].groupby(['mes_ocu'])[['estado_con']].count().reset_index().rename(columns={'estado_con': 'cantidad_ebrios'})
    ht9=ht[ht['tipo_eve']==1].groupby(['mes_ocu'])[['tipo_eve']].count().reset_index().rename(columns={'tipo_eve': 'cantidad_colisiones'})
    
    p9=pd.merge(fl9, vi9, how='outer', on='mes_ocu')
    p9=pd.merge(p9, ht9, how='outer', on='mes_ocu')
    
    columnas = list(p9.columns)
    columnas = columnas[1:]
   
    fig9 = px.line(p9, x = 'mes_ocu', y= columnas , width=1500, height =450 )
    
    
    # Editar gráfica
    fig9.update_layout(
            title_x=0.5,
            xaxis_title="<b>Mes<b>",
            yaxis_title='<b>Cantidad de personas<b>',
            legend_title_text='<b>Variable<b>',
            template = 'simple_white',
            plot_bgcolor='rgba(0,0,0,0)'
            )
    
    st.plotly_chart(fig9)
#############################################

######################ABOUT#####################3
elif  indicador == 'Indicadores':
    
    st.markdown("<h1 style ='text-align: center; color:#1F77B4;'>Indicadores </h1>", unsafe_allow_html =True)
    
##################### INDICADOR COLORES##################   
   
    ###accidentes por color
    c23,c24= st.columns((1,1))
    
    
    c23.markdown("<h3 style ='text-align: center; color:Black;'>Porcentaje de los colores mas accidentados</h3>", unsafe_allow_html =True)
    
    p23= vi[['color_veh', 'hora_ocu']]
    p23= p23.groupby('color_veh')[['hora_ocu']].count().reset_index().rename(columns={'hora_ocu': 'cantidad'}).sort_values('cantidad', ascending= False)
     
    x1 = dicc.loc[dicc['Variable'] == 'color_veh'][['Codigo', 'Valor']].rename(columns={'Codigo': 'color_veh', 'Valor':'color'})
    x1['color'] = x1['color'].replace(['Ignorado'], 'Sin dato')
    p23 = pd.merge(p23, x1, how='left', on='color_veh')
    
    p23['promedio']=p23['cantidad'].apply(lambda x: x/60529*100).round(2) 
    p23=p23.drop(columns='color_veh')
    p23= p23.head(5)
    
    # hacer la gráfica
    fig23 = px.pie(p23, values = 'promedio', names ='color',
             hole = .5,
             color_discrete_sequence=["blue", "black", "red", "white", "gray"])

    # poner detalles a la gráfica
    fig23.update_layout(
        
        template = 'simple_white',
        title_x = 0.5,
        annotations = [dict(text = str(60529), x=0.5, y = 0.5, font_size = 40, showarrow = False )])

    c23.plotly_chart(fig23)
    
    ##%de vehiculos involucrados##
    
    c24.markdown("<h3 style ='text-align: center; color: Black;'>Porcentaje de vehiculos involucrados en accidentes</h3>", unsafe_allow_html =True)
    p2 = vi[['fecha', 'tipo_veh']]
    x2 = dicc.loc[dicc['Variable'] == 'tipo_veh'][['Codigo', 'Valor']].rename(columns={'Codigo': 'tipo_veh', 'Valor':'tipo'})
    p2 = pd.merge(p2, x2, how='left', on='tipo_veh')
    p2 = p2.loc[p2['tipo_veh'] != 99]
    p22 = p2.groupby(['tipo'])[['tipo_veh']].count().reset_index().rename(columns={'hora_ocu': 'hora', 'tipo_veh':'cantidad'}).sort_values('cantidad', ascending=False)
    p22 = p22.head(5).reset_index().drop('index', axis=1)
    p22["%"]= (p22["cantidad"]/p22["cantidad"].sum())*100
    p22= p22.round(1)
    cnt_ed= p22["cantidad"].sum()
    fig = px.pie(p22, values = '%', names ='tipo',
                  hole = .5,
                 color_discrete_sequence=px.colors.qualitative.G10)
    
    # poner detalles a la gráfica
    fig.update_layout(
        legend_title ="Medios de transporte",
        template = 'simple_white',
        title_x = 0.5,
        annotations = [dict(text = str(cnt_ed), x=0.5, y = 0.5, font_size = 40, showarrow = False )])
    
    c24.plotly_chart(fig)
    
  ###############################  
    c241,c242= st.columns((1,1))
    
    ######accidentes por rango de edad
    c241.markdown("<h3 style ='text-align: center; color:Black;'>Accidentes por rangos de edad</h3>", unsafe_allow_html =True)
    
    vi4 = vi.loc[vi['edad_per'] != 999]
    bins = [0, 5, 11, 18, 26, 59, 100]
    names=['0-5','6-11','12-18','18-26','27-59','>60']
    vi4['edad_per']= pd.cut(vi['edad_per'], bins, labels= names)
    
    vi4= vi4.groupby(['edad_per'])[['num_corre']].count().reset_index()
    
    fig241 = px.bar(vi4, x='edad_per', y='num_corre', width=500, height =370)

    fig241.update_layout(xaxis_title="<b>Rango de edades<b>",
                  yaxis_title="<b>Cantidad<b>",
                  template = 'simple_white',
                  plot_bgcolor='rgba(0,0,0,0)')
    c241.plotly_chart(fig241)
    
    ####### accidentes por mes
    
    c242.markdown("<h3 style ='text-align: center; color:Black;'>Accidentes de transito en cada mes </h3>", unsafe_allow_html =True)
    ht4=ht.groupby('mes_ocu')[['num_corre']].count().reset_index().rename(columns={'num_corre': 'cantidad'}).sort_values('cantidad')
    
    fig242 = px.bar(ht4, x='mes_ocu', y='cantidad', width=600, height =370, color='mes_ocu')

    fig242.update_layout(xaxis_title="<b>Rango de edades<b>",
                  yaxis_title="<b>Cantidad<b>",
                  template = 'simple_white',
                  plot_bgcolor='rgba(0,0,0,0)')
    c242.plotly_chart(fig242)
    
    
    ##Accidentes registrados segun tipo de accidente##
    c21,c22=st.columns((1,1))
    
    c21.markdown("<h3 style ='text-align: center; color:Black;'> Porcentaje de accidentes según tipo de evento </h3>", unsafe_allow_html =True)
    p4 = ht[['fecha', 'tipo_eve']]
    x4 = dicc.loc[dicc['Variable'] == 'tipo_eve'][['Codigo', 'Valor']].rename(columns={'Codigo': 'tipo_eve', 'Valor':'tipo'})
    p4 = pd.merge(p4, x4, how='left', on='tipo_eve')
    p4 = p4.loc[p4['tipo_eve'] != 99]
    p44 = p4.groupby(['tipo'])[['tipo_eve']].count().reset_index().rename(columns={'tipo_eve':'cantidad'}).sort_values('cantidad', ascending=False)
    p44 = p44.head(5).reset_index().drop('index', axis=1)
    p44["%"]= (p44["cantidad"]/p44["cantidad"].sum())*100
    p44 = p44.round(1)
       
    fig = px.funnel(p44, x='%', y='tipo',color="tipo")
    fig.update_layout(
        legend_title ="Medios de transporte",
        template = 'simple_white',
        title_x = 0.5,
        plot_bgcolor='rgba(0,0,0,0)')
    
    c21.plotly_chart(fig)
    
    ###Evolucion colisiones
    c22.markdown("<h3 style ='text-align: center; color:Black;'>Evolución trimestral de colisiones en accidentes de transito  </h3>", unsafe_allow_html =True)
    p42 = p4.loc[p4['tipo'].isin(list(p44['tipo'].unique()))]
    p42['fecha'] = pd.to_datetime(p42['fecha'], dayfirst= False) #convertir los datos de la columna fecha en formato fecha
    p42 = p42.groupby(['fecha','tipo'])[['tipo_eve']].count().reset_index().rename(columns={'tipo_eve':'cantidad'}).sort_values('fecha', ascending=True)
    p42= p42.resample('Q',on ='fecha').sum().reset_index()
    fig4 = px.line(p42, x='fecha', y = 'cantidad', 
              color_discrete_sequence=px.colors.qualitative.G10)

    # agregar detalles
    fig4.update_layout(
        template = 'simple_white',
        title_x = 0.5,
        legend_title = 'Tipo de accidente:',
        xaxis_title = '<b>Fecha<b>',
        yaxis_title = '<b>Cantidad<b>',
        plot_bgcolor='rgba(0,0,0,0)'      
    )
    c22.plotly_chart(fig4)
    
########################### Porcentaje de lesionados segun genero#######
    
    p5 = fl[['ano_ocu', 'fall_les','sexo_per']]
    x5 = dicc.loc[dicc['Variable'] == 'fall_les'][['Codigo', 'Valor']].rename(columns={'Codigo': 'fall_les', 'Valor':'tipo'})
    p5 = pd.merge(p5, x5, how='left', on='fall_les')
    x53 = dicc.loc[dicc['Variable'] == 'sexo_per'][['Codigo', 'Valor']].rename(columns={'Codigo': 'sexo_per', 'Valor':'tipo'})
    p53 = pd.merge(p5, x53, how='left', on='sexo_per')
    p53 = p53.rename(columns={'tipo_x': 'tipo', 'tipo_y':'sexo'})
    p57lh= p53[p53["tipo"]== 'Lesionado']
    p58lh= p57lh[p57lh["sexo"]== 'Hombre']
    p58lh = p58lh.groupby(['ano_ocu','sexo']).agg({'tipo':'count'}).rename(columns={'tipo':'Cantidad'}) # no aplicarmos reset
    p57lm= p53[p53["tipo"]== 'Lesionado']
    p58lm= p57lm[p57lm["sexo"]== 'Mujer']
    p58lm = p58lm.groupby(['ano_ocu','sexo']).agg({'tipo':'count'}).rename(columns={'tipo':'Cantidad'}) # no aplicarmos reset
    xy= pd.merge(p58lh,p58lm, how= "outer",on='ano_ocu').reset_index().rename(columns={"Cantidad_x":"Hombre",'Cantidad_y':'Mujer'})
    xy= pd.merge(p58lh,p58lm, how= "outer",on='ano_ocu').reset_index().rename(columns={"Cantidad_x":"Hombre",'Cantidad_y':'Mujer'})
    xy["%h"]= (xy["Hombre"]/xy["Hombre"].sum())*100
    xy= xy.round(1)
    xy["%m"]= (xy["Mujer"]/xy["Mujer"].sum())*100
    xy= xy.round(1)
   
    
    c56,c57,c58,c59= st.columns((1,1,1,1))
    ##lesionados hombres##
    
    c56.markdown("<h3 style ='text-align: center; color:Black;'>Porcentaje de lesionados hombres</h3>", unsafe_allow_html =True)
    cnt_ed = xy['Hombre'].sum()
    cnt_ed0 = xy['Mujer'].sum()
    # hacer la gráfica
    fig56 = px.pie(xy, values = '%h', names ='ano_ocu',width=400, height=300,
             hole = .5,color="ano_ocu"
             )

    # poner detalles a la gráfica
    fig56.update_layout(
        template = 'simple_white',
        title_x = 0.5,
        annotations = [dict(text = str(cnt_ed), x=0.5, y = 0.5, font_size = 20, showarrow = False )])
   
    c56.plotly_chart(fig56)
    
    
    ####lesionadas mujeres####
    c57.markdown("<h3 style ='text-align: center; color:Black;'>Porcentaje de lesionados mujeres</h3>", unsafe_allow_html =True)
    fig57 = px.pie(xy, values = '%m', names ='ano_ocu',width=400, height=300, 
                   hole = .5,color="ano_ocu"
            )

    # poner detalles a la gráfica
    fig57.update_layout(
        template = 'simple_white',
        title_x = 0.5,
        annotations = [dict(text = str(cnt_ed0), x=0.5, y = 0.5, font_size = 20, showarrow = False )])
   
    c57.plotly_chart(fig57)
    
    ######### % fallecidos segun genero #############
    
    p57fh= p53[p53["tipo"]== 'Fallecido']
    p58fh= p57fh[p57fh["sexo"]== 'Hombre']
    p58fh = p58fh.groupby(['ano_ocu','sexo']).agg({'tipo':'count'}).rename(columns={'tipo':'Cantidad'}) # no aplicarmos reset
    p57fm= p53[p53["tipo"]== 'Fallecido']
    p58fm= p57fm[p57fm["sexo"]== 'Mujer']
    p58fm = p58fm.groupby(['ano_ocu','sexo']).agg({'tipo':'count'}).rename(columns={'tipo':'Cantidad'}) # no aplicarmos reset
    xy1= pd.merge(p58fh,p58fm, how= "left",on='ano_ocu').reset_index().rename(columns={"Cantidad_x":"Hombre",'Cantidad_y':'Mujer'})
    xy1["%h"]= (xy1["Hombre"]/xy1["Hombre"].sum())*100
    xy1= xy1.round(1)
    xy1["%m"]= (xy1["Mujer"]/xy1["Mujer"].sum())*100
    xy1= xy1.round(1)
          
    ##fallecidos hombres##
    cnt_edf = xy1['Hombre'].sum()
    cnt_edf0 = xy1['Mujer'].sum()
    
    c58.markdown("<h3 style ='text-align: center; color:Black;'> Porcentaje de fallecidos hombres </h3>", unsafe_allow_html =True)
    fig58 = px.pie(xy1, values = '%h', names ='ano_ocu',width=400, height=300,
              hole = .5,color="ano_ocu"
             )

    # poner detalles a la gráfica
    fig58.update_layout(
        template = 'simple_white',
        title_x = 0.5,
        annotations = [dict(text = str(cnt_edf), x=0.5, y = 0.5, font_size = 20, showarrow = False )])
   
    c58.plotly_chart(fig58)
    
    ####fallecidos mujeres####
    
    c59.markdown("<h3 style ='text-align: center; color:Black;'> Porcentaje de fallecidos Mujer </h3>", unsafe_allow_html =True)
    fig59 = px.pie(xy1, values = '%m', names ='ano_ocu',width=400, height=300,
             hole = .5,color="ano_ocu"
            )

    # poner detalles a la gráfica
    fig59.update_layout(
        template = 'simple_white',
        title_x = 0.5,
        annotations = [dict(text = str(cnt_edf0), x=0.5, y = 0.5, font_size = 20, showarrow = False )])
   
    c59.plotly_chart(fig59)
    
    