![](https://image.3001.net/images/20200303/1583221640_5e5e0b88635f4.png!small)

##  写在前面的话

**如果我有一台基于云的虚拟机，并且运行了Ubuntu或CentOS的Linux服务器系统，而这些设备可能是虚拟化的，也可能不是虚拟化的，那我们应该如何去判断这台Linux
Guest系统设备使用的是哪种虚拟化技术（VMWARE/ KVM/ XEN/ VirtualBox/ Container/lxc/Hyper-V等等）呢？那我们如何才能识别一台CentOS 7 Linux VPS所使用的虚拟化技术类型呢？**

##  技术分析

我们需要使用virt-what程序（一个Shell脚本）来检测目标设备系统所使用的虚拟化技术类型，它可以打印出每一条关于目标设备虚拟化技术的相关信息。在这篇文章中，我们将介绍如何去判断Linux
Guest VM虚拟化技术类型。

###  判断Linux Guest VM虚拟化技术类型

正如我们刚才说的，我们需要使用virt-what
Linux命令来判断一个程序当前是否在一台虚拟机设备上运行。该脚本支持各种虚拟机管理程序，接下来，我们看看如何在不同的Linux发行版系统中安装virt-what。

**Debian或Ubuntu Linux安装**

首先，运行下列apt命令/apt-get命令：

    
    
    $ sudo apt-get install virt-what

或者

    
    
    $ sudo apt install virt-what

![](https://image.3001.net/images/20200303/1583221687_5e5e0bb7161cd.jpg!small)

**在RHEL/CentOS/Scientific Linux VM中安装virt-what**

我们可以使用yum命令完成安装：

    
    
    $ sudo yum install virt-what

![](https://image.3001.net/images/20200303/1583221699_5e5e0bc3da4fd.jpg!small)

**Fedora Linux VM安装virt-what来检测当前环境是否为虚拟机环境**

执行dnf命令：

    
    
    $ sudo dnf install virt-what

**Suse/OpenSUSE安装**

运行zypper命令：

    
    
    sudo zypper in virt-what

![](https://image.3001.net/images/20200303/1583221723_5e5e0bdb233ad.png!small)

###  判断远程服务器是否为虚拟机环境

我们可以直接输入并运行下列命令：

    
    
    $ $ sudo virt-what
    
        xen
    
        xen-domU

输出结果：

    
    
    $ $ sudo virt-what
    
        kvm

其他输出结果：

    
    
    $ $ sudo virt-what
    
        lxc

下面给出的是AWS返回的结果：

    
    
    $ sudo virt-what
    
        xen
    
        xen-hvm
    
        aws

![](https://image.3001.net/images/20200303/1583221749_5e5e0bf5ca900.png!small)

###  其他可能的值

> 1、hyperv : 这是微软的Hyper-V管理程序；
>
> 2、parallels : 访客用户正在Parallels虚拟平台（Parallels Desktop、Parallels Server）中运行；
>
> 3、powervm_lx86 : 访客用户正在IBM powervm lx86 Linux/x86模拟器中运行；
>
> 4、qemu : 这是使用软件模拟技术的QEMU管理程序；
>
> 5、virtualpc : 访客用户正在微软VirualPC上运行；
>
> 6、xen-hvm : 这是一个Xen Guest完全虚拟化平台（HVM）；
>
> 7、uml : 这是一个用户模式Linux（UML）客户机；
>
> 8、openvz : 访客用户正在OpenVZ或Virtuozzo容器中运行；
>
> 9、linux_vserver : 此进程正在Linux VServer容器中运行；
>
> 10、ibm_systemz : 这是一个IBM SystemZ硬件分区系统；

如果没有任何输出结果，那意味着我们的程序可能是在裸机上运行的，或者程序是在一种我们无法检测到的虚拟机系统中运行的。

##  检测脚本源代码

下面给出的是脚本的源代码：

    
    
    #!/bin/sh -    
        # virt-what.  Generated from virt-what.in by configure.
    
        # Copyright (C) 2008-2017 Red Hat Inc.
    
        #
    
        # This program is free software; you can redistribute it and/or modify
    
        # it under the terms of the GNU General Public License as published by
    
        # the Free Software Foundation; either version 2 of the License, or
    
        # (at your option) any later version.
    
        #
    
        # This program is distributed in the hope that it will be useful,
    
        # but WITHOUT ANY WARRANTY; without even the implied warranty of
    
        # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    
        # GNU General Public License for more details.
    
        #
    
        # You should have received a copy of the GNU General Public License
    
        # along with this program; if not, write to the Free Software
    
        # Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
    
        # 'virt-what' tries to detect the type of virtualization being
    
        # used (or none at all if we're running on bare-metal).  It prints
    
        # out one or more lines each being a 'fact' about the virtualization.
    
        #
    
        # Please see also the manual page virt-what(1).
    
        # This script should be run as root.
    
        #
    
        # The following resources were useful in writing this script:
    
        # . <http://dmo.ca/blog/detecting-virtualization-on-linux/>
    
        # Do not allow unset variables, and set defaults.
    
        set -u
    
        root=''
    
        skip_qemu_kvm=false
    
        skip_lkvm=false
    
        VERSION="1.20"
    
        have_cpuinfo () {
    
            test -e "${root}/proc/cpuinfo"
    
        }
    
        use_sysctl() {
    
            # Lacking /proc, on some systems sysctl can be used instead.
    
            OS=$(uname) || fail "failed to get operating system name"
    
            [ "$OS" = "OpenBSD" ]
    
        }
    
        fail () {
    
            echo "virt-what: $1" >&2
    
            exit 1
    
        }
    
        usage () {
    
            echo "virt-what [options]"
    
            echo "Options:"
    
            echo "  --help          Display this help"
    
            echo "  --version       Display version and exit"
    
            exit 0
    
        }
    
        # Handle the command line arguments, if any.
    
        while test $# -gt 0; do
    
            case "$1" in
    
                --help) usage ;;
    
                --test-root=*)
    
                    # Deliberately undocumented: used for 'make check'.
    
                    root=$(echo "$1" | sed 's/.*=//')
    
                    shift 1
    
                    test -z "$root" && fail "--test-root option requires a value"
    
                    ;;
    
                -v|--version) echo "$VERSION"; exit 0 ;;
    
                --) shift; break ;;
    
                *) fail "unrecognized option '$1'";;
    
            esac
    
        done
    
        test $# -gt 0 && fail "extra operand '$1'"
    
        # Add /sbin and /usr/sbin to the path so we can find system
    
        # binaries like dmidecode.
    
        # Add /usr/libexec to the path so we can find the helper binary.
    
        prefix=/usr/local
    
        exec_prefix=${prefix}
    
        PATH="${root}${exec_prefix}/libexec:${root}/sbin:${root}/usr/sbin:${PATH}"
    
        export PATH
    
        # Check we're running as root.
    
        EFFUID=$(id -u) || fail "failed to get current user id"
    
        if [ "x$root" = "x" ] && [ "$EFFUID" -ne 0 ]; then
    
            fail "this script must be run as root"
    
        fi
    
        # Try to locate the CPU-ID helper program
    
        CPUID_HELPER=$(which virt-what-cpuid-helper 2>/dev/null)
    
        if [ -z "$CPUID_HELPER" ] ; then
    
            fail "virt-what-cpuid-helper program not found in \$PATH"
    
        fi
    
        # Many fullvirt hypervisors give an indication through CPUID.  Use the
    
        # helper program to get this information.
    
        cpuid=$(virt-what-cpuid-helper)
    
        # Check for various products in the BIOS information.
    
        # Note that dmidecode doesn't exist on all architectures.  On the ones
    
        # it does not, then this will return an error, which is ignored (error
    
        # message redirected into the $dmi variable).
    
        dmi=$(LANG=C dmidecode 2>&1)
    
        # Architecture.
    
        # Note for the purpose of testing, we only call uname with -m option.
    
        arch=$(uname -m | sed -e 's/i.86/i386/' | sed -e 's/arm.*/arm/')
    
        # Check for VMware.
    
        # cpuid check added by Chetan Loke.
    
        if [ "$cpuid" = "VMwareVMware" ]; then
    
            echo vmware
    
        elif echo "$dmi" | grep -q 'Manufacturer: VMware'; then
    
            echo vmware
    
        fi
    
        # Check for Hyper-V.
    
        # <http://blogs.msdn.com/b/sqlosteam/archive/2010/10/30/is-this-real-the-metaphysics-of-hardware-virtualization.aspx>
    
        if [ "$cpuid" = "Microsoft Hv" ]; then
    
            echo hyperv
    
        fi
    
        # Check for VirtualPC.
    
        # The negative check for cpuid is to distinguish this from Hyper-V
    
        # which also has the same manufacturer string in the SM-BIOS data.
    
        if [ "$cpuid" != "Microsoft Hv" ] &&
    
            echo "$dmi" | grep -q 'Manufacturer: Microsoft Corporation'; then
    
            echo virtualpc
    
        fi
    
        # Check for VirtualBox.
    
        # Added by Laurent Léonard.
    
        if echo "$dmi" | grep -q 'Manufacturer: innotek GmbH'; then
    
            echo virtualbox
    
        fi
    
        # Check for bhyve.
    
        if [ "$cpuid" = "bhyve bhyve " ]; then
    
          echo bhyve
    
        elif echo "$dmi" | grep -q "Vendor: BHYVE"; then
    
          echo bhyve
    
        fi
    
        # Check for OpenVZ / Virtuozzo.
    
        # Added by Evgeniy Sokolov.
    
        # /proc/vz - always exists if OpenVZ kernel is running (inside and outside
    
        # container)
    
        # /proc/bc - exists on node, but not inside container.
    
        if [ -d "${root}/proc/vz" -a ! -d "${root}/proc/bc" ]; then
    
            echo openvz
    
        fi
    
        # Check for LXC containers
    
        # <http://www.freedesktop.org/wiki/Software/systemd/ContainerInterface>
    
        # Added by Marc Fournier
    
        if [ -e "${root}/proc/1/environ" ] &&
    
            cat "${root}/proc/1/environ" | tr '\000' '\n' | grep -Eiq '^container='; then
    
            echo lxc
    
        fi
    
        # Check for Linux-VServer
    
        if test -e "${root}/proc/self/status" \
    
           && cat "${root}/proc/self/status" | grep -q "VxID: [0-9]*"; then
    
            echo linux_vserver
    
            if grep -q "VxID: 0$" "${root}/proc/self/status"; then
    
                echo linux_vserver-host
    
            else
    
                echo linux_vserver-guest
    
            fi
    
        fi
    
        # Check for UML.
    
        # Added by Laurent Léonard.
    
        if have_cpuinfo && grep -q 'UML' "${root}/proc/cpuinfo"; then
    
            echo uml
    
        fi
    
        # Check for IBM PowerVM Lx86 Linux/x86 emulator.
    
        if have_cpuinfo && grep -q '^vendor_id.*PowerVM Lx86' "${root}/proc/cpuinfo"
    
        then
    
            echo powervm_lx86
    
        fi
    
        # Check for Hitachi Virtualization Manager (HVM) Virtage logical partitioning.
    
        if echo "$dmi" | grep -q 'Manufacturer.*HITACHI' &&
    
           echo "$dmi" | grep -q 'Product.* LPAR'; then
    
            echo virtage
    
        fi
    
        # Check for IBM SystemZ.
    
        if have_cpuinfo && grep -q '^vendor_id.*IBM/S390' "${root}/proc/cpuinfo"; then
    
            echo ibm_systemz
    
            if [ -f "${root}/proc/sysinfo" ]; then
    
                if grep -q 'VM.*Control Program.*KVM/Linux' "${root}/proc/sysinfo"; then
    
                    echo ibm_systemz-kvm
    
                elif grep -q 'VM.*Control Program.*z/VM' "${root}/proc/sysinfo"; then
    
                    echo ibm_systemz-zvm
    
                elif grep -q '^LPAR' "${root}/proc/sysinfo"; then
    
                    echo ibm_systemz-lpar
    
                else
    
                    # This is unlikely to be correct.
    
                    echo ibm_systemz-direct
    
                fi
    
            fi
    
        fi
    
        # Check for Parallels.
    
        if echo "$dmi" | grep -q 'Vendor: Parallels'; then
    
            echo parallels
    
            skip_qemu_kvm=true
    
        fi
    
        # Check for oVirt/RHEV.
    
        if echo "$dmi" | grep -q 'Manufacturer: oVirt'; then
    
            echo ovirt
    
        fi
    
        if echo "$dmi" | grep -q 'Product Name: RHEV Hypervisor'; then
    
            echo rhev
    
        fi
    
        # Check for Xen.
    
        if [ "$cpuid" = "XenVMMXenVMM" ] &&
    
            ! echo "$dmi" | grep -q 'No SMBIOS nor DMI entry point found, sorry'; then
    
            echo xen; echo xen-hvm
    
            skip_qemu_kvm=true
    
        elif [ -d "${root}/proc/xen" ]; then
    
            echo xen
    
            if grep -q "control_d" "${root}/proc/xen/capabilities" 2>/dev/null; then
    
                echo xen-dom0
    
            else
    
                echo xen-domU
    
            fi
    
            skip_qemu_kvm=true
    
            skip_lkvm=true
    
        elif [ -f "${root}/sys/hypervisor/type" ] &&
    
            grep -q "xen" "${root}/sys/hypervisor/type"; then
    
            # Ordinary kernel with pv_ops.  There does not seem to be
    
            # enough information at present to tell whether this is dom0
    
            # or domU.  XXX
    
            echo xen
    
        elif [ "$arch" = "arm" ] || [ "$arch" = "aarch64" ]; then
    
            if [ -d "${root}/proc/device-tree/hypervisor" ] &&
    
                grep -q "xen" "${root}/proc/device-tree/hypervisor/compatible"; then
    
                echo xen
    
                skip_qemu_kvm=true
    
                skip_lkvm=true
    
            fi
    
        elif [ "$arch" = "ia64" ]; then
    
            if [ -d "${root}/sys/bus/xen" -a ! -d "${root}/sys/bus/xen-backend" ]; then
    
                # PV-on-HVM drivers installed in a Xen guest.
    
                echo xen
    
                echo xen-hvm
    
            else
    
                # There is no virt leaf on IA64 HVM.  This is a last-ditch
    
                # attempt to detect something is virtualized by using a
    
                # timing attack.
    
                virt-what-ia64-xen-rdtsc-test > /dev/null 2>&1
    
                case "$?" in
    
                    0) ;; # not virtual
    
                    1) # Could be some sort of virt, or could just be a bit slow.
    
                        echo virt
    
                esac
    
            fi
    
        fi
    
        # Check for QEMU/KVM.
    
        #
    
        # Parallels exports KVMKVMKVM leaf, so skip this test if we've already
    
        # seen that it's Parallels.  Xen uses QEMU as the device model, so
    
        # skip this test if we know it is Xen.
    
        if ! "$skip_qemu_kvm"; then
    
            if [ "$cpuid" = "KVMKVMKVM" ]; then
    
                echo kvm
    
            elif [ "$cpuid" = "TCGTCGTCGTCG" ]; then
    
                echo qemu
    
                skip_lkvm=true
    
            elif echo "$dmi" | grep -q 'Product Name: KVM'; then
    
                echo kvm
    
                skip_lkvm=true
    
            elif echo "$dmi" | grep -q 'Manufacturer: QEMU'; then
    
                # The test for KVM above failed, so now we know we're
    
                # not using KVM acceleration.
    
                echo qemu
    
                skip_lkvm=true
    
            elif [ "$arch" = "arm" ] || [ "$arch" = "aarch64" ]; then
    
                if [ -d "${root}/proc/device-tree" ] &&
    
                    ls "${root}/proc/device-tree" | grep -q "fw-cfg"; then
    
                    # We don't have enough information to determine if we're
    
                    # using KVM acceleration or not.
    
                    echo qemu
    
                    skip_lkvm=true
    
                fi
    
            elif [ -d ${root}/proc/device-tree/hypervisor ] &&
    
                 grep -q "linux,kvm" /proc/device-tree/hypervisor/compatible; then
    
                # We are running as a spapr KVM guest on ppc64
    
                echo kvm
    
                skip_lkvm=true
    
            elif use_sysctl; then
    
                # SmartOS KVM
    
                product=$(sysctl -n hw.product)
    
                if echo "$product" | grep -q 'SmartDC HVM'; then
    
                    echo kvm
    
                fi
    
            else
    
                # This is known to fail for qemu with the explicit -cpu
    
                # option, since /proc/cpuinfo will not contain the QEMU
    
                # string. QEMU 2.10 added a new CPUID leaf, so this
    
                # problem only triggered for older QEMU
    
                if have_cpuinfo && grep -q 'QEMU' "${root}/proc/cpuinfo"; then
    
                    echo qemu
    
                fi
    
            fi
    
        fi
    
        if ! "$skip_lkvm"; then
    
            if [ "$cpuid" = "LKVMLKVMLKVM" ]; then
    
                echo lkvm
    
            elif [ "$arch" = "arm" ] || [ "$arch" = "aarch64" ]; then
    
                if [ -d "${root}/proc/device-tree" ] &&
    
                    grep -q "dummy-virt" "${root}/proc/device-tree/compatible"; then
    
                    echo lkvm
    
                fi
    
            fi
    
        fi
    
        # Check for Docker.
    
        if [ -f "${root}/.dockerinit" ]; then
    
            echo docker
    
        fi
    
        # Check ppc64 lpar, kvm or powerkvm
    
        # example /proc/cpuinfo line indicating 'not baremetal'
    
        # platform  : pSeries
    
        #
    
        # example /proc/ppc64/lparcfg systemtype line
    
        # system_type=IBM pSeries (emulated by qemu)
    
        if [ "$arch" = "ppc64" ] || [ "$arch" = "ppc64le" ] ; then
    
            if have_cpuinfo && grep -q 'platform.**pSeries' "${root}/proc/cpuinfo"; then
    
                if grep -q 'model.*emulated by qemu' "${root}/proc/cpuinfo"; then
    
                        echo ibm_power-kvm
    
                else
    
                    # Assume LPAR, now detect shared or dedicated
    
                    if grep -q 'shared_processor_mode=1' "${root}/proc/ppc64/lparcfg"; then
    
                        echo ibm_power-lpar_shared
    
                    else
    
                        echo ibm_power-lpar_dedicated
    
                    fi
    
                # detect powerkvm?
    
                fi
    
            fi
    
        fi
    
        # Check for OpenBSD/VMM
    
        if [ "$cpuid" = "OpenBSDVMM58" ]; then
    
                echo vmm
    
        fi
    
        # Check for LDoms
    
        if [ "${arch#sparc}" != "$arch" ] && [ -e "${root}/dev/mdesc" ]; then
    
            echo ldoms
    
            if [ -d "${root}/sys/class/vlds/ctrl" ] && \
    
                     [ -d "${root}/sys/class/vlds/sp" ]; then
    
                echo ldoms-control
    
            else
    
                echo ldoms-guest
    
            fi
    
            MDPROP="${root}/usr/lib/ldoms/mdprop.py"
    
            if [ -x "${MDPROP}" ]; then
    
                if [ -n "$($MDPROP -v iodevice device-type=pciex)" ]; then
    
                    echo ldoms-root
    
                    echo ldoms-io
    
                elif [ -n "$($MDPROP -v iov-device vf-id=0)" ]; then
    
                    echo ldoms-io
    
                fi
    
            fi
    
        fi
    
        # Check for AWS.
    
        # AWS on Xen.
    
        if echo "$dmi" | grep -q 'Version: [0-9]\.[0-9]\.amazon'; then
    
            echo aws
    
        # AWS on baremetal or KVM.
    
        elif echo "$dmi" | grep -q 'Vendor: Amazon EC2'; then
    
            echo aws
    
        fi

