def str_to_bool(val):
    if val is None:
        return None
    if val == '':
        return None
    if str(val).strip().lower() == 'true':
        return True
    else:
        return False
