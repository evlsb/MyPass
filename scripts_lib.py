import subprocess


actions_po = [
    {"show": "whereis easy-rsa",
     "show_sudo": 0,
     "install": 'echo "PASSWORD" | sudo -S apt install -y easy-rsa',
     "install_sudo": 1,
     "remove": "echo 'PASSWORD' | sudo -S apt purge -y easy-rsa",
     "remove_sudo": 1,
     "name": "easy-rsa",
     "description": "Easy-RSA - инструмент управления инфраструктурой открытых ключей (PKI)",
     },
    {"show": "whereis openvpn",
         "show_sudo": 0,
         "install": "echo 'PASSWORD' | sudo -S apt install -y openvpn",
         "install_sudo": 1,
         "remove": "echo 'PASSWORD' | sudo -S apt purge -y openvpn",
         "remove_sudo": 1,
         "name": "openvpn",
         "description": "OpenVPN - cвободная реализация технологии виртуальной частной сети (VPN) с открытым исходным кодом для создания зашифрованных каналoв типа точка-точка или сервер-клиенты между компьютерами",
     }
]


actions = [
{"show": "if [ -d easy-rsa ]; then echo 'yes'; else echo 'no'; fi",
     "show_sudo": 0,
     "install": 'echo "PASSWORD" | sudo -S cp -r /usr/share/easy-rsa /$PWD',
     "install_sudo": 1,
     "remove": 'echo "PASSWORD" | sudo -S rm -R /$PWD/easy-rsa',
     "remove_sudo": 1,
     "name": "copy_easyrsa",
     "description": "copy_easyrsa",
    "inputs_cert": "d-none",
     },
    {"show": 'iam="$(whoami)"; var=$(ls -lG | grep easy-rsa); if echo "$var" | grep -q "$iam"; then echo "yes"; else echo "no"; fi',
     "show_sudo": 0,
     "install": 'var=$(echo "PASSWORD" | sudo -S chown -R "$(whoami)" easy-rsa); if echo "$var"; then echo "yes"; else echo "no"; fi',
     "install_sudo": 1,
     "remove": 'var=$(echo "PASSWORD" | sudo -S chown -R root easy-rsa); if echo "$var"; then echo "yes"; else echo "no"; fi',
     "remove_sudo": 1,
     "name": "whoami",
     "description": "Смена владельца папки Easy-Rsa",
    "inputs_cert": "d-none",
     },
    {"show": "if [ -d easy-rsa/pki ]; then echo 'yes'; else echo 'no'; fi",
     "show_sudo": 0,
     "install": "cd easy-rsa; printf 'PASSWORD' | sudo -S ./easyrsa init-pki",
     "install_sudo": 1,
     "remove": 'echo "PASSWORD" | sudo -S rm -R /$PWD/easy-rsa/pki',
     "remove_sudo": 1,
     "name": "Init_PKI",
     "description": "Description PKI",
    "inputs_cert": "d-none",
     },
    {"show": 'cd easy-rsa; iam="$(whoami)"; var=$(ls -lG | grep pki); if echo "$var" | grep -q "$iam"; then echo "yes"; else echo "no"; fi',
     "show_sudo": 0,
     "install": 'var=$(echo "PASSWORD" | sudo -S chown -R "$(whoami)" easy-rsa/pki); if echo "$var"; then echo "yes"; else echo "no"; fi',
     "install_sudo": 1,
     "remove": 'var=$(echo "PASSWORD" | sudo -S chown -R root easy-rsa/pki); if echo "$var"; then echo "yes"; else echo "no"; fi',
     "remove_sudo": 1,
     "name": "pki",
     "description": "Смена владельца папки PKI",
    "inputs_cert": "d-none",
     },
    {"show": "if [ -f easy-rsa/pki/ca.crt ]; then echo 'yes'; else echo 'no'; fi",
     "show_sudo": 0,
     "install": 'country="RU"; province="Bashkortostan"; city="Ufa"; org="Ozna"; email="levashov.en@ozna.ru"; ou="ASUTP"; cd easy-rsa; > vars; printf "set_var EASYRSA_REQ_COUNTRY    	\""$country"\"\nset_var EASYRSA_REQ_PROVINCE   	\""$province"\"\nset_var EASYRSA_REQ_CITY    	\""$city"\"\nset_var EASYRSA_REQ_ORG    	\""$org"\"\nset_var EASYRSA_REQ_EMAIL    	\""$email"\"\nset_var EASYRSA_REQ_OU    	\""$ou"\"\nset_var EASYRSA_ALGO           	\"ec\"\nset_var EASYRSA_DIGEST          \"sha512\"\n" >> vars; cd easy-rsa; printf "PASSWORD\ny\ny\n\ny\ny\n" | sudo -S ./easyrsa build-ca nopass',
     "install_sudo": 1,
     "remove": "echo 'PASSWORD' | sudo -S rm -R easy-rsa",
     "remove_sudo": 1,
     "name": "CA",
     "description": "CA",
    "inputs_cert": "",
     }
]


actions_server = [

]


# функция подготовки скрипта
def sudo(command_work, password=" "):
    # Переменные для выполнения скрипта от суперпользователя
    # SUDO1 = "echo "
    # SUDO2 = " | sudo -S "
    # Установка локальных переменных
    command_path = "export PATH=$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr" \
                   "/local/games:/snap/bin; "


    a =  command_path + command_work
    return a.replace("PASSWORD", password)



def bash(command):
    result = subprocess.run(command, \
                            stderr=subprocess.PIPE, \
                            stdout=subprocess.PIPE, \
                            shell=True, \
                            encoding='utf-8')

    return {"result": result.returncode,
            "stderr": result.stderr,
            "stdout": result.stdout}