##  如何使用dmidecode命令来寻找相同的信息

配合Bash for循环并使用dmidecode命令判断目标虚拟化技术：

    
    
    for i in system-manufacturer system-product-name
    
        do 
    
          sudo dmidecode -s $i
    
        done

样本输出：

    
    
    Red Hat
    
        KVM

##  其他用来判断虚拟化技术的命令

我们还可以使用systemd-detect-virt命令来检测虚拟化环境：

    
    
    systemd-detect-virt

![](https://image.3001.net/images/20200303/1583221824_5e5e0c40c40fc.png!small)

##  资源获取

> 1、virt-what：【[点我获取](https://people.redhat.com/~rjones/virt-what/)】
>
> 2、Bash for循环：【[参考文档](https://www.cyberciti.biz/faq/bash-for-loop/)】
>
> 3、yum命令：【[参考文档](https://www.cyberciti.biz/faq/rhel-centos-fedora-linux-yum-> command-howto/)】
>
> 4、apt命令：【[参考文档](https://www.cyberciti.biz/faq/ubuntu-lts-debian-linux-apt-> command-examples/)】
>
> 5、apt-get命令：【[参考文档](https://www.cyberciti.biz/tips/linux-debian-package-> management-cheat-sheet.html)】

 *** 参考来源：[cyberciti](https://www.cyberciti.biz/faq/linux-determine-virtualization-technology-command/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

