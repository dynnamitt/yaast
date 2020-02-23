from awsconfigparser import AWSConfParser as SUT
from awsconfigparser import Backup,CFile

try:
    awsops = SUT("xx",must_exist=True)
except:
    print("TEST PASSED: xx failed")

default = SUT("default",must_exist=True)
print(default.profile_presens)
default.new_credentials({})
# NO SAVE

defaultxx = SUT("defaultxx",must_exist=False)
defaultxx.new_credentials(
    { "token":"sdfksdj",
    "ID":"dsddf" },
    backup=Backup.UNLESS_TOKEN)

defaultxx.save("some-temp.file")
print("Ops I just wrote to your ~/.aws/credentials file :-D")
