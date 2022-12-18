from flask import Blueprint, render_template, redirect, url_for, request
import subprocess
from scripts_lib import *

ca = Blueprint('ca', __name__, template_folder='templates')


# pki = install_check(diagnostic=0, command_work="if ! [ -d /usr/share/easy-rsa/pki/ ]; then echo 'No directory'; fi", description_program="PKI - инструмент управления инфраструктурой открытых ключей (PKI)")
#
# cards = [pki]

@ca.route('/')
def index():
    arr_list = []

    for card in actions:
        # arr = {}
        # sudo(command_work=card["show"]) - подготовка запроса
        # bash(command=sudo(command_work=card["show"])) - выполнение запроса
        # list_cmd.append(bash(command=sudo(command_work=card["show"]))) - добавление в список
        arr_item = (bash(command=sudo(command_work=card["show"])))
        arr_item['description'] = card["description"]
        arr_item['install_sudo'] = card["install_sudo"]
        arr_item['remove_sudo'] = card["remove_sudo"]
        arr_item['name'] = card["name"]
        arr_item['visible_warning'] = 0


        arr_list.append(arr_item)
    print(arr_list)


    return render_template('ca/index.html', arr_list=arr_list)


@ca.route('/make', methods=['POST', 'GET'])
def make():

    arr_list = []
    loc = ""

    if request.method == 'POST':
        password = request.form['password']
        name_program = request.form['name_program']

        for card in actions:
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


    print(arr_list)
    # return arr_list
    return render_template('ca/index.html', arr_list=arr_list)
