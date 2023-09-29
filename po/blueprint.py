from flask import Blueprint, render_template, redirect, url_for, request
import subprocess
from scripts_lib import *
from flask_security import login_required

po = Blueprint('po', __name__, template_folder='templates')


# класс проверки наличия ПО
class install_check:
    # command_work          - bash команда
    # description_program   - описание программы, текст выводится на странице
    # name_program          - название программы, для выполнения bash комманд
    def __init__(self, command_work, description_program, name_program, diagnostic):
        self.list = ["", "", "", "", "", "", "", "", "", "", ""]
        self.diagnostic = diagnostic
        self.name_program = name_program
        self.command_work = command_work
        self.description_program = description_program
        self.state = self.sub_proc()

    command_path = "export PATH=$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr" \
                   "/local/games:/snap/bin; "

    def sub_proc(self):

        command = self.command_path + self.command_work + " " + self.name_program
        result = subprocess.run(command, \
                                stderr=subprocess.PIPE, \
                                stdout=subprocess.PIPE, \
                                shell=True, \
                                encoding='utf-8')

        self.list[7] = result.stderr
        self.list[8] = result.stdout
        self.list[9] = result.returncode

        if result.returncode == 0:
            self.list[4] = "Успешно!"
            self.list[6] = "success"
        else:
            self.list[4] = "Ошибка, см диагностику!"
            self.list[6] = "danger"

        if result.stdout.find('/') < 0:
            self.list[0] = "не установлен"
            self.list[1] = "danger"
            self.list[2] = "disabled"
            self.list[3] = ""

        else:

            self.list[0] = "установлен"
            self.list[1] = "success"
            self.list[2] = ""
            self.list[3] = "disabled"

        # нужно вы водить диагностическую информацию после выполнения команды
        if self.diagnostic == 0:
            self.list[5] = "d-none"
        else:
            self.list[5] = ""

        return result


easy_rsa = install_check(diagnostic=1, command_work="whereis", name_program="easy-rsa",
                         description_program="Easy-RSA - инструмент управления инфраструктурой открытых ключей (PKI)")
openvpn = install_check(diagnostic=1, command_work="whereis", name_program="openvpn",
                        description_program="OpenVPN - cвободная реализация технологии виртуальной частной сети (VPN) с открытым исходным кодом для создания зашифрованных каналoв типа точка-точка или сервер-клиенты между компьютерами")

cards = [easy_rsa, openvpn]


@po.route('/')
@login_required
def index():
    arr_list = []

    for card in actions_po:
        arr_item = (bash(command=sudo(command_work=card["show"])))
        arr_item['description'] = card["description"]
        arr_item['install_sudo'] = card["install_sudo"]
        arr_item['remove_sudo'] = card["remove_sudo"]
        arr_item['name'] = card["name"]
        arr_item['visible_warning'] = 0

        arr_list.append(arr_item)

    print(arr_list)
    return render_template('po/index.html', arr_list=arr_list)


@po.route('/make', methods=['POST', 'GET'])
def make():
    arr_list = []

    if request.method == 'POST':
        password = request.form['password']
        name_program = request.form['name_program']

        for card in actions_po:
            if name_program == card["name"]:
                if request.form['action'] == "Удалить":
                    arr_item_make = (bash(command=sudo(command_work=card["remove"],
                                                       password=password)))

                else:
                    arr_item_make = (bash(command=sudo(command_work=card["install"],
                                                       password=password)))

                arr_item = (bash(command=sudo(command_work=card["show"])))
                arr_item['make_result'] = arr_item_make["result"]
                arr_item['stdout_make'] = arr_item_make["stdout"]
                arr_item['stderr_make'] = arr_item_make["stderr"]
                arr_item['name'] = card["name"]
                arr_item['description'] = card["description"]
                arr_item['visible_warning'] = 1

                arr_list.append(arr_item)
            else:
                arr_item = (bash(command=sudo(command_work=card["show"])))
                arr_item['install_sudo'] = card["install_sudo"]
                arr_item['remove_sudo'] = card["remove_sudo"]
                arr_item['name'] = card["name"]
                arr_item['description'] = card["description"]
                arr_item['visible_warning'] = 0

                arr_list.append(arr_item)
            #
            print(arr_item)
    print(arr_list)
    # return arr_list
    return render_template('po/index.html', arr_list=arr_list)
