## 二开修改的内容

大概只有这些

github已经有项目收集二开的思路

欢迎大佬提供思路或者提供修改代码

    
    
    https://github.com/lucksec/magicReform_cobaltstrike.jar

修改细节

    
    
    修改监听不返回任何数据(带user-agent的请求302，不带的不返回任何数据)  
    添加teamserver认证白名单限制登陆IP  
    去除checksum8特征  
    免杀VT全绿  
    默认证书已替换  
    防止stage被扫  
    去除listenerConfig特征字符串  
    cs去除beaconeye特征  
    修复CVE-2022-39197  
    cs修复错误路径泄漏stage  
    增加谷歌动态密码(身份验证器)  
    修复cs4.5的foreign派生bug  
    添加中文汉化翻译  
    内置破解

## 二开思路

### 第一步，去除特征

防止空间搜索引擎对开放的端口进行标记

对teamserver进行添加内置防火墙

修改逻辑

    
    
    修改监听不返回任何数据(带user-agent的请求302，不带的不返回任何数据)  
    去除listenerConfig特征字符串  
    cs去除beaconeye特征  
    去除checksum8特征  
    默认证书已替换  
    防止stage被扫

这样在空间搜索引擎中，无法给vps进行打标，确保vps不被标红

### 第二步，去除BeaconEye

    
    
    引用：https://www.t00ls.com/articles-63215.html

使用修改后的beacon.dll和beacon.x64.dll，不做其他任何修改，上线后用BeaconEye扫不出来

### 第三步，添加认证

    
    
    增加谷歌动态密码(身份验证器)  
    修复CVE-2022-39197

利用谷歌验证码进行双因子认证

    
    
    参考项目：https://github.com/lovechoudoufu/GoogleCSAgent_cdf

登陆时需要填写谷歌动态验证码

防止teamserver被爆破

修复CVE-2022-39197

### 第四步，免杀

目前VT全绿

![1670078848_638b6180cdc94893a8de3.png!small?1670078849844](https://image.3001.net/images/20221203/1670078848_638b6180cdc94893a8de3.png!small?1670078849844)

    
    
    免杀常规免杀  
    shellcode免杀  
    loader免杀  
    ......等等

### 第五步，汉化

添加中文汉化翻译

引用被github，dmca项目

    
    
    https://github.com/Twi1ight/CSAgent

# 总结

· 二开cs无非就是那几个特征

· 二开后免的配置什么域前置，cdn，云函数什么，当然配置也是可以的（更安全）

· 内置过滤规则（到时候可以把更多过滤规则集成）

· 接下来准备去看看cs4.7（主要看中原生支持S5代理）

· 接下看看能不能修改4.5支持S5

· 可能过段时间开源，大家一起魔改

