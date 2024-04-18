from sys import exit
#

APP_META = {
    "name": "yaast",
    "ver": "0.1.x",
    "homepage": "github.com/dynnamitt/yaast"
}

def esc(e_code):
    return f'\033[{e_code}m'


def die(errtxt):

    print(type(errtxt))
    if type(errtxt) == "string":
        print(esc(31)+"ERROR:", esc(0) + errtxt)
    else:
        print(esc(31)+"ERROR:", esc(0) + str(errtxt))

    exit(1)
