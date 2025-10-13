from django.test import SimpleTestCase, RequestFactory

from main.qr_utils import (
    get_device_url_qr, get_device_info_qr,
    get_part_url_qr, get_part_info_qr,
)


class _DummyItem:
    def __init__(self, part_name: str, serial: str):
        class _Part:
            def __init__(self, name):
                self.name = name
        self.part = _Part(part_name)
        self.serial = serial


class _DummyInstances:
    def __init__(self, items):
        self._items = list(items)

    def all(self):
        return self

    def exists(self):
        return len(self._items) > 0

    def __iter__(self):
        return iter(self._items)


class _DummyDevice:
    def __init__(self, name: str, serial: str, desc: str, items, id: int = 1):
        self.id = id
        self.name = name
        self.serial = serial
        self.desc = desc
        self.part_instances = _DummyInstances(items)


class _DummyType:
    def __init__(self, name: str):
        self.name = name


class _DummyPartInstances:
    def __init__(self, count: int):
        self._count = count

    def count(self):
        return self._count


class _DummyPart:
    def __init__(self, name: str, decimal_num: str, type_name: str, parent_name: str | None, instances_count: int, desc: str | None):
        self.name = name
        self.decimal_num = decimal_num
        self.type = _DummyType(type_name)
        self.parent = type('P', (), {'name': parent_name}) if parent_name else None
        self.instances = _DummyPartInstances(instances_count)
        self.desc = desc


class TestQRUtilsLegacy(SimpleTestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def _req(self):
        return self.rf.get('/', HTTP_HOST='testserver')

    def test_get_device_url_qr(self):
        dummy = _DummyDevice('Dev', 'SN-1', 'desc', [])
        data_url = get_device_url_qr(dummy, self._req())
        self.assertIsInstance(data_url, str)
        self.assertTrue(data_url.startswith('data:image/png;base64,'))

    def test_get_device_info_qr_with_items(self):
        items = [_DummyItem('PartA', 'S1'), _DummyItem('PartB', 'S2')]
        dummy = _DummyDevice('Dev', 'SN-1', 'desc', items)
        data_url = get_device_info_qr(dummy)
        self.assertIsInstance(data_url, str)
        self.assertTrue(data_url.startswith('data:image/png;base64,'))

    def test_get_part_url_qr(self):
        dummy_part = type('P', (), {'id': 123})
        data_url = get_part_url_qr(dummy_part, self._req())
        self.assertIsInstance(data_url, str)
        self.assertTrue(data_url.startswith('data:image/png;base64,'))

    def test_get_part_info_qr_with_parent(self):
        part = _DummyPart(name='Node', decimal_num='1.2.3', type_name='TypeX', parent_name='Parent', instances_count=0, desc='')
        data_url = get_part_info_qr(part)
        self.assertIsInstance(data_url, str)
        self.assertTrue(data_url.startswith('data:image/png;base64,'))
