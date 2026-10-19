# 一、前言

之前去现场，大佬说客户要跑主机检查脚本，就是服务器有点多，有几百台，问有没有办法一键下发，然后执行脚本去跑，跑完之后回收数据，我听这需求，这不是有手就行？然后就应了下来，说我试试，我本以为就是简单的写个py脚本的事情，确认好需求之后就直接开整，刚开始我写的是使用ssh服务去批量搞。

# 二、python实现

先确定下流程，大概的流程就是这四个：

  1. 连接服务器

  2. 上传脚本

  3. 执行脚本

  4. 回收数据

最重要的是先连接上去，不然想得再好都没用，连接的话我用是py的paramiko，功能挺强大的，Paramiko是用py写的一个模块，远程连接到Linux服务器，查看上面的日志状态，批量配置远程服务器，文件上传，文件下载等都可以，除此之外我还用到了pandas，毕竟要批量的话，要去读取表格数据，从表格里面去获取每一台主机的信息，而在paramiko的连接这块有几个坑，首先是连接上去，连接上去有很多种方式，首先分为两大类，一类是SSH，一类是FTP，然后每一类都有两种连接方式，一种是基于密码，一种是基于密钥。先说下SSH连接上去的：

    
    
    ssh = paramiko.SSHClient()  
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  
    ssh.connect("IP",22,"user", "password")

这个的话是没办法上传下载文件的，如果我们要上传文件上去，并且回收数据的话，用这种是没办法实现的，当然也可能是我太菜了，如果有大铁子能实现，麻烦带带小弟。所以这边我使用的是Transport，这种方式连接上去之后能够实现很多功能，可以说是一个小型的putty了。

关键代码

    
    
    import paramiko  
    import pandas as pd  
    import time  
    #获取表格数据  
    df = pd.read_excel('server_information.xlsx')  
    data=df.values  
    #获取单列长度，之后可以作为循环次数的依据  
    L = len(df)  
    #------------------------------------------------------------------------------------------------------------  
    #这里做了个分割，是因为下面这块我把for去掉了，上面的表格是需要循环的时候用的，下面针对单个服务器进行说明  
    IP = data[i][0]  
    port = data[i][1]  
    name=data[i][2]  
    password=data[i][3]  
    # 实例化一个transport对象  
    trans = paramiko.Transport((IP, port))  
    # 建立连接  
    trans.connect(username=name, password=password)  
    # 将sshclient的对象的transport指定为以上的trans  
    ssh = paramiko.SSHClient()  
    ssh._transport = trans  
    sftp = paramiko.SFTPClient.from_transport(trans)  
    #下面是执行了获取IP的命令，因为回收的数据命名格式有根据本机IP来，所以这里先获取下IP  
    # stdout 为正确输出，stderr为错误输出，同时是有1个变量有值  
    stdin, stdout, stderr = ssh.exec_command('ip a|grep inet|grep brd')  
    # inet 10.0.20.12/22 brd 10.0.23.255 scope global eth0  
    # 打印执行结果  
    i_IP = stdout.read().decode('utf-8')  
    Intranet_IP_str= i_IP.split()  
    Intranet_IP = Intranet_IP_str[1].split('/')  
    # 10.0.20.12 22

这两种连接方式我用的都是账号密码连接登录，用密钥的话也可以，具体的可以去百度下用法，其实都差不多。连接上去之后，你以为就搞定了，确实是能上传下载文件的，但是还是有坑，这里离谱的一点就是，连接上去之后你没办法去到别的文件夹下面，也就是说，你始终在根目录下面。

