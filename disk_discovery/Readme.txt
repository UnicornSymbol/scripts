1:配置zabbix-agentd
添加以下配置
UserParameter=disk.scan,/bin/sh /usr/local/zabbix/scripts/disk_autocheck/diskiocheck.sh 
include conf.d/disk_io.conf

2：上传脚本diskiocheck.sh disk_io.conf到相应位置
3：上传模板文件