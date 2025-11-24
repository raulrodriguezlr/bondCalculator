import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import newton

def get_bond_cashflows(bond, analysis_date):
    """Genera los flujos de caja (fechas y montos) del bono."""
    maturity_date = pd.to_datetime(bond['Maturity'], format="%d/%m/%Y")
    
    # Ajuste para bonos Callable o Perpetuos (usamos Next Call Date)
    if bond['Callable'] == 'Y' or pd.isna(maturity_date):
        if not pd.isna(bond['Next Call Date']):
             maturity_date = pd.to_datetime(bond['Next Call Date'], format="%d/%m/%Y")
    
    if pd.isna(maturity_date): return []

    coupon_rate = bond['Coupon'] / 100.0
    freq = int(bond['Coupon Frequency']) if not pd.isna(bond['Coupon Frequency']) else 1
    
    cashflows = []
    # Principal al vencimiento
    cashflows.append((maturity_date, 100.0))
    
    # Cupones hacia atrás desde vencimiento
    current_date = maturity_date
    while current_date > analysis_date:
        coupon_amount = 100.0 * coupon_rate / freq
        cashflows.append((current_date, coupon_amount))
        months = int(12 / freq)
        current_date = current_date - pd.DateOffset(months=months)
    
    cashflows.sort(key=lambda x: x[0])
    # Filtrar flujos pasados
    cashflows = [cf for cf in cashflows if cf[0] > analysis_date]
    return cashflows

def get_discount_factor(date, curve_df, analysis_date, spread=0.0):
    """Calcula el factor de descuento interpolando la curva ESTR."""
    days_diff = (date - analysis_date).days
    t = days_diff / 365.0
    if t <= 0: return 1.0
    
    # Interpolación lineal de tipos cero
    curve_dates = curve_df['Date']
    curve_t = (curve_dates - analysis_date).dt.days / 365.0
    curve_rates = curve_df['Zero Rate'] / 100.0
    
    f = interp1d(curve_t, curve_rates, kind='linear', fill_value="extrapolate")
    zero_rate = float(f(t))
    
    # Añadir spread y calcular DF exponencial
    adjusted_rate = zero_rate + spread
    df = np.exp(-adjusted_rate * t)
    return df

def calculate_bond_price(bond, curve_df, analysis_date, spread=0.0):
    """Calcula Precio Sucio, Cupón Corrido y Precio Limpio."""
    cashflows = get_bond_cashflows(bond, analysis_date)
    if not cashflows: return None, None, None
    
    # Precio Sucio (NPV de flujos)
    dirty_price = 0.0
    for date, amount in cashflows:
        df = get_discount_factor(date, curve_df, analysis_date, spread)
        dirty_price += amount * df
        
    # Cupón Corrido (Accrued Interest)
    freq = int(bond['Coupon Frequency']) if not pd.isna(bond['Coupon Frequency']) else 1
    coupon_rate = bond['Coupon'] / 100.0
    
    # Recalcular madurez para encontrar cupón anterior
    maturity_date = pd.to_datetime(bond['Maturity'], format="%d/%m/%Y")
    if bond['Callable'] == 'Y' and not pd.isna(bond['Next Call Date']):
         maturity_date = pd.to_datetime(bond['Next Call Date'], format="%d/%m/%Y")
         
    current_date = maturity_date
    months = int(12 / freq)
    while current_date > analysis_date:
        current_date = current_date - pd.DateOffset(months=months)
    prev_coupon_date = current_date
    
    days_since_coupon = (analysis_date - prev_coupon_date).days
    if days_since_coupon < 0: days_since_coupon = 0
    
    accrued_interest = 100.0 * coupon_rate * (days_since_coupon / 365.0)
    clean_price = dirty_price - accrued_interest
    
    return dirty_price, accrued_interest, clean_price

def calculate_spread(bond, curve_df, analysis_date, market_clean_price):
    """Calcula el spread (z-spread) dado un precio de mercado."""
    def objective(s): # que se le pasara a newton para encontrar la raiz 
        _, _, price = calculate_bond_price(bond, curve_df, analysis_date, s)
        return price - market_clean_price
    try:
        spread = newton(objective, 0.01)
        return spread
    except:
        return np.nan

def calculate_yield(bond, analysis_date, market_dirty_price):
    """Calcula el Yield to Maturity (continuo)."""
    cashflows = get_bond_cashflows(bond, analysis_date)
    if not cashflows: return np.nan
    
    # Definimos la función objetivo: f(y) = Precio_Teórico(y) - Precio_Mercado que se le pasara a newton para encontrar la raiz
    # Buscamos 'y' tal que f(y) = 0
    def objective(y):
        price = 0.0
        for date, amount in cashflows:
            # Calculamos el tiempo en años (ACT/365)
            t = (date - analysis_date).days / 365.0
            # Descuento continuo: Valor Presente = Monto * e^(-y*t)
            price += amount * np.exp(-y * t)
        return price - market_dirty_price
        
    try:
        # Usamos el método de Newton-Raphson para encontrar la raíz (el yield)
        # Empezamos buscando cerca del 5% (0.05)
        y = newton(objective, 0.05)
        return y
    except:
        return np.nan

def calculate_duration_convexity(bond, analysis_date, yield_val):
    """Calcula Duración Modificada y Convexidad."""
    cashflows = get_bond_cashflows(bond, analysis_date)
    if not cashflows: return np.nan, np.nan
    price = 0.0
    d1 = 0.0
    d2 = 0.0
    for date, amount in cashflows:
        t = (date - analysis_date).days / 365.0
        df = np.exp(-yield_val * t)
        term = amount * df
        price += term
        d1 += term * (-t)
        d2 += term * (t**2)
    if price == 0: return np.nan, np.nan
    mod_duration = -1/price * d1
    convexity = 1/price * d2
    return mod_duration, convexity
