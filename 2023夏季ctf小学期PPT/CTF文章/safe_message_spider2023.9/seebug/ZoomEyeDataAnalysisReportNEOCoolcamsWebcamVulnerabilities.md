Author: Knownsec 404 ZoomEye Team  
Time: 2018/07/16  
Chinese version: <https://paper.seebug.org/653>

### 1\. Event Summary

Shenzhen NEO Coolcam electronics co. LTD is a new high-tech company that
integrates the R&D, production, and marketing of network digital products.
It's the pioneer in the field of Webcam in China. The company set up a
domestic Camera R&D Center in 2004 and obtained many national patents. The
products were authorized via the national quality supervision department and
the international standard certification like CE and FCC.

As early as August 02, 2017, the security researcher of Bitdefender companies
had pointed out that there are multiple buffer overflow vulnerabilities in
devices such as NIP-22 and Wi-Fi iDoorbell. Thousands of related devices that
leaked on the public network are threatened with potential security threats.
The researchers also provided relevant reports. Around September 2017, we
noticed the latest firmware released on the NEO Coolcam’s official English
website, which fixed the overflow vulnerabilities.

On July 10, 2018, we used ZoomEye Cyberspace Search Engine to locate related
devices and found 650,000 IP history records in the later risk assessment of
IOT devices which are susceptible to this vulnerability. China has the largest
number of devices with the vulnerability, about 167,000. In addition, we have
the following findings:

  * During the year between the release of the official updated version for the firmware by Coolcam and the publication of this article, most of the devices still didn't install the updated firmware. There are following reasons: 1. The target device itself doesn't have an automatic upgrade mechanism. 2. Ordinary users could not realize the existence of vulnerabilities, thus manually update firmware.3. The updated firmware was only published on the official English website. 4. The equipment produced by other OEM manufacturers also had the same vulnerabilities.

  * In the process of target equipment firmware audit, we have found the bypass login vulnerability, which will be presented in the following sections.

This means that a large number of target devices are at risk. The 404 Security
Team has made an in-depth study of a series of buffer overflow vulnerabilities
in NEO Coolcam's NIP-22FX cameras and executed remote code successfully from
the buffer overflow, which confirmed that the vulnerability has the potential
risk of being exploited by black products. Bypass login vulnerability has been
found in the process of an audit at the same time, which is also a serious
threat to user privacy.

### 2\. Vulnerability analysis

#### 2.1 Target equipment information

Device version: Neo Coolcam IPCam NIP-22FX  
Vulnerability binary file: MD5 (ipc_server) = 312d924344364620d85099ed279a5f03  
Firmware version: V7.7.4.1.1-20160701

The main program for web service and RTSP service is the ipc_server file, and
the target system is an ARM, 32-bit small end architecture.

