## Wazuh Ruleset

Wazuh的规则集由许多预定义的解码器（decoders）和规则（rules）组成。Wazuh规则是配置和优化Wazuh生成的每个告警的关键组件，包括通过标准syslog或rootkit检测而发送的告警。

Wazuh中预定义规则位于/var/ossec/ruleset/rules/，其解码器位于/var/ossec/ruleset/decoders/。不要在这些位置编辑规则或解码器，因为Wazuh的更新会覆盖你的更改。保存自定义规则和解码器的位置分别是/var/ossec/etc/rules/和/var/ossec/etc/decoders/。

Wazuh规则集只存储在Wazuh Manager中，因为只有Wazuh Manager负责解码和分析日志事件。

在Wazuh中，我们区分了原子（atomic）规则和关联（omposite）规则。原子（atomic）规则是简单的规则，只分析单个事件，没有任何相关性。此类规则的示例很可能是“身份验证失败”的日志消息或关于独特事件的任何警报。然而，关联（omposite）规则在给定的时间框架中寻找原子（atomic）规则的重复匹配。通过使用关键词“发生频率”和“时间范围”，将会很容易识别关联（omposite）规则。

### Wazuh规则中的告警级别

下面是所有Wazuh告警级别列表，其中有简短的描述和一个示例来描述其相关性。

 **级别**|  **描述**|  **告警示例**  
---|---|---  
  
Level 0

| 忽略，不会采取任何行动| 用来避免误报，这里没有安全问题  
Level 2| 系统低优先级的通知| 没有安全相关性的状态消息  
  
Level 3

| 成功或授权的事件| 成功登录，防火墙允许的事件  
Level 5| 用户生成的错误| 密码错误，拒绝操作  
Level 6| 低威胁的攻击| 对系统没有威胁的蠕虫或病毒(例如Linux机器上的Windows蠕虫)  
Level 9| 来自无效源的错误信息| 试图以未知用户或无效的来源登录  
Level 10| 用户产生重复性的错误| 多个错误密码，多次登录失败  
Level 11| 完整性检查的警告| 检测到二进制文件被修改或通过rootcheck检测到rootkit存在信息。它们可能表明袭击成功。  
Level 12| 重要事件| 来自系统或内核的错误或告警  
Level 13| 异常错误(重要)| 常见的攻击模式，如缓冲区溢出尝试  
Level 14| 重要安全事件| 多个检测规则形成关联结果  
Level 15| 严重的攻击成功| 很少产生误报，发现这个级别的告警需要立即处理  
  
  

##  **Wazuh Decoder**

Wazuh中的解码（decoding）就是从特定类型的事件中提取相关数据。解码分为预解码阶段和解码阶段。

  1. 预解码阶段：从已知字段(如syslog记录头中的字段)提取静态信息。这通常包括时间戳、主机名和程序名，这些值通常在所有syslog消息中都能找到，而不管哪个应用程序生成它们。
  2. 解码阶段：将从事件中提取更多的动态信息，如源IP地址、用户名、URL等等。一个或多个解码器专门用于从许多不同的应用程序和日志源中提取字段数据。

一旦日志事件被解码，Wazuh就可以根据其规则集对其进行评估，以确定是否应该生成警报。如果日志没有解码，Wazuh规则将被限制在寻找出现在日志事件中任何地方的通用子字符串，从而大大降低了生成告警的质量。

### 编写一个自定义的解码规则，提取日志中的用户名和源IP地址

日志样例：

> Dec 4 17:07:01 myserver Fakeinc: Accepted password for user tony, IP:
> 1.2.3.4

编辑/var/ossec/etc/decoders/下的local_decoder.xml文件，

>
>     <decoder name="fakeinc_custom">
>         <program_name>Fakeinc</program_name>
>     </decoder>
>     <decoder name="fakeinc_custom_message">
>         <parent>fakeinc_custom</parent>
>         <prematch> password for user </prematch>
>         <regex>^\w+ password for user (\w+), IP: (\S+)</regex>
>         <order>dstuser, srcip</order>
>     </decoder>

