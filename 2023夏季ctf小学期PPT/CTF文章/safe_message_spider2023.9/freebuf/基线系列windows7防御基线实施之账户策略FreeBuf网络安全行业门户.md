> 国际标准基线CCE编号索引https://www.scaprepo.com/
>
> 以下配置建议使用组策略来统一操作（其他方法设置也行）：gpedit.msc 【以下配置默认环境是win7，如需其他环境，需额外检查】
>
> 可用于等保2.0，合规与ISO27001
>
> 注意等保与合规的重点不是实施的一致性，而是在于不同人对于同一标准的不同解读
>
> gpedit.msc -- 计算机配置 -- windows 设置 -- 安全设置 -- 账户策略 -- 密码策略

## 密码策略

1.确保“ **强制密码历史记录** ”设置为“24 个或更多密码” （企业内部酌情调整）

今天用123456，明天改成654321，后天再改回来123456（ **强制密码历史记录** 次数限制。则修改失败）

![image](https://image.3001.net/images/20210720/1626751504_60f64210b9cec12b906d8.png!small)

默认值：域成员24，单机为0

https://www.scaprepo.com/view.jsp?id=CCE-35219-5

【密码最短使用期限】需要给值，不然无法阻止“爆破”

## 检查泄露的密码

哪些账号发生了泄露或者撞库？

这么多年以来，发生了大量的信息泄露事件。密码安全吗？查一下

匿名性的发送密码sha-1哈希值前5位给它  
![image](https://image.3001.net/images/20210720/1626754947_60f64f834373dfd7bcb27.png!small)1.使用curl可以查看密码哈希中带有21BD1字符串的密码数量：

 **curl https://api.pwnedpasswords.com/range/21BD1**

2.在任何Linux虚拟机的主目录中，创建具有以下内容的pwnpassword.sh脚本：

    
    
    #!/bin/bash
    candidate_password=$1
    echo "Candidate password: $candidate_password"
    full_hash=$(echo -n $candidate_password | sha1sum | awk '{print
    substr($1, 0, 32)}')
    prefix=$(echo $full_hash | awk '{print substr($1, 0, 5)}')
    suffix=$(echo $full_hash | awk '{print substr($1, 6, 26)}')
    if curl https://api.pwnedpasswords.com/range/$prefix | grep -i
    $suffix;
     then echo "Candidate password is compromised";
     else echo "Candidate password is OK for use";
    fi
    

3.将可执行权限添加到脚本：

 **chmod u+x pwnedpasswords.sh**

4.运行脚本，将TurkeyLips指定为密码：

 **./pwnedpasswords.sh TurkeyLips**

工作站锁屏

集中身份验证点尽可能的少一点，包括网络、安全和云系统

加密用户名和身份验证凭据的传输

确保“最长密码期限”设置为“60 天或更少天，但不是 0

![图片.png](https://image.3001.net/images/20210720/1626755097_60f65019d193bb89ddfda.png!small)

此策略设置的值范围为 0 到 999 天。 如果将该值设置为 0，则密码将永不过期。

CCE-34907-6

确保“密码最短使用期限”设置为“1 天或更多天”

![图片.png](https://image.3001.net/images/20210720/1626755148_60f6504c33e4d5e6afbad.png!small)

CCE-35366-4

确保“最小密码长度”设置为“14 个或更多字符”

![图片.png](https://image.3001.net/images/20210720/1626755235_60f650a3ca290fdbe6bc1.png!small)

推荐密码短语：Woaiwodezuguo123!

CCE-33789-9

确保“密码必须满足复杂性要求”设置为“已启用”

![图片.png](https://image.3001.net/images/20210720/1626755256_60f650b81468250a331ba.png!small)

7位字母，大约两小时爆破；引入大小写，大约60小时爆破；引入特殊字符，增加复杂度

CCE-33777-4

确保“使用可逆加密存储密码”设置为“已禁用”

![图片.png](https://image.3001.net/images/20210720/1626755297_60f650e1e78798d6c6bee.png!small)

如果您的组织通过远程访问或 IAS 服务使用 CHAP 身份验证协议或 IIS 中的摘要式身份验证，则必须将此策略设置配置为“已启用”。

CCE-35370-6

## 帐户锁定策略

“帐户锁定持续时间”设置为15 分钟以上

![image](https://image.3001.net/images/20210720/1626754726_60f64ea63863b0a396f10.png!small)

指定失败数量后账户将被锁定。 如果将 帐户锁定持续时间 配置为 0，帐户将保持锁定状态，直到管理员手动将其解锁。

CCE-35409-2

确保“帐户锁定阈值”设置为“10 次或更少，但不是 0”

![图片.png](https://image.3001.net/images/20210720/1626755323_60f650fb2ed4facf5e530.png!small)

CCE-33728-7

确保“重置帐户锁定计数器”设置为“15 分钟或更长”

![图片.png](https://image.3001.net/images/20210720/1626755384_60f6513873c8af2c599e2.png!small)

CCE-35408-4

