#!/usr/bin/env sh
#
# NAME
#        split-lines.sh - Split long vCard lines
#
# SYNOPSIS
#        split-lines.sh FILE...
#
# DESCRIPTION
#        Simply inserts the sequence CR, LF, space to make every line 75
#        characters (excluding CR and LF).
#
# BUGS
#        https://github.com/l0b0/vcard/issues
#
# COPYRIGHT
#        Copyright (C) 2012 Victor Engmark
#
#        This program is free software: you can redistribute it and/or modify
#        it under the terms of the GNU General Public License as published by
#        the Free Software Foundation, either version 3 of the License, or
#        (at your option) any later version.
#
#        This program is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#        GNU General Public License for more details.
#
#        You should have received a copy of the GNU General Public License
#        along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

sed -e '{ s/\(.\{75\}\)\([^\r]\)/\1\r\n \2/; P; D }' "$@"
