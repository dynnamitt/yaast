# Yaast (Jåst)



## YetAnotherAWSSessionTool

*Why?* ..After obtaining a normal accessKey set, 
the MFA enabled user faces the challege of 
mantaining a daily set of temp accessKeys+token (session) for
use with awscli, sdks and the stuff like terraform.

## 0. Setup "start" profile

    aws configure --profile awsops
    # PASTE keys from aws csv file ...
    
    vim ~/.aws/config 
    # ADD mfa_serial = arn:aws:iam::0000000:mfa/xxxxxxx

## 1. Execute

Writes a new [default] section into your $HOME/.aws/credentials,
after downloading a new SESSION temp access/token set through a "start" profile.
Start profile name defaults to [awsops] and should have 'mfa_serial' set, together with accesskeys.

Both the *start* and *dest* profiles names can be selected with flags

    yaast [-h] [flags] <mfacode>


*DEPENDS* on botocore

