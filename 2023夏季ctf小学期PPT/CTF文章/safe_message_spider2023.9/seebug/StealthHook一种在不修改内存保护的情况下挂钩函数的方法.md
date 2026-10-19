**作者：The_Itach1@知道创宇404实验室  
日期：2022年12月23日**

最近看了一下x86matthew关于hook方法的一篇文章<https://www.x86matthew.com/view_post?id=stealth_hook>，相对于传统的一些hook方式，个人认为StealthHook的最大优点并不在于不修改内存保护，而是其隐蔽性，这种hook方式是难以检测的，因为其没有直接作用于目标函数。

此hook方式，实际上并没有去hook目标函数，而是通过目标函数内的子函数，去获取了进入目标函数时，栈上保存的返回地址，通过修改这个地址，即可劫持执行流程，在函数返回前，执行我们的代码。

## hook样例-CreateFile

下面是其给出的例子。

    
    
    #include <stdio.h>
    #include <windows.h>
    
    DWORD dwGlobal_OrigCreateFileReturnAddr = 0;
    DWORD dwGlobal_OrigReferenceAddr = 0;
    
    void __declspec(naked) ModifyReturnValue()
    {
        // the original return address for the CreateFile call redirects to here
        _asm
        {
            // CreateFile complete - overwrite return value
            mov eax, 0x12345678
    
            // continue original execution flow (ecx is safe to overwrite at this point)
            mov ecx, dwGlobal_OrigCreateFileReturnAddr
            jmp ecx
        }
    }
    
    void __declspec(naked) HookStub()
    {
        // the hooked global pointer nested within CreateFile redirects to here
        _asm
        {
            // store original CreateFile return address
            mov eax, dword ptr [esp + 0x100]
            mov dwGlobal_OrigCreateFileReturnAddr, eax
    
            // overwrite the CreateFile return address
            lea eax, ModifyReturnValue
            mov dword ptr [esp + 0x100], eax
    
            // continue original execution flow
            mov eax, dwGlobal_OrigReferenceAddr
            jmp eax
        }
    }
    
    DWORD InstallHook()
    {
        BYTE *pModuleBase = NULL;
        BYTE *pHookAddr = NULL;
    
        // get base address of kernelbase.dll
        pModuleBase = (BYTE*)GetModuleHandle("kernelbase.dll");
        if(pModuleBase == NULL)
        {
            return 1;
        }
    
        // get ptr to function reference
        pHookAddr = pModuleBase + 0x1DF650;
    
        // store original value
        dwGlobal_OrigReferenceAddr = *(DWORD*)pHookAddr;
    
        // overwrite ptr to call HookStub
        *(DWORD*)pHookAddr = (DWORD)HookStub;
    
        return 0;
    }
    
    int main()
    {
        HANDLE hFile = NULL;
    
        // create temporary file (without hook)
        printf("Creating file #1...\n");
        hFile = CreateFile("temp_file_1.txt", GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        printf("hFile: 0x%X\n\n", hFile);
    
        // install hook
        printf("Installing hook...\n\n");
        if(InstallHook() != 0)
        {
            return 1;
        }
    
        // create temporary file (with hook)
        printf("Creating file #2...\n");
        hFile = CreateFile("temp_file_2.txt", GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        printf("hFile: 0x%X\n\n", hFile);
    
        return 0;
    }

上面的代码的作用就是钩取了CreatFile这个API函数，修改了其返回值为0x12345678，具体步骤如下。

  * Hook了kernelbase.dll+0x1DF650处的函数，这个函数是CreatFile内部会调用的一个子函数。
  * 在这个子函数执行前，将栈上CreatFile原本的返回地址保存下来，也就是[esp+0x100]的值，然后替换成了我们自己的函数ModifyReturnValue。
  * 子函数执行。
  * 最终会执行CreatFile函数最后的ret指令，但是此时栈上的返回地址以被修改，所以会先执行我们的函数，修改了eax，也就是返回值变成了0x12345678。
  * 最后mov eax, dwGlobal_OrigReferenceAddr jmp eax，回到真正的返回地址处。

下面来调试一下过程。

先是InstallHook()内部，Hook了一个子函数，其获取EAT中了某一子函数的地址，并且将其替换为了HookStub。
![](https://images.seebug.org/content/images/2022/12/23/1671774981000-1.png-w331s)

然后到第二次调用CreateFile的开头，我们查看一下，这时候ESP存放的返回地址是多少，实际上等下这里的值是会被修改的。
![](https://images.seebug.org/content/images/2022/12/23/1671774983000-2.png-w331s)

接着，我们本来会调用CreateFile内部的一个子函数，但是其已被我们hook现在变成了HookStub()函数，我们在HookStub()打断点，发现其对栈偏移100处进行了修改，这个地址保存的就是原CreateFile返回到main函数的返回地址。

HookStub()内部将栈上的地址先进行保存到全局变量，然后修改为了我们自己的一个函数，最后jmp到真正的子函数处。
![](https://images.seebug.org/content/images/2022/12/23/1671774983000-3.png-w331s)

然后在CreatFile函数内部最后的ret指令处打个断点，发现返回地址已被修改，不会跳转到main函数了，而是跳转到ModifyReturnValue()。
![](https://images.seebug.org/content/images/2022/12/23/1671774984000-4.png-w331s)

进入ModifyReturnValue()，发现其就是对eax(函数返回值)进行了修改，然后跳转到真正应该返回的地址。
![](https://images.seebug.org/content/images/2022/12/23/1671774985000-5.png-w331s)

最后结果如下，hook后，调用CreatFile函数的返回值会被修改为0x12345678。
![](https://images.seebug.org/content/images/2022/12/23/1671774985000-6.png-w331s)

整个过程还是比较清晰，也不是很复杂的hook过程，问题就在于，如何获取到子函数的地址，以及到目标函数的返回地址的栈偏移是多少，因为我们不可能自己去一个一个调试获取。

为了解决这个问题，x86matthew师傅开发了一款工具，用来获取可用的子函数地址，以及栈偏移。

## StealthHook工具

其先是注册了一个异常处理函数，用来处理EXCEPTION_SINGLE_STEP异常和EXCEPTION_ACCESS_VIOLATION异常。

    
    
    LONG WINAPI ExceptionHandler(EXCEPTION_POINTERS* ExceptionInfo)
    {
        NATIVE_VALUE dwReturnAddress = 0;
    
        // check exception code
        if (ExceptionInfo->ExceptionRecord->ExceptionCode == EXCEPTION_SINGLE_STEP)
        {
            if (dwGlobal_TraceStarted == 0)
            {
                //打在目标函数的硬件断点和此时的eip是否一致
                if (CURRENT_EXCEPTION_INSTRUCTION_PTR != ExceptionInfo->ContextRecord->Dr0)
                {
                    return EXCEPTION_CONTINUE_SEARCH;
                }
    
                //获取当前ESP寄存器的值
                dwGlobal_InitialStackPtr = CURRENT_EXCEPTION_STACK_PTR;
    
                //返回地址处打硬件断点
                ExceptionInfo->ContextRecord->Dr1 = *(NATIVE_VALUE*)dwGlobal_InitialStackPtr;
    
                // initial trace started
                dwGlobal_TraceStarted = 1;
            }
    
            // set debug control field
            ExceptionInfo->ContextRecord->Dr7 = DEBUG_REGISTER_EXEC_DR1;
    
            // check current instruction pointer
            if (CURRENT_EXCEPTION_INSTRUCTION_PTR == dwGlobal_Wow64TransitionStub)
            {
                // we have hit the wow64 transition stub - don't single step here, set a breakpoint on the current return address instead
                dwReturnAddress = *(NATIVE_VALUE*)CURRENT_EXCEPTION_STACK_PTR;
                ExceptionInfo->ContextRecord->Dr0 = dwReturnAddress;
                ExceptionInfo->ContextRecord->Dr7 |= DEBUG_REGISTER_EXEC_DR0;
            }
            else if (CURRENT_EXCEPTION_INSTRUCTION_PTR == ExceptionInfo->ContextRecord->Dr1)
            {
                //到达返回地址后，删除所有断点
                ExceptionInfo->ContextRecord->Dr7 = 0;
            }
            else
            {
                // scan all modules for the current instruction pointer
                ScanAllModulesForAddress(CURRENT_EXCEPTION_INSTRUCTION_PTR, CURRENT_EXCEPTION_STACK_PTR);
    
                // single step
                ExceptionInfo->ContextRecord->EFlags |= SINGLE_STEP_FLAG;
            }
    
            // continue execution
            return EXCEPTION_CONTINUE_EXECUTION;
        }
        else if (ExceptionInfo->ExceptionRecord->ExceptionCode == EXCEPTION_ACCESS_VIOLATION)
        {
            // access violation - check if the eip matches the expected value
            if (CURRENT_EXCEPTION_INSTRUCTION_PTR != OVERWRITE_REFERENCE_ADDRESS_VALUE)
            {
                return EXCEPTION_CONTINUE_SEARCH;
            }
    
            // caught current hook successfully
            dwGlobal_CurrHookExecuted = 1;
    
            // restore correct instruction pointer
            CURRENT_EXCEPTION_INSTRUCTION_PTR = dwGlobal_OriginalReferenceValue;
    
            // continue execution
            return EXCEPTION_CONTINUE_EXECUTION;
        }
    
        return EXCEPTION_CONTINUE_SEARCH;
    }

先不看这个异常处理，后面具体分析。

先看BeginTrace()函数，这个函数的参数就是目标函数的地址。

    
    
    DWORD BeginTrace(BYTE* pTargetFunction)
    {
        CONTEXT DebugThreadContext;
    
        // reset values
        dwGlobal_TraceStarted = 0;
        dwGlobal_SuccessfulHookCount = 0;
        dwGlobal_AddressCount = 0;
    
        // set initial debug context - hardware breakpoint on target function
        memset((void*)&DebugThreadContext, 0, sizeof(DebugThreadContext));
        DebugThreadContext.ContextFlags = CONTEXT_DEBUG_REGISTERS;
        DebugThreadContext.Dr0 = (NATIVE_VALUE)pTargetFunction;
        DebugThreadContext.Dr7 = DEBUG_REGISTER_EXEC_DR0;
        if (SetThreadContext(GetCurrentThread(), &DebugThreadContext) == 0)
        {
            return 1;
        }
    
        // execute the target function
        ExecuteTargetFunction();
    
        return 0;
    }

其在目标函数地址处，打上了硬件断点，这个异常会被我们自己的异常处理函数所捕获，获取了esp寄存器的值，并且在返回地址处又打了个硬件断点。

    
    
    if (dwGlobal_TraceStarted == 0)
    {
        //打在目标函数的硬件断点和此时的eip是否一致
        if (CURRENT_EXCEPTION_INSTRUCTION_PTR != ExceptionInfo->ContextRecord->Dr0)
        {
            return EXCEPTION_CONTINUE_SEARCH;
        }
        //获取当前ESP寄存器的值
        dwGlobal_InitialStackPtr = CURRENT_EXCEPTION_STACK_PTR;
    
        //返回地址处打硬件断点
        ExceptionInfo->ContextRecord->Dr1 = *(NATIVE_VALUE*)dwGlobal_InitialStackPtr;
    
        // initial trace started
        dwGlobal_TraceStarted = 1;
    }

接着执行，ScanAllModulesForAddress()函数是用来扫描子函数的，其参数是当前eip和当前esp，然后将EFlags设置为了单步执行，意味着后面每执行一条汇编指令，都会触发单步异常，从而进入这个异常处理函数。

    
    
    // scan all modules for the current instruction pointer
    ScanAllModulesForAddress(CURRENT_EXCEPTION_INSTRUCTION_PTR, CURRENT_EXCEPTION_STACK_PTR);
    
    // single step
    ExceptionInfo->ContextRecord->EFlags |= SINGLE_STEP_FLAG;

当进入到合适的子函数头部中时，就会调用下面的遍历过程，计算出其对应的dll以及函数地址，和栈偏移。下面两个函数，一个遍历模块，一个遍历EAT表，当遍历出子函数时，就会用最初目标函数的的esp-现在的esp，从而得到栈偏移。

    
    
    DWORD ScanModuleForAddress(BYTE* pModuleBase, char* pModuleName, NATIVE_VALUE dwAddr, NATIVE_VALUE dwStackPtr)
    {
        IMAGE_DOS_HEADER* pImageDosHeader = NULL;
        IMAGE_NT_HEADERS* pImageNtHeader = NULL;
        IMAGE_SECTION_HEADER* pCurrSectionHeader = NULL;
        DWORD dwReadOffset = 0;
        BYTE* pCurrPtr = NULL;
        MEMORY_BASIC_INFORMATION MemoryBasicInfo;
        DWORD dwStackDelta = 0;
    
        // get dos header
        pImageDosHeader = (IMAGE_DOS_HEADER*)pModuleBase;
        if (pImageDosHeader->e_magic != 0x5A4D)
        {
            return 1;
        }
    
        // get nt header
        pImageNtHeader = (IMAGE_NT_HEADERS*)(pModuleBase + pImageDosHeader->e_lfanew);
        if (pImageNtHeader->Signature != IMAGE_NT_SIGNATURE)
        {
            return 1;
        }
    
        // loop through all sections
        for (DWORD i = 0; i < pImageNtHeader->FileHeader.NumberOfSections; i++)
        {
            // get current section header
            pCurrSectionHeader = (IMAGE_SECTION_HEADER*)((BYTE*)&pImageNtHeader->OptionalHeader + pImageNtHeader->FileHeader.SizeOfOptionalHeader + (i * sizeof(IMAGE_SECTION_HEADER)));
    
            // ignore executable sections
            if (pCurrSectionHeader->Characteristics & IMAGE_SCN_MEM_EXECUTE)
            {
                continue;
            }
    
            // scan current section for the target address
            dwReadOffset = pCurrSectionHeader->VirtualAddress;
            for (DWORD ii = 0; ii < pCurrSectionHeader->Misc.VirtualSize / sizeof(NATIVE_VALUE); ii++)
            {
                // check if the current value contains the target address
                pCurrPtr = pModuleBase + dwReadOffset;
                if (*(NATIVE_VALUE*)pCurrPtr == dwAddr)
                {
                    // found target address - check memory protection
                    memset((void*)&MemoryBasicInfo, 0, sizeof(MemoryBasicInfo));
                    if (VirtualQuery(pCurrPtr, &MemoryBasicInfo, sizeof(MemoryBasicInfo)) != 0)
                    {
                        // check if the current region is writable
                        if (MemoryBasicInfo.Protect == PAGE_EXECUTE_READWRITE || MemoryBasicInfo.Protect == PAGE_READWRITE)
                        {
                            // ensure the address list is not full
                            if (dwGlobal_AddressCount >= MAXIMUM_STORED_ADDRESS_COUNT)
                            {
                                printf("Error: Address list is full\n");
                                return 1;
                            }
    
                            // store current address in list
                            dwGlobal_AddressList[dwGlobal_AddressCount] = (NATIVE_VALUE)pCurrPtr;
                            dwGlobal_AddressCount++;
    
                            // calculate stack delta
                            dwStackDelta = (DWORD)(dwGlobal_InitialStackPtr - dwStackPtr);
    
                            printf("Instruction 0x%p referenced at %s!0x%p (sect: %s, virt_addr: 0x%X, stack delta: 0x%X)\n", (void*)dwAddr, pModuleName, (void*)pCurrPtr, pCurrSectionHeader->Name, dwReadOffset, dwStackDelta);
                        }
                    }
                }
    
                // increase read offset
                dwReadOffset += sizeof(NATIVE_VALUE);
            }
        }
    
        return 0;
    }
    
    DWORD ScanAllModulesForAddress(NATIVE_VALUE dwAddr, NATIVE_VALUE dwStackPtr)
    {
        DWORD dwPEB = 0;
        PEB* pPEB = NULL;
        LDR_DATA_TABLE_ENTRY* pCurrEntry = NULL;
        LIST_ENTRY* pCurrListEntry = NULL;
        DWORD dwEntryOffset = 0;
        char szModuleName[512];
        DWORD dwStringLength = 0;
    
        // get PEB ptr
    #if _WIN64
        pPEB = (PEB*)__readgsqword(0x60);
    #else
        pPEB = (PEB*)__readfsdword(0x30);
    #endif
    
        // get InMemoryOrderLinks offset in structure
        dwEntryOffset = (DWORD)((BYTE*)&pCurrEntry->InLoadOrderLinks - (BYTE*)pCurrEntry);
    
        // get first link
        pCurrListEntry = pPEB->Ldr->InLoadOrderModuleList.Flink;
    
        // enumerate all modules
        for (;;)
        {
            // get ptr to current module entry
            pCurrEntry = (LDR_DATA_TABLE_ENTRY*)((BYTE*)pCurrListEntry - dwEntryOffset);
    
            // check if this is the final entry
            if (pCurrEntry->DllBase == 0)
            {
                // end of module list
                break;
            }
    
            // ignore main exe module
            if (pCurrEntry->DllBase != pGlobal_ExeBase)
            {
                // convert module name to ansi
                dwStringLength = pCurrEntry->BaseDllName.Length / sizeof(wchar_t);
                if (dwStringLength > sizeof(szModuleName) - 1)
                {
                    dwStringLength = sizeof(szModuleName) - 1;
                }
                memset(szModuleName, 0, sizeof(szModuleName));
                wcstombs(szModuleName, pCurrEntry->BaseDllName.Buffer, dwStringLength);
    
                // scan current module
                ScanModuleForAddress((BYTE*)pCurrEntry->DllBase, szModuleName, dwAddr, dwStackPtr);
            }
    
            // get next module entry in list
            pCurrListEntry = pCurrListEntry->Flink;
        }
    
        return 0;
    }

最终会将所有合适的子函数都保存到dwGlobal_AddressList[dwGlobal_AddressCount]这个全局数组中。

然后会验证一下获取到的这些子函数地址的可用性。

    
    
    {
        // attempt to hook the target function at all referenced instructions found earlier
        for (DWORD i = 0; i < dwGlobal_AddressCount; i++)
        {
            printf("\nOverwriting reference: 0x%p...\n", (void*)dwGlobal_AddressList[i]);
    
            // reset flag
            dwGlobal_CurrHookExecuted = 0;
    
            // store original value
            dwGlobal_OriginalReferenceValue = *(NATIVE_VALUE*)dwGlobal_AddressList[i];
    
            // overwrite referenced value with placeholder value
            *(NATIVE_VALUE*)dwGlobal_AddressList[i] = OVERWRITE_REFERENCE_ADDRESS_VALUE;
    
            printf("Calling target function...\n");
    
            // execute target function
            ExecuteTargetFunction();
    
            // restore original value
            *(NATIVE_VALUE*)dwGlobal_AddressList[i] = dwGlobal_OriginalReferenceValue;
    
            // check if the hook was executed
            if (dwGlobal_CurrHookExecuted == 0)
            {
                // hook wasn't executed - ignore
                printf("Failed to catch hook\n");
            }
            else
            {
                // hook was executed - this address can be used to hook the target function
                printf("Hook caught successfully!\n");
                dwGlobal_SuccessfulHookCount++;
            }
        }
    
        return 0;
    }

其将其函数地址修改为OVERWRITE_REFERENCE_ADDRESS_VALUE，导致这个子函数不可用，然后就会触发EXCEPTION_ACCESS_VIOLATION异常，由我们的异常处理函数来处理，主要就是修改dwGlobal_CurrHookExecuted
= 1，代表测试成功。

    
    
    else if (ExceptionInfo->ExceptionRecord->ExceptionCode == EXCEPTION_ACCESS_VIOLATION)
    {
        // access violation - check if the eip matches the expected value
        if (CURRENT_EXCEPTION_INSTRUCTION_PTR != OVERWRITE_REFERENCE_ADDRESS_VALUE)
        {
            return EXCEPTION_CONTINUE_SEARCH;
        }
    
        // caught current hook successfully
        dwGlobal_CurrHookExecuted = 1;
    
        // restore correct instruction pointer
        CURRENT_EXCEPTION_INSTRUCTION_PTR = dwGlobal_OriginalReferenceValue;
    
        // continue execution
        return EXCEPTION_CONTINUE_EXECUTION;
    }

## 总结

此hook方式的思路还是很新颖，同样也存在一些缺点，那就是只能在目标函数执行完成后，修改流程，并且可能hook的子函数万一被其他函数也调用了，这时候修改栈上的值，是否会有触发崩溃可能性呢。

通过这个工具的代码，也学到不少东西，异常处理，打硬件断点等等，可惜的是每想要hook一个API函数，都必须要去修改一下源码。

## 参考

<https://www.x86matthew.com/view_post?id=stealth_hook>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2035/>

