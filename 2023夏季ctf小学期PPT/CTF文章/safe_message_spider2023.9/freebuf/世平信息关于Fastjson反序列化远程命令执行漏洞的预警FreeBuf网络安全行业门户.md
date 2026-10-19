声明：本文关于详细升级方法部分引用至 GitHub

查看原文链接：http://suo.im/4DzZ0M

背景介绍

Fastjson 是一个 Java 语言编写的高性能功能完善的 JSON 库。采用独创的算 法，将 parse 的速度提升到极致，超过所有 json
库，包括曾经号称最快的 jackson。并且还超越了 google 的二进制协议 protocol buf。

1.1 漏洞描述

Fastjson 存在反序列化远程代码执行漏洞，当应用或系统使用 Fastjson 对由用户可控的 JSON
字符串数据进行解析时，将可能导致远程代码执行的危害。此漏洞为老漏洞新的绕过方式，利用方式还是JNDI，且无需依赖 autotype 的开
启，这意味着默认配置下的 Fastjson 即会受到漏洞影响。

1.2 漏洞编号

无

1.3 漏洞等级

高危

修复建议

2.1 受影响版本

fastjson < 1.2.51

2.2 临时解决方案

升级到 1.2.51 以上，并推荐关闭 Autotype

详细升级方法如下：

FASTJSON升级常见问题解答

在2018年2月5日和2018年10月1日，FASTJSON分别发布了1.2.46和1.2.51版本做了安全更新。

2018年2月5日发布FASTJSON 1.2.46

https://github.com/alibaba/fastjson/releases/tag/1.2.46

2018年10月1日发布FASTJSON 1.2.51

https://github.com/alibaba/fastjson/releases/tag/1.2.51

在2018年10月1日发布的1.2.51版本中，修复了所有已知安全漏洞。在1.2.51之后陆续修复了一些兼容性问题和bug，最新版本是1.2.58

https://github.com/alibaba/fastjson/releases/tag/1.2.58

为了方便大家升级，提供了兼容的补丁版本sec04。最近咨询升级兼容的同学较多，将更新常见问题整理如下：

更新方法

1\. Maven依赖配置更新

通过maven配置更新，使用最新版本，如下：

<!-- 1.2.51包括所有的安全更新 --><dependency>

<groupId>com.alibaba</groupId>

<artifactId>fastjson</artifactId>

<version>1.2.51</version>

</dependency><!-- 1.2.58是最新的版本 --><dependency>

<groupId>com.alibaba</groupId>

<artifactId>fastjson</artifactId>

<version>1.2.58</version>

</dependency>

2\. 直接下载

1.2.51版本下载地址：

http://repo1.maven.org/maven2/com/alibaba/fastjson/1.2.51/

1.2.58版本下载地址：

http://repo1.maven.org/maven2/com/alibaba/fastjson/1.2.58/

常见问题

1\. 升级遇到不兼容问题怎么办？

1.2.58已经修复了绝大多数兼容问题，但是总会有一些特殊的用法导致不兼容，如果你遇到不兼容问题，通过

https://github.com/alibaba/fastjson/wiki/incompatible_change_list

查看不兼容问题，链接的后面提供了遇到不兼容问题之后的使用相应的sec04版本解决办法。所有的sec04版本都可以在maven中央仓库中下载。

Maven中央仓库

http://repo.maven.apache.org/maven2/com/alibaba/fastjson/

2\. 所有的sec01版本是否需要升级

所有的sec01版本都是为了兼容的安全补丁版本，需要升级到sec04版本。sec04版本修复了所有已知安全漏洞。

3\. 升级之后报错autotype is not support

安全升级包禁用了部分autotype的功能，也就是"@type"这种指定类型的功能会被限制在一定范围内使用。如果你使用场景中包括了这个功能，https://github.com/alibaba/fastjson/wiki/enable_autotype这里有一个介绍如何添加白名单或者打开autotype功能。

4\. 通过配置打开autotype之后是否存在安全漏洞

在1.2.51以及所有的.sec04版本中，有多重保护，但打开autotype之后仍会存在风险，不建议打开，而是使用一个较小范围的白名单。打开autoType建议升级到最新版本1.2.51以上

5\. Android环境使用是否需要升级

目前未发现漏洞对Android系统产生影响，在Android环境中使用不用升级。但Android升级到最新版1.1.71.android版本能提升性能。

6\. 升级遇到问题希望提供支持怎么办？

作者愿意帮助大家一起解决问题，如果遇到文档中没说明到的问题，请通过如下方式联系作者：

钉钉号 wenshaojin2017

微信号 wenshaojin

微博 http://weibo.com/wengaotie

  

