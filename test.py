stringname = "aadhfdas fahsdfhasdf adhf (2010) [123123]"
print(stringname.__contains__("["))
stringname = stringname.split("(")[1].replace(")", "").split("[")[1].replace("]", "")
print(stringname + 'a')