## **前言**

Linux的几个常见的安装方式相比大家都比较清楚，基于rpm的rpm-i 包名，基于deb的drpg-i
xxx.deb等。其中个人觉得最好用的还是yum，其安装的一大特点便是解决依赖关系，平时安装软件的时候，相信大家都会遇到，类似安装a文件时需要b文件的依赖，而这个时候yum就能表现出它的优秀一面，接下来就是安装yum的一个简单步骤。

###  **0x01：**

首先我们先挂载一下本地的盘。

![1642989900_61ee094cc051a87e219b6.png!small](https://image.3001.net/images/20220124/1642989900_61ee094cc051a87e219b6.png!small)

![1642989923_61ee09637bdf89debcb7f.png!small](https://image.3001.net/images/20220124/1642989923_61ee09637bdf89debcb7f.png!small)

![1642989961_61ee09895062f6898f357.png!small](https://image.3001.net/images/20220124/1642989961_61ee09895062f6898f357.png!small)

这个时候我们可以看到我们的iso镜像已经挂载上了。

###  **0x02：**

我们把iso镜像重新挂载到media（mount /dev/sr0 /media）。

![1642990594_61ee0c02c30389bd96db1.png!small](https://image.3001.net/images/20220124/1642990594_61ee0c02c30389bd96db1.png!small)

可以看到已经挂载到media下了。

###  **0x03：**

接下来就是对我们yum的一个文件配置（vi /etc/yum.repos.d/rhel -source.repo）

![1642990968_61ee0d78091104959daf7.png!small](https://image.3001.net/images/20220124/1642990968_61ee0d78091104959daf7.png!small)

把光标下面的都删掉。

![1642991255_61ee0e9773fdb2dc9c051.png!small](https://image.3001.net/images/20220124/1642991255_61ee0e9773fdb2dc9c051.png!small)

把0改成1启用将原来的ftp地址改为你的server地址（file:///media/Server）

最后记得复制下最后一串密钥。![1642991393_61ee0f21c00517e0c2bbd.png!small](https://image.3001.net/images/20220124/1642991393_61ee0f21c00517e0c2bbd.png!small)

![1642991603_61ee0ff3865ec04920fd7.png!small](https://image.3001.net/images/20220124/1642991603_61ee0ff3865ec04920fd7.png!small)

安装密钥后就可以用yum安装了。

![1642991690_61ee104a46bb35d1679c6.png!small](https://image.3001.net/images/20220124/1642991690_61ee104a46bb35d1679c6.png!small)

如果yum不能安装可以尝试着清理一下yum缓存（yum clean all）。

###  **0x10:**

接下来就是LAMP的安装了。

首先我们先安装php php-mysql mysql MySQL-server。

![1642991850_61ee10ea14e3b71bbc918.png!small](https://image.3001.net/images/20220124/1642991850_61ee10ea14e3b71bbc918.png!small)

###  **0x11：**

安装完成后我们来启动一下apache和mysql（service httpd start service mysqld start）。

![1642991985_61ee11712fe1ab978b684.png!small](https://image.3001.net/images/20220124/1642991985_61ee11712fe1ab978b684.png!small)

启动完成后我们配置一下mysql账户密码。

mysqladmin -uroot password 123456

![1642992137_61ee1209832e487596771.png!small](https://image.3001.net/images/20220124/1642992137_61ee1209832e487596771.png!small)

登陆mysql可以看到我们的sql已经创建ok。

###  **0x12：**

接下来我们去找到它的配置文件 （vi /etc/httpd/conf/httpd.conf）。

![1642992682_61ee142ac5a160d2d6343.png!small](https://image.3001.net/images/20220124/1642992682_61ee142ac5a160d2d6343.png!small)

这个位置我们可以看到它的文件目录。

![1642992973_61ee154dbf398e828c786.png!small](https://image.3001.net/images/20220124/1642992973_61ee154dbf398e828c786.png!small)

我们可以写个文件来测试一下。

![1642993010_61ee157203d9f03e72940.png!small](https://image.3001.net/images/20220124/1642993010_61ee157203d9f03e72940.png!small)

可以看到已经成功了，如果需要写同ip不同端口的话需要关闭防火墙。

最后如果大家有什么疑问的话可以在评论区留言。

