# kikit-multipanel

This repo includes a CLI tool, helper library, example presets, and example projects for using kikit for multiple designs in a single panel.

This should be able to handle correctly placed selections of different boards.
Some extra board sections will need to be added in if the panel has gaps that are too large.

![](panel.svg)
![](panel-3D.png)

# installation under Linux

1. Download this repository via git or zip file (in this case unzip it)
2. ```sh
    cd kikit-multipanel
    ```
3. ```sh
   sudo make install
   ```
4. test your installation with
   ```sh
    kikit_multipanel --help
   ```
# usage example
```sh
kikit_multipanel --fname panel.xlsx --out panel.kicad_pcb --preset_f preset.json
```

## Future Developments
+ Add a rectangular packing optimization to autoplace the boards.
+ Centroid file correction
+ Add checking for sections that will be cut off
