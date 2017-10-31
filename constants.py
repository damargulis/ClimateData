
IMAGE_BLACKLIST = [
        u'https://www.regulations.gov/images/logo.png',
        u'https://www.regulations.gov/images/icon-search.png',
        u'https://www.regulations.gov/images/icon_pop-out.png',
        u'https://www.regulations.gov/images/clip_paper_icon.png',
        u'https://www.regulations.gov/images/clip_paper_icon.png',
        u'https://www.regulations.gov/images/clip_paper_icon.png',
        u'https://www.regulations.gov/images/external-link_brown.png',
        u'https://www.regulations.gov/images/fileicons/small/icon_pdf.gif',
        u'https://www.regulations.gov/images/fileicons/large/icon_pdf.gif',
        u'https://www.regulations.gov/images/fileicons/small/icon_xls.gif',
        u'https://www.regulations.gov/images/fileicons/large/icon_xls.gif',
        u'https://www.regulations.gov/images/fileicons/small/icon_doc.gif',
        u'https://www.regulations.gov/images/fileicons/large/icon_doc.gif',
        u'https://www.regulations.gov/images/fileicons/small/icon_crtext.gif',
        u'https://www.regulations.gov/images/fileicons/large/icon_crtext.gif',
        u'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAhCAYAAAC4JqlRAAAE7klEQVR42sWX209cVRTG9zswzOXMYExqSIxNTIwPjYkxfTAxqaX/gc/axqTAcJky3IVSKLcC1tpiQowvJNYaq0ZNa7ViaCpe0lotXhqgQrkNcztz5nKGGWA+1zrc5nAObTUBdvJlmP3tvX5rr7P3PoMQ1MZKc1/+x5N7fdKbF5uszsOOihjMYiazxXhFTtFMQz6CbXYo3RKiPTsrZjCLmcwW8637JpRuBxbPuZC+UICl/p0VM5jFTGaLUHtBJrkG300xM3RayohIhwPpc9T57i6LmMwWynoCeyClU+IEJKTeKTAo+bYLmWQYy747SN/9EOmRbqQuHkbqbIHp+P8jZgulXVoNukWxLglmbUWZRvrHXix+8KLpvP8iZotIG52APpdB3P/QtpxC+tYAkuf3m85/HDFDRFopgV6XQQqZync9iN76GMmp29vmkVlUkLpWhWSPyzTOw8RsIZ9yIHnGZVCMyuNvtGHGa8GUJw9TDYXwf1QGdfymaSLpPy4j0bvPNNZ2YraQT1ICXS6D1E4X4qediLZKiLQ4EGqyw1dnxQOPBbNnD2Nx+jdDEktTI1D7njaNZyZmi3CzQ4M9SokOqkqbU5u0UG+jqljgv1SJzFJKX4mJIcQ7nnismMwWYVqZ2u40KN62egqW53/H0t9XkPz8OK1uPxJUlRhVRaZ5c958rRrL8bAuicWfBrRxZnGzxWwRbqQEaGVbFWkynoJMOonUcA8SXYVItDqh0AoWaqyYaXkey9GAbqz6aYk2xiz2upgtQvV2JE45DeL+7dpKdAGJgVcRb6E90kyblZKY6zukexwriTCiHc+Yxs5miGCdXQu0VWwGL7oR/KoTycnbptWID76G2EmqRJMEn9cK/+BxfRVu9pMvmcZnMVsEaymBZqdBSqOEhSobpsstmCzJw4PWlxAfvWZIInbhFcSa6JE1ODBXmY/En9c3fbqslDMHTOOzmC0C1TbE3pIMilICHFSmLIM1Nvg8Vi2RwOVG/YUoT0NpeUobz+PmOw7q/MSNfigUx4zBbBGgVcYapEdKqXMg6KWLyW1B8LNmPeTrdkTrV8f4Kq1Q//petxfkOqdpTGaLwAmbNtlUXQeQHh9evWQmf6ZyvkBJ2DFdaoF6bzjrOo5DbnhSm8N+YLBYl2Dk/BHT+MwWAQ8lUCsZFKl2IHVvSH/J3B+BTP08Z65NX2pl8BiUGrofvPRTq6YQmZS64cWudmrxtjI4jghUUALVkkEhj11bmW7T0TELVdGGqyKIOx/q2A+bO/6XS5CpX/HS5i23IpnlJe9eRfiEw8BgtvDTYMXrMIhNNWtHa4EoqL/CuuHLX7ZveCl6N4QqbRueMvTe5jvCP4HgmpctZgu/mwJSdlsVLLdhtvZZxO5c0YLER7/FTP1zWj/7oQo6He+/vrnZVAWBsnWPkvukIeu4qhtetpgtFkqtiHgcBoUr6e1H3uSbeRg/mqN98nfu13xKYK44H/eP5WLsjRxMkc8Q9ji5WfImjhq9bDFbLJRQAhUOU4XLaUe7bfCX2LRP/r7uyeUEKrPDX2oDxwiUbvrsBd12bd5WL1vsCV+xVZuwF2K28JXYIZftjZgtAm0HMzKVay/EbKH++sV4kJ5VuNS+q2ImswWdkkOLo98g0nsEYTf9SKCy7KiIwSxmMlv7F53+KCLd4Jcbdr4tr7GKmP0vi5tvNuFm4WMAAAAASUVORK5CYII=',
        u'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAhCAYAAAC4JqlRAAAEP0lEQVR42sWY+VMTZxjH33+uM/5SpYBEUbTaMgqttFBrKYPaQdtivRjsMdNW247tdMbyA1CZSoDKkDuBXOSAkHBqjoVNNtkcAtFv3yeByLFILALPzGezefO+38+z2d3JwRivM/3xA3WDcVP9UBwNuww5yEVOcrNavtOkT+C6LYn20RS+c+8u5CAXOcnNWszJqXZXEr9MpHB/Mo3fdxlykIuc5GatNvnF3Yk0fgvsLeQkN7vpTOKen3e1x5CT3OwG3/zMu9kPyM2uO2X8yM/JfkBu1uqQ8YMv9Ua4H0ihczaN78eTRc0nN/vSLuNbvmAn3PEm4BIzWK34Yhbtnvi268jNWvimbSy5idteGQ+mU/zWye8rzcnN8ySgDSWxtrxCAn9OxF65jiA3u2yTcdOb3MR1lwRNMB8sPcti4GkKd8bWz73hkXFvLIatqmdGzs1RyifIzS5aE/iGT9rI184obllmkV7KFgIz2efQhFJo8+bXtI7GMCVl8Kr6KxDHNbeyg9zs85EEvnLLm7jqlNCsm4EzGN0Umll+jt4n/O13CNiuopllXLGLig5ys8+GE7jikhVpNoUgpha3Dk8voZi661lAizPObz1+3kdf+sjNzlviuMwHlWiyRHBN68NCMoM3UbpwChft0UI+uVm9OY5mZ0KRJquI+sEAdNPCjuVzUgpOQUajRSjkk5vVmSU0OuLK2CU0GILon9xZA0OBILo8c7ik8eO8OVLIJzf7wCThU3t8SxrMAv/cHselPgemxcT/auDcQytq+sbwke4JPhkRC9nkZmdNMdTzI92Kj61RnDOGUM0DUkvLry1/5Avi7GM/P9oIzxLXZZObVRtjqLNJeawxtPsSucfC2Mp4je4pGvpGkVwsvgmBX7y1ajdqjeH1eSuQm502xFBrlXLUDIv41R+HTkjjqpuPjeRfa7DF+LeYGObTi0XLqdHGARfeG5zO5a461kJudlIfxRkuIqrN8zg1NIuf3OEdXXQROY0LaidO9PlQbRIK+RshN6vSRfH+cCyPJYpT+jCO903gC37/R5LPXlve7ZnFya4RHFP7+BFGcpmF/A2Qmx3VRvGuJfYScxRV2hBUveN4p8OMNp0XgW2u/jA/4k73LKq7h1He7UDlwBROGIRc1rrsDZCbqbQiqki6FpOIY/oIjjyeQVmPG4c6LFB1GNCotqOx14Y/7JO4pfPk9k93mnHwgRGlXQ5UqCdQqQniuHF+c6YC5GblGhGVpqgyRhFHtGFUDM6hvH8SpY/4u9LjRcnfLpQ8dKP0n3GUqf04/O8MVJoQjhrmt85SgNysdIhLjEVgWIBKL6CCGuIyQqWL8LH54tYrQG5WwjeHjftDyWoDZYb9IdfAhxbpRYmeP9kHyM30wqL/be0CDur3FnKSm/Hb+K1hcQkXHBIO0Qu63YUc5CInuXM/0fnOAY6Gk8XuV3bFlft/4D+oXdznons4MgAAAABJRU5ErkJggg==',
]

BASIC_INFO_CLASS = "GIY1LSJNTC"
ADDITIONAL_INFO_CLASS = "GIY1LSJG3D"

METADATA_BLACKLIST = [
        u" \xd7 ",
        "close",
        "Press Escape to close",
        "OK",
]

