import os
import re
import sys
import json
import shutil

import bs4
import requests

sys.path.append('./../')
sys.path.append('.')
from scrape import ElectoralCommissionScraper

results_data = {
    "ctl00$ContentPlaceHolder1$searchControl1$RadScriptManager": "ctl00$ContentPlaceHolder1$searchControl1$RadScriptManager|ctl00$ContentPlaceHolder1$searchControl1$btnGo",
    "ctl00_ContentPlaceHolder1_searchControl1_RadScriptManager_TSM": ";;System.Web.Extensions, Version=3.5.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en-US:eb198dbd-2212-44f6-bb15-882bde414f00:ea597d4b:b25378d2;Telerik.Web.UI:en-US:57877faa-0ff2-4cb7-9385-48affc47087b:16e4e7cd:f7645509:ed16cbdc:24ee1bba:f46195d3:2003d0b8:1e771326:aa288e2d:b7778d6c:58366029",
    "ctl00_ContentPlaceHolder1_searchControl1_RadStyleSheetManager1_TSSM": ";Telerik.Web.UI, Version=2013.2.611.35, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en-GB:57877faa-0ff2-4cb7-9385-48affc47087b:45085116:1c2121e:e24b8e95:aac1aeb7:c73cf106:9e1572d6:e25b4b77",
    "__EVENTTARGET": "ctl00$ContentPlaceHolder1$searchControl1$btnGo",
    "__EVENTARGUMENT": "",
    "__VIEWSTATEENCRYPTED": "",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbEntityType": "All",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbEntityType$i0$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbEntityType$i1$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbEntityType$i2$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbEntityType$Footer$chkSelectAll": "on",
    "ctl00_ContentPlaceHolder1_searchControl1_cmbEntityType_ClientState": "",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbReferendum": "All",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbReferendum$i0$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbReferendum$i1$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbReferendum$i2$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbReferendum$i3$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbReferendum$Footer$chkSelectAll": "on",
    "ctl00_ContentPlaceHolder1_searchControl1_cmbReferendum_ClientState": "",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbDesignationStatus": "All",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbDesignationStatus$i0$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbDesignationStatus$i1$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbDesignationStatus$Footer$chkSelectAll": "on",
    "ctl00_ContentPlaceHolder1_searchControl1_cmbDesignationStatus_ClientState": "",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection": "All",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i0$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i1$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i2$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i3$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i4$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i5$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i6$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i7$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i8$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i9$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i10$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i11$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i12$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i13$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i14$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$i15$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbElection$Footer$chkSelectAll": "on",
    "ctl00_ContentPlaceHolder1_searchControl1_cmbElection_ClientState": "",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbEntityName": "All",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbEntityName$Footer$chkSelectAll": "on",
    "ctl00_ContentPlaceHolder1_searchControl1_cmbEntityName_ClientState": "",
    "ctl00$ContentPlaceHolder1$searchControl1$txtEntityName": "- free text search -",
    "ctl00_ContentPlaceHolder1_searchControl1_txtEntityName_ClientState": '{"enabled":true,"emptyMessage":"- free text search -","validationText":"","valueAsString":"","lastSetTextBoxValue":"- free text search -"}',
    "ctl00$ContentPlaceHolder1$searchControl1$cmbExpenditureType": "All",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbExpenditureType$i0$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbExpenditureType$i1$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbExpenditureType$i2$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbExpenditureType$i3$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbExpenditureType$i4$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbExpenditureType$i5$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbExpenditureType$i6$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbExpenditureType$i7$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbExpenditureType$i8$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbExpenditureType$i9$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbExpenditureType$i10$chkSelected": "on",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbExpenditureType$Footer$chkSelectAll": "on",
    "ctl00_ContentPlaceHolder1_searchControl1_cmbExpenditureType_ClientState": "",
    "ctl00$ContentPlaceHolder1$searchControl1$txtSupplierName": "",
    "ctl00_ContentPlaceHolder1_searchControl1_txtSupplierName_ClientState":'{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}',
    "ctl00$ContentPlaceHolder1$searchControl1$cmbCountry": "All",
    "ctl00_ContentPlaceHolder1_searchControl1_cmbCountry_ClientState": "",
    "ctl00$ContentPlaceHolder1$searchControl1$txtMinimumExpenditureAmount": "",
    "ctl00_ContentPlaceHolder1_searchControl1_txtMinimumExpenditureAmount_ClientState": '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}',
    "ctl00$ContentPlaceHolder1$searchControl1$txtMaximumExpenditureAmount": "",
    "ctl00_ContentPlaceHolder1_searchControl1_txtMaximumExpenditureAmount_ClientState": '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}',
    "ctl00$ContentPlaceHolder1$searchControl1$txtEntityNameIds": "",
    "ctl00$ContentPlaceHolder1$searchControl1$txtRepopulateEntityNameIds": "false",
    "ctl00$ContentPlaceHolder1$searchControl1$txtEntitySelectionText": "All",
    "ctl00$ContentPlaceHolder1$searchControl1$cmbSummaryTableType": "-- Please Select --",
    "ctl00_ContentPlaceHolder1_searchControl1_cmbSummaryTableType_ClientState": "",
    "ctl00_ContentPlaceHolder1_searchControl1_grdSummaryResults_ClientState": "",
    "ctl00$ContentPlaceHolder1$searchControl1$ddlResultsPerPage": "25",
    "ctl00_ContentPlaceHolder1_searchControl1_ddlResultsPerPage_ClientState": "",
    "ctl00_ContentPlaceHolder1_searchControl1_grdFullResults_ClientState": "",
    "__ASYNCPOST": "true",
    "RadAJAXControlID": "ctl00_ContentPlaceHolder1_searchControl1_RadAjaxManager1",
}

