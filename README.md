YetAnotherAWSSessionTool
========================

Will write a new [default] section into your ~/.aws/credentials,
after downloading a new temp access/token set through a "start" profile.

Start profile is [awsops] by default and should have 'mfa_serial' set,
together with accesskeys.

Both start and dest profiles can be overridden by flags

    ./write_session.py --help


DEPENDS on botocore ( pip install botocore --user )

