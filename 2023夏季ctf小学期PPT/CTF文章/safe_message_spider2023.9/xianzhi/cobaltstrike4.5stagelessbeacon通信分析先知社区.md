# 环境准备

分析stageless beacon 的http通信过程主要是为了看cs 各个功能是如何实现的以及具体的通信包结构以便自己实现beacon。

使用idea 反编译然后导入原jar包作为依赖的方法进行调试跟踪。  
取出序列化存储在.cobaltstrike.beacon_keys 里的rsa 公私钥。  
为了方便对通信数据进行手动解密需要把cs通信过程都做一个base64编码，服务端使用这个profile 启动即可

    
    
    http-get {
        set uri "/ca /dpixel /__utm.gif /pixel.gif /g.pixel /dot.gif /updates.rss /fwlink /cm /cx /pixel /match /visit.js /load /push /ptj /j.ad /ga.js /en_US/all.js /activity /IE9CompatViewList.xml";
    
        client {
            metadata {
                base64;
                header "Cookie";
            }
        }
    
        server {
            header "Content-Type" "application/octet-stream";
    
            output {
                base64;
                print;
            }
        }
    }
    
    http-post {
        set uri "/submit.php";
    
        client {
            header "Content-Type" "application/octet-stream";
            id {
                parameter "id";
            }
            output {
                base64;
                print;
            }
        }
        server {
            header "Content-Type" "text/html";
            output {
                base64;
                print;
            }
        }
    }

# 上线&心跳get请求

beacon 上线第一个请求就是一个带有metadata 信息的get包，然后服务端再返回一个没内容的响应包。  
默认这个metadata 信息是用rsa 公钥加密放在cookie 里的，这个行为的在profile 文件的http-get.client.metadata
里定义。  
后续的心跳请求也是这个，如果服务端有命令要下发给beacon 执行就是通过心跳请求的响应包来传递。

![](./img/8536865575389481490.png)

## teamserver 处理请求

teamserver 的NanoHTTPDrun 方法在获取到请求后传给WebServer.serve，最终请求信息传递给WebServer._serve
来处理请求信息。  
_serve 方法先检测ua是否在黑名单里在就把blockedByUA 设置为true，然后又检查ua
是否在白名单里，如果有设置白名单并且没有匹配到的话就把allowedByUA 设置我false，allowedByUA默认为true。  
只有当满足 allowedByUA && !blockedByUA 条件时才继续执行函数，否则就在控制台提示然后返回404  
黑白名单的ua 可以在profile的http-config 中配置，curl _/lynx_ /wget* 是默认黑名单

![](./img/6367586927235263731.png)

下一步就是判断请求方法是不是OPTIONS ，是就返回200 和允许的方法

![](./img/7330961306090603562.png)

再往下就是之前爆出的路径不规范泄露stager信息漏洞的地方，这里看this.hooks里的内容如果直接传入一个类似GET stager
HTTP/1.1，这样的请求头就会泄露stager信息

![](./img/8692711284805575488.png)

![](./img/9008125646149922321.png)

接着判断uri是否在profile 定义的http-get.set uri 或http-post.set uri里，满足就会先用service.serve
即MalleableHook.serve方法处理请求，MalleableHook.serve最终调用的是BeaconHTTP._A.serve方法，

![](./img/8721520337523936253.png)

## 处理metadata 信息

BeaconHTTP._A.serve 是处理metadata 信息用的  
BeaconHTTP._A.serve 方法先获取了beacon 端的ip，先使用recover 方法对metadata 进行bese64
解码，解码之后传入process_beacon_metadata 进行处理

![](./img/8915739643461151773.png)

process_beacon_metadata 方法内第一行先对var3即metadata 进行rsa解码，然后对各metadata 各部分的数据进行处理。

metadata 的数据结构如下，最终process_beacon_metadata 返回

    
    
    4byte：元数据的固定开头magic number 48897
    4byte：数据长度
    16byte：把这16位进行sha256加密，得出的32位二进制结果的前16位就是通信的aes密钥，后16位就是hmac hash
    2byte：大端字节序表示的编码，具体对应关系在WindowsCharsets.getName
    2byte：大端字节序表示的编码，具体对应关系在WindowsCharsets.getName
    4byte：beacon session id，用来标识每个会话
    4byte：pid
    2byte：ssh port
    1byte：用来判断系统和程序位数，和是否system权限，初始值为0，如果是64位系统就+4，如果是64位程序就+2，如果是system权限就+8，报错获取不到就+1，这里用按位与的方法来累加判断，用非常少的代码就表实现了这个判断，很巧妙。
    2byte：windows nt 版本
    2byte：window 系统build 号
    4byte：未知作用
    4byte：ptr_gmh
    4byte：ptr_gpa
    4byte：大端字节序表示的内网ip地址
    计算机信息：从输入的metadata 的第59位开始截取到末尾，截取的数据就是计算机名\n用户名\n程序名

