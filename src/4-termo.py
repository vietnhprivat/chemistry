import pandas as pd
import numpy as np
from typing import Dict

def lookup_property(df: pd.DataFrame, substance: str, property_name: str) -> float:
    """
    Retrieve a thermodynamic property for a given substance.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns: 'Substance', 'dHf', 'dGf', 'S'
    substance : str
        Chemical formula (e.g., "Na2SO4(s)", "Na+(aq)")
    property_name : str
        Property to retrieve: "dHf", "dGf", or "S"
    """
    allowed_props = {"dHf", "dGf", "S"}
    if property_name not in allowed_props:
        raise ValueError(f"Invalid property '{property_name}'. Must be one of {allowed_props}")

    if substance not in df["Substance"].values:
        raise KeyError(f"Substance '{substance}' not found in the DataFrame.")
    
    value = df.loc[df["Substance"] == substance, property_name].iloc[0]
    
    # Handle missing or invalid data
    if pd.isna(value) or value == "?":
        raise ValueError(f"No valid data for {property_name} of {substance}")
    
    return float(value)

def calculate_reaction(df: pd.DataFrame,reactants: Dict[str, float],products: Dict[str, float],property_name: str) -> float:
    """
    Calculate the change in a thermodynamic property for a reaction.
    
    Returns ΔH°rxn, ΔG°rxn, or ΔS°rxn using: Σ(products) - Σ(reactants)
    """
    sigma_r = sum(coeff * lookup_property(df, substance, property_name) 
                  for substance, coeff in reactants.items())
    
    sigma_p = sum(coeff * lookup_property(df, substance, property_name) 
                  for substance, coeff in products.items())
    
    return np.round(sigma_p - sigma_r, 3)
    
if __name__ == '__main__':
    apx2 = pd.read_csv("data/Appendix2.csv")
    
    # Question 7
    reactants_q7 = {"Na2SO4(s)": 1}
    products_q7 = {"Na+(aq)": 2, "SO4--(aq)": 1}
    ans_7 = calculate_reaction(apx2, reactants_q7, products_q7, "dHf")
    print(f"Question 7: ΔH°rxn = {ans_7} kJ/mol")
    
    # Question 8
    reactants_q8 = {"C6H12O6(s)": 1, "O2(g)": 6}
    products_q8 = {"CO2(g)": 6, "H2O(l)": 6}
    ans_8 = calculate_reaction(apx2, reactants_q8, products_q8, "dHf")
    print(f"Question 8: ΔH°rxn = {ans_8} kJ/mol")