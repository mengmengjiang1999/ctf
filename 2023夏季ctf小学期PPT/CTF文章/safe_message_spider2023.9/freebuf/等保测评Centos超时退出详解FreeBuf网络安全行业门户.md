## 一、说明

**等保测评主机测评中需要查询主机的超时退出配置，具体在Centos中的话，主要有两种方式可以实现超时退出的功能。其实这方面的资料很多，但是仍然存在一些地方没有说清楚（sshd_config的一个参数），所以本文的目的之一就是把那些问题说清楚。**

> 注：我使用的是Centos6  
>

另外本文也顺便说一说在linux系统中，查询配置的一个注意点。

## 二、设置TMOUT方式

这个是比较通用、简单的方式，通过设置TMOUT，就可以至少对本地tty登录和远程使用ssh登录的用户起作用，但应该对图形化界面无效，当然进入图形化界面你再打开终端，对于打开的终端也是起作用的。

### 2.1. 实现方式

在/etc/profile、~/.bashrc、~/.bash_profile等文件的最后加入export
TMOUT=900语句即可（单位是秒），然后想要不重新登录就起效就，还需要用source命令解析上述文件。

上述文件中，/etc/profile针对所有用户其效果，而~/.bashrc、~/.bash_profile则只对当前用户其效果，实际上从文件位置就能看出来。

### 2.2. 具体查询方式

从上面可以知道，理论上可以在好几个地方对TMOUT进行配置，不过一般应该是在/etc/profile这个文件中对所有用户进行设置，可能有极个别的会单独为每个用户配置超时时间。

所以直接查看/etc/profile文件内容，然后再用echo $TMOUT语句看看运行环境中的TMOUT变量到底是多少。

### 2.3. 配置查询的注意点

这里多说一点，在查配置时，对于linux系统最好是 **配置文件** 以及 **实际情况** 一块查。

为什么要一块查？

因为配置文件里写了不代表就起效了，比如/etc/profile修改后需要用source命令才能起效。另外，配置文件中的配置即使起效了，但未必就等同于现在实际执行的规则。

比如iptables的规则可以用命令动态修改，当然如果没有使用命令持久化（也就是将当前规则存入iptables的配置文件中）的话，重启iptables服务那些临时的规则就没了。

所以同样的，配置文件里啥都没写，不代表现在运行的环境中没有规则，比如iptables的规则可以用命令临时添加进来。

所以如果想在测评的时候更全面的了解情况，最好就是一块查。

## 三、修改sshd_config文件方式

一般来说，远程对linux服务器进行管理都是通过ssh协议，所以对sshd_config文件进行配置，也是一种方法，虽然只对通过ssh登录的所有用户有效。

记住修改完sshd_config文件后需要重启才能生效。

在sshd_config文件中有两个参数，分别是ClientAliveInterval和ClientAliveCountMax。

这里网上好像没说清楚，这里根据ClientAliveCountMax的取值是不是0，会有两种效果。

### 3.1. ClientAliveCountMax的值是0

这种情况下，就是我们想要的操作超时自动退出的效果，也就是当客户端多久没有操作，服务器端就直接断开ssh连接。

这个“多久”当然就是由ClientAliveInterval的值来决定，它的单位是秒。

比如ClientAliveInterval是600，ClientAliveCountMax是0，则代表着如果600秒内终端没有操作，则断开ssh连接。

### 3.2. ClientAliveCountMax的值大于0

这种情况下，和我们想要的效果有区别：

> ClientAliveInterval：指定了服务器端向客户端请求消息的时间间隔，默认值是0；
>
>
> ClientAliveCountMax：则指定这种请求服务器端发送后，客户端最多的无响应次数（但网上一般是说服务器端最多向客户端发送这种消息多少次，我觉得不太对），默认值是3。

如果ClientAliveInterval是60，ClientAliveCountMax是1，表面上看它的意思就是如果60s内客户端没有响应，服务器端就会给客户端发送一个请求判断还它存不存在，如果1次也就是60秒都没有任何回复，就断开连接。

所以咋一看上去，和ClientAliveCountMax的值是0时没啥区别，还是60秒后不操作就自动断开不了啊。

但实际上压根不一样，因为当服务器端给客户端发送一个请求判断还它存不存在时，客户端应该是会 **自动回复**
的，同时，ClientAliveCountMax并不是指会发送这种消息多少次，或者好像和这个压根就没关系，它应该是指
**服务器端发送这种请求后，客户端最多的无响应次数** ，而且还得是连续的，因为从源代码里面看（见下文），只要有一次正常相应，这个次数就会被清空。

