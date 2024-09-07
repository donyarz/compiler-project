from da_parser import Parser

INPUT_FILE_NAME = 'input.txt'

OUTPUT_FILE_NAME = 'output.txt'
SEMANTIC_ERROR_FILE_NAME = 'semantic_errors.txt'

code = open(INPUT_FILE_NAME, 'r').read()
parser = Parser(code)
parser.parse()

parser.code_gen.write_program_block_to_file()
