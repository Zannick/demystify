# deps -- ANTLR v3 parser rule dependency graph generation
# Copyright (C) 2012 Benjamin S Wolf
# 
# deps.py is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License,
# or (at your option) any later version.
# 
# deps.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with deps.py.  If not, see <http://www.gnu.org/licenses/>.

"""deps -- ANTLR v3 parser rule dependency graph generation."""

import os
import re
import sys

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

def print_deps(deps, indent_level=1):
    indent = '  ' * indent_level
    for rname, rdeps in deps.items():
        for d in rdeps:
            print('{}"{}" -> "{}";'.format(indent, rname, d))

def print_graph(basedir, colors):
    print('digraph gdeps {\n  truecolor=true;')
    # filename -> list of deps
    fdeps = {}
    # rule name -> filename
    dep_file = {}
    # filename -> filename it depends on
    file_deps = {}
    for f in colors:
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
    print('  subgraph "filedeps" {')
    for fname, fdeps in file_deps.items():
        print('    "{}" [shape=box,style=filled,color={}];'
              .format(fname, colors[fname]))
    print_deps(file_deps, indent_level=2)
    print('  }\n}')

def read_config(filename):
    """ Gets basedir and color mapping information from the given config. """
    basedir = None
    colors = {}
    with open(filename, 'r') as f:
        for lineno, line in enumerate(f):
            line = line.strip()
            if not line or line[0] == '#':
                continue
            if ':' not in line:
                sys.stderr.write('Error reading {} at line {}: Expected ":".\n'
                                 .format(filename, lineno + 1))
                sys.exit(1)
            arg0, arg1 = line.split(':', 1)
            arg0 = arg0.strip()
            arg1 = arg1.strip()
            if basedir is None:
                if arg0 == 'rel_path':
                    basedir = os.path.join(os.path.dirname(filename), arg1)
                elif arg0 == 'abs_path':
                    basedir = os.path.abs_path(os.path.join('/', arg1))
                else:
                    sys.stderr.write('Error reading {} at line {}: Unknown '
                                     'path spec {!r}.\n'
                                     .format(filename, lineno + 1, arg0))
                    sys.exit(1)
                if not os.path.exists(basedir):
                    sys.stderr.write('Error: Specified location {!r} does not '
                                     'exist.'.format(basedir))
                    sys.exit(1)
            else:
                colors[arg0] = arg1
    return basedir, colors

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write('Usage:\n  {} configfile\n'.format(sys.argv[0]))
        sys.exit(1)
    basedir, colors = read_config(sys.argv[1])
    print_graph(basedir, colors)
