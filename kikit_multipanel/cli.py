"""Console script for kikit_multipanel."""
import sys
import click
from . import kikit_multipanel, __version__
from kikit import panelize_ui_impl
import pandas


@click.command()
@click.option("--fname", required=True, help="XLS or XLSX panel spreadsheet")
@click.option("--out", required=True, help="Output filename. Should end in .kicad_pcb")
@click.option("--preset_f", required=True, help="Kikit preset json file")
@click.version_option(__version__)
def main(fname, out, preset_f, verison):
    preset = panelize_ui_impl.loadPreset(preset_f)
    panelize_ui_impl.postProcessPreset(preset)
    df = pandas.read_excel(fname)
    kikit_multipanel.panelize(df=df, out=out, preset=preset)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
