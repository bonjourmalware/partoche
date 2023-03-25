import json
from uuid import uuid4
from geoip2.errors import AddressNotFoundError
from src.runners.Base import Base


class MelodyRunner(Base):
    def __init__(self, local_data_path=""):
        super(MelodyRunner, self).__init__(local_data_path)

    def get_fresh_data(self):
        counter = 0
        data = []

        for line in self.local_data_file:
            loaded = json.loads(line)
            loaded["_id"] = uuid4()
            loaded["geoip"] = {}
            try:
                geodata = self.geoip_city_reader.city(loaded["src_ip"])
                loaded["geoip"]["country_name"] = geodata.country.name
                loaded["geoip"]["city_name"] = geodata.city.name
                loaded["geoip"]["country_code3"] = geodata.country.iso_code
                loaded["geoip"]["latitude"] = geodata.location.latitude
                loaded["geoip"]["longitude"] = geodata.location.longitude
            except AddressNotFoundError:
                pass

            try:
                asn_data = self.geoip_asn_reader.asn(loaded["src_ip"])
                loaded["geoip"]["asn"] = asn_data.autonomous_system_number
                loaded["geoip"]["as_org"] = asn_data.autonomous_system_organization
            except AddressNotFoundError:
                pass

            data.append(loaded)
            counter += 1
            if counter == self.local_chunk_size:
                break

        if counter < self.local_chunk_size:
            # EOF
            self.local_data_file.seek(0)

        return data
