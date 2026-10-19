2022年5月25日星期三

主要内容是连接处于内网环境的3389端口

### 单内网（公网IP访问内网IP）

 **利用的原理是内网能主动访问外网** ，需要先getshell然后把内网的33389端口转发到本机。

## 环境搭建

配置win 2003（192.168.43.144、192.168.52.2）、win 2016（192.168.52.200）和kali
Linux（192.168.43.139）三台虚拟机，2003模拟防火墙（路由器），2016模拟内网服务器，kali模拟公网设备。

2003使用两块网卡，一块使用vmnet8模拟连接外网，一块使用vmnet2。

![v2-673bf23f3e3ab64f9fac01baa139063c_b.jpg](https://image.3001.net/images/20220525/1653490801_628e4471ab995bfbaf1fe.jpg!small)

Vmnet8选自自动获取ip（模拟公网），此时2003能访问上网。

![v2-01707583820354ce5d693a195e1355d2_b.jpg](https://image.3001.net/images/20220525/1653490802_628e4472110c3d5dba82d.jpg!small)

Vmnet2IP配置如下（模拟私网），

![v2-4bafc481bff52a24a205fc66ab1a9ba4_b.jpg](https://image.3001.net/images/20220525/1653490802_628e447256a05014b6f1b.jpg!small)

2016使用1块网卡连接vmnet2，配置如下，

![v2-dce64241e43155bce56f4176411db93f_b.jpg](https://image.3001.net/images/20220525/1653490802_628e4472accd7cd0ff617.jpg!small)

网卡配置完成，

在2003上开启nat功能，

需要先停用服务种的Windows firewall 并禁止自启动。

![v2-2cf6118b5c77bd54cc0b5821682a884f_b.jpg](https://image.3001.net/images/20220525/1653490803_628e44730bef735bf2cd3.jpg!small)

点击路由和远程访问，

![v2-e4629837ee0385209170458df41acae0_b.jpg](https://image.3001.net/images/20220525/1653490803_628e4473706018bf8a991.jpg!small)

点击本地的服务器，并点击配置并启用，

![v2-db1b6b0a8a18e4b97afa3a2d825b4619_b.jpg](https://image.3001.net/images/20220525/1653490803_628e4473c178ed5f3868e.jpg!small)

下一步，然选择自定义配置，

![v2-725b55fd7754c2246ed5e6ff7e776bfc_b.jpg](https://image.3001.net/images/20220525/1653490804_628e447429c50f70b3076.jpg!small)

点击nat和基本防火墙，再点击安装，

![v2-a48b6f2e6e9921f902ad31bd8c7d34f3_b.jpg](https://image.3001.net/images/20220525/1653490804_628e44747721d4ec115d2.jpg!small)

选择是，

![v2-5a8b085f6ecc994d93a1ef113ce23cad_b.jpg](https://image.3001.net/images/20220525/1653490804_628e4474b153ec22286ea.jpg!small)

点击nat/基本防火墙，右键点击新增接口，

![v2-5b64e7ee9326f4a91344415580f95ef2_b.jpg](https://image.3001.net/images/20220525/1653490804_628e4474e1dc343bb30a4.jpg!small)

选择本地连接，

![v2-a11da6cf218c951a9de630dd52b1a134_b.jpg](https://image.3001.net/images/20220525/1653490805_628e4475412a667129c37.jpg!small)

选择公共接口，再点击启用NAT，点击确定。

![v2-5ee65d0acc38bc07c9c0bebbda83f8fc_b.jpg](https://image.3001.net/images/20220525/1653490805_628e4475822d8b81d4181.jpg!small)

再新增一个接口，选择本地连接2，

![v2-feba599363f64dc831b85f1f1dd67a10_b.jpg](https://image.3001.net/images/20220525/1653490805_628e4475cdc38fa9afdb6.jpg!small)

选择专用接口到专用网络，点击确定。

![v2-d84157402cab21a59f55d434ed44dcfc_b.jpg](https://image.3001.net/images/20220525/1653490806_628e4476495ce46608a0e.jpg!small)

此时2016就能上网。

![v2-456d08a954856a5a1c8aea4a418394a4_b.jpg](https://image.3001.net/images/20220525/1653490806_628e44769fc5dc35699f7.jpg!small)

此时需要做snat（把内网的web应用映射到公网的一个端口上）。

启动2016里的PHPstudy，

![v2-cbd06f9bc5ec1313f8e29674d3f951ce_b.jpg](https://image.3001.net/images/20220525/1653490806_628e4476ea576d5b4f38e.jpg!small)

回到2003，点击本地连接，点击服务与端口，滑到最下面点击web服务器，

![v2-80166bce441ee760521d4051bab5e139_b.jpg](https://image.3001.net/images/20220525/1653490807_628e44772cb45ce9c4b04.jpg!small)

输入2016的地址，点击确定，点击再点击确定。

![v2-859f4fd506762b20fe0c143febfe332f_b.jpg](https://image.3001.net/images/20220525/1653490807_628e44776de4f0261dce1.jpg!small)

此时在物理机上连接2003的80端口，就能访问到实际的2016的端口。

此时2016能ping通kali，kali不能ping通2016。

![v2-9fa5df1530ffd149cf7668d784b6954d_b.jpg](https://image.3001.net/images/20220525/1653490807_628e4477aa921a2faad3e.jpg!small)

此处需要先getshell，直接访问dvwa的上传目录，利用已有的一句话木马。

![v2-cb7bcea10175b954ffb277d0fea3e4a5_b.jpg](https://image.3001.net/images/20220525/1653490807_628e4477ee7792333388f.jpg!small)

使用蚁剑连接，

![v2-0c48ccaa4b4ab818b6b267b4640e9da7_b.jpg](https://image.3001.net/images/20220525/1653490808_628e4478401dbb325a61f.jpg!small)

开启3389端口，

REG ADD HKLM\SYSTEM\CurrentControlSet\Control\Terminal" "Server /v
fDenyTSConnections /t REG_DWORD /d 00000000 /f

![v2-25be4ec0a8015260c80ac76408f62a1d_b.jpg](https://image.3001.net/images/20220525/1653490808_628e447885fd585768af5.jpg!small)

启用Guest用户，

![v2-3ed88e839da9b0f997bf3f5bec0c5d9f_b.jpg](https://image.3001.net/images/20220525/1653490808_628e4478ba45182d11fc5.jpg!small)

设置一个密码，

![v2-ce4c3ed3bdc6f8638262c71ba51fc12e_b.jpg](https://image.3001.net/images/20220525/1653490808_628e4478ed7827c28581e.jpg!small)

把Guest加入管理员组，

![v2-eaaaae62c766b35c1578c800d7d3d5ca_b.jpg](https://image.3001.net/images/20220525/1653490809_628e44792b510661dc7cc.jpg!small)

上传一个lcx软件，这个软件的功能是把本机的3389端口转发到服务器上，

![v2-f0cf1b168c79c4571d8385fcd2be2b85_b.jpg](https://image.3001.net/images/20220525/1653490809_628e4479679081da277a9.jpg!small)

在kali上使用portmap把来自2333端口的数据转发到2334上，

![v2-930409af3ac935eb44790e88c64d9f0a_b.jpg](https://image.3001.net/images/20220525/1653490809_628e4479999d1830d324c.jpg!small)

然后使用lcx把2016的3389端口转发到kali 的2333端口（因为内网能主动访问外网），

![v2-98fcbce099e7e5eba46072db9acc7fb5_b.jpg](https://image.3001.net/images/20220525/1653490809_628e4479ced289cb273af.jpg!small)

此时kali 的portmap接收到数据，

![v2-13435b9cb40a15aa80a10c7319c4d2a8_b.jpg](https://image.3001.net/images/20220525/1653490810_628e447a11b349d5c295b.jpg!small)

使用remmina，连接本机的端口，因为portmap的流量转发是在本机转发，使用Guest账户。

![v2-076620ea541f5c8977e96d933b942769_b.jpg](https://image.3001.net/images/20220525/1653490810_628e447a42b3b79846eab.jpg!small)

若能连接但是不显示可能是色深的问题，改到8位，还有默认的分辨率太低，需要修改，

![v2-39bac47a99ce2f14297efb5b954f7af9_b.jpg](https://image.3001.net/images/20220525/1653490810_628e447a842da8e0f3346.jpg!small)

成功连接，首次连接时需要等待10-20秒左右。

![v2-854a61cc5f024e0b2b35a580ac150fd8_b.jpg](https://image.3001.net/images/20220525/1653490810_628e447ad24ffc64e8e13.jpg!small)

### 双内网（内网IP访问内网IP）

 **利用http隧道技术** ，因为蚁剑能连接目标内网是因为走的http协议，把目标的3389端口的流量封装到http协议里。

把kali的IP改为10.9.28.45就完全模拟两个内网环境，

使用ew，

Kali上执行ew的Linux版本，把3333端口监听到的流量转发给2222，

![v2-0a59ff330578bdac617813be3e0134ef_b.jpg](https://image.3001.net/images/20220525/1653490811_628e447b2373ddad63bfe.jpg!small)

在蚁剑里把win版本的ew上传进去，

![v2-c50428b9650ca7c6886a68e3226daec1_b.jpg](https://image.3001.net/images/20220525/1653490811_628e447b50e172777a1f5.jpg!small)

在目标上执行，启动服务并弹到代理服务器的3333端口，

![v2-e71f4ad08731f433a8748c9f34a99896_b.jpg](https://image.3001.net/images/20220525/1653490811_628e447b86ae6b4a3c9d1.jpg!small)

进入kali查看，已连接，

![v2-397f4fc690b3fb65e0a02df5c0f8c927_b.jpg](https://image.3001.net/images/20220525/1653490811_628e447baf20cf382ef4a.jpg!small)

进入proxychains4配置文件，

![v2-6f1bf6960f50745da384d2bca3726e63_b.jpg](https://image.3001.net/images/20220525/1653490811_628e447be14bf3c85d3df.jpg!small)![v2-b4439a30b4799dc805f9b91557ed4ee4_b.jpg](https://image.3001.net/images/20220525/1653490812_628e447c355b383b2b2a6.jpg!small)

127.0.0.1也行，

![v2-0e821165d91956ba3c33c91869906dd4_b.jpg](https://image.3001.net/images/20220525/1653490812_628e447c9590328e3b563.jpg!small)

使用这个代理，打开remmina，

![v2-5d53dea9041b86bf7897e85c3a33ea49_b.jpg](https://image.3001.net/images/20220525/1653490812_628e447ce1081d3eb1bea.jpg!small)

依然连接127.0.0.1，色深设置为8位，设置分辨率，连接成功。

![v2-3566e1055cafb5ff645da60b310cf76f_b.jpg](https://image.3001.net/images/20220525/1653490813_628e447d253b939ad9bde.jpg!small)

成功连接。

