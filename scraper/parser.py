import os
import json
import re
import glob

from bs4 import BeautifulSoup
from dateutil.parser import parse
import requests
try:
    import redis
    HAS_REDIS = True
    r = redis.Redis()
except ImportError:
    HAS_REDIS = False

class PartyParser(dict):
    def __init__(self, party_id):
        self['party_id']= party_id
        self.folder_name = os.path.abspath(os.path.join('raw_data', party_id))
        self.details_soup = BeautifulSoup(open(os.path.join(
            self.folder_name, "results_page.html"
        )))
        self.parse_details()


    def _text_from_id(self, el_id, find_all=False, soup=None, checkbox=False):
        if not soup:
            soup = self.details_soup
        if find_all:
            return [r.get_text() for r in soup.findAll(
                id=el_id)]

        el = soup.find(id=el_id)
        if not el:
            return None
        if checkbox:
            return "checked" in el.attrs

        text = el.get_text()
        if text == "No":
            return False
        if text == "Yes":
            return True
        return text

    def clean_party_name(self, name):
        if not 'de-registered' in name.lower():
            return (None, name)

        # Pensioners Party [De-registered 05/11/13]
        match = re.match(r'([^\[]+)\[De-registered ([0-9]+/[0-9]+/[0-9]+)\]', name)
        name, date = match.groups()
        return name.strip(), parse(date).isoformat()

    def parse_details(self):
        self['party_name'] = self._text_from_id(
            'ctl00_ContentPlaceHolder1_ProfileControl1_lblPrimaryNameValue')

        if 'De-registered' in self['party_name']:
            party_name, deregistered_date = self.clean_party_name(
                self['party_name'])
            self['party_name'] = party_name
            self['deregistered_date'] = deregistered_date

        self['alternative_names'] = self._text_from_id(
            'ctl00_ContentPlaceHolder1_ProfileControl1_lblAlternativeNameValue',
            find_all=True
            )

        self['register'] = self._text_from_id(
            "ctl00_ContentPlaceHolder1_ProfileControl1_lblRegisterValue")

        self['status'] = self._text_from_id(
            "ctl00_ContentPlaceHolder1_ProfileControl1_luStatus")

        registered_date = self._text_from_id(
            "ctl00_ContentPlaceHolder1_ProfileControl1_lblRegistrationDateValue")

        self['registered_date'] = parse(registered_date).isoformat()
        end_date = self._text_from_id(
                    re.compile("EffectiveEndDateValue"))
        if end_date:
            self['end_date'] = parse(end_date).isoformat()
        else:
            self['end_date'] = None

        self['financial_year_end'] = self._text_from_id(
            "ctl00_ContentPlaceHolder1_ProfileControl1_lblFinancialYearEndValue")

        self['party_address'] = self.details_soup.find(
            id='ctl00_ContentPlaceHolder1_ProfileControl1_lblAddress'
               '').find_next('td').get_text()

        if self['party_address']:
            # This is a bit rough, but it turns out it works
            self['postcode'] = self['party_address'].splitlines()[-2]

        if 'postcode' in self:
            self['geometry'] = self.geocode()

        self['email'] = self._text_from_id(
            "ctl00_ContentPlaceHolder1_ProfileControl1_lblEmailAddressValue")

        self['phone'] = self._text_from_id(
            "ctl00_ContentPlaceHolder1_ProfileControl1_lblPhoneNumberValue")

        self['phone_extension'] = self._text_from_id(
            "ctl00_ContentPlaceHolder1_ProfileControl1_lblTelephoneExtensionValue")

        self['fax'] = self._text_from_id(
            "ctl00_ContentPlaceHolder1_ProfileControl1_lblFaxNumberValue")

        self['party_leader'] = self._text_from_id(
            "ctl00_ContentPlaceHolder1_ProfileControl1_lblPartyLeaderValue")

        self['nominating_officer'] = self._text_from_id(
        "ctl00_ContentPlaceHolder1_ProfileControl1_lblNominatingOfficerValue")

        self['treasurer'] = self._text_from_id(
            "ctl00_ContentPlaceHolder1_ProfileControl1_lblTreasurerValue")

        self['campaigns_officer'] = self._text_from_id(
            "ctl00_ContentPlaceHolder1_ProfileControl1_lblCampaignsOfficerValue")

        self['other_officers'] = []
        others_table = self.details_soup.find(
            id="ctl00_ContentPlaceHolder1_ProfileControl1_gvAdditionalOfficers")
        if others_table:
            for row in others_table.findAll('tr')[1:]:
                officer = {}
                officer['name'] = self._text_from_id(re.compile("DisplayName"),
                                                     soup=row)

                officer['deputy_additional_officer'] = self._text_from_id(
                    re.compile("AdditionalOfficer"),
                    soup=row,
                    checkbox=True)

                officer['deputy_treasurer'] = self._text_from_id(
                    re.compile("IsDeputyTreasurer"), soup=row, checkbox=True)

                officer['deputy_nominating_officer'] = self._text_from_id(
                    re.compile("DeputyNominatingOfficer"),
                    soup=row,
                    checkbox=True)

                officer['deputy_campaigns_officer'] = self._text_from_id(
                    re.compile("CampaignsOfficer"), soup=row, checkbox=True)

                self['other_officers'].append(officer)

        self['fielding_in'] = []
        if self._text_from_id(
                re.compile("FieldingCandidatesInEngland")) == "Yes":
            self['fielding_in'].append("England")

        if self._text_from_id(
                re.compile("FieldingCandidatesInScotland")) == "Yes":
            self['fielding_in'].append("Scotland")

        if self._text_from_id(
                re.compile("FieldingCandidatesInWales")) == "Yes":
            self['fielding_in'].append("Wales")

        # The combined region is the South West of England, which for the
        # purposes of European Parliamentary elections includes Gibraltar.
        # https://pefonline.electoralcommission.org.uk/Help.aspx?pi=83
        if self._text_from_id(
                re.compile("FieldingCandidatesInCombinedRegion")) == "Yes":
            self['fielding_in'].append("Combined Region")

        if self._text_from_id(re.compile(
                    "IsAGibraltarPartyValue")) == "Yes":
            self['gibraltar_party'] = True
        else:
            self['gibraltar_party'] = False

        self['emblems'] = []
        for link in self.details_soup.findAll(id=re.compile('lnkEmblemId')):
            e_id = link.get_text()
            emblem = {
                'id': e_id,
                'description': link.find_next('td').get_text(),
                'image': self.emblem_dict[e_id]
            }
            self['emblems'].append(emblem)

        self['descriptions'] = []

        descriptions_table = self.details_soup.find(
            id='ctl00_ContentPlaceHolder1_ProfileControl1_gvDescriptions')
        if descriptions_table:
            for row in descriptions_table.findAll('tr')[1:]:
                cells = row.findAll('td')
                description = {
                    'description': cells[0].get_text(),
                    'translation': cells[1].get_text().strip(u"\u00a0")
                }
                self['descriptions'].append(description)

        self['accounting_units'] = {}
        self['accounting_units'][
            'exempt_from_parliamentary_election_returns'] = \
            self._text_from_id(
                re.compile("ExemptFromParliamentaryElectionReturnsValue"))

        self['accounting_units'][
            'exempt_from_quarterly_donation_returns'] = \
            self._text_from_id(
                re.compile("ExemptFromQuarterlyDonationReturnsValue"))

        self['accounting_units'][
            'exempt_from_quarterly_transaction_returns'] = \
            self._text_from_id(
                re.compile("ExemptFromQuarterlyTransactionReturnsValue"))

    def geocode(self):
        geometry = {"type": "Point",}
        if HAS_REDIS:
            coordinates = r.get(self['postcode'])
            if coordinates:
                geometry['coordinates']= json.loads(coordinates)
                return geometry

        import time
        time.sleep(2)

        url = "http://mapit.mysociety.org/postcode/{0}".format(self['postcode'])

        try:
            req = requests.get(url)
            req_json = req.json()
            coordinates = [req_json['wgs84_lon'], req_json['wgs84_lat']]
        except (KeyError, ValueError):

            print "MaPit failed, trying google"

            try:
                google_url = \
                    "https://maps.googleapis.com/maps/api/geocode/json?address="
                address = " ".join(self['party_address'].splitlines())
                req = requests.get(google_url + address)
                req_json = req.json()
                location = req_json['results'][0]['geometry']['location']
                coordinates = [location['lng'], location['lat']]
            except:
                # Just give up!
                pass
            print req.text



        if HAS_REDIS:
            r.set(self['postcode'], json.dumps(coordinates))
        geometry['coordinates ']= coordinates
        return geometry


    @property
    def emblem_dict(self):
        emblem_dict = {}
        all_emblems = glob.glob(os.path.join(self.folder_name, "Emblem_*"))
        for emblem in all_emblems:
            e_id = os.path.split(emblem)[-1].split('_')[-1].split('.')[0]
            emblem_dict[e_id] = os.path.relpath(emblem)
        return emblem_dict

    def as_json(self):
        return json.dumps(self, indent=4)

if __name__ == "__main__":
    all_data = []
    for path in glob.glob('raw_data/*'):
        party_id = os.path.split(path)[-1]
        p = PartyParser(party_id)

        with open(os.path.join('parsed', "{0}.json".format(party_id)),
                  'w') as f:
            all_data.append(p)
            f.write(p.as_json())

    with open("all_data.json", 'w') as f:
        f.write(json.dumps(all_data, indent=4))
