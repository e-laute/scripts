import pandas as pd
import os

from datetime import datetime

RDM_TOKEN = os.getenv("RDM_TEST_API_TOKEN")
# RDM_TOKEN = os.getenv("RDM_API_TOKEN")
RDM_API_URL = "https://test.researchdata.tuwien.ac.at/api/records"
# RDM_API_URL = "https://researchdata.tuwien.ac.at/api/records"

MEI_FILES_PATH = "../files"

sources_excel_df = pd.read_excel("xlsxs/sources_table.xlsx")
sources_table = pd.DataFrame()
sources_table["source_id"] = sources_excel_df["ID"].fillna(
    sources_excel_df["Shelfmark"]
)
sources_table["source_name"] = sources_excel_df["Title"]
sources_table["source_link"] = sources_excel_df["Source_link"].fillna("")
sources_table["RISM_link"] = sources_excel_df["RISM_link"].fillna("")
sources_table["VD_16"] = sources_excel_df["VD_16"].fillna("")


def look_up_source_title(source_id):
    return sources_table.loc[
        sources_table["source_id"] == source_id,
        "source_name",
    ].values[0]


def make_html_link(url):
    return f'<a href="{url}" target="_blank">{url}</a>'


def look_up_source_links(source_id):
    source_link = sources_table.loc[
        sources_table["source_id"] == source_id,
        "source_link",
    ].values[0]
    rism = sources_table.loc[
        sources_table["source_id"] == source_id,
        "RISM_link",
    ].values[0]
    vd16 = sources_table.loc[
        sources_table["source_id"] == source_id,
        "VD_16",
    ].values[0]

    links = []
    if source_link:
        links.append(source_link)
    if rism:
        links.append(rism)
    if vd16:
        links.append(vd16)

    return links


def get_metadata(mei_file):
    return None


def create_description(metadata_dict):
    links_stringified = ""
    links = look_up_source_links(metadata_dict["source_id"])
    for link in links if links else []:
        links_stringified += make_html_link(link) + ", "

    # links_stringified = ", ".join(look_up_source_links(metadata_dict["source_id"]))
    source_id = metadata_dict["source_id"]
    work_number = metadata_dict["work_id"].split("_")[-1]
    platform_link = make_html_link(
        f"https://edition.onb.ac.at/fedora/objects/o:lau.{source_id}/methods/sdef:TEI/get?mode={work_number}"
    )

    part1 = f" <h1>Audio recording of a lute piece from the E-LAUTE project</h1><h2>Overview</h2><p>This dataset contains an audio recording of the piece \"{metadata_dict['title']}\", a 16th century lute music piece originally notated in lute tablature, created as part of the E-LAUTE project (<a href=\"https://e-laute.info/\">https://e-laute.info/</a>). The recording preserves and makes historical lute music from the German-speaking regions during 1450-1550 accessible.</p><p>The recording is based on the work with the title \"{metadata_dict['title']}\" and the id \"{metadata_dict['work_id']}\" in the e-lautedb. It is found on the page(s) or folio(s) {metadata_dict['fol_or_p']} in the source \"{look_up_source_title(metadata_dict['source_id'])}\" with the source-id \"{metadata_dict['source_id']}\".</p>"

    part4 = f"<p>The original source and multiple transcriptions of the work can be found on the E-LAUTE platform: {platform_link}.</p>"

    if links_stringified not in [None, ""]:
        part2 = f"<p>Links to the source: {links_stringified}.</p>"

    part3 = '<h2>Dataset Contents</h2><p>This dataset includes:</p><ul><li><strong>Audio file</strong>: An audio recording of the lute piece in .wav format</li>  <li><strong>Metadata file</strong>: A metadata file with detailed information about the recording in .json format</li></ul><h2>About the E-LAUTE Project</h2><p><strong>E-LAUTE: Electronic Linked Annotated Unified Tablature Edition - The Lute in the German-Speaking Area 1450-1550</strong></p><p>The E-LAUTE project creates innovative digital editions of lute tablatures from the German-speaking area between 1450 and 1550. This interdisciplinary "open knowledge platform" combines musicology, music practice, music informatics, and literary studies to transform traditional editions into collaborative research spaces.</p><p>For more information, visit the project website: <a href="https://e-laute.info/">https://e-laute.info/</a></p>'

    return part1 + part4 + part2 + part3


def create_related_identifiers(links):
    related_identifiers = []
    for link in links:
        related_identifiers.append(
            {
                "identifier": link,
                "relation_type": {
                    "id": "ispartof",
                    "title": {"en": "Is part of"},
                },
                "resource_type": {
                    "id": "other",
                    "title": {"de": "Anderes", "en": "Other"},
                },
                "scheme": "url",
            },
        )
    return related_identifiers


