# Opgave 1
def electron_config(n):
    """
    Returns electron configuration for n electrons using Aufbau principle.
    
    Args:
        n (int): Number of electrons
    
    Returns:
        str: Electron configuration (e.g. "1s^2 2s^2 2p^6 3s^1")
    """
    
    aufbau_order = [
        '1s', '2s', '2p', '3s', '3p', '4s', '3d', '4p', '5s', '4d', 
        '5p', '6s', '4f', '5d', '6p', '7s', '5f', '6d', '7p'
    ]
    
    max_electrons = {'s': 2, 'p': 6, 'd': 10, 'f': 14}
    
    remaining = n
    config = []
    
    for orbital in aufbau_order:
        if remaining <= 0:
            break
            
        orbital_type = orbital[-1]
        max_for_orbital = max_electrons[orbital_type]
        electrons_in_orbital = min(remaining, max_for_orbital)
        
        if electrons_in_orbital > 0:
            config.append(f"{orbital}^{electrons_in_orbital}")
            remaining -= electrons_in_orbital
    
    return " ".join(config)

# Examples:
if __name__ == '__main__':
    Cu = electron_config(29)
    print(Cu)
    
    Ag = electron_config(47)
    print(Ag)
    
    Au = electron_config(79)
    print(Au)
    
    N_plus2 = electron_config(28-2)
    print(N_plus2)
    
    O_minus2 = electron_config(8+2)
    print(O_minus2)
    

