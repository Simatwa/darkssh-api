import click
from darkssh.main import country_codes_map, SSH
import os

@click.command()
@click.argument("output", type=click.Path(resolve_path=True))
@click.option(
    "-u",
    "--username",
    help="Server login username",
    type=click.STRING,
    prompt="Enter server login username",
)
@click.option(
    "-p",
    "--password",
    help="Server login passphrase",
    prompt="Enter server login passphrase",
)
@click.option(
    "-l",
    "--location",
    help="Server location",
    type=click.Choice(list(country_codes_map.keys())),
    default="United States",
)
@click.option(
    "-t",
    "--timeout",
    help="Http request timeout",
    type=click.FLOAT,
    default=20,
)
@click.option(
    "-i",
    "--indent",
    type=click.INT,
    help="Ouput json format indentation level",
    default=4,
)
@click.option(
    "-d",
    "--dir",
    help="Working directory",
    default=os.getcwd(),
    type=click.Path(
        file_okay=False,
        exists=True,
        writable=True,
        resolve_path=True,
    ),
)
@click.option(
    "--summarize",
    is_flag=True,
    help="Stdout server info in http-custom-friendly format.",
)
def generate(output, username, password, location, timeout, indent, dir, summarize):
    """Generate a new ssh server"""
    ssh_instance = SSH(country=location)
    ssh_instance.timeout = timeout
    path_to_captcha_image = ssh_instance.download_captcha_image(dir=dir)
    click.secho(f"Opening captcha image '{path_to_captcha_image}'", fg="yellow")
    click.launch(path_to_captcha_image)
    captcha_value = click.prompt("Enter captcha value")
    click.secho("Creating server ...", fg="green")
    server_info = ssh_instance.generate(
        username=username, password=password, captcha=captcha_value
    )
    jsonified_server_info = server_info.model_dump_json(indent=indent)
    if summarize:
        summarized_info = (
            f'AUTH : "{server_info.data.ip}:{server_info.data.op.split(',')[0]}'
            f'@{server_info.data.username}:{server_info.data.password}\n\n"'
            f'PAYLOAD : "{server_info.data.data.payload_http}"'
        )
        click.secho(
            summarized_info,
            color="cyan",
        )
    else:
        click.secho(jsonified_server_info, fg="cyan")
    save_to = os.path.join(dir, output)
    click.secho(f"Saving server info to '{save_to}'", fg='yellow')
    with open(save_to, "w") as fh:
        fh.write(jsonified_server_info)


def main():
    try:
        generate()
    except Exception as e:
        click.secho(f"Quitting - {e.args[1] if e.args and len(e.args)>1 else e}")
