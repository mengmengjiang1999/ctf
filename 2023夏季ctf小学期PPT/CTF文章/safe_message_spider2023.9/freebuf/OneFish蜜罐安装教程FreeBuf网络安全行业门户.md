安装第一步，首先需要安装数据库，对于新手，宝塔面板是最好的选择

地址：[
_https://www.bt.cn/bbs/thread-19376-1-1.html_](https://www.bt.cn/bbs/thread-19376-1-1.html)下载对应版本

![1614235726_6037484ed8ea8c8eff098.png!small](https://image.3001.net/images/20210225/1614235726_6037484ed8ea8c8eff098.png!small)

第二步下载onefish文件，地址：[ _https://hfish.io/download.html_
下载对应版本](https://hfish.io/download.html%E4%B8%8B%E8%BD%BD%E5%AF%B9%E5%BA%94%E7%89%88%E6%9C%AC)

![1614235737_60374859c01d499ffafec.png!small](https://image.3001.net/images/20210225/1614235737_60374859c01d499ffafec.png!small)

我用的都是是linux64位的

![1614235744_60374860ebe93599a77e1.png!small](https://image.3001.net/images/20210225/1614235744_60374860ebe93599a77e1.png!small)

宝塔页面安装完是这样的页面

![1614235749_60374865a93f4feed6c8c.png!small](https://image.3001.net/images/20210225/1614235749_60374865a93f4feed6c8c.png!small)

![1614235754_6037486aa72944d290414.png!small](https://image.3001.net/images/20210225/1614235754_6037486aa72944d290414.png!small)

输入用户名密码，进入页面

![1614235762_603748726e51f6bacedee.png!small](https://image.3001.net/images/20210225/1614235762_603748726e51f6bacedee.png!small)

登录进去会让你绑定你自己的宝塔账号，没有账号还得注册，比较麻烦，根据大佬指示，在地址栏输入/site就可以绕过。

![1614235769_60374879577753dc8b052.png!small](https://image.3001.net/images/20210225/1614235769_60374879577753dc8b052.png!small)

下一步，去软件商店安装数据库

![1614235776_60374880edf9aaa748a96.png!small](https://image.3001.net/images/20210225/1614235776_60374880edf9aaa748a96.png!small)

具体哪个版本看自己需求，我安装的是mysql5.5

![1614235782_60374886331a27dc4f7b0.png!small](https://image.3001.net/images/20210225/1614235782_60374886331a27dc4f7b0.png!small)

![1614235789_6037488d4120ce366ccfc.png!small](https://image.3001.net/images/20210225/1614235789_6037488d4120ce366ccfc.png!small)

安装完修改一下数据库密码，建议改成OneFish210，这样的话不用改config了，可以直接用

下载完源文件，解压（步骤省略）

Cd /ongfish目录

导入数据库文件，需要输入数据库密码OneFish210

![1614235807_6037489f5659459533d74.png!small](https://image.3001.net/images/20210225/1614235807_6037489f5659459533d74.png!small)

![1614235812_603748a4428a765f5441b.png!small](https://image.3001.net/images/20210225/1614235812_603748a4428a765f5441b.png!small)

就可以看到onefish数据库内容了，喜欢图形化管理的自行下载。我个人比较喜欢代码方式管理。

![1614235839_603748bf703bf6846cdb7.png!small](https://image.3001.net/images/20210225/1614235839_603748bf703bf6846cdb7.png!small)

给server一个可执行权限。

![1614235848_603748c81ec09f292cc87.png!small](https://image.3001.net/images/20210225/1614235848_603748c81ec09f292cc87.png!small)

执行server

查看是否运行成功

![1614235852_603748cc7d47bb2bda190.png!small](https://image.3001.net/images/20210225/1614235852_603748cc7d47bb2bda190.png!small)

或出现这样别急，能控制

![1614235861_603748d546c68336d10b0.png!small](https://image.3001.net/images/20210225/1614235861_603748d546c68336d10b0.png!small)

进入宝塔页面，添加放行端口443，就可以解决

![1614235866_603748dac8f39c46a4fe5.png!small](https://image.3001.net/images/20210225/1614235866_603748dac8f39c46a4fe5.png!small)

登录页面默用户名密码admin / OneFish2021

![1614235877_603748e548c4a4ae0bf14.png!small](https://image.3001.net/images/20210225/1614235877_603748e548c4a4ae0bf14.png!small)

添加钓鱼页面以及端口

![1614235901_603748fd9d2f7929b98f9.png!small](https://image.3001.net/images/20210225/1614235901_603748fd9d2f7929b98f9.png!small)

社区办可以选择5个服务

![1614235911_603749075a1f8a7bce022.png!small](https://image.3001.net/images/20210225/1614235911_603749075a1f8a7bce022.png!small)

![1614235920_6037491004efa4939b49d.png!small](https://image.3001.net/images/20210225/1614235920_6037491004efa4939b49d.png!small)

想要添加结点

![1614235926_603749167f61490135b1e.png!small](https://image.3001.net/images/20210225/1614235926_603749167f61490135b1e.png!small)

![1614235932_6037491ca220696224d3e.png!small](https://image.3001.net/images/20210225/1614235932_6037491ca220696224d3e.png!small)

![1614235941_603749252837f08e89d9d.png!small](https://image.3001.net/images/20210225/1614235941_603749252837f08e89d9d.png!small)

在你想部署的那台主机运行这条命令就行了，我没有多余的电脑，我用的是本机

![1614235947_6037492b64ee8560c5885.png!small](https://image.3001.net/images/20210225/1614235947_6037492b64ee8560c5885.png!small)

![1614235950_6037492e5f18b56174c91.png!small](https://image.3001.net/images/20210225/1614235950_6037492e5f18b56174c91.png!small)

结点已经出来了

![1614235959_60374937154d12ac70ea9.png!small](https://image.3001.net/images/20210225/1614235959_60374937154d12ac70ea9.png!small)

记得去宝塔里放行端口。

![1614235961_60374939da085af93dad9.png!small](https://image.3001.net/images/20210225/1614235961_60374939da085af93dad9.png!small)

![1614235969_60374941243881d5e452d.png!small](https://image.3001.net/images/20210225/1614235969_60374941243881d5e452d.png!small)

Onefish基本就已经安装好了

想关闭已经运行的结点

ps aux|grep client

![1614235974_60374946992828ab2870b.png!small](https://image.3001.net/images/20210225/1614235974_60374946992828ab2870b.png!small)

如果还有哪不懂，可以评论加私信的方式我看到会第一时间回复你

免责声明：本人坚决反对利用教学方法进行犯罪的行为，一切犯罪行为必将受到严惩，绿色网络需要我们共同维护，更推荐大家了解它们背后的原理，更好地进行防护。禁止任何人转载到其他站点，禁止用于任何非法用途。如有任何人凭此做何非法事情，均于笔者无关，特此声明。

