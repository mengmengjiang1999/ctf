***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 漏洞/事件概要

**北京时间4月18日凌晨，Oracle官方发布了4月份的关键补丁更新CPU（CriticalPatchUpdate）,其中包含一个高危的Weblogic反序列化漏洞(CVE-2018-2628)，通过该漏洞，攻击者可以在未授权的情况下远程执行代码。攻击者只需要发送精心构造的T3协议数据，就可以获取目标服务器的权限。攻击者可利用该漏洞控制组件，影响数据的可用性、保密性和完整性。**

## 风险等级

严重

## 影响范围

> OracleWebLogicServer10.3.6.0
>
> OracleWebLogicServer12.1.3.0
>
> OracleWebLogicServer12.2.1.2
>
> OracleWebLogicServer12.2.1.3

## 处置建议

升级Oracle201804月补丁

## 参考

> <http://www.oracle.com/technetwork/security-> advisory/cpuapr2018-3678067.html>
>
> <http://toutiao.secjia.com/cve-2018-2628>

