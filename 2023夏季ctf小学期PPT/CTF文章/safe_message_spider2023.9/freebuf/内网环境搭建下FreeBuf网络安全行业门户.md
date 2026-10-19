## 一、前言

在上篇文章中，我们已经搭建好了父域控制器以及辅域控制器，并添加了一些域用户以及域机器，在本篇文章中将继续介绍子域控制器的搭建以及两个林间该怎么建立林信任关系。

## 二、子域控制器搭建

1、右键虚拟机点击设置，将网络适配器模式修改为与父域控制相同的模式。

![image.png](https://image.3001.net/images/20211230/1640833734_61cd22c622895fc172868.png!small)

2、设置子域控IP地址，将DNS指向主域控IP地址，然后委派完DNS再把子域控制器DNS指向自己：

    
    
    IP：10.10.10.11
    子网掩码：255.255.255.0
    默认网关：10.10.10.1
    首选DNS：10.10.10.8（这个需要和域控IP地址一致）
    

![image.png](https://image.3001.net/images/20211230/1640833743_61cd22cf79669d090825c.png!small)

3、设置计算机名，然后重启即可

![image.png](https://image.3001.net/images/20211230/1640833749_61cd22d5b1820a76cc0f1.png!small)

4、再次打开开始菜单来到"服务器管理器"->"添加角色和功能"，和之前创建域控的操作是⼀样的，安装完成后选择"将此服务器提升为域控制器。

![image.png](https://image.3001.net/images/20211230/1640833756_61cd22dc3382ec40cbb3d.png!small)

5、AD域服务配置向导

在部署配置时需要做如下配置：

    
    
    选择部署操作：将新域添加到现有林
    选择域类型：子域
    ⽗域名：c1ay.lab
    ⼦域名：DC2.c1ay.lab
    凭据：填写父域的账号密码即可
    

![image.png](https://image.3001.net/images/20211230/1640833762_61cd22e29a0ce3898e2a9.png!small)

来到域控制器选项，填写新的DSRM密码：admin!@#45。

![image.png](https://image.3001.net/images/20211230/1640833770_61cd22ea54eab11012b39.png!small)

在dns选项后依次点击下一步，设置保持默认，安装完成后系统会自动重启。

![image.png](https://image.3001.net/images/20211230/1640833780_61cd22f405ac063400572.png!small)

6、使用子域域管登录后，修改DNS：

    
    
    ⾸选DNS选择子域IP : 10.10.10.11
    备用DNS选择父域IP : 10.10.10.8
    

![image.png](https://image.3001.net/images/20211230/1640833793_61cd23015bc03ec052d65.png!small)

这个时候子域控制器就彻底安装成功了。

## 三、信任域控制器搭建

1、设置静态IP地址，DNS为自己的IP

    
    
    IP：10.10.10.20
    子网掩码：255.255.255.0
    默认网关：10.10.10.1
    首选DNS：10.10.10.20（这个需要和域控IP地址一致）
    

![image.png](https://image.3001.net/images/20211230/1640833801_61cd230995a13eee6ae54.png!small)

2、修改计算机名

![image.png](https://image.3001.net/images/20211230/1640833807_61cd230f6f3bb24e8692c.png!small)

3、点击开始，在搜索程序和文件中输入如下命令，在Windows 2008 服务器上安装域控。

    
    
    dcpromo
    

![image.png](https://image.3001.net/images/20211230/1640833812_61cd23145a5fc15cf90a1.png!small)

2、点击下一步，选择在新林中新建域。

![image.png](https://image.3001.net/images/20211230/1640833818_61cd231ae16cf7a2922f5.png!small)

3、继续点击下一步，输入目录林根级域。

![image.png](https://image.3001.net/images/20211230/1640833823_61cd231fc7de49690acbb.png!small)

4、点击下一步，选择林功能级别（F）为Windows Server 2008 R2。

![image.png](https://image.3001.net/images/20211230/1640833829_61cd2325e5a5decdb178a.png!small)

5、点击下一步，在其他域控制选项勾选DNS 服务器 和 全局编录。

![image.png](https://image.3001.net/images/20211230/1640833835_61cd232bd0166626bf3cc.png!small)

6、点击下一步，忽视弹出的警告，点击确认。

![image.png](https://image.3001.net/images/20211230/1640833839_61cd232fe6a1b2fd873c5.png!small)

7、点击下一步，设置数据库文件夹、日志文件文件夹、SYSOL文件夹存放路径。

![image.png](https://image.3001.net/images/20211230/1640833847_61cd2337a9d89fa12eed5.png!small)

8、点击下一步，设置目录服务还原模式的Administrator密码：admin!@#45。

![image.png](https://image.3001.net/images/20211230/1640833852_61cd233c967791744c89b.png!small)

9、依次点击下一步进行安装即可。

![image.png](https://image.3001.net/images/20211230/1640833857_61cd234155f75f0cfe47b.png!small)

![image.png](https://image.3001.net/images/20211230/1640833862_61cd2346235613437f575.png!small)

10、自动重启后，使用域管账号登录。

![image.png](https://image.3001.net/images/20211230/1640833868_61cd234cc601760be26a1.png!small)

至此，信任域控制器搭建完成。

## 四、建立DNS辅助区域

1、登录到信任域控制器（c1ayfbi.com），依次点击服务管理器->角色->DNS->DC->正向查看区域->c1ayfi.com，右键打开属性，点击允许区域传送，设置模式为只允许到下列服务器，添加上父域控制器的IP，点击应用。

![image.png](https://image.3001.net/images/20211230/1640833874_61cd23528d434d1e0cd35.png!small)

在_msdcs.c1ayfbi.com也做相同的配置。

![image.png](https://image.3001.net/images/20211230/1640833885_61cd235de9540e087b098.png!small)

2、登录到父域控制器上，因为之前我们已经设置了允许DNS区域传送到任意服务器中，因此无需再做配置。

![image.png](https://image.3001.net/images/20211230/1640833890_61cd2362cef550426feec.png!small)

3、在父域控制器上建立辅助区域，主DNS服务器为信任域控制器，

打开父域控制器DNS管理器，在正向查找区域中新建区域。

![image.png](https://image.3001.net/images/20211230/1640833899_61cd236b769be71a55ddb.png!small)点击下一步，将区域类型设置为辅助区域。

![image.png](https://image.3001.net/images/20211230/1640833908_61cd23744eb8c113462c8.png!small)

设置区域名称为信任域控制器的根域名。

![image.png](https://image.3001.net/images/20211230/1640833914_61cd237a7f1034fa2a4bd.png!small)

添加主服务器的地址为信任域控制器的IP地址。

![image.png](https://image.3001.net/images/20211230/1640833919_61cd237fa59f11a133413.png!small)

点击下一步，再点击完成即可。

![image.png](https://image.3001.net/images/20211230/1640833924_61cd2384e3247015df09d.png!small)

4、在信任域控制器上建立辅助区域，主DNS服务器为父域控制器，

打开信任域控制器的DNS管理器，在正向查找区域中新建区域。

![image.png](https://image.3001.net/images/20211230/1640833930_61cd238a70ecd9a7ce2ee.png!small)

在区域类型中选择辅助区域，点击下一步。

![image.png](https://image.3001.net/images/20211230/1640833935_61cd238f0dc3487de9076.png!small)

设置区域名称为父域控制器的根域名。

![image.png](https://image.3001.net/images/20211230/1640833939_61cd2393e4e976f8879c5.png!small)

设置主服务器的地址。

![image.png](https://image.3001.net/images/20211230/1640833943_61cd23979501609207aed.png!small)

点击下一步，点击完成即可。

![image.png](https://image.3001.net/images/20211230/1640833948_61cd239c6fdd7b11e6c5a.png!small)

5、等待一会就可以看到dns已经相互同步。

![image.png](https://image.3001.net/images/20211230/1640833953_61cd23a107fe120f43413.png!small)

![image.png](https://image.3001.net/images/20211230/1640833956_61cd23a481dd99e9ce108.png!small)

## 五、建立林信任

1、登录信任域控制器，打开active directory域和信任关系，打开域的属性。

![image.png](https://image.3001.net/images/20211230/1640833962_61cd23aa0c3237f5583cd.png!small)

2、在信任选项中新建信任，点击下一步，

![image.png](https://image.3001.net/images/20211230/1640833967_61cd23af17563aeff93de.png!small)

3、输入父域控制器的netbios名称，点击下一步，

![image.png](https://image.3001.net/images/20211230/1640833971_61cd23b3c988c6dc00cce.png!small)

4、选择林信任，点击下一步，

![image.png](https://image.3001.net/images/20211230/1640833975_61cd23b7b23903cfe76ad.png!small)

5、选择信任方向为双向，

![image.png](https://image.3001.net/images/20211230/1640833981_61cd23bd3eb5824d9f971.png!small)

6、选择信任方为次域和指定的域，点击下一步!![image.png](https://image.3001.net/images/20211230/1640833986_61cd23c25aad7c83bf7ab.png!small)

7、输入父域控制器的用户名和密码，点击下一步。

![image.png](https://image.3001.net/images/20211230/1640833990_61cd23c65d9d4c8cb9271.png!small)

8、传出信任，选择全林性身份验证，点击下一步。

![image.png](https://image.3001.net/images/20211230/1640833995_61cd23cb3c73b82035984.png!small)

9、传入信任，选择全林性身份验证，点击下一步。

![image.png](https://image.3001.net/images/20211230/1640833999_61cd23cf5db0e761cfd09.png!small)

10、选择确认传出信任，点击下一步。

![image.png](https://image.3001.net/images/20211230/1640834004_61cd23d4aac4d1b8f2193.png!small)

11、选择确认传入信任，点击下一步。

![image.png](https://image.3001.net/images/20211230/1640834012_61cd23dc1e5d794ce3eda.png!small)

12、完成信任建立后，在信任域控制器端可以看到已经建立好的林的信任。

![image.png](https://image.3001.net/images/20211230/1640834016_61cd23e08e1c6c12174f3.png!small)

13、在父域控制器端也可以看到信任成功建立。

![image.png](https://image.3001.net/images/20211230/1640834020_61cd23e4e5453d0d49a70.png!small)

## 六、子域添加域机器和用户

### 6.1 添加域用户

1、查看当前域内的用户

    
    
    net user /domain
    

![image.png](https://image.3001.net/images/20211230/1640834029_61cd23edd9834525b6094.png!small)

2、打开Active Directory 用户和计算机，在Users中新建域用户，

输入域用户名后，点击下一步。

![image.png](https://image.3001.net/images/20211230/1640834035_61cd23f36283390747ab3.png!small)

设置密码及密码更改策略，点击下一步，再点击完成即可。

![image.png](https://image.3001.net/images/20211230/1640834039_61cd23f7ac2637f5d25c6.png!small)

通过命令可以看到成功创建名为lisi的域用户。

![image.png](https://image.3001.net/images/20211230/1640834044_61cd23fce62b3a0997595.png!small)

以相同的方式继续创建wangwu，wdc用户。

![image.png](https://image.3001.net/images/20211230/1640834049_61cd2401b95256e58612d.png!small)

### 6.2 添加域机器

（1）将Windows 7 系统添加到域内

1、设置静态IP地址，将DNS指向子域控IP

    
    
    IP：10.10.10.33
    子网掩码：255.255.255.0
    默认网关：10.10.10.1
    DNS：10.10.10.11（这个需要和子域控IP地址一致）
    

![image.png](https://image.3001.net/images/20211230/1640834055_61cd2407cdca1379143ec.png!small)

2、设置计算机名，讲机器添加到子域内

![image.png](https://image.3001.net/images/20211230/1640834059_61cd240ba00305786ec05.png!small)

3、使用域用户wdc的凭证加入子域中

![image.png](https://image.3001.net/images/20211230/1640834063_61cd240f7f83f06194ae5.png!small)

4、在子域控上可以看到计算机成功加入到了组内

![image.png](https://image.3001.net/images/20211230/1640834067_61cd24137aaa682afbbd8.png!small)

## 七、边界服务器搭建

1、右键虚拟机点击设置，添加两张网卡，一张为桥接模式，一张为自定义仅主机模式，子网为10.10.20.0/24。

![image.png](https://image.3001.net/images/20211230/1640834071_61cd2417891336de4f24a.png!small)

2、以本地管理员身份登陆该机器，设置网络适配器

将桥接网卡设置为dhcp动态获取IP地址

![image.png](https://image.3001.net/images/20211230/1640834075_61cd241bb98130ad50016.png!small)

将自定义仅主机模式网卡设置为静态地址

![image.png](https://image.3001.net/images/20211230/1640834082_61cd24222c3098d5c1b37.png!small)

3、给子域内的win7主机添加一个自定义仅主机18的网卡，并设置一个静态IP地址

![image.png](https://image.3001.net/images/20211230/1640834099_61cd24335484bdaf84bf7.png!small)

4、确保边界服务器能够和子域内的win7主机能够相互通信。

![image.png](https://image.3001.net/images/20211230/1640834105_61cd2439da0ee21159b27.png!small)

![image.png](https://image.3001.net/images/20211230/1640834109_61cd243de9d76878db2f8.png!small)

至此内网环境搭建完成。

## 八、后语

在下篇文章中将继续为大家带来内网信息收集的相关思路及方法，敬请期待！

