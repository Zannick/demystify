grammar Demystify;

options {
    language = Python;
    output = AST;
}

import Keywords, costs, types;

tokens {
    TYPELINE;
    VAR;
}

@lexer::header {
    import logging
    logging.basicConfig(level=logging.DEBUG, filename="LOG")
    llog = logging.getLogger("Lexer")
    llog.setLevel(logging.DEBUG)
}

@parser::header {
    import logging
    logging.basicConfig(level=logging.DEBUG, filename="LOG")
    plog = logging.getLogger("Parser")
    plog.setLevel(logging.DEBUG)

    # hack to allow unicode
    if sys.getdefaultencoding() != 'utf-8':
        reload(sys)
        sys.setdefaultencoding('utf-8')

    # hack to make all subparsers have the same error logging
    def log_error(parser, msg):
        plog.error(msg)

    def _getErrorHeader(self, e):
        if hasattr(self._state, 'card'):
            return "{}:{}:{}".format(self._state.card,
                                     e.line, e.charPositionInLine)
        else:
            return "line {}:{}".format(e.line, e.charPositionInLine)

    Parser.emitErrorMessage = log_error
    Parser.getErrorHeader = _getErrorHeader

    # hack to make __repr__ somewhat meaningful
    def _tree_repr(self):
        return ('<{0.__module__}.{0.__name__} instance {1}>'
                .format(self.__class__, self.toStringTree()))

    CommonTree.__repr__ = _tree_repr
}

@lexer::footer {
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

@lexer::members {
    def emitErrorMessage(self, msg):
        if hasattr(self, 'card'):
            msg = self.card + ':' + msg
        llog.error(msg)
}

@parser::members {
    def setCardState(self, name):
        self._state.card = name
}

card_mana_cost : mc_symbols -> ^( COST mc_symbols );

COMMA : ',';
COLON : ':';
SEMICOLON : ';';
PERIOD : '.';
DQUOTE : '"';
SQUOTE : '\'' | '\u2018';
PLUS_SYM : '+';
MINUS_SYM : '-';
STAR_SYM : '*';
DIV_SYM : '/';
