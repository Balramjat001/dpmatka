import re
from datetime import datetime


def validate_mobile(value):
    return bool(re.fullmatch(r'\d{10}', str(value or '').strip()))


def validate_bid_value(bid_type, value):
    if bid_type == 'single_digit':
        return value.isdigit() and 0 <= int(value) <= 9
    if bid_type == 'jodi_digit':
        return re.fullmatch(r'\d{2}', str(value or '')) is not None and 0 <= int(value) <= 99
    if bid_type in ('single_panna', 'double_panna', 'triple_panna'):
        digits = str(value or '')
        if len(digits) != 3 or not digits.isdigit():
            return False
        if bid_type == 'single_panna':
            return len(set(digits)) == 3
        if bid_type == 'double_panna':
            return (digits[0] == digits[1] or digits[1] == digits[2]) and digits[0] != digits[2]
        if bid_type == 'triple_panna':
            return len(set(digits)) == 1
    if bid_type == 'half_sangam':
        return re.fullmatch(r'\d{3}-\d', str(value or '')) is not None
    if bid_type == 'full_sangam':
        return re.fullmatch(r'\d{3}-\d{3}', str(value or '')) is not None
    return False


def validate_result_value(bid_type, value):
    return validate_bid_value(bid_type, value)


def parse_time(value):
    try:
        return datetime.strptime(str(value), '%H:%M')
    except Exception:
        return None
