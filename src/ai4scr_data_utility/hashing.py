import hashlib
import json

def hash_configuration(config: dict, method='sha256'):
    if method not in hashlib.algorithms_available:
        raise ValueError(f"Hash method {method} not available."
                         f"Available methods are {', '.join(hashlib.algorithms_available)}")

    hash_fnc = getattr(hashlib, method)

    # Serialize the dictionary into a JSON string
    json_str = json.dumps(config, sort_keys=True)

    # Compute the hash of the JSON string
    hash_object = hash_fnc(json_str.encode())
    hash = hash_object.hexdigest()
    return hash