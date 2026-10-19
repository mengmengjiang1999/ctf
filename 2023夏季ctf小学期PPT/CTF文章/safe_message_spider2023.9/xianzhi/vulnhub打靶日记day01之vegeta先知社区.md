# 一、靶机配置

靶机地址：<https://www.vulnhub.com/entry/vegeta-1,501/>

我攻击机网络模式是nat模式，所以靶机也设置为nat模式

有可能存在扫不到靶机ip情况，需要做些设置：

1、靶机开启后进入这个界面按下e键

![](./img/3755198964937367024.png)

2、将ro 改成 `rw signie init=/bin/bash`

![](./img/4781546471449245367.png)

![](./img/5890646655667511975.png)

3、设置成功后按下ctrl键+x键，进入bash界面

![](./img/8306540637988818750.png)

4、一般这种情况都是网卡没配好的原因，首先查看下系统内核属于debian，命令`cat /etc/*-release`，或者`uname -a`也可以

![](./img/4579862003232915932.png)

5、`ip a` 查看网卡信息，debian中`/etc/network/interfaces`文件是网卡配置信息，对比发现网卡名字不同

![](./img/4237991159543105627.png)

![](./img/6121918741095814196.png)

6、将enp0s3那两条配置信息改成

`auto ens33`

`iface ens33 inet dhcp`

将ipv6那个注释掉

![](./img/1340230933541441101.png)

7、重启网络，`/etc/init.d/networking restart`，然后ip就正常了

![](./img/8759816469480308294.png)

# 二、信息收集

1、`nmap -sn 10.10.10.0/24` 扫描下攻击机同网段ip，发现目标ip为10.10.10.130

![](./img/4624370819841949589.png)

2、nmap -Pn -A -p- 10.10.10.130 扫下ip，发现开启22和80端口

![](./img/1812436909924509721.png)

3、22端口没有发现可利用点。访问80端口，只有一张贝吉塔图片

![](./img/7741735669360606553.png)

4、目录扫描一波，我用的是webpathscan工具（<https://github.com/Matrix-Cain/WebPathScanner.git>），`pathmap.exe scan url http://10.10.10.130`

![](./img/3107499464477703811.png)

5、所有目录都访问了一遍在robots.txt文件中发现另一个隐藏目录,`http://10.10.10.130/find_me`,访问

![](./img/1632021929612323840.png)

6、看网页没发现什么，看了下源码发现一串疑似base64加密的字符串

![](./img/2932348858772184710.png)

7、将这串字符串解密后还是一串加密字符串，进行二次解码，发现这是图片隐写

![](./img/2022362126121105577.png)

