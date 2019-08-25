// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)


// R0 * R1 = R2:
// for(i=1; i < R1; i++){
//   sum += R0;
// }
@R2
M=0
@i
M=1
@sum
M=0


@R0
D=M
@END
D;JEQ
@R1
D=M
@END
D;JEQ

(LOOP)
  @i
  D=M
  @R1
  D=D-M
  @STOP
  D;JGT // if (i - len) > 0

  @sum
  D=M
  @R0
  D=D+M
  @sum
  M=D // sum += len
  @i
  M=M+1
  @LOOP
  0;JMP

(STOP)
  @sum
  D=M
  @R2
  M=D // RAM[2] = sum
  @sum
  M=0
  @END
  0;JMP

(END)
  @END
  0;JMP
