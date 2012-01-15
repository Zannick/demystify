parser grammar pt;

/* Power/toughness related rules. */

// This rule is used for printed p/t, p/t setting abilities,
// and p/t modifying abilities.

pt : p=( pt_signed_part | pt_part ) DIV_SYM t=( pt_signed_part | pt_part )
     -> ^( PT $p $t );

pt_signed_part : PLUS_SYM pt_part -> ^( PLUS pt_part )
               | MINUS_SYM pt_part -> ^( MINUS pt_part );

pt_part : NUMBER_SYM
        | VAR_SYM -> ^( VAR VAR_SYM )
        | STAR_SYM
        | a=NUMBER_SYM b=( PLUS_SYM | MINUS_SYM ) c=STAR_SYM
          { plog.debug('Ignoring p/t value "{} {} {}" in {}; '
                       'deferring actual p/t calculation to rules text.'
                       .format($a.text, $b.text, $c.text,
                               self.getCardState())) }
          -> STAR_SYM;
