##  背景

 **1\.
本地环境中部署了2台NTA（Suricata）接收内网12台DNS服务器的流量，用于发现DNS请求中存在的安全问题。近一段时间发现2台NTA服务器运行10小时左右就会自动重启Suricata进程，看了一下日志大概意思是说内存不足，需要强制重启释放内存。说起这个问题当时也是花了一些时间去定位。首先DNS这种小包在我这平均流量也就25Mbps，所以大概率不是因为网卡流量过大而导致的。继续定位，由于我们这各个应用服务器会通过内网域名的形式进行接口调用，所以DNS请求量很大。Kibana上看了一下目前dns_type:
query事件的数据量320,000,000/天 ~ 350,000,000/天（这仅仅是dns_type: query数据量，dns_type:
answer数据量也超级大）。由于Suricata不能在数据输出之前对指定域名进行过滤，这一点确实很傻，必须吐槽。当时的规避做法就是只保留dns_type:
query事件，既保证了Suricata的正常运行也暂时满足了需求。**

2\.
近一段时间网站的某个上传接口被上传了包含恶意Payload的jpg与png。虽然Suricata有检测到，但也延伸了新的需求，如何判断文件是否上传成功以及文件还原与提取HASH。虽然这两点Suricata自身都可以做，但是有一个弊端不得不说。例如Suricata只要开启file_info就会对所有支持文件还原的协议进行HASH提取。由于我们是电商，外部访问的数据量会很大，Suricata默认不支持过滤，针对用户访问的HTML网页这种也会被计算一个HASH，这个量就非常的恐怖了。

**总结：** 针对以上2个问题，我需要的是一个更加灵活的NTA框架，下面请来本次主角 - Zeek。

##  需求

> 1\. 过滤内部DNS域名，只保留外部DNS域名的请求与响应数据；
>
> 2\. 更灵活的文件还原与提取HASH;

##  实现

1\. 过滤本地DNS请求

###  **DNS脚本 - dns-filter_external.zeek**

    
    
    redef Site::local_zones = {"canon88.github.io", "baidu.com", "google.com"};
    
    function dns_filter(rec: DNS::Info): bool
      {
      return ! Site::is_local_name(rec$query);
      }
    
    redef Analyzer::disable_all = T
    
    event zeek_init()
      {
      Analyzer::enable_analyzer(Analyzer::ANALYZER_VXLAN);
      Analyzer::enable_analyzer(Analyzer::ANALYZER_DNS);
      Log::remove_default_filter(DNS::LOG);
      local filter: Log::Filter = [$name="dns_split", $path="/data/logs/zeek/dns_remotezone", $pred=dns_filter];
      Log::add_filter(DNS::LOG, filter);
      }

**简述**

1\. 通过 **Site::local_zones** 定义一个内部的域名，这些域名默认都是我们需要过滤掉的。例如，在我的需求中，多为内网的域名；

2\. 优化性能， 只开启DNS流量解析。由于这2台NTA只负责解析DNS流量，为了保留针对域名特征检测的能力，我选择了 **Suricata** 与
**Zeek** 共存，当然 **Zeek** 也可以做特征检测，只是我懒。。。通过
**Analyzer::enable_analyzer(Analyzer::ANALYZER_DNS);** 指定了只对DNS流量进行分析；

3\. 过滤日志并输出；

**样例**

    
    
    {
      "ts": 1589175829.994196,
      "uid": "CPRxOZ2RtkPYhjz8R9",
      "id.orig_h": "1.1.1.1",
      "id.orig_p": 40411,
      "id.resp_h": "2.2.2.2",
      "id.resp_p": 53,
      "proto": "udp",
      "trans_id": 696,
      "rtt": 1.3113021850585938e-05,
      "query": "graph.facebook.com",
      "qclass": 1,
      "qclass_name": "C_INTERNET",
      "qtype": 1,
      "qtype_name": "A",
      "rcode": 0,
      "rcode_name": "NOERROR",
      "AA": false,
      "TC": false,
      "RD": true,
      "RA": true,
      "Z": 0,
      "answers": [
        "api.facebook.com",
        "star.c10r.facebook.com",
        "157.240.22.19"
      ],
      "TTLs": [
        540,
        770,
        54
      ],
      "rejected": false,
      "event_type": "dns"
    }

