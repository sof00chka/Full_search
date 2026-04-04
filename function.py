def show_obj(toponym):
    # Долгота и широта:
    toponym_coodrinates = toponym["Point"]["pos"].split(" ")
    # Масштаб(spn)
    toponym_envelop = toponym["boundedBy"]["Envelope"]
    toponym_l = list(map(float, toponym_envelop["lowerCorner"].split()))
    toponym_u = list(map(float, toponym_envelop["upperCorner"].split()))
    toponym_spn = [str(toponym_u[0] - toponym_l[0]), str(toponym_u[1] - toponym_l[1])]
    return toponym_coodrinates, toponym_spn

def calculate_distance(lon1, lat1, lon2, lat2):
    dx = (lon2 - lon1) * 111
    dy = (lat2 - lat1) * 111
    return (dx ** 2 + dy ** 2) ** 0.5


def get_pharmacy_color(work_hours):
    if not work_hours:
        return "gr"
    work_hours_lower = work_hours.lower()
    if "круглосуточно" in work_hours_lower or "24" in work_hours_lower or "сутки" in work_hours_lower:
        return "gn"
    else:
        return "bl"