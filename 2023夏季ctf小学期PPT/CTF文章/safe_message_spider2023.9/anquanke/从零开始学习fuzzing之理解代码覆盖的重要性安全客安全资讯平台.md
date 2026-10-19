# 从零开始学习fuzzing之理解代码覆盖的重要性

阅读量 **204507**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-06-02 16:30:37

 **x**

##### 译文声明

本文是翻译文章，文章原作者 h0mbre，文章来源：h0mbre.github.io

原文地址：<https://h0mbre.github.io/Fuzzing-Like-A-Caveman-3/#>

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p5.ssl.qhimg.com/t01a26895dd8cd92a0d.png)

## 前言

这是“从零开始学习fuzzing”的第三篇文章，我们会继续fuzzing的菜鸟学习之路，从代码覆盖(code
coverage)的角度对我们之前编写的模糊测试器进行探讨，并说明其重要性。据我所知，代码覆盖概括来讲指的是模糊测试器的输入对目标程序代码的覆盖范围。也就是说，模糊测试器的输入所能覆盖的代码范围越广，攻击面就越大，测试就越全面。除此之外，还有一些我尚未了解的内容。

我最近一直在提升自己的pwn技能，但为了保持状态也在中途休息一下，编写了一些C语言代码，并观看了[@gamozolabs](https://github.com/gamozolabs
"@gamozolabs")的直播。 [@gamozolabs](https://github.com/gamozolabs
"@gamozolabs")在他的一个直播中强调了代码覆盖的重要性，我并没有截取这部分内容，但是也留下的足够的印象，让我在自己的测试中创建了一些测试用例，从而说明普通的模糊测试器远没有注重代码覆盖的模糊测试器有效果。你要做好准备阅读一些（可能并不正确的🤣）八年级概率论知识了。在阅读完本文之后，读者至少应该能广泛地了解到1990年最先进的模糊测试器的工作原理了。

## 我们的模糊测试器

