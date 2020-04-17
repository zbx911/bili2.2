"""本脚本单独运行，目的是将商用的批量txt文件转化为本项目可用的toml格式。"""

import os
from re import compile
from string import whitespace

import toml

path_curr = os.path.dirname(os.path.realpath(__file__))
path_input = f'{path_curr}/yw.txt'
path_output = f'{path_curr}/orig_user_1_50.toml'


# split_str只填一个字符就行。但是split_str禁止存在于密码与用户名中，空格也禁止
# 每行数据的左右空白字符均会被删除
def yw2accounts(split_str: str):
    assert len(split_str) == 1
    split_elements = f'{split_str}{whitespace}'
    split_pattern = compile(
        f'([^{split_elements}]+)[{split_elements}]+([^{split_elements}]+)[{split_elements}]+([^{split_elements}]+)[{split_elements}]+([^{split_elements}]+)')

    list_users = []
    with open(path_input, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 50:
                line = line.strip()
                if not line:
                    continue
                result = split_pattern.fullmatch(line)
                print(result)
                username = result.group(2)
                password = result.group(3)
                cookie = result.group(4)
                print(f'原数据:|{line}|')
                print(f'分割　:|{username}|{password}|{cookie}|', end='\n\n')

                dict_user = {
                    'username': username,
                    'password': password,
                    'access_key': '',
                    'cookie': '',
                    'csrf': '',
                    'uid': '',
                    'refresh_token': ''
                }
                list_users.append(dict_user)

    dict_users = {'users': list_users}

    with open(path_output, 'w', encoding='utf-8') as f:
        toml.dump(dict_users, f)


yw2accounts('-')
