import re

l1_pattern = re.compile(r'\([^()]*\)')
l2_pattern = re.compile(r'(-?\d+)(\.\d+)?[/*](-?\d+)(\.\d+)?')
l3_pattern = re.compile(r'(-?\d+)(\.\d+)?[-+](-?\d+)(\.\d+)?')
mul_sub_pattern = re.compile(r'(-?\d+)(\.\d+)?\*-(-?\d+)(\.\d+)?')
div_sub_pattern = re.compile(r'(-?\d+)(\.\d+)?/-(-?\d+)(\.\d+)?')


def min_cal(string):
    if string.count('+') == 1:
        return str(float(string[:string.find('+')]) + float(string[string.find('+')+1:]))
    elif string[1:].count('-') == 1:
        return str(float(string[:string.find('-', 1)]) - float(string[string.find('-', 1)+1:]))
    elif string.count('*') == 1:
        return str(float(string[:string.find('*')]) * float(string[string.find('*')+1:]))
    elif string.count('/') == 1:
        return str(float(string[:string.find('/')]) / float(string[string.find('/')+1:]))


def normal_numerator(string):
    if string.count('+') + string.count('*') + string.count('/') == 0 and string[1:].find('-') < 0:
        return string

    elif string.count('+-') + string.count('--') + string.count('*-') + string.count('/-') != 0:
        string = string.replace('+-', '-')
        string = string.replace('--', '+')
        if string.count('*-') != 0:
            string = string.replace(mul_sub_pattern.search(string).group(),'-' + mul_sub_pattern.search(string).group().replace('*-', '*'))

        if string.count('/-') != 0:
            string = string.replace(div_sub_pattern.search(string).group(),'-' + div_sub_pattern.search(string).group().replace('/-', '/'))

        return normal_numerator(string)

    elif string.count('*') + string.count('/') != 0:
        from_str = l2_pattern.search(string).group()
        string = string.replace(from_str, min_cal(from_str))
        return normal_numerator(string)

    elif string.count('+') != 0 or string.count('-') != 0:
        from_str = l3_pattern.search(string).group()
        string = string.replace(from_str, min_cal(from_str))
        return normal_numerator(string)


def l1_analysis(string):
    if string.find('(') == -1:
        return normal_numerator(string)

    else:
        from_str = l1_pattern.search(string).group()
        string = string.replace(from_str, normal_numerator(from_str[1:-1]))
        return l1_analysis(string)

