# Code Samples: T1574 LD_PRELOAD Hijacking

This folder contains code examples for abusing LD_PRELOAD to inject malicious libraries on Linux systems.

## Example: Malicious Shared Library (C)
```c
// Minimal shared library for LD_PRELOAD
#include <stdio.h>
__attribute__((constructor)) void preload() {
    printf("Malicious LD_PRELOAD library loaded!\n");
}
```

## Example: Set LD_PRELOAD
```bash
export LD_PRELOAD=/path/to/malicious.so
ls
```
