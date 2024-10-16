import os
import json

from typing import Union

from rdflib import Namespace, URIRef
from lxml import etree
from PIL import Image as pil_image

iiif_prezi3_context = "http://iiif.io/api/presentation/3/context.json"

nsCanvas = Namespace("https://data.goldenagents.org/datasets/fricktalk2023/canvas/")
nsAnnotationPage = Namespace(
    "https://data.goldenagents.org/datasets/fricktalk2023/annotationpage/"
)
nsAnno = Namespace("https://data.goldenagents.org/datasets/fricktalk2023/annotation/")

GHPREFIX = "https://lvanwissen.github.io/fricktalk-2023/"


def main(
    imagefolder: str,
    annotationfolder: str = None,
    nameslocationsfile: str = None,
    canvasmetadatafile: str = None,
    matcheditemsfile: str = None,
    htrobjectsfile: str = None,
):

    manifest = createManifest(
        imagefolder,
        annotationfolder,
        nameslocationsfile,
        canvasmetadatafile,
        matcheditemsfile,
        htrobjectsfile,
    )

    with open("iiif/manifest.json", "w") as outfile:
        json.dump(manifest, outfile, indent=2)


def createManifest(
    imagefolder: str,
    annotationfolder: str = None,
    nameslocationsfile: str = None,
    canvasmetadatafile: str = None,
    matcheditemsfile: str = None,
    htrobjectsfile: str = None,
):

    manifest = {
        "@context": [
            "http://www.w3.org/ns/anno.jsonld",
            "http://iiif.io/api/presentation/3/context.json",
        ],
        "id": f"{GHPREFIX}iiif/manifest.json",
        "type": "Manifest",
        "label": {
            "en": [
                "Exploring 17th-Century Dutch Domestic Interiors Digitally - Frick Art Reference Library talk 2023"
            ]
        },
        "summary": "Annotation demo, showing the benefits of cross-institutional collaboration",
        "metadata": [
            {
                "label": {"en": ["Title"]},
                "value": {
                    "en": [
                        "Annotation demo, showing the benefits of cross-institutional collaboration"
                    ]
                },
            },
            {
                "label": {"en": ["Provenance"]},
                "value": {
                    "en": [
                        "Amsterdam City Archives, NA 2408.",
                        "Notary Jacob de Winter (1626-1675).",
                        "Inventory dated 1648-1665.",
                    ]
                },
            },
            {"label": {"en": ["Creator"]}, "value": {"en": ["Leon van Wissen"]}},
            {
                "label": {"en": ["Contributor"]},
                "value": {"en": ["Golden Agents project"]},
            },
            {"label": {"en": ["Language"]}, "value": {"en": ["English"]}},
            {"label": {"en": ["Date Statement"]}, "value": {"en": ["2023"]}},
            {"label": {"en": ["Description"]}, "value": {"en": ["DescriptionValue"]}},
            {
                "label": {"en": ["Collection"]},
                "value": {"en": ["Conference presentations"]},
            },
            {
                "label": {"en": ["Subject"]},
                "value": {
                    "en": [
                        "Linked Open Data",
                        "Dutch Golden Age",
                        "Probate inventories",
                        "Getty Provenance Index",
                    ]
                },
            },
            {"label": {"en": ["Other Identifier"]}, "value": {"en": ["doi?"]}},
            {"label": {"en": ["Record Created"]}, "value": {"en": ["2023-03-21"]}},
            {
                "label": {"en": ["Holding Institution"]},
                "value": {"en": ["Golden Agents"]},
            },
        ],
        "homepage": [
            {
                "id": "https://www.goldenagents.org",
                "type": "Text",
                "label": {"en": ["View project information"]},
                "format": "text/html",
            }
        ],
        "logo": [
            {
                "id": f"{GHPREFIX}assets/img/logo-golden-agents.png",
                "type": "Image",
                "format": "image/png",
            }
        ],
        "thumbnail": [
            {
                "id": f"{GHPREFIX}assets/img/logo-golden-agents.png",
                "type": "Image",
                "format": "image/png",
            }
        ],
        "requiredStatement": {
            "label": {"en": ["Terms of Use"]},
            "value": {
                "en": [
                    '<p> <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://licensebuttons.net/i/l/by-sa/transparent/00/00/00/88x31.png"></a><br>This demo is developed by <a xmlns:cc="http://creativecommons.org/ns#" href="https://www.goldenagents.org/" property="cc:attributionName" rel="cc:attributionURL">Golden Agents</a> and is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons BY-SA 4.0 International License</a>. </p>'
                ]
            },
            "format": "text/html",
        },
        "behavior": ["individuals"],
        "start": {
            "id": "https://data.goldenagents.org/datasets/fricktalk2023/canvas/A16098000033",
            "type": "Canvas",
        },
        "items": [],
    }

    items = []

    if nameslocationsfile:
        with open(nameslocationsfile) as infile:
            nameslocationsdata = json.load(infile)
    else:
        nameslocationsdata = dict()

    if canvasmetadatafile:
        with open(canvasmetadatafile) as infile:
            canvasmetadata = json.load(infile)
    else:
        canvasmetadata = dict()

    if matcheditemsfile:
        with open(matcheditemsfile) as infile:
            matcheditems = json.load(infile)
    else:
        matcheditems = dict()

    if htrobjectsfile:
        with open(htrobjectsfile) as infile:
            htrobjectsdata = json.load(infile)
    else:
        htrobjectsdata = dict()

    for fn in sorted(os.listdir(imagefolder)):
        imagepath = os.path.join(imagefolder, fn)
        imagepath = os.path.join(GHPREFIX, imagepath)

        baseFilename, _ = os.path.splitext(fn)

        # HTR annotations
        if annotationfolder:
            annotationpath = os.path.join(annotationfolder, baseFilename + ".json")

            if not os.path.exists(annotationpath):

                annotationpath = None

        else:
            annotationpath = None

        # PersonNames and Locations have been selected by AAA
        nameslocations = nameslocationsdata.get(fn, [])

        # Objects from the HTR
        htrobjects = htrobjectsdata.get(fn, [])

        # Metadata from AAA
        canvasmeta = canvasmetadata.get(fn)
        metadata = []

        if canvasmeta:
            md = {
                "Type of deed": canvasmeta["actType"],
                "Date": canvasmeta["registrationDate"],
                "Description": canvasmeta["description"],
                "Language": canvasmeta["language"].title(),
                "Notary": canvasmeta["notary"],
                "Persons": canvasmeta["persons"],
                "Locations": canvasmeta["locations"],
                "Amsterdam City Archives id": canvasmeta["identifier"],
            }

            # Getty inventory
            if "getty" in canvasmeta:
                md["Getty Provenance Index id"] = canvasmeta["getty"]["identifier"]
                if canvasmeta["getty"].get("owners"):
                    md["Owners (Getty)"] = canvasmeta["getty"]["owners"]
                if canvasmeta["getty"].get("appraisers"):
                    md["Appraisers (Getty)"] = canvasmeta["getty"]["appraisers"]
                if canvasmeta["getty"].get("comments"):
                    md["Comments (Getty)"] = canvasmeta["getty"]["comments"]

            # Frick inventory
            if "frick" in canvasmeta:
                md["The Frick Collection id"] = (
                    f"<a href={canvasmeta['frick']['url']}>{canvasmeta['frick']['identifier']}</a>"
                )
                if canvasmeta["frick"].get("owners"):
                    md["Owners (Frick)"] = canvasmeta["frick"]["owners"]
                if canvasmeta["frick"].get("appraisers"):
                    md["Appraisers (Frick)"] = canvasmeta["frick"]["appraisers"]
                if canvasmeta["frick"].get("comments"):
                    md["Comments (Frick)"] = canvasmeta["frick"]["comments"]
            for k, v in md.items():
                if v:
                    metadata.append(
                        {
                            "label": {"en": [k]},
                            "value": {"en": [v] if type(v) is str else v},
                        }
                    )

        canvas = getCanvas(
            imagepath,
            annotationpath,
            nameslocations,
            metadata=metadata,
            matcheditems=matcheditems,
            htrobjects=htrobjects,
        )
        items.append(canvas)

    manifest["items"] = items

    return manifest


