from . import write_session
from . import die
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
def console_url(args):
    """Assume-role and output URL for web console"""
    pass


if __name__ == '__main__':
    cli_group()
