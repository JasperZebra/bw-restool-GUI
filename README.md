# Battalion Wars Unified Tool V1.2
The Battalion Wars Unified Tool combines the restool and the texture convertor that were made by [Yoshi2](https://github.com/RenolY2. It handles RES archive extraction and texture file conversion with automatic game version detection.

# RES Converter Tab
Extracts `.res` and `.res.gz` archive files from Battalion Wars games.

## **Single File Conversion:**
1. Click `Select File` under **"Convert Single File"**
2. Choose a `.res` **(For BW1) ** or `.res.gz` **(For BW2)** file
3. The tool automatically detects the game version
4. Extracted files are saved here in the root of the `.exe`:
   - For BW1: `converted_res_files/bw1/`
   - For BW2: `converted_res_files/bw2/`

## **Single File Repacking:**
1. Click `Select Folder` under **"Repack Single Folder"**
2. Choose a `.res` folder **(For BW1) ** or `.res.gz` **(For BW2)** file
3. The tool automatically detects the game version
4. Repacked files are saved here in the root of the `.exe`:
   - For BW1: `repacked_res_files/bw1/`
   - For BW2: `repacked_res_files/bw2/`

## **Batch Conversion:**
1. Click `Select Folder` under **"Batch Convert"**
2. Choose the **"CompoundFiles"** folder for either bw1 or bw2 to start the converting.
3. The tool searches all subfolders and automatically separates files by game version
4. Extracted files are saved here in the root of the `.exe`:
   - For BW1: `converted_batch_res_files/bw1/`
   - For BW2: `converted_batch_res_files/bw2/`

## **Batch Repacking:**
1. Click `Select Folder` under **"Batch Repack"**
2. Choose either the `bw1` or `bw2` folders in the `repacked_res_files` folder for either bw1 or bw2 to start the repacking.
3. The tool searches all subfolders and automatically separates files by game version
4. Repacked files are saved here in the root of the `.exe`:
   - For BW1: `repacked_res_files/bw1/`
   - For BW2: `repacked_res_files/bw2/`

# Texture Converter Tab
Converts texture files between `.texture` and `.png` formats and back for both games.

## **Single File Conversion (4 options):**
- **BW1: Texture to PNG** - Convert one BW1 `.texture` file to `.png`
- **BW1: PNG to Texture** - Convert one `.png` file to BW1 `.texture` format
- **BW2: Texture to PNG** - Convert one BW2 `.texture` file to `.png`
- **BW2: PNG to Texture** - Convert one `.png` file to BW2 `.texture` format

## **Batch Conversion (4 options):**
- Select either `converted_batch_res_files/bw1/` or `converted_batch_res_files/bw2/` and the tool will automatically find all `Textures` subfolders
- Converts all matching files in each `Textures` folder
- Choose the appropriate batch option for your game version and conversion direction
