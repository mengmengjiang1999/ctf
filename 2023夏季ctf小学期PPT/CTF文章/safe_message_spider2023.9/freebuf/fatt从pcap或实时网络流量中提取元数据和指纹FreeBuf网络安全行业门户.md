**![fatt：从pcap或实时网络流量中提取元数据和指纹](https://image.3001.net/images/20190604/1559608520_5cf5bcc826a24.png!small)**

**fatt是一个用于从pcap或实时网络流量中提取元数据和指纹（如[JA3](https://github.com/salesforce/ja3)和[HASSH](https://github.com/salesforce/hassh)）的python脚本。其主要用例是监视蜜罐，但你也可以用于其他用例，例如网络取证分析。fatt当前支持的系统包括Linux，macOS和Windows。**

注意，fatt使用pyshark（tshark的python包装器），因此性能并不是很好！但这问题不大，因为显然这不是你在生产中使用的工具。你可以使用其他网络分析工具（如[Bro/Zeek](https://github.com/bro/bro)，[Suricata](https://github.com/OISF/suricata)或[Netcap](https://github.com/dreadl0ck/netcap)）来处理那些更为严重的用例。
[Joy](https://github.com/cisco/joy)则是另一个非常不错的用于捕获和分析网络流数据的工具。

除此之外，我正在开发基于go的fatt版本它的处理速度会更快，你可以在基于gopacket的工具中使用它的库，例如packetbeat。我发布了其gQUIC库（[QUICk](https://github.com/0x4D31/quick)）的初始版本。

## 特性

> 协议支持：SSL/TLS，SSH，RDP，HTTP，gQUIC。
>
> 即将添加：IETF QUIC，MySQL，MSSQL 等。

## 指纹

> JA3：TLS client/server 指纹
>
> HASSH：SSH client/server 指纹
>
> RDFP：我的标准RDP安全协议的实验性RDP指纹（注意其他RDP安全模式使用TLS并且可以使用JA3进行指纹识别） HTTP header 指纹
> gQUIC/iQUIC 指纹（即将添加） JSON 输出

## 安装

 **安装 tshark**

你需要先安装[tshark](https://github.com/wireshark/wireshark)。确保你当前的版本为v2.9.0或更高版本。Tshark/Wireshak从版本v2.9.0将'ssl'重命名为'tls'，fatt基于新版本的tshark编写。

 **安装依赖**

    
    
    cd fatt/
    pip3 install pipenv
    pipenv install

或者如果你不想使用虚拟环境，只需安装pyshark：

    
    
    pip3 install pyshark==0.4.2.2

要激活virtualenv，请运行pipenv shell：

    
    
    $ pipenv shell
    Launching subshell in virtual environment…
    bash-3.2$  . /Users/adel/.local/share/virtualenvs/fatt-ucJHMzzt/bin/activate
    (fatt-ucJHMzzt) bash-3.2$ python3 fatt.py -h

或者，使用pipenv run在virtualenv中运行命令：

    
    
    $ pipenv run python3 fatt.py -h

输出：

    
    
    usage: fatt.py [-h] [-r READ_FILE] [-d READ_DIRECTORY] [-i INTERFACE]
                   [-fp [{tls,ssh,rdp,http,gquic} [{tls,ssh,rdp,http,gquic} ...]]]
                   [-da DECODE_AS] [-f BPF_FILTER] [-j] [-o OUTPUT_FILE]
                   [-w WRITE_PCAP] [-p]
    
    A python script for extracting network fingerprints
    
    optional arguments:
      -h, --help            show this help message and exit
      -r READ_FILE, --read_file READ_FILE
                            pcap file to process
      -d READ_DIRECTORY, --read_directory READ_DIRECTORY
                            directory of pcap files to process
      -i INTERFACE, --interface INTERFACE
                            listen on interface
      -fp [{tls,ssh,rdp,http,gquic} [{tls,ssh,rdp,http,gquic} ...]], --fingerprint [{tls,ssh,rdp,http,gquic} [{tls,ssh,rdp,http,gquic} ...]]
                            protocols to fingerprint. Default: all
      -da DECODE_AS, --decode_as DECODE_AS
                            a dictionary of {decode_criterion_string:
                            decode_as_protocol} that is used to tell tshark to
                            decode protocols in situations it wouldn't usually.
      -f BPF_FILTER, --bpf_filter BPF_FILTER
                            BPF capture filter to use (for live capture only).'
      -j, --json_logging    log the output in json format
      -o OUTPUT_FILE, --output_file OUTPUT_FILE
                            specify the output log file. Default: fatt.log
      -w WRITE_PCAP, --write_pcap WRITE_PCAP
                            save the live captured packets to this file
      -p, --print_output    print the output

## 使用

 **实时网络流量捕获：**

    
    
    $ python3 fatt.py -i en0 --print_output --json_logging
    192.168.1.10:59565 -> 192.168.1.3:80 [HTTP] hash=598c34a2838e82f9ec3175305f233b89 userAgent="Spotify/109600181 OSX/0 (MacBookPro14,3)"
    192.168.1.10:59566 -> 13.237.44.5:22 [SSH] hassh=ec7378c1a92f5a8dde7e8b7a1ddf33d1 client=SSH-2.0-OpenSSH_7.9
    13.237.44.5:22 -> 192.168.1.10:59566 [SSH] hasshS=3f0099d323fed5119bbfcca064478207 server=SSH-2.0-babeld-80573d3e
    192.168.1.10:59584 -> 93.184.216.34:443 [TLS] ja3=e6573e91e6eb777c0933c5b8f97f10cd serverName=example.com
    93.184.216.34:443 -> 192.168.1.10:59584 [TLS] ja3s=ae53107a2e47ea20c72ac44821a728bf
    192.168.1.10:59588 -> 192.168.1.3:80 [HTTP] hash=598c34a2838e82f9ec3175305f233b89 userAgent="Spotify/109600181 OSX/0 (MacBookPro14,3)"
    192.168.1.10:59601 -> 216.58.196.142:80 [HTTP] hash=d6662c018cd4169689ddf7c6c0f8ca1b userAgent="curl/7.54.0"
    216.58.196.142:80 -> 192.168.1.10:59601 [HTTP] hash=c5241aca9a7c86f06f476592f5dda9a1 server=gws
    192.168.1.10:54387 -> 216.58.203.99:443 [QUIC] UAID="Chrome/74.0.3729.169 Intel Mac OS X 10_14_5" SNI=clientservices.googleapis.com AEAD=AESG KEXS=C255

JSON 输出：

    
    
    $ cat fatt.log
    {"timestamp": "2019-05-28T03:41:25.415086", "sourceIp": "192.168.1.10", "destinationIp": "192.168.1.3", "sourcePort": "59565", "destinationPort": "80", "protocol": "http", "http": {"requestURI": "/DIAL/apps/com.spotify.Spotify.TVv2", "requestFullURI": "http://192.168.1.3/DIAL/apps/com.spotify.Spotify.TVv2", "requestVersion": "HTTP/1.1", "requestMethod": "GET", "userAgent": "Spotify/109600181 OSX/0 (MacBookPro14,3)", "clientHeaderOrder": "connection,accept_encoding,host,user_agent", "clientHeaderHash": "598c34a2838e82f9ec3175305f233b89"}}
    {"timestamp": "2019-05-28T03:41:26.099574", "sourceIp": "13.237.44.5", "destinationIp": "192.168.1.10", "sourcePort": "22", "destinationPort": "59566", "protocol": "ssh", "ssh": {"server": "SSH-2.0-babeld-80573d3e", "hasshServer": "3f0099d323fed5119bbfcca064478207", "hasshServerAlgorithms": "curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256;chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr,aes256-cbc,aes192-cbc,aes128-cbc;hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1;none,zlib,zlib@openssh.com", "hasshVersion": "1.0", "skex": "curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256", "seastc": "chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr,aes256-cbc,aes192-cbc,aes128-cbc", "smastc": "hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1", "scastc": "none,zlib,zlib@openssh.com", "slcts": "[Empty]", "slstc": "[Empty]", "seacts": "chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr,aes256-cbc,aes192-cbc,aes128-cbc", "smacts": "hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1", "scacts": "none,zlib,zlib@openssh.com", "sshka": "ssh-dss,rsa-sha2-512,rsa-sha2-256,ssh-rsa"}}
    {"timestamp": "2019-05-28T03:41:26.106737", "sourceIp": "192.168.1.10", "destinationIp": "13.237.44.5", "sourcePort": "59566", "destinationPort": "22", "protocol": "ssh", "ssh": {"client": "SSH-2.0-OpenSSH_7.9", "hassh": "ec7378c1a92f5a8dde7e8b7a1ddf33d1", "hasshAlgorithms": "curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group14-sha256,diffie-hellman-group14-sha1,ext-info-c;chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com;umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1;none,zlib@openssh.com,zlib", "hasshVersion": "1.0", "ckex": "curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group14-sha256,diffie-hellman-group14-sha1,ext-info-c", "ceacts": "chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com", "cmacts": "umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1", "ccacts": "none,zlib@openssh.com,zlib", "clcts": "[Empty]", "clstc": "[Empty]", "ceastc": "chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com", "cmastc": "umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1", "ccastc": "none,zlib@openssh.com,zlib", "cshka": "rsa-sha2-512-cert-v01@openssh.com,rsa-sha2-256-cert-v01@openssh.com,ssh-rsa-cert-v01@openssh.com,rsa-sha2-512,rsa-sha2-256,ssh-rsa,ecdsa-sha2-nistp256-cert-v01@openssh.com,ecdsa-sha2-nistp384-cert-v01@openssh.com,ecdsa-sha2-nistp521-cert-v01@openssh.com,ssh-ed25519-cert-v01@openssh.com,ecdsa-sha2-nistp256,ecdsa-sha2-nistp384,ecdsa-sha2-nistp521,ssh-ed25519"}}
    {"timestamp": "2019-05-28T03:41:36.762811", "sourceIp": "192.168.1.10", "destinationIp": "93.184.216.34", "sourcePort": "59584", "destinationPort": "443", "protocol": "tls", "tls": {"serverName": "example.com", "ja3": "e6573e91e6eb777c0933c5b8f97f10cd", "ja3Algorithms": "771,49200-49196-49192-49188-49172-49162-159-107-57-52393-52392-52394-65413-196-136-129-157-61-53-192-132-49199-49195-49191-49187-49171-49161-158-103-51-190-69-156-60-47-186-65-49170-49160-22-10-255,0-11-10-13-16,29-23-24,0", "ja3Version": "771", "ja3Ciphers": "49200-49196-49192-49188-49172-49162-159-107-57-52393-52392-52394-65413-196-136-129-157-61-53-192-132-49199-49195-49191-49187-49171-49161-158-103-51-190-69-156-60-47-186-65-49170-49160-22-10-255", "ja3Extensions": "0-11-10-13-16", "ja3Ec": "29-23-24", "ja3EcFmt": "0"}}
    {"timestamp": "2019-05-28T03:41:36.920935", "sourceIp": "93.184.216.34", "destinationIp": "192.168.1.10", "sourcePort": "443", "destinationPort": "59584", "protocol": "tls", "tls": {"ja3s": "ae53107a2e47ea20c72ac44821a728bf", "ja3sAlgorithms": "771,49199,65281-0-11-16", "ja3sVersion": "771", "ja3sCiphers": "49199", "ja3sExtensions": "65281-0-11-16"}}
    {"timestamp": "2019-05-28T03:41:37.487609", "sourceIp": "192.168.1.10", "destinationIp": "192.168.1.3", "sourcePort": "59588", "destinationPort": "80", "protocol": "http", "http": {"requestURI": "/DIAL/apps/com.spotify.Spotify.TVv2", "requestFullURI": "http://192.168.1.3/DIAL/apps/com.spotify.Spotify.TVv2", "requestVersion": "HTTP/1.1", "requestMethod": "GET", "userAgent": "Spotify/109600181 OSX/0 (MacBookPro14,3)", "clientHeaderOrder": "connection,accept_encoding,host,user_agent", "clientHeaderHash": "598c34a2838e82f9ec3175305f233b89"}}
    {"timestamp": "2019-05-28T03:41:48.700730", "sourceIp": "192.168.1.10", "destinationIp": "216.58.196.142", "sourcePort": "59601", "destinationPort": "80", "protocol": "http", "http": {"requestURI": "/", "requestFullURI": "http://google.com/", "requestVersion": "HTTP/1.1", "requestMethod": "GET", "userAgent": "curl/7.54.0", "clientHeaderOrder": "host,user_agent,accept", "clientHeaderHash": "d6662c018cd4169689ddf7c6c0f8ca1b"}}
    {"timestamp": "2019-05-28T03:41:48.805393", "sourceIp": "216.58.196.142", "destinationIp": "192.168.1.10", "sourcePort": "80", "destinationPort": "59601", "protocol": "http", "http": {"server": "gws", "serverHeaderOrder": "location,content_type,date,cache_control,server,content_length", "serverHeaderHash": "c5241aca9a7c86f06f476592f5dda9a1"}}
    {"timestamp": "2019-05-28T03:41:58.038530", "sourceIp": "192.168.1.10", "destinationIp": "216.58.203.99", "sourcePort": "54387", "destinationPort": "443", "protocol": "gquic", "gquic": {"tagNumber": "25", "sni": "clientservices.googleapis.com", "uaid": "Chrome/74.0.3729.169 Intel Mac OS X 10_14_5", "ver": "Q043", "aead": "AESG", "smhl": "1", "mids": "100", "kexs": "C255", "xlct": "cd9baccc808a6d3b", "copt": "NSTP", "ccrt": "cd9baccc808a6d3b67f8adc58015e3ff", "stk": "d6a64aeb563a19fe091bc34e8c038b0a3a884c5db7caae071180c5b739bca3dd7c42e861386718982fbe6db9d1cb136f799e8d10fd5a", "pdmd": "X509", "ccs": "01e8816092921ae8", "scid": "376976b980c73b669fea57104fb725c6"}}
    Packet capture file (pcap):

 **数据包捕获文件（pcap）：**

让我们来看看最近的CVE-2019-0708 RDP漏洞（BlueKeep）捕获的Metasploit auxiliary scanner流量。

    
    
    $ python3 fatt.py -r RDP/cve-2019-0708_metasploit_aux.pcap -p -j; cat fatt.log | python -m json.tool
    192.168.1.10:39079 -> 192.168.1.20:3389 [RDP] rdfp=525e1cb209280b81c24f1668dd55ed94 cookie="mstshash=user0" req_protocols=0x00000000
    
    {
        "destinationIp": "192.168.1.20",
        "destinationPort": "3389",
        "protocol": "rdp",
        "rdp": {
            "channelDefArray": {
                "0": {
                    "name": "cliprdr",
                    "options": "c0a00000"
                },
                "1": {
                    "name": "MS_T120",
                    "options": "80800000"
                },
                "2": {
                    "name": "rdpsnd",
                    "options": "c0000000"
                },
                "3": {
                    "name": "snddbg",
                    "options": "c0000000"
                },
                "4": {
                    "name": "rdpdr",
                    "options": "80800000"
                }
            },
            "clientBuild": "2600",
            "clientDigProductId": "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
            "clientName": "x1810",
            "clientProductId": "1",
            "clusterFlags": "09000000",
            "colorDepth": "0x0000ca01",
            "connectionType": "0",
            "cookie": "mstshash=user0",
            "desktopHeight": "600",
            "desktopWidth": "800",
            "earlyCapabilityFlags": "1",
            "encryptionMethods": "03000000",
            "extEncMethods": "00000000",
            "highColorDepth": "0x00000018",
            "keyboardFuncKey": "12",
            "keyboardLayout": "1033",
            "keyboardSubtype": "0",
            "keyboardType": "4",
            "pad1Octet": "00",
            "postbeta2ColorDepth": "0x0000ca01",
            "rdfp": "525e1cb209280b81c24f1668dd55ed94",
            "rdfpAlgorithms": "4;8;09000000;03000000;00000000;cliprdr:c0a00000;MS_T120:80800000;rdpsnd:c0000000;snddbg:c0000000;rdpdr:80800000",
            "rdfpVersion": "0.2",
            "requestedProtocols": "0x00000000",
            "sasSequence": "43523",
            "serialNumber": "0",
            "supportedColorDepths": "0x00000007",
            "verMajor": "4",
            "verMinor": "8"
        },
        "sourceIp": "192.168.1.10",
        "sourcePort": "39079",
        "timestamp": "2019-05-23T03:51:25.438445"
    }

让我们用另一个CVE-2019-0708 PoC测试它：

    
    
    $ python3 fatt.py -r RDP/cve-2019-0708_poc.pcap -p -j; cat fatt.log | python -m json.tool
    192.168.1.10:54303 -> 192.168.1.20:3389 [RDP] req_protocols=0x00000001
    
    {
        "destinationIp": "192.168.1.20",
        "destinationPort": "3389",
        "protocol": "rdp",
        "rdp": {
            "requestedProtocols": "0x00000001"
        },
        "sourceIp": "192.168.1.10",
        "sourcePort": "54303",
        "timestamp": "2019-05-23T18:41:42.572758"
    }

这次我们没有看到RDP ClientInfo消息，这是因为PoC使用TLS（而不是标准的RDP安全协议）。因此我们只能看到Negotiation
Request消息，但如果你将数据包解码为TLS，则可以看到TLS clientHello和JA3指纹。以下将特定端口解码为另一个协议：

    
    
    $ python3 fatt.py -r RDP//cve-2019-0708_poc.pcap -p -j --decode_as '{"tcp.port==3389": "tls"}'
    192.168.1.10:50026 -> 192.168.1.20:3389 [TLS] ja3=67e3d18fd9dddbbc8eca65f7dedac674 serverName=192.168.1.20
    192.168.1.20:3389 -> 192.168.1.10:50026 [TLS] ja3s=649d6810e8392f63dc311eecb6b7098b
    
    $ cat fatt.log
    {"timestamp": "2019-05-23T17:21:56.056200", "sourceIp": "192.168.1.10", "destinationIp": "192.168.1.20", "sourcePort": "50026", "destinationPort": "3389", "protocol": "tls", "tls": {"serverName": "192.168.1.20", "ja3": "67e3d18fd9dddbbc8eca65f7dedac674", "ja3Algo
    
    
    、rithms": "771,49196-49195-49200-49199-159-158-49188-49187-49192-49191-49162-49161-49172-49171-57-51-157-156-61-60-53-47-10-106-64-56-50-19-5-4,0-5-10-11-13-35-23-65281,29-23-24,0", "ja3Version": "771", "ja3Ciphers": "49196-49195-49200-49199-159-158-49188-49187-49192-49191-49162-49161-49172-49171-57-51-157-156-61-60-53-47-10-106-64-56-50-19-5-4", "ja3Extensions": "0-5-10-11-13-35-23-65281", "ja3Ec": "29-23-24", "ja3EcFmt": "0"}}
    {"timestamp": "2019-05-23T17:21:56.059333", "sourceIp": "192.168.1.20", "destinationIp": "192.168.1.10", "sourcePort": "3389", "destinationPort": "50026", "protocol": "tls", "tls": {"ja3s": "649d6810e8392f63dc311eecb6b7098b", "ja3sAlgorithms": "771,49192,23-65281", "ja3sVersion": "771", "ja3sCiphers": "49192", "ja3sExtensions": "23-65281"}}

***参考来源：[GitHub](https://github.com/0x4D31/fatt)，FB小编secist编译，转载请注明来自FreeBuf.COM
**  

