from write_session import ConfState


try:
    awsops = ConfState("xx",must_exist=True)
except:
    print("TEST PASSED: xx failed")

default = ConfState("default",must_exist=True)
default.new_credentials({})
# NO SAVE

defaultxx = ConfState("defaultxx",must_exist=False)
defaultxx.new_credentials(
    { "token":"sdfksdj",
    "ID":"dsddf" },
    backup=ConfState.BACKUP_UNLESS_TOKEN)

defaultxx.save()
print("Ops I just wrote to your ~/.aws/credentials file :-D")
