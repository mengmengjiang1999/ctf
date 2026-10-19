**CVE-2020-9054 PoC于上个月公开发布后立即被用来感染Zyxel
NAS设备。Mirai新变体Mukashi暴力使用不同组合的默认凭据强制登录，将登录成功结果发送到命令和控制（C2）服务器。Zyxel
NAS产品固件版本低于5.21容易受到此预身份验证命令注入漏洞的攻击。本文包括整个攻击图文分析和IoC。**

## 漏洞分析

可执行文件weblogin.cgi在验证过程中未正确清除username参数。 攻击者可以使用单引号分号实现命令注入。 weblogin.cgi接受HTTP
GET和POST请求，攻击者可以将恶意有效负载嵌入HTTP请求并进行代码执行。

## 在野利用

第一次事件发生在2020年3月12日19:07，如下图1和2所示，攻击者试图将Shell脚本下载到tmp目录，执行脚本并删除设备上的攻击痕迹。

![](https://image.3001.net/images/20200322/1584879957_5e775955d7de3.png!small)

执行后脚本下载不同体系结构的Mirai bot，运行下载的二进制文件，然后删除。

![](https://image.3001.net/images/20200322/1584880005_5e775985e5ea8.png!small)

## 新Mirai变体：Mukashi

Mukashi是一个自动化程序，它扫描随机主机的TCP端口23，使用不同的默认凭据组合强行强登录，并向其C2服务器报告成功的登录。像其他Mirai变体一样，Mukashi也能够接收C2命令并发起DDoS攻击。

执行后，Mukashi将显示“Protecting your device from further
infections”。然后该恶意软件将其进程名改为dvrhelper，这表明Mukashi可能会继承其前身的某些特征。

在执行操作之前，Mukashi绑定到TCP端口23448，确保在受感染的系统上仅有一个实例运行。恶意软件在初始化期间会即时解码字符串。如下表所示，这些解码后的字符串包括凭据以及C2命令。Mukashi使用自定义解密函数对这些命令和凭据进行加密。附录中提供了解密脚本。

![](https://image.3001.net/images/20200322/1584880290_5e775aa2c607e.png!small)

当恶意软件执行凭据暴力攻击时，Mukashi将使用默认密码，例如t0talc0ntr0l4!和taZz@23495859，以及在扫描阶段前已解码的凭据。
图3显示了Mukashi扫描随机主机时捕获的流量，图4显示了恶意软件暴力身份验证尝试。

![](https://image.3001.net/images/20200322/1584880392_5e775b080bf8d.png!small)

![](https://image.3001.net/images/20200322/1584880396_5e775b0c1beab.png!small)

成功登录后，Mukashi将有效凭据报告给C2服务器45.84.196.75。该消息具有以下格式<host ip addr>：23
<username>：<password>。 下图显示了此类消息的示例。

![](https://image.3001.net/images/20200322/1584880484_5e775b643d955.png!small)

恶意软件启动并初始化，将信标发送回C2服务器45.84.196.75，监听端口4864，通知其C2服务器已准备好执行命令。
信标示例如图6中显示，具有以下格式：<名称>.<输入参数>.<name>， 如果成功创建了套接字，则<name>为root，否则为默认值。 <input
arguments>子字符串是执行二进制文件时的参数。 如果未提供输入参数，则字符串为“无”。

![](https://image.3001.net/images/20200322/1584880617_5e775be900e04.png!small)

Mukashi的DDoS功能与Mirai及其变体的DDoS攻击机制（例如UDP，TCP，UDP绕过和TCP绕过）相同。
Mukashi包含dvrhelper变体的某些功能，还具有抵抗DDoS防御功能。 下表显示了Mukashi支持的C2命令。

![](https://image.3001.net/images/20200322/1584882340_5e7762a46f79c.png!small)

Attack_parsing函数负责处理Mukashi从C2服务器接收的命令。除了命令类型和目标地址之外还包括其他相关信息，如SYN标志，ACK标志，URG标志，PSH标志，Rst标志，时间字段，目标端口，数据包长度等。如果目标端口不可用，Mukashi将选择一个随机端口。
如果未指定数据包的长度，则Mukashi将使用默认值1458。

下图显示了x86版本与arm7版本的区别。

![](https://image.3001.net/images/20200322/1584882504_5e776348c4ceb.png!small)

![](https://image.3001.net/images/20200322/1584882504_5e776348c6786.png!small)

建议用户更新固件，使用复杂登录密码。

## IoCs

### File (Sha256)

> 8c0c4d8d727bff5e03f6b2aae125d3e3607948d9dff578b18be0add2fff3411c (arm.bot)
>
> 5f918c2b5316c52cbb564269b116ce63935691ee6debe06ce1693ad29dbb5740 (arm5.bot)
>
> 8fa54788885679e4677296fca4fe4e949ca85783a057750c658543645fb8682f (arm6.bot)
>
> 90392af3fdc7af968cc6d054fc1a99c5156de5b1834d6432076c40d548283c22 (arm7.bot)
>
> 675f4af00520905e31ff96ecef2d4dc77166481f584da89a39a798ea18ae2144 (mips.bot)
>
> 46228151b547c905de9772211ce559592498e0c8894379f14adb1ef6c44f8933 (mpsl.bot)
>
> 753914aa3549e52af2627992731ca18e702f652391c161483f532173daeb0bbd (sh4.bot)
>
> ce793ddec5410c5104d0ea23809a40dd222473e3d984a1e531e735aebf46c9dc (x86.bot)
>
> a059e47b4c76b6bbd70ca4db6b454fd9aa19e5a0487c8032fe54fa707b0f926d (zi)

### Network

> 45[.]84[.]196[.]75:34834 (Report Successful Login Attempt)
>
> 45[.]84[.]196[.]75:4864 (Command and Control)
>
> 0[.]0[.]0[.]0:23448 (Singleton)

### IDApython 6.x-7.3 Script

    
    
    import ida_kernwin
    from idc import *
    from idautils import *
    from idaapi import *
     
    
    def decode_str(encoded_str):
    if len(encoded_str) == 0:
    return “”
    
    buf = list(encoded_str)
    result = ”
    buf[0] = chr(ord(buf[0]) – 2)
    
    slen = len(encoded_str)
    
    v1 = slen / 2;
    if v1 > 0:
    i = v1
    while True:
    if i >= slen:
    break;
    buf[i] = chr(ord(buf[i]) – 1);
    i += 1
    
    v2 = slen / 4;
    if v2 > 0:
    j = v2
    while True:
    if j >= slen:
    break;
    buf[j] = chr(ord(buf[j]) – 1)
    j += 1
    
    for k in xrange(0, slen):
                  buf[k] = chr(ord(buf[k]) – 1)
    
    v3 = 0
    if slen > 24:
    if slen > 99:
    v3 = slen / 5 – 3;
    else:
                           v3 = slen / 5 – 1;
         else:
    v3 = slen / 5;
    
    l = v3
         while True:
                 if l >= slen:
                       break
                 buf[l]= chr(0);
                 l += 1
    
    result = “”.join(buf)
         return result
    
    def main():
    for addr in XrefsTo(0x080482A0, flags=0):
    print(“[*] addr.frm {0}”.format(hex(addr.frm)))
             prev_addr = PrevHead(addr.frm)
    
    encoded_str = “”
    if GetMnem(prev_addr) == “push”:
    str_addr = GetOperandValue(prev_addr, 0)
             elif GetMnem(prev_addr) == “mov”:
                  str_addr = GetOperandValue(prev_addr, 1)
    
    print(“\tstr_addr: {0}”.format(hex(str_addr)))
    encoded_str = GetString(str_addr)
    print(“\tencoded_str: {0}”.format(encoded_str))
    decoded_str = decode_str(encoded_str)
    print(“\tdecoded_str: {0}”.format(decoded_str))
    
    if __name__ == ‘__main__’:
    main()  
    

### IDApython 7.4 Script

    
    
    def decrypt_string(enc_str):
    strlen = len(enc_str)str = chr(ord(enc_str[0])-2) + enc_str[1:]v1 = strlen/2
    if v1>0:
    str = str[0:v1] + ”.join([chr(ord(x)-1) for x in str[v1:]])
    v2 = strlen/4
    if v2>0:
    str = str[0:v2] + ”.join([chr(ord(x)-1) for x in str[v2:]])
    
    str = ”.join([chr(ord(x)-1) for x in str])
    
    if strlen>24:
    if strlen>99:
    v9 = strlen/5 – 3
    else:
    v9 = strlen/5 – 1
    
    else:
    v9 = strlen/5
    
    str = str[:v9] + chr(0) + str[v9+1:]
    return str
    
    def main():
    strrefs = []
    for addr in XrefsTo(0x080482a0, flags=0):
    prev_ins = prev_head(addr.frm)
    ref = get_operand_value(prev_ins, 1)
    if ref>0:
                                               strrefs.append(ref)
    
    for ref in strrefs:
    enc_str = get_strlit_contents(ref)
    print “Encrypted string: %s” %enc_str
    dec_str = decrypt_string(enc_str)
    print “Decrypted string: %s” %dec_str
    
    if __name__ == ‘__main__’:
    main()  
    

 ***参考来源：[unit42](https://unit42.paloaltonetworks.com/new-mirai-variant-mukashi/)，由Kriston编译，转载请注明来自FreeBuf.COM**  

