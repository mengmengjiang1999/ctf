**Jenkins是一个广泛使用的开源自动化服务器，它允许DevOps开发人员高效、可靠地构建、测试和部署软件。**

**为了充分利用Jenkins的模块化架构，开发人员利用插件来扩展其核心功能。截至目前，Jenkins的插件索引中有1600多个社区贡献的插件。其中一些插件存储未加密的纯文本凭据。在数据泄露的情况下，网络犯罪分子可以在用户不知情的情况下访问这些信息。**

我们将专门讨论以下信息泄露漏洞以及受影响的相应插件：

![](https://image.3001.net/images/20190902/1567392104_5d6c81687d47c.png!small)

在撰写本文时，Port Allocator、testlink和caliper-ci插件中的漏洞尚未修复。当前版本的eggplant插件已弃用。

##  访问存储的凭据

可以利用Jenkins插件漏洞获取用户凭据。当具有扩展读取权限或访问主文件系统的用户凭据泄漏时，攻击者也可访问其他集成服务，尤其是当用户对不同平台或服务使用相同的密码时。

插件配置通常以XML文件的形式存储在$jenkins_home
root中，该文件定义了每个插件结构和设置。通常插件的配置保存为工作配置文件的一部分，例如$jenkins_home/job s/new
job/config.xml。如果凭证是插件配置的一部分，那么它们应该以加密的形式存储，而对于Gogs, Port Allocator, Caliper
CI, TestLink, and eggPlant插件则不是这样。

凭证存储在未加密的纯文本中：

存储凭据的正确方法是将其委托给第三方凭据提供程序，然后由配置文件中的CredentialSid引用该插件。

如果用户能够读取配置文件，则只能查看CredentialSid引用，实际凭证存储在引用中。

![](https://image.3001.net/images/20190902/1567392432_5d6c82b048145.png!small)

包含在默认建议插件列表中的凭据插件用于存储加密的凭据。以下描述了凭据存储的详细信息。

![](https://image.3001.net/images/20190902/1567392487_5d6c82e745446.png!small)

此插件将加密的凭据存储在$jenkins_home/credentials.xml中。

![](https://image.3001.net/images/20190902/1567392537_5d6c831932ff2.png!small)

在上面的示例中，密码存储以base64为编码。通过使用base64解码器，我们可以观察到某些不可打印的字符被编码。

![](https://image.3001.net/images/20190902/1567392612_5d6c8364a0636.png!small)

事实上，加密的密码和加密元数据是使用base64编码的。

用于解密的密钥是在Jenkins中硬编码的。Jenkins的不同安装会导致不同的key。密钥被加密存储在$jenkins_home/secrets/hudson.util.secret文件中。hudson.util.secret文件是通过aes使用从主密钥派生的密钥加密的，这在每个jenkins安装中也有所不同。

这意味着，保护$jenkins_home/secrets目录对于防止泄露存储的凭证至关重要。在master上执行作业或构建可能会影响Jenkins的整体安全性，例如安装插件、创建新作业、读取和删除凭据以及其他私有数据。在master上运行的作业还可以授予较低访问权限，并允许其使用shell命令打印数据。

##  安全建议

以纯文本形式存储的凭证可能构成直接威胁。但是，管理员还应该记住，有权访问$jenkins_home/secrets目录的用户也可以访问存储的凭证。$jenkins\u
home/hudson.util.secret和$jenkins\u
home/secrets/master.key是用于解密保存的密码的文件，它们的暴露会使攻击者对存储的密码进行解密。

像所有DevOps工具一样，Jenkins应该考虑到安全性。在其默认设置中，Jenkins不执行安全检查。因此，Jenkins建议用户执行最佳实践，包括对用户进行身份验证、强制访问控制，而不是在大型系统的主节点上构建。

如果作业必须在主节点上运行，Jenkins建议使用作业限制插件，该插件可以基于用户权限限制作业执行或节点配置。

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/hiding-in-plain-text-jenkins-plugin-vulnerabilities/)，由Kriston编译，转载请注明来自FreeBuf.COM**

  

