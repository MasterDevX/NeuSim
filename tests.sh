#!/bin/bash

assemble_bad_usage () {
    ./assemble.py
}

assemble_bad_in_file () {
    ./assemble.py test.as test.mc
}

assemble_bad_out_file () {
    echo "halt" > test.as
    ./assemble.py test.as test/mc
}

assemble_label_multiple_def () {
    echo "label: noop" > test.as
    echo "label: halt" >> test.as
    ./assemble.py test.as test.mc
}

assemble_label_undefined () {
    echo "beq 0 0 label" > test.as
    ./assemble.py test.as test.mc
}

assemble_instr_missing () {
    echo "label:" > test.as
    ./assemble.py test.as test.mc
}

assemble_instr_unrecognized () {
    echo "test" > test.as
    ./assemble.py test.as test.mc
}

assemble_instr_args_missing () {
    echo "add" > test.as
    ./assemble.py test.as test.mc
}

assemble_out_of_range_reg () {
    echo "dec 150" > test.as
    ./assemble.py test.as test.mc
}

assemble_out_of_range_mem () {
    echo "lw 0 1 99999999" > test.as
    ./assemble.py test.as test.mc
}

assemble_out_of_range_var () {
    echo ".fill 9999999999999999999999999" > test.as
    ./assemble.py test.as test.mc
}

run_bad_usage () {
    ./run.py
}

run_bad_in_file () {
    ./run.py test.mc
}

run_grid_overflow () {
    echo "add @p1 @p2 1" > test.as
    echo "op: .fill 9671406556917033397649407" >> test.as
    echo "p1: .fill op" >> test.as
    echo "p2: .fill op" >> test.as
    ./assemble.py test.as test.mc
    ./run.py test.mc
}

run_zero_division () {
    echo "xidiv @p1 0 1" > test.as
    echo "op: .fill 1" >> test.as
    echo "p1: .fill op" >> test.as
    ./assemble.py test.as test.mc
    ./run.py test.mc
}

run_opcode_unrecognized () {
    echo "6044629098073145873530880" > test.mc
    ./run.py test.mc
}

run_out_of_range_pc () {
    echo "beq 0 0 33554431" > test.as
    ./assemble.py test.as test.mc
    ./run.py test.mc
}

run_out_of_range_reg () {
    echo "604462909807323177287680" > test.mc
    ./run.py test.mc
}

run_out_of_range_mem () {
    echo "906694364710972250128385" > test.mc
    echo "33554432" >> test.mc
    ./run.py test.mc
}

tests=(
    assemble_bad_usage
    assemble_bad_in_file
    assemble_bad_out_file
    assemble_label_multiple_def
    assemble_label_undefined
    assemble_instr_missing
    assemble_instr_unrecognized
    assemble_instr_args_missing
    assemble_out_of_range_reg
    assemble_out_of_range_mem
    assemble_out_of_range_var
    run_bad_usage
    run_bad_in_file
    run_grid_overflow
    run_zero_division
    run_opcode_unrecognized
    run_out_of_range_pc
    run_out_of_range_reg
    run_out_of_range_mem
)

run_test () {
    echo "Running test: $test"
    output=$($@)
    status=$?
    if [ $status -eq 0 ]; then
        msg="successful termination"
    elif [ $status -eq 1 ]; then
        msg="invalid usage"
    elif [ $status -eq 2 ]; then
        msg="file I/O error"
    elif [ $status -eq 3 ]; then
        msg="compilation / simulation error"
    else
        msg="unknown error"
    fi
    echo "Caught exit code: $status ($msg)"
    echo "Program output:"
    if echo "$output" | grep -q '[!]'; then
        echo "$output" | grep '[!]'
    else
        echo "$output"
    fi
    echo
}

for test in "${tests[@]}"; do
    run_test $test
done

rm -f test.as
rm -f test.mc

exit 0