def getCanvas(
    imagepath: str,
    annotationpath: str = None,
    nameslocations: list = None,
    canvasid: str = None,
    metadata: list = [],
    matcheditems: dict = None,
    htrobjects: list = None,
) -> dict:

    _, filename = os.path.split(imagepath)
    baseFilename, ext = os.path.splitext(filename)

    if canvasid is None:
        canvasid = nsCanvas.term(baseFilename)

    canvas = {
        "id": canvasid,
        "type": "Canvas",
        "label": {"none": [filename]},
        "items": [
            getAnnotationPage(
                target=canvasid, imagepath=imagepath, motivation="painting"
            )
        ],
        "annotations": [],
        "metadata": metadata,
    }

    annotations = []

    # index data
    if nameslocations:

        ap = getAnnotationPage(
            target=canvasid,
            baseFilename=baseFilename,
            motivation="commenting",
            annopageid=f"{GHPREFIX}iiif/annotations/{baseFilename}-index.json",
            nameslocations=nameslocations,
            embedded=False,
        )

        annotations.append(ap)

    # htr data
    if annotationpath:

        ap = getAnnotationPage(
            target=canvasid,
            motivation="supplementing",
            annopageid=f"{GHPREFIX}iiif/annotations/{baseFilename}-htr.json",
            annotationpath=annotationpath,
            matcheditems=matcheditems,
            embedded=False,
        )

        annotations.append(ap)

    # htr objects (via Analiticcl GA)

    if htrobjects:

        ap = getAnnotationPage(
            target=canvasid,
            baseFilename=baseFilename,
            motivation="commenting",
            annopageid=f"{GHPREFIX}iiif/annotations/{baseFilename}-objects.json",
            htrobjects=htrobjects,
            embedded=False,
        )

        annotations.append(ap)

    canvas["annotations"] = annotations

    # These are already calculated in the painting annotation
    canvas["width"] = canvas["items"][0]["items"][0]["body"]["width"]
    canvas["height"] = canvas["items"][0]["items"][0]["body"]["height"]

    return canvas


