import click


def main():
    click.echo('Continue? [yn] ', nl=False)
    c = click.getchar()
    click.echo()
    if c == 'y':
        click.echo('We will go on')
    elif c == 'n':
        click.echo('Abort!')
    else:
        click.echo('Invalid input :(')
    pass


if __name__ == "__main__":
    main()