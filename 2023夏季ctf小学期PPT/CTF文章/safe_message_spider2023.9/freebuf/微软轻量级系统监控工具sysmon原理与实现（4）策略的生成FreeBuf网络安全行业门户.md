## 前情提要

>
> [微软轻量级监控工具sysmon原理与实现（1）](https://www.freebuf.com/articles/system/184910.html)
>
>
> [微软轻量级系统监控工具sysmon原理与实现（2）](https://www.freebuf.com/articles/system/182895.html)
>
>
> [微软轻量级系统监控工具sysmon原理与实现（3）](https://www.freebuf.com/articles/system/250909.html)

上一篇讲了sysmon各个内核事件的输出结构，
今天主要讲解的是sysmon注册EventFiltering规则的congfig文件得xml和sysmon命令行生成rule规则文件的算法过程。

##  **一、Config的xml结构**

 **以进程为例**

    
    
    <Sysmon schemaversion="4.21">
    
    <EventFiltering>
    
    <RuleGroup name="" groupRelation="or">
    
    <ProcessCreate onmatch="exclude">
    
    <ParentImage condition="is">C:\Program Files (x86)\RES Software\Workspace Manager\pfwsmgr.exe</ParentImage>
    
    <ParentImage condition="is">C:\Program Files (x86)\RES Software\Workspace Manager\respesvc64.exe</ParentImage>
    
    <ParentImage condition="is">C:\Program Files (x86)\Ivanti\Workspace Control\pfwsmgr.exe</ParentImage>
    
    <ParentImage condition="is">C:\Program Files (x86)\RES Software\Workspace Manager\ResPesvc64.exe</ParentImage>
    
    <ParentImage condition="is">C:\Program Files\RES Software\Workspace Manager\respesvc.exe</ParentImage>
    
    <ParentImage condition="is">C:\Program Files\Ivanti\Workspace Control\ResPesvc.exe</ParentImage>
    
    </RuleGroup>
    
    </EventFiltering>
    
    </Sysmon>

 **ProcessCreate** 是事件的类型， **onmatch** 是匹配的类型， **ParentImage**
是过滤的具体的字段，这段规则的表示的是 **exclude** 是排除掉，就是不记录这些进程。

Sysmon 配置config的方式有两种

> Sysmon -i 配置文件名 安装的时候配置
>
> Sysmon -c 配置文件名 更新配置文件

##  **二、Config的xml解析**

下面就开始讲解sysmon的解析过程。

在exe的入口wmain函数里，有个

 **SysmonUpdateConfig(argun, argwcv2, &rule_xml_data, &pRule_size, (WCHAR
**)&lpFileName, (WCHAR *)a6, v13)**

来解析参数判断是否是 -I -c 的参数

![1602662241_5f86af614195cd9e5de0a.png!small](https://image.3001.net/images/20201014/1602662241_5f86af614195cd9e5de0a.png!small)

来看下这个函数内部的实现。

先对比下参数是否能对应内置的参数表

![1602662263_5f86af773176a7c12dc68.png!small](https://image.3001.net/images/20201014/1602662263_5f86af773176a7c12dc68.png!small)

结构体stru_4BF890 就是内置的参数表

![1602662340_5f86afc40e73697485984.png!small](https://image.3001.net/images/20201014/1602662340_5f86afc40e73697485984.png!small)

一共24个参数表，他的结构体是

    
    
    struct _Sysmon_Xml_Config_Cmd
    
    {
    
    ULONG flags;
    
    String_Name_0x8 BigCmd;
    
    String_Name_0x8 SmallCmd;
    
    Sysmon_Parse_Param *Param2;
    
    };

有全称和缩写参数两种。第一个数值flags 表示是否开启的标志位，最后一个结构Param2是附带参数的值会被动态的写入这个结构里方便计算，hash
，判断是否改变了。可以看到下面代码是在找到对应的参数后，会把后面附带的参数加如param2

![1602662374_5f86afe69c79b1c9f6c0e.png!small](https://image.3001.net/images/20201014/1602662374_5f86afe69c79b1c9f6c0e.png!small)

如果找到-c 的参数后就会解析后面的文件，并且解析里面的xml的内容变成规则，同时计算这个文件的hash值

![1602662418_5f86b012c75effa184b6b.png!small](https://image.3001.net/images/20201014/1602662418_5f86b012c75effa184b6b.png!small)

 **CreateSysmonConfigValid(pXmlFileName, pXmlData)** 函数是计算解析xml

下面我就看他如何解析的

![](https://image.3001.net/images/20201014/1602662446_5f86b02e)

