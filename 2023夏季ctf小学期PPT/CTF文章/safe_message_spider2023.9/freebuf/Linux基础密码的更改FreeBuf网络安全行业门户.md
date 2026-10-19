## **前言：**

相信大家在学习Linux时都会遇到类似这样

![1642823655_61eb7fe7a521953cda858.png!small](https://image.3001.net/images/20220122/1642823655_61eb7fe7a521953cda858.png!small)

或者这样的尴尬场面

![1642823698_61eb8012790caf4bc9ac8.png!small](https://image.3001.net/images/20220122/1642823698_61eb8012790caf4bc9ac8.png!small)

从Windows刚”跳槽“过来的你显然会显得一脸懵逼，咋办呢？难道用解决Windows的方法来解决Linux？那显然是有点不可取的。

##  **0x1：**

那我们就简单用Redhat来解决一下这种问题吧，首先，虚拟机安装Redhat都会吧？不会的话接着往下看。

###  **0x11：**

前面的步骤相信大家都会所以我们直接到这一步![1642823993_61eb81392574c9829bbb6.png!small](https://image.3001.net/images/20220122/1642823993_61eb81392574c9829bbb6.png!small)

选择稍后安装系统，我们接着往下

![1642824043_61eb816bce48edd905752.png!small](https://image.3001.net/images/20220122/1642824043_61eb816bce48edd905752.png!small)

选择自己的镜像版本，我这里是用的Redhat6，所以我们接着往下

![1642824151_61eb81d7529a484f9a766.png!small](https://image.3001.net/images/20220122/1642824151_61eb81d7529a484f9a766.png!small)

路径自己选，建议不要扔在c盘

后面的步骤一直下一步就可以了

![1642824217_61eb8219d9db1d94c98ca.png!small](https://image.3001.net/images/20220122/1642824217_61eb8219d9db1d94c98ca.png!small)

导入我们的镜像文件，然后开机测试

![1642824275_61eb8253059a9ad75756b.png!small](https://image.3001.net/images/20220122/1642824275_61eb8253059a9ad75756b.png!small)

到这一步说明你前面都没问题昂，接下来，我们往下

选第一个然后下一步

![1642824347_61eb829b4f9a628262f12.png!small](https://image.3001.net/images/20220122/1642824347_61eb829b4f9a628262f12.png!small)

这里我们选第二个就可以了

![1642824403_61eb82d32a553a3464ee6.png!small](https://image.3001.net/images/20220122/1642824403_61eb82d32a553a3464ee6.png!small)

这里我们选是

前面的步骤我们一直下一步，到这里，我们可以简单的配置一下我们的分区

![1642824486_61eb8326351dacbd4da2f.png!small](https://image.3001.net/images/20220122/1642824486_61eb8326351dacbd4da2f.png!small)

选到最后一个

![1642824579_61eb838381fbbabcb3498.png!small](https://image.3001.net/images/20220122/1642824579_61eb838381fbbabcb3498.png!small)

如上进行一个简单的配置，boot咱给200就够用了，再创建一个swap2048就好，最后创建根目录，然后咱继续往下

![1642824694_61eb83f6a5215086f1276.png!small](https://image.3001.net/images/20220122/1642824694_61eb83f6a5215086f1276.png!small)

这里按自己的需求填就是了，也可以选择定制就不做过多的介绍了，我们跳到最后

![1642824929_61eb84e1ecf2fc63bfeef.png!small](https://image.3001.net/images/20220122/1642824929_61eb84e1ecf2fc63bfeef.png!small)

安装完成后，直接重新引导

![1642824990_61eb851e438a9e8db9db5.png!small](https://image.3001.net/images/20220122/1642824990_61eb851e438a9e8db9db5.png!small)

重启后，一直前进就可以了，如果有特殊需求，可做配置；

  

![1642825053_61eb855de793608e157df.png!small](https://image.3001.net/images/20220122/1642825053_61eb855de793608e157df.png!small)

到这，安装就结束了

##  **0x2**

接下来，就是更改密码的步骤了，首先我们重启Linux

![1642825232_61eb86101c5c29e5876c5.png!small](https://image.3001.net/images/20220122/1642825232_61eb86101c5c29e5876c5.png!small)

在这个位置按e

![1642825259_61eb862bb7243b7c1c07c.png!small](https://image.3001.net/images/20220122/1642825259_61eb862bb7243b7c1c07c.png!small)

选中第按e输入空格加s

![1642825327_61eb866f1ca215513cc1d.png!small](https://image.3001.net/images/20220122/1642825327_61eb866f1ca215513cc1d.png!small)

回车后按b引导单用户模式

![1642825493_61eb8715658b6d89928cf.png!small](https://image.3001.net/images/20220122/1642825493_61eb8715658b6d89928cf.png!small)

进入单用户模式后输入passwd就可以重置密码了

![1642825549_61eb874d1f158eaf5e5ef.png!small](https://image.3001.net/images/20220122/1642825549_61eb874d1f158eaf5e5ef.png!small)

最后reboot重启你的密码就更改成功了

![1642825607_61eb8787d0746737ef479.png!small](https://image.3001.net/images/20220122/1642825607_61eb8787d0746737ef479.png!small)

该技术仅供学习，未得允许下请勿用于他人系统！

