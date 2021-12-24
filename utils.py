# -*- encoding: utf-8 -*-
'''
@File    :   utils.py
@Time    :   2021/12/24 12:57:05
@Author  :   Mingyu Li
@Version :   1.0
@Contact :   lmytime@hotmail.com
'''


def download_aptx(id, outdir="."):
    """Download JWST proposal .aptx file from stsci website

    Parameters
    ----------
    id : int
        The proposal id
    outdir : str, optional
        Output directory to save downloaded .aptx file
        (default is curren directory .)

    Returns
    -------
    bool
        return True if download fine, else return False
    """
    from pathlib import Path
    import requests
    url = f"https://www.stsci.edu/jwst/phase2-public/{id}.aptx"
    outpath = Path(outdir, f"{id}.aptx")
    r = requests.get(url=url, allow_redirects=True)
    if(not r.content.decode("utf-8", "ignore").startswith("<!DOCTYPE HTML")):
        with open(outpath, "wb") as f:
            f.write(r.content)
            print(f"OK {id}.aptx")
            return True
    else:
        print(f"NO {id}.aptx")
        return False


def extract_aptx(inpfile, outdir="."):
    """Extract JWST proposal .aptx file

    Parameters
    ----------
    inpfile : str
        The path of proposal .aptx file
    outdir : str, optional
        Output directory to save extracted files
        (default is curren directory .)
    """
    from pathlib import Path
    from zipfile import ZipFile
    filename = Path(inpfile).name[:-len("".join(Path(inpfile).suffixes))]
    with ZipFile(Path(inpfile), "r") as zipObj:
        zipObj.extractall(Path(outdir, filename))


class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    ''' Read .xml file as dict

    Example usage:

    >>> from xml.etree import cElementTree as ElementTree
    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> from xml.etree import cElementTree as ElementTree
    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})


if __name__ == "__main__":
    '''
    Here are some examples.
    '''
    from xml.etree import cElementTree as ElementTree
    import json

    id = 1435

    download_aptx(id=id, outdir=".")

    extract_aptx(inpfile=f"{id}.aptx", outdir=".")

    tree = ElementTree.parse(f"{id}/{id}.xml")
    root = tree.getroot()
    xmldict = XmlDictConfig(root)

    with open(f"{id}.json", "w") as outfile:
        json.dump(xmldict, outfile, indent=4)
