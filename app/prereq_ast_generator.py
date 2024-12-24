# Token Types
import json
from typing import List

VALUE = 'VALUE'
AND = 'AND'
OR = 'OR'
MIN_GRADE = 'MIN_GRADE'
LPAREN = 'LPAREN'
RPAREN = 'RPAREN'
EOF = 'EOF'

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()

class Scanner(object):
    def __init__(self, text):
        self.text : str = text
        self.pos = 0

        # If there is empty text, then the curr_char will be None,
        # otherwise, it will be whatever the first character is
        self.curr_char = None
        self.advance(0)

    def error(self):
        raise Exception('Invalid character')

    def advance(self, amount=1):
        self.pos += amount
        self.curr_char = self.text[self.pos] if self.pos < len(self.text) else None

    def whitespace(self):
        while self.curr_char is not None and self.curr_char.isspace():
            self.advance()

    def keyword(self) -> Token:
        def check_keyword(keyword):
            return self.text[self.pos:self.pos+len(keyword)] == keyword

        if check_keyword('and '):
            self.advance(4)
            return Token(AND, 'and')

        if check_keyword('or '):
            self.advance(3)
            return Token(OR, 'or')

        if check_keyword('Minimum Grade: '):
            self.advance(15)
            return Token(MIN_GRADE, 'Minimum Grade')

    def value(self) -> Token:
        value = ''
        while self.curr_char is not None and (self.curr_char.isalnum() or self.curr_char == '-'):
            value += self.curr_char
            self.advance()

        return Token(VALUE, value)

    def get_next_token(self) -> Token:
        while self.curr_char is not None:
            if self.curr_char.isspace():
                self.whitespace()
                continue

            if self.curr_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.curr_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            if token := self.keyword():
                return token

            if self.curr_char.isalnum():
                return self.value()

            self.error()

        return Token(EOF, None)

class AST(object):
    pass

class Operator(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        self.type = 'OPERATOR'

class Course(AST):
    def __init__(self, subject_code_token, course_number_token, min_grade_token):
        self.subject_code = subject_code_token.value
        self.course_number = course_number_token.value
        self.min_grade = min_grade_token.value
        self.type = 'COURSE'

class Parse(object):
    def __init__(self, scanner):
        self.scanner = scanner
        self.curr_token = self.scanner.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def consume(self, token_type):
        if self.curr_token.type == token_type:
            self.curr_token = self.scanner.get_next_token()
        else:
            self.error()

    def factor(self):
        """
        Rules:
            0: factor -> VALUE VALUE MIN_GRADE VALUE
            1: factor -> LPAREN expression RPAREN

        :return:
        """
        token = self.curr_token

        if token.type == VALUE:
            self.consume(VALUE)
            course_number_token = self.curr_token
            self.consume(VALUE)
            self.consume(MIN_GRADE)
            min_grade_token = self.curr_token
            self.consume(VALUE)
            return Course(token, course_number_token, min_grade_token)

        self.consume(LPAREN)
        node = self.expression()
        self.consume(RPAREN)
        return node

    def term(self):
        """
        Rules:
            0: term -> factor AND term
            1: term -> factor

        :return:
        """
        node = self.factor()

        if self.curr_token.type == AND:
            op = self.curr_token
            self.consume(AND)
            right = self.term()
            return Operator(node, op, right)

        return node

    def expression(self):
        """
        Rules:
            0: expression -> term OR expression
            1: expression -> term

        :return:
        """
        node = self.term()

        if self.curr_token.type == OR:
            op = self.curr_token
            self.consume(OR)
            right = self.expression()
            return Operator(node, op, right)

        return node

    def parse(self):
        if self.curr_token.type == EOF:
            return None

        return self.expression()

def get_prereq_ast(text):
    scanner = Scanner(text)
    parser = Parse(scanner)
    return parser.parse()

def get_all_courses(text) -> List[Course]:
    get_all_courses_w_ast(get_prereq_ast(text))

def get_all_courses_w_ast(ast):
    courses = []

    if ast is None:
        return courses

    def traverse(ast):
        courses = []

        if isinstance(ast, Operator):
            courses.extend(traverse(ast.left))
            courses.extend(traverse(ast.right))
        elif isinstance(ast, Course):
            courses.append(ast)

        return courses

    return traverse(ast)

if __name__ == '__main__':
    text = 'ECE 200 Minimum Grade: D and (MATH 300 Minimum Grade: A or CS 265 Minimum Grade: C)'

    ast = get_prereq_ast(text)
    print(json.dumps(ast, default=lambda o: o.__dict__, indent=4))

    courses = get_all_courses_w_ast(ast)
    print([f'{course.subject_code}-{course.course_number}' for course in courses])
