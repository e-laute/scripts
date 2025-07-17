import os
import shutil
import xml.etree.ElementTree as ET

GLT_to_F_and_ILT = ["enc_dipl_GLT.mei", "enc_ed_GLT.mei"]

# XML declaration and model declarations
XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>'
RELAXNG_MODEL = '<?xml-model href="https://music-encoding.org/schema/5.1/mei-all.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>'
SCHEMATRON_MODEL = '<?xml-model href="https://music-encoding.org/schema/5.1/mei-all.rng" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>'

ET.register_namespace("", "http://www.music-encoding.org/ns/mei")


# Inject XML file with proper model declarations
def inject_xml_model_declaration(tree, file_name):
    # Get the XML content as string without the declaration
    xml_content = ET.tostring(tree.getroot(), encoding="unicode")

    # Build the complete file content with declarations
    content_lines = [
        XML_DECLARATION,
        RELAXNG_MODEL,
        SCHEMATRON_MODEL,
        xml_content,
    ]

    with open(file_name, "w", encoding="utf-8") as file:
        file.write("\n".join(content_lines))


# Process MEI files to convert GLT to FLT and ILT
def process_mei_file(input_file, output_dir):
    french_dir = os.path.join(output_dir, "FLT")
    italian_dir = os.path.join(output_dir, "ILT")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(french_dir, exist_ok=True)
    os.makedirs(italian_dir, exist_ok=True)
    if not input_file.endswith("GLT.mei"):
        return False
    try:
        tree = ET.parse(input_file)
        tree_root = tree.getroot()

        output_french = os.path.join(
            french_dir, os.path.basename(input_file.replace("GLT", "FLT"))
        )
        output_italian = os.path.join(
            italian_dir, os.path.basename(input_file.replace("GLT", "ILT"))
        )

        # Remove rests from the tree
        def iterator(parents):
            for child in reversed(parents):
                if len(child) >= 1:
                    iterator(child)
                if child.tag == "{http://www.music-encoding.org/ns/mei}rest":
                    if (
                        parents.tag
                        == "{http://www.music-encoding.org/ns/mei}tabGrp"
                    ):
                        has_tabDurSym = any(
                            c.tag
                            == "{http://www.music-encoding.org/ns/mei}tabDurSym"
                            for c in parents
                        )
                        if not has_tabDurSym:
                            parents.append(
                                ET.Element(
                                    "{http://www.music-encoding.org/ns/mei}tabDurSym",
                                )
                            )
                    parents.remove(child)

        iterator(tree_root)

        # Remove tab.line from <note> and <tabDurSym>
        for note in tree_root.findall(
            ".//{http://www.music-encoding.org/ns/mei}note"
        ):
            if "tab.line" in note.attrib:
                note.attrib.pop("tab.line")
        for tabDurSym in tree_root.findall(
            ".//{http://www.music-encoding.org/ns/mei}tabDurSym"
        ):
            if "tab.line" in tabDurSym.attrib:
                tabDurSym.attrib.pop("tab.line")

        staffDef = tree_root.find(
            ".//{http://www.music-encoding.org/ns/mei}staffDef"
        )
        title_part_abbr = tree_root.find(
            ".//{http://www.music-encoding.org/ns/mei}title/{http://www.music-encoding.org/ns/mei}titlePart/{http://www.music-encoding.org/ns/mei}abbr"
        )
        # Ensure, that lines='6' and remove tab.align and tab.anchorline
        staffDef.set("lines", "6")
        staffDef.attrib.pop("tab.align", None)
        staffDef.attrib.pop("tab.anchorline", None)

        # write French file
        staffDef.set("notationtype", "tab.lute.french")
        if title_part_abbr is not None:
            title_part_abbr.text = "FLT"
            title_part_abbr.set("expan", "French Lute Tablature")
        inject_xml_model_declaration(tree, output_french)

        # write Italian file
        staffDef.set("notationtype", "tab.lute.italian")
        if title_part_abbr is not None:
            title_part_abbr.text = "ILT"
            title_part_abbr.set("expan", "Italian Lute Tablature")
        inject_xml_model_declaration(tree, output_italian)
        return True
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")
        return False


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = "converted"

    # Create output directories
    german_dir = os.path.join(output_dir, "GLT")
    french_dir = os.path.join(output_dir, "FLT")
    italian_dir = os.path.join(output_dir, "ILT")
    cmn_dir = os.path.join(output_dir, "CMN")
    os.makedirs(german_dir, exist_ok=True)
    os.makedirs(french_dir, exist_ok=True)
    os.makedirs(italian_dir, exist_ok=True)
    os.makedirs(cmn_dir, exist_ok=True)

    # Find all folders that start with "Jud_1523-2"
    for folder_name in os.listdir(base_dir):
        if folder_name.startswith("Jud_1523-2") and os.path.isdir(
            os.path.join(base_dir, folder_name)
        ):
            folder_path = os.path.join(base_dir, folder_name)

            # Look for GLT.mei and CMN.mei files in this folder
            for file in os.listdir(folder_path):
                if file.endswith("GLT.mei"):
                    input_file = os.path.join(folder_path, file)

                    # Process the file to create FLT and ILT versions
                    if process_mei_file(input_file, output_dir):
                        # Copy the original GLT file to the GLT folder
                        shutil.copy(input_file, os.path.join(german_dir, file))
                    else:
                        print(f"Failed to process {file}")

                elif file.endswith("CMN.mei"):
                    input_file = os.path.join(folder_path, file)
                    try:
                        # Copy CMN file to the CMN folder
                        shutil.copy(input_file, os.path.join(cmn_dir, file))
                    except Exception as e:
                        print(f"Failed to copy {file}: {str(e)}")


if __name__ == "__main__":
    main()
