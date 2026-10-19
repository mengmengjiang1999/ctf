## yak语言简介

`yak`是一款专门为渗透测试而生的编程开发语言，是国际上首个致力于网络安全底层能力融合的 垂直开发语言，提供了非常强大的安全能力，`Yak`是绝大部分
“数据描述语言 / 容器语言”
的超集，也是图灵完备的脚本语言。通过函数提供各类底层安全能力，包括端口扫描、指纹识别、`poc`框架、`shell`管理、`MITM`劫持、强大的插件系统等。

## 正文部分

本篇文章出于小白的角度，结合学习`yak官方文档`，开发自己的第一个插件。

在`yak`出现之前，我们更习惯使用`Python`脚本来编写个人的`PoC`，一个最最最简单的检测方法如下：

  

    
    
    socket.setdefaulttimeout(1)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host, 6379))
                s.send(bytes("INFO\r\n", 'UTF-8'))
                result = s.recv(1024).decode()
                if "redis_version" in result:
    	             core.checksuc(target=host,name='Redis unauthorize',payload='INFO')
    

检测思路非常简单，首先与目标及端口建立socket连接，之后向目标发送INFO这个字节，然后根据对方返回给我们的响应是否包含redis_version的关键字节来判断是否存在Redis未授权访问。

那么就可以使用同样的思路使用yak编写。

首先，我们先设定`log`级别：

  

    
    
    log.setLevel("info")
    

然后我们需要设定两个参数，`target`和`port`，同时对这两个参数的输入有一个初步的判断：

    
    
    target = cli.String("target")
    // 这里就是判断如果target输入是空，那么程序会退出，输出Empty Target
    if target == "" {
        die("Empty Target")
        return
    }
    
    port = cli.Int("port", cli.setDefault(6379))
    if port <= 0 {
        die("Port is invalid")
        return
    }
    

接着我们和目标及端口建立连接并判断建立是否成功，失败的话输出具体的错误信息：

    
    
    conn,err = tcp.Connect(target, port)
    if err != nil {
        log.Info("Connect to %v failed: %v", target, err)
    }
    die(err)
    

成功建立连接之后，我们就向目标发送`info`字节：

    
    
    log.Info("write info to %v", target)
    conn.Send("info\r\n")
    

接着我们对目标返回响应进行判断：

    
    
    log.Info("Start to waiting result")
    result, err := conn.RecvStringTimeout(1)
    if str.Contains(result, "redis_version") {
        log.info("Found Redis未授权访问漏洞", str.HostPort(target, port))
    }
    

就这样，一个非常基础简单的未授权检测脚本就写好了，测试一下看看：

![v2-c02aa35fc5cbf3655dd5ec9b2142cdb0_720w.jpg](https://image.3001.net/images/20220218/1645153747_620f0dd35a61ef67797a2.jpg!small)

很有趣对吧。

有了基础的框架之后，我们就可以进行添加功能，比如结果保存至自定义文本、批量扫描，这里以自定义文本举例：

首先要满足自定义文本，我们需要用到yak的file函数，根据文档，`file.Open("test-file.txt")`等效为`file.OpenFile("test-file.txt", file.O_CREATE|file.O_RDWR,
0777)`

那么我们就可以如下构建：

    
    
    log.info("Save the results to %v",out_put)
    f,err := file.Open(out_put)
    die(err)
    f.Write(result)
    f.Close()
    

这里的out_put参数也就是新添加的参数：

    
    
    out_put = cli.String("output",cli.setDefault("_result.txt"))
    if out_put == ""{
        die("Empty output")
        return
    }
    

这里我们是把目标`redis`运行`info`的结果保存到本地，此时运行：

![v2-e781994167a2bcf2701fd10dea2fe217_720w.jpg](https://image.3001.net/images/20220218/1645153747_620f0dd3a899dbb3ae35b.jpg!small)

此时目录下会自动创建一个redis.txt的文本，内容为info的具体信息：

![v2-7bef90d15e607d962c9c12610b60e96f_720w.jpg](https://image.3001.net/images/20220218/1645153752_620f0dd86199a837034cf.jpg!small)

如果我们想进行批量扫描，同样也需要file函数按行读写功能，这里暂不赘述：

    
    
    f, err := file.Open("12_fileio.yak")
    die(err)
    dump(f.ReadLines())
    f.Close()
    

yak脚本编写完成之后，我们运行`Yakit`，尝试编写一个`Yakit插件`：

首先新建一个插件，填写基础信息：

![v2-d042f8451ea841b632035f919312f8e9_720w.jpg](https://image.3001.net/images/20220218/1645153752_620f0dd8bc38f9b230b2f.jpg!small)

之后开始编写插件源码。

首先我们必须要对插件进行初始化：

    
    
    yakit.AutoInitYakit()
    

接着运用同样的检测思路：

    
    
    target = cli.String("target")
    if target == "" {
        yakit.Error("Empty Target")
        return
    }
    
    port = cli.Int("port", cli.setDefault(6379))
    if port <= 0 {
        yakit.Error("Port is invalid")
        return
    }
    conn,err = tcp.Connect(target, port)
    if err != nil {
        yakit.Error("Connect to %v failed: %v", target, err)
    }
    die(err)
    
    yakit.Info("write info to %v", target)
    conn.Send("info\r\n")
    
    yakit.Info("Start to waiting result")
    result, err := conn.RecvStringTimeout(3)
    if str.MatchAllOfSubString(result, "redis_version") {
        yakit.StatusCard("Redis未授权访问漏洞", str.HostPort(target, port))
    }
    

这里面某些函数和单独编写`yak`脚本不同，具体内容可以参考`Yakit`的API文档

源码编写好之后，我们需要添加一个必要参数，也就是目标：

![v2-50abc74b154b6879a3a572fbaf4968ba_720w.jpg](https://image.3001.net/images/20220218/1645153756_620f0ddc001504cf64907.jpg!small)

点击下方创建新模块之后，在插件板块我们就可以看到我们编写的新插件：

![v2-14cbe4b66d1f7e16be5b68fa3ea450de_720w.jpg](https://image.3001.net/images/20220218/1645153756_620f0ddc487aaf2b3ab10.jpg!small)

输出目标IP之后测试一下：

![v2-59f104d7153fe83630353357fe6cecef_720w.jpg](https://image.3001.net/images/20220218/1645153756_620f0ddc8b7da56a91fcf.jpg!small)

至此，一个简单的`Redis未授权`检测插件编写完毕。

## 结语

yak的用法显然不止如此，还有更为强大的`poc`函数和`nuclei`函数，官方的文档也非常清晰易懂，适合小白入手。

## END

感谢斑马还没睡的投稿~~我们的投稿活动还在进行中，走过路过不要错过，参加即可获得精美小礼物，投稿还有稿费噢~进交流群和投稿添加以下微信即可~有找工作想法的小伙伴也欢迎打扰噢（实习也招~）

投稿活动详情（[Yakit联合HackingClub开启有奖征稿啦~](https://link.zhihu.com/?target=http%3A//mp.weixin.qq.com/s%3F__biz%3DMzAxOTAzOTU3Mw%3D%3D%26mid%3D2247484212%26idx%3D1%26sn%3Da391d8bbeaecd0baff71accad6b3bada%26chksm%3D9bcc570eacbbde18637049dc30ea0ad5f3f1fce062e00b19254faf6de686bdb54c4a38362ac7%26scene%3D21%23wechat_redirect)）

官网教程：https://www.yaklang.io/products/intro

下载地址：https://github.com/yaklang/yakit

