

def create_full_address(address_dict : dict):
    
    full_address = ",".join(value for key, value in address_dict.items() if value != None or key != "landmark") 
    
    return full_address