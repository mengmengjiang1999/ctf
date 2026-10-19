废话不多说，直接进入正题。

我们在进行测评的时候首先要确定资产的关键程度（注意：不同关键程度资产安全策略可能不同）。

![1683161194_6453006ab66744b46b9e6.png!small?1683161197150](https://image.3001.net/images/20230504/1683161194_6453006ab66744b46b9e6.png!small?1683161197150)

然后根据安全策略对相应资产进行核查

![1683161338_645300fab46883cfc0683.png!small?1683161341416](https://image.3001.net/images/20230504/1683161338_645300fab46883cfc0683.png!small?1683161341416)

下面我们先以Linux操作系统为例。

## 一、身份鉴别

### a）应对登录的用户进行身份标识和鉴别，身份标识具有唯一性，身份鉴别信息具有复杂度要求并定期更换。

咱们直接先看答案，然后根据答案进行复现相关知识点。

![1683160795_6452fedb67e85dc4e058d.png!small?1683160798515](https://image.3001.net/images/20230504/1683160795_6452fedb67e85dc4e058d.png!small?1683160798515)

 **1.通过 pam_pwquality
设定口令长度检查和复杂度检查，未添加参数enforce_for_root，root用户可以设置自身及其他操作系统用户不符合口令安全策略的口令。**

现场情况：

查看 /etc/pam.d/system-auth

![1683161592_645301f8387f02ba06d03.png!small?1683161595186](https://image.3001.net/images/20230504/1683161592_645301f8387f02ba06d03.png!small?1683161595186)

查看/etc/security/pwquality.conf

![1683161651_64530233e656786268e19.png!small?1683161654917](https://image.3001.net/images/20230504/1683161651_64530233e656786268e19.png!small?1683161654917)

再确定相应的安全策略

![1683162390_645305166c0f659278725.png!small?1683162392769](https://image.3001.net/images/20230504/1683162390_645305166c0f659278725.png!small?1683162392769)

根据截图，我们可以判断该系统通过 pam_pwquality 模块设定相应的口令长度以及复杂度，并且发现system-auth文件与pwquality.conf文件中minlen参数冲突了。经测试，冲突的参数以system-auth文件中配置的为准，所以这里的minlen=12。

最终配置情况为：minlen=12，minclass=3，maxrepeat=0，maxclassrepeat=0，lcredit=0，ucredit=0，dcredit=0，ocredit=0。

 **参数详解：**

minlen=N 密码最小长度

maxrepeat 新密码中允许的最大连续相同字符数，如果为0代表禁用

maxclassrepeat 新密码中允许的同一类的最大连续字符数

dcredit=N N >0密码中最多有多少个数字长度加1;

N<0密码中最少有多少个数字

lcredit=N 小写字母的个数

ucredit=N 大写字母的个数

ocredit=N 特殊字母的个数

minclass=N 密码组成(大/小字母,数字,特殊字符)

authtok_type= enforce_for_root 表示root用户也需遵守该规则

所以是满足长度以及复杂度要求，但是缺乏限制root账户的手段。但是经测试 authtok_type= enforce_for_root
写在pwquality.conf 文件中该参数仅会提示，但并不生效，需写在system-auth文件中（不清楚啥情况）。

![1683170367_6453243f3b8680a7fa338.png!small?1683170369496](https://image.3001.net/images/20230504/1683170367_6453243f3b8680a7fa338.png!small?1683170369496)

所以第一点的检查还是比较简单的，之前类似的都有考察过。

 **2./etc/login.defs 中设定的PASS_MAX_DAYS
口令有效期检查策略仅适用于之后创建的用户，经查看/etc/shadow文件中各用户口令有效期，root和mysql账户口令有效期为99999（天），不符合安全策略要求**

第二点就更简单了，直接查看/etc/shadow文件，发现root和mysql账户均为99999

![1683171096_645327186a55f3c9aa080.png!small?1683171099251](https://image.3001.net/images/20230504/1683171096_645327186a55f3c9aa080.png!small?1683171099251)

再查看/etc/login.defs文件，PASS_MAX_DAYS 只适用于进行该设置以后，新添加的用户，PASS_MIN_LEN
参数无效，root账户设置后到期也必须修改密码。

![1683171245_645327ad9793b0a41669e.png!small?1683171248522](https://image.3001.net/images/20230504/1683171245_645327ad9793b0a41669e.png!small?1683171248522)

 **3\. /etc/pam.d/sshd 文件中第一行添加了 auth sufficient pam_listfile/so onerr=succeed
item=user sense=allow file=/etc/bduser 配置项，其中/etc/bduser中所列的 securityM02
用户能够以任意口令 SSH 远程登录，绕过了操作系统的身份鉴别过程**

这个就考察测评师对 pam 认证模块的理解了，首先我们先看对应的配置文件，一般登录我们都是采用ssh的方式，所以本地登录可能不作要求，但最好带过看一眼
system-auth 文件中是否也存在认为配置的情况。这里查看/etc/pam.d/sshd 文件

![1683172162_64532b427ec4e8362eb9d.png!small?1683172165056](https://image.3001.net/images/20230504/1683172162_64532b427ec4e8362eb9d.png!small?1683172165056)

这里笔者当时没查这么细，虽有研究过pam一些模块，但感觉不会考这么细，就没深入了，结果这次居然考了，而且这个模块刚好没记录过，所以直接寄了，没查出来。这次也没有/etc/bduser的截图，后续经本地测试，发现可免密登录。

这边先简单介绍下pam_listfile.so 模块：

pam_listfile.so模块的功能和pam_access.so模块类似，目标也是实现基于用户/组，主机名/IP，终端的访问控制。不过它实现的方式和pam_access.so会稍微有些不同，因为它没有专门的默认配置文件。访问控制是靠pam配置文件中的控制选项和一个自定义的配置文件来实现的。而且除了针对上述访问源的控制之外，还能够控制到
ruser，rhost，所属用户组和登录shell。所以有些用户认为它的功能似乎比pam_access.so更加灵活和强大一些。

使用pam_listfile.so模块配置的格式分为五个部分：分别是item、onerr、sense、file以及apply。 其中：

a）item=[tty|user|rhost|ruser|group|shell]：定义了对哪些列出的目标或者条件采用规则，显然，这里可以指定多种不同的条件。

b）onerr=succeed|fail：定义了当出现错误（比如无法打开配置文件）时的缺省返回值。

c）sense=allow|deny：定义了当在配置文件中找到符合条件的项目时的控制方式。如果没有找到符合条件的项目，则一般验证都会通过。

d）file=filename：用于指定配置文件的全路径名称。

e）apply=user|@group：定义规则适用的用户类型（用户或者组）。

而至于file文件的写法就简单了，每行一个用户或者组名称即可。所以，当需要对其它服务进行类似的访问控制的时候，就可以照葫芦画瓢。例如现在需要在SSH服务器上对ssh客户端实现基于用户的访问控制

 **示例一：**

不允许 zfy 账号通过ssh方式登录。做法如下，加入这么一行：

auth required pam_listfile.so item=user sense=deny file=/etc/denyusers
onerr=succeed

![1683172400_64532c30230d1518b2c96.png!small?1683172402553](https://image.3001.net/images/20230504/1683172400_64532c30230d1518b2c96.png!small?1683172402553)

然后在/etc/denyusers 文件中加入这个用户，此用户会被拒绝登录，其余账户可正常登录

![1683172444_64532c5c135af33502e24.png!small?1683172446354](https://image.3001.net/images/20230504/1683172444_64532c5c135af33502e24.png!small?1683172446354)

 **示例二：**

例如能力验证，sufficient （pam模块认证规则以及说明网上一搜一大把，这里就不介绍了，贴一张简单的图）

![1683172585_64532ce9deeddcb518d6c.png!small?1683172588777](https://image.3001.net/images/20230504/1683172585_64532ce9deeddcb518d6c.png!small?1683172588777)

通过后就不进行下面的认证了，所以在/etc/bduser中的用户可以跳过密码认证，这样的话只要通过第一条，后面的auth认证就不进行了，导致该文件内用户输入任意密码均可登录。

![1683172644_64532d24dcf0fb2476b87.png!small?1683172647890](https://image.3001.net/images/20230504/1683172644_64532d24dcf0fb2476b87.png!small?1683172647890)

我这边随便输入密码均可登录成功。

![1683172660_64532d34b35aef1f2c555.png!small?1683172663763](https://image.3001.net/images/20230504/1683172660_64532d34b35aef1f2c555.png!small?1683172663763)

所以这个点可能失分会较多，如果自身没去研究过pam认证机制，或者不认识这个模块，就容易忽略，考的还是比较细致的。

###  **b）应具有登录失败处理功能，应配置并启用结束会话、限制非法登录次数和当登录连接超时自动退出等相关措施。**

老规矩，先看答案。

![1683356112_6455f9d015c70278f930e.png!small?1683356112515](https://image.3001.net/images/20230506/1683356112_6455f9d015c70278f930e.png!small?1683356112515)

![1683356133_6455f9e51dc23c8f45409.png!small?1683356133703](https://image.3001.net/images/20230506/1683356133_6455f9e51dc23c8f45409.png!small?1683356133703)

 **1.登录失败处理措施仅针对SSH远程登录的用户生效，对本地登录用户及其他远程登录方式（本机已开启Telnet远程登录，tcp/50629）无效。**

确认关键资产的对应登录失败处理功能的策略是怎样的。

![1683356853_6455fcb5af32cbbec9ce5.png!small?1683356854033](https://image.3001.net/images/20230506/1683356853_6455fcb5af32cbbec9ce5.png!small?1683356854033)

  

针对ssh的登录失败处理功能，这里我们查看/etc/pam.d/sshd文件。

![1683356362_6455faca9638179b45ec7.png!small?1683356363285](https://image.3001.net/images/20230506/1683356362_6455faca9638179b45ec7.png!small?1683356363285)

确认了针对于ssh登录方式的登录失败处理功能配置是没有问题的。那么接下来坑就来了，他仅仅只有一个ssh的登录方式吗？这里我们先用 netstat
-tuanp 命令查看端口的开放情况。

![1683357095_6455fda77908c576365a9.png!small?1683357096001](https://image.3001.net/images/20230506/1683357095_6455fda77908c576365a9.png!small?1683357096001)

看到上述不知名Program name名称的端口一定要留意了，其中肯定有坑。这里笔者有点菜，不知道xinetd这个telnet服务怎么在centos
7的版本上安装成功的，我直接安装的telnet程序都是systemd（21年能力验证的telnet服务就是这个），centos 7
已经不用xinetd服务来启telnet了，所以这里可能无法复现成功。

![1683357726_6456001ea3d0aaa07f9be.png!small?1683357727074](https://image.3001.net/images/20230506/1683357726_6456001ea3d0aaa07f9be.png!small?1683357727074)

根据网上的资料，我们查看 /etc/services 文件就可以找到telnet服务所对应的端口。

![1683357815_64560077e8c7cebbc6dfa.png!small?1683357816576](https://image.3001.net/images/20230506/1683357815_64560077e8c7cebbc6dfa.png!small?1683357816576)

centos 7 则是修改 /usr/lib/systemd/system/telnet.socket 文件 ListenStream 参数。

![1683359618_6456078254687c92dbaeb.png!small?1683359618534](https://image.3001.net/images/20230506/1683359618_6456078254687c92dbaeb.png!small?1683359618534)

![1683359571_645607532fdc592dbf4ea.png!small?1683359571441](https://image.3001.net/images/20230506/1683359571_645607532fdc592dbf4ea.png!small?1683359571441)

所以啊，登录失败处理功能就没有telnet这个模块就不能给符合。

 **2.虽然在/etc/profile 中设定了 export TMOUT 900，但该项配置未放置在文件末尾处，在该项配置后，/etc/profile
配置了加载/etc/profiled/ 目录下的所有脚本文件，其中/etc/profiled/idletimeout.sh 中配置了export TMOUT
3600，覆盖了/etc/profile 中的TMOUT 设定。通过echo $TMOUT
可知实际生效的空闲超时时间为3600（秒），不符合安全策略要求。**

查看安全策略

![1683360301_64560a2d154e2b46adffd.png!small?1683360301406](https://image.3001.net/images/20230506/1683360301_64560a2d154e2b46adffd.png!small?1683360301406)

这里通常是看 /etc/profile 文件，当时测的时候也是看这个，

![1683360035_645609234a9f5f0325e37.png!small?1683360035523](https://image.3001.net/images/20230506/1683360035_645609234a9f5f0325e37.png!small?1683360035523)

但是最最稳定的方式就是输出他当前环境变量的TMOUT值，采用echo $TMOUT命令，

![1683360150_6456099613837fe5509f7.png!small?1683360150317](https://image.3001.net/images/20230506/1683360150_6456099613837fe5509f7.png!small?1683360150317)

当时就很纠结啊，不知道他在哪里又配置了一个3600，开始我以为在用户家目录下的 .bash_profile
文件中进行了配置，后来发现没有。所以配置的文件可能有很多种，不确定的情况下，直接echo $TMOUT
，答出这个我想应该也是会给分的。由于当时没查过/etc/profiled/idletimeout.sh 这个文件，所以也没法复现当时他是怎么配置的。

###  **c）当进行远程管理时，应采取必要措施防止鉴别信息在网络传输过程中被窃听**

![1683360258_64560a027047f82794ca4.png!small?1683360259001](https://image.3001.net/images/20230506/1683360258_64560a027047f82794ca4.png!small?1683360259001)

这条就很明显了，可以直接查看服务器当天端口开放情况 netstat -tuanp

![1683357095_6455fda77908c576365a9.png!small?1683357096001](https://image.3001.net/images/20230506/1683357095_6455fda77908c576365a9.png!small?1683357096001)

然后去/etc/services文件中确认下是啥服务，上述已经说明了，这里就不重复描述了。

  

