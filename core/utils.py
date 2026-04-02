import os
import re
import json
from shutil import copyfile
from django.conf import settings


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_ft():
    from feeding.models import FeedingType
    return FeedingType.objects.all()


def get_ht():
    from history.models import HistoryType
    return HistoryType.objects.all()


def get_htt():
    from terrariums.models import TerrariumHistoryType
    return TerrariumHistoryType.objects.all()


def get_at():
    from animals.models import AnimalType
    return AnimalType.objects.all()


def get_tt():
    from terrariums.models import TerrariumType
    return TerrariumType.objects.all()


def get_setting(name=None):
    from app_settings.models import AppSetting
    if name is None:
        result = {}
        for s in AppSetting.objects.all():
            result[s.setting] = [s.value, s.name, s.description]
        return result
    else:
        try:
            return AppSetting.objects.get(setting=name).value
        except AppSetting.DoesNotExist:
            return None


def get_fsize(animal_type, weight_text):
    try:
        weight_number = float(weight_text.split(' ')[0].replace(',', '.'))
        feeding_size = ""
        setting_feeding_size = json.loads(get_setting("feeding_size") or '[]')
        if str(animal_type.id) in setting_feeding_size:
            if weight_number > 0:
                feed_min = float(animal_type.f_max) / 100 * weight_number
                feed_max = float(animal_type.f_min) / 100 * weight_number
                feeding_size = (
                    f"Currently a feeding size between {feed_min:.0f} gr "
                    f"and {feed_max:.0f} gr "
                    f"({animal_type.f_min}% -> {animal_type.f_max}%) is recommended!"
                )
    except Exception:
        feeding_size = ""
    return feeding_size


def _parse_weight(text):
    """Extract numeric value and unit from a weight string like '890', '940g', '586 gr'."""
    text = text.strip()
    m = re.match(r'^([0-9]+(?:[.,][0-9]+)?)\s*([a-zA-Z]*)', text)
    if not m:
        return None, ''
    value = float(m.group(1).replace(',', '.'))
    unit = m.group(2).strip()
    return value, unit


def get_weight_chart(animal_id):
    from history.models import History
    weight_setting = get_setting("weight_type")
    weight_list = []
    try:
        animal_weights = (
            History.objects
            .filter(event_id=weight_setting, animal_id=animal_id)
            .order_by('date')
        )
        for w in animal_weights:
            value, unit = _parse_weight(w.text or '')
            if value is None:
                continue
            weight_list.append({
                'weight': value,
                'weight_unit': unit,
                'date': w.date,
            })
    except Exception:
        weight_list = []
    return weight_list


def _build_animal_dict(animal, animal_type, weight_setting):
    from history.models import History
    try:
        current_weight = (
            History.objects
            .filter(event_id=weight_setting, animal=animal)
            .order_by('-date')
            .values_list('text', flat=True)
            .first()
        ) or "0"
    except Exception:
        current_weight = "0"

    weight_value, weight_unit = _parse_weight(current_weight)

    if animal_type:
        art_name = animal_type.name
        art_id = animal_type.id
        f_min = animal_type.f_min
        f_max = animal_type.f_max
        feeding_size = get_fsize(animal_type, current_weight)
    else:
        art_name = ''
        art_id = None
        f_min = 0
        f_max = 0
        feeding_size = ''

    return {
        'id': animal.id,
        'name': animal.name,
        'art': art_name,
        'art_id': art_id,
        'morph': animal.morph,
        'gender': animal.gender,
        'birth': animal.birth,
        'notes': animal.notes,
        'image': animal.image,
        'background_color': animal.background_color,
        'f_min': f_min,
        'f_max': f_max,
        'default_ft': animal.default_ft_id,
        'terrarium': animal.terrarium_id,
        'updated_date': animal.updated_date,
        'current_weight': current_weight,
        'current_weight_value': weight_value or 0,
        'current_weight_unit': weight_unit or 'g',
        'feeding_size': feeding_size,
    }


