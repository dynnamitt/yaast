YetAnotherAWSSessionTool
========================

After obtaining a normal accessKey set, 
the MFA enabled user faces the challege of 
mantaining a daily set of temp accessKeys+token (session) for
use with awscli, sdks and terrible stuff like terraform.

## 1. write_session (MFA resolver)

Writes a new [default] section into your $HOME/.aws/credentials,
after downloading a new SESSION temp access/token set through a "start" profile.
Start profile name defaults to [awsops] and should have 'mfa_serial' set, together with accesskeys.

Both the *start* and *dest* profiles names can be selected with flags

    ./write_session.py --help


*DEPENDS* on botocore (pip3 install botocore)

## 2a. assume+console (shell version)

Posix script that downloads AssumeRole temp access/token set and 
also mixes in a CONSOLE_URL signed with these fresh credentials

     ./assume+console.sh [role_arn-profile]
     
*DEPENDS* on awscli , jq and curl

## 2b assume+console (py3 version)

PENDING


## 3 Writing new profiles into $HOME/.aws/config

PENDING

Create multiple profiles from a cfg data file.

### 3.1 cfg file format

Format from basefarm/aws-session-tool :

```
<ROLEID>      <ROLEARN>  <NAME>        <EXTID>
```

Check sample file _____ .

### 3.2 adding

PENDING

A profile (in ~/.aws/config) will be made using the <NAME>
and adding a 'source_profile' attr to connect the session token/credentials.

The 'source_profile' value will be litteraly 'default' if not given with flag.

*NB:* The 'source_profile' value SHOULD NOT be the same as above <CORE_PROFILE>

```read multiple records from STDIN
add_roles [-s source_profile] [-o] < roles.cfg
```
```single operation
add_role -n <NAME> -r <ROLEARN> [-s source_profile] [-o]
```
NOTE: Customization like region and others can now be added by you in ~/.aws/config

## 4. Shell aliases 

PENDING

Either `awscli --profile x` or `AWS_PROFILE=x ` could be ..
