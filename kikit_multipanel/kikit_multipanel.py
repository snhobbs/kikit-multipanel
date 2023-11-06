import itertools
import pandas
from kikit import panelize_ui_impl
from kikit.units import mm, deg
from kikit.common import fromDegrees
from kikit.panelize import Panel
from pcbnewTransition.transition import pcbnew
# import pcbnew
import logging


def panelize(df, out, preset):
    '''
    Panelize a set of arbitrary board files.
    :param pandas.DataFrame df: DataFrame of board with columns fname, x, y, rotation
    :param str out: Panel output name
    :param dict preset: Fully formated preset object.
    :returns None:
    '''
    settings_board = df.iloc[0]["fname"]
    board = pcbnew.LoadBoard(settings_board)
    panel = panelize.Panel(out)
    panel.inheritDesignSettings(board)
    panel.inheritProperties(board)
    panel.inheritTitleBlock(board)

    #cuts = panel.makeFrame(frame_width, frame_hor_space, frame_ver_space)
    frame_width = preset["framing"]["width"]
    rail_width = frame_width
    backbone_width = frame_width

    tab_width = 2*mm#preset["tabs"]["width"]
    backbone_cut_width = tab_width

    # add the boards

    origin = [0, 0]
    panel_origin = pcbnew.wxPointMM(*origin)
    for _, line in df.iterrows():
        logging.info("Loading board from file: %s", line["fname"])
        bounding_box = panel.appendBoard(
            filename=line["fname"],
            destination=pcbnew.wxPoint(line["x"], line["y"]),
            rotationAngle=fromDegrees(line["rotation"]),
            origin=panelize.Origin.TopLeft,
            tolerance=1 * mm,
            inheritDrc=False  # Required to avoid merging DRC rules
        )
        # ignore bounding box, we should already know the sizes

    # create a dummy framing substrate (required for partition lines)
    # (frame_hor_offset, frame_ver_offset)

    framing_substrates = panelize_ui_impl.dummyFramingSubstrate(
        panel.substrates, preset
    )

    panel.buildPartitionLineFromBB(boundarySubstrates=framing_substrates, safeMargin=0)

    # add the tabs
    tabs = preset["tabs"]
    panel.buildTabAnnotationsFixed(hcount=tabs["hcount"], vcount=tabs["vcount"], hwidth=tabs["hwidth"], vwidth=tabs["vwidth"], minDistance=tabs["mindistance"], ghostSubstrates=framing_substrates)

    # add a backbone

    backboneCuts = panel.renderBackbone(
        0, backbone_width, backbone_cut_width, backbone_cut_width
    )

    # add frame


    # create the tab cuts
    # panel.copperFillNonBoardAreas()
    cuts_pr = preset["cuts"]

    #print(tabCuts)

    #tab_cuts = panel.buildTabsFromAnnotations(2*mm)#preset['post']["millradius"])
    tabCuts = panelize_ui_impl.buildTabs(preset, panel, panel.substrates, framing_substrates)
    panelize_ui_impl.makeTabCuts(preset, panel, tabCuts)
    cuts = panelize_ui_impl.buildFraming(preset, panel)
    frame_cuts = itertools.chain(*cuts)
    frameCuts = panelize_ui_impl.buildFraming(preset, panel)
    panelize_ui_impl.makeOtherCuts(preset, panel, chain(backboneCuts, frameCuts))
    panelize_ui_impl.buildPostprocessing(preset["post"], panel)
    panelize_ui_impl.buildFiducials(preset, panel)
    panelize_ui_impl.buildTooling(preset, panel)
    panelize_ui_impl.buildCopperfill(preset["copperfill"], panel)
    #panelize_ui_impl.buildText(preset["text"], panel)
    panel.save(reconstructArcs=True)
    return None
