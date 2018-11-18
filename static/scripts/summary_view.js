'use strict';

var init_summary_view = function () {

	var global_parents = [{
		"000404142411": {"value": "Ingersoll-Rand European Holding Company B.V.", "status": "no"},
		"000985033590": {"value": "INGERSOLL-RAND PUBLIC LIMITED COMPANY", "status": "yes"},
		"000544292089": {"value": "INGERSOLL-RAND EUROPEAN SALES LIMITED", "status": "yes"},
		"000400671451": {"value": "Ingersoll-Rand International Limited BUITENL.VEN", "status": "yes"},
		"000918577644": {"value": "INGERSOLL-RAND INTERNATIONAL (INDIA) PRIVATE LIMITED", "status": "yes"},
		"000669664240": {"value": "Ingersoll-Rand (Hong Kong) Holding Company Limited", "status": "no"},
		"000796641363": {"value": "Ingersoll-Rand Federal Credit Union", "status": "yes"},
		"000120748509": {"value": "Ingersoll-Rand Employees Federal Credit Union", "status": "yes"},
		"000650054542": {"value": "INGERSOLL - RAND CLIMATE SOLUTIONS PRIVATE LIMITED", "status": "yes"},
		"000812772609": {"value": "Ingersoll Rand Manufactura, S. de R.L. de C.V.", "status": "yes"},
		"000668080302": {"value": "Ingersoll-Rand Superay Holdings Limited", "status": "no"}
	}];

	var entity_demo = [{
		"CASE_DUNS": {"value": "285005117", "status": "yes"},
		"CASE_NAME": {"value": "IDEAL STANDARD INDUSTRIES FRANCE", "status": "yes"},
		"CASE_SECOND_NAME": {"value": "", "status": "yes"},
		"CASE_REG_ADDR_FLAG": {"value": "N", "status": "yes"},
		"CASE_ADDRESS1": {"value": "ZONE INDUSTRIELLE", "status": "yes"},
		"CASE_ADDRESS2": {"value": "65 RUE DE CRISSEY", "status": "yes"},
		"CASE_CITY": {"value": "DOLE", "status": "yes"},
		"CASE_STATE_NAME": {"value": "JURA", "status": "yes"},
		"CASE_COUNTRY_NAME": {"value": "FRANCE", "status": "yes"},
		"CASE_CITY_CODE": {"value": "125", "status": "yes"},
		"CASE_COUNTY_CODE": {"value": "0", "status": "yes"},
		"CASE_STATE_CODE": {"value": "39", "status": "yes"},
		"CASE_STATE_ABBR": {"value": "", "status": "yes"},
		"CASE_COUNTRY_CODE": {"value": "241", "status": "yes"},
		"CASE_POSTAL_CODE": {"value": "39100", "status": "yes"},
		"CASE_CONTINENT": {"value": "3", "status": "yes"},
		"CASE_MAIL_ADDRESS": {"value": "", "status": "yes"},
		"CASE_MAIL_CITY": {"value": "", "status": "yes"},
		"CASE_MAIL_COUNTY": {"value": "", "status": "yes"},
		"CASE_MAIL_STATE": {"value": "", "status": "yes"},
		"CASE_MAIL_COUNTRY": {"value": "", "status": "yes"},
		"CASE_MAIL_CITY_CODE": {"value": "", "status": "yes"},
		"CASE_MAIL_COUNTY_CODE": {"value": "0", "status": "yes"},
		"CASE_MAIL_STATE_CODE": {"value": "0", "status": "yes"},
		"CASE_MAIL_STATE_ABBR": {"value": "", "status": "yes"},
		"CASE_MAIL_COUNTRY_CODE": {"value": "0", "status": "yes"},
		"CASE_MAIL_POSTAL_CODE": {"value": "", "status": "yes"},
		"CASE_MAIL_CONTINENT": {"value": "", "status": "yes"},
		"CASE_NATL_ID": {"value": "4.87421E+13", "status": "yes"},
		"CASE_NATL_ID_SYS": {"value": "17", "status": "yes"},
		"CASE_PHONE_CODE": {"value": "33", "status": "yes"},
		"CASE_PHONE": {"value": "384829500", "status": "yes"},
		"CASE_TELEX": {"value": "311NMNNANP", "status": "yes"},
		"CASE_FAX": {"value": "", "status": "yes"},
		"CEO_NAME": {"value": "BenoÃ®t Jacques Simon MARSAUD", "status": "yes"},
		"CEO_TITLE": {"value": "President", "status": "yes"},
		"LOB": {"value": "Plastics products, nec, nsk", "status": "yes"},
		"SIC1": {"value": "30890000", "status": "yes"},
		"SIC2": {"value": "", "status": "yes"},
		"SIC3": {"value": "", "status": "yes"},
		"SIC4": {"value": "", "status": "yes"},
		"SIC5": {"value": "", "status": "yes"},
		"SIC6": {"value": "", "status": "yes"},
		"ACTIVITY_CODE": {"value": "2223Z", "status": "yes"},
		"ACTIVITY_IND": {"value": "15", "status": "yes"},
		"START_YEAR": {"value": "2005", "status": "yes"},
		"SALES_LOC": {"value": "4067645", "status": "yes"},
		"SALES_CD": {"value": "0", "status": "yes"},
		"SALES_US": {"value": "4369114", "status": "yes"},
		"CURRENCY_CODE": {"value": "5080", "status": "yes"},
		"EMPLOYEES_HERE": {"value": "57", "status": "yes"},
		"EMPLOYEES_HERE_IND": {"value": "2", "status": "yes"},
		"EMPLOYEES_TOTAL": {"value": "57", "status": "yes"},
		"EMPLOYEES_TOTAL_IND": {"value": "0", "status": "yes"},
		"INCLUDE_PRINCIPLE": {"value": "N", "status": "yes"},
		"IMPORT_G": {"value": "G", "status": "yes"},
		"LEGAL_STATUS": {"value": "3", "status": "yes"},
		"CONTROL_IND": {"value": "", "status": "yes"},
		"GLOBAL_STATUS_CODE": {"value": "1", "status": "yes"},
		"SUBSIDIARY_CODE": {"value": "3", "status": "yes"},
		"PREVIOUS_DUNS": {"value": "0", "status": "yes"},
		"REPORT_DATE": {"value": "", "status": "yes"},
		"PARENT_DUNS": {"value": "275236297", "status": "no"},
		"PARENT_NAME": {"value": "IDEAL STANDARD FRANCE", "status": "yes"},
		"PARENT_ADDRESS": {"value": "PARIS NORD II PRC REFLETS", "status": "yes"},
		"PARENT_CITY": {"value": "ROISSY EN FRANCE", "status": "yes"},
		"PARENT_STATE": {"value": "VAL D OISE", "status": "yes"},
		"PARENT_COUNTRY_NAME": {"value": "FRANCE", "status": "yes"},
		"PARENT_CITY_CODE": {"value": "5503", "status": "yes"},
		"PARENT_COUNTY_CODE": {"value": "0", "status": "yes"},
		"PARENT_STATE_ABBR": {"value": "", "status": "yes"},
		"PARENT_COUNTRY_CODE": {"value": "241", "status": "yes"},
		"PARENT_POSTAL_CODE": {"value": "95700", "status": "yes"},
		"PARENT_CONTINENT_CODE": {"value": "3", "status": "yes"},
		"DOMESTIC_DUNS": {"value": "737828962", "status": "yes"},
		"DOMESTIC_NAME": {"value": "AMERICAN STANDARD FRENCH HOLDINGS", "status": "yes"},
		"DOMESTIC_ADDRESS": {"value": "", "status": "yes"},
		"DOMESTIC_CITY": {"value": "ROISSY EN FRANCE", "status": "yes"},
		"DOMESTIC_STATE": {"value": "VAL D OISE", "status": "yes"},
		"DOMESTIC_CITY_CODE": {"value": "5503", "status": "yes"},
		"DOMESTIC_COUNTRY_CODE": {"value": "241", "status": "yes"},
		"DOMESTIC_STATE_ABBR": {"value": "", "status": "yes"},
		"DOMESTIC_POSTAL_CODE": {"value": "95700", "status": "yes"},
		"GLOBAL_INDICATOR": {"value": "N", "status": "yes"},
		"GLOBAL_DUNS": {"value": "404142411", "status": "yes"},
		"GLOBAL_NAME": {"value": "Ingersoll-Rand European Holding Company B.V.", "status": "yes"},
		"GLOBAL_ADDRESS": {"value": "Produktieweg 10", "status": "yes"},
		"GLOBAL_CITY": {"value": "Zoeterwoude", "status": "yes"},
		"GLOBAL_STATE": {"value": "ZUID-HOLLAND", "status": "yes"},
		"GLOBAL_COUNTRY_NAME": {"value": "NETHERLANDS", "status": "yes"},
		"GLOBAL_CITY_CODE": {"value": "1716", "status": "yes"},
		"GLOBAL_COUNTY_CODE": {"value": "0", "status": "yes"},
		"GLOBAL_STATE_ABBR": {"value": "", "status": "yes"},
		"GLOBAL_COUNTRY_CODE": {"value": "521", "status": "yes"},
		"GLOBAL_POSTAL_CODE": {"value": "2382 PB", "status": "yes"},
		"GLOBAL_CONTINENT_CODE": {"value": "3", "status": "yes"},
		"GLOBAL_FAMILY_NUM": {"value": "128", "status": "yes"},
		"GLOBAL_DIAS_CODE": {"value": "8867788", "status": "yes"},
		"GLOBAL_HIERARCHY_CODE": {"value": "6", "status": "yes"},
		"FAMILY_UPDATE_DATE": {"value": "20161007", "status": "yes"},
		"NAICS1": {"value": "326199", "status": "yes"},
		"NAICS2": {"value": "", "status": "yes"},
		"NAICS3": {"value": "", "status": "yes"},
		"NAICS4": {"value": "", "status": "yes"},
		"NAICS5": {"value": "", "status": "yes"},
		"NAICS6": {"value": "", "status": "yes"},
		"FLAG": {"value": "", "status": "yes"},
		"RECORD_TYPE": {"value": "", "status": "yes"},
		"PROCESS_DATE": {"value": "", "status": "yes"},
		"EATON_PARENT_DUNS": {"value": "", "status": "yes"},
		"VERIFIED_DUNS": {"value": "", "status": "yes"},
		"REASON_CODE": {"value": "", "status": "yes"},
		"BEMFAB_INDICATOR": {"value": "", "status": "yes"},
		"latitude": {"value": "47.0940244", "status": "yes"},
		"longitude": {"value": "5.4838695", "status": "yes"}
	}]

	generate_table(global_parents, $("#global-parents-table"));
	generate_table(entity_demo, $("#pnid-entities-table"));
	generate_table(entity_demo, $("#metadata-table"));
}

var generate_table = function (dataset, table) {
	var thead_content = "<tr>";
	var tbody_content = "";
	var init_flag = true;
	for (var i = 0; i < dataset.length; i++) {
		tbody_content += "<tr>";
		for (var key in dataset[i]) {
			if (dataset[i][key]["status"] == "no") {
				tbody_content += "<td class='error-in-table'>" + dataset[i][key]["value"] + "</td>";
			} else {
				tbody_content += "<td>" + dataset[i][key]["value"] + "</td>";
			}
		}
		tbody_content += "</tr>";
		if (init_flag) {
			for (var key in dataset[i]) {
			    thead_content += ("<th>" + key + "</th>");
			}
			thead_content += "</tr>";
			init_flag = false;
		}
	}
	table.children("thead").empty().html(thead_content);
	table.children("tbody").empty().html(tbody_content);
}
