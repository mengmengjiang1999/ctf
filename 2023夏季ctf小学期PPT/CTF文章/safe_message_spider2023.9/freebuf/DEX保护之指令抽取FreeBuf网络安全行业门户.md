***本文作者：xiongchaochao，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

## 引言

**首先我们需要了解一代壳的原理，一代壳是对dex文件进行加密，反编译只能看见壳程序的代码，只能通过IDA动态调试或者使用Xposed等HOOK框架，hook相关API在App运行时dump出解密后的dex文件，这两种方法都是通过内存dump出解密后的dex文件来进行脱壳的。**

针对上面一代壳的简单描述，我们引出二代壳的功能：防止内存dump出dex文件

## 指令抽取概念

将需要保护的源码隐藏起来，通过的就是修改dex文件结构来删除指令集，这样即使dump出的dex文件也是不完整的。

这里需要了解dex文件结构，这里大概说一下，dex文件结构中的倒数第二个 **class def**
段存储着源码中类的各种详细信息，我们关注和修改的就是其中 **encode_method**
结构体，这个结构体保存中类中方法的详细信息，也是源码的逻辑结构，需要保护起来的，这个结构体里的的 **code_item**
就是这个方法中的代码信息，我们只要把指令集(指令集构成的每一行代码)置空，也就是删除了这个方法内部逻辑代码，这个方法也就成了空方法，即使dump出来也没什么作用。

## 具体实现

### 指令抽取

进行下面dex文件格式解析过程，需要对dex文件格式有一定的了解，可以看尼古拉斯赵四的dex文件解析的博客。

