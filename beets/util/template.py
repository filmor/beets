# This file is part of beets.
# Copyright 2011, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

class Template(object):
    """Implements a lazy substitute for string.Template, that allows to skip
       substitutions if part of the string is empty."""
    def __init__(self, string):
        self._string = string

    def _get_val(self, mapping, key):
        value = mapping.get(key, "")
        if hasattr(value, "__call__"):
            value = value()
        return value

    def _do_subs(self, mapping, start, end):
        result = ""
        string = self._string
        i = start
        while i < end:
            # Handle escaping
            if string[i] == '$' and string[i+1] == '$':
                result += string[i+1]
                i += 1

            elif string[i] == '$':
                i += 1
                j = i
                if string[i] == '{':
                    while j < end and string[j] != '}':
                        j += 1

                    value = self._get_val(mapping, string[i+1:j])
                    if value == "":
                        return ""
                    else:
                        result += value
                    i = j
                else:
                    while j < end and string[j].isalpha():
                        j += 1

                    value = self._get_val(mapping, string[i:j])
                    if value == "":
                        return ""
                    else:
                        result += value

                    i = j - 1

            elif string[i] == '{':
                i += 1
                j = i
                level = 1
                while j < end:
                    if string[j] == '$' and string[j+1] in '${}':
                        j += 1
                    elif string[j] == '{':
                        level += 1
                    elif string[j] == '}':
                        level -= 1
                        if level == 0:
                            result += self._do_subs(mapping, i, j)
                            i = j
                            break
                    j += 1

                if level != 0:
                    raise SyntaxError
            else:
                result += string[i]
            i += 1

        return result

    def substitute(self, mapping):
        return self._do_subs(mapping, 0, len(self._string))