**总结**

当采用Zeek过滤了DNS请求后，现在每天的DNS数据量 **6,300,000/天 ~ 6,800,000/天** （query +
answer），对比之前的数据量 **320,000,000/天 ~ 350,000,000/天**
（query）。数据量减少很明显，同时也减少了后端ES存储的压力。

**Zeek DNS （query + answer）**

**![](https://image.3001.net/images/20200513/1589350615_5ebb90d729e16.png!small)**

 **Suricata DNS （query）**

**![](https://image.3001.net/images/20200513/1589350631_5ebb90e738f14.png!small)**

2\. 更灵活的文件还原与提取文件HASH

###  **文件还原脚本 - file_extraction.zeek**

Demo脚本，语法并不优雅，切勿纠结。

    
    
    @load base/frameworks/files/main
    @load base/protocols/http/main
    
    module Files;
    
    export {
        redef record Info += {
            hostname:         string &log &ampoptional
            proxied:          set[string] &log &ampoptional
            url:              string &log &ampoptional
            method:           string &log &ampoptional
            true_client_ip:   string &log &ampoptional
            logs:             bool &log &ampoptional
        };
    
        option http_info = T;
    }
    
    redef FileExtract::prefix = "/data/logs/zeek/extracted_files/";
    
    global mime_to_ext: table[string] of string = {
        ["text/plain"] = "txt",
        ["application/x-executable"] = "",
        ["application/x-dosexec"] = "exe",
        ["image/jpeg"] = "jpg",
        ["image/png"] = "png",
        ["application/pdf"] = "pdf",
        ["application/java-archive"] = "jar",
        ["application/x-java-applet"] = "jar",
        ["application/x-java-jnlp-file"] = "jnlp",
        ["application/msword"] = "doc",
        ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"] = "docs",
        ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"] = "xlsx",
        ["application/vnd.openxmlformats-officedocument.presentationml.presentation"] = "pptx",
    };
    
    global file_analyzer: table[string] of bool = {
        ["Extraction"] = T,
    };
    
    global http_method: set[string] = {
        "GET",
        "POST",
    };
    
    global http_hostname: set[string] = {
      "canon88.github.io",
    };
    
    global http_uri: set[string] = {
      "/index.php",
      "/account.php",
    };
    
    function files_filter(rec: Files::Info): bool
        {
        return rec?$logs;
        }
    
    event zeek_init()
        {
        Log::remove_default_filter(Files::LOG);
        local filter: Log::Filter = [$name="file_extraction", $path="/data/logs/zeek/file_extraction", $pred=files_filter];
        Log::add_filter(Files::LOG, filter);
        }
    
    event file_sniff(f: fa_file, meta: fa_metadata) &priority=3
        {
        if ( f$source != "HTTP" )
            return;
    
        if ( ! f$http?$method )
            return;
    
        if ( f$http$method !in http_method )
            return;
    
        if ( ! f$http?$host )
            return;
    
        if ( f$http$host !in http_hostname )
            return;
    
        if ( ! meta?$mime_type )
            return;
    
        if ( meta$mime_type !in mime_to_ext )
            return;
    
        f$info$logs = T;
    
        if ( file_analyzer["Extraction"] )
            {
            local fname = fmt("%s-%s.%s", f$source, f$id, mime_to_ext[meta$mime_type]);
            Files::add_analyzer(f, Files::ANALYZER_EXTRACT, [$extract_filename=fname]);
            }
    
        Files::add_analyzer(f, Files::ANALYZER_MD5);
    
        if ( http_info )
            {
            if ( f$http?$host )
                f$info$hostname = f$http$host;
            if ( f$http?$proxied )
                f$info$proxied = f$http$proxied;
            if ( f$http?$method )
                f$info$method = f$http$method;
            if ( f$http?$uri )
                f$info$url = f$http$uri;
            if ( f$http?$true_client_ip )
                f$info$true_client_ip = f$http$true_client_ip;
            }
        }
    
    
    event file_state_remove(f: fa_file)
        {
            if ( !f$info?$extracted || !f$info?$md5 || FileExtract::prefix == "" || !f$info?$logs )
                return;
    
            local orig = f$info$extracted;
            local split_orig = split_string(f$info$extracted, /\./);
            local extension = split_orig[|split_orig|-1];
            local ntime = fmt("%D", network_time());
            local ndate = sub_bytes(ntime, 1, 10);
            local dest_dir = fmt("%s%s", FileExtract::prefix, ndate);
            mkdir(dest_dir);
            local dest = fmt("%s/%s.%s", dest_dir, f$info$md5, extension);
            local cmd = fmt("mv %s/%s %s", FileExtract::prefix, orig, dest);
            when ( local result = Exec::run([$cmd=cmd]) )
            {
    
            }
            f$info$extracted = dest;
        }

**简述**

> 1\. 支持针对指定hostname，method，url，文件头进行hash的提取以及文件还原；
>
> 2\. 默认文件还原按照年月日进行数据的存储，保存名字按照MD5名称命名；
>
> 3\. 丰富化了文件还原的日志，增加HTTP相关字段；

**样例**

    
    
    {
      "ts": 1588891497.173108,
      "fuid": "FhOGNc2zDdlF3AP5c",
      "tx_hosts": [
        "1.1.1.1"
      ],
      "rx_hosts": [
        "2.2.2.2"
      ],
      "conn_uids": [
        "CItQs61wvvtPqSB0Ub"
      ],
      "source": "HTTP",
      "depth": 0,
      "analyzers": [
        "MD5",
        "SHA1",
        "EXTRACT"
      ],
      "mime_type": "image/png",
      "duration": 0,
      "local_orig": true,
      "is_orig": false,
      "seen_bytes": 353,
      "total_bytes": 353,
      "missing_bytes": 0,
      "overflow_bytes": 0,
      "timedout": false,
      "md5": "fd0229d400049449084b3864359c445a",
      "sha1": "d836d3f06c0fc075cf0f5d95f50b79cac1dac97d",
      "extracted": "/data/logs/zeek/extracted_files/2020-05-07/fd0229d400049449084b3864359c445a.png",
      "extracted_cutoff": false,
      "hostname": "canon88.github.io",
      "proxied": [
        "TRUE-CLIENT-IP -> 3.3.3.3",
        "X-FORWARDED-FOR -> 4.4.4.4"
      ],
      "url": "/image/close.png",
      "method": "GET",
      "true_client_ip": "3.3.3.3",
      "logs": true
    }

**这是其中一个包含恶意Payload还原出的图片样例**

    
    
    $ ll /data/logs/zeek/extracted_files/
    total 89916
    drwxr-xr-x 10 root root      150 May 11 06:14 ./
    drwxr-xr-x  4 root root       67 May 11 06:00 ../
    drwxr-xr-x  2 root root       50 May  5 07:54 2020-05-04/
    drwxr-xr-x  2 root root     4096 May  5 23:51 2020-05-05/
    drwxr-xr-x  2 root root   671744 May  6 23:41 2020-05-06/
    drwxr-xr-x  2 root root     4096 May  7 22:44 2020-05-07/
    drwxr-xr-x  2 root root   741376 May  8 23:59 2020-05-08/
    drwxr-xr-x  2 root root 23425024 May  9 23:59 2020-05-09/
    drwxr-xr-x  2 root root 25047040 May 10 23:59 2020-05-10/
    drwxr-xr-x  2 root root 24846336 May 11 06:14 2020-05-11/
    
    $ xxd /data/logs/zeek/extracted_files/2020-05-07/884d9474180e5b49f851643cb2442bce.jpg
    00000000: 8950 4e47 0d0a 1a0a 0000 000d 4948 4452  .PNG........IHDR
    00000010: 0000 003c 0000 003c 0806 0000 003a fcd9  ...<...<.....:..
    00000020: 7200 0000 1974 4558 7453 6f66 7477 6172  r....tEXtSoftwar
    00000030: 6500 4164 6f62 6520 496d 6167 6552 6561  e.Adobe ImageRea
    00000040: 6479 71c9 653c 0000 0320 6954 5874 584d  dyq.e<... iTXtXM
    00000050: 4c3a 636f 6d2e 6164 6f62 652e 786d 7000  L:com.adobe.xmp.
    ..........
    00001030: 8916 ce5f 7480 2f38 c073 69f1 5c14 83fb  ..._t./8.si.\...
    00001040: aa9d 42a3 8f4b ff05 e012 e04b 802f 01be  ..B..K.....K./..
    00001050: 04b8 91c7 ff04 1800 bcae 819f d1da 1896  ................
    00001060: 0000 0000 4945 4e44 ae42 6082 3c3f 7068  ....IEND.B`.<?ph
    00001070: 7020 7068 7069 6e66 6f28 293b 3f3e 1a    p phpinfo();?>.

**总结**

通过Zeek脚本扩展后，可以“ **随意所欲** ”的获取各种类型文件的Hash以及定制化的进行文件还原。

##  **头脑风暴**

当获取文件上传的Hash之后，可以尝试扩展出以下2个安全事件：

1\. 判断文件是否上传成功。

通常第一时间会需要定位文件是否上传成功，若上传成功需要进行相关的事件输出，这个时候我们可以通过采用HIDS进行文件落地事件的关联。

2\. 关联杀毒引擎/威胁情报。

将第一个关联好的事件进行Hash的碰撞，最常见的是将HASH送到VT或威胁情报。

这里以Wazuh事件为例，将Zeek的文件还原事件与Wazuh的新增文件事件进行关联，关联指标采用Hash。

a. Zeek 事件

    
    
    {
      "ts": 1589158812.471443,
      "fuid": "FBkqzM2AFg0jrioji6",
      "tx_hosts": [
        "1.1.1.1"
      ],
      "rx_hosts": [
        "2.2.2.2"
      ],
      "conn_uids": [
        "CcOyQo2ziEuoLBNIb9"
      ],
      "source": "HTTP",
      "depth": 0,
      "analyzers": [
        "SHA1",
        "EXTRACT",
        "MD5",
        "DATA_EVENT"
      ],
      "mime_type": "text/plain",
      "duration": 0,
      "local_orig": true,
      "is_orig": true,
      "seen_bytes": 31,
      "total_bytes": 31,
      "missing_bytes": 0,
      "overflow_bytes": 0,
      "timedout": false,
      "md5": "37a74f452f1c49854a2951fd605687c5",
      "extracted": "/data/logs/zeek/extracted_files/2020-05-11/37a74f452f1c49854a2951fd605687c5.txt",
      "extracted_cutoff": false,
      "hostname": "canon88.github.io",
      "proxied": [
        "X-FORWARDED-FOR -> 3.3.3.3",
        "TRUE-CLIENT-IP -> 4.4.4.4"
      ],
      "url": "/index.php",
      "method": "POST",
      "true_client_ip": "4.4.4.4",
      "logs": true
    }

b. Wazuh 事件

![](https://image.3001.net/images/20200513/1589350997_5ebb92555c2f0.png!small)

***本文作者：Shell.，转载请注明来自FreeBuf.COM**

