from lxml import etree
import os

if(not(os.path.exists("../build/"))):
    os.mkdir("../build")

jmdict = etree.parse("../sources/jmdict/JMdict.xml")


print("done")