# -*- coding: utf-8 -*-
import execjs

_MAP_LEN = 64
_charMap = [
        ["A", "d"], ["B", "e"], ["C", "f"], ["D", "g"], ["E", "h"], ["F", "i"], ["G", "j"],
        ["H", "k"], ["I", "l"], ["J", "m"], ["K", "n"], ["L", "o"], ["M", "p"], ["N", "q"], ["O", "r"],
        ["P", "s"], ["Q", "t"], ["R", "u"], ["S", "v"], ["T", "w"], ["U", "x"], ["V", "y"], ["W", "z"],
        ["X", "a"], ["Y", "b"], ["Z", "c"], ["a", "Q"], ["b", "R"], ["c", "S"], ["d", "T"], ["e", "U"],
        ["f", "V"], ["g", "W"], ["h", "X"], ["i", "Y"], ["j", "Z"], ["k", "A"], ["l", "B"], ["m", "C"],
        ["n", "D"], ["o", "E"], ["p", "F"], ["q", "0"], ["r", "1"], ["s", "2"], ["t", "3"], ["u", "4"],
        ["v", "5"], ["w", "6"], ["x", "7"], ["y", "8"], ["z", "9"], ["0", "G"], ["1", "H"], ["2", "I"],
        ["3", "J"], ["4", "K"], ["5", "L"], ["6", "M"], ["7", "N"], ["8", "O"], ["9", "P"],
        ["\n", ":|~"], ["\r", ""]
    ]


def _nst_encrypt(nst_token):
    ret = ""
    for r in range(len(nst_token)):
        n = nst_token[r]
        for s in range(_MAP_LEN):
            if n == _charMap[s][0]:
                n = _charMap[s][1]
                break
        ret += n
    return ret


def _nst_decrypt(nst_token):
    ret = ""
    nst_token_len = len(nst_token)
    r = 0
    while nst_token_len > r:
        n = nst_token[r]
        for s in range(_MAP_LEN):
            if ":" == n and ":|~" == nst_token[r, r + 3]:
                n = "\n"
                r += 2
                break
            if (n == _charMap[s][1]):
                n = _charMap[s][0]
                break
        ret += n
        r += 1
    return ret


def get_token(code=""):
    js_code = '''function getToken(){location = "http://user.qzone.qq.com/%s"; Z = [], z = [];
    gh = (function() {
                        var e = 0
                          , t = 0
                          , n = 0;
                        return function(o) {
                            e > 0 && e % 2 == 0 && (2 > t ? Z[t++] = o : 3 > n && (z[n++] = o)),
                            e++
                        }
                    }
                    )();
    !function() ''' + code + ''',

                    J = (_ = 0,
                    function() {
                        return H[L[_++]]
                    }
                    );
                    !function() {
                            for (var _ = 0; _ < L.length; _++)
                                gh(J())
                    }()
                }(); return Z.join("") + String.fromCharCode(46) + z.join("")}'''
    js_exe = execjs.compile(js_code)
    token = js_exe.call("getToken")
    return _nst_decrypt(token)

if __name__ == '__main__':
    print(_nst_decrypt("vVMc4a"))