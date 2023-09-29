#country="RU"; province="Bashkortostan"; city="Ufa"; org="Ozna"; email="levashov.en@ozna.ru"; ou="ASUTP"; cd easy-rsa; > vars; printf "set_var EASYRSA_REQ_COUNTRY    	\""$country"\"\nset_var EASYRSA_REQ_PROVINCE   	\""$province"\"\nset_var EASYRSA_REQ_CITY    	\""$city"\"\nset_var EASYRSA_REQ_ORG    	\""$org"\"\nset_var EASYRSA_REQ_EMAIL    	\""$email"\"\nset_var EASYRSA_REQ_OU    	\""$ou"\"\nset_var EASYRSA_ALGO           	\"ec\"\nset_var EASYRSA_DIGEST          \"sha512\"\n" >> vars

#if [ -d /etc/openvpn/server/USER ]; then echo 'yes'; else echo 'no'; fi

#var=$(ls /etc/openvpn/server/USER); 

var=$(if ! [ -d /etc/openvpn/server/USER ]; then printf 'levashov' | sudo -S mkdir /etc/openvpn/server/USER; else echo "$(ls /etc/openvpn/server/USER)"; fi);

#echo "$var"
cd /home

if [ "$?" -ne "0" ]; then
  echo "Sorry, Command execution failed !"
fi

#-------------------------$*---------------------------------
#export IFS='-'
#cnt=1

#echo "Values of \"\$*\":"

#for arg in "$*"
#do
#   echo "Arg #$cnt=$arg"
#   let "cnt+=1"
#done

#-------------------------$@---------------------------------
#cnt=1
#echo "Values of \"\$@\":"
#for arg in "$@"
#do
#   echo "Arg #$cnt= $arg"
#   let "cnt+=1"
#done

#-------------------------$#---------------------------------
#if [ $# -lt 2 ]
#then
#  echo "Usage: $0 arg1 arg2"
#  exit
#fi

#echo -e  "\$1=$1"
#echo -e "\$2=$2"

#-------------------------$?, $-, $_---------------------------------

#echo -e "$_";

#if [ "$?" -ne "0" ]; then
#  echo "Sorry, Command execution failed !"
#fi

#echo -e "$-";