![](./img/2675184586158260862.png)

![](./img/7181593499653382501.png)

处理完metadata 信息后就回到MalleableHook.serve构造返回包给beacon，get 请求就处理完了

![](./img/2008451890437621494.png)

用python 对metadata 解析

![](./img/3176529885852644249.png)

# TeamServer 下发任务

cs 客户端构造命令发送到teamserver，beacon 通过get 心跳会话的响应包获取teamserver 下发的任务。  
teamserver 会用metadata 信息里的aes key 和硬编码的iv abcdefghijklmnop
对下发的任务数据进行aes加密，然后使用hmac key 当做盐和aes 加密后的数据进行hash 计算得到的hash
签名再和aes加密后的数据进行拼接，最后通过响应包的形式下发给beacon。

## cs 客户端构造任务数据

比如执行shell whoami 对应任务数据结构是%COMSPEC%\n/C whoami这样，这个是在cs
的客户端就构造好直接发送给teamserver 的，在aggressor/windows/BeaconConsole 类的actionPerformed
方法会根据会话里输入的命令类型进入到TaskBeacon 里相应的方法

![](./img/6703460684254538026.png)

来到shell方法，这里把beacon会话对应的beacon id、任务类型、具体命令传入三参数的shell方法

![](./img/1832387747618834693.png)

具体参数如下图，经过判断后走到1645行开始构造任务数据的结构，这里不同的任务类型结构不一样，shell 开头的命令结构就是这样。  
this.builder.setCommand 是把this.builder.command 设置为shell 命令类型即78  
addLengthAndString 给this.builder.backing 添加一个4byte 的"%COMSPEC%"长度和其本身  
addLengthAndEncodedString
把输入的命令whoami转换成beacon客户端的编码，并把长度和内容添加进this.builder.backing，长度还是占4byte  
addShort添加2个0

![](./img/4563928401202228761.png)

然后跟入1651行的build方法，这个方法的作用是在刚才构造出来的this.backing前面加上4byte
的命令类型即78，以及4byte的之前this.bucking的长度，这就是最终cs客户端传递给teamserver 的命令结构了

![](./img/282192920921707224.png)

## TeamServer 对客户端活动监控

eamServer 起来后会起一个while 循环一直监听客户端连接，当有客户端连着teamserver的时候会读取客户端输入的内容到一个Request
对象，这个对象的类属性call 是客户端的活动类型，如果是在beacon 会话里输入命令则call 就是beacon.task；另一个类属性args
就是输入的参数的加工格式。

![](./img/9148883384676519177.png)

跟如process 方法，里面会根据var1.call 属性来进入不同的方法，beacon任务类在最后一个else
if里，前面没有匹配到的call类型但又含有在this.calls 里的就会进入到这个else if。  
然后在这里通过hook进入到Beacon.call方法，beacon开头的call属性都会进入到这个方法被处理。

![](./img/6183079080528332084.png)

跟如Beacon.call 方法  
传入的参数var1是Request 类对象，参数var2 是当前teamserver 控制台的登录用户信息。  
根据call 类型进入到297行的if 里，在300行进入task方法并传入beacon id和任务数据为参数。

![](./img/4608554256931191024.png)

跟入task 方法  
60行this.getQueue 把beacon id 为var1 的任务队列this.queues LinkedList 返回给var4  
第一个if先判断一下shouldPad这个暗桩是否开启，时间是否够了；第二个if 的A是判断有没有使用javaagent的结果，都没问题就到87行往var4
里添加任务数据，即往对应的this.quequs 任务队列里添加任务数据。this.queues 就是存储在teamserver 上等待beacon
来取的任务队列。

![](./img/270189310497710961.png)

## beacon 获取任务队列数据

回到处理get 请求的BeaconHTTP._A.serve 方法，当process_beacon_metadata 方法处理完metadata
信息后，125行判断有无错误，没有就进入到else部分用dump 方法通过beacon id获取teamserver console
的任务数据赋值给var8

![](./img/6142637837759267193.png)

