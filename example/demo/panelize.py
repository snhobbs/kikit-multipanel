#!/usr/bin/env python3

import itertools

from kikit import panelize
from kikit import panelize_ui_impl
from kikit.units import mm
from pcbnewTransition import (
    pcbnew,  # Required due to type difference, see https://github.com/yaqwsx/KiKit/issues/503
)


class Board:
    def __init__(self, fname, width=0, length=0):
        self.fname = fname
        self.width = width
        self.length = length


def order_boards(boards, spacing):
    """
    Order boards into x,y positions.
    Use rect_pact as the algorithm.
    1. Create a bounding box for each board
    2. Add spacing around the boards
    3. Run rect pack
    4. Create a data frame of board files and position / rotation. Pair up the board sizes with the rectangle sizes.
    """
    df = pandas.DataFrame(
        {
            fname: [board.fname for board in boards],
            board: [pcbnew.LoadBoard(str(board.fname)) for board in boards],
        }
    )
    df["bbox"] = [findBoardBoundingBox(board) for board in df["board"]]  # type BOX2I
    df["width"] = [pt.GetWidth() for pt in df["bbox"]]
    df["height"] = [pt.GetHeight() for pt in df["bbox"]]


def main(out, boards, preset_f):
    preset = panelize_ui_impl.loadPreset(preset_f)
    panelize_ui_impl.postProcessPreset(preset)
    # cuts = panel.makeFrame(frame_width, frame_hor_space, frame_ver_space)
    frame_width = 5 * mm
    rail_width = frame_width
    backbone_width = frame_width

    tab_width = 2 * mm
    backbone_cut_width = tab_width
    board_spacing = backbone_width + 2 * tab_width

    frame_hor_space = tab_width
    frame_ver_space = tab_width

    frame_hor_offset = tab_width
    frame_ver_offset = tab_width

    panel = panelize.Panel(out)

    # add the boards

    origin = [0, 0]
    panel_origin = pcbnew.wxPointMM(*origin)
    for board in boards:
        bounding_box = panel.appendBoard(
            board.fname,
            destination=panel_origin,
            origin=panelize.Origin.TopLeft,
            tolerance=1 * mm,
        )

        panel_origin = pcbnew.wxPoint(
            bounding_box.GetX(),
            bounding_box.GetY() + bounding_box.GetHeight() + board_spacing,
        )

    # create a dummy framing substrate (required for partition lines)
    # (frame_hor_offset, frame_ver_offset)

    framing_substrates = panelize_ui_impl.dummyFramingSubstrate(
        panel.substrates, preset
    )

    panel.buildPartitionLineFromBB(boundarySubstrates=framing_substrates, safeMargin=0)

    # dummy = []

    # add the tabs

    # tab_cuts = panel.buildTabsFromAnnotations(fillet=1*mm)
    panel.buildTabAnnotationsFixed(
        hcount=2,
        vcount=2,
        hwidth=1.5,
        vwidth=1.5,
        minDistance=25.4 * mm,
        ghostSubstrates=framing_substrates,
    )
    tab_cuts = panel.buildTabsFromAnnotations(2 * mm)

    # add a backbone

    backbone_cuts = []
    backbone_cuts = panel.renderBackbone(
        0, backbone_width, backbone_cut_width, backbone_cut_width
    )

    # add frame

    cuts = panelize_ui_impl.buildFraming(preset, panel)
    frame_cuts = itertools.chain(*cuts)

    # create the tab cuts
    # panel.copperFillNonBoardAreas()
    panel.makeMouseBites(
        tab_cuts,
        diameter=0.5 * mm,
        spacing=0.75 * mm,
        offset=0 * mm,
        prolongation=0.5 * mm,
    )

    # create the backbone and frame cuts

    panel.makeMouseBites(
        frame_cuts,
        diameter=0.5 * mm,
        spacing=0.75 * mm,
        offset=0 * mm,
        prolongation=0.5 * mm,
    )
    panel.addMillFillets(1 * mm)
    panel.save()


import click


@click.command()
@click.option("--board_f", required=True)
@click.option("--out", required=True)
@click.option("--preset", required=True)
def click_main(**kwargs):
    board = Board(kwargs["board_f"])
    main(out=kwargs["out"], boards=[board] * 5, preset_f=kwargs["preset"])


if __name__ == "__main__":
    click_main()
