lexer grammar Demystify;

options {
    language = Python;
}

import Keywords, Symbols;

@header {
    import logging
    logging.basicConfig(level=logging.DEBUG, filename="LOG")
    llog = logging.getLogger("Lexer")
    llog.setLevel(logging.DEBUG)

    # hack to allow unicode
    if sys.getdefaultencoding() != 'utf-8':
        reload(sys)
        sys.setdefaultencoding('utf-8')
}

@footer {
    _token_names = {}
    for name, i in globals().items():
        if (name not in ('HIDDEN', 'HIDDEN_CHANNEL',
                         'INVALID_TOKEN_TYPE', 'MIN_TOKEN_TYPE')
            and isinstance(i, int)):
            if i in _token_names:
                sys.stderr.write('Token collision at {}: {} and {}.'
                                 .format(i, _token_names[i], name))
            else:
                _token_names[i] = name

    def getTokenName(i):
        """ Use a reverse lookup to get the name of the token rule
            for the given raw token (an integer).
            Returns None if nothing matches. """
        return _token_names.get(i)
}

@members {
    def emitErrorMessage(self, msg):
        if hasattr(self, 'card'):
            msg = self.card + ':' + msg
        llog.error(msg)
}

COMMA : ',';
COLON : ':';
SEMICOLON : ';';
PERIOD : '.';
DQUOTE : '"';
SQUOTE : '\'';
PLUS_SYM : '+';
MINUS_SYM : '-';
STAR_SYM : '*';
DIV_SYM : '/';
