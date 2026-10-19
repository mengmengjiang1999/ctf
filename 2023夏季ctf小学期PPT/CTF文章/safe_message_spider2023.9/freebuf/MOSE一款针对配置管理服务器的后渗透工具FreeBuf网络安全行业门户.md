![](https://image.3001.net/images/20210203/1612318865_601a08913f6da05bbb004.png!small)  

## MOSE (Master Of SErvers)

MOSE 是一款功能强大的后渗透工具，无论你的技术能力有多强，或者是否经验足够丰富，该工具都能够帮助广大安全研究专家渗透配置管理（CM）技术环境。类似[
_Puppet_](https://puppet.com/)、[ _Chef_](https://www.chef.io/)、[
_Salt_](https://www.saltstack.com/)和[
_Ansible_](https://www.ansible.com/)这样的CM工具可以根据不同的网络环境和给定的系统并以一种统一的方式来提供自己的功能。成功入侵一台CM服务器之后，攻击者将能够使用这些工具来在CM服务器资源清单中的任意或所有系统中执行命令。但是，如果攻击者没有使用这些类型工具的经验，则可能会出现非常耗时的学习曲线。

在MOSE的帮助下，渗透测试人员可以指定它们所要运行的内容，而不必纠结于如何编写特定于专有CM工具的代码细节。除此之外，它还会自动将所需的命令合并到系统上的现有代码中，从而消除用户的负担。MOSE允许渗透测试人员在服务器的清单列表范围内选择他们想要攻击的目标资产，这种特性对于定位特定资产（如Web服务器）或选择接管CM服务器清单中的所有系统将非常有用。

## 工具依赖

为了确保MOSE的正常工作，我们首先需要在主机上下载并安装下列环境：

  * [ _Golang_](https://golang.org/)：已测试v1.12.7-1.15.2版本。

确保正确设置了GOROOT、PATH和GOPATH环境变量。

  * [ _Docker_](https://docs.docker.com/install/)：已测试v18.09.2-19.03.12版本。

## 工具下载

广大研究人员可以直接使用下列go get命令来下载并安装MOSE，而无需将该项目源码克隆至本地：

    
    
    go get -u -v github.com/master-of-servers/mose

接下来，运行下列命令安装所有指定的Go依赖包并构建项目代码。请确保在运行下列命令之前在命令行终端使用cd命令切换至该项目目录下：

    
    
    make build

## 工具使用

    
    
    Usage:
    
      github.com/master-of-servers/mose [command]
    
     
    
    Available Commands:
    
      ansible     Create MOSE payload for ansible
    
      chef        Create MOSE payload for chef
    
      help        Help about any command
    
      puppet      Create MOSE payload for puppet
    
      salt        Create MOSE payload for salt
    
     
    
    Flags:
    
          --basedir string            Location of payloads output by mose (default "/Users/l/programs/go/src/github.com/master-of-servers/mose")
    
      -c, --cmd string                Command to run on the targets
    
          --config string             config file (default is $PWD/.settings.yaml)
    
          --debug                     Display debug output
    
          --exfilport int             Port used to exfil data from chef server (default 9090, 443 with SSL) (default 9090)
    
      -f, --filepath string           Output binary locally at <filepath>
    
      -u, --fileupload string         File upload option
    
      -h, --help                      help for github.com/master-of-servers/mose
    
      -l, --localip string            Local IP Address
    
          --nocolor                   Disable colors for mose
    
      -a, --osarch string             Architecture that the target CM tool is running on
    
      -o, --ostarget string           Operating system that the target CM server is on (default "linux")
    
      -m, --payloadname string        Name for backdoor payload (default "my_cmd")
    
          --payloads string           Location of payloads output by mose (default "/Users/l/programs/go/src/github.com/master-of-servers/mose/payloads")
    
          --remoteuploadpath string   Remote file path to upload a script to (used in conjunction with -fu) (default "/root/.definitelynotevil")
    
      -r, --rhost string              Set the remote host for /etc/hosts in the chef workstation container (format is hostname:ip)
    
          --ssl                       Serve payload over TLS
    
          --tts int                   Number of seconds to serve the payload (default 60)
    
          --websrvport int            Port used to serve payloads (default 8090, 443 with SSL) (default 8090)
    
     
    
    Use "github.com/master-of-servers/mose [command] --help" for more information about a command.

## TLS证书

我们还需要生成并使用一个由受信证书机构签发的TLS证书。我们已经给大家提供了一个自签名的证书和密钥了（存储在data目录中），不过我们不建议大家去使用。因为这个密钥和证书是公开的，隐私保护性并不高。

## 工具使用样例

### 指定运行命令

该模式将允许我们在所有目标代理中执行特定的命令。

    
    
    ./mose <CM target> -c <command>

 **样例:**

    
    
    ./mose chef -c "echo HELLO >> /tmp/friendlyFile.txt"

在目标设备上，下载Payload，并提供可执行权限，然后运行Payload：

    
    
    ./<CM target>-<CM OS>

 **样例：**

    
    
    ./chef-linux

### 上传并运行文件

该模式将允许我们指定需要在目标主机上运行的脚本或代码。

    
    
    ./mose puppet -u <name of file>

 **样例：**

    
    
    ./mose puppet -u /tmp/notevil.sh

在目标设备上，下载Payload，并提供可执行权限，然后提取并运行Payload：

    
    
    tar -vxf files.tar
    
    ./<CM target>-<CM OS>

 **样例：**

    
    
    ./puppet-linux

## 工具运行截图

### MOSE +
Puppet![](https://image.3001.net/images/20210203/1612319083_601a096b958f5e53fb14c.gif)

### MOSE + Chef

![](https://image.3001.net/images/20210203/1612319800_601a0c38a36528a95c208.gif)

## 项目地址

MOSE：【[ _GitHub传送门_](https://github.com/master-of-servers/mose)】

