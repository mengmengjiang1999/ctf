精心制作的 Windows Exploitation 资源列表与 Android 安全资源列表。

感谢 [**TK 教主**](http://weibo.com/101174)推荐

项目地址：

  * https://github.com/enddo/awesome-windows-exploitation
  * https://github.com/enddo/android-security-awesome

## Awesome Windows Exploitation

### 目录

  * Windows stack overflows
  * Windows heap overflows
  * Kernel based Windows overflows
  * Return Oriented Programming
  * Windows memory protections
  * Bypassing filter and protections
  * Typical windows exploits
  * Exploit development tutorial series
  * Corelan Team
  * Fuzzysecurity
  * Securitysift
  * Whitehatters Academy
  * TheSprawl
  * Tools

## Windows stack overflows

_Stack Base Overflow Articles._

  * [Win32 Buffer Overflows (Locatio n, Exploitation and Prevention)](http://www.phrack.com/issues.html?issue=55&id=15#article) \- by Dark spyrit [1999]
  * [Writing Stack Based Overflows on Windows](http://www.packetstormsecurity.org/papers/win/) \- by Nish Bhalla’s [2005]
  * [Stack Smashing as of Today](https://www.blackhat.com/presentations/bh-europe-09/Fritsch/Blackhat-Europe-2009-Fritsch-Bypassing-aslr-slides.pdf) \- by Hagen Fritsch [2009]
  * [SMASHING C++ VPTRS](http://phrack.org/issues/56/8.html) \- by rix [2000]

## Windows heap overflows

_Heap Base Overflow Articles._

  * [Third Generation Exploitation smashing heap on 2k](http://www.blackhat.com/presentations/win-usa-02/halvarflake-winsec02.ppt) \- by Halvar Flake [2002]
  * [Exploiting the MSRPC Heap Overflow Part 1](http://freeworld.thc.org/root/docs/exploit_writing/msrpcheap.pdf) \- by Dave Aitel (MS03-026) [September 2003]
  * [Exploiting the MSRPC Heap Overflow Part 2](http://freeworld.thc.org/root/docs/exploit_writing/msrpcheap2.pdf) \- by Dave Aitel (MS03-026) [September 2003]
  * [Windows heap overflow penetration in black hat](https://www.blackhat.com/presentations/win-usa-04/bh-win-04-litchfield/bh-win-04-litchfield.ppt) \- by David Litchfield [2004]
  * [Glibc Adventures: The Forgotten Chunk](http://www.contextis.com/documents/120/Glibc_Adventures-The_Forgotten_Chunks.pdf) \- by François Goichon [2015]
  * [Pseudomonarchia jemallocum](http://www.phrack.org/issues/68/10.html) \- by argp & huku
  * [The House Of Lore: Reloaded](http://phrack.org/issues/67/8.html) \- by blackngel [2010]
  * [Malloc Des-Maleficarum](http://phrack.org/issues/66/10.html) \- by blackngel [2009]
  * [free() exploitation technique](http://phrack.org/issues/66/6.html) \- by huku
  * [Understanding the heap by breaking it](https://www.blackhat.com/presentations/bh-usa-07/Ferguson/Whitepaper/bh-usa-07-ferguson-WP.pdf) \- by Justin N. Ferguson [2007]
  * [The use of set_head to defeat the wilderness](http://phrack.org/issues/64/9.html) \- by g463
  * [The Malloc Maleficarum](http://seclists.org/bugtraq/2005/Oct/118) \- by Phantasmal Phantasmagoria [2005]
  * [Exploiting The Wilderness](http://seclists.org/vuln-dev/2004/Feb/25) \- by Phantasmal Phantasmagoria [2004]
  * [Advanced Doug lea's malloc exploits](http://phrack.org/issues/61/6.html) \- by jp

## Kernel based Windows overflows

_Kernel Base Exploit Development Articles._

  * [How to attack kernel based vulns on windows was done](http://www.derkeiler.com/Mailing-Lists/Full-Disclosure/2003-08/0101.html) \- by a Polish group called “sec-labs” [2003]
  * [Sec-lab old whitepaper](http://www.artofhacking.com/tucops/hack/windows/live/aoh_win32dcv.htm)
  * [Sec-lab old exploit](http://www.securityfocus.com/bid/8329/info)
  * [Windows Local Kernel Exploitation (based on sec-lab research)](http://www.packetstormsecurity.org/hitb04/hitb04-sk-chong.pdf) \- by S.K Chong [2004]
  * [How to exploit Windows kernel memory pool](http://packetstormsecurity.nl/Xcon2005/Xcon2005_SoBeIt.pdf) \- by SoBeIt [2005]
  * [Exploiting remote kernel overflows in windows](http://research.eeye.com/html/papers/download/StepIntoTheRing.pdf) \- by Eeye Security
  * [Kernel-mode Payloads on Windows in uninformed](http://www.uninformed.org/?v=3&a=4&t=pdf) \- by Matt Miller
  * [Exploiting 802.11 Wireless Driver Vulnerabilities on Windows](http://www.uninformed.org/?v=6&a=2&t=pdf)
  * [BH US 2007 Attacking the Windows Kernel](http://www.blackhat.com/presentations/bh-usa-07/Lindsay/Whitepaper/bh-usa-07-lindsay-WP.pdf)
  * [Remote and Local Exploitation of Network Drivers](http://www.blackhat.com/presentations/bh-usa-07/Bulygin/Presentation/bh-usa-07-bulygin.pdf)
  * [Exploiting Comon Flaws In Drivers](http://www.reversemode.com/index.php?option=com_content&task=view&id=38&Itemid=1)
  * [I2OMGMT Driver Impersonation Attack](http://www.immunityinc.com/downloads/DriverImpersonationAttack_i2omgmt.pdf)
  * [Real World Kernel Pool Exploitation](http://sebug.net/paper/Meeting-Documents/syscanhk/KernelPool.pdf)
  * [Exploit for windows 2k3 and 2k8](http://www.argeniss.com/research/TokenKidnapping.pdf)
  * [Alyzing local privilege escalations in win32k](http://www.uninformed.org/?v=10&a=2&t=pdf)
  * [Intro to Windows Kernel Security Development](http://www.dontstuffbeansupyournose.com/trac/browser/projects/ucon09/Intro_NT_kernel_security_stuff.pdf)
  * [There’s a party at ring0 and you’re invited](http://www.cr0.org/paper/to-jt-party-at-ring0.pdf)
  * [Windows kernel vulnerability exploitation](http://vexillium.org/dl.php?call_gate_exploitation.pdf)
  * [A New CVE-2015-0057 Exploit Technology](https://www.blackhat.com/docs/asia-16/materials/asia-16-Wang-A-New-CVE-2015-0057-Exploit-Technology-wp.pdf) \- by Yu Wang [2016]
  * [Exploiting CVE-2014-4113 on Windows 8.1](https://labs.bluefrostsecurity.de/publications/2016/01/07/exploiting-cve-2014-4113-on-windows-8.1/) \- by Moritz Jodeit [2016]
  * [Easy local Windows Kernel exploitation](http://media.blackhat.com/bh-us-12/Briefings/Cerrudo/BH_US_12_Cerrudo_Windows_Kernel_WP.pdf) \- by Cesar Cerrudo [2012]
  * [Windows Kernel Exploitation ](http://www.hacking-training.com/download/WKE.pdf) \- by Simone Cardona 2016
  * [Exploiting MS16-098 RGNOBJ Integer Overflow on Windows 8.1 x64 bit by abusing GDI objects](https://sensepost.com/blog/2017/exploiting-ms16-098-rgnobj-integer-overflow-on-windows-8.1-x64-bit-by-abusing-gdi-objects/) \- by Saif Sherei 2017
  * [Windows Kernel Exploitation : This Time Font hunt you down in 4 bytes](http://www.slideshare.net/PeterHlavaty/windows-kernel-exploitation-this-time-font-hunt-you-down-in-4-bytes) \- by keen team [2015]
  * [Abusing GDI for ring0 exploit primitives](https://www.coresecurity.com/system/files/publications/2016/10/Abusing-GDI-Reloaded-ekoparty-2016_0.pdf) \- [2016]

## Return Oriented Programming

  * [The Geometry of Innocent Flesh on the Bone: Return-into-libc without Function Calls](http://cseweb.ucsd.edu/~hovav/dist/geometry.pdf)
  * [Blind return-oriented programming](http://www.scs.stanford.edu/brop/bittau-brop.pdf)
  * [Sigreturn-oriented Programming](https://www.cs.vu.nl/~herbertb/papers/srop_sp14.pdf)
  * [Jump-Oriented Programming: A New Class of Code-Reuse Attack](http://ftp.ncsu.edu/pub/tech/2010/TR-2010-8.pdf)
  * [Out of control: Overcoming control-flow integrity](http://www.cs.stevens.edu/~gportoka/files/outofcontrol_oakland14.pdf)
  * [ROP is Still Dangerous: Breaking Modern Defenses](http://www.cs.berkeley.edu/~daw/papers/rop-usenix14.pdf)
  * [Loop-Oriented Programming(LOP): A New Code Reuse Attack to Bypass Modern Defenses](https://www.sec.in.tum.de/assets/staff/muntean/Loop-Oriented_Programming_A_New_Code_Reuse_Attack_to_Bypass_Modern0ADefenses.pdf) \- by Bingchen Lan, Yan Li, Hao Sun, Chao Su, Yao Liu, Qingkai Zeng [2015]
  * [Systematic Analysis of Defenses Against Return-Oriented Programming](https://people.csail.mit.edu/nickolai/papers/skowyra-rop.pdf) -by R. Skowyra, K. Casteel, H. Okhravi, N. Zeldovich, and W. Streilein [2013]
  * [Return-oriented programming without returns](https://www.cs.uic.edu/~s/papers/noret_ccs2010/noret_ccs2010.pdf) -by S.Checkoway, L. Davi, A. Dmitrienko, A. Sadeghi, H. Shacham, and M. Winandy [2010]
  * [Jump-oriented programming: a new class of code-reuse attack](https://www.comp.nus.edu.sg/~liangzk/papers/asiaccs11.pdf) -by T. K. Bletsch, X. Jiang, V. W. Freeh, and Z. Liang [2011]
  * [Stitching the gadgets: on the ineffectiveness of coarse-grained control-flow integrity protection](https://www.usenix.org/system/files/conference/usenixsecurity14/sec14-paper-davi.pdf) \- by L. Davi, A. Sadeghi, and D. Lehmann [2014]
  * [Size does matter: Why using gadget-chain length to prevent code-reuse attacks is hard](https://www.usenix.org/system/files/conference/usenixsecurity14/sec14-paper-goktas.pdf) \- by E. Göktas, E.Athanasopoulos, M. Polychronakis, H. Bos, and G.Portokalidis [2014]
  * [Buffer overflow attacks bypassing DEP (NX/XD bits) – part 1](http://www.mastropaolo.com/2005/06/04/buffer-overflow-attacks-bypassing-dep-nxxd-bits-part-1/) \- by Marco Mastropaolo [2005]
  * [Buffer overflow attacks bypassing DEP (NX/XD bits) – part 2](http://www.mastropaolo.com/2005/06/05/buffer-overflow-attacks-bypassing-dep-nxxd-bits-part-2-code-injection/) \- by Marco Mastropaolo [2005]
  * [Practical Rop](http://trailofbits.files.wordpress.com/2010/04/practical-rop.pdf) \- by Dino Dai Zovi [2010]
  * [Exploitation with WriteProcessMemory](https://packetstormsecurity.com/papers/general/Windows-DEP-WPM.txt) \- by Spencer Pratt [2010]
  * [Exploitation techniques and mitigations on Windows](http://hick.org/~mmiller/presentations/misc/exploitation_techniques_and_mitigations_on_windows.pdf) \- by skape
  * [A little return oriented exploitation on Windows x86 – Part 1](http://blog.harmonysecurity.com/2010/04/little-return-oriented-exploitation-on.html) \- by Harmony Security and Stephen Fewer [2010]
  * [A little return oriented exploitation on Windows x86 – Part 2](http://blog.harmonysecurity.com/2010/04/little-return-oriented-exploitation-on_16.html) \- by Harmony Security and Stephen Fewer [2010]

## Windows memory protections

_Windows memory protections Introduction Articles._

  * [Data Execution Prevention](http://support.microsoft.com/kb/875352)
  * [/GS (Buffer Security Check)](http://msdn.microsoft.com/en-us/library/Aa290051)
  * [/SAFESEH](http://msdn.microsoft.com/en-us/library/9a89h429\(VS.80\).aspx)
  * [ASLR](http://blogs.msdn.com/michael_howard/archive/2006/05/26/address-space-layout-randomization-in-windows-vista.aspx)
  * [SEHOP](http://blogs.technet.com/srd/archive/2009/02/02/preventing-the-exploitation-of-seh-overwrites-with-sehop.aspx)

## Bypassing filter and protections

_Windows memory protections Bypass Methods Articles._

  * [Third Generation Exploitation smashing heap on 2k](http://www.blackhat.com/presentations/win-usa-02/halvarflake-winsec02.ppt) \- by Halvar Flake [2002]
  * [Creating Arbitrary Shellcode In Unicode Expanded Strings](http://www.net-security.org/dl/articles/unicodebo.pdf) \- by Chris Anley
  * [Advanced windows exploitation](http://www.immunityinc.com/downloads/immunity_win32_exploitation.final2.ppt) \- by Dave Aitel [2003]
  * [Defeating the Stack Based Buffer Overflow Prevention Mechanism of Microsoft Windows 2003 Server](http://www.ngssoftware.com/papers/defeating-w2k3-stack-protection.pdf) \- by David Litchfield
  * [Reliable heap exploits and after that Windows Heap Exploitation (Win2KSP0 through WinXPSP2)](http://cybertech.net/~sh0ksh0k/projects/winheap/XPSP2%20Heap%20Exploitation.ppt) \- by Matt Conover in cansecwest 2004
  * [Safely Searching Process Virtual Address Space](http://www.hick.org/code/skape/papers/egghunt-shellcode.pdf) \- by Matt Miller [2004]
  * [IE exploit and used a technology called Heap Spray](http://www.exploit-db.com/exploits/612)
  * [Bypassing hardware-enforced DEP](http://www.uninformed.org/?v=2&a=4&t=pdf) \- by Skape (Matt Miller) and Skywing (Ken Johnson) [October 2005]
  * [Exploiting Freelist[0] On XP Service Pack 2](http://www.orkspace.net/secdocs/Windows/Protection/Bypass/Exploiting%20Freelist%5B0%5D%20On%20XP%20Service%20Pack%202.pdf) \- by Brett Moore [2005]
  * [Kernel-mode Payloads on Windows in uninformed](http://www.uninformed.org/?v=3&a=4&t=pdf)
  * [Exploiting 802.11 Wireless Driver Vulnerabilities on Windows](http://www.uninformed.org/?v=6&a=2&t=pdf)
  * [Exploiting Comon Flaws In Drivers](http://www.reversemode.com/index.php?option=com_content&task=view&id=38&Itemid=1)
  * [Heap Feng Shui in JavaScript](http://www.blackhat.com/presentations/bh-europe-07/Sotirov/Presentation/bh-eu-07-sotirov-apr19.pdf) by Alexander sotirov [2007]
  * [Understanding and bypassing Windows Heap Protection](http://kkamagui.springnote.com/pages/1350732/attachments/579350) \- by Nicolas Waisman [2007]
  * [Heaps About Heaps](http://www.insomniasec.com/publications/Heaps_About_Heaps.ppt) \- by Brett moore [2008]
  * [Bypassing browser memory protections in Windows Vista](http://taossa.com/archive/bh08sotirovdowd.pdf) \- by Mark Dowd and Alex Sotirov [2008]
  * [Attacking the Vista Heap](http://www.ruxcon.org.au/files/2008/hawkes_ruxcon.pdf) \- by ben hawkes [2008]
  * [Return oriented programming Exploitation without Code Injection](http://cseweb.ucsd.edu/~hovav/dist/blackhat08.pdf) \- by Hovav Shacham (and others ) [2008]
  * [Token Kidnapping and a super reliable exploit for windows 2k3 and 2k8](http://www.argeniss.com/research/TokenKidnapping.pdf) \- by Cesar Cerrudo [2008]
  * [Defeating DEP Immunity Way](http://www.immunityinc.com/downloads/DEPLIB.pdf) \- by Pablo Sole [2008]
  * [Practical Windows XP2003 Heap Exploitation](http://www.blackhat.com/presentations/bh-usa-09/MCDONALD/BHUSA09-McDonald-WindowsHeap-PAPER.pdf) \- by John McDonald and Chris Valasek [2009]
  * [Bypassing SEHOP](http://www.sysdream.com/articles/sehop_en.pdf) \- by Stefan Le Berre Damien Cauquil [2009]
  * [Interpreter Exploitation : Pointer Inference and JIT Spraying](http://www.semantiscope.com/research/BHDC2010/BHDC-2010-Slides-v2.pdf) \- by Dionysus Blazakis[2010]
  * [Write-up of Pwn2Own 2010](http://vreugdenhilresearch.nl/Pwn2Own-2010-Windows7-InternetExplorer8.pdf) \- by Peter Vreugdenhil
  * [All in one 0day presented in rootedCON](http://wintercore.com/downloads/rootedcon_0day_english.pdf) \- by Ruben Santamarta [2010]
  * [DEP/ASLR bypass using 3rd party](http://web.archive.org/web/20130820021520/http://abysssec.com/files/The_Arashi.pdf) \- by Shahin Ramezany [2013]
  * [Bypassing EMET 5.0](http://blog.sec-consult.com/2014/10/microsoft-emet-armor-against-zero-days.html) \- by René Freingruber [2014] 

## Typical windows exploits

  * [Real-world HW-DEP bypass Exploit](http://www.exploit-db.com/exploits/3652) \- by Devcode
  * [Bypassing DEP by returning into HeapCreate](http://www.metasploit.com/redmine/projects/framework/repository/revisions/7246/entry/modules/exploits/windows/brightstor/mediasrv_sunrpc.rb) \- by Toto
  * [First public ASLR bypass exploit by using partial overwrite ](http://www.metasploit.com/redmine/projects/framework/repository/entry/modules/exploits/windows/email/ani_loadimage_chunksize.rb) \- by Skape
  * [Heap spray and bypassing DEP](http://skypher.com/SkyLined/download/www.edup.tudelft.nl/%7Ebjwever/exploits/InternetExploiter2.zip) \- by Skylined
  * [First public exploit that used ROP for bypassing DEP in adobe lib TIFF vulnerability](http://www.metasploit.com/redmine/projects/framework/repository/revisions/8833/raw/modules/exploits/windows/fileformat/adobe_libtiff.rb)
  * [Exploit codes of bypassing browsers memory protections](http://phreedom.org/research/bypassing-browser-memory-protections/bypassing-browser-memory-protections-code.zip)
  * [PoC’s on Tokken TokenKidnapping . PoC for 2k3 -part 1](http://www.argeniss.com/research/Churrasco.zip) \- by Cesar Cerrudo
  * [PoC’s on Tokken TokenKidnapping . PoC for 2k8 -part 2](http://www.argeniss.com/research/Churrasco2.zip) \- by Cesar Cerrudo
  * [An exploit works from win 3.1 to win 7](http://lock.cmpxchg8b.com/c0af0967d904cef2ad4db766a00bc6af/KiTrap0D.zip) \- by Tavis Ormandy KiTra0d
  * [Old ms08-067 metasploit module multi-target and DEP bypass](http://metasploit.com/svn/framework3/trunk/modules/exploits/windows/smb/ms08_067_netapi.rb)
  * [PHP 6.0 Dev str_transliterate() Buffer overflow – NX + ASLR Bypass](http://www.exploit-db.com/exploits/12189)
  * [SMBv2 Exploit](http://www.metasploit.com/redmine/projects/framework/repository/revisions/8916/raw/modules/exploits/windows/smb/ms09_050_smb2_negotiate_func_index.rb) \- by Stephen Fewer
  * [Microsoft IIS 7.5 remote heap buffer overflow](http://www.phrack.org/issues/68/12.html) \- by redpantz
  * [Browser Exploitation Case Study for Internet Explorer 11](https://labs.bluefrostsecurity.de/files/Look_Mom_I_Dont_Use_Shellcode-WP.pdf) \- by Moritz Jodeit [2016]

## Exploit development tutorial series

_Exploid Development Tutorial Series Base on Windows Operation System
Articles._

  * Corelan Team
  * [Exploit writing tutorial part 1 : Stack Based Overflows](https://www.corelan.be/index.php/2009/07/19/exploit-writing-tutorial-part-1-stack-based-overflows/)
  * [Exploit writing tutorial part 2 : Stack Based Overflows – jumping to shellcode](https://www.corelan.be/index.php/2009/07/23/writing-buffer-overflow-exploits-a-quick-and-basic-tutorial-part-2/)
  * [Exploit writing tutorial part 3 : SEH Based Exploits](https://www.corelan.be/index.php/2009/07/25/writing-buffer-overflow-exploits-a-quick-and-basic-tutorial-part-3-seh/)
  * [Exploit writing tutorial part 3b : SEH Based Exploits – just another example](https://www.corelan.be/index.php/2009/07/28/seh-based-exploit-writing-tutorial-continued-just-another-example-part-3b/)
  * [Exploit writing tutorial part 4 : From Exploit to Metasploit – The basics](https://www.corelan.be/index.php/2009/08/12/exploit-writing-tutorials-part-4-from-exploit-to-metasploit-the-basics/)
  * [Exploit writing tutorial part 5 : How debugger modules & plugins can speed up basic exploit development](https://www.corelan.be/index.php/2009/09/05/exploit-writing-tutorial-part-5-how-debugger-modules-plugins-can-speed-up-basic-exploit-development/)
  * [Exploit writing tutorial part 6 : Bypassing Stack Cookies, SafeSeh, SEHOP, HW DEP and ASLR](https://www.corelan.be/index.php/2009/09/21/exploit-writing-tutorial-part-6-bypassing-stack-cookies-safeseh-hw-dep-and-aslr/)
  * [Exploit writing tutorial part 7 : Unicode – from 0x00410041 to calc](https://www.corelan.be/index.php/2009/11/06/exploit-writing-tutorial-part-7-unicode-from-0x00410041-to-calc/)
  * [Exploit writing tutorial part 8 : Win32 Egg Hunting](https://www.corelan.be/index.php/2010/01/09/exploit-writing-tutorial-part-8-win32-egg-hunting/)
  * [Exploit writing tutorial part 9 : Introduction to Win32 shellcoding](https://www.corelan.be/index.php/2010/02/25/exploit-writing-tutorial-part-9-introduction-to-win32-shellcoding/)
  * [Exploit writing tutorial part 10 : Chaining DEP with ROP – the Rubik’s Cube](https://www.corelan.be/index.php/2010/06/16/exploit-writing-tutorial-part-10-chaining-dep-with-rop-the-rubikstm-cube/)
  * [Exploit writing tutorial part 11 : Heap Spraying Demystified](https://www.corelan.be/index.php/2011/12/31/exploit-writing-tutorial-part-11-heap-spraying-demystified/)
  * Fuzzysecurity
  * [Part 1: Introduction to Exploit Development](https://www.fuzzysecurity.com/tutorials/expDev/1.html)
  * [Part 2: Saved Return Pointer Overflows](https://www.fuzzysecurity.com/tutorials/expDev/2.html)
  * [Part 3: Structured Exception Handler (SEH)](https://www.fuzzysecurity.com/tutorials/expDev/3.html)
  * [Part 4: Egg Hunters](https://www.fuzzysecurity.com/tutorials/expDev/4.html)
  * [Part 5: Unicode 0x00410041](https://www.fuzzysecurity.com/tutorials/expDev/5.html)
  * [Part 6: Writing W32 shellcode](https://www.fuzzysecurity.com/tutorials/expDev/6.html)
  * [Part 7: Return Oriented Programming](https://www.fuzzysecurity.com/tutorials/expDev/7.html)
  * [Part 8: Spraying the Heap Chapter 1: Vanilla EIP](https://www.fuzzysecurity.com/tutorials/expDev/8.html)
  * [Part 9: Spraying the Heap Chapter 2: Use-After-Free](https://www.fuzzysecurity.com/tutorials/expDev/11.html)
  * [Part 10: Kernel Exploitation -> Stack Overflow](http://www.fuzzysecurity.com/tutorials/expDev/14.html)
  * [Part 11: Kernel Exploitation -> Write-What-Where](http://www.fuzzysecurity.com/tutorials/expDev/15.html)
  * [Part 12: Kernel Exploitation -> Null Pointer Dereference](http://www.fuzzysecurity.com/tutorials/expDev/16.html)
  * [Part 13: Kernel Exploitation -> Uninitialized Stack Variable](http://www.fuzzysecurity.com/tutorials/expDev/17.html)
  * [Part 14: Kernel Exploitation -> Integer Overflow](http://www.fuzzysecurity.com/tutorials/expDev/18.html)
  * [Part 15: Kernel Exploitation -> UAF](http://www.fuzzysecurity.com/tutorials/expDev/19.html)
  * [Part 16: Kernel Exploitation -> Pool Overflow](http://www.fuzzysecurity.com/tutorials/expDev/20.html)
  * [Part 17: Kernel Exploitation -> GDI Bitmap Abuse (Win7-10 32/64bit)](http://www.fuzzysecurity.com/tutorials/expDev/21.html)
  * [Heap Overflows For Humans 101](http://www.fuzzysecurity.com/tutorials/mr_me/2.html)
  * [Heap Overflows For Humans 102](http://www.fuzzysecurity.com/tutorials/mr_me/3.html)
  * [Heap Overflows For Humans 102.5](http://www.fuzzysecurity.com/tutorials/mr_me/4.html)
  * [Heap Overflows For Humans 103](http://www.fuzzysecurity.com/tutorials/mr_me/5.html)
  * [Heap Overflows For Humans 103.5](http://www.fuzzysecurity.com/tutorials/mr_me/6.html)
  * Securitysift
  * [Windows Exploit Development – Part 1: The Basics](http://www.securitysift.com/windows-exploit-development-part-1-basics/)
  * [Windows Exploit Development – Part 2: Intro to Stack Based Overflows](http://www.securitysift.com/windows-exploit-development-part-2-intro-stack-overflow/)
  * [Windows Exploit Development – Part 3: Changing Offsets and Rebased Modules](http://www.securitysift.com/windows-exploit-development-part-3-changing-offsets-and-rebased-modules/)
  * [Windows Exploit Development – Part 4: Locating Shellcode With Jumps](http://www.securitysift.com/windows-exploit-development-part-4-locating-shellcode-jumps/)
  * [Windows Exploit Development – Part 5: Locating Shellcode With Egghunting](http://www.securitysift.com/windows-exploit-development-part-5-locating-shellcode-egghunting/)
  * [Windows Exploit Development – Part 6: SEH Exploits](http://www.securitysift.com/windows-exploit-development-part-6-seh-exploits/)
  * [Windows Exploit Development – Part 7: Unicode Buffer Overflows](http://www.securitysift.com/windows-exploit-development-part-7-unicode-buffer-overflows/)

  * Whitehatters Academy
  * [Intro to Windows kernel exploitation 1/N: Kernel Debugging](https://www.whitehatters.academy/intro-to-kernel-exploitation-part-1/)
  * [Intro to Windows kernel exploitation 2/N: HackSys Extremely Vulnerable Driver](https://www.whitehatters.academy/intro-to-windows-kernel-exploitation-2-windows-drivers/)
  * [Intro to Windows kernel exploitation 3/N: My first Driver exploit](https://www.whitehatters.academy/intro-to-windows-kernel-exploitation-3-my-first-driver-exploit/)
  * [Intro to Windows kernel exploitation 3.5/N: A bit more of the HackSys Driver](https://www.whitehatters.academy/intro-to-windows-kernel-exploitation-more-of-the-hacksys-driver/)
  * [Backdoor 103: Fully Undetected](https://www.whitehatters.academy/backdoor-103-fully-undetected/)
  * [Backdoor 102](https://www.whitehatters.academy/backdoor-102/)
  * [Backdoor 101](https://www.whitehatters.academy/backdoor101-vysec/)

  * TheSprawl
  * [corelan - integer overflows - exercise solution](http://thesprawl.org/research/corelan-integer-overflows-exercise-solution/)
  * [heap overflows for humans - 102 - exercise solution](http://thesprawl.org/research/heap-overflows-humans-102-exercise-solution/)
  * [exploit exercises - protostar - final levels](http://thesprawl.org/research/exploit-exercises-protostar-final/)
  * [exploit exercises - protostar - network levels](http://thesprawl.org/research/exploit-exercises-protostar-network/)
  * [exploit exercises - protostar - heap levels](http://thesprawl.org/research/exploit-exercises-protostar-heap/)
  * [exploit exercises - protostar - format string levels](http://thesprawl.org/research/exploit-exercises-protostar-format/)
  * [exploit exercises - protostar - stack levels](http://thesprawl.org/research/exploit-exercises-protostar-stack/)
  * [open security training - introduction to software exploits - uninitialized variable overflow](http://thesprawl.org/research/ost-introduction-software-exploits-uninit-overflow/)
  * [open security training - introduction to software exploits - off-by-one](http://thesprawl.org/research/ost-introduction-exploits-offbyone/)
  * [open security training - introduction to re - bomb lab secret phase](http://thesprawl.org/research/ost-introduction-re-bomb-secret-phase/)
  * [open security training - introductory x86 - buffer overflow mystery box](http://thesprawl.org/research/ost-introductory-x86-buffer-overflow-mystery-box/)
  * [corelan - tutorial 10 - exercise solution](http://thesprawl.org/research/corelan-tutorial-10-exercise-solution/)
  * [corelan - tutorial 9 - exercise solution](http://thesprawl.org/research/corelan-tutorial-9-exercise-solution/)
  * [corelan - tutorial 7 - exercise solution](http://thesprawl.org/research/corelan-tutorial-7-exercise-solution/)
  * [getting from seh to nseh](http://thesprawl.org/research/seh-to-nseh/)
  * [corelan - tutorial 3b - exercise solution](http://thesprawl.org/research/corelan-tutorial-3b-exercise-solution/)

## Tools

_Disassemblers, debuggers, and other static and dynamic analysis tools._

  * [angr](https://github.com/angr/angr) \- Platform-agnostic binary analysis framework developed at UCSB's Seclab.
  * [BARF](https://github.com/programa-stic/barf-project) \- Multiplatform, open source Binary Analysis and Reverse engineering Framework.
  * [Binary Ninja](https://binary.ninja/) \- Multiplatform binary analysis IDE supporting various types of binaries and architecturs. Scriptable via Python.
  * [binnavi](https://github.com/google/binnavi) \- Binary analysis IDE for reverse engineering based on graph visualization.
  * [Bokken](http://www.bokken.re/) \- GUI for Pyew and Radare.
  * [Capstone](https://github.com/aquynh/capstone) \- Disassembly framework for binary analysis and reversing, with support for many architectures and bindings in several languages.
  * [codebro](https://github.com/hugsy/codebro) \- Web based code browser using clang to provide basic code analysis.
  * [dnSpy](https://github.com/0xd4d/dnSpy) \- .NET assembly editor, decompiler and debugger.
  * [Evan's Debugger (EDB)](http://codef00.com/projects#debugger) \- A modular debugger with a Qt GUI.
  * [GDB](http://www.sourceware.org/gdb/) \- The GNU debugger.
  * [GEF](https://github.com/hugsy/gef) \- GDB Enhanced Features, for exploiters and reverse engineers.
  * [hackers-grep](https://github.com/codypierce/hackers-grep) \- A utility to search for strings in PE executables including imports, exports, and debug symbols.
  * [IDA Pro](https://www.hex-rays.com/products/ida/index.shtml) \- Windows disassembler and debugger, with a free evaluation version.
  * [Immunity Debugger](http://debugger.immunityinc.com/) \- Debugger for malware analysis and more, with a Python API.
  * [ltrace](http://ltrace.org/) \- Dynamic analysis for Linux executables.
  * [objdump](https://en.wikipedia.org/wiki/Objdump) \- Part of GNU binutils, for static analysis of Linux binaries.
  * [OllyDbg](http://www.ollydbg.de/) \- An assembly-level debugger for Windows executables.
  * [PANDA](https://github.com/moyix/panda) \- Platform for Architecture-Neutral Dynamic Analysis
  * [PEDA](https://github.com/longld/peda) \- Python Exploit Development Assistance for GDB, an enhanced display with added commands.
  * [pestudio](https://winitor.com/) \- Perform static analysis of Windows executables.
  * [Process Monitor](https://technet.microsoft.com/en-us/sysinternals/bb896645.aspx) \- Advanced monitoring tool for Windows programs.
  * [Pyew](https://github.com/joxeankoret/pyew) \- Python tool for malware analysis.
  * [Radare2](http://www.radare.org/r/) \- Reverse engineering framework, with debugger support.
  * [SMRT](https://github.com/pidydx/SMRT) \- Sublime Malware Research Tool, a plugin for Sublime 3 to aid with malware analyis.
  * [strace](http://sourceforge.net/projects/strace/) \- Dynamic analysis for Linux executables.
  * [Udis86](https://github.com/vmt/udis86) \- Disassembler library and tool for x86 and x86_64.
  * [Vivisect](https://github.com/vivisect/vivisect) \- Python tool for malware analysis.
  * [X64dbg](https://github.com/x64dbg/) \- An open-source x64/x32 debugger for windows.

A collection of android security related resources.

A lot of work is happening in academia and industry on tools to perform
dynamic analysis, static analysis and reverse engineering of android apps.

## android-security-awesome

## ONLINE ANALYZERS

  1. [AndroTotal](http://andrototal.org/)
  2. [CopperDroid](http://copperdroid.isg.rhul.ac.uk/copperdroid/)
  3. [Dexter](https://dexter.dexlabs.org/)
  4. [SandDroid](http://sanddroid.xjtu.edu.cn/)
  5. [Tracedroid](http://tracedroid.few.vu.nl/)
  6. [Visual Threat](http://www.visualthreat.com/)
  7. [Mobile Malware Sandbox](http://www.mobilemalware.com.br/analysis/index_en.php)
  8. [MobiSec Eacus](http://www.mobiseclab.org/eacus.jsp)
  9. [IBM Security AppScan Mobile Analyzer](https://appscan.bluemix.net/mobileAnalyzer) \- not free
  10. [NVISO ApkScan](https://apkscan.nviso.be/)
  11. [AVC UnDroid](http://www.av-comparatives.org/avc-analyzer/)
  12. [Fireeye](https://fireeye.ijinshan.com/)\- max 60MB 15/day
  13. [habo](https://habo.qq.com/) 10/day
  14. [Virustotal](https://www.virustotal.com/)-max 128MB
  15. [Fraunhofer App-ray](https://www.app-ray.com) \- not free
  16. ~~[Stowaway](http://www.android-permissions.org/)~~
  17. ~~[Anubis](http://anubis.iseclab.org/)~~
  18. ~~[Mobile app insight](http://www.mobile-app-insight.org)~~
  19. ~~[Mobile-Sandbox](http://mobile-sandbox.com)~~
  20. ~~[Ijiami](http://safe.ijiami.cn/)~~
  21. ~~[Comdroid](http://www.comdroid.org/)~~
  22. ~~[Android Sandbox](http://www.androidsandbox.net/)~~
  23. ~~[Foresafe](http://www.foresafe.com/scan)~~

## STATIC ANALYSIS TOOLS

  1. [Androwarn](https://github.com/maaaaz/androwarn/) \- detect and warn the user about potential malicious behaviours developped by an Android application.
  2. [ApkAnalyser](https://github.com/sonyxperiadev/ApkAnalyser)
  3. [APKInspector](https://github.com/honeynet/apkinspector/)
  4. [Droid Intent Data Flow Analysis for Information Leakage](https://www.cert.org/secure-coding/tools/didfail.cfm)
  5. [Several tools from PSU](http://siis.cse.psu.edu/tools.html)
  6. [Smali CFG generator](https://github.com/EugenioDelfa/Smali-CFGs)
  7. [FlowDroid](https://blogs.uni-paderborn.de/sse/tools/flowdroid/)
  8. [Android Decompiler](https://www.pnfsoftware.com/) – not free
  9. [PSCout](http://pscout.csl.toronto.edu/) \- A tool that extracts the permission specification from the Android OS source code using static analysis
  10. [Amandroid](http://amandroid.sireum.org/)
  11. [SmaliSCA](https://github.com/dorneanu/smalisca) \- Smali Static Code Analysis
  12. [CFGScanDroid](https://github.com/douggard/CFGScanDroid) \- Scans and compares CFG against CFG of malicious applications
  13. [Madrolyzer](https://github.com/maldroid/maldrolyzer) \- extracts actionable data like C&C, phone number etc.
  14. [SPARTA](http://www.cs.washington.edu/sparta) \- verifies (proves) that an app satisfies an information-flow security policy; built on the [Checker Framework](http://types.cs.washington.edu/checker-framework/)
  15. [ConDroid](https://github.com/JulianSchuette/ConDroid) \- Performs a combination of symoblic + concrete execution of the app

## APP VULNERABILITY SCANNERS

  1. [QARK](https://github.com/linkedin/qark/) \- QARK by LinkedIn is for app developers to scan app for security issues
  2. [AndroBugs](https://github.com/AndroBugs/AndroBugs_Framework)
  3. [Nogotofail](https://github.com/google/nogotofail)

## DYNAMIC ANALYSIS TOOLS

  1. [Android DBI frameowork](http://www.mulliner.org/blog/blosxom.cgi/security/androiddbiv02.html)
  2. [Android Malware Analysis Toolkit](http://www.mobilemalware.com.br/amat/download.html) \- (linux distro) Earlier it use to be an [online analyzer](http://dunkelheit.com.br/amat/analysis/index_en.html)
  3. [Mobile-Security-Framework MobSF](https://github.com/ajinabraham/Mobile-Security-Framework-MobSF) \- Mobile Security Framework is an intelligent, all-in-one open source mobile application (Android/iOS) automated pen-testing framework capable of performing static, dynamic analysis and web API testing.
  4. [AppUse](https://appsec-labs.com/AppUse/) – custom build for pentesting
  5. [Cobradroid](https://thecobraden.com/projects/cobradroid/) – custom image for malware analysis
  6. [ViaLab Community Edition](https://www.nowsecure.com/blog/2014/09/10/introducing-vialab-community-edition/)
  7. [Droidbox](https://github.com/pjlantz/droidbox)
  8. [Mercury](http://labs.mwrinfosecurity.com/tools/2012/03/16/mercury/)
  9. [Drozer](https://labs.mwrinfosecurity.com/tools/drozer/)
  10. [Taintdroid](https://appanalysis.org/download.html) \- requires AOSP compilation
  11. [Xposed](https://forum.xda-developers.com/showthread.php?t=1574401) \- equivalent of doing Stub based code injection but without any modifications to the binary
  12. [Android Hooker](https://github.com/AndroidHooker/hooker) \- API Hooking of java methods triggered by any Android application (requires the Substrate Framework)
  13. [Android tamer](https://androidtamer.com/) \- custom image
  14. [Droidscope](https://code.google.com/p/decaf-platform/wiki/DroidScope) \- custom image for dynamic analysis
  15. [CuckooDroid](https://github.com/idanr1986/cuckoo-droid) \- Android extension for Cuckoo sandbox
  16. [Mem](https://github.com/MobileForensicsResearch/mem) \- Memory analysis of Android (root required)
  17. [Crowdroid](http://www.ida.liu.se/labs/rtslab/publications/2011/spsm11-burguera.pdf) – unable to find the actual tool
  18. [AuditdAndroid](https://github.com/nwhusted/AuditdAndroid) – android port of auditd, not under active development anymore
  19. [Android Security Evaluation Framework](https://code.google.com/p/asef/) \- not under active development anymore
  20. [Android Reverse Engineering](https://redmine.honeynet.org/projects/are/wiki) – ARE (android reverse engineering) not under active development anymore
  21. [Aurasium](https://github.com/xurubin/aurasium) – Practical security policy enforcement for Android apps via bytecode rewriting and in-place reference monitor.
  22. [Android Linux Kernel modules](https://github.com/strazzere/android-lkms) *
  23. [Appie](https://manifestsecurity.com/appie/) \- Appie is a software package that has been pre-configured to function as an Android Pentesting Environment.It is completely portable and can be carried on USB stick or smartphone.This is a one stop answer for all the tools needed in Android Application Security Assessment and an awesome alternative to existing virtual machines.
  24. [StaDynA](https://github.com/zyrikby/StaDynA) \- a system supporting security app analysis in the presence of dynamic code update features (dynamic class loading and reflection). This tool combines static and dynamic analysis of Android applications in order to reveal the hidden/updated behavior and extend static analysis results with this information.
  25. [DroidAnalytics](https://github.com/zhengmin1989/DroidAnalytics) \- incomplete
  26. [Vezir Project](https://github.com/oguzhantopgul/Vezir-Project) \- Virtual Machine for Mobile Application Pentesting and Mobile Malware Analysis 

## REVERSE ENGINEERING

  1. [Smali/Baksmali](https://github.com/JesusFreke/smali) – apk decompilation
  2. [emacs syntax coloring for smali files](https://github.com/strazzere/Emacs-Smali)
  3. [vim syntax coloring for smali files](http://codetastrophe.com/smali.vim)
  4. [AndBug](https://github.com/swdunlop/AndBug)
  5. [Androguard](https://github.com/androguard/androguard) – powerful, integrates well with other tools
  6. [Apktool](https://ibotpeaches.github.io/Apktool/) – really useful for compilation/decompilation (uses smali)
  7. [Android Framework for Exploitation](https://github.com/appknox/AFE)
  8. [Bypass signature and permission checks for IPCs](https://github.com/iSECPartners/Android-KillPermAndSigChecks)
  9. [Android OpenDebug](https://github.com/iSECPartners/Android-OpenDebug) – make any application on device debuggable (using cydia substrate).
  10. [Dare](http://siis.cse.psu.edu/dare/index.html) – .dex to .class converter
  11. [Dex2Jar](https://github.com/pxb1988/dex2jar) \- dex to jar converter
  12. [Enjarify](https://github.com/google/enjarify) \- dex to jar converter from Google
  13. [Dedexer](http://dedexer.sourceforge.net)
  14. [Fino](https://github.com/sysdream/fino)
  15. [Indroid](https://bitbucket.org/aseemjakhar/indroid) – thread injection kit
  16. [IntentSniffer](https://www.nccgroup.trust/us/about-us/resources/intent-sniffer/)
  17. [Introspy](https://github.com/iSECPartners/Introspy-Android)
  18. [Jad](http://varaneckas.com/jad/) \- Java decompiler
  19. [JD-GUI](https://github.com/java-decompiler/jd-gui) \- Java decompiler
  20. [CFR](http://www.benf.org/other/cfr/) \- Java decompiler
  21. [Krakatau](https://github.com/Storyyeller/Krakatau) \- Java decompiler
  22. [Procyon](https://bitbucket.org/mstrobel/procyon/wiki/Java%20Decompiler) \- Java decompiler
  23. [FernFlower](https://github.com/fesh0r/fernflower) \- Java decompiler
  24. [Redexer](https://github.com/plum-umd/redexer) – apk manipulation
  25. [Smali viewer](http://blog.avlyun.com/wp-content/uploads/2014/04/SmaliViewer.zip)
  26. [ZjDroid](https://github.com/BaiduSecurityLabs/ZjDroid) (no longer available), [fork/mirror](https://github.com/yangbean9/ZjDroid)
  27. [Simplify Android deobfuscator](https://github.com/CalebFenton/simplify)
  28. [Bytecode viewer](https://github.com/Konloch/bytecode-viewer)
  29. [Radare2](https://github.com/radare/radare2)

## FUZZ TESTING

  1. [IntentFuzzer](https://www.nccgroup.trust/us/about-us/resources/intent-fuzzer/)
  2. [Radamsa Fuzzer](https://github.com/anestisb/radamsa-android)
  3. [Honggfuzz](https://github.com/google/honggfuzz)
  4. [An Android port of the melkor ELF fuzzer](https://github.com/anestisb/melkor-android)
  5. [Media Fuzzing Framework for Android](https://github.com/fuzzing/MFFA)

## APP REPACKAGING DETECTORS

  1. [FSquaDRA](https://github.com/zyrikby/FSquaDRA) \- a tool for detection of repackaged Android applications based on app resources hash comparison.

## Exploitable Vulnerabilties

  1. [Vulnerability Google doc](https://docs.google.com/spreadsheet/pub?key=0Am5hHW4ATym7dGhFU1A4X2lqbUJtRm1QSWNRc3E0UlE&single=true&gid=0&output=html)
  2. [Root Exploits (from Drozer issue #56)](https://github.com/mwrlabs/drozer/issues/56)

## SAMPLE SOURCES

  1. [contagio mini dump](http://contagiominidump.blogspot.com)
  2. [Android malware github repo](https://github.com/ashishb/android-malware)
  3. [Open Source database](https://code.google.com/p/androguard/wiki/DatabaseAndroidMalwares)
  4. [Drebin](http://user.informatik.uni-goettingen.de/~darp/drebin/)
  5. [Admire](http://admire.necst.it/)
  6. [MalGenome](http://www.malgenomeproject.org/policy.html) \- contains 1260 malware samples categorized into 49 different malware families, free for research purpose.
  7. [VirusTotal Malware Intelligence Service](https://www.virustotal.com/en/about/contact/) \- powered by VirusTotal,not free

## Reading material

  1. [Android Security (and Not) Internals](http://www.zhauniarovich.com/pubs.html)
  2. [Android security related presentations](https://github.com/jacobsoo/AndroidSlides)
  3. [A good collection of static analysis papers](https://tthtlc.wordpress.com/2011/09/01/static-analysis-of-android-applications/)

## MARKET CRAWLERS

  1. [Google play crawler (Java)](https://github.com/Akdeniz/google-play-crawler)
  2. [Google play crawler (Python)](https://github.com/egirault/googleplay-api)
  3. [Google play crawler (Node) ](https://github.com/dweinstein/node-google-play) \- get app details and download apps from official Google Play Store.
  4. [Aptoide downloader (Node)](https://github.com/dweinstein/node-aptoide) \- download apps from Aptoide third-party Android market
  5. [Appland downloader (Node)](https://github.com/dweinstein/node-appland) \- download apps from Appland third-party Android market

## MISC TOOLS

  1. [smalihook](http://androidcracking.blogspot.com/2011/03/original-smalihook-java-source.html)
  2. [APK-Downloader](http://codekiem.com/2012/02/24/apk-downloader/)
  3. [AXMLPrinter2](http://code.google.com/p/android4me/downloads/detail?name=AXMLPrinter2.jar) \- to convert binary XML files to human-readable XML files
  4. [adb autocomplete](https://romannurik-code.googlecode.com/git/bash_completion/adb)
  5. [Dalvik opcodes](http://pallergabor.uw.hu/androidblog/dalvik_opcodes.html)
  6. [Opcodes table for quick reference](http://www.xchg.info/corkami/opcodes_tables.pdf)
  7. [ExploitMe Android Labs](http://securitycompass.github.io/AndroidLabs/setup.html) \- for practice
  8. [GoatDroid](https://github.com/jackMannino/OWASP-GoatDroid-Project) \- for practice
  9. [mitmproxy](https://github.com/mitmproxy/mitmproxy)
  10. [dockerfile/androguard](https://github.com/dweinstein/dockerfile-androguard)
  11. [Android Vulnerability Test Suite](https://github.com/nowsecure/android-vts) \- android-vts scans a device for set of vulnerabilities

## Good Tutorials

  1. [Android Reverse Engineering 101 by Daniele Altomare](http://www.fasteque.com/android-reverse-engineering-101-part-1/)

# Other Awesome Lists

Other amazingly awesome lists can be found in the [awesome-awesomeness](https://github.com/bayandin/awesome-awesomeness) list.

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/195/>

