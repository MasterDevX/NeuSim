                lw          0               10              operand     operand -> reg[10]
                xidiv       @operandPTR     @dividorPTR     20          step = operand / dividor -> reg[20]; swap opernd and dividor
                lw          0               30              stepPTR     step pointer -> reg[30]
                sw          0               20              400         step -> mem[400]
                sw          0               30              500         step pointer -> mem[500]
loop:           add         125             10              125         result + operand -> result (reg[125])
                add         10              @500            10          operand + step -> operand (reg[10])
                dec         @counterPTR                                 decrement loop counter
                jmg         @counterPTR     0               loop        loop if counter > 0
                halt                                                    shutdown
operand:	    .fill	    8
dividor:	    .fill	    2
counter:	    .fill	    14
stepPTR:        .fill       400
operandPTR:     .fill       operand
dividorPTR:     .fill       dividor
counterPTR:     .fill       counter