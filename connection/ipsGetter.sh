echo $1
echo $1
echo $1

sshpass -p $1 ssh -o StrictHostKeyChecking=no root@$2 "lxc-ls -f" >ips.txt


