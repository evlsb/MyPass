import subprocess
import os
import shutil
import sys

# command = "cd ~/easy-rsa; ./easyrsa init-pki"
# result = subprocess.run(command, shell=True)
#

# my_file = open("varss.txt", "w+")
# my_file.write("Привет, файл!")
# my_file.close()
#
#
# shutil.move("varss.txt", "../../easy-rsa")

f = open('../../easy-rsa/pki/issued/647db5bf0a8c4a28aab3438c047ac355.crt','r')
print(*f)