8、写了一个图片解密的python脚本，也可一找相关图片隐写解密工具

    
    
    import base64
    from io import BytesIO
    from PIL import Image
    
    base64_data = "aVZCT1J3MEtHZ29BQUFBTlNVaEVVZ0FBQU1nQUFBRElDQVlBQUFDdFdLNmVBQUFIaGtsRVFWUjRuTzJad1k0c09RZ0U1LzkvK3UyMU5TdTdCd3JTaVN0QzhoR2M0SXBMOTg4L0FGanljem9BZ0RNSUFyQUJRUUEySUFqQUJnUUIySUFnQUJzUUJHQURnZ0JzUUJDQURRZ0NzQUZCQURhRUJmbjUrUmwvbk9aTFAxeER6K3g5VTA1cWJoWjFkcjRzSFQyejkwMDVxYmxaMU5uNXNuVDB6TjQzNWFUbVpsRm41OHZTMFRONzM1U1RtcHRGblowdlMwZlA3SDFUVG1wdUZuVjJ2aXdkUGJQM1RUbXB1Vm5VMmZteWRQVE0zamZscE9hdVhKUVRUamxkSHZ0YmxvNDZOUWp5UjV4eUlvZ09CUGtqVGprUlJBZUMvQkdubkFpaUEwSCtpRk5PQk5HQklIL0VLU2VDNkVDUVArS1VFMEYwakJWRS9aSGM4SEhkUHZ1RWQwZVF3N003MWFtelRIaDNCRGs4dTFPZE9zdUVkMGVRdzdNNzFhbXpUSGgzQkRrOHUxT2RPc3VFZDBlUXc3TTcxYW16VEhoM0JEazh1MU9kT3N1RWQwZVFJcWJNNENUcmhKMGhTQkZUWmtDUUdBaFN4SlFaRUNRR2doUXhaUVlFaVlFZ1JVeVpBVUZpSUVnUlUyWkFrQmdJVXNTVUdSQWtCb0lVMFRHZjAxN2UrdTRJVXNScEtSRGtXYzVsdjNEQlN4ZjFqZE5TSU1pem5NdCs0WUtYTHVvYnA2VkFrR2M1bC8zQ0JTOWQxRGRPUzRFZ3ozSXUrNFVMWHJxb2I1eVdBa0dlNVZ6MkN4ZThkRkhmT0MwRmdqekx1ZXdYTGhCL2VGazZjcm84Mm9rc2IzMTNCQkgwdkNITFc5OGRRUVE5YjhqeTFuZEhFRUhQRzdLODlkMFJSTkR6aGl4dmZYY0VFZlM4SWN0YjN4MUJCRDF2eVBMV2R5OFZaTXJwV1BDYjY2YWNEQWdTbUkrNjJTY0RnZ1RtbzI3MnlZQWdnZm1vbTMweUlFaGdQdXBtbnd3SUVwaVB1dGtuQTRJRTVxTnU5c25nOVNPMkFjcmxQN212SXd2OEg3YjVDd1NCVDlqbUx4QUVQbUdidjBBUStJUnQvZ0pCNEJPMitRc0VnVS9ZNWk4UUJENlIvUS9pMURPTFU4OHBkV3FxY3lKSTBlenFubFBxMUNBSWdveXFVNE1nQ0RLcVRnMkNJTWlvT2pVSWdpQ2o2dFFnQ0lLTXFsTnpYQkExYnhZeWk5TU1UbStVeWwvZXNSZ0VpZU0wZzlNYnBmS1hkeXdHUWVJNHplRDBScW44NVIyTFFaQTRUak00dlZFcWYzbkhZaEFranRNTVRtK1V5bC9lc1JnRWllTTBnOU1icGZLWGR5d0dRZUk0emVEMFJxbjhwYzJTUTcxWkFxZlpwd2pTVWJmc2w2cEtoRU1RajV3SUVzeWZxa3FFUXhDUG5BZ1N6SitxU29SREVJK2NDQkxNbjZwS2hFTVFqNXdJRXN5ZnFrcUVReENQbkFnU3pKK3FTb1JERUkrY0NCTE1uNm9xRHVleWpLNmVhcHdFNmNpWjdabkttS29xRHVleWpLNmVhaEFFUVI3VnFYdXFRUkFFZVZTbjdxa0dRUkRrVVoyNnB4b0VRWkJIZGVxZWFoQUVRUjdWcVh1cVFaQ0JncWcvNWpmZjEvRngzUzdXOHE2cHdia1BRUkNFK3hDa01HZnFycW5CdVE5QkVJVDdFS1F3WitxdXFjRzVEMEVRaFBzUXBEQm42cTdLY0ZtY0hzYnBvM1RLMlpGbEFnaHlPQXVDZUlNZ2g3TWdpRGNJY2pnTGduaURJSWV6SUlnM0NISTRDNEo0Z3lDSHN5Q0lONldDM1A0d1RvL3RKTEo2TDhvc0NGSjBueG9FUVpDMkxCMzNxVUVRQkduTDBuR2ZHZ1JCa0xZc0hmZXBRUkFFYWN2U2NaOGFCRUdRdGl3ZDk2bEJrSUdDZE5TcGUyYnZVMzk0Nm5mb3lPazAzN0pmdU1Ba2VGZlA3SDFPSDE3MlBuVk9wL21XL2NJRkpzRzdlbWJ2Yy9yd3N2ZXBjenJOdCt3WExqQUozdFV6ZTUvVGg1ZTlUNTNUYWI1bHYzQ0JTZkN1bnRuN25ENjg3SDNxbkU3ekxmdUZDMHlDZC9YTTN1ZjA0V1h2VStkMG1tL1pMMXhnRXJ5clovWStwdzh2ZTU4NnA5Tjh5MzdoQXZHSGZzUHlPN0pNMmFkNlp3aGkrbWdkODkyd1R3UzU3RUU3WmtjUUJMbm1RVHRtUnhBRXVlWkJPMlpIRUFTNTVrRTdaa2NRQkxubVFUdG1SNUFYQ1hJNzZnKzJBN1dRSFZrNnhFcmxUMVZkRElKNFpFRVFVeERFSXd1Q21JSWdIbGtReEJRRThjaUNJS1lnaUVjV0JERUZRVHl5akJXa1kyRDFjV0xLQitUeXdYNERRUkFFUVlUM0ljaGhFS1FXQkVFUUJCSGVoeUNIUVpCYUVBUkJFRVI0SDRJY0JrRnFzUmJFaVk2Y04zek1UaCtzK28xUy9VNEg2QUpCRUFSQk5pQUlnaURJQmdSQkVBVFpnQ0FJZ2lBYkVBUkJFR1FEZ2lESUtFRnUrTGc2NW5QSzRuVFV1MTdlRlM0d2VqUjF6bzc1bkxJNEhmV3VsM2VGQzR3ZVRaMnpZejZuTEU1SHZldmxYZUVDbzBkVDUreVl6eW1MMDFIdmVubFh1TURvMGRRNU8rWnp5dUowMUx0ZTNoVXVNSG8wZGM2TytaeXlPQjMxcnBkM2hRdU1IazJkczJNK3B5eE9SNzNyNVYzaEFxTkhVK2QwMnN1VUxOTnpJb2h4M1ExWnB1ZEVFT082RzdKTXo0a2d4blUzWkptZUUwR002MjdJTWowbmdoalgzWkJsZWs0RU1hNjdJY3YwbkFoU3hKUVoxRDJuZkMvTEhKWExjQm9ZUVR4NlR2bGVsamtxbCtFME1JSjQ5Snp5dlN4elZDN0RhV0FFOGVnNTVYdFo1cWhjaHRQQUNPTFJjOHIzc3N4UnVReW5nUkhFbytlVTcyV1pvM0laVGdNamlFZlBLZC9MTWtmbE1weVk4bEVxSC9zSlRoODZnaFNBSUxVZ1NQT2kxQ0JJTFFqU3ZDZzFDRklMZ2pRdlNnMkMxSUlnell0U2d5QzFJRWp6b3RRZ1NDMElVckNvS1NjN245TmVzcHplZmNVTTJmbFMvU29EVERrZEMzYWF3U2tuZ2d3OEhRdDJtc0VwSjRJTVBCMExkcHJCS1NlQ0REd2RDM2Fhd1NrbmdndzhIUXQybXNFcEo0SU1QQjBMZHByQktlZnJCQUY0RXdnQ3NBRkJBRFlnQ01BR0JBSFlnQ0FBR3hBRVlBT0NBR3hBRUlBTkNBS3dBVUVBTmlBSXdBWUVBZGp3SHlVRnd2VnIwS3ZGQUFBQUFFbEZUa1N1UW1DQw=="
    
    # 第一次解码 base64 数据
    image_data1 = base64.b64decode(base64_data)
    
    # 第二次解码 base64 数据
    image_data2 = base64.b64decode(image_data1)
    
    # 创建 BytesIO 对象
    image_stream = BytesIO(image_data2)
    
    # 打开图片
    image = Image.open(image_stream)
    
    # 显示图片
    image.show()

