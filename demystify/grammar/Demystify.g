grammar Demystify;

// This file is part of Demystify.
// 
// Demystify: a Magic: The Gathering parser
// Copyright (C) 2012 Benjamin S Wolf
// 
// Demystify is free software; you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation; either version 3 of the License,
// or (at your option) any later version.
// 
// Demystify is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with Demystify.  If not, see <http://www.gnu.org/licenses/>.

/* Top-level grammar for Demystify. */

options {
    language = Python;
    output = AST;
}

// Order is absurdly relevant. eg. subsets invokes rules in zones,
// hence zones must be imported after so that antlr can correctly
// generate lookahead code for it. This is mostly necessary for rules with
// optional or repeated parts, where LL(1) can't correctly predict which rule
// to use to parse the next tokens. See the graph output from deps.py.
// Note further that rules in *this* file are handled as if imported last.
import Words, events, keywords, costs, subsets, math, properties, counters, zones, types, players, pt, raw_keywords, misc, macro;

tokens {
    ADD_COUNTERS;
    ATTACHED_TO;
    CMC;
    CONDITION;
    COUNTER_GROUP;
    COUNTER_SET;
    EVENT;
    GEQ;
    GT;
    HAS_COUNTERS;
    INT;
    KEYWORDS;
    LEQ;
    LT;
    MAX;
    MULT;
    PAY_LIFE;
    PAY_PER;
    PER;
    PLAYER_GROUP;
    PROPERTIES;
    PT;
    REMOVE_COUNTERS;
    SUBSET;
    SUBTYPES;
    SUPERTYPES;
    TYPECYCLING;
    TYPELINE;
    TYPES;
    VAR;
    ZONE_SET;
}

@lexer::header {
    import logging
    logging.basicConfig(level=logging.DEBUG, filename="LOG")
    llog = logging.getLogger("Lexer")
    llog.setLevel(logging.DEBUG)

    # hack to allow unicode
    if sys.getdefaultencoding() != 'utf-8':
        reload(sys)
        sys.setdefaultencoding('utf-8')
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
    # header guard to prevent rewrapping some functions below
    if not hasattr(Parser, 'PARSER_ERRORS_REDEF'):
        Parser.PARSER_ERRORS_REDEF = True
        def log_error(parser, msg):
            plog.error(msg)

        def _getCardState(self):
            return getattr(self._state, 'card', None)

        def _emitDebugMessage(self, msg):
            plog.debug("{}:{}".format(self.getCardState(), msg))

        def _getErrorHeader(self, e):
            if hasattr(self._state, 'card'):
                return "{}:{}:{}".format(self._state.card,
                                         e.line, e.charPositionInLine)
            else:
                return "line {}:{}".format(e.line, e.charPositionInLine)

        def __getErrorMessage(supermethod):
            def _getErrorMessage(self, e, tokenNames):
                stack = self.getRuleInvocationStack()
                msg = ""
                if isinstance(e, NoViableAltException):
                    msg = ("no viable alt; token={0.token} "
                           "(decision={0.decisionNumber}"
                           " state={0.stateNumber})"
                           .format(e))
                else:
                    msg = supermethod(self, e, tokenNames)
                return "{} {}".format(stack, msg)
            return _getErrorMessage

        def _getTokenErrorDisplay(self, t):
            return str(t)

        def _getRuleInvocationStack(cls, ffilter):
            rules = []
            mrules = []
            for frame in reversed(inspect.stack()):
                code = frame[0].f_code
                codeMod = inspect.getmodule(code)
                if codeMod is None:
                    continue
                mrules.append((codeMod.__name__, code.co_name))
                if not ffilter(codeMod.__name__, code.co_name):
                    continue
                if code.co_name in ('nextToken', '<module>'):
                    continue
                if len(mrules) > 1:
                    pm, pr = mrules[-2]
                    if code.co_name == pr and pm != codeMod:
                        continue
                rules.append(code.co_name)
            return rules

        def _ffilter(modulename, funcname):
            return (modulename.startswith("grammar")
                    and funcname[0] != '_')

        def __getRuleInvocationStack(ffilter):
            def _getRuleInvocationStack1(self):
                return self._getRuleInvocationStack(ffilter)
            return _getRuleInvocationStack1

        Parser.emitErrorMessage = log_error
        Parser.getCardState = _getCardState
        Parser.emitDebugMessage = _emitDebugMessage
        Parser.getErrorHeader = _getErrorHeader
        Parser.getErrorMessage = __getErrorMessage(Parser.getErrorMessage)
        Parser.getTokenErrorDisplay = _getTokenErrorDisplay
        Parser._getRuleInvocationStack = classmethod(_getRuleInvocationStack)
        Parser.getRuleInvocationStack = __getRuleInvocationStack(_ffilter)

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

// Literals used in parsing rules don't have to be declared,
// but for reference they are:
// ,:;."'+-*/

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
