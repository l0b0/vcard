#!/usr/bin/env bash
#
# NAME
#        join-lines.sh - Join previously split vCard lines
#
# SYNOPSIS
#        join-lines.sh FILE...
#
# DESCRIPTION
#        Simply removes any occurrences of the sequence CR, LF, space.
#
#        Can be used as a preprocessing script for vCards handling.
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

sed -n '1h;1!H;${;g;s/\r\n //g;p;}' "$@"