运行脚本后显示一个二维码图片

![](./img/693653608157869966.png)

9、解码后得到一个密码，尝试了下root登录发现失败

![](./img/2831613647256331415.png)

10、思路到这里断了，看了下别人打靶文章发现还扫出了一个目录bulma。vulnhub靶机都是基于kali中自带的字典来设置目录路径或密码的，所以使用kali自带的字典可以爆出这个目录，一般的目录爆破工具爆不出来

![](./img/2058394015709647306.png)

11、点开音频文件是一段莫斯密码，这里没有解密，直接看了别人的解密结果（在线解码地址：`https://morsecode.world/international/decoder/audio-decoder-expert.html`）。解密后可以得到一个用户名和密码trunks:u$3r，尝试ssh登录，登录成功

![](./img/7506091274480441588.png)

# 三、内网信息收集

1、查看下账号权限，发现是普通用户

![](./img/1511937553841458301.png)

2、看下当前目录有什么文件

![](./img/7261744313795425992.png)

3、看下passwd文件和shadow文件权限，passwd文件存在读写权限

![](./img/1648931261868807873.png)

# 四、linux提权

1、passwd文件提权，首先生成一个加密密码。可以直接使用kali中的openssl生成，`openssl passwd
-1`。这里生成了一个密码为123的加密密码

![](./img/3485659621993919978.png)

2、`echo 'test:$1$imGj2JWO$YVM/Yh0cfGHtlm7Uz5vKw/:0:0:root:/root:/bin/bash'
>>/etc/passwd`，向passwd文件中写入一个用户名为test，密码123的用户，权限为root。写入成功会显示出来，失败则会显示不全

![](./img/2929598195839147769.png)

# 五、get flag

1、直接`su test` 切换账号

![](./img/6574499189001280166.png)

2、切换到root目录下，获得flag

![](./img/1815754028743737189.png)

# 六、总结

这个靶机挺简单的，主要考察了图片解密，莫斯音频解密，passwd文件提权，还有就是bulma这个目录可能扫不出来。

