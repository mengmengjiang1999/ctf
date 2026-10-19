## **0x01 概要**

我们在平时的安全运维中，Redis服务对我们来说是一种比较常见的服务，相应的Redis漏洞也比较棘手，网上有很多关于Reids漏洞利用和再现的方法，如果想延伸一下这个课题，我们可以考虑如何主动的防护redis的漏洞，那怕只是监听redis服务中，可能存在的威胁行为，先解决一部分问题？这个就是本文要给出的一个思路和解决方案。关键是，现在有些系统是不提供这种服务的，所以我们尝试定制开发。

##  **0x02 背景**

我们在再现redis的漏洞时，用tcpdump等工具，抓取了渗透的流量，把威胁流量保存写到pcap包中，经过分析我们发现redis的协议数据是明文的，经过截取包，我们可以看到其中的内容，所有的这些set、get、dir、config命令一般的流量中我们都可以看到，在redis密码没有设置的情况下。我们发现一般的防火墙也并不抓取redis的流量并解析，甚至是报警。基于我们之前的实践，既然tcpdump能抓到，我们用pcap基础开发包也可以抓到。

##  **0x03 防护策略**

既然我们可以抓取流量，就可以监听redis的流量中的内容，先期的预想是，只要我们分析出redis攻击行为几个动作序列，采用行为模式匹配的方式，只要有人触发了比较危险的几个动作指令，我们就把这次Redis操作列为一个可疑的行为，并对这种形为的IP进行监听日志留存，并把威胁攻击IP相关的属性信息，和其它设备中的威胁数据做碰撞，这一切基础前提就是：我们可以抓取访问者的流量（靠工具），并识别他的行为动作（靠策略）。下面我们就用工具监听redis的set、get、config命令为例子，通过这个来展示整个流程的监听过程。

