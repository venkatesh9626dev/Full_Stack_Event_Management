def create_full_address(address_dict: dict):
    street_address = address_dict.get("street_address", "")
    city = address_dict.get("city", "")
    state = address_dict.get("state", "")
    pin_code = address_dict.get("pin_code", "")
    country = address_dict.get("country", "")

    # used none in filter to remove the falsy values from the full address string
    full_address = " ".join(
        filter(None, [street_address, city, state, pin_code, country])
    )

    return full_address