我们可以看到，新的父解码器是由它的唯一名称“fakeinc_custom”定义的。解码器的“name”是一个必填字段。它有一个子解码器“fakeinc_custom_message”，将“fakeinc_custom”作为其父解码器。  
父解码器将匹配任何先于“Fakeinc”的程序名的事件。子解码器专门在这些Fakeinc日志中查找包含短语“password for
user”的消息，然后尝试通过正则表达式提取字段dstuser和srcip。

配置之前的效果，提示解码完成，未匹配到解码器：

![](https://image.3001.net/images/20210311/1615463841_604a05a1386b88b522088.png!small)

配置之后的效果，找到对应的fakeinc_custom解码器，成功提取dstuser，srcip字段：

![](https://image.3001.net/images/20210311/1615463921_604a05f13d6af53535622.png!small)

  

## Wazuh Rules

编写匹配以下日志消息的自定义规则，并分配适当的警报和级别:

> Dec 4 17:07:01 myserver Fakeinc: Accepted password for user tony, IP:
> 1.2.3.4
>
> Dec 4 17:07:01 myserver Fakeinc: Failed password for user tony, IP: 1.2.3.4
>
> Dec 4 17:07:01 myserver Fakeinc: Application is shutting down: Internal
> error
>
> Dec 4 17:07:01 myserver Fakeinc: DEBUG: Received OK.

由于有4条非常相似的日志消息，然而我们只想关注日志消息中变化的那一部分，所以我们首先需要创建一个“父规则”，当没有其他“子规则”触发时，它总是触发。

    
    
    <rule​ ​id​=​"100202"​ ​level​=​"0">
        <decoded_as>fakeinc_custom</decoded_as> 
        <description>Parent rule for Fakeinc custom</description> 
    </rule>

我们将规则ID设置为100202，并将警报级别设置为0，因为我们不希望在该规则触发时发出任何警报。相反，我们希望触发其他子规则。接下来我们定义我们想要使用的解码器，即“fakeinc_custom”解码器，现在Wazuh知道在哪里查找以提取正确的字段。规则的最后一部分是描述，这应该是尽可能有意义和连贯的，这样其他人就会更好地理解这条规则的意义。

可以看到成功匹配到规则100202：

![](https://image.3001.net/images/20210312/1615521202_604ae5b24252db135465e.png!small)

接下来我们开始写子规则：

    
    
    <rule id="100203" level="7"> 
        <if_sid>100202</if_sid> 
        <match>Failed</match> 
        <description>Fakeinc Custom: Failed password</description> 
        <group>authentication_failed</group> 
    </rule>

我们使用<if_sid>标记设定凡是父规则100202而来的日志，都会进行匹配，使用<match>标记设定如果匹配到“Failed”关键字，则产生level7的告警事件。

可以看到成功匹配到了级别是7的密码失败登录告警：

![](https://image.3001.net/images/20210312/1615521529_604ae6f948b1fb3b658e1.png!small)

  

接着我们可以写第二条子规则，凡是通过父规则ID100202而来的日志，匹配到Accepted关键字则生成一条Level3的信息事件。

    
    
    <rule id="100204" level="3"> 
        <if_sid>100202</if_sid> 
        <match>Accepted</match> 
        <description>Fakeinc Custom: Accepted password</description> 
    </rule>

可以看到成功匹配到了级别是3的成功登录事件：

![](https://image.3001.net/images/20210312/1615521670_604ae7862f6b585e688e2.png!small)

最后，我们将编写一个关联规则，在多次尝试失败的密码后触发该规则。

这次我们使用原子规则100203作为父规则，因为它已经匹配了失败的密码尝试。我们希望将警报级别进一步提高到10，以便在5分钟间隔内进行5次尝试后触发。

    
    
    <rule id="100205" level="10" frequency="5" timeframe="300"> 
        <if_matched_sid>100203</if_matched_sid> 
        <same_source_ip /> 
        <description>Fakeinc Custom: Multiple Failed passwords</description> 
        <group>authentication_failures</group> 
    </rule>

我们使用标签<if_matched_sid>来引用新的父规则。并使用<same_source_ip />标签来限制仅来自相同IP地址的尝试。

可以看到一开始匹配到的还是级别为7的100203告警，但是在连续输入5次密码失败之后，会生成级别为10的10205告警：

![](https://image.3001.net/images/20210312/1615521892_604ae864888338148ed95.png!small)

  

  

  