def fill_out_basic_metadata(metadata_dict):
    metadata = {
        "metadata": {
            "title": f'{metadata_dict["title"]} ({metadata_dict["work_id"]})',
            # "additional_titles": [
            #     {
            #         "lang": {
            #             "id": "gmh",
            #             "title": {"en": "Middle High German (ca. 1050-1500)"},
            #         },
            #         "title": metadata_dict["title"],
            #         "type": {
            #             "id": "alternative-title",
            #             "title": {"en": "Alternative title"},
            #         },
            #     },
            #    (
            #     {
            #         "lang": {"id": "deu", "title": {"en": "German"}},
            #         "title": metadata_dict["translated_title"] ,
            #         "type": {
            #             "id": "translated-title",
            #             "title": {"en": "Translated title"},
            #         },
            #     },) if metadata_dict["translated_title"] else None
            # ],
            "creators": [
                {
                    "person_or_org": {
                        "family_name": metadata_dict["performer_lastname"],
                        "given_name": metadata_dict["performer_firstname"],
                        "type": "personal",
                    },
                    "role": {
                        "id": "other",
                        "title": {"en": "Other"},
                    },
                },
            ],
            "contributors": [
                {
                    "person_or_org": {
                        "family_name": metadata_dict["performer_lastname"],
                        "given_name": metadata_dict["performer_firstname"],
                        "type": "personal",
                    },
                    "role": {
                        "id": "other",
                        "title": {"en": "Other"},
                    },
                },
                {
                    "affiliations": [{"id": "04d836q62", "name": "TU Wien"}],
                    "person_or_org": {
                        "family_name": "Jaklin",
                        "given_name": "Julia Maria",
                        "name": "Jaklin, Julia Maria",
                        "type": "personal",
                    },
                    "role": {
                        "id": "contactperson",
                        "title": {"en": "Contact person"},
                    },
                },
            ],
            "description": create_description(metadata_dict),
            "publication_date": datetime.today().strftime("%Y-%m-%d"),
            "dates": [
                {
                    "date": metadata_dict["date"],
                    "description": "Recording date",
                    "type": {"id": "created", "title": {"en": "Created"}},
                }
            ],
            "publisher": "E-LAUTE",
            "references": [{"reference": "https://e-laute.info/"}],
            "related_identifiers": [],
            "resource_type": {
                "id": "sound",
                "title": {"de": "Audio", "en": "Audio"},
            },
            "rights": [
                {
                    "description": {
                        "en": "Permits almost any use subject to providing credit and license notice. Frequently used for media assets and educational materials. The most common license for Open Access scientific publications. Not recommended for software."
                    },
                    "icon": "cc-by-sa-icon",
                    "id": "cc-by-sa-4.0",
                    "props": {
                        "scheme": "spdx",
                        "url": "https://creativecommons.org/licenses/by-sa/4.0/legalcode",
                    },
                    "title": {
                        "en": "Creative Commons Attribution Share Alike 4.0 International"
                    },
                }
            ],
        }
    }

    # Add producer if it exists and is not NaN
    if pd.notna(metadata_dict["producer"]):
        metadata["metadata"]["creators"].append(
            {
                "person_or_org": {
                    "family_name": metadata_dict["producer_lastname"],
                    "given_name": metadata_dict["producer_firstname"],
                    "name": metadata_dict["producer"],
                    "type": "personal",
                },
                "role": {"id": "producer", "title": {"en": "Producer"}},
            }
        )
    if pd.notna(metadata_dict["producer"]):
        metadata["metadata"]["contributors"].append(
            {
                "person_or_org": {
                    "family_name": metadata_dict["producer_lastname"],
                    "given_name": metadata_dict["producer_firstname"],
                    "name": metadata_dict["producer"],
                    "type": "personal",
                },
                "role": {"id": "producer", "title": {"en": "Producer"}},
            }
        )

    links_to_source = look_up_source_links(metadata_dict["source_id"])
    if links_to_source:
        if pd.notna(metadata_dict["source_link"]):
            metadata["metadata"]["related_identifiers"].extend(
                create_related_identifiers(links_to_source)
            )

    return metadata


def upload_mei_files():
    """
    Uploads MEI files to TU RDM.
    """
    # Get all MEI files in the directory
    mei_files = [f for f in os.listdir(MEI_FILES_PATH) if f.endswith(".mei")]

    if not mei_files:
        print("No MEI files found to upload.")
        return

    for mei_file in mei_files:

        # mei_metadata = get_metadata(mei_file) # TODO: extract metadata from MEI file
        fill_out_basic_metadata(
            {
                "title": "Example Title",
                "work_id": "example_work_id",
                "source_id": "example_source_id",
                "fol_or_p": "example_fol_or_p",
                "date": "2023-10-01",
                "performer_firstname": "John",
                "performer_lastname": "Doe",
                "producer_firstname": "Jane",
                "producer_lastname": "Smith",
                "producer": "Jane Smith",
            }
        )
