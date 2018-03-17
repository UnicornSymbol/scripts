#!/bin/bash
 
# Author: 51clocker
# blog: http://www.51clocker.com
# des: system_init_shell
 
 
if [[ "$(whoami)" != "root" ]]; then
  
    echo "please run this script as root ." >&2
    exit 1
fi
  
echo -e "\033[31m 这个是centos7系统初始化脚本，请慎重运行！ press ctrl+C to cancel \033[0m"
sleep 5
  
  
#update system pack
yum_update(){
    yum -y install wget
    cd /etc/yum.repos.d/
    mkdir bak
    mv ./*.repo bak
    wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo
    wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo
    yum clean all && yum makecache
    yum -y install net-tools lrzsz gcc gcc-c++ make cmake libxml2-devel openssl-devel curl curl-devel unzip sudo ntp libaio-devel wget vim ncurses-devel autoconf automake zlib-devel  python-devel
}
#set ntp
zone_time(){
    cp  /usr/share/zoneinfo/Asia/Chongqing  /etc/localtime
    printf 'ZONE="Asia/Chongqing"\nUTC=false\nARC=false' > /etc/sysconfig/clock
    /usr/sbin/ntpdate pool.ntp.org
    echo "* */5 * * * /usr/sbin/ntpdate pool.ntp.org > /dev/null 2>&1" >> /var/spool/cron/root;chmod 600 /var/spool/cron/root
    echo 'LANG="en_US.UTF-8"' > /etc/sysconfig/i18n
    source  /etc/sysconfig/i18n
} 
#set ulimit
ulimit_config(){
echo "ulimit -SHn 102400" >> /etc/rc.local
cat >> /etc/security/limits.conf << EOF
 *           soft   nofile       102400
 *           hard   nofile       102400
 *           soft   nproc        102400
 *           hard   nproc        102400
EOF
}
 
#set ssh
sshd_config(){
sed -i 's/^GSSAPIAuthentication yes$/GSSAPIAuthentication no/' /etc/ssh/sshd_config
sed -i 's/#UseDNS yes/UseDNS no/' /etc/ssh/sshd_config
systemctl start crond
}
  
#set sysctl
sysctl_config(){
cp /etc/sysctl.conf /et/sysctl.conf.bak
cat > /etc/sysctl.conf << EOF
 net.ipv4.ip_forward = 0
 net.ipv4.conf.default.rp_filter = 1
 net.ipv4.conf.default.accept_source_route = 0
 kernel.sysrq = 0
 kernel.core_uses_pid = 1
 net.ipv4.tcp_syncookies = 1
 kernel.msgmnb = 65536
 kernel.msgmax = 65536
 kernel.shmmax = 68719476736
 kernel.shmall = 4294967296
 net.ipv4.tcp_max_tw_buckets = 6000
 net.ipv4.tcp_sack = 1
 net.ipv4.tcp_window_scaling = 1
 net.ipv4.tcp_rmem = 4096 87380 4194304
 net.ipv4.tcp_wmem = 4096 16384 4194304
 net.core.wmem_default = 8388608
 net.core.rmem_default = 8388608
 net.core.rmem_max = 16777216
 net.core.wmem_max = 16777216
 net.core.netdev_max_backlog = 262144
 net.core.somaxconn = 262144
 net.ipv4.tcp_max_orphans = 3276800
 net.ipv4.tcp_max_syn_backlog = 262144
 net.ipv4.tcp_timestamps = 0
 net.ipv4.tcp_synack_retries = 1
 net.ipv4.tcp_syn_retries = 1
 net.ipv4.tcp_tw_recycle = 1
 net.ipv4.tcp_tw_reuse = 1
 net.ipv4.tcp_mem = 94500000 915000000 927000000
 net.ipv4.tcp_fin_timeout = 1
 net.ipv4.tcp_keepalive_time = 1200
 net.ipv4.ip_local_port_range = 1024 65535
EOF
/sbin/sysctl -p
echo "sysctl set OK!!"
}
  
#disable selinux
selinux_config(){
sed -i '/SELINUX/s/enforcing/disabled/' /etc/selinux/config
setenforce 0
}
 
iptables_config(){
systemctl stop firewalld.servic
systemctl disable firewalld.service
yum -y install iptables-services
cat > /etc/sysconfig/iptables << EOF
# Firewall configuration written by system-config-securitylevel
# Manual customization of this file is not recommended.
*filter
:INPUT DROP [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
:syn-flood - [0:0]
-A INPUT -i lo -j ACCEPT
-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
-A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
-A INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
-A INPUT -p icmp -m limit --limit 100/sec --limit-burst 100 -j ACCEPT
-A INPUT -p icmp -m limit --limit 1/s --limit-burst 10 -j ACCEPT
-A INPUT -p tcp -m tcp --tcp-flags FIN,SYN,RST,ACK SYN -j syn-flood
-A INPUT -j REJECT --reject-with icmp-host-prohibited
-A syn-flood -p tcp -m limit --limit 3/sec --limit-burst 6 -j RETURN
-A syn-flood -j REJECT --reject-with icmp-port-unreachable
COMMIT
EOF
/sbin/service iptables restart
}
main(){
yum_update
zone_time
ulimit_config
#sysctl_config
sshd_config
selinux_config
iptables_config
}
main
