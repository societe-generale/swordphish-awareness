from LocalUsers.models import Entity, Region


def get_user_entities(user):
    entities = []
    if user is not None:
        entities = Entity.objects.filter(admins__username=user.username)
    return entities


def get_user_regions(user):
    regions = []
    if user is not None:
        regions = Region.objects.filter(members__username=user.username)
        entities = get_user_entities(user)

        for entity in entities:
            subregions = Region.objects.filter(entity_name=entity.name)
            for region in subregions:
                if region not in regions:
                    regions.add(region)

    return regions
