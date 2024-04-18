from botocore.session import Session



def resolve(app_meta, profile, role_arns, tags):

    aws_session = Session(profile=profile)

    aws_session.assume_role(

    )
