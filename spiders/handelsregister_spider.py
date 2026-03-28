import scrapy
from datetime import datetime

class HandelsregisterSpider(scrapy.Spider):
    name = "handelsregister"
    start_urls = [
        "https://www.handelsregister.de/rp_web/erweitertesuche/welcome.xhtml"
    ]

    def __init__(self, firma=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not firma:
            raise ValueError("Bitte -a firma=... angeben")
        self.firma = firma

    def parse(self, response):

        yield scrapy.FormRequest.from_response(
            response, formdata={
                "form:schlagwoerter": self.firma,
                "javax.faces.ViewState": response.css('input[name="javax.faces.ViewState"]::attr(value)').get(),
                "suchTyp": "e",
                "form:schlagwortOptionen": "1",
                "form:ergebnisseProSeite_input": "10",
                "form": "form",
                "form:btnSuche": ""
            },
            callback = self.after_search
        )

    def after_search(self, response):

        si_link = response.xpath("//a[contains(@class, 'dokumentList')][.//span[normalize-space(text())='SI']]")
        si_button_id = si_link.xpath("@id").get()

        yield scrapy.FormRequest.from_response(
            response, formname="ergebnissForm",
            formdata={
                "property": "Global.Dokumentart.SI",
                "property2": "",
                si_button_id: si_button_id,
                "javax.faces.ViewState": response.css('input[name="javax.faces.ViewState"]::attr(value)').get(),
                "ergebnissForm:selectedSuchErgebnisFormTable_rppDD": "10",
                "ergebnissForm": "ergebnissForm"
            },
            callback=self.after_si_download,
            dont_filter=True
        )

    def after_si_download(self, response):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"si_{timestamp}_{self.firma}.xml"

        with open(f"downloads/{filename}", "wb") as f:
            f.write(response.body)