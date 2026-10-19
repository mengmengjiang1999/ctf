## ************vBulletin**** ** **组件**** ** **介绍****

vBulletin是论坛和社区发布软件的全球领导者。其安全性，强大的管理功能和速度，可为40,000多个在线社区提供服务等特点备受客户青睐。很多大型论坛都选择vBulletin作为自己的社区。从vBulletin官方网站所展示的客户列表可以得知，著名的游戏制作公司EA、著名的游戏平台Steam、日本大型跨国企业Sony、以及美国NASA等均为其客户，vBulletin高效，稳定，安全，在中国也有很多大型客户，比如[蜂鸟网](https://baike.baidu.com/item/%E8%9C%82%E9%B8%9F%E7%BD%91)，51团购，海洋部落等在线上万人的论坛都用vBulletin。

## ****漏洞描述****

2020年8月11日，深信服安全团队跟踪到一则vBulletin
5.x版本远程代码执行漏洞的0-day信息，该0-day漏洞是对2019年vBulletin
CVE-2019-16759漏洞补丁的绕过，漏洞定级为高危。此次漏洞影响vBulletin
5.x系列所有版本，且官方尚未修复该漏洞以及给出解决方案，远程攻击者能够通过精心构造的恶意参数，执行任意代码，控制目标服务器或窃取敏感用户信息。

## ****漏洞复现****

通过在vBulletin 5.x版本复现该漏洞，执行echo命令，效果如图：

![](https://image.3001.net/images/20200812/1597202033.png!small)

# ****影响范围****

通过网络空间搜索引擎可以得知，在全球范围内，对互联网开放的vBulletin网站有近3万个，其中较多网站为国际大型企业所维护的国际社区论坛，所以该漏洞影响面较大。

目前受影响的版本为： ** **vBulletin 5.x，即vBulletin 5系列的全版本均受影响**** 。

## ****修复建议****

  1. vBulletin官方尚未修复该漏洞，请受该漏洞影响的用户关注vBulletin官网，获取最新修复补丁：[ _https://www.vbulletin.com/_](https://www.vbulletin.com/)
  2. 临时解决方案：vBulletin所有者可以通过以下步骤对论坛的设置进行以下修改来防止利用：

  * 进入vBulletin管理员控制面板
  * 单击左侧菜单中的“Settings”，然后单击下拉菜单中的“Options”
  * 选择“General Settings”，然后单击“Edit Settings”
  * 查找“Disable PHP, Static HTML, and Ad Module rendering"”，设置为“YES”，然后保存即可。

# ****时间轴****

2020/8/11 深信服安全团队跟踪到一则vBulletin 5.x版本远程代码执行漏洞的0-day信息

2020/8/12 深信服千里目安全实验室复现此漏洞，并发布解决方案。

