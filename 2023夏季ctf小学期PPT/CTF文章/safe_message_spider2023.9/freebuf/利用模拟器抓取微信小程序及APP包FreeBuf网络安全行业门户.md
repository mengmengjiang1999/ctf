本文仅用于记录自身学习过程。

## 条件：

抓取微信小程序数据包的关键点，就是SSL证书绑定的问题。在安卓系统7.0以下的版本，不管微信是什么版本，都会信任系统提供的证书，而现在微信版本已经到了8.0.16
且安装老版本也会强制用户升级，且微信只信任系统及自身内置的证书。

安卓系统7.0以下：微信的任意版本，都会信任用户提供的证书。

安卓系统7.0以上：微信7.0以上版本，微信只信任系统及自身内置的证书

微信7.0以下版本，微信会信任用户提供的证书

## 准备工具：

1、夜神模拟器

2、BurpSuite

3、XPosed

4、justTruseMe

## 环境配置：

安装XPosed框架 ** **(**** Xposed
Framework)是一套开源的、在Android高权限模式下运行的框架服务，可以在不修改APK文件的情况下影响程序运行(修改系统)的框架服务绕过SSL
证书验证。使用这种方法进行抓包的时候要求安卓手机必须需要ROOT。

1.直接在模拟器搜索Xposed进行安装

![1645775226_6218897aa6ba5a4c4e249.png!small?1645775226810](https://image.3001.net/images/20220225/1645775226_6218897aa6ba5a4c4e249.png!small?1645775226810)

2.安装/更新最新版本

![1645775231_6218897f8a1ecf5d1674f.png!small?1645775231682](https://image.3001.net/images/20220225/1645775231_6218897f8a1ecf5d1674f.png!small?1645775231682)

3.添加模块[
_JustTrustMe.apk_](https://github.com/Fuzion24/JustTrustMe/releases/download/v.2/JustTrustMe.apk)

https://github.com/Fuzion24/JustTrustMe/releases/tag/v.2

![1645775238_6218898607526f2170cc0.png!small?1645775238149](https://image.3001.net/images/20220225/1645775238_6218898607526f2170cc0.png!small?1645775238149)

4.此时设置burpsuite证书，设置代理以及代理端口。

![1645775244_6218898c1dc4a02a91312.png!small](https://image.3001.net/images/20220225/1645775244_6218898c1dc4a02a91312.png!small)

5.使用安卓模拟器访问浏览器，http://burp/ 下载证书，改名字，将后缀改为.cer

![1645775253_62188995bbee39a9aa340.png!small?1645775253845](https://image.3001.net/images/20220225/1645775253_62188995bbee39a9aa340.png!small?1645775253845)

6.模拟器安装证书

![1645775261_6218899d43a578b6065c1.png!small](https://image.3001.net/images/20220225/1645775261_6218899d43a578b6065c1.png!small)

7.burpsuite设置监听，最好设置本地ip，至此可以发挥你的技术了。

![1645775270_621889a69d0346ef7927d.png!small?1645775270790](https://image.3001.net/images/20220225/1645775270_621889a69d0346ef7927d.png!small?1645775270790)

  

