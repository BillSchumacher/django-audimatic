import re

def _dict_to_hstore(d):
    """
    Converts a Python dictionary to a Postgres hstore string.
    Example: {'a': 1, 'b': 2} -> '"a"=>"1","b"=>"2"'
    """
    return ','.join([f'"{k}"=>"{v}"' for k, v in d.items()])

def _ensure_dict(val):
    """
    Ensures that a string in hstore format is parsed back into a dictionary.
    Accepts both ':' and '=>' as separators, and comma as delimiter.
    """
    # Updated regex to support => and comma
    pattern = r'"([^"]+)"\s*=>\s*"([^"]*)"|([^,:\s]+)\s*:\s*([^,:\s]+)'
    matches = re.findall(pattern, val)
    d = {}
    for m in matches:
        if m[0]:
            k, v = m[0], m[1]
        else:
            k, v = m[2], m[3]
        d[k] = v
    return d

# Example usage:
def save_data(data_dict):
    # Convert dict to hstore string before saving (simulate DB save)
    hstore_string = _dict_to_hstore(data_dict)
    # ... Save hstore_string to DB ...
    return hstore_string

def load_data(hstore_string):
    # Convert hstore string back to dict after loading from DB
    data_dict = _ensure_dict(hstore_string)
    # ... Use data_dict ...
    return data_dict

# Example "before" and "after" variables, showing the conversion:
if __name__ == "__main__":
    before = {"foo": "bar", "x": 123}
    hstore_before = _dict_to_hstore(before)
    print("Hstore string:", hstore_before)
    after = _ensure_dict(hstore_before)
    print("Parsed dict:", after)