def getAnnotationPage(
    target: Union[str, URIRef],
    baseFilename: str = None,
    imagepath: str = None,
    motivation: str = "painting",
    annopageid: str = None,
    annotationpath: str = None,
    nameslocations: list = None,
    matcheditems: dict = None,
    htrobjects: list = None,
    embedded: bool = True,
) -> dict:

    if annopageid is None and imagepath:
        _, filename = os.path.split(imagepath)
        baseFilename, _ = os.path.splitext(filename)
        annopageid = nsAnnotationPage.term(baseFilename)
    elif annopageid is None and annotationpath:
        _, filename = os.path.split(annotationpath)
        baseFilename, _ = os.path.splitext(filename)
        annopageid = f"{GHPREFIX}iiif/annotations/{baseFilename}.json"
    elif annotationpath:
        _, filename = os.path.split(annotationpath)
        baseFilename, _ = os.path.splitext(filename)
    elif (
        annotationpath is None
        and imagepath is None
        and nameslocations is None
        and htrobjects is None
    ):
        return {}

    annotationPage = {
        "@context": iiif_prezi3_context,
        "id": annopageid,
        "type": "AnnotationPage",
        "items": [],
    }

    if imagepath:
        annotationPage["items"] = [
            getAnnotation(target, imagepath, motivation=motivation)
        ]

    # This is for the HTR transcriptions
    if annotationpath:
        items = []

        with open(annotationpath) as infile:
            annotations = json.load(infile)

        for region in annotations["PcGts"]["Page"]["elements"]:
            for a in region["elements"]:

                annoMatchId = f"{baseFilename}{a['attributes']['id']}"
                annoid = nsAnno.term(annoMatchId)

                # Getty / Frick data
                matchedItem = matcheditems.get(annoMatchId, {})

                if matchedItem:
                    color = "#11aa09"
                else:
                    color = "#f9b942"

                coordinates = a["geometry"]["coords"]
                if coordinates is None:
                    continue

                targetselector = {
                    "source": target,
                    "selector": {
                        "type": "SvgSelector",
                        "value": getSVG(coordinates, color=color),
                    },
                }

                bodyValue = "\n".join([i["text"] for i in a["elements"]])
                if bodyValue.strip() == "":  # not interested in empty anno
                    continue

                body = []

                # first the text itself (HTR)
                textualBody = {
                    "type": "TextualBody",
                    "language": "nl",
                    "value": "<p><b>HTR</b><br>" + bodyValue + "</p>",
                }
                body.append(textualBody)

                # Getty / Frick items
                if matchedItem:

                    ## Getty
                    matchedItemGetty = matcheditems.get(annoMatchId, {}).get("getty")

                    if matchedItemGetty:

                        properties = {
                            "label": matchedItemGetty["label"],
                            "transcription": matchedItemGetty["transcription"],
                            "type": (
                                'Schilderij [<a href="http://vocab.getty.edu/aat/300177435">AAT</a>]'
                                if matchedItemGetty["type"] == "Schilderij"
                                else matchedItemGetty["type"]
                            ),
                            "artist": matchedItemGetty["artist"],
                            "room": matchedItemGetty["room"],
                            "valuation": matchedItemGetty["valuation"],
                            "subject": matchedItemGetty["subject"],
                            "iconclass": (
                                f'{matchedItemGetty["iconclass"]} [<a href="http://iconclass.org/{matchedItemGetty["iconclass"]}">ICONCLASS</a>]'
                                if {matchedItemGetty["iconclass"]}
                                else None
                            ),
                            "identifier": matchedItemGetty["identifier"],
                        }

                        value = "<br>\n".join(
                            f"<span>{key.title()}: </span>{value}"
                            for key, value in properties.items()
                            if value
                        )

                        textualBody = {
                            "type": "TextualBody",
                            "language": "nl",
                            "value": f"""<p>
                                  <b>Getty Provenance Index</b><br>
                                  {value}
                                </p>""",
                        }
                        body.append(textualBody)

                        ### Then the tags
                        tagBodyType = {
                            "type": "TextualBody",
                            "purpose": "tagging",  # for a nice tag!
                            "value": matchedItemGetty["type"],
                        }
                        body.append(tagBodyType)

                        if matchedItemGetty["iconclass"]:
                            tagBodyIconclass = {
                                "type": "TextualBody",
                                "purpose": "tagging",  # for a nice tag!
                                "value": matchedItemGetty["iconclass"],
                            }
                            body.append(tagBodyIconclass)

                    ## Frick
                    matchedItemFrick = matchedItem.get("frick")
                    if matchedItemFrick:

                        properties = {
                            "label": matchedItemFrick["label"],
                            "transcription": matchedItemFrick["transcription"],
                            "type": matchedItemFrick["type"],
                            "artist": matchedItemFrick["artist"],
                            "room": matchedItemFrick["room"],
                            "valuation": matchedItemFrick["valuation"],
                            "subject": matchedItemFrick["subject"],
                            "iconclass": matchedItemFrick["iconclass"],
                            "identifier": f'<a href="https://research.frick.org/montias/inventoryList/{matchedItemFrick["identifier"].replace(".", "#A", 1)}">{matchedItemFrick["identifier"]}</a>',
                        }

                        value = "<br>\n".join(
                            f"<span>{key.title()}: </span>{value}"
                            for key, value in properties.items()
                            if value
                        )

                        textualBody = {
                            "type": "TextualBody",
                            "language": "nl",
                            "value": f"""<p>
                                  <b>The Frick Collection</b><br>
                                  {value}
                                </p>""",
                        }
                        body.append(textualBody)

                        ### Then the tags
                        tagBodyType = {
                            "type": "TextualBody",
                            "purpose": "tagging",  # for a nice tag!
                            "value": matchedItemFrick["type"],
                        }
                        body.append(tagBodyType)

                        if matchedItemFrick["iconclass"]:
                            tagBodyIconclass = {
                                "type": "TextualBody",
                                "purpose": "tagging",  # for a nice tag!
                                "value": matchedItemFrick["iconclass"],
                            }
                            body.append(tagBodyIconclass)

                anno = getAnnotation(
                    target=targetselector,
                    motivation=motivation,
                    body=body,
                    annoid=annoid,
                )

                items.append(anno)

        annotationPage["items"] = items

    # This is data coming from the index in which Persons and Locations have been tagged
    if nameslocations:
        items = []

        for n, a in enumerate(nameslocations, 1):

            targetselector = {
                "source": target,
                "selector": {
                    "type": "FragmentSelector",
                    "value": f"xywh={a['coords']}",
                },
            }

            properties = {
                "Name": a["label"],
                "URI": f'<a href="{a["id"]}">{a["id"]}</a>',
                "Bredius excerpt": (
                    f'<a href="{a["bredius"][0]}">{a["bredius"][0]} ({a["bredius"][1]})</a>'
                    if a.get("bredius")
                    else None
                ),
            }

            value = "<br>\n".join(
                f"<span>{key.title()}: </span>{value}"
                for key, value in properties.items()
                if value
            )

            body = [
                {
                    "type": "TextualBody",
                    "language": "nl",
                    "value": f"<p><b>Index</b><br>{value}</p>",
                },
                {
                    "type": "TextualBody",
                    "purpose": "tagging",  # for a nice tag!
                    "value": a["type"],
                },
            ]

            anno = getAnnotation(
                target=targetselector,
                motivation=motivation,
                body=body,  # already a list
                annoid=nsAnno.term(f"{baseFilename}/index{n}"),
            )

            items.append(anno)

        annotationPage["items"] = items

    # This is data coming from automatic object detection on the HTR using Analiticcl in the GA project
    if htrobjects:
        items = []

        for n, a in enumerate(htrobjects, 1):

            targetselector = {
                "source": target,
                "selector": {
                    "type": "FragmentSelector",
                    "value": f"xywh={a['coords']}",
                },
            }

            properties = {
                "Original label": a["object_name_original"],
                "Modernized label": a["object_name_modern"],
            }

            value = "<br>\n".join(
                f"<span>{key.title()}: </span>{value}"
                for key, value in properties.items()
                if value
            )

            body = [
                {
                    "type": "TextualBody",
                    "language": "nl",
                    "value": f"<p><b>Object detection</b><br>{value}</p>",
                },
                {
                    "type": "TextualBody",
                    "purpose": "tagging",  # for a nice tag!
                    "value": a["type"],
                },
            ]

            anno = getAnnotation(
                target=targetselector,
                motivation=motivation,
                body=body,  # already a list
                annoid=nsAnno.term(f"{baseFilename}/object{n}"),
            )

            items.append(anno)

        annotationPage["items"] = items

    if embedded:
        return annotationPage
    else:

        with open(annopageid.replace(GHPREFIX, ""), "w") as outfile:
            json.dump(annotationPage, outfile, indent=1)

        return {
            "@context": iiif_prezi3_context,
            "id": annopageid,
            "type": "AnnotationPage",
        }


