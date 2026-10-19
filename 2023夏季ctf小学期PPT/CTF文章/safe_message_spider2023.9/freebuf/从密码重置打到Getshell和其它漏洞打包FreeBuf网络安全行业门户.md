# 前言

前几天是准备上点edusrc的分的所以就准备用手上还没刷的Nday继续上分，然后就有了今天这个案例：

# 信息收集

之前在挖某体育学院证书的时候就挖到过一个通过修改html文件更改密码修改步骤的漏洞。

![202307201406779.png](https://image.3001.net/images/20230724/1690189458_64be3e927f58bd929844a.png!small)

所以就准备测绘一下这个资产继续看看能不能上分。

![202307201406781.png](https://image.3001.net/images/20230724/1690189459_64be3e93ab9818ff79ca8.png!small)

![202307201406782.png](https://image.3001.net/images/20230724/1690189460_64be3e94c2d884f20cc76.png!small)

挑一个打开：

![202307201406783.png](https://image.3001.net/images/20230724/1690189461_64be3e95c4772ad3f563b.png!small)

没有背景图了但还是同资产，因为在测试某体育学院的时候是有账户的，所以直接输入那个账户就能进行下一步操作了，但是这个资产无账户，所以我打算去在搜集一下学号之类的。

![202307201406785.png](https://image.3001.net/images/20230724/1690189462_64be3e96a190aaba5c0af.png!small)

![202307201406786.png](https://image.3001.net/images/20230724/1690189463_64be3e97c2d2f327ecf94.png!small)

学号这块都是一无所获，然后正准备想其它切入点的时候就突然发现：

![202307201406787.png](https://image.3001.net/images/20230724/1690189464_64be3e98e047c00a14fb2.png!small)

这块的要求是输入学号后5位，而学号通常是有规律的，所以就去生成字典FUZZ了一下。

![202307201406789.png](https://image.3001.net/images/20230724/1690189465_64be3e99c9b41bbf4fe0a.png!small)

Python输出从00000~99999字典的程序为：

    
    
    dictionary = {}  
    ​  
    for i in range(100000):  
    ​  
    key = str(i).zfill(5)  
    ​  
    value = \"Value \" + key  
    ​  
    dictionary\[key\] = value  
    ​  
    with open(\'dict.txt\', \'w\') as file:  
    ​  
    for key, value in dictionary.items():  
    ​  
    file.write(key + \'\\n\')

![202307201406790.png](https://image.3001.net/images/20230724/1690189466_64be3e9ad4b1db714528f.png!small)

载入字典后还要设置下时间。

![202307201406791.png](https://image.3001.net/images/20230724/1690189468_64be3e9c0e1f49345760f.png!small)

最后成功拿到几个账户。

![202307201406792.png](https://image.3001.net/images/20230724/1690189469_64be3e9d04ea5ba8afc91.png!small)

EDUSRC不收爆破类漏洞所以这个学号不能算是漏洞，但最后学号总归是出来了。

随后直接输入FUZZ出的5位学号把<https://1.test.edu.cn/passworf/find1_html>后的find1_html改为find2_html

![202307201406793.png](https://image.3001.net/images/20230724/1690189469_64be3e9df2b74e64f9046.png!small)

直接输入我们要重置的密码更改成功后去登录后台：

![202307201406794.png](https://image.3001.net/images/20230724/1690189470_64be3e9ec34a33d141cdc.png!small)

持续浏览功能点寻找突破点：

![202307201406796.png](https://image.3001.net/images/20230724/1690189471_64be3e9fb97bea4cdad61.png!small)

发现一个活动添加点：

![202307201406797.png](https://image.3001.net/images/20230724/1690189472_64be3ea0a1fe6df379226.png!small)

不存在上传点但是存在描述功能，直接构造xss的payload试试：

<Script>alert("1)</Script>![202307201406798.png](https://image.3001.net/images/20230724/1690189473_64be3ea17ae1a916c9b95.png!small)

存储XSS+1

此处的payload：<Script>alert("1)</Script>

采用大小写绕过

随后又发现一个信息上传点：

这几块点是透明没开bp，然后就打算开BP看看能不能拿到些什么突破口

![202307201406799.png](https://image.3001.net/images/20230724/1690189474_64be3ea26d17896c3d292.png!small)

点击这块的【添加简历信息】下面的标题处的第一个点：

![202307201406800.png](https://image.3001.net/images/20230724/1690189475_64be3ea347d05c64d967b.png!small)

发现是个信息编辑界面但它这块是跳出个小窗口的所以前面没怎么注意到开了BP抓包时才发现这块点：

![202307201406801.png](https://image.3001.net/images/20230724/1690189476_64be3ea4236cafd7394bb.png!small)

点击右侧的修改抓包后：

![202307201406802.png](https://image.3001.net/images/20230724/1690189477_64be3ea503b897335583a.png!small)

![202307201406803.png](https://image.3001.net/images/20230724/1690189477_64be3ea5cca7e0eb7e890.png!small)

发现id值，直接单引号闭合查看：

![202307201406804.png](https://image.3001.net/images/20230724/1690189478_64be3ea6c86c6a89c6a18.png!small)

浏览器端：

![202307201406805.png](https://image.3001.net/images/20230724/1690189479_64be3ea7d4010e82cb2bd.png!small)

发现执行了sql语句

且发现是GET请求：

![202307201406806.png](https://image.3001.net/images/20230724/1690189480_64be3ea8b4e3c869db2a5.png!small)

所以把这块的路径拉到浏览器直接访问：

![202307201406807.png](https://image.3001.net/images/20230724/1690189481_64be3ea9b23c5672e1623.png!small)

这样就不用担心防sqlmap表单了，且不用打包数据包更快捷了：

![202307201406808.png](https://image.3001.net/images/20230724/1690189482_64be3eaa96d83903f3bd6.png!small)

![202307201406809.png](https://image.3001.net/images/20230724/1690189483_64be3eab8bdf7b0e42ae2.png!small)

Sqlmap成功跑出数据！

Sql注入+1

随后继续到【会员注册】处

![202307201406810.png](https://image.3001.net/images/20230724/1690189484_64be3eac9434fe3deb823.png!small)

![202307201406811.png](https://image.3001.net/images/20230724/1690189485_64be3ead740062edf8e2b.png!small)

直接在搜索处单引号闭合：

![202307201406812.png](https://image.3001.net/images/20230724/1690189486_64be3eae698412b59b6db.png!small)

![202307201406813.png](https://image.3001.net/images/20230724/1690189487_64be3eaf3c60ecc84780a.png!small)

成功执行查询语句：

![202307201406814.png](https://image.3001.net/images/20230724/1690189488_64be3eb036b35e343a063.png!small)

F12调出网络又发现也是GET请求方式，复制请求URL直接查看回显：

![202307201406815.png](https://image.3001.net/images/20230724/1690189489_64be3eb1495279c32d763.png!small)

直接sqlmap跑：

![202307201406816.png](https://image.3001.net/images/20230724/1690189490_64be3eb252e665950db4e.png!small)

Sql注入+2

然后点击右上角【管理员】三个字：

![202307201406817.png](https://image.3001.net/images/20230724/1690189491_64be3eb33c761314ec5fd.png!small)

一开始没发现这三个字还能点击，点击后发现到了信息上传点：

![202307201406819.png](https://image.3001.net/images/20230724/1690189492_64be3eb4576fc1c78f6b7.png!small)

这块可以上传文件先上传个php试试：

![202307201406820.png](https://image.3001.net/images/20230724/1690189493_64be3eb5479e8d08f6c74.png!small)

提示只能上传上面列出的文件类型，正要准备想其它办法绕过的时候突然发现这块允许上传的文件类型中包括pdf，所以直接上传一个pdf-xss试试：

![202307201406821.png](https://image.3001.net/images/20230724/1690189494_64be3eb66477a447d22c3.png!small)

成功上传然后浏览器访问试试：

![202307201406822.png](https://image.3001.net/images/20230724/1690189495_64be3eb796bfd20e6e439.png!small)

但浏览器提示没有文件，然后仔细看了一下文件上传回显：

![202307201406823.png](https://image.3001.net/images/20230724/1690189496_64be3eb8892f62d314a8c.png!small)

这里的uploadfile/16893293978.pdf的路径是跟在了?value=参数后面的然后这块参数给完后还在后面又跟了个参数：

![202307201406824.png](https://image.3001.net/images/20230724/1690189497_64be3eb9a1ee919c63e10.png!small)

？file=url=uploadfile/16893293978.pdf，再回到请求包中的参数：

![202307201406825.png](https://image.3001.net/images/20230724/1690189498_64be3eba74c76bee1377c.png!small)

发现此处的有个&field=url的参数尝试把参数改成1：

![202307201406826.png](https://image.3001.net/images/20230724/1690189499_64be3ebb50fe06379cebc.png!small)

![202307201406827.png](https://image.3001.net/images/20230724/1690189500_64be3ebc3006d9bd9953c.png!small)

浏览器回显不存在"1"，所以这块就明了的，参数&field=后面应该接的参数是文件上传后的路径，因为我们这块输入1，不存在1这个文件所以回显NotFound
，明了了这块所以我们那文件试试：

![202307201406828.png](https://image.3001.net/images/20230724/1690189501_64be3ebd09c17ade5072d.png!small)

![202307201406829.png](https://image.3001.net/images/20230724/1690189501_64be3ebdbea351667ab1e.png!small)

放包：

![202307201406830.png](https://image.3001.net/images/20230724/1690189502_64be3ebed9ddf6dd434d7.png!small)

成功触发XSS

存储xss+2

但是这块的任务是getshell所以还是继续尝试文件上传：

![202307201406831.png](https://image.3001.net/images/20230724/1690189504_64be3ec00053ae05249f3.png!small)

修改MIME信息且php5分段绕过但还是提示不能上传，传了图片马但是不能解析：

![202307201406832.png](https://image.3001.net/images/20230724/1690189504_64be3ec0e03f526910c05.png!small)

这块上传应该是写死了，所以继续找其它突破口，查看参数发现存在"filename"

![202307201406833.png](https://image.3001.net/images/20230724/1690189506_64be3ec25ffb41bbd61cf.png!small)

问题参数啊，迅速添加延时命令试试：

`sleep 7`

![202307201406834.png](https://image.3001.net/images/20230724/1690189507_64be3ec37a3ab7295be58.png!small)

![202307201406835.png](https://image.3001.net/images/20230724/1690189508_64be3ec46030da8b581b3.png!small)

回显处成功延时：

![202307201406836.png](https://image.3001.net/images/20230724/1690189509_64be3ec52b8426ed185b1.png!small)

命令执行成功！进一步探测：

![202307201406837.png](https://image.3001.net/images/20230724/1690189510_64be3ec610acdbb84db9d.png!small)

Curl命令探测ngrok.io

![202307201406838.png](https://image.3001.net/images/20230724/1690189510_64be3ec6dd4d56ed3b3eb.png!small)

![202307201406839.png](https://image.3001.net/images/20230724/1690189511_64be3ec7c59799f6578c9.png!small)

成功回显！

命令执行+1，最后相对应的用命令获取shell就行。

# 总结

整体难度适中只不过这次测试后台功能点有点多需要仔细观察测试，后台的信息收集做好了Getshell难度瞬间就变小了。