我们现在已经有一个漂亮，没有错误且编写完美的单线程基于变异的模糊测试器了，它能够对JPEG文件进行模糊测试，在[上一篇文章](https://www.anquanke.com/post/id/202989)中，我们将其移植到了C语言中，并针对实验需求进行了一些调整。

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <time.h>
    #include <string.h>
    #include <sys/wait.h>
    #include <unistd.h> 
    #include <fcntl.h>
    
    int crashes = 0;
    
    struct ORIGINAL_FILE {
        char * data;
        size_t length;
    };
    
    struct ORIGINAL_FILE get_data(char* fuzz_target) {
    
        FILE *fileptr;
        char *clone_data;
        long filelen;
    
        // open file in binary read mode
        // jump to end of file, get length
        // reset pointer to beginning of file
        fileptr = fopen(fuzz_target, "rb");
        if (fileptr == NULL) {
            printf("[!] Unable to open fuzz target, exiting...n");
            exit(1);
        }
        fseek(fileptr, 0, SEEK_END);
        filelen = ftell(fileptr);
        rewind(fileptr);
    
        // cast malloc as char ptr
        // ptr offset * sizeof char = data in .jpeg
        clone_data = (char *)malloc(filelen * sizeof(char));
    
        // get length for struct returned
        size_t length = filelen * sizeof(char);
    
        // read in the data
        fread(clone_data, filelen, 1, fileptr);
        fclose(fileptr);
    
        struct ORIGINAL_FILE original_file;
        original_file.data = clone_data;
        original_file.length = length;
    
        return original_file;
    }
    
    void create_new(struct ORIGINAL_FILE original_file, size_t mutations) {
    
        //
        //----------------MUTATE THE BITS-------------------------        //
        int* picked_indexes = (int*)malloc(sizeof(int)*mutations);
        for (int i = 0; i < (int)mutations; i++) {
            picked_indexes[i] = rand() % original_file.length;
        }
    
        char * mutated_data = (char*)malloc(original_file.length);
        memcpy(mutated_data, original_file.data, original_file.length);
    
        for (int i = 0; i < (int)mutations; i++) {
            char current = mutated_data[picked_indexes[i]];
    
            // figure out what bit to flip in this 'decimal' byte
            int rand_byte = rand() % 256;
    
            mutated_data[picked_indexes[i]] = (char)rand_byte;
        }
    
        //
        //---------WRITING THE MUTATED BITS TO NEW FILE-----------        //
        FILE *fileptr;
        fileptr = fopen("mutated.jpeg", "wb");
        if (fileptr == NULL) {
            printf("[!] Unable to open mutated.jpeg, exiting...n");
            exit(1);
        }
        // buffer to be written from,
        // size in bytes of elements,
        // how many elements,
        // where to stream the output to :)
        fwrite(mutated_data, 1, original_file.length, fileptr);
        fclose(fileptr);
        free(mutated_data);
        free(picked_indexes);
    }
    
    void exif(int iteration) {
    
        //fileptr = popen("exiv2 pr -v mutated.jpeg >/dev/null 2>&1", "r");
        char* file = "vuln";
        char* argv[3];
        argv[0] = "vuln";
        argv[1] = "mutated.jpeg";
        argv[2] = NULL;
        pid_t child_pid;
        int child_status;
    
        child_pid = fork();
        if (child_pid == 0) {
    
            // this means we're the child process
            int fd = open("/dev/null", O_WRONLY);
    
            // dup both stdout and stderr and send them to /dev/null
            dup2(fd, 1);
            dup2(fd, 2);
            close(fd);
    
    
            execvp(file, argv);
            // shouldn't return, if it does, we have an error with the command
            printf("[!] Unknown command for execvp, exiting...n");
            exit(1);
        }
        else {
            // this is run by the parent process
            do {
                pid_t tpid = waitpid(child_pid, &child_status, WUNTRACED |
                 WCONTINUED);
                if (tpid == -1) {
                    printf("[!] Waitpid failed!n");
                    perror("waitpid");
                }
                if (WIFEXITED(child_status)) {
                    //printf("WIFEXITED: Exit Status: %dn", WEXITSTATUS(child_status));
                } else if (WIFSIGNALED(child_status)) {
                    crashes++;
                    int exit_status = WTERMSIG(child_status);
                    printf("r[>] Crashes: %d", crashes);
                    fflush(stdout);
                    char command[50];
                    sprintf(command, "cp mutated.jpeg ccrashes/%d.%d", iteration, 
                    exit_status);
                    system(command);
                } else if (WIFSTOPPED(child_status)) {
                    printf("WIFSTOPPED: Exit Status: %dn", WSTOPSIG(child_status));
                } else if (WIFCONTINUED(child_status)) {
                    printf("WIFCONTINUED: Exit Status: Continued.n");
                }
            } while (!WIFEXITED(child_status) && !WIFSIGNALED(child_status));
        }
    }
    
    int main(int argc, char** argv) {
    
        if (argc < 3) {
            printf("Usage: ./cfuzz <valid jpeg> <num of fuzz iterations>n");
            printf("Usage: ./cfuzz Canon_40D.jpg 10000n");
            exit(1);
        }
    
        // get our random seed
        srand((unsigned)time(NULL));
    
        char* fuzz_target = argv[1];
        struct ORIGINAL_FILE original_file = get_data(fuzz_target);
        printf("[>] Size of file: %ld bytes.n", original_file.length);
        size_t mutations = (original_file.length - 4) * .02;
        printf("[>] Flipping up to %ld bytes.n", mutations);
    
        int iterations = atoi(argv[2]);
        printf("[>] Fuzzing for %d iterations...n", iterations);
        for (int i = 0; i < iterations; i++) {
            create_new(original_file, mutations);
            exif(i);
        }
    
        printf("n[>] Fuzzing completed, exiting...n");
        return 0;
    }
    

我不会再介绍该模糊测试器的功能，但还是要强调一下有关它的重要特征：

  * 该模糊测试器会接收一个文件作为输入，并将其中的字节复制到缓冲区中；
  * 它会计算该缓冲区的字节长度，然后用任意字节随机覆盖其中的2％字节；
  * 负责变异的函数`create_new`不会记录发生变化的字节索引，因此从理论上讲，同一位置的字节可能会发生多次变异，所以准确来说，该模糊测试器 **最多** 可以对2％的字节进行变异。

###  抱歉，一些改动

为了方便，我在这里只使用了一种变异方法，在此过程中，我也学会了一些很有用的东西，而这些内容我之前并没有仔细考虑过。在之前的文章中，我还曾经明确地表示随机位翻转随机字节覆盖之间没有什么大的区别。好吧，事实证明，它们完全不同。让我们花点时间看看差别到底在哪里。

假设我们要对`bytes`字节数组进行变异。对索引5处的字节进行修改，未修改之前`bytes[5]` == ` x41`
`（十进制为65）`。如果只进行位翻转，那么可以改变的字节数是非常有限的。65的二进制是`01000001`。让我们看一下翻转任意字节对它的改变有多大：

  * 翻转第一位：`11000001` = 193，
  * 翻转第二位：`00000001` = 1，
  * 翻转第三位：`01100001` = 97，
  * 翻转第四位：`01010001` = 81，
  * 翻转第五位：`01001001` = 73，
  * 翻转第六位：`01000101` = 69，
  * 翻转第七位：`01000011` = 67，
  * 翻转第八位：`01000000` = 64。

如你所见，存在的可能性非常有限。

所以对于该程序，我选择用另外一个方法，不再修改随机字节中的一个位，而是修改该字节。

## 存在漏洞的程序

我编写了一个简单的程序来说明普通的模糊测试器在寻找漏洞时有多困难。假设目标应用程序的二进制文件中，其反汇编视图中具有多个决策树。
在将输入传递给某个存在漏洞的函数之前，该程序会对输入执行2-3次检查，确定其是否满足某些条件。如下图所示：

![](https://p5.ssl.qhimg.com/t01a71856b27f87f3d5.png)

程序会执行以下操作，它会检索输入文件中的字节，并检查位于1/3、1/2、2/3文件长度位置的字节，看它们是否和某些任意的硬编码值相匹配。
如果所有检查都通过，程序会把字节缓冲区复制到一个小的缓冲区中，引发一个段错误，从而模拟一个存在漏洞的函数行为。程序如下：

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <errno.h>
    
    struct ORIGINAL_FILE {
        char * data;
        size_t length;
    };
    
    struct ORIGINAL_FILE get_bytes(char* fileName) {
    
        FILE *filePtr;
        char* buffer;
        long fileLen;
    
        filePtr = fopen(fileName, "rb");
        if (!filePtr) {
            printf("[>] Unable to open %sn", fileName);
            exit(-1);
        }
    
        if (fseek(filePtr, 0, SEEK_END)) {
            printf("[>] fseek() failed, wtf?n");
            exit(-1);
        }
    
        fileLen = ftell(filePtr);
        if (fileLen == -1) {
            printf("[>] ftell() failed, wtf?n");
            exit(-1);
        }
    
        errno = 0;
        rewind(filePtr);
        if (errno) {
            printf("[>] rewind() failed, wtf?n");
            exit(-1);
        }
    
        long trueSize = fileLen * sizeof(char);
        printf("[>] %s is %ld bytes.n", fileName, trueSize);
        buffer = (char *)malloc(fileLen * sizeof(char));
        fread(buffer, fileLen, 1, filePtr);
        fclose(filePtr);
    
        struct ORIGINAL_FILE original_file;
        original_file.data = buffer;
        original_file.length = trueSize;
    
        return original_file;
    }
    
    void check_one(char* buffer, int check) {
    
        if (buffer[check] == 'x6c') {
            return;
        }
        else {
            printf("[>] Check 1 failed.n");
            exit(-1);
        }
    }
    
    void check_two(char* buffer, int check) {
    
        if (buffer[check] == 'x57') {
            return;
        }
        else {
            printf("[>] Check 2 failed.n");
            exit(-1);
        }
    }
    
    void check_three(char* buffer, int check) {
    
        if (buffer[check] == 'x21') {
            return;
        }
        else {
            printf("[>] Check 3 failed.n");
            exit(-1);
        }
    }
    
    void vuln(char* buffer, size_t length) {
    
        printf("[>] Passed all checks!n");
        char vulnBuff[20];
    
        memcpy(vulnBuff, buffer, length);
    
    }
    
    int main(int argc, char *argv[]) {
    
        if (argc < 2 || argc > 2) {
            printf("[>] Usage: vuln example.txtn");
            exit(-1);
        }
    
        char *filename = argv[1];
        printf("[>] Analyzing file: %s.n", filename);
    
        struct ORIGINAL_FILE original_file = get_bytes(filename);
    
        int checkNum1 = (int)(original_file.length * .33);
        printf("[>] Check 1 no.: %dn", checkNum1);
    
        int checkNum2 = (int)(original_file.length * .5);
        printf("[>] Check 2 no.: %dn", checkNum2);
    
        int checkNum3 = (int)(original_file.length * .67);
        printf("[>] Check 3 no.: %dn", checkNum3);
    
        check_one(original_file.data, checkNum1);
        check_two(original_file.data, checkNum2);
        check_three(original_file.data, checkNum3);
    
        vuln(original_file.data, original_file.length);
    
    
        return 0;
    }
    

请注意该代码中检查方式并不唯一，二进制文件中会存在很多种不同类型的条件检查情况。之所以选择这种方式，是因为这样做可以以一种夸大的形式说明纯粹依靠随机性来覆盖目标程序中新的范围是很困难的。

此处仍使用之前文章中使用的测试文件（之后会对其进行变异并输入到存在漏洞的程序中），即带有exif数据的`Canon_40D.jpg`文件。

    
    
    h0mbre@pwn:~/fuzzing$ file Canon_40D.jpg 
    Canon_40D.jpg: JPEG image data, JFIF standard 1.01, resolution (DPI), density 72x72, segment length 16, Exif Standard: [TIFF image data, little-endian, direntries=11, manufacturer=Canon, model=Canon EOS 40D, orientation=upper-left, xresolution=166, yresolution=174, resolutionunit=2, software=GIMP 2.4.5, datetime=2008:07:31 10:38:11, GPS-Data], baseline, precision 8, 100x68, frames 3
    h0mbre@pwn:~/fuzzing$ ls -lah Canon_40D.jpg 
    -rw-r--r-- 1 h0mbre h0mbre 7.8K May 25 06:21 Canon_40D.jpg
    

该文件长度有7958。接下来我们会把它输入到存在漏洞的程序中，看一下选择检查的索引值是哪些：

    
    
    h0mbre@pwn:~/fuzzing$ vuln Canon_40D.jpg 
    [>] Analyzing file: Canon_40D.jpg.
    [>] Canon_40D.jpg is 7958 bytes.
    [>] Check 1 no.: 2626
    [>] Check 2 no.: 3979
    [>] Check 3 no.: 5331
    [>] Check 1 failed.
    

可以看到选择了索引`2626`、`3979`和`5331`进行测试，并且该文件未通过第一次检查，因为该位置的字节不是`x6c`。

## 实验1：只通过一次检查

让我们移除第二个和第三个检查，看看当只需要通过一次检查时，我们的模糊测试器在测试文件上的性能如何。

我把第二个和第三个检查注释掉了。

    
    
    check_one(original_file.data, checkNum1);
    //check_two(original_file.data, checkNum2);
    //check_three(original_file.data, checkNum3);
    
    vuln(original_file.data, original_file.length);
    

接下来，我们会把上面没有通过第一次检查的JPEG文件输入到我们的模糊测试器中，对其进行变异，然后将其发送给存在漏洞的程序中，看看是不是会发生崩溃。要记得，在每次的模糊测试迭代中，模糊测试器最多会更改7958字节中的159字节。如果模糊测试器能够在索引`2626`处随机插入一个`x6c`，那么我们就会通过第一个检查，执行会进行到存在漏洞的函数处，并引发崩溃。让我们运行100万次该模糊测试器，看看会发生多少次崩溃。

    
    
    h0mbre@pwn:~/fuzzing$ ./fuzzer Canon_40D.jpg 1000000
    [>] Size of file: 7958 bytes.
    [>] Flipping up to 159 bytes.
    [>] Fuzzing for 1000000 iterations...
    [>] Crashes: 88
    [>] Fuzzing completed, exiting...
    

所以在100万次迭代中，一共发生了88次崩溃。
所以只有大约0.0088%的迭代通过了第一次检查，并进入到存在漏洞的函数中。再仔细检查一遍发生崩溃的逻辑，确保在任何代码中都没有错误（我用American
fuzzy
lop在QEMU模式下(模拟没有源代码的情况)启用所有检查对存在漏洞的程序进行了14个小时的模糊测试，并没有让其崩溃，所以我希望它里面没有任何我尚未发现的错误😬。）

    
    
    h0mbre@pwn:~/fuzzing/ccrashes$ vuln 998636.11 
    [>] Analyzing file: 998636.11.
    [>] 998636.11 is 7958 bytes.
    [>] Check 1 no.: 2626
    [>] Check 2 no.: 3979
    [>] Check 3 no.: 5331
    [>] Passed all checks!
    Segmentation fault
    

所以把引发崩溃的文件输入到存在漏洞的程序中确实会引发崩溃，太棒了。

_免责声明：这里要涉及到一些数学知识了，我不保证这部内容是正确的。我甚至从像@Firzen14这么聪明的人那里寻求了帮助，但仍然无法对自己的数学水平拥有百分之百的信心。但是，我确实对这里涉及的系统进行了数亿次的仿真，而实验数据的结果非常接近数学证明中得到的结果。因此，即使并不十分正确，但它至少已经能够证明我想要证明的观点了。_

接下来试着计算一下通过第一次检查并引发崩溃的可能性。我们需要克服的第一个障碍是要保证选择变异的索引值是`2626`。如果该位置没有发生变化，我们已经知道默认情况下这个位置的值与检查中的值并不匹配，所以不会通过检查。因为我们要进行159次的选择字节并变异的操作，而选择的范围有7958个字节，所以选择到索引`2626`处的字节进行变异的概率应该是`159/7958`，即`0.0199798944458407`。

第二个障碍是，我们要保证修改后的字节是`x6c`，而模糊测试器有255个字节值可供选择。因此，一旦选择了该位置字节进行变异，将其精确地修改为`x6c`的概率是`1/255`，即`0.003921568627451`。

因此，这两种情况同时发生的概率应该为`0.0199798944458407` *
`0.003921568627451`（约等于0.0078％），如果乘以100万，会引发大约78次崩溃。这个值已经很接近88了，鉴于实验是随机的，可能会有一些差异。

因此，此次实验的结论是，普通的模糊测试器能够比较可靠地通过一次检查并到达存在漏洞的函数。接下来看一下添加第二个检查之后情况会如何变化。

## 实验2：通过两次检查

这次数学问题变得更加庞大。但正如我之前所说，我对该事件已经进行了数亿次的模拟，最后的结果与我计算出来的数字非常接近。

我认为让字节值与检查值匹配非常简单，概率总是为1/255，但是在159次选择中同时选中两个确定的索引值并进行变异且的概率就有些复杂了。我运行了一个模拟器，查看同时选中两个索引值进行变异的次数，运行一段时间，经过3.9亿次迭代之后，总共发生了约155,000次。

    
    
    <snip>
    Occurences: 155070    Iterations: 397356879
    Occurences: 155080    Iterations: 397395052
    Occurences: 155090    Iterations: 397422769
    <snip>
    

`155090/397422769` == `.0003902393423261565`。而我认为的数学运算应该是`(159/7958)
*(158/7958)`，即`.0003966855142551934`。
可以看到这两个值相距很近，考虑到随机因素，它们相差不大。这应该已经足够说明问题了。

现在我们必须通过两次检查，使用我们的普通模糊测试器已经能够在数学上对这种情况发生的概率进行总结了，如下所示：

    
    
    ((159/7958) * (1/255)) == odds to pass first check
    odds to pass first check * (158/7958) == odds to pass first check and have second index targeted for mutation
    odds to pass first check * ((158/7958) * (1/255)) == odds to have second index targeted for mutation and hold the correct value
    ((159/7958) * (1/255)) * ((158/7958) * (1/255)) == odds to pass both checks
    ((0.0199798944458407 * 0.003921568627451‬) * (0.0198542347323448 * 0.003921568627451)) == 6.100507716342904e-9
    

所以同时选中两个索引值并将其修改为检查值的概率约为`.000000006100507716342904`，即`.0000006100507716342904％`。

如果只启用一次检查，大约每12,820次迭代会发生一次崩溃。

如果启用两次检查，大约 **每1.63亿次迭代** 才会发生一次崩溃。

这确实是一个问题，我们的模糊测试器需要运行很长时间才能达到该迭代次数。在虚拟中执行时，该模糊测试器每秒大约执行1600次迭代。所以大约需要28个小时才能达到1.63亿次迭代。所以说多添加一次检查，发现漏洞的概率会呈指数级下降，更别说添加第三次检查了！

## 代码覆盖有什么用

如果我们的模糊测试器能够对代码覆盖进行分钟，就可以让这个问题更加易于管理。

一般来说，模糊测试器中的代码覆盖跟踪系统会记录哪些输入覆盖到了程序中新的代码范围。存在很多方法达到该目的。如果拥有源代码，你就可以使用其他工具对其进行重新编译，在到达新的代码范围的时候通知模糊测试器。[@gamozolabs](https://github.com/gamozolabs
"@gamozolabs")发布了一个非常棒的Windows用户域代码覆盖系统，该系统中使用了一个运行速度极快的调试器，它会在目标二进制文件中设置数百万个断点，并在到达每个断点时慢慢对断点进行删除，该工具叫做‘[mesos](https://github.com/gamozolabs/mesos)’。
一旦模糊测试器发现某个变异的输入到达了新的代码范围，就会将其保存下来，以便接下来重复使用，或者进一步进行变异从而覆盖更多代码范围。下图进行了一个简单的解释，但希望解释得足够清晰。

![](https://p0.ssl.qhimg.com/t0116e1ead215f70e0b.png)

我还没有在模糊测试器中添加代码覆盖追踪技术，但我们可以简单地对其进行模拟。假设我们的模糊测试器能够在约每13,000次中通过1次程序中的第一个检查，并到达第二个检查。

在输入第一次达到第二个检查时，就可以认为它到达了新的代码范围。这种情况下，新的智能模糊测试器应该能够保存该输入。然后把让该输入通过变异器，并希望其能再次到达相同的代码范围，并有可能覆盖更多的代码范围。

让我们演示一下这一过程。先修改文件`Canon_40D.jpg`，让其索引`2626`处的字节为`x6c`，然后将其输入到我们的存在漏洞的程序中。

    
    
    h0mbre@pwn:~/fuzzing$ vuln Canon_altered.jpg 
    [>] Analyzing file: Canon_altered.jpg.
    [>] Canon_altered.jpg is 7958 bytes.
    [>] Check 1 no.: 2626
    [>] Check 2 no.: 3979
    [>] Check 2 failed.
    

可以看到它通过了第一次检查，但是第二次检查失败了。接下来使用这个`Canon_altered.jpg`文件作为我们的基本输入，来模拟存在代码覆盖跟踪系统的模糊测试器，看看只进行两次检查的时候会发生多少次崩溃。

    
    
    h0mbre@pwn:~/fuzzing$ ./fuzzer Canon_altered.jpg 1000000
    [>] Size of file: 7958 bytes.
    [>] Flipping up to 159 bytes.
    [>] Fuzzing for 1000000 iterations...
    [>] Crashes: 86
    [>] Fuzzing completed, exiting...
    

所以说，使用这个能够提高代码覆盖（即能够通过第一次检查）的文件作为基本输入，并让其通过变异器，我们能够通过86次第二次检查。从本质上说，我们把之前遇到的指数级问题转化成了一开始只需要进行一次检查的问题。真正的模糊测试器在工作时还需要考虑很多其他因素，但我在这里只想简单地说明这种技术可以把指数问题简化为更易于管理的问题。

我们把概率只有`((0.0199798944458407 * 0.003921568627451‬) * (0.0198542347323448 *
0.003921568627451)) == 6.100507716342904e-9`的问题简化到了概率接近`(0.0199798944458407 *
0.003921568627451)‬`的问题，这对我们来说是一个巨大的胜利。

但也存在一些细节问题没有讨论，让修改后的文件通过突变器的过程可能有一些副作用：它可能会改变索引`2626`处的字节值，这样我们甚至都无法通过第一个检查；也有可能会使文件的变化过大（在第一轮变异后，它和原始JPEG已经有2%的区别了），这样存在漏洞的程序可能会直接拒绝该输入，浪费了测试周期。

因此还有很多其他因素需要考虑，但希望上述内容可以清楚地说明代码覆盖能够帮助模糊测试器对目标二进制文件进行更全面的测试。

## 结论

网络上存在很多关于各类代码覆盖技术的资源，如果你感兴趣的话，一定要关注并阅读有关该主题的更多信息。@carste1n发布了一系列很棒的文章，在里面逐步地对模糊测试器进行改进，最新文章位于：<https://carstein.github.io/2020/05/21/writing-simple-fuzzer-4.html>

之后我们可以在我们的普通模糊测试器中添加有关代码覆盖追踪的代码，并且把本文中的漏洞程序作为基准，用于判断代码覆盖技术的有效性。

一些有趣的注意事项：我用American fuzzy
lop，对启用了三个检查的漏洞程序进行了大约13个小时的模糊测试，没能让它崩溃！我不知道为什么会这么难。如果只启用两个检查的话，AFL可以很快的找到崩溃。可能是我的测试中存在问题吧，我不确定。

期待下一篇文章！

本文翻译自h0mbre.github.io [原文链接](https://h0mbre.github.io/Fuzzing-Like-A-Caveman-3/#)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **zoemurmure** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/207307](/post/id/207307)

安全客 - 有思想的安全新媒体

本文转载自: [h0mbre.github.io](https://h0mbre.github.io/Fuzzing-Like-A-Caveman-3/#)

如若转载,请注明出处： <https://h0mbre.github.io/Fuzzing-Like-A-Caveman-3/#>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Fuzzing](/tag/Fuzzing)

 **+1** __9赞

 __收藏

![](https://p1.ssl.qhimg.com/t0148810f786e0f31fb.png) zoemurmure

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