def getAnnotation(
    target: Union[str, URIRef, dict],
    imagepath: str = None,
    motivation: str = "painting",
    body: list = None,
    annoid: str = None,
) -> dict:

    if motivation == "painting" and imagepath and type(target) is not dict:

        _, filename = os.path.split(imagepath)
        baseFilename, ext = os.path.splitext(filename)

        if annoid is None:
            annoid = nsAnno.term(baseFilename)

        with pil_image.open(imagepath.replace(GHPREFIX, "")) as img:
            (w, h) = img.size
            height = h
            width = w

        # This is the annotation that attaches the image to the canvas
        annotation = {
            "@context": iiif_prezi3_context,
            "id": annoid,
            "type": "Annotation",
            "motivation": motivation,
            "body": {
                "id": imagepath,
                "type": "Image",
                "label": {"en": [filename]},
                "format": "image/jpeg",
                "width": width,
                "height": height,
            },
            "target": target,
        }

    else:
        # But the Annotation type is also used for other commentary etc.
        annotation = {
            "@context": iiif_prezi3_context,
            "id": annoid,
            "type": "Annotation",
            "motivation": motivation,
            "body": body,
            "target": target,
        }

    return annotation


def getSVG(
    coordinates: Union[list, tuple], color: str = "#66cc99", opacity: str = "0.08"
):

    points = "M "  # start at this point
    points += " L ".join(
        [f"{c['x']},{c['y']}" for c in coordinates]
    )  # then move from point to point
    points += f" L {coordinates[0]['x']},{coordinates[0]['y']} Z"  # repeat the first point and close

    svg = etree.Element("svg", xmlns="http://www.w3.org/2000/svg")
    _ = etree.SubElement(
        svg,
        "path",
        **{
            "fill-rule": "evenodd",
            "fill": color,
            "stroke": "#555555",
            "stroke-width": "1",
            "fill-opacity": opacity,
            "d": points,
        },
    )

    return etree.tostring(svg, encoding=str)


if __name__ == "__main__":
    main(
        imagefolder="images/2408/",
        annotationfolder="data/htr/2408/",
        nameslocationsfile="data/2408_nameslocations.json",
        canvasmetadatafile="data/2408_canvasmetadata.json",
        matcheditemsfile="data/2408_itemsmetadata.json",
        htrobjectsfile="data/2408_objectshtr.json",
    )