![](https://images.seebug.org/content/images/2018/07/8c410b0c-da96-484f-b96b-4578310521ed.png-w331s)

The mitigation measure of buffer overflow is all closed.

![](https://images.seebug.org/content/images/2018/07/9edc5898-2b3f-4a84-8353-46c77880eddc.png-w331s)

#### 2.2 Bypass login vulnerability

The Webcam Web service is based on HTTP basic authentication. There are three
groups of default credentials which correspond to different permission levels.
This app will only remind you of modifying the default password for your admin
account when installing. Three groups of default credentials and corresponding
operations are as follows:

  1. admin: admin
  2. user: user
  3. guest: guest

![](https://images.seebug.org/content/images/2018/07/ebd5b12d-fd7f-40a6-a3f7-c2470611c0a5.png-w331s)

It is worth mentioning that the user and guest accounts can also view video
streams and most users will not change the default password of these accounts,
which lead to privacy leaks.

![](https://images.seebug.org/content/images/2018/07/c6e28658-f271-4317-bf8e-f4e2dc7d523d.png-w331s)

#### 2.3 Remote Code execution vulnerability based on buffer overflow in web
services (no Authentication required)

##### 2.3.1 Vulnerability detail analysis

The overflow point is located near the address 0x0007DE80. The processing
logic of this function is to call the libs_parsedata function to parse the usr
and pwd in the URL, and then store them in two buffers of this function stack
frame.

![](https://images.seebug.org/content/images/2018/07/1871b44d-34fd-44b2-81e1-80a8ba14fe86.png-w331s)

The prototype of the libs_parsedata function is:  
`int libs_parsedata(int a1, int a2, char *needle, int a4, int a5, int a6){}`

It takes 6 parameters from left to right. The order is:

  * a1: The original string.
  * a2: Length of the original string. 
  * needle: The point to match the beginning of a string to be intercepted.
  * a4: A delimiter used to intercept a string.
  * a6: The target buffer for storing the intercepted string.

The processing logic of this function is to use the string needle and
delimiter a4 to intercept the original string a1. After intercepting, it
writes the intercepted string into the buffer which referred as a6 by the
strncpy() function. The writing’s length is similar to the intercepted string.
Finally, it writes a byte of '\x00'. Because the length of the parameter GET
is controllable, a buffer overflow will occur when an attacker inputs usr or
pwd which oversteps the buffer length.

![](https://images.seebug.org/content/images/2018/07/e5ccc238-4871-4ac2-9ab3-883fbbbe101d.png-w331s)

##### 2.3.2 Exploit analysis

Buffer overflow measures of binary file ipc_server are all closed. This buffer
overflow vulnerability is easy to exploit. In the process, we need to consider
how to avoid the bad characters such as blank characters, &, \x00 and so on.
Blank characters can be replaced by ${IFS}.

The following code is located at the 0x0004E4D8 address in ipc_server:

![](https://images.seebug.org/content/images/2018/07/6019b613-e2a9-4eaf-a8ad-7b4118aa3ed8.png-w331s)

The attackers only need to let the return address point to the address
0x0004E4D8 with the command to be executed, which can lead to remote code
execution from the buffer overflow. The libs_parsedata function will write a
\x00 at the end of the string, so we can exploit two overflow vulnerabilities
to write the return address and the instruction to be executed at the same
time.

The target system doesn’t contain commands such as curl, nc, wget and so on.
So we can redirect the command execution results to the Web directory and then
access the HTTP interface to get the execution result. If the attacker and the
camera are in the same network environment, the attacker also can open the
telnetd service of the targeted system to achieve complete control of the
vulnerable device. Because the file system of the target device is mounted in
the manner of read-write, it has the risk of malicious tampering by an
attacker.

The results on NIP-22FX are as followed:

![](https://images.seebug.org/content/images/2018/07/1845a67a-f258-48f0-a879-9e15d8f3f9d2.png-w331s)

##### 2.3.3 Patch analysis

In the latest version of firmware (V7.7.4.1.1-20170828), a seventh parameter
is added to the libs_parsedata function to control the target buffer writable
length.

![](https://images.seebug.org/content/images/2018/07/e34af116-0653-44b3-8db3-e7b990eb3889.png-w331s)

#### 2.4 RTSP service's remote Code execution vulnerability based on buffer
overflow (no Authentication required)

##### 2.4.1 Vulnerability detail analysis

The overflow point is located at address 0x006C6D4, using the sscanf function
to match key and value in the Authorization: Digest key=”value” in RTSP Header
and saving them on the stack of this function. The stack is overflowed because
both of the lengths cannot be checked.

![](https://images.seebug.org/content/images/2018/07/dcab932c-d813-4592-af97-7db988d687f5.png-w331s)

##### 2.4.2 Vulnerability exploitation analysis

The way to exploit this vulnerability is the same as the method in Section
2.3.2. The attacker can use two overflow vulnerabilities to write the
instruction to be executed and the return address which can easily lead to
remote code execute from buffer overflow. The results in NIP-22FX are as
follows: The telnetd service of the target system is successfully opened by
using the buffer overflow of the RTSP service.

![](https://images.seebug.org/content/images/2018/07/0d13387a-3695-473b-ae6e-bd378e5efbf7.png-w331s)

##### 2.4.3 Patch analysis

In the latest version of firmware (V7.7.4.1.1-20170828), the length constraint
is added to the regular matching expression of sscanf, and the maximum of it
is 255 bytes. The return address cannot be overwritten since there are 296
bytes left between buffer and stack bottom.

![](https://images.seebug.org/content/images/2018/07/71e13de5-2801-40e7-bf8e-eb6022c946d5.png-w331s)

### 3\. The scope within vulnerability impact

We found 651780 IP history data on ZoomEye's Cyberspace Search Engine by using
'keyword' related to CRT NIP-22 HD camera device.

![](https://images.seebug.org/content/images/2018/07/4a1b0a5a-8e8a-4f15-b7ce-ff029bdd8621.png-w331s)

We use the keyword, “Error: username or password error, please input again.”,
to search on the ZoomEye's Cyberspace Search Engine, and get 651780 IP history
record. After verification, there are 58,413 devices still alive.

The distribution of survival equipment countries is as follows. It can be
observed that these vulnerabilities are mainly distributed in Korea, the
United States, China and other countries. Because China's network IP changes
rapidly, the number of relevant surviving devices is more than 5878 in China.

![](https://images.seebug.org/content/images/2018/07/74ccb4db-e14f-48f1-bc79-79d67ee78ce8.png-w331s)

Further statistical analysis of the above surviving devices shows that most of
the devices have at least one default credential. This shows that NEO
Coolcam's HD camera devices generally have default credentials. Attackers can
use the default credentials to access the video stream of the camera. It is
worth mentioning that lots of the surviving devices also have admin: admin
default credentials. The attacker can obtain the administrator identity and
probably take over the target devices completely via uploading elaborate
device firmware.

In the process of data analysis for devices that can be affected by the
vulnerabilities, we found that a large number of devices were sold by OEM.
Device firmware has great homology, and some devices between two different
vendors are just simply changing LOGO.

Using the md5 value of the device page 'web/mainpage.HTML' to distinguish
different OEM, statistical results are as follows:

![](https://images.seebug.org/content/images/2018/07/82417fb7-26f5-4de0-9565-c9855dad08d2.png-w331s)
![](https://images.seebug.org/content/images/2018/07/bd3c1267-5fc6-4105-9925-0fb9bd089640.png-w331s)
![](https://images.seebug.org/content/images/2018/07/29541951-7203-466c-96fa-443378b17ce1.png-w331s)

In addition to the default credential problem, NEO Coolcam's HD camera NIP-22
also has a buffer overflow vulnerability that doesn't require authentication
for Web services and RTSP services. This overflow vulnerability is not
difficult to exploit and the attacker can execute arbitrary commands remotely
based on it. The watchdog process will restart the entire system after an
overflow problem occurs which can also be used by an attacker to cause the
deny of service. Due to the homology of firmware. These two overflow
vulnerabilities are also likely to exist in devices which produced by other
OEM manufacturers.

### 4\. Vulnerability Repair Recommendation

#### 4.1 Users' repair recommendation

To avoid privacy leaks, it is recommended that users repair the series of
vulnerabilities as soon as possible.

First of all, users can connect to the webcam Web management system and modify
the username and password of three sets of default credentials on the
following page.

![](https://images.seebug.org/content/images/2018/07/a7c29028-b2a4-415f-acba-31c0b8150b2c.png-w331s)

What's more, if the device is NEO Coolcam's, it is recommended to download the
latest version of the firmware from the NEO Coolcam's official website and
manually update to repair the two overflow vulnerabilities. If the device is
produced by other OEM vendor, you can try to contact the vendor to update
firmware and isolate the device from the public network.

![](https://images.seebug.org/content/images/2018/07/a72de615-ca1d-4a01-b75c-f4e4be3461cf.png-w331s)

#### 4.2 Manufacturer's repair recommendation

Because this series of vulnerability can affect dozens of OEM vendors at home
and abroad, the vendors in the above list should check again to avoid the
possible vulnerabilities, release patch firmware in time and notify their
users to update the firmware.

### 5\. Summary

  1. Most of the surviving devices have default credentials, which is a serious threat to the privacy of users. Users should modify the default password in time.

  2. This series of vulnerabilities may also affect dozens of OEM manufacturers at home and abroad. Embedded device firmware development usually uses the third-party's open source tools or general software. This common software is usually developed by a specific manufacturer, which leads to the homogeneity of many firmware devices. Different brands of devices may run the same or similar firmware and contain the same third-party libraries. After the disclosure of the vulnerabilities, many manufacturers’ products can be affected but not all vendors will release patches, so a great number of devices can’t be repaired.

  3. In recent years, the security vulnerabilities of loT device such as a router, camera, video camera, NAS and intelligent wearable equipment emerge in endlessly. With more and more embedded devices connected to the network, the personal privacy of users is seriously threatened. On the one hand, manufacturers and developers should constantly improve the security of their own R & D equipment. On the other hand, vulnerabilities are unavoidable. For users, they should make effort to improve their security awareness and avoid exposing such devices directly on the network space. For all loT vendors, as more and more vulnerabilities are exposed, fixing the vulnerabilities in time and providing an automatic upgrade mechanism for products is the only effective way.

### 6\. Reference

[1] NEO Coolcam's official website  
<http://www.szneo.com/>  
[2] Bitdefender vulnerability announcement  
<https://www.bitdefender.com/box/blog/ip-cameras-vulnerabilities/neo-coolcams-not-cool-buffer-overflow/>  
[3] Download address of the official update firmware  
<http://szneo.com/en/service/index.php>  
[4] ZoomEye Cyberspace Exploration Engine  
<https://www.zoomeye.org/searchResult?q=%22Error%3A%20username%20or%20password%20error%2Cplease%20input%20again.%22>  
[5] Pocsuite  
<https://github.com/knownsec/Pocsuite>  
[6] Seebug  
<https://www.seebug.org/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/652/>

