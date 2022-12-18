#!/bin/bash


#chown -R $iam MyPass/pki/
#echo "$(whoami)"


#str1="$(whoami)"; str2="levashov"; if [[ $str1 == $str2 ]]; then echo "yes"; else echo "no"; fi;
#iam="$(whoami)"; var=$(ls -lG | grep pki); if echo "$var" | grep -q "$iam"; then echo "yes"; else echo "no"; fi

#echo "$var"

#iam="$(whoami)"; var=$(chown -R "$iam" pki); if echo "$var"; then echo "yes"; else echo "no"; fi
#var=$(echo "levashov" | sudo -S chown -R "$(whoami)" pki); if echo "$var"; then echo "yes"; else echo "no"; fi

#cp -r /usr/share/easy-rsa $PWD/ea
#cp -r /usr/share/easy-rsa /$PWD

useradd -m sb
printf 'levashov\nlevashov\n' | passwd sb
usermod -aG sudo sb
usermod --shell /bin/bash sb
su sb

printf "levashov" | sudo -S apt update
printf "levashov" | sudo -S apt -y install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv ufw nginx git tmux
cd ~
git clone https://github.com/evlsb/MyPass.git
cd MyPass
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
sudo ufw allow 5000
printf "levashov" | sudo -S cp MyPass.service /etc/systemd/system/MyPass.service
printf "levashov" | sudo -S systemctl start MyPass
printf "levashov" | sudo -S systemctl enable MyPass
#printf "levashov" | sudo -S systemctl status MyPass
