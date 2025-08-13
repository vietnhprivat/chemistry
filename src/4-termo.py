import pandas as pd
import numpy as np
from typing import Dict, Union

def lookup_property(df: pd.DataFrame, substance: str, property_name: str) -> float:
    """
    Retrieve a thermodynamic property for a given substance.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns: 'Substance', 'H', 'G', 'E'
    substance : str
        Chemical formula (e.g., "Na2SO4(s)", "Na+(aq)")
    property_name : str
        Property to retrieve: "H", "G", or "E"
    """
    
    # Error check like who cares?
    allowed_props = {"H", "G", "E"}
    if property_name not in allowed_props:
        raise ValueError(f"Invalid property '{property_name}'. Must be one of {allowed_props}")

    if substance not in df["Substance"].values:
        raise KeyError(f"Substance '{substance}' not found in the DataFrame.")
    
    # Actual code begins here mate -_-
    value = df.loc[df["Substance"] == substance, property_name].iloc[0]
    return float(value)

def calculate_reaction(df: pd.DataFrame,
                     reactants: Dict,
                     products: Dict, 
                     property_name: str) -> float:
    """
    Calculate the change in a thermodynamic property for a reaction.
    
    Returns ΔH°rxn, ΔG°rxn, or ΔS°rxn using: Σ(products) - Σ(reactants) <- gpt (not me)
    """
    sigma_r = sum(coeff * lookup_property(df, substance, property_name) 
                  for substance, coeff in reactants.items())
    
    sigma_p = sum(coeff * lookup_property(df, substance, property_name) 
                  for substance, coeff in products.items())
    
    return np.round(sigma_p - sigma_r, 3)

def get_molarmass(formula: str) -> float:
    "Gets the molarmass."
    substance = Substance.from_formula(formula)
    if substance is None or substance.mass is None:
        raise ValueError(f"Could not determine molar mass for formula: {formula}")
    return float(substance.mass)

def celsius_kelvin(celsius):
    return celsius + 273.15

def kelvin_celsius(kelvin):
    return kelvin - 273.15
    
if __name__ == '__main__':
    from chempy import Substance
    from sympy import symbols, solve, Eq, ln

    """
    # Template
    reactants_q = {}
    products_q = {}
    ans_ = calculate_reaction(apx2, reactants_q, products_q, "H")
    print(f"Question : ΔH°rxn = {ans_}")
    """
    apx2 = pd.read_csv("data/Appendix2.csv")
    
    # Question 7
    reactants_q7 = {"Na2SO4(s)": 1}
    products_q7 = {"Na+(aq)": 2, "SO4--(aq)": 1}
    ans_7 = calculate_reaction(apx2, reactants_q7, products_q7, "H")
    print(f"Question 7: ΔH°rxn = {ans_7} kJ/mol")
    
    # Question 9
    reactants_q9 = {"C6H12O6(s)": 1, "O2(g)": 6}
    products_q9 = {"CO2(g)": 6, "H2O(l)": 6}
    ans_9 = calculate_reaction(apx2, reactants_q9, products_q9, "H")
    print(f"Question 9: ΔH°rxn = {ans_9} kJ/mol")
    
    # Question 10
    deltaH = ans_9
    m_glu = 10
    n_glu = 10/get_molarmass('C6H12O6')
    ans_10 = deltaH * n_glu
    print(f'Question 10: {ans_10:.2f} kj')
    
    # Question 11
    reactants_q11 = {"Na2SO4(s)": 1}
    products_q11 = {"Na+(aq)": 2, "SO4--(aq)": 1}
    ans_11 = calculate_reaction(apx2, reactants_q11, products_q11, "E")    
    print(f"Question 11: = {ans_11}")
    
    # Question 12
    reactants_q12 = {'Na2SO4(s)': 1}
    products_q12 = {'Na+(aq)': 2, "SO4--(aq)": 1}
    ans_12 = calculate_reaction(apx2, reactants_q12, products_q12, "G")
    print(f"Question 12: ΔH°rxn = {ans_12}")
    
    # Question 14
    T = symbols('T')
    H = 5.4 * 10**3
    S = 18
    equation = H - T*S
    solution = solve(equation, T)
    print(f"Question 14: {solution[0]:.2f}")
    
    # Question 15
    ## Initialize
    R, T, K, G = symbols('R T K G')
    equation = Eq(G, -R*T*ln(K))  # Standard form: ΔG = -RT ln(K)

    ## Info from question
    R_val = 8.314  # J/(mol·K)
    K_val = 2.5e-3
    T_val = celsius_kelvin(800)
    G_val = 'Unknown'

    ## Solve
    G_solution = solve(equation.subs([(R, R_val), (T, T_val), (K, K_val)]), G)
    print(f"Question 15: ΔG = {G_solution[0]:.2f} J/mol")

    # Question 16
    ## Initialize
    R, T, K, G = symbols('R T K G')
    equation = Eq(G, -R*T*ln(K))  # Standard form: ΔG = -RT ln(K)

    ## Info from question
    R_val = 8.314  # J/(mol·K)
    T_val = celsius_kelvin(25)
    G_val = 'Unknown'
    K_val = 'Unknown'

    ## Step 1: Calculate ΔG from reaction
    reactants_q16 = {"SO2(g)": 2, "O2(g)": 1}
    products_q16 = {"SO3(g)": 2}
    G_val = calculate_reaction(apx2, reactants_q16, products_q16, "G")
    print(f"Question 16 - Step 1: ΔG = {G_val:.2f} J/mol")

    ## Step 2: Solve for K
    K_solution = solve(equation.subs([(R, R_val), (T, T_val), (G, G_val*1000)]), K)
    print(f"Question 16 - Step 2: K = {K_solution[0]:.2e}")
    