class CampaignScraper(ElectoralCommissionScraper):
    def first_page(self):
        print "First Campaign page"
        req = self.session.get(
        "https://pefonline.electoralcommission.org.uk/Search/SearchIntro.aspx")
        self._extract_viewstate(req)
        self._extract_event_validation(req)
        self._view_state_generator(req)
        self.data = {
            '__VIEWSTATE': self.VIEWSTATE,
            '__EVENTVALIDATION': self.EVENTSTATE,
            '__VIEWSTATEGENERATOR': self.VIEWSTATEGENERATOR,
            "__VIEWSTATEENCRYPTED": "",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "ctl00$ctl05$ctl13": "Campaign expenditure search"
        }


    def form_page(self):
        """
        Requires the data set by self.first_page.

        Note that this needs to POST to the search form, but that in turn
        gets 'redirected' (in JS) to a GET requests at
        /CampaignExpenditureSearch.aspx

        """

        print "Form page"
        req = self.session.post("https://pefonline.electoralcommission.org.uk"
                           "/Search/SearchIntro.aspx", self.data)

        print "GET Form page"
        req = self.session.get("https://pefonline.electoralcommission.org.uk"
                           "/Search/CampaignExpenditureSearch.aspx")

        self._extract_viewstate(req)
        self._extract_event_validation(req)
        self._view_state_generator(req)

    def results(self):
        """
        Get all results
        """
        print "Results"

        # ev = _extract_event_validation(x)
        data = {
            '__VIEWSTATE': self.VIEWSTATE,
            '__EVENTVALIDATION': self.EVENTSTATE,
            '__VIEWSTATEGENERATOR': self.VIEWSTATEGENERATOR,
        }

        data.update(results_data)

        req = self.session.post("https://pefonline.electoralcommission.org.uk"
           "/Search/CampaignExpenditureSearch.aspx",
            data, headers={
            "X-MicrosoftAjax":"Delta=true",
            "Referer":"https://pefonline.electoralcommission.org.uk/Search"
            "/CampaignExpenditureSearch.aspx",
            "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36",
        })
        def _get_mundged_data(req):
            data = re.findall(r"\|__([^\|]+)\|([^\|]+)|", req.text, re.MULTILINE)
            for item in data:
                if item[0] == "EVENTVALIDATION":
                    self.EVENTSTATE = item[1]
                if item[0] == "VIEWSTATEGENERATOR":
                    self.VIEWSTATEGENERATOR = item[1]
                if item[0] == "VIEWSTATE":
                    self.VIEWSTATE = item[1]

        _get_mundged_data(req)
        data.update({
            '__VIEWSTATE': self.VIEWSTATE,
            '__EVENTVALIDATION': self.EVENTSTATE,
            '__VIEWSTATEGENERATOR': self.VIEWSTATEGENERATOR,
            "__EVENTTARGET": 'ctl00$ContentPlaceHolder1$searchControl1$ddlResultsPerPage',
            "__EVENTARGUMENT": '{"Command":"Select","Index":8}',
            "ctl00_ContentPlaceHolder1_searchControl1_grdFullResults_ctl00_ctl03_ctl01_PageSizeComboBox_ClientState": "",
            "ctl00$ContentPlaceHolder1$searchControl1$grdFullResults$ctl00$ctl03$ctl01$PageSizeComboBox": "25",
            "ctl00_ContentPlaceHolder1_searchControl1_ddlResultsPerPage_ClientState":'{"logEntries":[],"value":"All","text":"All","enabled":true,"checkedIndices":[],"checkedItemsTextOverflows":false}',
            "ctl00$ContentPlaceHolder1$searchControl1$RadScriptManager": "ctl00$ContentPlaceHolder1$searchControl1$ctl00$ContentPlaceHolder1$searchControl1$divResultsPerPagePanel|ctl00$ContentPlaceHolder1$searchControl1$ddlResultsPerPage",
            "ctl00$ContentPlaceHolder1$searchControl1$ddlResultsPerPage": "All",
            "ctl00$ContentPlaceHolder1$searchControl1$RadScriptManager":"ctl00$ContentPlaceHolder1$searchControl1$ctl00$ContentPlaceHolder1$searchControl1$divResultsPerPagePanel|ctl00$ContentPlaceHolder1$searchControl1$ddlResultsPerPage",

        })
        req = self.session.post("https://pefonline.electoralcommission.org.uk"
           "/Search/CampaignExpenditureSearch.aspx",
            data, headers={
            "X-MicrosoftAjax":"Delta=true",
            "Referer":"https://pefonline.electoralcommission.org.uk/Search"
            "/CampaignExpenditureSearch.aspx",
            "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36",
        })
        _get_mundged_data(req)

        soup = bs4.BeautifulSoup(req.text.encode('utf8'))
        # Print all results:
        all_results = soup.findAll('a', {'class':'RadGridLinkAlt'})
        # print all_results
        print "Found %s results" % len(all_results)

        for result in all_results:
            target = result['href'].split("'")[1]
            spend_id = result.get_text().replace(' ', '')
            print spend_id
            path = "campaign_expenditure/raw_data/{0}/results_page.html".format(spend_id)
            if os.path.exists(path):
                print "Seen: {0}".format(spend_id)
                continue
            try:
                self.detail_view(target, spend_id, path)
            except requests.exceptions.ConnectionError:
                if os.path.exists(path):
                    # Cleanup, as we want this to be included next time
                    # scraper is run
                    shutil.rmtree(os.path.abspath("campaign_expenditure/raw_data/{0}".format(spend_id)))

    def detail_view(self, target, spend_id, path):
        print "DETAIL VIEW {0}".format(spend_id)
        data = results_data

        data["__EVENTTARGET"] = "ctl00$ContentPlaceHolder1$searchControl1$grdFullResults$ctl00$ctl04$lbReferenceView"
        data['__VIEWSTATEGENERATOR'] = self.VIEWSTATEGENERATOR
        data["ctl00$ContentPlaceHolder1$searchControl1$RadScriptManager"] =\
            'ctl00$ContentPlaceHolder1$searchControl1$ctl00$ContentPlaceHolder1$searchControl1$grdFullResultsPanel|%s' % target
        data['RadAJAXControlID'] = \
            "ctl00_ContentPlaceHolder1_searchControl1_RadAjaxManager1"
        data['ctl00_ContentPlaceHolder1_searchControl1_grdFullResults_ctl00_ctl03_ctl01_PageSizeComboBox_ClientState'] = ""
        data["ctl00$ContentPlaceHolder1$searchControl1$grdFullResults$ctl00$ctl03$ctl01$PageSizeComboBox"] = "25"
        data['__VIEWSTATE'] = self.VIEWSTATE
        data['__EVENTVALIDATION'] = self.EVENTSTATE
        # print data
        req = self.session.post("https://pefonline.electoralcommission.org.uk"
                           "/Search/CampaignExpenditureSearch.aspx", data, headers={
                "X-MicrosoftAjax":"Delta=true",
                "Referer":"https://pefonline.electoralcommission.org.uk/Search/CampaignExpenditureSearch.aspx",
                "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36",

            })

        req = self.session.get("https://pefonline.electoralcommission.org.uk"
                    "/Search/ViewReturns/CampaignExpenditureReturnItem.aspx")

        soup = bs4.BeautifulSoup(req.text)
        self.save_file(path, unicode(soup).encode('utf8'))

        tmp_vs = soup.find(id="__VIEWSTATE")['value']
        tmp_ev = soup.find(id="__EVENTVALIDATION")['value']
        self.get_invoice(spend_id, tmp_vs, tmp_ev)


    def get_invoice(self, spend_id, vs, ev):
        data = {
            "__EVENTTARGET": "ctl00$ContentPlaceHolder1$CampaignExpenditureControl1$ctl56",
            "__VIEWSTATE": vs,
            '__EVENTVALIDATION': ev,
            "__VIEWSTATEENCRYPTED": '',
            "__EVENTARGUMENT": '',
        }

        req = self.session.post(
            "https://pefonline.electoralcommission.org.uk/Search/ViewReturns/CampaignExpenditureReturnItem.aspx",
            data, headers={
                "Referer":"https://pefonline.electoralcommission.org.uk/Search/ViewReturns/CampaignExpenditureReturnItem.aspx",
                "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36",
                "Accept":"text/html,application/xhtml+xml,"
                         "application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Origin":"https://pefonline.electoralcommission.org.uk",
                "Content-Length":"95712",
                "Accept-Encoding":"gzip, deflate",
            })

        filename = req.headers.get('content-disposition', 'invoice.pdf').split('=')[-1]
        path = "campaign_expenditure/raw_data/{0}/{1}".format(spend_id, filename)
        self.save_file(path, req.content, mode="wb")



    def get_all(self):
        self.first_page()
        self.form_page()
        self.results()

if __name__ == "__main__":
    e = CampaignScraper()
    print "GETTING WHOLE LIST"
    e.get_all()
