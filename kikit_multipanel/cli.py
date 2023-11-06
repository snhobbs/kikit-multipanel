"""Console script for kikit_multipanel."""
import sys
import click
from . import kikit_multipanel

@click.command()
@click.option("--fname", required=True)
@click.option("--out", required=True)
@click.option("--preset_f", required=True)
def main(fname, out, preset_f):
    preset = panelize_ui_impl.loadPreset(preset_f)
    panelize_ui_impl.postProcessPreset(preset)
    df = pandas.read_excel(fname)
    kikit_multipanel.panelize(df=df, out=out, preset=preset)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
