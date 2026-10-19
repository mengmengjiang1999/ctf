## 工具技术介绍

### sysmon介绍

Sysmon是微软的一款轻量级的系统监控工具，提供有关进程创建，网络连接以及文件创建时间更改的详细信息,是安全事件检测、分析和溯源的神器，sysmon 13
增加了一个Event ID 25,可用于检测高级恶意攻击策略Process Hollowing和Process Herpaderping

### Process Hollowing和Process Herpaderping技术介绍

Process Hollowing：

    
    
    攻击者可以删除可执行文件中的代码，然后将其替换为恶意代码。黑客使用进程空心化攻击(类似于进程注入)来导致原本合法的进程执行恶意代码。可以在逃避潜在防御措施（例如检测分析软件）的情况下进行此攻击,执行流程为:map->modify section -> exeute
    

Process Herpaderping

    
    
    一种通过在映像映射后修改磁盘上的内容来掩盖进程意图的方法，执行流程为:writer->map-modify ->execute -> close
    

### Herpaderping工具介绍

Herpaderping是一种image被映射之后修改磁盘上的内容来隐藏进程意图的方法。

    
    
    作者的网站：https://jxy-s.github.io/herpaderping
    工具项目地址：https://github.com/jxy-s/herpaderping
    

绕过流程如下：

    
    
    1、将目标二进制文件写入磁盘，保持句柄打开
    2、将文件映射为image section
    3、使用节句柄创建进程对象
    4、使用相同的目标文件句柄，隐藏磁盘上的文件
    5、在进程中创建初始线程（此时，内核中的进程创建回调将启动。磁盘上的内容与image的内容不匹配。此时检查文件将导致错误的属性）
    6、关闭句柄，触发IRP_MJ_CLEANUP，此时安全产品开始检查文件（因为我们已经隐藏了正在执行的内容，所以此时的检查将导致错误的属性）
    

作者提供的流程图  
![image](https://image.3001.net/images/20210328/1616938197_606084d56ec6ebcf9319d.png!small)

## 实战Sysmon 13检测进程篡改

### Sysmon安装

Sysmonconfig-export.xml 配置文件

    
    
    <Sysmon schemaversion="4.50">
      <EventFiltering>
    	  <ProcessTampering onmatch="exclude">
    	  </ProcessTampering>
      </EventFiltering>
    </Sysmon>
    

sysmon安装  
![image](https://image.3001.net/images/20210328/1616938427_606085bbd6b26a3211f04.png!small)

### Herpaderping使用

参数说明： .\ProcessHerpaderping.exe 恶意文件名称,新文件名称,伪造程序名称  
![image](https://image.3001.net/images/20210328/1616938451_606085d36cc4379ddbc9b.jpg!small)mimikatz已存在微软的数字签名  
![image](https://image.3001.net/images/20210328/1616938512_6060861053ca8f4a8b1a5.png!small)

### Sysmon进程篡改日志信息

进程篡改命令记录![image](https://image.3001.net/images/20210328/1616938613_606086759fdbfdfb6911e.png!small)

