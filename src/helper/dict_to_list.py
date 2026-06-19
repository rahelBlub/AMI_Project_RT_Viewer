def dict_to_list(in_dict: dict[str]) -> list[str]:
    out_list = []
    for _, val in in_dict.items():
        out_list.append(str(val))
    return out_list
