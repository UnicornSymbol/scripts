1:����zabbix-agentd
�����������
UserParameter=disk.scan,/bin/sh /usr/local/zabbix/scripts/disk_autocheck/diskiocheck.sh 
include conf.d/disk_io.conf

2���ϴ��ű�diskiocheck.sh disk_io.conf����Ӧλ��
3���ϴ�ģ���ļ