def get_ad(id=None, terrarium=None):
    from animals.models import Animal, AnimalType
    weight_setting = get_setting("weight_type")

    if id:
        animal = Animal.objects.select_related('art').get(pk=id)
        return _build_animal_dict(animal, animal.art, weight_setting)
    elif terrarium:
        animals = Animal.objects.select_related('art').filter(terrarium_id=terrarium)
        return [_build_animal_dict(a, a.art, weight_setting) for a in animals]
    else:
        animals = Animal.objects.select_related('art').all()
        return [_build_animal_dict(a, a.art, weight_setting) for a in animals]


def get_fd(id=None, animal_id=None, limit=None):
    from feeding.models import Feeding
    if id:
        f = Feeding.objects.select_related('feeding_type').get(pk=id)
        return {
            'id': f.id,
            'animal': f.animal_id,
            'type': f.feeding_type.name,
            'ftunit': f.feeding_type.unit,
            'detail': f.feeding_type.detail,
            'count': f.count,
            'unit': f.unit,
            'date': f.date,
        }
    else:
        qs = (
            Feeding.objects
            .select_related('feeding_type')
            .filter(animal_id=animal_id)
            .order_by('-date')
        )
        if limit:
            qs = qs[:limit]
        return [
            {
                'id': f.id,
                'animal': f.animal_id,
                'type': f.feeding_type.name,
                'ftunit': f.feeding_type.unit,
                'detail': f.feeding_type.detail,
                'count': f.count,
                'unit': f.unit,
                'date': f.date,
            }
            for f in qs
        ]


def get_hd(id=None, animal_id=None, limit=None, e_type=None):
    from history.models import History
    if id:
        h = History.objects.select_related('event').get(pk=id)
        return {
            'id': h.id,
            'animal': h.animal_id,
            'name': h.event.name,
            'eventType': h.event_id,
            'text': h.text,
            'date': h.date,
        }
    else:
        qs = History.objects.select_related('event').filter(animal_id=animal_id)
        if e_type:
            qs = qs.filter(event_id=e_type)
        qs = qs.order_by('-date')
        if limit:
            qs = qs[:limit]
        return [
            {
                'id': h.id,
                'animal': h.animal_id,
                'name': h.event.name,
                'eventType': h.event_id,
                'text': h.text,
                'date': h.date,
            }
            for h in qs
        ]


def get_thd(id=None, terrarium_id=None, limit=None):
    from terrariums.models import TerrariumHistory
    if id:
        th = TerrariumHistory.objects.select_related('event').get(pk=id)
        return {
            'id': th.id,
            'terrarium': th.terrarium_id,
            'name': th.event.name,
            'text': th.text,
            'date': th.date,
        }
    else:
        qs = (
            TerrariumHistory.objects
            .select_related('event')
            .filter(terrarium_id=terrarium_id)
            .order_by('-date')
        )
        if limit:
            qs = qs[:limit]
        return [
            {
                'id': th.id,
                'terrarium': th.terrarium_id,
                'name': th.event.name,
                'text': th.text,
                'date': th.date,
            }
            for th in qs
        ]


def get_tr(id=None):
    from terrariums.models import Terrarium
    if id:
        t = Terrarium.objects.select_related('terrarium_type').get(pk=id)
        return {
            'id': t.id,
            'name': t.name,
            'size': t.size,
            'type_id': t.terrarium_type_id,
            'type': t.terrarium_type.name,
            'notes': t.notes,
            'image': t.image,
        }
    else:
        terrariums = Terrarium.objects.select_related('terrarium_type').all()
        return [
            {
                'id': t.id,
                'name': t.name,
                'size': t.size,
                'type_id': t.terrarium_type_id,
                'type': t.terrarium_type.name,
                'notes': t.notes,
                'image': t.image,
            }
            for t in terrariums
        ]


