from datetime import datetime
import os
from os.path import join, splitext, exists
import re
import json
from shutil import move
from tempfile import NamedTemporaryFile
import time
from urllib import urlencode
from urlparse import urljoin

from PIL import Image, ImageChops
import magic
import mimetypes
import requests
import dateutil.parser

import hashlib
try:
    import redis
    HAS_REDIS = True
    r = redis.Redis()
except ImportError:
    HAS_REDIS = False


def get_file_md5sum(filename):
    with open(filename, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def image_uploaded_already(api_collection, object_id, image_filename):
    person_data = api_collection(object_id).get()['result']
    md5sum = get_file_md5sum(image_filename)
    for image in person_data.get('images', []):
        if image.get('notes') == 'md5sum:' + md5sum:
            return True
        elif image.get('md5sum') == md5sum:
            return True
    return False

emblem_directory = 'all_images'
base_emblem_url = 'http://search.electoralcommission.org.uk/Api/Registrations/Emblems/'

class Parser():
    def run(self):
        self.mime_type_magic = magic.Magic(mime=True)
        start = 0
        per_page = 50
        url = 'http://pefonline.electoralcommission.org.uk/api/search/Registrations'
        params = {
            'rows': per_page,
            'et': ["pp", "ppm", "tp", "perpar", "rd"],
            'register': ["gb", "ni", "none"],
            'regStatus': ["registered", "deregistered", "lapsed"],
        }
        total = None
        while total is None or start <= total:
            ntf = NamedTemporaryFile(delete=False)
            params['start'] = start
            print start
            try:
                resp = requests.get(url + '?' + urlencode(params, doseq=True)).json()
                if total is None:
                    total = resp['Total']
                with open(ntf.name, 'w') as f:
                    json.dump(resp['Result'], f)
                self.parse_data(ntf.name)
            finally:
                os.remove(ntf.name)
            start += per_page

        all_data = []
        for filename in os.listdir('parsed'):
            if not filename.endswith('.json'):
                continue
            with open(join('parsed', filename), 'r') as f:
                all_data.append(json.load(f))

        with open('all_data.json', 'w') as f:
            f.write(json.dumps(all_data, indent=4))

    def get_descriptions(self, party):
        if not party['PartyDescriptions']:
            return []
        return [
            {'description': d['Description'],
             'translation': d['Translation'] if d['Translation'] else ""}
            for d in party['PartyDescriptions']
        ]

    def fielding_in(self, ec_party):
        areas = ["England", "Scotland", "Wales"]
        return [area for area in areas if ec_party["FieldingCandidatesIn{}".format(area)]]

    def get_officers(self, officer_list):
        officers = {
            'party_leader': 'None',
            'nominating_officer': 'None',
            'campaigns_officer': 'None',
            'treasurer': 'None',
            'other_officers': [],
        }
        for x in officer_list:
            if x['Role'] == 'Leader':
                officers['party_leader'] = x['Name']
            elif x['Role'] == 'Nominating Officer':
                officers['nominating_officer'] = x['Name']
            elif x['Role'] == 'Campaigns Officer':
                officers['campaigns_officer'] = x['Name']
            elif x['Role'] == 'Treasurer':
                officers['treasurer'] = x['Name']
            else:
                officers['other_officers'].append({
                    'name': x['Name'],
                    'deputy_additional_officer': x['Role'] == 'Deputy Additional Officer',
                    'deputy_treasurer': x['Role'] == 'Deputy Treasurer',
                    'deputy_nominating_officer': x['Role'] == 'Deputy Nominating Officer',
                    'deputy_campaigns_officer': x['Role'] == 'Deputy Campaigns Officer',
                })
        return officers

    def get_address(self, ec_party):
        address_parts = ['Line1', 'Line2', 'Line3', 'Line4', 'Town', 'County', 'Postcode', 'Country']
        address = [ec_party[x] for x in address_parts if ec_party[x]]
        return '\r\n'.join(address) + '\r\n'

    def format_year_end(self, date):
        if date:
            return datetime.strptime(date, "%d/%m").strftime("%d/%m")

    def parse_data(self, json_file):
        with open(json_file) as f:
            for ec_party in json.load(f):
                ec_party_id = ec_party['ECRef'].strip()
                if ec_party['RegulatedEntityTypeName'] == 'Minor Party':
                    register = ec_party['RegisterNameMinorParty'].replace(
                        ' (minor party)', ''
                    )
                else:
                    register = ec_party['RegisterName']

                parsed_filename = join('parsed', '{}.json'.format(ec_party_id))
                address = self.get_address(ec_party)
                if exists(parsed_filename):
                    with open(parsed_filename) as c:
                        j = json.load(c)
                    geometry = j.get('geometry')
                    end_date = j.get('end_date')
                else:
                    geometry = self.geocode(address, ec_party['Postcode'])
                    end_date = None
                party_name, deregistered_date = self.clean_name(ec_party['RegulatedEntityName'])
                emblems = self.upload_images(ec_party['PartyEmblems'])
                registered_date = self.clean_date(ec_party['ApprovedDate'])
                officers = self.get_officers(ec_party['Officers'])
                party_data = {
                    'fielding_in': self.fielding_in(ec_party),
                    "other_officers": officers['other_officers'],
                    "campaigns_officer": officers.get('campaigns_officer'),
                    'registered_date': registered_date,
                    "postcode": ec_party['Postcode'],
                    "party_leader": officers.get('party_leader'),
                    "nominating_officer": officers.get('nominating_officer'),
                    'emblems': emblems,
                    "party_address": address,
                    "email": "",
                    "gibraltar_party": ec_party['IsGibraltarParty'],
                    "financial_year_end": self.format_year_end(ec_party['FinancialYearEnd']),
                    "status": ec_party['RegulatedEntityStatusName'],
                    "fax": "",
                    'end_date': end_date,
                    "phone_extension": "",
                    "phone": "",
                    "treasurer": officers.get('treasurer'),
                    'party_id': ec_party_id,
                    "accounting_units": {
                        "exempt_from_parliamentary_election_returns": ec_party['ExemptFromParliamentaryElectionReturns'],
                        "exempt_from_quarterly_transaction_returns": ec_party['ExemptFromQuarterlyTransactionReturns'],
                        "exempt_from_quarterly_donation_returns": ec_party['ExemptFromQuarterlyDonationReturns'],
                    },
                    "geometry": geometry,
                    'register': register,
                    'party_name': party_name,
                    "alternative_names": [
                        ec_party["RegulatedEntityAlternateName"] if ec_party["RegulatedEntityAlternateName"] else ""
                    ],
                    'descriptions': self.get_descriptions(ec_party),
                }

                if deregistered_date:
                    party_data['deregistered_date'] = deregistered_date

                with open(join('parsed', '{}.json'.format(ec_party_id)), 'w') as o:
                    json.dump(party_data, o, indent=4)

    def clean_date(self, date):
        timestamp = re.match(
            r'\/Date\((\d+)\)\/', date).group(1)
        dt = datetime.fromtimestamp(int(timestamp) / 1000.)
        return dt.isoformat()

    def clean_name(self, name):
        name = name.strip()
        if 'de-registered' not in name.lower():
            return name, None

        match = re.match(
            r'(.+)\[De-registered ([0-9]+/[0-9]+/[0-9]+)\]', name)
        name, deregistered_date = match.groups()
        name = re.sub(r'\([Dd]e-?registered [^\)]+\)', '', name)
        deregistered_date = dateutil.parser.parse(
            deregistered_date, dayfirst=True).isoformat()

        return name.strip(), deregistered_date

    def upload_images(self, emblems):
        all_emblems = []
        if not emblems:
            return all_emblems
        for emblem in emblems:
            emblem_id = str(emblem['Id'])
            ntf = NamedTemporaryFile(delete=False)
            image_url = urljoin(base_emblem_url, emblem_id)
            r = requests.get(image_url)
            with open(ntf.name, 'w') as f:
                f.write(r.content)
            mime_type = self.mime_type_magic.from_file(ntf.name)
            extension = mimetypes.guess_extension(mime_type)
            if extension == ".jpe":
                extension = ".jpg"
            fname = 'Emblem_{0}{1}'.format(emblem_id, extension)
            all_emblems.append({
                'image': fname,
                'primary': False,
                'id': str(emblem['Id']),
                'description': emblem['MonochromeDescription'],
            })
            fpath = join(emblem_directory, fname)
            move(ntf.name, fpath)
            self.trim_logo(fpath)
        return all_emblems

    def geocode(self, address, postcode):
        geometry = {"type": "Point",}
        if HAS_REDIS:
            coordinates = r.get(postcode)
            if coordinates:
                geometry['coordinates']= json.loads(coordinates)
                return geometry

        time.sleep(0.5)

        url = "http://mapit.mysociety.org/postcode/{0}".format(postcode)

        try:
            req = requests.get(url)
            req_json = req.json()
            coordinates = [req_json['wgs84_lon'], req_json['wgs84_lat']]
        except (KeyError, ValueError):
            print "MaPit failed, trying google"

            try:
                google_url = \
                    "https://maps.googleapis.com/maps/api/geocode/json?address="
                address = " ".join(address.splitlines())
                req = requests.get(google_url + address)
                req_json = req.json()
                location = req_json['results'][0]['geometry']['location']
                coordinates = [location['lng'], location['lat']]
            except:
                # Just give up!
                pass
            print req.text

        if HAS_REDIS:
            r.set(postcode, json.dumps(coordinates))
        coordinates = None
        geometry['coordinates'] = coordinates
        return geometry

    def trim_logo(self, path):
        """
        With thanks to this SO post:
        http://stackoverflow.com/questions/10615901/trim-whitespace-using-pil
        """
        try:
            im = Image.open(path)
        except IOError:
            # Sometimes the images don't exist.  Just return in that case
            return
        im = im.convert('RGB')
        # Don't get 0,0, as some have a black border
        bg = Image.new(im.mode, im.size, im.getpixel((5,5)))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 1.0, -100)
        bbox = diff.getbbox()
        if bbox:
            new_im = im.crop(bbox)
            new_im.save(path)

Parser().run()
