## Question 2

### (a) Memory Space Population (64Kb ROM, 256Kb RAM, and 8255 PPI)
*(Note: As specified in the question paper, $64\text{Kb} = 8\text{KB}$ where $8K \times 8 = 8\text{KB}$, and $256\text{Kb} = 32\text{KB}$ where $32K \times 8 = 32\text{KB}$)*[cite: 6].

* **Total Address Space:** The Intel 8085A processor provides a 16-bit address bus (`0000H` to `FFFFH`), supporting $64\text{ KB}$ of total addressable memory[cite: 6].
* **ROM ($8\text{ KB}$):** Requires 13 address lines ($A_{12}-A_0$) implemented via an $8\text{K} \times 8$ ROM chip, mapped from `0000H` to `1FFFH`[cite: 6].
* **RAM ($32\text{ KB}$):** Requires 15 address lines ($A_{14}-A_0$) implemented using RAM chips mapped from `2000H` to `9FFFH`[cite: 6].
* **Intel 8255 PPI:** Requires 4 internal registers (Ports A, B, C, and Control Word Register), needing 2 address lines ($A_1, A_0$) mapped via higher-order address decoding[cite: 6].
* **Decoder Circuitry:** A 3-to-8 decoder (such as 74LS138) connected to upper address lines ($A_{15}, A_{14}, A_{13}$) generates the respective chip select ($\overline{CS}$) signals for the memory blocks and peripherals[cite: 6].

---

### (b) Assembly Language Subroutine `smallest (int a[], unsigned int n)`
```assembly
; Subroutine: smallest
; Input: HL points to array a[], Register B contains n (number of elements)
; Output: Register A contains the smallest element
smallest:
    MOV A, M       ; Load first element into A as initial minimum
    DCR B          ; Decrement count
    JZ end_small   ; If n = 1, return
loop_start:
    INX HL         ; Increment pointer to next array element
    MOV C, M       ; Load current element into C
    CMP C          ; Compare A with C (A - C)
    JC skip_update ; If A < C, keep current minimum in A
    MOV A, C       ; Otherwise, update minimum in A
skip_update:
    DCR B          ; Decrement loop counter
    JNZ loop_start ; Repeat until all elements are checked
end_small:
    RET            ; Return with smallest element in A
```[cite: 6]

---

## Question 3

### System Design for 4 Square Waves (10Hz, 20Hz, 30Hz, and 40Hz)
* **Design Approach:** To generate square waves of $10\text{ Hz}$, $20\text{ Hz}$, $30\text{ Hz}$, and $40\text{ Hz}$ on 4 output lines, an Intel 8253 Programmable Interval Timer (PIT) or an 8255 PPI can be interfaced with the 8085 system[cite: 6].
* **Half-Periods ($T/2$):**
  * $10\text{ Hz} \implies T = 100\text{ ms}$ (Toggle every $50\text{ ms}$)[cite: 6]
  * $20\text{ Hz} \implies T = 50\text{ ms}$ (Toggle every $25\text{ ms}$)[cite: 6]
  * $30\text{ Hz} \implies T = 33.3\text{ ms}$ (Toggle every $16.6\text{ ms}$)[cite: 6]
  * $40\text{ Hz} \implies T = 25\text{ ms}$ (Toggle every $12.5\text{ ms}$)[cite: 6]
* **Hardware Interfacing:** 4 output pins of an 8255 PPI port (e.g., PC0 to PC3) connect to the square wave output channels, driven by a timer-based interrupt service routine or a calibrated polling loop[cite: 6].

---

## Question 4

### (a) Role of the Monitor Program in an SDK (e.g., SDK-85)
The Monitor Program is the core firmware stored in the ROM of a Microprocessor System Development Kit[cite: 6]. Its primary functions include:
1. **Command Processing:** Reading the hexadecimal keypad and parsing commands to inspect or edit memory and registers[cite: 6].
2. **Execution Management:** Launching user applications via the `GO` command and managing hardware breakpoints[cite: 6].
3. **Peripheral Multiplexing:** Refreshing the onboard 7-segment LED display and scanning the keyboard matrix[cite: 6].
4. **System Initialization:** Setting up default stack pointers, interrupt vectors, and hardware peripherals upon a reset[cite: 6].

---

### (b) Essential Information a User Must Know to Utilize an SDK
To use an SDK effectively, a developer must know[cite: 6]:
* **Memory Map:** The precise address boundaries separating the monitor ROM space from the user RAM space[cite: 6].
* **Keypad Operations:** The correct sequence of keys to enter opcodes, examine memory, and execute programs[cite: 6].
* **I/O Port Assignments:** Base addresses for built-in peripherals like the 8255 PPI and display units[cite: 6].
* **Interrupt Structure:** Which interrupt lines are consumed by the monitor firmware versus those available for user projects[cite: 6].

---

## Question 5

### Short Notes

#### (a) I/O Mapped I/O for Intel 8085A
* Maintains completely separate address spaces for memory ($64\text{ KB}$) and I/O ports ($256$ ports from `00H` to `FFH`)[cite: 6].
* Uses dedicated assembly instructions: `IN` and `OUT`[cite: 6].
* Employs specialized control lines ($\overline{\text{IOR}}$ and $\overline{\text{IOW}}$) rather than memory access lines, leaving full main memory capacity available for code storage[cite: 6].

#### (b) Memory Folding (Aliasing)
* Occurs when higher-order address lines are left unconnected or partially decoded during hardware design[cite: 6].
* Because the address decoder ignores these upper bits, the same physical memory chip responds across multiple redundant address blocks in the system memory map[cite: 6].

#### (c) Software vs. Hardware Interrupts
* **Hardware Interrupts:** Triggered asynchronously by external hardware devices via dedicated CPU pins (`TRAP`, `RST 7.5`, `RST 6.5`, `RST 5.5`, `INTR`)[cite: 6].
* **Software Interrupts:** Triggered synchronously by explicit instructions (`RST 0` through `RST 7`) embedded within program code, typically used for system calls and debugging traps[cite: 6].
