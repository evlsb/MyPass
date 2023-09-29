START_PORT=60000
END_PORT=64000

# получаем свободный порт
while [ $START_PORT -le $END_PORT ]
  do
    RESULT=$(echo 'levashov' | sudo -S lsof -i :$START_PORT)

#    if [ $? -eq 0 ]; then
#      echo "port $START_PORT busy"
#    else
#      echo "port $START_PORT free"
#    fi

    if [ $? -ne 0 ]; then
      echo "$START_PORT"
      break
    fi

    let "START_PORT+=1"
  done

#echo "$STR" > foo.txt

