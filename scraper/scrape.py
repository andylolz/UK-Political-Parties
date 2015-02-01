import os
import re
import shutil

import bs4
import requests

results_data = {
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$RadScriptManager": 'ctl00$ContentPlaceHolder1$EntitySearchControl1$ctl00$ContentPlaceHolder1$EntitySearchControl1$divResultsPerPagePanel|ctl00$ContentPlaceHolder1$EntitySearchControl1$ddlResultsPerPage',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$grdFullResults$ctl00$ctl03$ctl01$PageSizeComboBox": '25',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_RadScriptManager_TSM": ';;System.Web.Extensions, Version=3.5.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en-US:eb198dbd-2212-44f6-bb15-882bde414f00:ea597d4b:b25378d2;Telerik.Web.UI:en-US:57877faa-0ff2-4cb7-9385-48affc47087b:16e4e7cd:f7645509:ed16cbdc:24ee1bba:f46195d3:2003d0b8:1e771326:aa288e2d:b7778d6c:58366029',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_RadStyleSheetManager1_TSSM": ';Telerik.Web.UI, Version=2013.2.611.35, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en-GB:57877faa-0ff2-4cb7-9385-48affc47087b:45085116:1c2121e:e24b8e95:aac1aeb7:c73cf106:9e1572d6:e25b4b77',
    "__EVENTTARGET": 'ctl00$ContentPlaceHolder1$EntitySearchControl1$ddlResultsPerPage',
    "__EVENTARGUMENT":'{"Command":"Select","Index":6}',
    "__VIEWSTATEENCRYPTED": '',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityType": 'All',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityType$i0$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityType$i1$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityType$i2$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityType$i3$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityType$Footer$chkSelectAll": 'on',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_cmbEntityType_ClientState": '',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus": 'All',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$i0$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$i1$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$i2$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$i3$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$i4$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$i5$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$i6$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$i7$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$i8$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$i9$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$i10$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$i11$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$i12$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityStatus$Footer$chkSelectAll": 'on',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_cmbEntityStatus_ClientState": '',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbRegistrationStatus": 'Registered',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbRegistrationStatus$i0$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbRegistrationStatus$i1$chkSelected": 'on',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_cmbRegistrationStatus_ClientState": '',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbReferendum": 'All',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbReferendum$i0$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbReferendum$i1$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbReferendum$i2$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbReferendum$i3$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbReferendum$Footer$chkSelectAll": 'on',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_cmbReferendum_ClientState": '',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbDesignationStatus": 'All',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbDesignationStatus$i0$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbDesignationStatus$i1$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbDesignationStatus$Footer$chkSelectAll": 'on',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_cmbDesignationStatus_ClientState": '',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbRegister": 'All',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbRegister$i0$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbRegister$i1$chkSelected": 'on',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbRegister$Footer$chkSelectAll": 'on',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_cmbRegister_ClientState": '',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityName": 'All',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbEntityName$Footer$chkSelectAll": 'on',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_cmbEntityName_ClientState": '',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$txtEntityName": '- free text search -',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_txtEntityName_ClientState": '{"enabled":true,"emptyMessage":"- free text search -","validationText":"","valueAsString":"","lastSetTextBoxValue":"- free text search -"}',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$txtEntityIdNo": '',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_txtEntityIdNo_ClientState": '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$txtAccountingUnit": '',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_txtAccountingUnit_ClientState": '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$txtCompanyRegNo": '',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_txtCompanyRegNo_ClientState": '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$txtPersonName": '',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_txtPersonName_ClientState": '{"enabled":true,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$dtDateRangeFrom": '01/01/0001 00:00:00',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$dtDateRangeFrom$ddlDay": '-1',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$dtDateRangeFrom$ddlMonth": '-1',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$dtDateRangeFrom$ddlYear": '-1',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$dtDateRangeTo": '01/01/0001 00:00:00',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$dtDateRangeTo$ddlDay": '-1',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$dtDateRangeTo$ddlMonth": '-1',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$dtDateRangeTo$ddlYear": '-1',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$cmbFieldingCandidatesIn": 'Any',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_cmbFieldingCandidatesIn_ClientState": '',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$txtEntityNameIds": '',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$txtRepopulateEntityNameIds": 'false',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$txtEntitySelectionText": 'All',
    "ctl00$ContentPlaceHolder1$EntitySearchControl1$ddlResultsPerPage": 'All',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_ddlResultsPerPage_ClientState": '{"logEntries":[],"value":"All","text":"All","enabled":true,"checkedIndices":[],"checkedItemsTextOverflows":false}',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_grdFullResults_ClientState": '{"selectedIndexes":[],"selectedCellsIndexes":[],"unselectableItemsIndexes":[],"reorderedColumns":[],"expandedItems":[],"expandedGroupItems":[],"expandedFilterItems":[],"deletedItems":[],"hidedColumns":[],"showedColumns":[],"groupColsState":{},"hierarchyState":{},"scrolledPosition":"0,2","popUpLocations":{},"draggedItemsIndexes":[]}',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_grdFullResults_ctl00_ctl03_ctl01_PageSizeComboBox_ClientState": '',
    "ctl00_ContentPlaceHolder1_EntitySearchControl1_RadScriptManager_TSM": ';;System.Web.Extensions, Version=3.5.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en-US:eb198dbd-2212-44f6-bb15-882bde414f00:ea597d4b:b25378d2;Telerik.Web.UI:en-US:57877faa-0ff2-4cb7-9385-48affc47087b:16e4e7cd:f7645509:ed16cbdc:24ee1bba:f46195d3:2003d0b8:1e771326:aa288e2d:b7778d6c:58366029;',
    "__ASYNCPOST": 'true',
    "RadAJAXControlID": 'ctl00_ContentPlaceHolder1_EntitySearchControl1_RadAjaxManager1',
}


if __name__ == "__main__":

    class ElectoralCommissionScraper(object):
        def __init__(self):
            self.session = requests.Session()

        def _extract_viewstate(self, req):
            soup = bs4.BeautifulSoup(req.text)
            self.VIEWSTATE = soup.find(id="__VIEWSTATE")['value']
            return self.VIEWSTATE

        def _extract_event_validation(self, req):
            soup = bs4.BeautifulSoup(req.text)
            self.EVENTSTATE = soup.find(id="__EVENTVALIDATION")['value']
            return self.EVENTSTATE




        def first_page(self):
            print "First page"
            req = self.session.get(
            "https://pefonline.electoralcommission.org.uk/Search/SearchIntro.aspx")
            self._extract_viewstate(req)
            self._extract_event_validation(req)
            self.data = {
                '__VIEWSTATE': self.VIEWSTATE,
                '__EVENTVALIDATION': self.EVENTSTATE,
                "__VIEWSTATEENCRYPTED": "",
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "ctl00$ctl05$ctl16": "Registration search"
            }

        def form_page(self):
            """
            Requires the data set by self.first_page.

            Note that this needs to POST to the search form, but that in turn
            gets 'redirected' (in JS) to a GET requests at /EntitySearch.aspx

            """
            print "Form page"
            req = self.session.post("https://pefonline.electoralcommission.org.uk"
                               "/Search"\
                         "/SearchIntro.aspx", self.data)

            print "GET Form page"
            req = self.session.get("https://pefonline.electoralcommission.org.uk"
                               "/Search"\
                          "/EntitySearch.aspx")

            self._extract_viewstate(req)

        def results(self):
            """
            Get all results

            """
            print "Results"

            # ev = _extract_event_validation(x)
            data = {
                '__VIEWSTATE': self.VIEWSTATE,
            }
            data.update(results_data)
            # print data

            req = self.session.post("https://pefonline.electoralcommission.org.uk"
                               "/Search"\
                             "/EntitySearch.aspx", data, headers={
                "X-MicrosoftAjax":"Delta=true",
                "Referer":"https://pefonline.electoralcommission.org.uk/Search"
                          "/EntitySearch.aspx",
                "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36",

            })
            soup = bs4.BeautifulSoup(req.text.encode('utf8'))
            # Print all results:
            all_results = soup.findAll('a', {'class':'RadGridLinkAlt'})
            # print all_results
            for result in all_results:
                target = result['href'].split("'")[1]
                party_id = result.get_text().replace(' ', '')
                path = "raw_data/{0}/results_page.html".format(party_id)
                if os.path.exists(path):
                    print "Seen: {0}".format(party_id)
                    # continue
                try:
                    self.detail_view(target, party_id, path)
                except requests.exceptions.ConnectionError:
                    if os.path.exists(path):
                        # Cleanup, as we want this to be included next time
                        # scraper is run
                        shutil.rmtree(os.path.abspath("raw_data/{0}".format(party_id)))


        def detail_view(self, target, party_id, path):
            print "DETAIL VIEW {0}".format(party_id)
            data = results_data
            data["ctl00$ContentPlaceHolder1$EntitySearchControl1$RadScriptManager"] =\
                'ctl00$ContentPlaceHolder1$EntitySearchControl1$ctl00$ContentPlaceHolder1$EntitySearchControl1$grdFullResultsPanel|%s' % target
            data["__EVENTTARGET"] = target
            data.update({
                'ctl00$ContentPlaceHolder1$EntitySearchControl1$grdFullResults$ctl00$ctl03$ctl01$PageSizeComboBox': '25',
                'ctl00_ContentPlaceHolder1_EntitySearchControl1_ddlResultsPerPage_ClientState': '{"logEntries":[],"value":"All","text":"All","enabled":true,"checkedIndices":[],"checkedItemsTextOverflows":false}',
                'ctl00_ContentPlaceHolder1_EntitySearchControl1_grdFullResults_ClientState': '{"selectedIndexes":[],"selectedCellsIndexes":[],"unselectableItemsIndexes":[],"reorderedColumns":[],"expandedItems":[],"expandedGroupItems":[],"expandedFilterItems":[],"deletedItems":[],"hidedColumns":[],"showedColumns":[],"groupColsState":{},"hierarchyState":{},"scrolledPosition":"0,2","popUpLocations":{},"draggedItemsIndexes":[]}',
                'ctl00_ContentPlaceHolder1_EntitySearchControl1_grdFullResults_ctl00_ctl03_ctl01_PageSizeComboBox_ClientState': '',
                'ctl00_ContentPlaceHolder1_EntitySearchControl1_RadScriptManager_TSM': ';;System.Web.Extensions',
                '__EVENTARGUMENT': '{"Command":"Select","Index":6}',
                "ctl00_ContentPlaceHolder1_EntitySearchControl1_RadStyleSheetManager1_TSSM:;Telerik.Web.UI, Version": "2013.2.611.35, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en-GB:57877faa-0ff2-4cb7-9385-48affc47087b:45085116:1c2121e:e24b8e95:aac1aeb7:c73cf106:9e1572d6:e25b4b77"


            })
            data['__VIEWSTATE'] = self.VIEWSTATE
            # print data
            req = self.session.post("https://pefonline.electoralcommission.org.uk"
                               "/Search/EntitySearch.aspx", data, headers={
                    "X-MicrosoftAjax":"Delta=true",
                    "Referer":"https://pefonline.electoralcommission.org.uk/Search"
                              "/EntitySearch.aspx",
                    "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) "
                                 "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36",

                })

            req = self.session.get("https://pefonline.electoralcommission.org.uk"
                                "/Search/ViewRegistrations/Profile.aspx")


            soup = bs4.BeautifulSoup(req.text)
            self.save_file(path, unicode(soup).encode('utf8'))

            tmp_vs = soup.find(id="__VIEWSTATE")['value']
            tmp_ev = soup.find(id="__EVENTVALIDATION")['value']

            self.get_accounting_units(party_id, tmp_vs, tmp_ev)

            emblems = soup.findAll('a',
                id=re.compile(r"ctl00_ContentPlaceHolder1_ProfileControl1_gvEmblems_ctl[0-9]+_lnkEmblemId"))

            if emblems:

                for emblem in emblems:
                    self.get_emblem(party_id, emblem, tmp_vs, tmp_ev)




        def get_emblem(self, party_id, link, vs, ev):
            target = link['href'].split("'")[1]
            data = {
                "__EVENTTARGET": target,
                "__VIEWSTATE": vs,
                '__EVENTVALIDATION': ev,
                "__VIEWSTATEENCRYPTED": '',
                "__EVENTARGUMENT": '',
            }

            req = self.session.post(
                "https://pefonline.electoralcommission.org.uk/Search/ViewRegistrations/Profile.aspx",
                data, headers={
                    "Referer":"https://pefonline.electoralcommission.org.uk/Search"
                                              "/EntitySearch.aspx",
                    "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36",
                    "Accept":"text/html,application/xhtml+xml,"
                             "application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Origin":"https://pefonline.electoralcommission.org.uk",
                    "Content-Length":"95712",
                    "Accept-Encoding":"gzip, deflate",
                })

            filename = req.headers['content-disposition'].split('=')[-1]
            path = "raw_data/{0}/{1}".format(party_id, filename)
            self.save_file(path, req.content, mode="wb")


        def get_accounting_units(self, party_id, vs, ev):
            data = {
                "__EVENTTARGET": "ctl00$ContentPlaceHolder1$ProfileControl1$lnkViewAccountingUnits",
                "__VIEWSTATE": vs,
                '__EVENTVALIDATION': ev,
                "__VIEWSTATEENCRYPTED": '',
                "__EVENTARGUMENT": '',
            }

            req = self.session.post(
            "https://pefonline.electoralcommission.org.uk/Search/ViewRegistrations/Profile.aspx",
            data, headers={
                "X-MicrosoftAjax":"Delta=true",
                "Referer":"https://pefonline.electoralcommission.org.uk/Search"
                                          "/EntitySearch.aspx",
                "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36",
                "Accept":"text/html,application/xhtml+xml,"
                         "application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Origin":"https://pefonline.electoralcommission.org.uk",
                "Accept-Encoding":"gzip, deflate",
            })

            if not "ErrorHandler.aspx" in req.text:
                req = self.session.get("https://pefonline.electoralcommission.org.uk"
                                            "/Search/ViewRegistrations/AccountingUnitsProfile.aspx")
                if not "This party doesn't currently have any accounting " \
                      "units" in req.text:
                    print "GOT ACCOUNTING UNITS"
                    path = "raw_data/{0}/accounting_untis.html".format(party_id)
                    self.save_file(path, req.text.encode('utf8'))

        def save_file(self, full_path, content, mode="w"):
            path, file_name = head, tail = os.path.split(full_path)

            if not os.path.exists(path):
                os.makedirs(path)

            with open(full_path, mode) as f:
                f.write(content)

        def get_all(self):
            self.first_page()
            self.form_page()
            self.results()



    e = ElectoralCommissionScraper()
    print "GETTING WHOLE LIST"
    e.get_all()