##  **0x04 监听部署**

  
![1.png](https://image.3001.net/images/20180426/15247248799961.png!small)  

为了测试，我们是把某个机房的某个网段的流量，镜像集中到另一台服务器上，
我们集中监听打到这台服务上，其它的Redis的服务的流量汇总，我们通过分析这些Redis服务的操作内容，进行流量监控和行为识别，然后将监听的威胁行为数据保存到威胁行为库里。

##  **0x05 工具实施**

这个监听系统工作模式就这样，接下来就是我们要用工具实施我们方案，我们选用的工具还是传统的C语言和Lua的脚本方式，用C读取监听6379端口是的流量数据，然后将解析出来的数据推给Lua进行模式匹配。

  
![2.png](https://image.3001.net/images/20180426/15247248864679.png!small)  

一般的攻击行为都有一个大概的请求序列，Redis服务本身就是系统内存的一个服务器监听程序，一般会Bind本机的IP，监听默认的6379端口，如果Redis的对外提供服务，需要改变redis.conf的配置，打开配置文件对应把bind
xxx.xxx.xxx.xxx的IP改成你本地的网卡IP，这样在外部使用Redis访问，才不会出现端口访问被拒绝的情况。

![3.png](https://image.3001.net/images/20180426/15247248965437.png!small)  

改变IP后，我们要解决的是密码设置问题，如果有一天某台Redis的密码“消失了”。
这时这台机器可能会被威胁利用，这时就满足了我们要设定场景，重现这种情况就要把redis.conf中的密码去掉。

![4.png](https://image.3001.net/images/20180426/15247249063923.png!small)  

    
    
    sudo service redis restart

这种启动方式，是不能渗透成功的，我们要用下面的方式进行redis的服务启动，进入root然后输入:

    
    
    sudo -s 
    
    redis-server

如果我们想简单的用Tcpdump截取Redis数据包，我们可以用下面的命令：

    
    
    sudo  tcpdump -s0 -vv -e -i eth0 -nn port 6379 -w  candylab.pcap

我们可以一边渗透Redis，一边记录这次渗透过程中，攻击指令的序列数据。

下面就是用我们要用的工具，用于监听和解析Redis的流量数据的数据：

[https://github.com/shengnoah/riff](https://github.com/shengnoah/riff)

我们下载这个pcap监听的工具包,我们默认的工作平台是：

    
    
    make linux

因为，这个工具在linux上使用，用C实现，嵌入了Lua脚本插件化的处理，来获取监听接口的数据，本文中提的是对6379接口的监听。我们在完成编译动作后，需要改一个config.lua的配置。

打开config.lua， 修改return的返回值，告诉C主进程，我们让Pcap监听本机的6389端口，以下。

    
    
    function format()
    
        return "dst port 6389"
    
    end

需要注意的是watch.c的代码，以下

    
    
    const char* format = lua_tostring(L,-1); 
    
      lua_pop(L, 1); 
    
      /* construct a filter */  
    
      struct bpf_program filter;  
    
      //pcap_compile(device, &filter, "dst port 80", 1, 0);  
    
      // 这里的format就是config.lua的代码中return返回的内容: “dst port 6389”
    
      pcap_compile(device, &filter, format, 1, 0);  
    
      pcap_setfilter(device, &filter);  
    
    // 关键的部分就是让pcap进入监听主循环，轮询getPacket函数，不短把6379的数据推给getPacket，我们在这个函数，我们把网络的buf数据再推给Lua，用Lua进行相关的协议解析的处理。
    
     /* wait loop forever */  
    
      int id = 0;  
    
      pcap_loop(device, -1, getPacket, (u_char*)&id);  
    
      pcap_close(device);  

getPacket()这个函数，主体功还是把数据推给lua，基本的逻辑就是这么简单，关键就是这个有个入口buffer.lua，我们记着这个时序的入口就行，便于以后面的逻辑的理解清楚。
从buffer.lua这个执行序开始后，逻辑都交给lua来处理了，具体lua怎么处理，要自己根据自己定制的规则情况写处理逻辑。

    
    
    L = lua_open();
    
          luaL_openlibs(L);
    
      if (luaL_loadfile(L, "buffer.lua") || lua_pcall(L, 0,0,0))
    
          printf("Cannot run configuration file:%s", lua_tostring(L, -1));
    
      lua_getglobal(L, "buffer");
    
      lua_newtable(L); 
    
      int idx = 0;
    
      for (idx=1; idx < pkthdr->len; idx++) {
    
          lua_pushnumber(L, idx);  
    
          lua_pushnumber(L, packet[idx]);  
    
          lua_settable(L, -3);  
    
      }
    
      lua_pcall(L, 1,0,0);

Lua代码一直运行在pcap的循环内，采用的是插件机制，我们加一个处理，就相当于要加一个插件。插件模板的代码都是类似的，我们看一个其它的就看懂了，其它相关脚手架的代码不介绍了：

    
    
    local filter_plugin = {}
    
    local src = {
    
       args="filter args"
    
    }
    
    local sink = {
    
        name = "filter_plugin",
    
        ver = "0.1"
    
    }
    
    function filter_plugin.output(self, list, flg)
    
        if flg == 0 then
    
            return
    
        end
    
        for k,v in pairs(list) do
    
            print(k,v)
    
        end
    
    end
    
    function filter_plugin.push(self, stream) 
    
        for k,v in pairs(stream.metadata) do
    
            self.source[k]=v
    
        end 
    
    end
    
    function  filter_plugin.init(self)
    
        self.source = src
    
        self.sink = sink
    
    end
    
    function filter_plugin.action(self, stream) 
    
        io.write(stream.data, "\n")
    
        local flg = string.find(stream.data, "pcap")
    
        if flg then 
    
    	print("###########[ OK ]#############")
    
        end
    
    end
    
    function  filter_plugin.match(self, param)
    
        self.sink['found_flg']=false
    
        for kn,kv in pairs(self.source) do
    
             self.sink[kn] = kv
    
        end
    
        self.sink['metadata'] = { data=self.source['data'] }
    
        self:action(self.sink)
    
        return self.source, self.sink
    
    end
    
    return  filter_plugin

用lua写代码，是为了降低策略实现部分的代码复杂度，最关键的函数filter_plugin.action()，这里的stream.data就是吐到6369上的所有数据，包括Redis相关的执行的get、set、config等请求都会在这个变量里中的所体现。我们先打开redis-cli的客户端，发送一个set指令看看，看我们的程序是否可能监听到。

![5.png](https://image.3001.net/images/20180426/15247249193381.png!small)  

我们启动这个基于pcap库的监听程序，画红色圆的地方就是，pcap主循环推给lua脚本的数据。“set a
[www.candylab.net](http://www.candylab.net)”的整个指令的数据内容都在。

![6.png](https://image.3001.net/images/20180426/15247249278242.png!small)  

##  **0x06 总结**

到此我们完成了整个监控程序的执行周期，通过这个工具，所有经过6379端口的数据我们都可以取得到，至于客官们想针对什么样的的reids攻击，写出对应的策略，编写lua插件逻辑就可以了。本身lua的代码实现就不复杂，提供的数据结构操作类似字符串序列这种数据也很方便，代码可以到github上直接下载，如何变动，具体就看各自的需求和各自的策略设计了。简单说，剩下的工作就是用lua写攻击模式的甄别。

