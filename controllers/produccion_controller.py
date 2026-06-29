import pandas as pd
import numpy as np
from database import Database
import math
from scipy.stats import norm

class ProduccionController:
    def __init__(self, db: Database):
        self.db = db
        self.ultimo_resultado = None  # Para detectar cambios
    
    def obtener_productos_grupo_a(self):
        """Obtiene los productos del Grupo A desde la BD"""
        articulos = self.db.obtener_articulos()
        if not articulos:
            return []
        
        from controllers.abc_controller import ABCController
        abc_controller = ABCController(self.db)
        df = abc_controller.calcular_analisis_abc()
        
        if df is None:
            return []
        
        grupo_a = df[df['grupo'] == 'A']
        
        productos_a = []
        for _, row in grupo_a.iterrows():
            productos_a.append({
                'id': row['id'],
                'sku': row['sku'],
                'nombre': row['nombre'],
                'demanda': row['demanda'],
                'costo_unitario': row['costo_unitario']
            })
        
        return productos_a
    
    def calcular_epq(self, demanda, co, p, ch, cb=None):
        """
        Calcula el Lote Económico de Producción (EPQ)
        """
        if p <= demanda:
            return {
                'error': True,
                'mensaje': f"La tasa de producción (p = {p}) debe ser mayor que la demanda (D = {demanda})"
            }
        
        tiene_faltantes = cb is not None and cb > 0
        
        if tiene_faltantes:
            q_optima_calculada = np.sqrt(
                (2 * demanda * co) / (ch * (1 - demanda / p)) * ((ch + cb) / cb)
            )
        else:
            q_optima_calculada = np.sqrt(
                (2 * demanda * co) / (ch * (1 - demanda / p))
            )
        
        q_optima = math.ceil(q_optima_calculada)
        
        cp = (demanda / q_optima) * co
        cm = (q_optima / 2) * ch * (1 - demanda / p)
        ct = cp + cm
        t = q_optima / demanda
        tp = q_optima / p
        td = t - tp
        imax = q_optima * (1 - demanda / p)
        n = demanda / q_optima
        
        resultados = {
            'error': False,
            'tiene_faltantes': tiene_faltantes,
            'q_optima': q_optima,
            'cp': cp,
            'cm': cm,
            'ct': ct,
            't': t,
            'tp': tp,
            'td': td,
            'imax': imax,
            'n': n
        }
        
        if tiene_faltantes:
            s_optima = q_optima * (ch / (ch + cb))
            nivel_servicio_epq = (q_optima - s_optima) / q_optima
            cf = (s_optima ** 2 * cb) / (2 * q_optima * (1 - demanda / p))
            ct_f = cp + cm + cf
            
            resultados.update({
                's_optima': s_optima,
                'nivel_servicio_epq': nivel_servicio_epq,
                'cf': cf,
                'ct_f': ct_f,
                'cb': cb
            })
        
        return resultados
    
    def calcular_ss_pr(self, demanda, dias_operativos, L, sigma_L=0, sigma_d=0, 
                        nivel_servicio=0.95, s_optima=0, tipo_desviacion='diaria', ch=0):
        """
        Calcula Stock de Seguridad y Punto de Reorden
        
        tipo_desviacion:
            - 'diaria': sigma_d es la desviación de la demanda diaria
            - 'lead_time': sigma_d es la desviación de la demanda durante el lead time completo
        """
        demanda_diaria = demanda / dias_operativos
        mu_L = demanda_diaria * L
        
        # Calcular desvío según el tipo seleccionado
        if tipo_desviacion == 'diaria':
            # σ_d es la desviación de la demanda diaria
            sigma_total = np.sqrt(L * sigma_d**2 + demanda_diaria**2 * sigma_L**2)
        else:  # 'lead_time'
            # σ_d es la desviación de la demanda durante el lead time completo
            if sigma_L > 0 and sigma_d > 0:
                sigma_total = np.sqrt((demanda_diaria * sigma_L)**2 + sigma_d**2)
            elif sigma_L > 0:
                sigma_total = demanda_diaria * sigma_L
            elif sigma_d > 0:
                sigma_total = sigma_d
            else:
                sigma_total = 0
        
        z = norm.ppf(nivel_servicio)
        ss = z * sigma_total
        pr = mu_L + ss - s_optima

        ss_redondeado = math.ceil(ss)
        pr_redondeado = math.ceil(pr)

        costo_ss = ss_redondeado * ch if ch > 0 else 0
        
        return {
            'demanda_diaria': demanda_diaria,
            'mu_L': mu_L,
            'sigma_total': sigma_total,
            'z': z,
            'ss': ss,
            'ss_redondeado': ss_redondeado,
            'pr': pr,
            'pr_redondeado': pr_redondeado,
            'nivel_servicio': nivel_servicio,
            's_optima': s_optima,
            'tiene_incertidumbre': sigma_L > 0 or sigma_d > 0,
            'tipo_incertidumbre': 'lead_time' if sigma_L > 0 else 'demanda' if sigma_d > 0 else 'ambas' if (sigma_L > 0 and sigma_d > 0) else 'ninguna',
            'costo_ss': costo_ss,
            'tipo_desviacion': tipo_desviacion
        }
    
    def comparar_con_anterior(self, nuevos_resultados):
        """
        Compara los nuevos resultados con los anteriores y retorna un dict con los cambios
        """
        if self.ultimo_resultado is None:
            return None
        
        cambios = {}
        variables_a_comparar = [
            # Variables principales del EPQ
            ('q_optima', 'Cantidad óptima a producir (Q*)'),
            ('cp', 'Costo de producción anual (CP)'),
            ('cm', 'Costo de inventario anual (CI)'),
            ('ct', 'Costo total anual (CT)'),
            ('imax', 'Inventario máximo (Imax)'),                    # <--- NUEVO
            ('n', 'Número de ciclos por año'),
            
            # Variables de tiempos
            ('t_dias', 'Duración del período (T) en días'),
            ('tp_dias', 'Tiempo de producción (tp) en días'),
            ('td_dias', 'Tiempo muerto (td) en días'),               # <--- NUEVO
            
            # Variables de stock
            ('ss_redondeado', 'Stock de seguridad (SS)'),
            ('pr_redondeado', 'Punto de reorden (PR)'),
            
            # Variables de costos con stock de seguridad
            ('costo_ss', 'Costo del stock de seguridad (SS × Ch)'),
            ('ct_con_ss', 'Costo total con stock de seguridad'),
            
            # Variables específicas si hay faltantes (se agregan condicionalmente)
            ('s_optima', 'Déficit máximo permitido (S*)'),           # <--- NUEVO
            ('ct_f', 'Costo total con faltantes (CT_f)'),            # <--- NUEVO
        ]
        
        for clave, nombre in variables_a_comparar:
            valor_nuevo = nuevos_resultados.get(clave)
            valor_anterior = self.ultimo_resultado.get(clave)
            if valor_nuevo is not None and valor_anterior is not None:
                if valor_nuevo != valor_anterior:
                    if valor_nuevo > valor_anterior:
                        cambios[clave] = {
                            'nombre': nombre,
                            'valor_anterior': valor_anterior,
                            'valor_nuevo': valor_nuevo,
                            'cambio': 'aumento',
                            'simbolo': '🔴',
                            'diferencia': valor_nuevo - valor_anterior
                        }
                    else:
                        cambios[clave] = {
                            'nombre': nombre,
                            'valor_anterior': valor_anterior,
                            'valor_nuevo': valor_nuevo,
                            'cambio': 'disminucion',
                            'simbolo': '🟢',
                            'diferencia': valor_anterior - valor_nuevo
                        }
        
        return cambios
    
    def generar_recomendaciones(self, demanda, q_optima, cp, cm, ct, t, tp, td, imax, n, 
                                ss, pr, nivel_servicio, tiene_faltantes=False, s_optima=0, cb=None, 
                                cf=None, ct_f=None, dias_operativos=300, L=0,
                                sigma_L=0, sigma_d=0, tipo_desviacion='diaria',
                                costo_ss=0, costo_unitario=0):
        """
        Genera un informe textual con recomendaciones en formato de párrafo continuo
        """
        # Redondear valores para mejor legibilidad
        cp_redondeado = round(cp, 2)
        cm_redondeado = round(cm, 2)
        ct_redondeado = round(ct, 2)
        costo_ss_redondeado = round(costo_ss, 2)
        
        # Costo total incluyendo SS
        ct_con_ss = ct + costo_ss
        ct_con_ss_redondeado = round(ct_con_ss, 2)
        
        t_dias = t * dias_operativos
        tp_dias = tp * dias_operativos
        td_dias = td * dias_operativos
        n_redondeado = round(n, 1)
        
        # ============================================================
        # TEXTO CONTINUO - ESTRATEGIA DE PRODUCCIÓN
        # ============================================================
        
        texto = f"""
📋 RECOMENDACIONES Y ESTRATEGIA ÓPTIMA DE PRODUCCIÓN
{'=' * 70}

El análisis realizado sobre el producto seleccionado permite determinar la estrategia de producción que minimiza los costos operativos anuales.

📌 ESTRATEGIA RECOMENDADA

Se recomienda producir lotes de {q_optima} unidades por ciclo de producción. """
        
        if tiene_faltantes:
            texto += f"Adicionalmente, se ha considerado la posibilidad de permitir faltantes planificados, por lo que se puede permitir un faltante máximo de {math.ceil(s_optima)} unidades en cada ciclo. "
        
        texto += f"Con esta estrategia, el nivel máximo de inventario que se alcanzará será de {imax:.0f} unidades, justo al finalizar la fase de producción. "
        
        texto += f"Cada año estará compuesto por aproximadamente {n_redondeado} ciclos de producción completos, cada uno con una duración total de {t_dias:.1f} días. "
        texto += f"De estos, {tp_dias:.1f} días se dedicarán exclusivamente a la producción, mientras que los restantes {td_dias:.1f} días serán de 'tiempo muerto' donde no se produce pero se sigue consumiendo el inventario acumulado. "

        # Stock de Seguridad y Punto de Reorden
        if ss > 0:
            texto += f"Para protegerse ante variaciones en la demanda o en los tiempos de entrega, se recomienda mantener un stock de seguridad de {ss} unidades. "
        
        if tiene_faltantes:
            texto += f"El punto de reorden se ha calculado en {pr} unidades, lo que significa que cuando el inventario baje a ese nivel se debe iniciar la producción del siguiente lote. "
            texto += f"Este valor ya considera que se permiten faltantes planificados, por lo que es normal que ocasionalmente el inventario llegue a cero o incluso a valores negativos."
        else:
            texto += f"El punto de reorden se ha calculado en {pr} unidades, lo que significa que cuando el inventario baje a ese nivel se debe iniciar la producción del siguiente lote, para que el nuevo stock llegue justo antes de que se agote el inventario actual."

        # Costos
        texto += f"\n\n💰 ANÁLISIS DE COSTOS\n"
        
        if tiene_faltantes:
            cf_redondeado = round(cf, 2) if cf else 0
            ct_f_redondeado = round(ct_f, 2) if ct_f else 0
            cb_redondeado = round(cb, 2) if cb else 0
            texto += f"Siguiendo la estrategia recomendada, anualmente se gastarían ${cp_redondeado:,.2f} en producción y ${cm_redondeado:,.2f} en inventario, alcanzando un costo total anual de ${ct_redondeado:,.2f}. "
            texto += f"Al considerar la posibilidad de faltantes, se agrega un costo adicional de ${cf_redondeado:,.2f} por las unidades que no se pudieron entregar a tiempo (${cb_redondeado:,.2f} por cada unidad faltante). "
            texto += f"Incluyendo este concepto, el costo total anual con faltantes sería de ${ct_f_redondeado:,.2f}."
        else:
            texto += f"Con esta estrategia, anualmente se gastarían ${cp_redondeado:,.2f} en producción y ${cm_redondeado:,.2f} en inventario, alcanzando un costo total anual de ${ct_redondeado:,.2f}."

        # Costo del Stock de Seguridad
        if ss > 0 and costo_ss > 0:
            texto += f" El costo asociado al mantenimiento del stock de seguridad es de ${costo_ss_redondeado:,.2f} anuales, por lo que el costo total incluyendo el stock de seguridad sería de ${ct_con_ss_redondeado:,.2f}."

        # Incertidumbre
        if sigma_L > 0 or sigma_d > 0:
            texto += f"\n\n📊 INCERTIDUMBRE CONSIDERADA\n"
            if tipo_desviacion == 'diaria':
                texto += f"Se ha considerado incertidumbre en la demanda diaria (σ_d = {sigma_d} unidades/día) y en el tiempo de envío (σ_L = {sigma_L} días). "
            else:
                texto += f"Se ha considerado incertidumbre en la demanda durante el tiempo de envío (σ_d = {sigma_d} unidades) y en el tiempo de envío (σ_L = {sigma_L} días). "
            texto += f"El stock de seguridad de {ss} unidades permite cubrir estas variaciones con un nivel de servicio del {nivel_servicio*100:.1f}%."

        # Recomendación final
        texto += f"\n\n✅ CONCLUSIÓN\nLa estrategia óptima consiste en producir lotes de {q_optima} unidades, iniciando la producción cuando el inventario llegue a {pr} unidades, manteniendo un stock de seguridad de {ss} unidades y repitiendo este ciclo aproximadamente {n_redondeado} veces al año. "
        
        if tiene_faltantes:
            texto += f"Se permite un faltante máximo de {math.ceil(s_optima)} unidades. "
        
        texto += f"Implementando esta estrategia, se logrará minimizar los costos totales, "
        
        if tiene_faltantes:
            texto += f"alcanzando un gasto anual de aproximadamente ${ct_f_redondeado:,.2f} considerando costos de producción, inventario y faltantes."
        else:
            texto += f"alcanzando un gasto anual de aproximadamente ${ct_con_ss_redondeado:,.2f} considerando costos de producción, inventario y stock de seguridad."

        texto += f"\n\n{'=' * 70}"
        texto += f"\n📊 Análisis realizado con el modelo EPQ (Economic Production Quantity)"
        if tiene_faltantes:
            texto += " con faltantes planificados"
        else:
            texto += " clásico sin faltantes"
        if ss > 0:
            texto += f" - Nivel de servicio: {nivel_servicio*100:.1f}%"
        texto += f"\n{'=' * 70}"

        return texto
    
    def validar_datos(self, nivel_servicio, dias_operativos):
        """
        Valida los datos ingresados y retorna advertencias
        """
        advertencias = []
        
        # Validar nivel de servicio
        if nivel_servicio < 0.50:
            advertencias.append(
                f"⚠️ ADVERTENCIA: El nivel de servicio ingresado ({nivel_servicio*100:.1f}%) es muy bajo. "
                f"Se recomienda un nivel de servicio mínimo del 90% para evitar faltantes frecuentes. "
                f"Un nivel de servicio bajo significa que en { (1 - nivel_servicio) * 100:.1f}% de los ciclos "
                f"habrá faltantes, lo que puede generar insatisfacción en los clientes y pérdidas de ventas."
            )
        elif nivel_servicio < 0.70:
            advertencias.append(
                f"⚠️ El nivel de servicio ({nivel_servicio*100:.1f}%) está por debajo del 70%. "
                f"Para la mayoría de los productos, se recomienda un nivel de servicio entre 90% y 99%."
            )
        elif nivel_servicio > 0.99:
            advertencias.append(
                f"ℹ️ El nivel de servicio ({nivel_servicio*100:.1f}%) es muy alto. "
                f"Esto requerirá un stock de seguridad grande, incrementando los costos de inventario. "
                f"Considere si realmente es necesario un nivel tan alto."
            )
        
        # Validar días operativos
        if dias_operativos > 365:
            advertencias.append(
                f"⚠️ ERROR: Los días operativos ({dias_operativos:.0f}) exceden el máximo de 365 días por año. "
                f"El máximo permitido es 365."
            )
        
        return advertencias