def get_te(id=None, terrarium_id=None):
    from terrariums.models import TerrariumEquipment
    if id:
        return TerrariumEquipment.objects.filter(terrarium_id=terrarium_id).first()
    else:
        return (
            TerrariumEquipment.objects
            .filter(terrarium_id=terrarium_id)
            .order_by('name', 'text')
        )


def get_tl(id=None, terrarium_id=None):
    from terrariums.models import TerrariumLamps
    if id:
        return TerrariumLamps.objects.filter(terrarium_id=terrarium_id).first()
    else:
        return (
            TerrariumLamps.objects
            .filter(terrarium_id=terrarium_id)
            .order_by('lamp_type', 'watt')
        )


def get_docs(target, id):
    from documents.models import Document
    if target == 'animal':
        return Document.objects.filter(animal_id=id)
    elif target == 'terrarium':
        return Document.objects.filter(terrarium_id=id)


def insert_defaults():
    from animals.models import AnimalType
    from feeding.models import FeedingType
    from history.models import HistoryType
    from terrariums.models import TerrariumType, TerrariumHistoryType
    from app_settings.models import AppSetting

    if not AnimalType.objects.exists():
        AnimalType.objects.create(name='Ball Python', f_min=10, f_max=20)
        AnimalType.objects.create(name='Leopard Gecko', f_min=0, f_max=0)

    if not FeedingType.objects.exists():
        for name, unit, detail in [
            ('Elephant', 'weight', 't'),
            ('Toddler', 'text', 'BMI'),
            ('Mouse', 'weight', 'gr'),
            ('Rat', 'weight', 'gr'),
            ('Whale', 'weight', 't'),
            ('Grasshopper', 'size', 'small,medium,sub,adult'),
        ]:
            FeedingType.objects.create(name=name, unit=unit, detail=detail)

    if not HistoryType.objects.exists():
        for name in ['Shed', 'Weighed', 'Medical', 'Miscellaneous']:
            HistoryType.objects.create(name=name)

    if not AppSetting.objects.exists():
        AppSetting.objects.create(setting='weight_type', value='2', name='Weight Option',
            description='Last entry will be shown as weight on the animal page!')
        AppSetting.objects.create(setting='feeding_size', value='["1"]', name='Feeding Size',
            description='Show feeding size for animal type!')
        AppSetting.objects.create(setting='color_female', value='#e481e4', name='Female Color',
            description='Color for female animals!')
        AppSetting.objects.create(setting='color_male', value='#89cff0', name='Male Color',
            description='Color for male animals!')
        AppSetting.objects.create(setting='color_other', value='#29a039', name='Other Color',
            description='Color for other animals!')

    if not TerrariumType.objects.exists():
        TerrariumType.objects.create(name='Tropical')
        TerrariumType.objects.create(name='Desert')

    if not TerrariumHistoryType.objects.exists():
        for name in ['Cleaning', 'Maintenance']:
            TerrariumHistoryType.objects.create(name=name)


def create_folders():
    upload_folder = settings.MEDIA_ROOT
    logs_folder = settings.BASE_DIR / 'data' / 'logs'

    for folder in [
        upload_folder,
        logs_folder,
        upload_folder / 'terrariums',
        upload_folder / 'animals',
        upload_folder / 'documents',
    ]:
        os.makedirs(folder, exist_ok=True)

    dummy_animal = upload_folder / 'animals' / 'dummy.jpg'
    if not dummy_animal.exists():
        copyfile(str(settings.BASE_DIR / 'static' / 'images' / 'dummy.jpg'), str(dummy_animal))

    dummy_terrarium = upload_folder / 'terrariums' / 'dummy.jpg'
    if not dummy_terrarium.exists():
        copyfile(str(settings.BASE_DIR / 'static' / 'images' / 'dummy_big.jpg'), str(dummy_terrarium))