![1683734976_645bc1c04417d0ab87d8c.png!small](https://image.3001.net/images/20230511/1683734976_645bc1c04417d0ab87d8c.png!small)

后面我去找了好久，看了下exec_command的说明才知道，原来每次执行完之后，他都会跳回到原目录下面，也就是说，虽然你执行了cd命令，但是他cd过去之后由于这个函数的原因，他会自己回到原来的目录下面，这就难搞了，我怎么去到我想要的那个文件夹下面去执行文件啊，本来试了下，根据路径去执行文件，但是试了几次发现不行，它只支持执行本目录的文件。

找了一段时间之后，发现可以cd到别的文件夹下面，但是需要去写别的东西，然后为了偷懒，我开始尝试一次执行多条命令，毕竟两条命令搞不定，我就一条命令完成，但是拼接也不是我们用的那种&&了，这个函数有个独特的地方就是，它自带了一个执行多条命令的功能，在一条命令后面使用“;”就可以把命令隔开，看成是两条命令了，例如

    
    
    stdin, stdout, stderr = ssh.exec_command('cd tmp;ls')

![1683735035_645bc1fb0666b6b1ecb7a.png!small](https://image.3001.net/images/20230511/1683735035_645bc1fb0666b6b1ecb7a.png!small)

它就会先cd到tmp这个目录下面，然后执行ls命令，到这无法上传下载文件，无法跳转目录两个坑基本上就填上了，这里贴下完整的数据，表格的格式是IP，端口，用户名，密码。

    
    
    import paramiko  
    import pandas as pd  
    import time  
    df = pd.read_excel('server_information.xlsx')  
    data=df.values  
    L = len(df)  
    print("检测到当前主机数：")  
    print(L)  
    for i in range(0,L):  
    IP = data[i][0]  
    port = data[i][1]  
    name=data[i][2]  
    password=data[i][3]  
    # 实例化一个transport对象  
    trans = paramiko.Transport((IP, port))  
    # 建立连接  
    trans.connect(username=name, password=password)  
    # 将sshclient的对象的transport指定为以上的trans  
    ssh = paramiko.SSHClient()  
    ssh._transport = trans  
    sftp = paramiko.SFTPClient.from_transport(trans)  
    stdin, stdout, stderr = ssh.exec_command('ip a|grep inet|grep brd')  
    # inet 10.0.20.12/22 brd 10.0.23.255 scope global eth0  
    i_IP = stdout.read().decode('utf-8')  
    Intranet_IP_str= i_IP.split()  
    Intranet_IP = Intranet_IP_str[1].split('/')  
    # 10.0.20.12 22  
    #localpath—本地文件地址，remotepath——服务器存放地址  
    sftp.put(localpath='/home/a.sh',  
    remotepath='/tmp/a.sh')  
    stdin, stdout, stderr = ssh.exec_command('cd tmp;./a.sh')  
    Host_information = stdout.read().decode('utf-8')  
    time.sleep(10)  
    sftp.get(localpath=Intranet_IP[0]+'.xml',  
    remotepath='/tmp/'+Intranet_IP[0]+'.xml')  
    #sftp.get—下载文件，sftp.put—上传文件  
    print(IP+":已完成")

![1683735043_645bc2036e8b00d962fb0.png!small](https://image.3001.net/images/20230511/1683735043_645bc2036e8b00d962fb0.png!small)

当我开开心心提交过去给客户的时候，不出意外要有意外了，客户说想要shell脚本，啊这，也行！shell而已，这回先把客户那边开放的端口，服务啥的给问清楚，具体需要我做到什么，先了解清楚了先，然后一番讨价还价下来，客户说他那边有个平台能批量上传和运行文件了，叫我实现下回收就行了，那这还不好办。

# 三、shell脚本实现

回到脚本这来，已知客户需要的是shell脚本，我又不会，那怎么办？还能怎么办，现学咯，然后就看了下shell编程，基础语法看差不多之后我觉得我又行了，话不多说，开整。首先我想的还是用ftp服务，毕竟这个能满足所有需求，然后我就搞了个ftp的，搞完发现其实shell也有支持连接其他服务器的功能，而且方式还很多，写的话也不难写。

    
    
    #!/bin/bash  
    #用户名  
    user=  
    #密码  
    password=  
    #本地存在这个文件的目录  
    local_url=/tmp  
    #上传的目的目录  
    server_url=/home  
    #服务器IP  
    ip=  
    #端口  
    port=22  
    cd ${local_url};  
    #定位在50分钟内生成的xml文件，这个可以根据自己的需求来改需要回收的数据类型  
    files=`find ${local_url} -mmin -50 -name '*.xml'`  
    for file in ${files}  
    do  
    echo ${file}  
    #建立ftp连接  
    lftp -u ${user},${password} sftp://${ip}:${port} <<EOF  
    cd ${server_url}/  
    lcd ${local_url}  
    put ${file}  
    by  
    EOF  
    done

到这里，我以为就搞定了，开开心心发过去，看了看点，三踮几啦，饮茶先啦，点了杯奶茶。不出意外要出意外了，客户说他那边没lftp这个服务，问我能不能用SCP服务，他们之前用的SCP服务，到手的奶茶突然不香了，也行！不就是SCP嘛，开整！也就是改下服务的事情。

    
    
    #!/bin/bash  
    #用户名  
    user=  
    #本地存在这个文件的目录  
    local_url=/tmp  
    #上传的目的目录  
    server_url=/home  
    #服务器IP  
    ip=  
    #端口  
    port=22  
    ​  
    cd ${local_url}  
    files=`find ${local_url} -mmin -50 -name '*.xml'`  
    for file in ${files}  
    do  
    echo ${file}  
    scp -P ${port} ${file} ${user}@${ip}:${server_url} <<EOF  
    by  
    EOF  
    done

这个的功能实现了，但是跟FTP不一样的是，FTP能够在命令中把密码加进去，而SCP需要自己输入密码。

    
    
    lftp -u ${user},${password} sftp://${ip}:${port} <<EOF  
    #账号密码在命令上  
    scp -P ${port} ${file} ${user}@${ip}:${server_url} <<EOF  
    #账号密码需要自己输入

客户看到又有问题了，啊这，能不能让他自己输入密码啊，我这不支持输入密码。也行，用expect写个监测关键字就行了，我没想到就是因为我这句也行，让我头秃了两天。

    
    
    #!/usr/bin/expect  
    #ip=`ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:"`  
    spawn scp -P 22 /home/ax/a.xml 用户名@服务器IP:/tmp  
    set timeout 20  
    #监测下面的命令行中有没有password这个关键字  
    expect "password"  
    exec sleep 1  
    #监测到了就发送密码  
    send "密码\r"  
    interact

这个只是实现了一部分的功能，上面我说到，跑完主机之后的数据文件是带本机IP的，所以我们需要找到我们的本机IP，而关键点就在这，如果我要使用

    
    
    ip=`ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:"`

这句命令来找IP的话，我需要用到bash解释器里面的东西，而我用expect是需要用到/usr/bin/expect这个解释器，而这两个是没办法直接引用到上面的，也就是一个shell脚本无法直接使用两个解释器。

    
    
    #!/usr/bin/expect  
    #!/bin/bash

找了两天的解决办法，什么方式都尝试了一遍，文件包含，命令行传参啥的都尝试了，都没办法，我甚至午休躺在椅子上面睡觉还梦到有别的解决办法，然后惊醒，本来已经打算跟客户说让他用ftp那个的时候，我偶然看到一个代码块，里面有个词引起了我的注意，内嵌类型！！！！！！当时就感觉有戏，好像我找的方式就是他，让仔细查了下内嵌类型是个啥，果然！！！！我只需要把我需要用到解释器的部分代码内嵌到我另一个解释器的代码里面，就可以了。

    
    
    #!/bin/bash  
    local_ip=`ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d "addr:"`  
    #用户名  
    user=  
    #密码  
    password=  
    #本地存在这个文件的目录，格式例如/home/ax/  
    local_url=  
    #上传的目的目录,格式：/tmp  
    server_url=  
    #端口  
    port=22  
    #服务器IP  
    server_ip=  
    #这里一定要加<<EOF,才能将另一个解释器的代码内嵌到这里来  
    /usr/bin/expect <<EOF  
    spawn scp -P ${port} ${local_url}${local_ip}_a.xml ${user}@${server_ip}:${server_url}  
    set timeout 20  
    expect "password"  
    exec sleep 2  
    send "${password}\r"  
    interact  
    expect eof  
    EOF  
    #结尾的时候要把EOF给结束掉，也就是将上面的代码包进来

这样直接把过滤文件的方式已经自动输入密码给完成了，其实如果想要实现那些自动上传脚本，执行这些也是能完成的，只要解决了两个解释器命令能够在同一个脚本里面执行，其他都很好解决，设计好逻辑思路就可以了，但是这个是属于被白嫖的服务，能少点需求就少点需求，然鹅，客户用完之后直呼好，但是他还是想用第一版的py脚本~

