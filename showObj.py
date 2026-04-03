def show_obj(toponym):
    # Долгота и широта:
    toponym_coodrinates = toponym["Point"]["pos"].split(" ")
    # Масштаб(spn)
    toponym_envelop = toponym["boundedBy"]["Envelope"]
    toponym_l = list(map(float, toponym_envelop["lowerCorner"].split()))
    toponym_u = list(map(float, toponym_envelop["upperCorner"].split()))
    toponym_spn = [str(toponym_u[0] - toponym_l[0]), str(toponym_u[1] - toponym_l[1])]
    return toponym_coodrinates, toponym_spn