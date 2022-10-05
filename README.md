# LEDesignController
A python script for controlling a zig-zag segmented LED matrix strip with a Raspberry Pi. This makes use of the rpi_ws281x library, which may need to be installed prior to use. 
 
 ![LEDesignController_Kirby](https://user-images.githubusercontent.com/26748231/193985309-b930d845-b889-4a88-9405-7ea9b89d9629.gif)

## Usage:
This script requires two additional files within the same directory to work properly; a text file containing the pattern to be displayed and a `config.cfg` file with various configurations for said pattern and the matrix strip. These must be formatted in a paticular way to work properly with the script, but can be made easily using this designer tool on Windows. As such, it is not recommended to type these files manually, but it can be done if formatted as follows.

1. Config file:
   - Each property must be set on its own separate line, lines that start with the ! character will be ignored:
     - `mode = x`, in which x is 0, 1, or 2 (static, scrolling, or frame-by-frame patterns respectively).
     - `rows = x`, in which x is the physical number of rows on the matrix strip.
     - `columns = x`, in which x is the physical number of columns on the matrix strip.
     - `scrollMode = x`, in which x is 0, 1, 2, or 3 (right to left, left to right, top to bottom, or bottom to top).
     - `preFrame = x`, in which x is the number of seconds before the first frame of an animated pattern.
     - `postFrame = x`, in which x is the number of seconds after the last frame of an animated pattern.
     - `patternFile = x`, in which x is name of the text file containing the pattern, including the file extension. 
     - `frames = x`, in which x is the number of frames in a frame-by-frame pattern.
     - `gpio = x`, in which x is the GPIO pin number that the matrix strip is connected to.
     - `freqhz = x`, in which x is the signal frequency in khz. Try 800.
     - `dma = x`, in which x is the signal channel. Try 10.
     - `brightness = x`, in which x is a value between 0 - 255, controlling the brightness of the LEDs.
     - `inv = x`, in which x is 0 or 1 (1 inverts the signal).
     - `speed = x`, in which x is a decimal value greater than 0, controlling the speed of an animated pattern.
     - `gapColor = x`, in which x is a hexidecimal color value, meant to be displayed during in-betweens for scrolling patterns.
     
   - This file must be named `config.cfg` and must contain a value for a pattern file name.
   
2. Pattern file:
   - Each value must be set on its own separate line:
   
     - `#000000` - `#FFFFFF` is used to set the color of a pixel in a row on the matrix.
     - `-` is used as a divider to mark the end of a row on the matrix.
     - `=` is used as a divider to mark the end of a frame for a frame-by-frame pattern.

Once completed, transfer the script along with the two additional files to the same directory on a Raspberry Pi running Raspberry Pi OS, then run the script. 