跟入dump 函数，通过this.data.dump 函数获取任务赋值给var5

![](./img/6519173986176883018.png)

跟入this.data.dump 方法，154行把beacon id 传入getQueue 方法

![](./img/6684009255847949243.png)

getQueue 方法里从this.queues 里取出该beacon id 对应的任务返回。

![](./img/3402145085124524469.png)

如果var5有数据，在控制台输出这句发送了多少bytes 的提示，然后把任务返回给serve 方法的var8

![](./img/629465419262474497.png)

任务数据赋值给var8 后判断profile 中是否设置了数据抖动datajitter 设置了就在var8 后面拼接字符，没设置就直接到下一个if var8
>0 就对var8 进行加密

![](./img/547188634770233783.png)

跟入encrypt 方法，120、121行先根据beacon id 获取aes key、hmac key，然后给var3然后填充一个4byte
的时间戳、4byte的任务数据长度、任务数据，126行在用A补足长度。

![](./img/4878390935884765451.png)

130行使用aes key var5对var3 进行aes加密，137行对加密出来的var16 用hmac key即var6进行hmac hash
完整性签名计算，计算结果前16位赋值给var17，最后把var16和截取16 byte 的var17 拼接后返回。

## 任务数据结构

首先返回包是aes 加密的数据和16byte 的hmac hash签名  
数据结构如下

    
    
    4byte 时间戳
    4byte 任务数据长度
    任务数据
        4byte 命令类型
        4byte cmdbuf长度
        cmd buf

cmd buf不同类型的任务结构不一样，shell 任务的结构就是这样

    
    
    4byte cmdbuf len
    4byte %COMSPEC%长度
    %COMSPEC%
    4byte 命令长度
    命令
    2byte 00

脚本解析如下

![](./img/4900518092977974997.png)

# TeamServer 处理Beacon 回传任务结果

beacon 是通过post 来回传任务的结果，teamserver 处理post 数据是在BeaconHTTP._B.serve 方法里。  
beacon 会把session id放在post 会话里一起回传以告诉teamserver 数据对应的session id，默认这个id 是放在url
中。

![](./img/3260020663268913816.png)

serve 方法90行把这个id
赋值给var5。98行把post过来的数据base64解码后转成byte赋值var8，然后把这两个参数一块传入process_beacon_data 方法。

![](./img/6458457394633045153.png)

跟入process_beacon_data，这里把var2取出前4byte 转换为int赋值给var4 表示真实数据的长度，然后把剩下的赋值给var5
传入process_beacon_callback

![](./img/5753729447754975475.png)

继续跟入，process_beacon_callback

![](./img/254441536910904970.png)

跟入decrypt，169、170行分别为aes key和hmac key，然后把传入的数据var2的后16位即hmac
hash签名赋值给var7，其他的赋值给var6，再用var7对var6做完整性校验，通过的话就在186行把var6 做aes解密赋值给var19。

![](./img/6544859943002022564.png)

再把var19转成DataInputStream var11，取var11 的前4byte 赋给var12
用来验证是否重放攻击，再取4byte赋给var13 用来表示回传数据内容的长度，然后根据var13 来读取数据内容赋值var14

![](./img/4084390966694646407.png)

回到process_beacon_callback 后又把session id和刚才的返回值
process_beacon_callback_decrypted

![](./img/8641956367087752337.png)

process_beacon_callback_decrypted 里取var2 的前4byte
转换为int赋值给var16，var16就代表返回的任务类型，30就是shell
任务，进入到529行然后把剩下的var2取出来转换为对应的编码然后输出到控制台。

![](./img/4023890132708753354.png)

## 任务结果数据结构

总结一下beacon 回传的任务数据结构如下，这里这个其他数据在shell 类型里有8byte，暂时没看到有利用

    
    
    4byte：数据长度
        aes 加密数据
            4byte：cs 防重放int
            4byte：数据长度
                4byte：数据对应任务类型
                任务结果数据
                其他数据
        16byte：hmac hash签名

shell whoami 任务结果  
![](./img/2152182878118331199.png)

脚本连接<https://github.com/l3anma/cobaltstrike4.5_http_dec>

# 参考

<https://wbglil.gitbook.io/cobalt-strike/cobalt-strike-yuan-li-jie-shao/cs-mu-biao-shang-xian-guo-cheng#yuan-shu-ju>  
<https://unit42.paloaltonetworks.com/cobalt-strike-metadata-encryption-decryption/>

