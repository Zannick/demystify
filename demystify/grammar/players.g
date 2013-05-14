parser grammar players;

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

/* Players, controllers, and owners. */

player_subset : player_group ( conj^ player_group )? ;

// TODO: objects can have controllers and/or owners
// TODO: Handle 'that player' etc refs differently?
player_group : ( number OF )? player_poss ( OPPONENT | TEAMMATE )
               -> ^( PLAYER_GROUP number? player_poss OPPONENT[]? TEAMMATE[]? )
             | number player_base -> ^( PLAYER_GROUP number player_base )
             | THAT player_base -> ^( PLAYER_GROUP THAT[] player_base )
             | ( CHOSEN | ENCHANTED )? player_base
               -> ^( PLAYER_GROUP CHOSEN[]? ENCHANTED[]? player_base )
             | ( ACTIVE | DEFENDING ) PLAYER
               -> ^( PLAYER_GROUP ACTIVE[]? DEFENDING[]? PLAYER[] )
             | ANOTHER PLAYER -> ^( PLAYER_GROUP NOT YOU )
             | YOU
             | ref_player
             ;

ref_player : ref_object POSS ( OWNER -> ^( OWNER[] ref_object )
                             | CONTROLLER -> ^( CONTROLLER[] ref_object )
                             )
           ;

player_poss : YOUR -> ^( POSS YOU )
            | ( number | THAT )? player_base poss
              -> ^( POSS ^( PLAYER_GROUP number? THAT[]? player_base ) )
            | ref_player_poss
            ;

ref_player_poss : HIS OR HER -> THEIR
                | THEIR -> THEIR[]
                ;

player_base : OPPONENT | TEAMMATE | PLAYER ;
