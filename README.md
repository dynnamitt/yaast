YetAnotherAWSSessionTool
========================

## 1. write_session (MFA resolver)

Writes a new [default] section into your ~/.aws/credentials,
after downloading a new SESSION temp access/token set through a "start" profile.

Start profile is [awsops] by default and should have 'mfa_serial' set,
together with accesskeys.

Both the *start* and *dest* profiles names can be selected with flags

    ./write_session.py --help


*DEPENDS* on botocore ( pip install botocore --user )

## 2. assume+console

Posix script that downloads AssumeRole temp access/token set and 
also mixes in a CONSOLE_URL signed with these fresh credentials

     ./assume+console.sh [role_arn-profile]
     
*DEPENDS* on jq and curl
