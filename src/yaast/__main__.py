from . import write_session
from . import die, APP_META
import click


@click.group(context_settings={'show_default': True})
def cli_group():
    """AWS Session helper-utils"""
    pass


@cli_group.command()
@click.argument("mfa_code")
@click.option("--profile", "-p",
              default="awsops",
              help="Base profile w/ mfa_serial & credentials")
@click.option("--dest-profile", "-d",
              default="default",
              help="Dest profile to write into ~/.aws")
def mfa(**args):
    """MFA resolver, write session/token into ~/.aws/credentials """
    try:
        write_session.resolve(**args)
    except Exception as e:
        die(e)


@cli_group.command()
@click.option("--role-arn", "-r", help="role to assume first")
@click.option("--tag", "-t", help="tag(s) if role-arn")
def console_url(**args):
    """Output URL for web console, assume-role as option"""
    pass


@cli_group.command()
@click.argument("role_arn")
@click.option("--tag", "-t", help="tag(s)")
@click.option("--session-name", "-n", help="name the session", default=APP_META['name'])
def assume(**args):
    """just assume role"""
    pass


if __name__ == '__main__':
    cli_group()
