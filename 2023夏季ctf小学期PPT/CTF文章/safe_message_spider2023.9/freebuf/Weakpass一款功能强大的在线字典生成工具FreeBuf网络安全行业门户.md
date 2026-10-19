![](https://image.3001.net/images/20211008/1633681003_615ffe6b87511bff8ba13.jpg!small)

## 关于Weakpass

Weakpass是一款基于规则的在线字典生成器，可以帮助广大研究人员根据输入的单词集来创建自定义字典。

在渗透测试的过程中，我们可能需要访问某些受密码保护的服务、设备、帐户或Wi-Fi网络。而此时，有的密码是设备/网络/组织名称与某些日期、特殊字符等的组合。因此，在启动更复杂和耗时的检查之前，如果能够测试某些字典密码组合的话，就可以帮助我们节省更多的时间。比如说，使用单词列表破解Wi-Fi密码可能需要几个小时，并且可能会失败，即使您选择了一个很好的单词列表。

因此，使用Weakpass生成的字典列表，可以组织有针对性且有效在线密码检查。

## 功能介绍

Weakpass使用了hashcat规则语法来生成字典列表。默认情况下，生成器使用一组规则“online.rule”来执行以下操作：

> 在生成的字典单词结尾添加特殊字符和指定的结束字符，比如说- !,!@, !@#, 123! etc. evilcorp!, evilcorp!123等；
>
> 添加1-31的数字，或01-12，比如说evilcorp01, evilcorp12；
>
> 添加2018-2023日期，例如evilcorp2018, evilcorp2019；
>
> 各种1-3的组合，例如evilcorp2018!；
>
> 首字母大写，其余字母小写，例如Evilcorp!2021；

我们以单词evilcorp为例，则Weakpass可以生成下列密码（总共216个）：

    
    
    evilcorp
    
    Evilcorp
    
    EVILCORP
    
    evilcorp123456
    
    evilcorp2018
    
    Evilcorp!2021
    
    Evilcorp!2022
    
    Evilcorp2018!@#

当然了，我们也可以使用自己的hashcat规则，我们可以点击“显示规则”，并在“规则”文本框内输入规则列表。

工具将会自动过滤掉重复的密码，针对Wi-Fi密码，工具将会自动把长度小于8个字符的密码删除掉。所有数据都是使用Javascript生成的，因此你可以在不访问internet的情况下使用生成器。

## 工具使用

> 如需生成一个字典文件，则需要进入“单词”字段，输入基础密码。
>
> 点击“生成”按钮。
>
> 将接收到的内容拷贝下来，并用于其他地方。

## 工具使用地址

 **Weakpass：** 【[ _官方网站_](https://github.com/zzzteph/weakpass)】

## 工具使用截图

![](https://image.3001.net/images/20211008/1633681037_615ffe8d14080678c7139.png!small)

## 工具使用演示

![](https://image.3001.net/images/20211008/1633681043_615ffe93d75ef15831e62.gif)

## 项目地址

 **Weakpass：** 【[ _GitHub传送门_](https://github.com/zzzteph/weakpass)】

## 参考资料

> [
> _https://zzzteph.github.io/weakpass/_](https://zzzteph.github.io/weakpass/)
>
> [ _https://weakpass.com/generate_](https://weakpass.com/generate)
>
> [
> _https://hashcat.net/wiki/doku.php?id=rule_based_attack_](https://hashcat.net/wiki/doku.php?id=rule_based_attack)

