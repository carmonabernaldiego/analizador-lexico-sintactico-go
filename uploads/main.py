import ply.lex as lex
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Lista de tokens
tokens = (
    'ID', 'NUMBER', 'STRING',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON', 'PERIOD',
    'PACKAGE', 'IMPORT', 'FUNC', 'FMT', 'PRINTLN'
)

# Palabras reservadas
reserved = {
    'package': 'PACKAGE',
    'import': 'IMPORT',
    'func': 'FUNC',
    'fmt': 'FMT',
    'Println': 'PRINTLN'
}

# Reglas de expresiones regulares para tokens simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMICOLON = r';'
t_PERIOD = r'\.'

# Regla para las palabras reservadas y los identificadores


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t

# Regla para las cadenas de texto


def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    return t

# Regla para los números (aunque no se usan en este código)


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


# Regla para los espacios en blanco y los comentarios
t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Regla para manejar errores


def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)


# Construir el lexer
lexer = lex.lex()


def analyze_code(code):
    lexer.input(code)
    tokens = []
    counts = {
        'PACKAGE': 0,
        'IMPORT': 0,
        'FUNC': 0,
        'FMT': 0,
        'PRINTLN': 0,
        'ID': 0,
        'NUMBER': 0,
        'STRING': 0,
        'PLUS': 0,
        'MINUS': 0,
        'TIMES': 0,
        'DIVIDE': 0,
        'LPAREN': 0,
        'RPAREN': 0,
        'LBRACE': 0,
        'RBRACE': 0,
        'SEMICOLON': 0,
        'PERIOD': 0,
        'LEXICAL_ERROR': 0
    }

    while True:
        tok = lexer.token()
        if not tok:
            break
        token_type = tok.type
        tokens.append({
            'token': tok.value,
            'line': tok.lineno,
            'type': token_type
        })
        if token_type in counts:
            counts[token_type] += 1
        else:
            counts['LEXICAL_ERROR'] += 1

    return tokens, counts


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return render_template('index.html', tokens=[], counts={}, code='', file_error="No se ha seleccionado ningún archivo")
            file_path = os.path.join(
                app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            with open(file_path, 'r') as f:
                code = f.read()
            tokens, counts = analyze_code(code)
            return render_template('index.html', tokens=tokens, counts=counts, code=code)
        else:
            code = request.form['code']
            tokens, counts = analyze_code(code)
            return render_template('index.html', tokens=tokens, counts=counts, code=code)
    return render_template('index.html', tokens=[], counts={}, code='')


@app.route("/analyze", methods=['POST'])
def analyze():
    code = request.json['code']
    tokens, counts = analyze_code(code)
    return jsonify({'tokens': tokens, 'counts': counts})


if __name__ == '__main__':
    app.run(debug=True)