也就是说， **这里判断的应该是客户端那边网络有没有出现问题，比如断线了之类的** 。

因为只要网络正常，客户端这边永远会自动回复服务器端发送过来的请求，则这个计数永远达不到限定的阈值1，也永远不会自动退出（理想情况下啊），和你有没有进行操作没有任何关系……

我自己测试过，将ClientAliveInterval设置为60，ClientAliveCountMax设置1，然后我一直不操作，同时我把xshell里保持活动状态的选项关掉：  
![图片.png](https://image.3001.net/images/20190717/1563344579_5d2ebec32bf41.png!small)

结果就是到了60秒后根本不会自动退出……

然后我又把ClientAliveInterval和ClientAliveCountMax都设置成1，结果就是服务器那边每隔1秒就发个消息过来（有消息传输的时候那个箭头会亮）：  
![图片.png](https://image.3001.net/images/20190717/1563344590_5d2ebece4db93.png!small)

要是按照网上的解释，最多只发送1次这种消息就结束会话，那压根解释不通，这都给我发了无数次了……

我跑去看man里的解释，也没看出所以然：

    
    
    ClientAliveCountMax
                 Sets the number of client alive messages (see below) which may be sent without sshd(8) receiving any messages back from the client. If this threshold is reached while client alive messages are being sent, sshd will disconnect the client, terminating the session. It is important to note that the use of client alive messages is very different from TCPKeepAlive (below). The client alive messages are sent through the encrypted channel and therefore will not be spoofable. The TCP keepalive option enabled by TCPKeepAlive is spoofable.  The client alive mechanism is valuable when the client or server depend on knowing when a connection has become inactive. The default value is 3. If ClientAliveInterval (see below) is set to 15, and ClientAliveCountMax is left at the default, unresponsive SSH clients will be disconnected after approximately 45 seconds. This option applies to protocol version 2 only.
    
    ClientAliveInterval
              Sets a timeout interval in seconds after which if no data has been received from the client, sshd(8) will send a message through the encrypted channel to request a response from the client. The default is 0, indicating that these messages will not be sent to the client. This option applies to protocol version 2 only.
    

### 3.3. 源代码解释

于是我就去翻了翻源代码，不过我对c语言不熟，只能大概猜一猜了（有错误请见谅）：

wait_until_can_do_something函数里有这么一段：

    
    
    	/* Wait for something to happen, or the timeout to expire. */
    	ret = select((*maxfdp)+1, *readsetp, *writesetp, NULL, tvp);
    
    	if (ret == -1) {
    		memset(*readsetp, 0, *nallocp);
    		memset(*writesetp, 0, *nallocp);
    		if (errno != EINTR)
    			error("select: %.100s", strerror(errno));
    	} else {
    		if (ret == 0 && client_alive_scheduled)
    			client_alive_check();
    		if (!compat20 && program_alive_scheduled && fdin_is_tty) {
    			if (!fdout_eof)
    				FD_SET(fdout, *readsetp);
    			if (!fderr_eof)
    				FD_SET(fderr, *readsetp);
    		}
    	}
    

里面的select函数定义是这样的：

    
    
    int select(int maxfdp,fd_set *readfds,fd_set *writefds,fd_set *errorfds,struct timeval*timeout); 

它能够监视我们需要监视的文件描述符的变化情况——读写或是异常，它的最后一个参数timeval*timeout是一个超时时间，如果timeout的值大于0，这就是等待的超时时间，即select在timeout时间内阻塞，超时时间之内有事件到来就返回了，否则在超时后不管怎样一定返回。  

如果timeout的值是null，则代表将select置于阻塞状态，一定等到监视文件描述符集合中某个文件描述符发生变化为止。

而返回值为-1代表出异常了，为0则代表超时时间内，监视的这些文件即没有可写的也没有可读的，换句话说，为0就是意味着客户端那没有任何操作。

在代码中，在一定的条件下，这个timeout的值就是我们设置的ClientAliveInterval的值（如果设置值大于0），如果ClientAliveInterval是0，则timeout的值根据一些条件则为null。

然后根据client_alive_scheduled的值，就有可能调用client_alive_check()，不过如果是使用ssh2协议然后设置了ClientAliveInterval，应该client_alive_scheduled的值就是1，代码如下：

    
    
    if (compat20 &&
    	    max_time_milliseconds == 0 && options.client_alive_interval) {
    		client_alive_scheduled = 1;
    		max_time_milliseconds = options.client_alive_interval * 1000;
    	}
    

client_alive_check的定义如下：

    
    
    static void
    client_alive_check(void)
    {
    	int channel_id;
    
    	/* timeout, check to see how many we have had */
    	if (packet_inc_alive_timeouts() > options.client_alive_count_max) {
    		logit("Timeout, client not responding.");
    		cleanup_exit(255);
    	}
    
    	/*
    	 * send a bogus global/channel request with "wantreply",
    	 * we should get back a failure
    	 */
    	if ((channel_id = channel_find_open()) == -1) {
    		packet_start(SSH2_MSG_GLOBAL_REQUEST);
    		packet_put_cstring("keepalive@openssh.com");
    		packet_put_char(1);	/* boolean: want reply */
    	} else {
    		channel_request_start(channel_id, "keepalive@openssh.com", 1);
    	}
    	packet_send();
    }
    

可以看到如果packet_inc_alive_timeouts()大于options.client_alive_count_max，则就结束了。

而packet_inc_alive_timeouts的定义很简单，就是把累积的timeouts加个1，然后返回。

    
    
    int
    packet_inc_alive_timeouts(void)
    {
    	return ++active_state->keep_alive_timeouts;
    }
    

所以，如果设置的ClientAliveCountMax是0，到这里就直接结束了（0+1>0），不会执行下面的发送请求的代码。

如果(channel_id = channel_find_open())不为-1，应该代表channel没问题的话，就会执行：

    
    
    channel_request_start(channel_id, "keepalive@openssh.com", 1);

channel_request_start中有这么一句：

    
    
    packet_start(SSH2_MSG_CHANNEL_REQUEST);

而SSH2_MSG_CHANNEL_REQUEST应该是绑定了一个函数

    
    
    dispatch_set(SSH2_MSG_CHANNEL_REQUEST, &server_input_channel_req); 

所以就会调用server_input_channel_req函数，server_input_channel_req函数在有这么一段：

    
    
    reply = packet_get_char();
    
    …………
    
    
    if (reply) {
    		packet_start(success ?
    		    SSH2_MSG_CHANNEL_SUCCESS : SSH2_MSG_CHANNEL_FAILURE);
    		packet_put_int(c->remote_id);
    		packet_send();
    	}
    

这里根据success的值又会调用一个函数，其实好像调用的函数是一样的：

    
    
    dispatch_set(SSH2_MSG_CHANNEL_SUCCESS, &server_input_keep_alive);
    dispatch_set(SSH2_MSG_CHANNEL_FAILURE, &server_input_keep_alive);
    dispatch_set(SSH2_MSG_REQUEST_SUCCESS, &server_input_keep_alive);
    dispatch_set(SSH2_MSG_REQUEST_FAILURE, &server_input_keep_alive);
    

都是server_input_keep_alive函数，这个函数的意思就很简单了：

    
    
    static void
    server_input_keep_alive(int type, u_int32_t seq, void *ctxt)
    {
    	debug("Got %d/%u for keepalive", type, seq);
    	/*
    	 * reset timeout, since we got a sane answer from the client.
    	 * even if this was generated by something other than
    	 * the bogus CHANNEL_REQUEST we send for keepalives.
    	 */
    	packet_set_alive_timeouts(0);
    }
    

packet_set_alive_timeouts(0)就是把active_state->keep_alive_timeouts的值设为0，也就是重置了这个计数。

所以饶了一圈，这些代码的意思大概应该是这样，如果客户端在规定时间内没有响应，就先判断未响应次数是否超过设置的值，如果超过就结束。

如果没超过，就把这个次数加1，然后发送一个请求，看看客户端还在不在，如果客户端网络正常（应该会自动回复），就会得到客户端的回复，于是就重置这个未响应计数。

## 四、两个方式的不同

TMOUT方式可以针对所有用户通过本地tty或远程ssh登录时起作用，而修改sshd_config只针对使用ssh登录的用户。

另外一点就是TMOUT判断你有没有在操作，好像是看你有没有输入什么字符然后敲回车执行，你输入正确的命令敲回车执行命令，就算。输入无意义的字符敲回车没有找到可执行的命令，那也算。光输入字符不敲回车就不算，而判断你处于空闲状态，超时就会登出。

而ssh是基于网络来判断，只要客户端对服务器有发送信息，那就算有在操作。

这也是两者的一些细微的不同之处。

 ***本文原创作者：起于凡而非于凡，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

