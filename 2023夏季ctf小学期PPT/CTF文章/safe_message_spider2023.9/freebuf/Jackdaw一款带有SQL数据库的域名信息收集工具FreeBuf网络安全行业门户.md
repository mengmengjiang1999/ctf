![1.jpg](https://image.3001.net/images/20200408/1586358439_5e8de8a7d9f9d.jpg!small)**Jackdaw这款工具能够帮助广大研究人员收集关于目标域名的所有详细信息，并将这些数据存储在一个SQL数据库中。收集完成之后，Jackdaw还能够以图形化的方式给用户进行数据呈现，并显示目标域名对象与其他对象之间的交互情况，并告知用户其中存在的潜在安全问题。除此之外，它还带有非常方便的功能来存储、查询和报告用户哈希或密码，以帮助用户实现密码破解的目标。**

## 工具下载

广大研究人员可以使用下列命令将Jackdaw项目源码克隆至本地：

    
    
    git clone https://github.com/skelsec/jackdaw.git

## 功能介绍

## 数据收集

### 通过LDAP

LDAP枚举阶段将查询活动目录信息、用户、设备、OU和组对象等数据，而这些数据之后将会以节点的形式在图形化界面中显示，并且会存储在数据库的独立表中。除此之外，这些所有对象的安全描述符都将会在之后进行解析，并将对应的ACL添加至数据库中（DACL）。成员关系信息将会在图形化界面中以边的形式呈现，而且自定义SQL查询也可以对上述数据对象执行。

### 通过SMB

SMB枚举阶段的数据查询将通过连接域名中的每一台设备来获取共享信息、本地组、会话信息和NTLM数据等等。

### 通过LSASS导出（可选）

框架将允许用户上传LSASS内存导出数据，存储凭证并扩展会话信息表。这些数据都可以被用来当作图中的额外边。除此之外，框架还使用了这些信息来创建可供破解的凭证密码报告。

### 通过DCSYNC结果（可选）

框架允许用户上传DCSYNC文件来存储凭证。它们将被用于图中的额外边（共享密码）。除此之外，框架还是用这些信息来创建可供破解的凭证密码报告。

### 通过手动上传（可选）

该框架允许我们手动扩展可用的数据库。比如说，当工具在给定计算机上发现了用户会话信息之后，我们就可以手动上传这些会话数据，并填充数据库和结果图。

## 工具命令样例

目前，Jackdaw的绝大部分命令都可以直接通过Web API来使用，除了数据库初始化之外。

## 数据库初始化

    
    
    jackdaw --sql sqlite:///<full path here>/test.db dbinit

## 枚举功能

使用整合SSPI的完整枚举-仅支持Windows：

    
    
    jackdaw --sql sqlite:///test.db enum 'ldap+sspi://10.10.10.2' 'smb+sspi-ntlm://10.10.10.2'

使用用户名和密码的完整枚举-平**立（密码为Passw0rd!）：

    
    
    jackdaw --sql sqlite:///test.db enum 'ldap://TEST\victim:Passw0rd!@10.10.10.2' 'smb+ntlm-password://TEST\victim:Passw0rd!@10.10.10.2'

LDAP-仅使用用户名和密码的枚举-平**立（密码为Passw0rd!）：

    
    
    jackdaw --sql sqlite:///test.db ldap 'ldap://TEST\victim:Passw0rd!@10.10.10.2'

开启交互式Web接口和访问额外功能：

    
    
    jackdaw --sql sqlite:///<FULL PATH TO DB> nest

访问`<http://127.0.0.1:5000/ui>`以开启API。

UI接口构建完成之后，访问`<http://127.0.0.1:5000/nest>`以使用图形化接口。

## 技术部分

## 后台数据库

Jackdaw使用了SQLAlchemy
ORM模块，并允许我们使用任意SQL后台数据库。我们在测试时主要使用的是SQLite，但你可以根据自己的喜好来选择。

## 构建UI

该工具的UI接口采用React开发，在使用之前需要进行UI构建。因此，你需要安装NodeJS和npm。接下来：

1、进入到`jackdaw/nest/site/nui`；

2、运行命令：`npm install`；

3、运行命令：`npm run build`；

上述操作完成之后，UI构建就算正式完成了，接下来你就可以开始使用Jackdaw了。

## 项目地址

Jackdaw：【[ _GitHub传送门_](https://github.com/skelsec/jackdaw)】

*** 参考来源：[
_skelsec_](https://github.com/skelsec/jackdaw)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

