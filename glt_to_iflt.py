import os
import shutil
import xml.etree.ElementTree as ET

GLT_to_F_and_ILT = ["enc_dipl_GLT.mei", "enc_ed_GLT.mei"]

ET.register_namespace("", "http://www.music-encoding.org/ns/mei")


# Inject XML model declaration for MEI files
def inject_xml_model_declaration(file_name):
    with open(file_name, "r") as file:
        content = file.read()
        content = content.replace(
            "<?xml version='1.0' encoding='utf-8'?>",
            """<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="https://music-encoding.org/schema/5.1/mei-all.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"?>
<?xml-model href="https://music-encoding.org/schema/5.1/mei-all.rng" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"?>""",
        )
    with open(file_name, "w") as file:
        file.write(content)


# Process MEI files to convert GLT to FLT and ILT
def process_mei_file(input_file, output_dir):
    french_dir = os.path.join(output_dir, "FLT")
    italian_dir = os.path.join(output_dir, "ILT")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(french_dir, exist_ok=True)
    os.makedirs(italian_dir, exist_ok=True)
    if not input_file.endswith("GLT.mei"):
        print(f"Skipping non-GLT file: {input_file}")
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
                    # TODO: add <tabDurSym> instead of <rest> if not already present
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
        tree.write(
            output_french,
            xml_declaration=True,
            encoding="utf-8",
        )
        inject_xml_model_declaration(output_french)

        # write Italian file
        staffDef.set("notationtype", "tab.lute.italian")
        if title_part_abbr is not None:
            title_part_abbr.text = "ILT"
            title_part_abbr.set("expan", "Italian Lute Tablature")
        tree.write(
            output_italian,
            encoding="UTF-8",
            xml_declaration=True,
        )
        inject_xml_model_declaration(output_italian)
        return True
    except Exception as e:
        print(f"Error processing {input_file}: {str(e)}")
        return False


def main():
    input_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "Judenkuenig"
    )
    output_dir = input_dir + "_converted"

    german_dir = os.path.join(output_dir, "GLT")
    os.makedirs(german_dir, exist_ok=True)
    print(f"Current directory: {input_dir}")
    for file in os.listdir(input_dir):
        if file.endswith(".mei"):
            input_file = os.path.join(input_dir, file)
            if process_mei_file(input_file, output_dir):
                shutil.copy(input_file, os.path.join(german_dir, file))
            else:
                print(f"Failed to process {file}")


if __name__ == "__main__":
    main()
