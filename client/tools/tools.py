import re


def validate_ip_port_domain(input_str):
    # Паттерн для IP адреса и порта вида {ip}:{port}
    ip_port_pattern = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5})$'

    # Паттерн для домена
    domain_pattern = r'^([\da-zA-Z\.-]+)\.([a-zA-Z\.]{2,6})$'

    if re.match(ip_port_pattern, input_str):
        return True
    elif re.match(domain_pattern, input_str):
        return True
    else:
        return False