#!/bin/bash

#set -o xtrace

#system optimization script
#The fllow apply to CentOS 6.x
. /etc/init.d/functions
 
function check_ok(){
  if [ $? -eq 0 ]
   then
     echo ""
     continue
  else
     echo "pls check error"
     exit
  fi
}
 
cat<<EOF
-----------------------------------------------------------------------
|                     system optimization                             |
-----------------------------------------------------------------------
EOF

#install tools
echo "===installing tools==="
yum -y install sysstat wget vmstat lrzsz rsync &> /dev/vull
check_ok
action "install tools" /bin/true
 
#close unimportant system services
echo "===Close unimportant system services,it will take serval mintinues==="
for s in `chkconfig --list|grep 3:on|awk '{print $1}'|grep -Ev "crond|sshd|sysstat|rsyslog|network"`
do
  chkconfig $s off
done
check_ok
action "Close unimportant system services" /bin/true
 
 
#close selinux
echo "===close SELINUX==="
if [ `getenforce` != "Disabled" ]
then
  sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
  echo "selinux is disabled,you must reboot!"
else
  action "SELINUX is closed" /bin/true
fi
check_ok
action "Close SELINUX" /bin/true
 
 
#close ctrl+alt+del
mv /etc/init/control-alt-delete.conf /etc/init/control-alt-delete.conf.bak
 
 
#close iptables
echo "===close iptables==="
iptables-save >/etc/sysconfig/iptables_$(date +%s)
iptables -F
service iptables save
check_ok
action "iptables is closed" /bin/true
 
 
#set ulimit
echo "ulimit -SHn 65535" >>/etc/rc.local
sed -i '/End of file/i*           soft   nofile       65535' /etc/security/limits.conf
sed -i '/End of file/i*           hard   nofile       65535' /etc/security/limits.conf
 
#set SSH
sed -i 's/#UseDNS yes/UseDNS no/g' /etc/ssh/sshd_config
sed -i 's/#Port 22/Port 65500/g' /etc/ssh/sshd_config
service sshd restart
 
 
#lock system files
chattr +i /etc/passwd
chattr +i /etc/group
chattr +i /etc/shadow
chattr +i /etc/gshadow
 
 
#set ntp
yum install ntpdate -y
ntpdate ntp.fudan.edu.cn
echo "* 3 * * * /usr/sbin/ntpdate ntp.fudan.edu.cn >/dev/null 2>&1" >>/etc/crontab
service crond restart
check_ok
action "ntpdate is installed and add in crontab" /bin/true
 
 
#set vim
echo "===install vim,it will take serval mintinues==="
yum install vim-enhanced -y &> /dev/null
alias vi=vim
echo "alias vi=vim" >>/root/.bashrc
check_ok
action "vim is installed" /bin/true
 
 
#set yum repos
echo "===update yum repos,it will take serval mintinues==="
yum install wget -y &> /dev/null
mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.bak
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-6.repo &>/dev/null
wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-6.repo &>/dev/null
yum clean all &>/dev/null
yum makecache &>/dev/null
check_ok
action  "yum repos update is ok" /bin/true

#set +o xtrace
