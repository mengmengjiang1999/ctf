![](https://image.3001.net/images/20200222/1582351426_5e50c4424600d.jpg!small)

**在此之前，Forensic的研究人员曾使用LNK快捷方式文件来恢复关于目标用户近期访问文件的元数据，其中包括那些访问过之后就删除的文件。在近期的一次研究过程中，FireEye
Mandiant的研究人员遇到了一种能够验证攻击者是否访问目标文件的LNK文件，其中就包括Windows资源管理器中的搜索结果。根据我们的经验，结合上述这两种技术将能够设计出一种全新的取证方式。在这篇文章中，我们将跟大家分享这一个能够更好地映射出攻击者活动的技术。**

##  Windows LNK格式

.lnk后缀是Windows中的一种文件格式，这种代码格式文件包含的信息可以用来访问[Windows
Shell](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-shllink/16cb4ca1-9339-4d0c-a68d-bf1d6cc0f943)中的其他数据对象。

LNK快捷方式文件时一种Shell
Item类型，当用户通过一个支持的应用程序访问文件时，Windows操作系统将会自动创建LNK文件，不过用户也可以手动创建。LNK快捷方式文件一般会包含关于访问文件的元数据，其中包括文件名、文件大小、原始路径、时间戳、卷宗、系统信息和网络信息等。幸运的是，现在已经有工具可以解析这些文件了。在这篇文章中，我们将会使用Eric
Zimmerman的LECmd来演示，下图显示的就是LECmd.exe的命令行选项：

![](https://image.3001.net/images/20200222/1582351432_5e50c44828958.png!small)

##  用户搜索LNK文件

近期，Mandiant遇到了一种我们此前没研究过的LNK文件格式，这种文件来自于Windows Server 2012 R2系统，文件路径类似如下所示：

    
    
    C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\passw.lnk
    
        C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\gov.lnk

取证分析人员可以使用LNK快捷方式文件名来了解用户曾打开过一个名为passw或gov的文件。接下来，他们就可以使用类似LECmd之类的工具来恢复出额外的元数据。这样就可以获取到被访问文件的完整文件路径、被访问时间的时间戳以及其他类型的取证数据。

但是，之前的LNK文件并没有暴露额外的元数据，下面显示的是LECmd针对passw.lnk文件的分析输出：

    
    
    LECmd version 1.3.2.1
    
        Author: Eric Zimmerman (saericzimmerman@gmail.com)
    
        <https://github.com/EricZimmerman/LECmd>
    
        --- Header ---    
          Target created:
    
          Target modified:
    
          Target accessed:
    
          File size: 0
    
          Flags: HasTargetIdList, IsUnicode, DisableKnownFolderTracking
    
          File attributes: 0
    
          Icon index: 0
    
          Show window: SwNormal (Activates and displays the window. The window is restored to its original size and position if the window is minimized or maximized.)
    
        --- Target ID information (Format: Type ==> Value) ---    
          Absolute path: Search Folder\passw
    
          -Users property view ==> Search Folder
    
          >> Property store (Format: GUID\ID Description ==> Value)
    
             d5cdd505-2e9c-101b-9397-08002b2cf9ae\AutoList  ==> VT_STREAM not implemented (yet) See extension block section for contents for now
    
             d5cdd505-2e9c-101b-9397-08002b2cf9ae\AutolistCacheTime  ==> 1849138729510
    
             d5cdd505-2e9c-101b-9397-08002b2cf9ae\AutolistCacheKey  ==> Search Results in Local Disk (C:)0
    
          -Variable: Users property view ==> passw
    
          >> Property store (Format: GUID\ID Description ==> Value)
    
             1e3ee840-bc2b-476c-8237-2acd1a839b22\2      (Description not available)         ==> VT_STREAM not implemented
    
             1e3ee840-bc2b-476c-8237-2acd1a839b22\8      (Description not available)         ==> passw
    
             28636aa6-953d-11d2-b5d6-00c04fd918d0\11     Item Type                           ==> Stack
    
             28636aa6-953d-11d2-b5d6-00c04fd918d0\25     SFGAO Flags                         ==> 805306372
    
             b725f130-47ef-101a-a5f1-02608c9eebac\10     Item Name Display                   ==> passw
    
        --- End Target ID information ---    
        --- Extra blocks information ---    
        >> Property store data block (Format: GUID\ID Description ==> Value)
    
           (Property store is empty)

我们可以看到，在Target ID数据域中包含一些非常有意思的字符串，比如说“Search Folder\passw”和“Search Results in
Local Disk
(C:)”。为了方便对比，我们在下面的数据中标注了标准LNK快捷方式文件（测试文件）。需要注意的是，目标文件时间戳、文件大小、完整文件路径和其他元数据。

    
    
    LECmd version 1.3.2.1
    
        Author: Eric Zimmerman (saericzimmerman@gmail.com)
    
        <https://github.com/EricZimmerman/LECmd>
    
        --- Header ---    
          Target created:  2020-01-21 19:34:28
    
          Target modified: 2020-01-21 19:34:28
    
          Target accessed: 2020-01-22 21:25:12
    
          File size: 4
    
          Flags: HasTargetIdList, HasLinkInfo, HasRelativePath, HasWorkingDir, IsUnicode, DisableKnownFolderTracking
    
          File attributes: FileAttributeArchive
    
          Icon index: 0
    
          Show window: SwNormal (Activates and displays the window. The window is restored to its original size and position if the window is minimized or maximized.)
    
        Relative Path: ..\..\..\..\..\Desktop\test.txt
    
        Working Directory: C:\Users\<username>\Desktop
    
        --- Link information ---    
        Flags: VolumeIdAndLocalBasePath
    
        >>Volume information
    
          Drive type: Fixed storage media (Hard drive)
    
          Serial number: <serial number>
    
          Label: OSDisk
    
          Local path: C:\Users\<username>\Desktop\test.txt
    
        --- Target ID information (Format: Type ==> Value) ---    
          Absolute path: My Computer\Desktop\test.txt
    
          -Root folder: GUID ==> My Computer
    
          -Root folder: GUID ==> Desktop
    
          -File ==> test.txt
    
            Short name: test.txt
    
            Modified: 2020-01-21 19:34:30
    
            Extension block count: 1
    
            --------- Block 0 (Beef0004) ---------    
            Long name: test.txt
    
            Created: 2020-01-21 19:34:30
    
            Last access: 2020-01-21 19:34:32
    
            MFT entry/sequence #: 108919/8 (0x1A977/0x8)
    
        --- End Target ID information ---    
        --- Extra blocks information ---    
        >> Tracker database block
    
           Machine ID: <hostname>
    
           MAC Address: <mac address>
    
           MAC Vendor: INTEL
    
           Creation: 2020-01-21 15:19:59
    
           Volume Droid: <volume>
    
           Volume Droid Birth: <volume>
    
           File Droid: <file>
    
           File Droid birth: <file>

幸运的是，在一次调查过程中，我们还解析了用户的NTUSER.DAT注册表文件，并查看了WorldWheelQuery键，其中包含了用户资源管理器的详细搜索历史。passw.lnk文件突然就变得更加有意思了！下面给出的是这个注册表键的解析条目：

    
    
    wordwheelquery v.20100330
    
        (NTUSER.DAT) Gets contents of user's WordWheelQuery key
    
        Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery
    
        LastWrite Time Wed Nov 13 06:51:46 2019 (UTC)
    
         Searches listed in MRUListEx order
    
        14   Secret                         
    
        6    passw                         
    
        13   ccc                           
    
        12   bbb                           
    
        11   aaa                           
    
        10   *.cfg                         
    
        9    apple                         
    
        8    dni                           
    
        7    private                         
    
        4    gov                           
    
        5    air                           
    
        3    intelsat                      
    
        2    adhealthcheck                 
    
        1    *.ps1                         
    
        0    global

通过分析WorldWheelQuery注册表键以及根据MRUListEx顺序，我们发现了passw就是用户资源管理器搜索记录中的最近的第二个搜索条目。MRUListEx是一个注册表键值，其中包含了用户近期搜索项目的顺序，也就是用户在资源管理器中搜索内容的顺序。passw还与之前一个包含了字符串“Search
Results in Local Disk
(C:)”的LNK文件相匹配，这也就意味着，这种LNK文件跟用户资源管理器搜索结果有关，因此我们可以暂且将其称之为“用户搜索LNK文件”。

##  细微差别分析

通过在系统中查询用户资源管理器搜索历史记录中的条目，我们发现并非所有的搜索条目都有与之相对应的用户搜索LNK文件。下面显示的是其中部分LNK文件以及其对应的文件创建与修改时间戳，我们发现有15条搜索与WorldWheelQuery注册表键有关，但是这里只有4个用户搜索LNK文件。

    
    
    2019-11-09 08:33:14    Created Modified
    
        C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\gov.lnk
    
        2019-11-09 09:29:11    Created
    
        2019-11-09 09:29:37    Modified
    
        C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\private.lnk
    
        2019-11-09 08:38:29    Created
    
        2019-11-13 06:47:56    Modified
    
        C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\passw.lnk
    
        2019-11-13 06:57:03    Created
    
        2019-11-13 06:57:25    Modified
    
        C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\Secret.lnk

除此之外，我们还发现了同一时间创建出的拥有类似文件名的LNK文件对，下面这两个文件都是在2019-11-09 08:38:29 UTC创建的：

    
    
    C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\passw.lnk
    
        C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\password.lnk

进一步分析后我们发现，当用户打开搜索结果所生成的其中一个文件后，系统将会根据资源管理器的搜索结果来创建一个用户搜索LNK文件。如果用户没有打开搜索结果所返回的文件，那么用户搜索LNK文件将不会被创建。

在这个样例中，password.lnk文件包含了目标文件元数据，指向的文件为T:\
directory\password.txt。passw.lnk只包含了用户搜索LNK文件的元数据，比如说Search Folder\passw的绝对路径。

基于passw.lnk文件的创建与修改时间戳之间的差异，我们可以知道用户搜索了passw，并在搜索结果中打开了这个文件：

    
    
    2019-11-09 08:38:29    Created
    
        2019-11-13 06:47:56    Modified
    
        C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\passw.lnk

第二次搜索passw的行为发生在2019年11月13日，这一次，用户再次使用了Windows资源管理器的搜索功能来搜索passw，但是是在C:\盘驱动器根目录下执行的搜索，并且在搜索结果中点击了一个名为password2.txt的文件。LECmd对password2.lnk的解析结果如下：

    
    
    LECmd version 1.3.2.1
    
        Author: Eric Zimmerman (saericzimmerman@gmail.com)
    
        <https://github.com/EricZimmerman/LECmd>
    
        --- Header ---    
          Target created:  2015-11-09 22:14:10
    
          Target modified: 2010-01-11 16:57:11
    
          Target accessed: 2015-11-09 22:14:10
    
          File size: 19
    
          Flags: HasTargetIdList, HasLinkInfo, HasRelativePath, HasWorkingDir, IsUnicode, DisableKnownFolderTracking
    
          File attributes: FileAttributeArchive
    
          Icon index: 0
    
          Show window: SwNormal (Activates and displays the window. The window is restored to its original size and position if the window is minimized or maximized.)
    
        Relative Path: ..\..\..\..\..\..\..\<file path>\password2.txt
    
        Working Directory: C:\<file path>
    
        --- Link information ---    
        Flags: VolumeIdAndLocalBasePath, CommonNetworkRelativeLinkAndPathSuffix
    
        >>Volume information
    
          Drive type: Fixed storage media (Hard drive)
    
          Serial number: <serial number>
    
          Label: (No label)
    
          Network share information
    
            Share name: \\<hostname>\<top level folder>
    
            Provider type: <provider type>
    
            Share flags: ValidNetType
    
          Local path: C:\<top level folder>\
    
          Common path: <file path>\password2.txt
    
        --- Target ID information (Format: Type ==> Value) ---    
          Absolute path: Search Folder\passw\password2
    
          -Users property view ==> Search Folder
    
          >> Property store (Format: GUID\ID Description ==> Value)
    
             d5cdd505-2e9c-101b-9397-08002b2cf9ae\AutoList  ==> VT_STREAM not implemented (yet) See extension block section for contents for now
    
             d5cdd505-2e9c-101b-9397-08002b2cf9ae\AutolistCacheTime  ==> 1849138729510
    
             d5cdd505-2e9c-101b-9397-08002b2cf9ae\AutolistCacheKey  ==> Search Results in Local Disk (C:)0
    
          -Variable: Users property view ==> passw
    
          >> Property store (Format: GUID\ID Description ==> Value)
    
             1e3ee840-bc2b-476c-8237-2acd1a839b22\2      (Description not available)         ==> VT_STREAM not implemented
    
             1e3ee840-bc2b-476c-8237-2acd1a839b22\8      (Description not available)         ==> passw
    
             28636aa6-953d-11d2-b5d6-00c04fd918d0\11     Item Type                           ==> Stack
    
             28636aa6-953d-11d2-b5d6-00c04fd918d0\25     SFGAO Flags                         ==> 805306372
    
             b725f130-47ef-101a-a5f1-02608c9eebac\10     Item Name Display                   ==> passw
    
          -Variable: Users property view ==> password2
    
          >> Property store (Format: GUID\ID Description ==> Value)
    
             49691c90-7e17-101a-a91c-08002b2ecda9\3      Search Rank                         ==> 0
    
             28636aa6-953d-11d2-b5d6-00c04fd918d0\25     SFGAO Flags                         ==> 1077936503
    
             28636aa6-953d-11d2-b5d6-00c04fd918d0\32     Delegate ID List                    ==> VT_VECTOR data not implemented (yet) See extension block section for contents for now
    
             28636aa6-953d-11d2-b5d6-00c04fd918d0\11     Item Type                           ==> .txt
    
             28636aa6-953d-11d2-b5d6-00c04fd918d0\24     Parsing Name                        ==> password2.txt
    
             446d16b1-8dad-4870-a748-402ea43d788c\100    Thumbnail Cache Id                  ==> 7524032674880659487
    
             1e3ee840-bc2b-476c-8237-2acd1a839b22\12     (Description not available)         ==> Null
    
             1e3ee840-bc2b-476c-8237-2acd1a839b22\20     (Description not available)         ==> 1
    
             1e3ee840-bc2b-476c-8237-2acd1a839b22\3      (Description not available)         ==> document
    
             1e3ee840-bc2b-476c-8237-2acd1a839b22\17     (Description not available)         ==> {1685D4AB-A51B-4AF1-A4E5-CEE87002431D}.Merge Any
    
             1e3ee840-bc2b-476c-8237-2acd1a839b22\8      (Description not available)         ==> C:\<file path>\password2.txt
    
             b725f130-47ef-101a-a5f1-02608c9eebac\4      Item Type Text                      ==> Text Document
    
             b725f130-47ef-101a-a5f1-02608c9eebac\10     Item Name Display                   ==> password2
    
             b725f130-47ef-101a-a5f1-02608c9eebac\12     Size                                ==> 19
    
             b725f130-47ef-101a-a5f1-02608c9eebac\14     Date Modified                       ==> 01/11/2010 16:57:11
    
             006fdbaa-864f-4d1c-a8e8-e62772e454fe\11     (Description not available)         ==> 59
    
             006fdbaa-864f-4d1c-a8e8-e62772e454fe\13     (Description not available)         ==> 1077936423
    
             cf5be8c0-236c-4ad3-bace-cd608a2748d7\100    (Description not available)         ==> True
    
             e3e0584c-b788-4a5a-bb20-7f5a44c9acdd\6      Item Folder Path Display            ==> C:\<file path>
    
        --- End Target ID information ---    
        --- Extra blocks information ---    
        >> Property store data block (Format: GUID\ID Description ==> Value)
    
           (Property store is empty)
    
        >> Tracker database block
    
           Machine ID: <hostname>
    
           MAC Address: <mac address>
    
           MAC Vendor: VMWARE
    
           Creation: 2019-11-13 04:29:24
    
           Volume Droid: <volume>
    
           Volume Droid Birth: <volume>
    
           File Droid: <file>
    
           File Droid birth: <file>
    
        这里的重点就在于，用户搜索LNK文件只跟搜索词相关，而与搜索上下文无关。

##  总结

LNK快捷方式文件是确定用户对目标文件和相关文件元数据访问行为的可靠方法。有了用户搜索LNK文件之后，我们就可以丰富我们对Windows资源管理器搜索记录的研究成果，并通过对用户搜索活动的额外时间戳来进行更加详细的用户活动分析。

 *** 参考来源：[fireeye](https://www.fireeye.com/blog/threat-research/2020/02/the-missing-lnk-correlating-user-search-lnk-files.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

