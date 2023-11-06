from pcbnewTransition.pcbnew import LoadBoard


class Board:
    def __init__(self, fname, width=0, length=0, rotation=0, x=0, y=0):
        self.fname = fname
        self.width = width
        self.length= length
        self.board = LoadBoard(fname)
        self.rotation = rotation
        self.x = x
        self.y = y


def makeGrid(boards):
    '''
    For now just take the boards as given with
    '''
    pass


def buildLayout(preset, panel, sourceBoard, sourceArea):
    """
    Build layout for the boards - e.g., make a grid out of them.

    Return the list of created substrates and framing substrates. Also ensures
    that the partition line is build properly.
    """
    layout = preset["layout"]
    framing = preset["framing"]
    try:
        type = layout["type"]
        if type == "grid":
            placementClass = getPlacementClass(layout["alternation"])
            placer = placementClass(
                verSpace=layout["vspace"],
                horSpace=layout["hspace"],
                hbonewidth=layout["hbackbone"],
                vbonewidth=layout["vbackbone"],
                hboneskip=layout["hboneskip"],
                vboneskip=layout["vboneskip"],
                hbonefirst=layout["hbonefirst"],
                vbonefirst=layout["vbonefirst"])
            substrates = panel.makeGrid(
                boardfile=sourceBoard, sourceArea=sourceArea,
                rows=layout["rows"], cols=layout["cols"], destination=VECTOR2I(0, 0),
                rotation=layout["rotation"], placer=placer,
                netRenamePattern=layout["renamenet"], refRenamePattern=layout["renameref"],
                bakeText=layout["baketext"])
            framingSubstrates = dummyFramingSubstrate(substrates, preset)
            panel.buildPartitionLineFromBB(framingSubstrates)
            backboneCuts = buildBackBone(layout, panel, substrates, framing)
            return substrates, framingSubstrates, backboneCuts
        if type == "plugin":
            lPlugin = layout["code"](preset, layout["arg"], layout["renamenet"],
                                     layout["renameref"], layout["vspace"],
                                     layout["hspace"], layout["rotation"])
            substrates = lPlugin.buildLayout(panel, sourceBoard, sourceArea)
            framingSubstrates = dummyFramingSubstrate(substrates, preset)
            lPlugin.buildPartitionLine(panel, framingSubstrates)
            backboneCuts = lPlugin.buildExtraCuts(panel)
            return substrates, framingSubstrates, backboneCuts

        raise PresetError(f"Unknown type '{type}' of layout specification.")
    except KeyError as e:
        raise PresetError(f"Missing parameter '{e}' in section 'layout'")



def main(output, boards, preset):
    """
    The panelization logic is separated into a separate function so we can
    handle errors based on the context; e.g., CLI vs GUI
    """
    from kikit import panelize_ui_impl as ki
    from kikit.panelize import Panel
    from pcbnewTransition.transition import pcbnew
    from itertools import chain

    if preset["debug"]["deterministic"]:
        pcbnew.KIID.SeedGenerator(42)
    if preset["debug"]["drawtabfail"]:
        import kikit.substrate
        kikit.substrate.TABFAIL_VISUAL = True

    panel = Panel(output)
    origin = [0, 0]
    panel_origin = pcbnew.wxPointMM(*origin)

    panel.inheritDesignSettings(boards[0].board)
    panel.inheritProperties(boards[0].board)
    panel.inheritTitleBlock(boards[0].board)


    for board in boards:
        bounding_box = panel.appendBoard(
            board.fname,
            destination=panel_origin,
            origin=panelize.Origin.TopLeft,
            tolerance=1 * mm
        )

        panel_origin = pcbnew.wxPoint(
            bounding_box.GetX(),
            bounding_box.GetY() + bounding_box.GetHeight() + board_spacing,
        )


    #sourceArea = ki.readSourceArea(preset["source"], board)
    #substrates, framingSubstrates, backboneCuts = \
    #    ki.buildLayout(preset, panel, input, sourceArea)

    useHookPlugins(lambda x: x.afterLayout(panel, substrates))

    tabCuts = ki.buildTabs(preset, panel, substrates, framingSubstrates)

    useHookPlugins(lambda x: x.afterTabs(panel, tabCuts, backboneCuts))

    frameCuts = ki.buildFraming(preset, panel)

    useHookPlugins(lambda x: x.afterFraming(panel, frameCuts))

    ki.buildTooling(preset, panel)
    ki.buildFiducials(preset, panel)
    for textSection in ["text", "text2", "text3", "text4"]:
        ki.buildText(preset[textSection], panel)
    ki.buildPostprocessing(preset["post"], panel)

    ki.makeTabCuts(preset, panel, tabCuts)
    ki.makeOtherCuts(preset, panel, chain(backboneCuts, frameCuts))

    useHookPlugins(lambda x: x.afterCuts(panel))

    ki.buildCopperfill(preset["copperfill"], panel)

    ki.setStackup(preset["source"], panel)
    ki.setPageSize(preset["page"], panel, board)
    ki.positionPanel(preset["page"], panel)

    ki.runUserScript(preset["post"], panel)
    useHookPlugins(lambda x: x.finish(panel))

    ki.buildDebugAnnotation(preset["debug"], panel)

    panel.save(reconstructArcs=preset["post"]["reconstructarcs"],
               refillAllZones=preset["post"]["refillzones"])


import click
@click.command()
@click.option("--board_f", required=True)
@click.option("--out", required=True)
@click.option("--preset", required=True)
def click_main(**kwargs):
    board = Board(kwargs["board_f"])
    main(output=kwargs["out"], boards=[board]*5, preset=kwargs["preset"])

if __name__ == "__main__":
    click_main()
