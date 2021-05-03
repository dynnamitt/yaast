from . import write_session

# yaast.main
def main():
    write_session.main(app_meta = {
        "name" : "yaast",
        "ver": "0.0.4",
        "homepage" : "sample.com/yaast"
    })