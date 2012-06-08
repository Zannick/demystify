# deps -- ANTLR v3 parser rule dependency graph generation
# Copyright (C) 2012 Benjamin S Wolf
# 
# Demystify is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License,
# or (at your option) any later version.
# 
# Demystify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Demystify.  If not, see <http://www.gnu.org/licenses/>.

"""deps -- ANTLR v3 parser rule dependency graph generation."""

import os
import re
import sys

basedir = os.path.join(os.path.dirname(__file__), '..', 'demystify', 'grammar')

rule = re.compile(r"^(?:[a-z_0-9]+\+?=)?([a-z_0-9]+)\+?\*?!?\??$")
comments = re.compile(r"//.*?$|/\*.*?\*/", re.M|re.S)
actions = re.compile(r"""{([^'"]|'[^']*'|"[^"]*"|'''.*?'''"""
                     r'''|""".*?""")*?}''', re.M)
full_rule = re.compile(r"^([a-z_0-9]+)\s*:(.*);\s*$", re.M)

def find_rules(fulltext):
    """ fulltext is the full text of the file. """
    ct = comments.sub(' ', fulltext)
    nt = ct.replace('\n ', ' ')
    deps = {}
    for m in full_rule.finditer(nt):
        rname, rtext = m.groups()
        rt = actions.sub('', rtext)
        deps[rname] = set()
        for token in rt.split():
            m = rule.match(token)
            if m:
                deps[rname].add(m.group(1))
    return deps

def print_deps(deps):
    for rname, rdeps in deps.items():
        for d in rdeps:
            print('  "{}" -> "{}";'.format(rname, d))

def print_graph(files):
    print('digraph gdeps {\n  truecolor=true;')
    # filename -> list of deps
    fdeps = {}
    # rule name -> filename
    dep_file = {}
    # filename -> filename it depends on
    file_deps = {}
    for f in files:
        with open(os.path.join(basedir, f)) as g:
            s = g.read()
        f = os.path.basename(f)
        deps = find_rules(s)
        fdeps[f] = deps
        for rname in deps:
            dep_file[rname] = f
        file_deps[f] = set()
    for f, deps in fdeps.items():
        color = colors[f]
        g = os.path.splitext(f)[0]
        print('  subgraph "{g}" {{\n    node [style=filled,color={c}];\n'
              .format(g=g, c=color))
        for rname, rdeps in deps.items():
            print('    {};'.format(rname))
            for rdep in rdeps:
                if dep_file[rname] != dep_file[rdep]:
                    file_deps[dep_file[rname]].add(dep_file[rdep])
        print('  }')
    for deps in fdeps.values():
        print_deps(deps)
    print('  subgraph "files" {')
    for fname, fdeps in file_deps.items():
        print('    "{}" [shape=box,style=filled,color={}];'
              .format(fname, colors[fname]))
    print_deps(file_deps)
    print('  }\n}')

colors = {
    'Demystify.g': 'gray',
    'costs.g': 'gold',
    'counters.g': 'plum',
    'keywords.g': 'salmon',
    'macro.g': 'cyan',
    'math.g': 'violetred',
    'misc.g': 'red',
    'players.g': 'blue',
    'properties.g': 'greenyellow',
    'pt.g': 'seagreen',
    'raw_keywords.g': 'chocolate',
    'subsets.g': 'skyblue',
    'types.g': 'lightgray',
    'zones.g': 'green',
}

if __name__ == "__main__":
    print_graph(colors.keys())
