# -*- coding: utf-8 -*-

import re
import os
import sys
from constants import TO_TRANSLATE_FILE, FILE_EXTENSION, READ_FILE_EXTENSION, \
    A_INSTRUCTION_START, LOOP_START, A_ZERO_COMP, A_ONE_COMP, \
    DEST_DICT, JUMP_DICT


class Assembler:
    init_symbol_address = 16
    symbol_dict = {
        "R0": "0", "R1": "1",
        "R2": "2", "R3": "3",
        "R4": "4", "R5": "5",
        "R6": "6", "R7": "7",
        "R8": "8", "R9": "9",
        "R10": "10", "R11": "11",
        "R12": "12", "R13": "13",
        "R14": "14", "R15": "15",
        "SCREEN": "16384", "KBD": "24576",
        "SP": "0", "LCL": "1", "ARG": "2",
        "THIS": "3", "THAT": "4"
    }

    @staticmethod
    def read_file():
        """
        read contents from the specified file
        :return: array of string
            text lines
        """
        try:
            if not (os.path.exists(TO_TRANSLATE_FILE) or os.path.isfile(TO_TRANSLATE_FILE)):
                raise FileNotFoundError

            file = open(TO_TRANSLATE_FILE, 'r')
            lines = file.readlines()
            file.close()
            return lines
        except FileNotFoundError:
            if not file.closed:
                file.close()
            print("Couldn't find a file {} ".format(TO_TRANSLATE_FILE))
            raise

    @staticmethod
    def write_file(text_lines):
        """
         write the result of assembling into a .hack file
        in the same folder than the original one (overwrite if it exists)
        :param text_lines: array of string
            texts to write
        """
        try:
            folder_path = os.path.dirname(TO_TRANSLATE_FILE) + "/"
            match = re.match(r'^({})(.*)({})$'.format(folder_path, "\\" + READ_FILE_EXTENSION), TO_TRANSLATE_FILE)
            if not match:
                raise FileNotFoundError
            write_path = folder_path + match.groups()[1] + FILE_EXTENSION
            file = open(write_path, 'w')
            file.write("\n".join(text_lines))
            file.close()
        except Exception as e:
            if not file.closed:
                file.close()
            print("Unexpected error:", sys.exc_info()[0])
            raise

    @staticmethod
    def get_comp_a(comp):
        """
        get comp instruction in binary
        :param comp: string
            comp instruction in non-binary
        :return: string
            comp instruction in binary
        """
        if comp in A_ZERO_COMP:
            return "0" + A_ZERO_COMP.get(comp)
        elif comp in A_ONE_COMP:
            return "1" + A_ONE_COMP.get(comp)
        return None

    @staticmethod
    def decimal_to_binary(decimal):
        return format(decimal if decimal >= 0 else (1 << 16) + decimal, '016b')

    def a_instruction_to_binary(self, line):
        """
            extract programs from text lines
            :param line : array of string
                lines of texts read from the target file
            :return: array of string
                program lines
        """
        after_at = line[1:]
        # non-symbolic
        if re.match(r'^[0-9]+$', after_at):
            return self.decimal_to_binary(int(after_at))
        # symbolic
        elif after_at in self.symbol_dict:
            return self.decimal_to_binary(int(self.symbol_dict[after_at]))
        else:
            print("not in ", after_at)
        return after_at

    def c_instruction_to_binary(self, line):
        """
            translate C-instruction to binary
            :param line : string
                C-instruction
            :return: result : string
                C-instruction in binary (111 a c1~c6 d1~d3 j1~j3)
        """
        result = "111"  # static
        match = re.match(r'^(.*)=(.*)$|^(.*);(.*)$', line)
        if not match:
            raise ValueError('Invalid C Instruction')
        if match.groups()[0] is not None:  # no jump instruction
            dest = match.groups()[0]
            comp = match.groups()[1]
            jump = "null"
        else:
            dest = "null"
            comp = match.groups()[2]
            jump = match.groups()[3]

        comp_bi = self.get_comp_a(comp)  # a c1~c6
        dest_bi = DEST_DICT.get(dest)  # d1~d3
        jump_bi = JUMP_DICT.get(jump)  # j1~j3

        result += comp_bi + dest_bi + jump_bi
        return result

    def extract_program_lines(self, text_lines):
        """
            extract programs from text lines
            :param text_lines : array of string
                lines of texts read from the target file
            :return: program_lines : array of string
                program lines
        """
        program_lines = []
        line_index = 0
        label_lists = []
        for line in text_lines:
            if not re.compile('^[\r\n]$').match(line) and line:
                match_comment = re.match(r'^(.*)(//)(.*)$', line)
                target = match_comment.groups()[0].strip() if match_comment else line.strip()
                if not target:
                    continue
                if target.startswith(LOOP_START):
                    self.symbol_dict[target[1:-1]] = str(line_index)
                    label_lists.append(target[1:-1])
                    continue
                program_lines.append(target)
                line_index += 1

        for program_line in program_lines:
            if program_line.startswith(A_INSTRUCTION_START) \
                    and program_line[1:] not in self.symbol_dict \
                    and re.match(r'^.*[^0-9].*$', program_line[1:])\
                    and program_line[1:] not in label_lists:
                self.symbol_dict[program_line[1:]] = str(self.init_symbol_address)
                self.init_symbol_address += 1

        return program_lines

    def translate_programs(self, lines):
        """
        translate text lines into instructions in binary
        :param lines: text lines to translate
        :return: instructions in binary
        """
        result = []

        for line in lines:
            if line.startswith(A_INSTRUCTION_START):  # A-instruction
                result.append(self.a_instruction_to_binary(line))
            else:  # C-instruction
                result.append(self.c_instruction_to_binary(line))
        return result

    def main(self):
        try:
            program_lines = self.extract_program_lines(self.read_file())
            translated_lines = self.translate_programs(program_lines)
            self.write_file(translated_lines)
        except FileNotFoundError:
            print("Couldn't find a file")
            raise
        except ValueError as err:
            print("ValueError: {}".format(err))
        except Exception as err:
            print("Unexpected error:", err)


if __name__ == "__main__":
    assembler = Assembler()
    assembler.main()
    sys.exit()