1、首先需要遍历dex文件的class段

    
    
    public static void parseClassIds(byte[] srcByte){
            int idSize = ClassDefItem.getSize();
            int countIds = classIdsSize;
    //        System.out.println("Total " + String.valueOf(countIds) + " classes(自定义类)\n");
            for(int i=0;i<countIds;i++){
                ClassDefItem item = new ClassDefItem();
                byte[] classItemByte = Utils.copyByte(srcByte, classIdsOffset+i*idSize, idSize);
                byte[] classIdxByte = Utils.copyByte(classItemByte, 0, 4);
                item.class_idx = Utils.byte2int(classIdxByte);
                byte[] accessFlagsByte = Utils.copyByte(classItemByte, 4, 4);
                item.access_flags = Utils.byte2int(accessFlagsByte);
                byte[] superClassIdxByte = Utils.copyByte(classItemByte, 8, 4);
                item.superclass_idx = Utils.byte2int(superClassIdxByte);
                byte[] iterfacesOffByte = Utils.copyByte(classItemByte, 12, 4);
                item.iterfaces_off = Utils.byte2int(iterfacesOffByte);
                byte[] sourceFileIdxByte = Utils.copyByte(classItemByte, 16, 4);
                item.source_file_idx = Utils.byte2int(sourceFileIdxByte);
                byte[] annotationsOffByte = Utils.copyByte(classItemByte, 20, 4);
                item.annotations_off = Utils.byte2int(annotationsOffByte);
                byte[] classDataOffByte = Utils.copyByte(classItemByte, 24, 4);
                item.class_data_off = Utils.byte2int(classDataOffByte);
                byte[] staticValueOffByte = Utils.copyByte(classItemByte, 28, 4);
                item.static_value_off = Utils.byte2int(staticValueOffByte);
                classIdsList.add(item);
            }
    

2、解析class段下的每个类的类数据，也就是解析每个classItemData中的方法字段。

![1558359253083](https://image.3001.net/images/20190601/1559359345_5cf1ef71c14e8.png!small)

    
    
    //directMethods
                EncodedMethod[] staticMethodsAry = new EncodedMethod[item.direct_methods_size];
                for(int i=0;i<item.direct_methods_size;i++){
                    /**
                     *  public byte[] method_idx_diff;
                        public byte[] access_flags;
                        public byte[] code_off;
                     */
                    EncodedMethod directMethod = new EncodedMethod();
                    directMethod.method_idx_diff = Utils.readUnsignedLeb128(srcByte, dataOffset);
                    dataOffset += directMethod.method_idx_diff.length;
                    directMethod.access_flags = Utils.readUnsignedLeb128(srcByte, dataOffset);
                    dataOffset += directMethod.access_flags.length;
                    directMethod.code_off = Utils.readUnsignedLeb128(srcByte, dataOffset);
                    dataOffset += directMethod.code_off.length;
                    staticMethodsAry[i] = directMethod;
                }
                //virtualMethods
                EncodedMethod[] instanceMethodsAry = new EncodedMethod[item.virtual_methods_size];
                for(int i=0;i<item.virtual_methods_size;i++){
                    /**
                     *  public byte[] method_idx_diff;
                        public byte[] access_flags;
                        public byte[] code_off;
                     */
                    EncodedMethod instanceMethod = new EncodedMethod();
                    instanceMethod.method_idx_diff = Utils.readUnsignedLeb128(srcByte, dataOffset);
                    dataOffset += instanceMethod.method_idx_diff.length;
                    instanceMethod.access_flags = Utils.readUnsignedLeb128(srcByte, dataOffset);
                    dataOffset += instanceMethod.access_flags.length;
                    instanceMethod.code_off = Utils.readUnsignedLeb128(srcByte, dataOffset);
                    dataOffset += instanceMethod.code_off.length;
                    instanceMethodsAry[i] = instanceMethod;
                }
    

3、进一步向结构体内部解析，找到code结构体的指令集数组。

    
    
    /            System.out.printf("\tDirect methods\t-\n");
                if(item.direct_methods.length != 0) {
                    for(int i=0; i<item.direct_methods.length; i++) {
                        int methodIndex = Utils.decodeUleb128(item.direct_methods[i].method_idx_diff);
                        int accessflag = Utils.decodeUleb128(item.direct_methods[i].access_flags);
                        int code_off = Utils.decodeUleb128(item.direct_methods[i].code_off);
                        if(code_off == 0) {
                            System.out.printf("\t\t    null code item");
                            continue;
                        }
    
                        //解析code_item结构体
                        byte[] codeItemByte = Utils.copyByte(srcByte, code_off, 16);
                        ClassCodeItem mClassCodeItem = new ClassCodeItem();
                        mClassCodeItem.registersSize = Utils.byte2Short(Utils.copyByte(codeItemByte, 0, 2));
                        mClassCodeItem.insSize = Utils.byte2Short(Utils.copyByte(codeItemByte, 2, 2));
                        mClassCodeItem.outsSize = Utils.byte2Short(Utils.copyByte(codeItemByte, 4, 2));
                        mClassCodeItem.triesSize = Utils.byte2Short(Utils.copyByte(codeItemByte, 6, 2));
                        mClassCodeItem.debugInfoOff = Utils.byte2int(Utils.copyByte(codeItemByte, 8, 4));
                        mClassCodeItem.insnsSize = Utils.byte2int(Utils.copyByte(codeItemByte, 12, 4));
                        byte[] instruction_byte = Utils.copyByte(srcByte, code_off+16, mClassCodeItem.insnsSize*2);
                        for(int j=0; j<mClassCodeItem.insnsSize; j++) {
                            mClassCodeItem.insns.add(Utils.byte2Short(Utils.copyByte(instruction_byte, 2*j, 2)));
                        }
                        System.out.printf("\t\t  name\t:%s\n", stringList.get(methodIdsList.get(methodIndex).name_idx));
                        System.out.printf("\t\t    instructions:%s\n", mClassCodeItem.insns.toString());
                        System.out.printf("\t\t    指令置空：\n");
                        if(flag == 0) {
                            dexByte = set_instru2null(srcByte, code_off+16, mClassCodeItem.insnsSize*2);
                            byte[] null_instruction = Utils.copyByte(dexByte, code_off+16, mClassCodeItem.insnsSize*2);
                            flag++;
                        }else {
                            dexByte = set_instru2null(dexByte, code_off+16, mClassCodeItem.insnsSize*2);
                        }
                        byte[] null_byte = Utils.copyByte(dexByte, code_off+16, mClassCodeItem.insnsSize*2);
                        System.out.println("\t\t" + Utils.bytesToHexString(null_byte)+"\n");
                    }
                }
                if(item.virtual_methods.length != 0) {
                    for(int i=0; i<item.virtual_methods.length; i++) {
                        int methodIndex = Utils.decodeUleb128(item.virtual_methods[i].method_idx_diff);
                        int accessflag = Utils.decodeUleb128(item.virtual_methods[i].access_flags);
                        int code_off = Utils.decodeUleb128(item.virtual_methods[i].code_off);
                        if(code_off == 0) {
                            System.out.printf("\t\t    null code item");
                            continue;
                        }
    
                        //解析code_item结构体
                        byte[] codeItemByte = Utils.copyByte(srcByte, code_off, 16);
                        ClassCodeItem mClassCodeItem = new ClassCodeItem();
                        mClassCodeItem.registersSize = Utils.byte2Short(Utils.copyByte(codeItemByte, 0, 2));
                        mClassCodeItem.insSize = Utils.byte2Short(Utils.copyByte(codeItemByte, 2, 2));
                        mClassCodeItem.outsSize = Utils.byte2Short(Utils.copyByte(codeItemByte, 4, 2));
                        mClassCodeItem.triesSize = Utils.byte2Short(Utils.copyByte(codeItemByte, 6, 2));
                        mClassCodeItem.debugInfoOff = Utils.byte2int(Utils.copyByte(codeItemByte, 8, 4));
                        mClassCodeItem.insnsSize = Utils.byte2int(Utils.copyByte(codeItemByte, 12, 4));
                        byte[] instruction_byte = Utils.copyByte(srcByte, code_off+16, mClassCodeItem.insnsSize*2);
                        for(int j=0; j<mClassCodeItem.insnsSize; j++) {
                            mClassCodeItem.insns.add(Utils.byte2Short(Utils.copyByte(instruction_byte, 2*j, 2)));
                        }
                        System.out.printf("\t\t  name\t:%s\n", stringList.get(methodIdsList.get(methodIndex).name_idx));
                        System.out.printf("\t\t    instructions:%s\n", mClassCodeItem.insns.toString());
                        System.out.printf("\t\t    指令置空：\n");
                        if(flag == 0) {
                            dexByte = set_instru2null(srcByte, code_off+16, mClassCodeItem.insnsSize*2);
                            flag++;
                        }else {
                            dexByte = set_instru2null(dexByte, code_off+16, mClassCodeItem.insnsSize*2);
                        }
                        byte[] null_byte = Utils.copyByte(dexByte, code_off+16, mClassCodeItem.insnsSize*2);
                        System.out.println("\t\t" + Utils.bytesToHexString(null_byte)+"\n");
    
                    }
                }
    

4、上面代码解析出指令数组后，使用了set_instru2null方法将指令偏移处指定大小的字节流置0，来返回一个指令集为0的dex文件的字节流。

    
    
        public static byte[] set_instru2null(byte[] src, int start, int len) {
            if(src == null){
                return null;
            }
            if(start > src.length){
                return null;
            }
            if((start+len) > src.length){
                return null;
            }
            if(start<0){
                return null;
            }
            if(len<=0){
                return null;
            }
            byte[] resultByte = new byte[src.length];
            for(int i=0; i<src.length-1; i++) {
                if(i<start) {
                    resultByte[i] = src[i];
                }else if((i-start) < len){
                    resultByte[i] = 0;
                }else {
                    resultByte[i] = src[i];
                }
            }
            return resultByte;
        }
    

## 小结

上面的代码主要都是对dex文件格式的解析，需要对dex文件格式有了解，可以参考我github上的工具[readdex.jar](https://github.com/xiongchaochao/dextool)。然后将下图中所示的指令集置0，也就隐藏了代码。

![1558360169292](https://image.3001.net/images/20190601/1559359359_5cf1ef7f7fd8e.png!small)

下面通过Jadx打开经过更改的dex文件的对比，可以从图中明显看出改过指令的dex文件方法内部的代码全部被隐藏了。

![1558444865131](https://image.3001.net/images/20190601/1559359368_5cf1ef88686a5.png!small)

### 重写校验

dex文件头中有两个字段，随着dex文件格式的修改是要进行改变的，否则安装apk的时候，会通不过系统校验。

 **checksum** ：文件校验码，除 magic 和此字段之外的文件剩下内容的 adler32 校验和，用于检测文件损坏情况；

 **signature** ：SHA-1 签名,除 magic、checksum 和此字段之外的文件的内容的 SHA-1
签名（哈希），用于对文件进行唯一标识。

也就需要写两个方法分别进行adler32校验和SHA1摘要。

先进行SHA1摘要，然后再进行CRC计算：

    
    
        //替换校验值
        public static void resetDexCheckSum(byte[] src) {
            byte[] SHA1byte = new byte[src.length-33];
            System.arraycopy(src, 32, SHA1byte, 0, src.length-33);
            byte[] sha1 = getSHA1(SHA1byte);
            replaceByte(dexByte, 12, sha1);
            byte[] checkByte = checksum_bin(dexByte, 12);
            replaceByte(dexByte, 8, checkByte);
        }
        //替换指定位置的字节数组
        public static void replaceByte(byte[] src, int offset, byte[] repByte) {
            for(int i=0; i<repByte.length; i++) {
                src[offset+i] = repByte[i];
            }
        }
        //获取SHA1值
        public static byte[] getSHA1(byte[] bt) {
            MessageDigest mMessageDigest;
            byte[] messageDigest = null;
            try {
                mMessageDigest = MessageDigest.getInstance("SHA-1");
                mMessageDigest.update(bt);
                messageDigest = mMessageDigest.digest();
                 StringBuffer hexString = new StringBuffer();
                for (int i = 0; i < messageDigest.length; i++) {
                    String shaHex = Integer.toHexString(messageDigest[i] & 0xFF);
                    if (shaHex.length() < 2) {
                        hexString.append(0);
                    }
                    hexString.append(shaHex);
                }
    
            } catch (NoSuchAlgorithmException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
            return messageDigest;
        }
        //计算checksum 
        public static byte[] checksum_bin(byte[] data, int off) { 
            int len = data.length - off; 
            Adler32 adler32 = new Adler32(); 
            adler32.reset(); 
            adler32.update(data, off, len); 
            long checksum = adler32.getValue(); 
            byte[] checksumbs = new byte[]{ 
                    (byte) checksum, 
                    (byte) (checksum >> 8), 
                    (byte) (checksum >> 16), 
                    (byte) (checksum >> 24)}; 
            return checksumbs; 
        }
    

## 小结

本文只是一种对类方法的一种隐藏，如果你对dex文件有一定了解的话还可以做到对类字段、静态字段隐藏、类方法的重复定义。

## 参考

> [1] [Android中实现「类方法指令抽取方式」加固方案原理解析](http://www.520monkey.com/archives/1118)
>
> [2] [DEX文件混淆加密](http://gnaixx.cc/2017/02/06/20170206hidex-hack/)

 ***本文作者：xiongchaochao，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

